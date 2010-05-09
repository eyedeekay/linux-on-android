import ril.ril
import threading

class Phone:
    def __init__(self):
        self.state_lock = Lock()
        self.state_lock.acquire()
        self.__class__ = StateUnknown()
        self.transition()
        
    def transition(self):
        pass
        
    

class StateUnknown(Phone):
    pass
    
