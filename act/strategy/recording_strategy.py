from act.strategy.strategy import Strategy


class RecordingStrategy(Strategy):

    def __init__(self):
        self.recorded_iterations = list()

    def process_next_candle(self):
        previous_complete_candle = self.get_data().get_previous_complete_candle()
        print("previous_complete_candle: ", previous_complete_candle)
        current_developing_candle = self.get_data().get_current_developing_candle()
        print("current_developing_candle: ", current_developing_candle)
        self.recorded_iterations.append((previous_complete_candle, current_developing_candle))
        return True
