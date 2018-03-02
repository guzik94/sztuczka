from pygejm import acts
import numpy as np
import random
from collections import deque
from pygejm.model_resolver import ModelResolver
from pygejm.constants import actor_health, actor_id, none_action_id
from pygejm.visible_object import VisibleObject
import pandas as pd


n_actions = len(acts.actor_actions)
mb_size = 300
max_experiences = 200000


class VisibleActor(VisibleObject):
    def __init__(self, name, rect, is_interactive=False,
                 load_model_path='', model_id=None):
        super().__init__(rect, identifier=actor_id)
        self.health = actor_health
        self.name = name
        self.action = acts.actions[none_action_id]
        self.last_action = 0
        self.rect = rect
        self.last_health = self.health
        self.last_action_idx = 0
        self.is_interactive = is_interactive
        self.discount = 0.85
        self.alive_time = 0
        # epsilon aka how random will actions be
        self.epsilon = 0.4
        self.min_epsilon = 0.05
        self.lower_epsilon_after = 1000
        # last_obs depends on observation size, so we initialize them when we know that value
        self.last_obs = None
        self.model = ModelResolver.resolve(model_id, load_model_path=load_model_path)
        self.experiences = deque()

    def act(self, game_state):
        self.alive_time += 1
        action = self.next_act(game_state)
        self.last_action = action
        return action

    def _save_experience(self, last_reward, obs):
        self.experiences.append((self.last_obs, self.last_action_idx, last_reward, obs))
        if len(self.experiences) > max_experiences:
            self.experiences.popleft()

    def next_act(self, obs):
        if self.is_interactive:
            return
        if len(self.experiences) > 0 and (self.alive_time % (mb_size * 5) == 0):
            self.model.train(self.experiences)

        obs_size = (len(obs), )
        action_shape = (n_actions,)

        if self.model.not_built:
            self.model.build_model(obs_size, action_shape)
        if self.last_obs is None:
            self.last_obs = np.zeros((1, obs_size[0]))

        last_reward = self.health - self.last_health

        obs = obs.reshape((-1, len(obs)))
        print('Input:')
        print(obs)
        Q_sa = self.model.predict(obs)

        print('Predicted action:')
        print(Q_sa)

        # predict
        if np.random.rand() <= self.epsilon:
            action_idx = random.sample(list(range(n_actions)), 1)[0]
        else:
            action_idx = np.argmax(Q_sa)

        self._save_experience(last_reward, obs)

        # if self.alive_time % 1e5 == 0:
        #	self.model.model.save(r'E:\data\game\model.h5')

        if self.alive_time % self.lower_epsilon_after == 0:
            self.epsilon = max(self.epsilon * 0.99, self.min_epsilon)
            print('epsilon: %.2f' % self.epsilon)

        self.last_obs = obs
        self.last_health = self.health
        self.last_action_idx = action_idx

        return acts.Action(acts.actor_actions[action_idx])

    def save_experiences(self):
        data = np.array(list(self.experiences))
        x = data[:, 3]
        pd.DataFrame(x).to_csv(r'~/data/game/x_%d' % self.alive_time)

        y = data[:, 2]
        pd.DataFrame(y).to_csv(r'~/data/game/y_%d' % self.alive_time)
        return
