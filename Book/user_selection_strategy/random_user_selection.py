import random

from Book.user_selection_strategy.user_selection import UserSelectionStrategy


class RandomUserSelectionStrategy(UserSelectionStrategy):
    def select_user(self, registered_users):
        return random.choice(registered_users)
