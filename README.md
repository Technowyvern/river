# River
A functional programming inspired digital audio creation module for python outputting to .wav files using scipy

## Usage
River can be used, but it is a package, that I have not packaged in an installable way so you need to stick the source folder in somewhere on your PYTHONPATH. Then you can import the useful bits by doing something like
```python
from river import Track
import river.synthesizer as synth
```
and then build a track with something like this example that uses with from river.synthesizer import * because I'm lazy
```python
from river import Track
from river.synthesizer import *

samplerate = 44100

track = Track(0.25*14,samplerate)

cmajor = [261.6,293.7,329.7,349.2,392,440,493]

sawtooth_instrument = work_on_scale(phase_shift(instrument(sawtooth,samplerate),[0,2,4]),cmajor)

track.register(
    part(
        instrument=sawtooth_instrument,
        tempo=2,
        samplerate=samplerate,
        instructions=((i,0.25,0.25) for i in [0,1,2,3,4,5,6,6,5,4,3,2,1,0])
    )
)

track.write("example.wav")
```
and example.wav will be the example provided in this repo