from abc import *


class AdapterMeta(metaclass=ABCMeta):
    @abstractmethod
    def retrieve(self, entry, provenance_holder, user):
        pass

    @abstractmethod
    def collect(self, message, provenance_holder, user):
        pass
