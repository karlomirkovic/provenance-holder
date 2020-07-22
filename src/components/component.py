from abc import *


# The interface of the components.
class Component(metaclass=ABCMeta):
    @abstractmethod
    def retrieve(self):
        pass

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def record(self, message):
        pass
