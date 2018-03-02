from random import sample
from pygejm.acts import actions
import numpy as np
from collections import defaultdict
import copy


class Actor:
    def __init__(self, name, rect, df, is_interactive=False):
        self.name = name
        self.df = df.copy()
        self.action = actions[0]
        self.last_action = 0
        self._rect = rect
        self.__init_variables_from_rect(rect)

        self.config = {
            "init_mean": 0.0,  # Initialize Q values with this mean
            "init_std": 0.0,  # Initialize Q values with this standard deviation
            "learning_rate": 0.1,
            "eps": 0.1,  # Epsilon in epsilon greedy policies
            "discount": 0.95}

        self.q = defaultdict(
            lambda: self.config["init_std"] * np.random.randn(len(actions.items())) + self.config["init_mean"])
        self.last_obs = []
        self.last_health = self.health
        self.last_action_idx = 0
        self.is_interactive = is_interactive

    def __init_variables_from_rect(self, rect):
        self.df['x'] = rect.x
        self.df['y'] = rect.y
        self.df['h'] = rect.h
        self.df['w'] = rect.w

    @property
    def health(self):
        return self.df.health[0]

    @health.setter
    def health(self, value):
        self.df['health'][0] = value

    def update_rect(self):
        self._rect.x = self.df['x']
        self._rect.y = self.df['y']
        self._rect.w = self.df['w']
        self._rect.h = self.df['h']

    @property
    def rect(self):
        return self._rect

    def get_possible_actions(self):
        return actions

    def act(self, game_state):
        action = self.next_act(game_state)
        self.last_action = action
        return action

    def next_act(self, obs):
        if self.is_interactive:
            tmp = copy.copy(self.action)
            self.action = actions[0]
            return tmp
        # prediction = sum([self.weights.setdefault(pt, 0.0) for pt in coords]) / len(coords)
        future = 0  # np.max(self.q[obs])
        last_reward = self.health - self.last_health

        actions_idxs = []

        if len(self.last_obs) > 0:
            for i in range(len(self.last_obs)):
                self.q[self.last_obs[i]][self.last_action_idx] -= \
                    self.config["learning_rate"] * (
                                self.q[self.last_obs[i]][self.last_action_idx] - last_reward - self.config[
                            "discount"] * future)

                actions_idxs.append(np.argmax(self.q[obs[i]]) if np.random.random() > self.config["eps"] else
                                    sample(list(actions.keys()), k=1)[0])

        if len(actions_idxs) == 0:
            action_idx = 0
        else:
            action_idx = max(set(actions_idxs), key=actions_idxs.count)

        self.last_obs = obs
        self.last_health = copy.copy(self.health)
        self.last_action_idx = action_idx

        return actions[action_idx]


