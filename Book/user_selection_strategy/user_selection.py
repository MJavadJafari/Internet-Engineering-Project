from abc import ABC, abstractmethod


class UserSelectionStrategy(ABC):
    @abstractmethod
    def select_user(self, registered_users):
        pass

