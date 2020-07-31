from abc import *


class ProviderMeta(metaclass=ABCMeta):
    @abstractmethod
    def retrieve(self, search_id, search_type):
        pass

    @abstractmethod
    def record(self, message):
        pass
