from abc import *


class ProviderMeta(metaclass=ABCMeta):
    def __init__(self, session):
        self.session = session

    @abstractmethod
    def retrieve(self, entry_type, entry):
        pass

    @abstractmethod
    def record(self, message):
        pass

    @abstractmethod
    def migrate(self):
        pass
