
from abc import ABC, abstractmethod


class DataFeed(ABC):

    def __init__(self):
        self.previous_complete_candle = None
        self.current_developing_candle = None

    @abstractmethod
    def got_next_candle(self):
        pass

    def get_previous_complete_candle(self):
        return self.previous_complete_candle

    def get_current_developing_candle(self):
        return self.current_developing_candle

    @abstractmethod
    def load_next_candle(self):
        pass

    @abstractmethod
    def set_store(self, store):
        pass
