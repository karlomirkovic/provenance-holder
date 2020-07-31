from abc import *


class AdapterMeta(metaclass=ABCMeta):
    @abstractmethod
    def retrieve(self, search_id, search_type, provenance_holder, user):
        pass

    @abstractmethod
    def collect(self, message, provenance_holder, user):
        pass
