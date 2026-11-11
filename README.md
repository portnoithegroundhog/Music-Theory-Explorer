# Music-Theory-Explorer

What this is, and what it is for
Music Theory Explorer is a synthesizer for learning music theory by ear. You choose a scale, hear it, play it on a keyboard, look at its notes and intervals, find other scales like it, and record what you play. It works for the familiar 12-note scales and for microtonal scales, scales with steps smaller than a semitone, and scales with more or fewer notes than twelve, up to twelve notes in a scale.

It is made for beginners who happen across it while searching for music education, and for experienced players who want to hear a scale before they try to name it. You do not need to read sheet music to use it. Everything is played, heard, and shown as numbers: note names, frequencies in hertz, and cents, where 100 cents is one semitone and 1200 cents is one octave.

It is a dream synth, built to be played. It is not a replacement for any other program, and it does not try to be. If you already love another scale or synthesis program, keep using it. This one is for exploring scales by ear, in one page, on your own machine.

One file, no server, no external dependencies, nothing sent anywhere except to the local MIDI bridge on your own machine, and only if you turn MIDI out on. See the MIDI bridge section below.

Download and use offline
This page can be downloaded and used offline with full functionality. On the main page, click Download this page for offline use. Save the downloaded file, open it in a browser, and everything works: scales, keyboard, finder, recorder, and exports. You do not need an internet connection, and you do not need to install anything to use the built-in sound.

The only extra file you need, and only if you want MIDI out, is midi-bridge.py, in the same folder as the main page. The main page assumes the bridge file is in the same folder, for simplicity.

Available downloads in the same folder: the main page (synth.html, titled Music Theory Explorer), this about page (about.html), midi-bridge.py, and midi-test.html, a browser test page for the bridge that makes no sound itself.

How to use each section, in order
1. Scale
Choose a bell note, also called the tonic or root, and an octave. The default is A4, 440 hertz, the standard tuning pitch. Then type a step pattern, for example 2-2-1-2-2-2-1 for Major, where the numbers are steps in the equal temperament the pattern adds up to. That pattern adds up to 12, so it is a 12-note temperament, 12-EDO. Click Apply step pattern. Below that are built-in scales, Major, Natural Minor, Major Pentatonic and Harmonic Minor, which work even without the named list. A scale may have at most 12 notes here. A step pattern itself has no upper limit on the temperament, so you can enter a pattern that adds up to 47, 49, or even 537, and play it, even if the finder below would not try to list every scale in such a large temperament.

2. Named scale lookup
Search by name or by step pattern, for example Major, pentatonic, or 2-2-3-2-3. Click a result to load it into the keyboard, statistics and chord buttons, with the bell note and octave you already chose. The named list is embedded in the main page, so it works even when you open the page directly with file://, with no separate file fetch needed. If the list ever fails to load, the built-ins and manual step-pattern entry still work.

3. Statistics
For the scale you loaded, the table shows each degree: its note name, with a plus or minus if it is sharpened or flattened from the nearest ordinary note, its interval from the tonic, its frequency, its cents from the tonic, and its cents from the previous degree. Use this to see, not just hear, how a scale is built. The summary line above the table gives the scale name, step pattern, temperament, note count, step size in cents, and bell note and frequency.

4. Synth voice, and effects
Voicing sets the timbre. There are 20 voicings: Pure sine, Flute, Pan flute, Glass harmonica, Theremin, Organ, Clarinet (odd harmonics only), Oboe / reed, Voice / choir vowel (a vowel approximation with two formants, not a singer), Brass, String pad, Square lead, Saw lead, Bass, Pluck, Harp, Guitar, Marimba, Vibraphone, and Bell (FM, inharmonic). They are parameter presets over a few engines, not recordings. The old Waveform dropdown is kept only as a fallback for older saved recordings; voicing wins.

Master volume is the overall loudness. Attack, Decay, Sustain and Release (ADSR) shape how a note starts, falls, holds, and ends. Sustained voices follow ADSR. Percussive voices, Pluck, Harp, Guitar, Marimba, Vibraphone and Bell, decay on their own and ignore Sustain, like a real plucked string; releasing early damps them.

Effects add colour and flavour to the voices and to the basic wave shapes. They are not meant to replace the plugins you may already use in Audacity or elsewhere. Each effect has an on/off switch, a slider, and a number box with the same value, so you can drag or type an exact number. The chain, in order, is: voice, then distortion / harmonics, then high-pass / low-pass filters, then chorus, then delay, then reverb, then master volume. One shared effects bus serves every voice, so live playing, playback, and the WAV export all sound the same. The effects are:

Distortion: drive and mix. More drive means more saturation and more edge.
Harmonics: amount, blending extra 2nd and 3rd harmonics into the voice.
High-pass / Low-pass: cutoff in hertz each. High-pass removes low frequencies below the cutoff; low-pass removes high frequencies above it.
Chorus: rate, depth and mix. A modulated delay that thickens the sound.
Delay: time in milliseconds, feedback, and mix. Feedback is capped below 1, so it cannot run away, but high feedback can still sound very strange.
Reverb: decay time and mix. The reverb impulse is generated inside the page, with no external file.
Superposition: a second waveform layered on the voice, with its own waveform, detune in cents, and mix. This is the old idea of stacking waveforms and detuned pairs.
Vibrato (global): rate and depth in cents, applied to all voices. It stacks with theremin vibrato, which already has its own.
Tremolo (global): rate and depth, a regular loudness wobble.
Effects bypass: one switch for dry only, so you can compare with and without effects in one click.
Ranges are wide on purpose. Extreme settings are allowed to sound weird. That is part of exploring.

Click / metronome: BPM and click volume, with an on/off switch. The click is dry, it does not go through effects, and it is not recorded and not exported. It is only for playing along to.

5. MIDI bridge output
By default, local sound is on and MIDI out is off. Nothing leaves the page unless you turn MIDI out on and connect to the bridge. The bridge is a small Python program, midi-bridge.py, that you run on your own machine. It takes notes from the page over a local WebSocket, at ws://127.0.0.1:8765, and turns them into MIDI on a virtual port called MuseSynth. Each note sends its frequency, its nearest MIDI note, and its bend in cents, so microtonal notes sound in tune, not just at the nearest semitone, on a synth that understands pitch bend. Chords use separate MIDI channels, 1 to 15, so each note can bend independently. See the full bridge guides below.

6. Keyboard
Play with the mouse or touch, or with QWERTY keys. There are four rows of ten keys: z to / (lowest), then a to ;, then q to p, then 1 to 0 (highest). In Per-row anchored mode, each row starts at its own octave and cycles the scale across its ten keys, so a 3-note scale repeats across a row and a 10-note scale fills a row exactly. In Continuous 40-key mode, the keys run in order across all four rows, so with 11 or 12 notes you can reach every degree. QWERTY playing is disabled while you are typing in a text box, so typing a step pattern does not sound notes. Pressing a key starts its note; releasing it stops it.

7. Chords of the current mode
Triads are built on each degree from degrees 0, 2 and 4 above it, wrapping up an octave when needed. Dyads are adjacent degrees. Hold a button down to hear the chord; release to stop it. The adjacent dyads are kept on purpose: they let you hear, quickly, when two neighbouring notes in a scale are dissonant or not, which is not the same question as hearing every possible pair in the scale.

Below the triads and dyads is a button, Open chord reference page for this mode, which becomes enabled when a mode is loaded for play. It opens a separate, generated page listing every 2, 3 and 4-note chord in the current mode, grouped by first note, each playable on click, with one sound only: glass harmonica, because it chords well and does not get ringy. That page is a listening reference for playing the keyboard on the main page, not a printed table.

8. Scale finder
Find scales by temperament (EDO), note count, and minimum interval in cents, with presets 38.71, 50, 100, 150, 200 and 300 cents. The smallest preset, 38.71 cents, is the 31-note temperament interval, 1200 divided by 31. The finder first shows an estimated count, so it does not try to list millions of scales at once and crash the browser, as the old program did above 47-EDO. If the estimate is small, you get the full filtered list. If it is large, you get a streamed top list, best evenness first, with progress and Cancel. Evenness is measured by how close the steps are to the mean step. Two extra filters, Must include step and Must include sub-pattern, are requirements, not upper bounds: they are applied before the top list is chosen, so a scale containing the step you want cannot be buried below the cutoff. You can also generate the full filtered list as text, with a preview, download, and copy, without rendering hundreds of thousands of lines on the page. Click a finder result, then a mode, to load it into the keyboard with your current bell note and octave. The finder lists step patterns only, with no frequencies, until you choose a mode; tuning runs lazily for that one mode.

9. Recorder and exports
Press Record, play the keyboard or a chord button, then press Stop recording. The event list is not shown while recording, to avoid display lag; it appears when you stop. Each event keeps its own frequency, cents from tonic, nearest MIDI note and bend, start time and duration, and the scale snapshot from when recording started, so changing the scale afterwards does not change the recording. Play recorded plays it back through local sound, with the current voicing, effects, ADSR and master volume, and playback is never re-recorded and does not send MIDI out. You can delete individual events.

Exports are all rendered from the same event list, so they agree with each other. Timing is real time and gridless: no quantization, except that the MusicXML export has to quantize to its divisions grid, as explained below.

JSON: exact ground truth, scale snapshot, settings, and every event.
MIDI (MPE, exact): Standard MIDI File, 480 ticks per quarter, 120 beats per minute as a clock, per-note bend on channels 1 to 15, bend range 2 semitones. This is the exact microtonal record for other programs.
MIDI (quantized, 12-TET): nearest notes, no bend, all on channel 0, clearly labelled. Use this only when a program cannot handle bend.
MusicXML for Rosegarden: 12-note temperament only, integer sharps and flats only, nearest note, labelled as an approximation. It uses 100/4 time, so a whole take fits in one or two very long measures, instead of being split across four-beat barlines. Its value is not readable sheet music: it lets you import the played thing into Rosegarden, assign instruments to it, and re-record it with a synth oboe or violin sound. Exact microtones are in the JSON and MPE MIDI.
WAV: rendered from the synth's own voice, 44100 hertz, mono, with the current voicing, effects, ADSR and master volume. Recordings over 600 seconds are refused for WAV; use JSON or MIDI for longer recordings. The default master volume is 25%, which was found to be the sweet spot in Audacity for chord renders. If a render at a higher volume would clip, the WAV export scales the whole render down to a peak of 0.95 instead of hard-clipping, and says so in the status line, so dynamics are preserved.
Load JSON recording: load a saved JSON recording back in, to play it again or re-export it.
The MIDI bridge, in detail
Install and run the bridge (Linux / Unix / BSD)
Download midi-bridge.py into the same folder as the main page.
Install the dependencies. Either with pip:
python3 -m pip install mido python-rtmidi websockets
or, on Debian / Ubuntu / Peppermint, with apt:
sudo apt install python3-rtmidi python3-websockets (plus mido from your distribution if it is available). If pip and apt disagree, a virtual environment works too: python3 -m venv ~/musesynth-venv, then ~/musesynth-venv/bin/pip install mido python-rtmidi websockets, then run the bridge with that Python.
In a terminal, in that folder, run:
python3 midi-bridge.py
Leave the terminal running. The bridge listens on your own machine only, at ws://127.0.0.1:8765, and opens a virtual ALSA MIDI port called MuseSynth.
On the main page, section 5, click Connect to MIDI bridge, then tick MIDI out on.
To test the bridge alone, without the main page, open midi-test.html in a browser. It has plain-note buttons and bent-note buttons (A, A +35 cents, A -40 cents) and a log. It makes no sound itself; it only sends MIDI through the bridge.
If the bridge says a module is missing, that is the install step above, not a fault in the page. The bridge also has a --no-mpe mode, all notes on channel 0, for one-channel or monophonic synths, and a --test mode that plays a plain scale, then A, then A bent by 35 cents. Do not use a very large bend range with a synth whose default bend range is 2 semitones; the bridge default is 2 semitones for that reason.

With QjackCtl (JACK)
QjackCtl is only the control panel for JACK; JACK itself must be running, started from QjackCtl, and left running while you play. The order matters: JACK first, then the bridge, then the program you want to play, so MuseSynth already exists when that program opens and looks for MIDI devices. If you open the program first, its saved device may fall back to something else.

In QjackCtl, there are two tabs that matter. In the MIDI tab, connect the MuseSynth output to the input of the program you want to play. In the Audio tab, connect that program's audio outputs to system playback, so you can hear it. A program does not always connect its own audio automatically.

Do not use Midi Through. Midi Through is a loopback port, not the bridge. If you see MuseSynth connected only to Midi Through, and Midi Through looped back to itself, that is the fault: connect MuseSynth directly to the program's input instead, and disconnect MuseSynth from Midi Through.

On this Linux setup, JACK and ALSA audio do not run at the same time. It is one or the other for audio. So use all-JACK while JACK is running, or all-ALSA with JACK stopped, not a mix of ALSA MIDI and JACK audio inside one program, unless that program is explicitly routing MIDI through the JACK mirror (a2j) as described for VCV Rack below.

With Rosegarden
Rosegarden has two uses here. First, import a MusicXML file from the recorder, section 9. Rosegarden can import MusicXML in 100/4, which is what the main page exports. Import the file, assign an instrument to each track, and play or re-record the same thing you played, with a synth oboe or violin sound, or any other instrument you assign. The MusicXML is a 12-note approximation, as above; for exact microtones, use the MPE MIDI file instead, or record live MIDI from the bridge into Rosegarden, below.

Second, record live MIDI from the bridge. With JACK running and the bridge running, route MuseSynth to Rosegarden's MIDI input in QjackCtl's MIDI tab, arm a track in Rosegarden, and play the main page keyboard. Rosegarden records the notes, with bend, and you can then assign instruments and play them back. Rosegarden's MusicXML support is old and narrow, so keep to the main page's safe subset: one part, no layout, integer sharps and flats, and the 100/4 time signature the page already uses.

Audio for Rosegarden sessions in this setup lives on a separate audio drive, not on the system drive, and the usual chain here is Rosegarden to QSynth to Audacity, with QSynth as the synth source. See the QSynth note under Audacity below for the soundfont point.

With Audacity, without JACK
You do not need JACK, the bridge, or any MIDI at all to record the built-in sound into Audacity. Play the main page in a browser, with local sound on, and record in Audacity from the internal monitor, that is, from the system sound output, not from a microphone. That path is proven: the synth's Web Audio sound goes to system sound, and Audacity captures it from the internal monitor.

If you do use QSynth, as a synth source for Rosegarden or for the bridge, remember that QSynth makes no sound unless a soundfont is loaded, and its audio outputs, left and right, must be connected to system playback in QjackCtl's Audio tab. Plain notes from the bridge go to QSynth directly in the ALSA tab, with no a2j step, because both are ALSA. Bent notes work in QSynth at its default 2-semitone bend range, which matches the bridge default.

Audacity troubleshooting, from experience: Audacity sometimes freezes while working on a project with a single window open, where keyboard navigation still works but the mouse does not. Before killing Audacity, which would lose unsaved work, try this keyboard-only reset: press Ctrl+N to open a second Audacity window, then Alt+F4 to close that second window. Mouse control usually returns to the original project window. Save the project right after the mouse returns.

With VCV Rack
VCV Rack here is version 1.1.6, the version that loads the older modules used here. Rack 1 plugins do not load in Rack 2, so do not mix major versions. On Linux, unzip the Rack download, make sure zenity is installed, and run ./Rack.

Order, again: JACK running, then bridge running, then Rack started, so MuseSynth exists in Rack's device list. If Rack was opened first, restart it.

Use all-JACK while JACK is running. In the MIDI-CV module, set MIDI Driver to JACK, MIDI Device to a2j:MuseSynth (the JACK mirror of the bridge port), and MIDI Channel to All Channels. In QjackCtl's MIDI tab, connect a2j MuseSynth capture to VCV Rack input. Do not use a2j Midi Through, for the same reason as above. For a first test, run the bridge with --no-mpe, and in MIDI-CV set Polyphony Channels to 1. For the default MPE bridge later, set Polyphony Mode to MPE and Polyphony Channels to 16.

In the AUDIO-8 module, set Audio Driver to JACK and Audio Device to system. Then, in QjackCtl's Audio tab, manually connect VCV Rack outputs 0 and 1 to system playback 1 and 2. VCV does not connect JACK audio cabling automatically.

A working first patch is: MIDI-CV V/OCT to VCO V/OCT, MIDI-CV GATE to ADSR GATE, VCO output to VCF input, VCF low-pass output to mixer input 1, ADSR output to mixer CV 1, mixer mix output to AUDIO-8 inputs 1 and 2, with the filter cutoff open. If the GATE light does not move, the MIDI driver, device or channel is wrong. If GATE moves but the audio meters do not, the patch, ADSR or mixer is wrong. If the meters move but you hear nothing, the audio driver, device, or QjackCtl audio connection is wrong.

Two Rack traps, learned the hard way. First, in Rack 1 you stack cables on an output to send one signal to several places, not on an input to sum two signals. To add pitch bend (PW) to V/OCT, you need a separate mixer or summer module first, then that output to VCO V/OCT. Second, if Rack suddenly makes no sound and nothing else changed, it may have crashed; restarting Rack and reloading the saved preset has fixed that before, and is worth trying before changing bridge or synth settings.

Velocity, if you want it: do not plug VEL into the same mixer CV that ADSR already uses, or the channel will drone after release, because VCV sums CVs and VEL is held. For brightness with no extra module, plug VEL to VCF frequency CV, with the cutoff down a bit and the frequency CV knob up. For true loudness, add a VCA between VCF and mixer, plug VEL to VCA CV, and leave ADSR on mixer CV; they are then in series, so velocity scales volume and the envelope still gates.

Copyright and licence
Copyright © 2026 Ed Swain.

This page is published under a GPL non-commercial licence. The licence text is the GNU General Public License, version 3, at https://www.gnu.org/licenses/gpl-3.0.html, with the author's non-commercial condition: please do not sell this page, or use it in a commercial product, without the author's permission.

This page was made by a life long learner with the help of Muse. It is the replacement for Musical Scale Explorer, which was deleted by accident.
