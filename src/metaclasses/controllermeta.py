from abc import *


class ControllerMeta(metaclass=ABCMeta):
    @abstractmethod
    def retrieve(self, search_id, search_type, provider, user, entry_type):
        pass

    @abstractmethod
    def validate(self, message, user):
        pass

    @abstractmethod
    def record(self, message, provider, user):
        pass

    @abstractmethod
    def migrate(self):
        pass
