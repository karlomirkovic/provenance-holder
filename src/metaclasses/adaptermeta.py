from abc import *


class AdapterMeta(metaclass=ABCMeta):
    @abstractmethod
    def retrieve(self, entry, provenance_holder, user, entry_type):
        pass

    @abstractmethod
    def collect(self, message, provenance_holder, user):
        pass
