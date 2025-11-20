from abc import ABC, abstractmethod

class Strategy(ABC):

    @abstractmethod
    def calc_indicator(self):

        pass

    @abstractmethod
    def calc_position(self):

        pass

    @abstractmethod
    def plot_pos_chart(self):

        pass