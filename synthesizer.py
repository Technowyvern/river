from numbers import Real
import itertools
import math
from collections.abc import Iterable,Sequence
from typing import Callable

# Basic waveforms
def sine(frequency:Real,samplerate:int):
    '''A generator that yields from a sine wave with frequnecy Hz'''
    for i in itertools.count():
        yield math.sin(2*math.pi*i*frequency/samplerate)

def sawtooth(frequency:Real,samplerate:int):
    period=1/frequency
    for i in itertools.count():
        yield 2*((i/samplerate)%period)/period-1

def triangle(frequency:Real,samplerate:int):
    period=1/frequency
    half_period=period/2
    for i in itertools.count():
        yield 4*((abs((i/samplerate)%period-half_period))/period)-1

def square(frequency:Real,samplerate:int):
    period=int(samplerate/frequency/2)
    while True:
        for i in range(period):
            yield 1
        for i in range(period):
            yield -1

#Instrument related capabilities
def instrument(stream_factory:Callable[[Real,int],Iterable[float]],samplerate:int):
    '''Creates a basic "instrument" from the given stream_factory.
    
    stream_factory takes in a frequency and samplerate.
    
    The returned function takes two parameters, frequency, and duration, and produces a note "played" by the instrument for that duration'''
    
    def play(frequency:Real,duration:Real):
        for ind,val in zip(range(int(samplerate*duration)),stream_factory(frequency,samplerate=samplerate)):
            yield val
    return play

def enveloped_instrument(stream_factory:Callable[[Real,int],Iterable[float]],amplitude_envelope:Callable[[Real],Iterable[float]],samplerate:int):
    '''Creates an insturment from the given stream_factory, with amplitude controlled by the amplitude envelope.
    
    stream_facotry and takes a frequency and samplerate.
    
    amplitude is a Callable that could have any parameters but is assumed to take a duration that the note is held for (or key is pressed for a hypothetical live play)'''
    
    def play(frequency:Real,duration:Real):
        for mulitpliter,val, in zip(amplitude_envelope(duration),stream_factory(frequency,samplerate=samplerate)):
            yield mulitpliter*val
    return play

def part(instrument:Callable[[Real,Real],Iterable[float]], tempo:Real|None, instructions: Iterable[tuple[Real|Iterable[Real],Real,Real]],samplerate:int,normalise_chords=True):
    '''Takes an instrument, and instructions, and plays the notes from the instructions at tempo.
    
    instrument is a Callable that takes a frequency and duration (in that order), such as the return value of the provided instrument function
    
    tempo is in Hz (i.e to go from bpm to the units of tempo divide by 60)
    
    instructions is an iterable of a triple of values that is assumed to be in the order frequency, duration played, and delay after playing the note before palying another
    
    If the frequency in an instruction is instead an iterable it is treated like a chord and the notes are played simultaneously. If this happens, if normalise_chords is true, the yielded value is divided by the number of notes in the chord (requires the iterable of the different notes to have __len__)'''
    
    playing={}
    counter=itertools.count()
    tempo=tempo*samplerate
    flag=0
    completed_instructions=False
    instructions=iter(instructions)
    for i in itertools.count():
        if flag!=0:
            flag-=1
        else:
            try:
                frequency,duration,delay = next(instructions)
            except StopIteration:
                completed_instructions=True
            else:
                if hasattr(frequency,"__iter__"):
                    if normalise_chords:
                        playing[next(counter)]=(sum(vals)/len(frequency) for vals in zip(*(instrument(_frequency,duration) for _frequency in frequency)))
                    else:
                        playing[next(counter)]=(sum(vals) for vals in zip(*(instrument(_frequency,duration) for _frequency in frequency)))
                else:
                    playing[next(counter)]=(instrument(frequency,duration))
                flag+=int(samplerate*delay)
        val=0
        _to_remove=[]
        for ind,note in playing.items():
            try:
                val+=next(note)
            except StopIteration:
                _to_remove.append(ind)
        yield val
        for i in _to_remove:
            del playing[i]
        if len(playing)==0 and completed_instructions:
            return

#Other hopefully useful functions
def phase_shift(instrument:Callable[[Real,Real],Iterable[float]],shifts:Iterable[float], normalise:bool=True):
    '''Turns an instrument (such as the one returned from the instrument function in this module) into another instrument that yields the sum of the values of that instrument with frequncy increased by that much
    
    If normalise is True the values returned are divided by the length of shifts (and therefore shifts is required to provide a __len__ method)'''
    if normalise:
        l=len(shifts)
        def play(frequency:Real,duration:Real):
            for vals in zip(*(instrument(frequency+shift,duration) for shift in shifts)):
                yield sum(vals)/l
    else:
        def play(frequency:Real,duration:Real):
            for vals in zip(*(instrument(frequency+shift,duration) for shift in shifts)):
                yield sum(vals)
    return play

def work_on_scale(instrument:Callable[[Real,Real],Iterable[float]],scale:Sequence[float], wrap_around:int=2):
    '''Converts an instrument to work on a scale rather on raw frequency.
    
    wrap_around is assumed to be 2 to work with scales that fall within an octave

    The formula for the frequency played for some note x on a scale with some size l is scale[x%l] * wrap_around**(x//l)'''
    l = len(scale)
    def play(frequency:Real,duration:Real):
        div,mod = divmod(frequency,l)
        note = scale[mod]*(wrap_around**div)
        for val in instrument(note,duration):
            yield val
    return play