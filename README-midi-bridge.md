# MuseSynth MIDI bridge: try it with QjackCtl and VCV Rack

This is a test of the MIDI chain only. The test page makes no sound
by itself. If this works, the full synth can later send the same
messages, and the only new work is the synth engine, not the plumbing.

Files here:
- `midi-bridge.py` - WebSocket (localhost:8765) to virtual ALSA MIDI port
- `midi-test.html` - plain notes plus a bent-note test, in a browser
- `scala-modes.json` - the named Scala modes list, parsed and filtered
- `DESIGN-DECISIONS.md` - the decisions locked in from your last message

Note: this was built on the Muse VM, which has no JACK, QjackCtl, or
VCV Rack, so the live test on your Peppermint machine is the real
verification. The bridge maths (nearest note plus bend) was unit-tested
here; the QjackCtl wiring below is what you are testing there.

## 1. Install (once, on your audio machine)

```sh
pip install mido python-rtmidi websockets
```

If pip refuses to install into the system Python, use a venv:

```sh
python3 -m venv ~/musesynth-venv
~/musesynth-venv/bin/pip install mido python-rtmidi websockets
~/musesynth-venv/bin/python midi-bridge.py
```

## 2. Start in this order

1. Start JACK in QjackCtl.
2. Make sure `a2jmidid -e` runs in QjackCtl Setup > Options >
   Execute script **after** Startup, not on Startup. Restart JACK
   after changing this. This is the same bridge already used for
   Rosegarden, because Rosegarden is ALSA MIDI only and Ardour is
   JACK MIDI only.
3. Start VCV Rack.
4. Start the bridge:
   ```sh
   python3 midi-bridge.py
   ```
   You should see: `MIDI out: virtual port 'MuseSynth' (ALSA tab in QjackCtl)`
5. In QjackCtl, open Connections.

## 3. Connect in QjackCtl

VCV Rack can use either MIDI driver, and the connection tab changes
with it. Pick one and stick to it for the test:

**If VCV Rack is set to the ALSA driver:**
- ALSA tab: connect `MuseSynth` (output) to VCV Rack's MIDI input.
- No a2j step is needed, because both sides are ALSA.

**If VCV Rack is set to the JACK driver:**
- MIDI tab: connect the `a2j` client for MuseSynth to VCV Rack's
  MIDI input. a2jmidid mirrors every ALSA port as a JACK port, so
  MuseSynth should appear there as an a2j client.
- If it does not appear, check QjackCtl Messages for an a2jmidid
  error, and check `ps -C a2jmidid` in a terminal.

In VCV Rack, add a MIDI-CV module, set it to the driver and device
you just connected, and patch its V/Oct and Gate outputs to a
simple oscillator and envelope, as you normally would.

## 4. Test without a browser first (recommended)

```sh
python3 midi-bridge.py --test
```

Press Enter when prompted. It plays a plain C major scale, then
A 440 Hz, then A bent +35 cents. This separates two questions:

- If the scale is silent, the connection or the VCV patch is wrong.
- If the scale sounds but the bent A sounds identical to plain A,
  the connection is right and the receiving patch is ignoring pitch
  bend. See section 6.

## 5. Test from the browser

1. Keep the bridge running (without `--test` this time).
2. Open `midi-test.html` in Chromium or Brave. Any browser works
   for this test, because it uses WebSocket, not Web MIDI.
3. Press Connect, then the plain note buttons, then the bent buttons.
4. Watch the log at the bottom of the page and the bridge terminal.
   Both should agree on what was sent.

## 6. If VCV Rack ignores pitch bend

This is the most likely surprise, and it is not a bridge bug.
The bridge sends the nearest MIDI note plus a per-note bend
(MPE channels 1-15, bend range 2 semitones by default).

Try this patch:
- MIDI-CV V/Oct -> oscillator pitch, as normal.
- MIDI-CV PW (pitch wheel) output -> an attenuator/offset, summed
  into the same oscillator pitch input.
- Set the attenuator so that a full bend matches the bridge's
  bend range (2 semitones by default). Start with the PW output
  unattenuated and adjust by ear with the +35 cent test button:
  the bent A should sit audibly sharp of plain A, by much less
  than a semitone.

If your VCV patch has an MPE mode, try that first, with the same
bend range on both sides. If neither works, tell me which VCV
MIDI module you are using and what its PW output does, and we
will match the bridge to it rather than guessing further.

Other checks:
- Notes stuck on: the bridge sends all-notes-off when the browser
  disconnects, and you can send `{"type": "all_notes_off"}` from
  the test page log path by reconnecting. In VCV, a stuck gate
  usually means a note-off went to a different channel, which
  should not happen with the id-matched note-offs in this script.
- Port not listed: the bridge must be running, and mido /
  python-rtmidi must be installed in the same Python you run it
  with. The script prints a clear install message if either is missing.
- Browser cannot connect: the bridge prints
  `WebSocket listening on ws://127.0.0.1:8765`. Open the test page
  from the same machine, not from another device, unless you
  restart the bridge with `--host 0.0.0.0` (only on a trusted
  local network, and only for testing).

## 7. What this proves, and what it does not

Proves: page -> bridge -> QjackCtl -> VCV Rack, with correct
nearest-note plus bend messages.

Does not prove: the full synth engine, the scale finder, or
Rosegarden MusicXML. Those are separate modules, built next,
and they will reuse this bridge unchanged.
