class Track:
    def __init__(self,samplerate:int, duration:int|None) -> None:
        self.samplerate=samplerate
        self.registered = []
        self.duration = duration
    

    def cache_registered_streams(self,duration:int|None):
        '''Write the registered streams to the tracks write'''
        