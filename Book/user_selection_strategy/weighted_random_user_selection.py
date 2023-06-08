import random

from Book.user_selection_strategy.user_selection import UserSelectionStrategy


class WeightedRandomUserSelectionStrategy(UserSelectionStrategy):
    def select_user(self, registered_users):
        # Assign weights based on user's credit and VIP status
        weights = []
        for user in registered_users:
            if user.is_user_vip():
                weight = user.credit * 1.1  # VIP members have 10% higher weight
            else:
                weight = user.credit
            weights.append(weight)
        # Select a user based on weights
        return random.choices(registered_users, weights=weights, k=1)[0]
