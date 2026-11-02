#!/usr/bin/env python3
"""
MuseSynth MIDI bridge: browser page -> local MIDI port.

Why this exists
---------------
A web page cannot appear in QjackCtl as a JACK client by itself.
This small script is the missing piece:

    synth page (WebSocket, any browser)
        -> this script (localhost:8765)
        -> virtual ALSA MIDI port "MuseSynth"
        -> QjackCtl ALSA tab, direct to an ALSA synth (QSynth, VCV Rack on ALSA)
        -> or, via a2jmidid, QjackCtl MIDI tab to a JACK MIDI synth
           (Ardour, VCV Rack on JACK, etc.)

That last step is the same a2jmidid bridge already used for Rosegarden:
Rosegarden is ALSA MIDI only, Ardour is JACK MIDI only, and a2jmidid
bridges the two worlds. This bridge is an ALSA client on purpose, so
the existing a2j setup just works. No new JACK plumbing to invent.

Install (on the Linux audio machine, not in the Muse VM):
    pip install mido python-rtmidi websockets
    # Debian/Ubuntu equivalent, if you prefer packages:
    #   sudo apt install python3-mido python3-rtmidi python3-websockets

Run:
    python3 midi-bridge.py
    python3 midi-bridge.py --port-name MuseSynth --ws-port 8765 --bend-range 2

Test without a browser page:
    python3 midi-bridge.py --test
    # Connect MuseSynth to your synth in QjackCtl first, then listen.
    # --test plays plain notes, then the same note bent +35 cents,
    # so you can tell whether the receiving patch actually uses pitch bend.

Protocol (JSON text messages over the WebSocket)
------------------------------------------------
Note on by frequency (the normal microtonal path):
    {"type": "note_on", "id": "z", "freq": 440.0, "velocity": 100}
Note on by MIDI note, with an explicit bend in cents:
    {"type": "note_on", "id": "z", "midi": 69, "bend_cents": 35, "velocity": 100}
Note off, matched by the same id:
    {"type": "note_off", "id": "z"}
Raw MIDI passthrough (for testing):
    {"type": "raw", "bytes": [144, 60, 100]}
Panic:
    {"type": "all_notes_off"}
Ping:
    {"type": "ping"}  ->  {"type": "pong"}

Microtonal MIDI, honestly
-------------------------
Plain MIDI has 12 notes per octave. This bridge does NOT quantise
away microtones silently. It sends the nearest MIDI note plus a
per-note pitch bend (MPE style: one MIDI channel per sounding note,
channels 1-15, round-robin). The bend range must match the receiving
synth: --bend-range 2 means a full bend of 2 semitones, which is
plenty, because the bend from the nearest note is never more than
50 cents. If the receiving patch ignores pitch bend, you will hear
the nearest 12-TET note, not the microtone. That is a property of
the patch, not a silent error in this bridge. See README-midi-bridge.md
for the VCV Rack PW-output patch to try if bend seems ignored.

With --no-mpe, all notes share channel 0 and bend is global, so
chords with different bends will be wrong. That mode is only for
old synths that do not understand per-channel bend.
"""

import argparse
import json
import math
import sys

# ---------------------------------------------------------------------------
# Pure maths. No MIDI, no network, no UI in here. This is deliberate:
# the tuning maths must never be nested inside, or confused with,
# the enumeration maths or the transport code. These functions are
# unit-testable by importing this file, with no MIDI hardware present.
# ---------------------------------------------------------------------------

A4_FREQ = 440.0
A4_MIDI = 69


def freq_to_midi_bend(freq, bend_range_semitones=2.0):
    """Return (nearest_midi_note, bend_cents, bend_value_14bit).

    bend_cents is in [-50, +50] by construction, because the nearest
    note is chosen. bend_value is the 14-bit MIDI pitch-bend value,
    8192 = centre, for the given bend range in semitones.
    """
    if freq <= 0:
        raise ValueError("freq must be positive")
    midi_float = A4_MIDI + 12.0 * math.log2(freq / A4_FREQ)
    nearest = int(round(midi_float))
    bend_cents = (midi_float - nearest) * 100.0
    bend_value = bend_value_from_cents(bend_cents, bend_range_semitones)
    return nearest, bend_cents, bend_value


def bend_value_from_cents(bend_cents, bend_range_semitones=2.0):
    """14-bit pitch-bend value for a bend in cents."""
    value = 8192 + round((bend_cents / 100.0) / bend_range_semitones * 8192)
    return max(0, min(16383, value))


def clamp_velocity(velocity):
    try:
        v = int(velocity)
    except (TypeError, ValueError):
        return 100
    return max(1, min(127, v))


class ChannelAllocator:
    """Round-robin MPE channels 1..15 (mido channels are 0-based).

    Channel 0 is left alone so a non-MPE fallback, if ever used,
    does not fight the per-note channels.
    """

    def __init__(self, use_mpe=True):
        self.use_mpe = use_mpe
        self._next = 1  # mido channel number, 1..15 for MPE
        self._by_id = {}  # id -> (midi_note, channel)

    def allocate(self, note_id, midi_note):
        if not self.use_mpe:
            self._by_id[note_id] = (midi_note, 0)
            return 0
        if note_id in self._by_id:
            return self._by_id[note_id][1]
        channel = self._next
        self._next = 1 + (self._next % 15)  # 1..15, then wrap
        self._by_id[note_id] = (midi_note, channel)
        return channel

    def release(self, note_id):
        return self._by_id.pop(note_id, None)

    def active(self):
        return dict(self._by_id)


# ---------------------------------------------------------------------------
# MIDI transport (mido / python-rtmidi). Kept separate from the maths above.
# ---------------------------------------------------------------------------

class MidiSender:
    def __init__(self, port_name, bend_range=2.0, use_mpe=True):
        try:
            import mido
        except ImportError as exc:
            raise SystemExit(
                "mido is not installed. Run: pip install mido python-rtmidi\n"
                f"({exc})"
            ) from exc
        self.mido = mido
        self.bend_range = bend_range
        self.allocator = ChannelAllocator(use_mpe=use_mpe)
        # virtual=True creates the port; it appears in QjackCtl's ALSA tab.
        self.port = mido.open_output(port_name, virtual=True)
        print(f"MIDI out: virtual port '{port_name}' (ALSA tab in QjackCtl)")
        print("  For JACK MIDI synths, bridge it with a2jmidid (see README).")

    def close(self):
        try:
            self.all_notes_off()
        finally:
            self.port.close()

    def _send(self, msg):
        self.port.send(msg)

    def note_on(self, note_id, freq=None, midi=None, bend_cents=None,
                velocity=100):
        mido = self.mido
        if freq is not None:
            midi_note, cents, bend = freq_to_midi_bend(freq, self.bend_range)
        elif midi is not None:
            midi_note = int(midi)
            cents = float(bend_cents or 0.0)
            bend = bend_value_from_cents(cents, self.bend_range)
        else:
            raise ValueError("note_on needs freq or midi")
        channel = self.allocator.allocate(note_id, midi_note)
        # Bend first, so the note starts already bent, not sliding in.
        self._send(mido.Message("pitchwheel", channel=channel, pitch=bend - 8192))
        self._send(mido.Message(
            "note_on", channel=channel, note=midi_note,
            velocity=clamp_velocity(velocity)))
        print(f"  on  id={note_id!r} midi={midi_note} ch={channel} "
              f"bend={cents:+.1f}c vel={clamp_velocity(velocity)}")

    def note_off(self, note_id, midi=None):
        mido = self.mido
        found = self.allocator.release(note_id)
        if found is not None:
            midi_note, channel = found
        elif midi is not None:
            midi_note, channel = int(midi), 0
        else:
            return
        self._send(mido.Message("note_off", channel=channel, note=midi_note))
        print(f"  off id={note_id!r} midi={midi_note} ch={channel}")

    def raw(self, data):
        self._send(self.mido.Message.from_bytes(list(data)))

    def all_notes_off(self):
        mido = self.mido
        for _note_id, (midi_note, channel) in self.allocator.active().items():
            self._send(mido.Message("note_off", channel=channel, note=midi_note))
        self.allocator = ChannelAllocator(use_mpe=self.allocator.use_mpe)
        for channel in range(16):
            self._send(mido.Message("control_change", channel=channel,
                                    control=123, value=0))


def handle_message(sender, message):
    """One JSON dict -> MIDI. Returns a dict to send back, or None."""
    kind = message.get("type")
    if kind == "note_on":
        sender.note_on(
            note_id=str(message.get("id", message.get("midi", "?"))),
            freq=message.get("freq"),
            midi=message.get("midi"),
            bend_cents=message.get("bend_cents"),
            velocity=message.get("velocity", 100),
        )
    elif kind == "note_off":
        sender.note_off(note_id=str(message.get("id", "?")),
                        midi=message.get("midi"))
    elif kind == "raw":
        sender.raw(message.get("bytes", []))
    elif kind == "all_notes_off":
        sender.all_notes_off()
    elif kind == "ping":
        return {"type": "pong"}
    else:
        return {"type": "error", "message": f"unknown type: {kind!r}"}
    return None


def run_test(sender):
    """Play plain notes, then a bent note, with pauses for connecting."""
    import time
    print("Test: connect MuseSynth to your synth in QjackCtl, then press Enter.")
    print("  (If you already connected it, just press Enter now.)")
    input()
    scale = [60, 62, 64, 65, 67, 69, 71, 72]
    print("Test 1: plain C major, one note at a time.")
    for note in scale:
        sender.note_on(note_id=f"test-{note}", midi=note, velocity=90)
        time.sleep(0.45)
        sender.note_off(note_id=f"test-{note}")
        time.sleep(0.05)
    print("Test 2: A 440 Hz, then A +35 cents (MPE bend).")
    print("  If test 2 sounds identical to plain A, the receiving patch")
    print("  is ignoring pitch bend. See README for the VCV PW patch.")
    sender.note_on(note_id="test-a", midi=69, bend_cents=0, velocity=90)
    time.sleep(0.7)
    sender.note_off(note_id="test-a")
    time.sleep(0.2)
    sender.note_on(note_id="test-a-bent", midi=69, bend_cents=35, velocity=90)
    time.sleep(0.7)
    sender.note_off(note_id="test-a-bent")
    print("Test done.")


async def serve(sender, host, ws_port):
    try:
        import websockets
    except ImportError as exc:
        raise SystemExit(
            "websockets is not installed. Run: pip install websockets\n"
            f"({exc})"
        ) from exc

    async def handler(websocket):
        print(f"Browser connected from {websocket.remote_address}")
        try:
            async for text in websocket:
                try:
                    message = json.loads(text)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps(
                        {"type": "error", "message": "not JSON"}))
                    continue
                try:
                    reply = handle_message(sender, message)
                except Exception as exc:  # keep the server alive
                    reply = {"type": "error", "message": str(exc)}
                if reply is not None:
                    await websocket.send(json.dumps(reply))
        finally:
            sender.all_notes_off()
            print("Browser disconnected, all notes off.")

    print(f"WebSocket listening on ws://{host}:{ws_port}")
    print("Open midi-test.html in a browser and press Connect, or use the")
    print("full synth page once it is built. Ctrl-C to stop.")
    async with websockets.serve(handler, host, ws_port):
        import asyncio
        await asyncio.Future()  # run forever


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--ws-port", type=int, default=8765)
    parser.add_argument("--port-name", default="MuseSynth")
    parser.add_argument("--bend-range", type=float, default=2.0,
                        help="pitch-bend range in semitones, must match "
                             "the receiving synth (default 2)")
    parser.add_argument("--no-mpe", action="store_true",
                        help="share channel 0 instead of per-note channels")
    parser.add_argument("--test", action="store_true",
                        help="play a test scale, no WebSocket server")
    args = parser.parse_args(argv)

    sender = MidiSender(args.port_name, bend_range=args.bend_range,
                        use_mpe=not args.no_mpe)
    try:
        if args.test:
            run_test(sender)
        else:
            import asyncio
            asyncio.run(serve(sender, args.host, args.ws_port))
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        sender.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
