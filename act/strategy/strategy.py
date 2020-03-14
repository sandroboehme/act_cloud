
from abc import ABC, abstractmethod


class Strategy(ABC):

    def __init__(self):
        self.data = None

    @abstractmethod
    def process_next_candle(self):
        pass

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data
