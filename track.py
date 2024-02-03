import numpy as np
from typing import TextIO
from scipy.io.wavfile import write as write_wav
from numbers import Real
from collections.abc import Iterable

class Track:
    def __init__(self,duration:Real|None, samplerate:int) -> None:
        self.samplerate=samplerate
        self._registered_streams = []
        self.duration = duration
        self._amplitudes = None
    

    def cache_registered_streams(self,duration:Real|None=None):
        '''Write the registered streams to the track's stored value array. 
        
        Writes up to self.duration seconds of each stream to the array if duration is None, otherwise it writes duration seconds of each stream to the array. Raises an error if both are None.

        You probably should not be caching streams manually, and just be calling the write() method instead.'''
        if self.duration is not None:
            duration=self.duration
        if duration is None:
            raise ValueError("Provided duration and self.duration are both None, so no duration could be resolved.")

        samples = int(self.samplerate*duration)

        if self._amplitudes is None:
            self._amplitudes = np.zeros(samples)
        
        elif len(self._amplitudes)<samples:
            np.concatenate(self._amplitudes,np.zeros(len(self._amplitudes)-samples))

        for stream in self._registered_streams:
            for ind,val in zip(range(samples),stream):
                self._amplitudes[ind]+=val
    
    def write_cache_to_wav(self,file:TextIO|str):
        '''Write the cached values to the file located at the given path or open file handle.
        
        You probably want to use the write() method instead, as that caches registered streams beforehand'''
        write_wav(file,self.samplerate,self._amplitudes.astype(np.float32))
    
    def write(self, file:TextIO|str, duration:Real|None=None):
        '''Writes all the registered streams to the provided file located at the given path or open file handle.
        
        If a duration is not None it is used, otherwise self.duration seconds of each stream is written to the file. If both are None an error is raised as it's impossible to figure out a length for the track'''
        self.cache_registered_streams(duration)
        self.write_cache_to_wav(file)

    def register(self,stream:Iterable[float]):
        '''Registers some iterable stream to the track, stream is interpreted as being amplitudes of the produced sound by the stream, on a range of -1 to 1'''
        self._registered_streams.append(stream)