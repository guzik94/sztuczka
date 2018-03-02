from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.optimizers import Adam

import random
import numpy as np


class Model:
    def __init__(self, param_choices, load_path=''):
        self.model = None
        self.minibatch_size = param_choices.get('minibatch_size', 32)
        self.neurons = param_choices.get('neurons', [20, 20])
        self.learning_rate = param_choices.get('learning_rate', 0.001)
        self.discount = param_choices.get('discount', 0.9)
        self.load_path = load_path

    @property
    def not_built(self):
        return self.model is None

    def train(self, experiences):
        if self.model is None:
            raise RuntimeError('Model not built.')
        # sample experience
        samples = random.sample(range(len(experiences)), self.minibatch_size)
        samples = [experiences[i] for i in samples]

        for state, action, reward, next_state in samples:
            discounted_future_reward = self.discount * np.amax(self.model.predict(next_state))
            target = reward + discounted_future_reward
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)

    def predict(self, arg):
        return self.model.predict(arg)

    def build_model(self, obs_size, action_size):
        if self.load_path != '':
            self.model = load_model(self.load_path)
            print('Model loaded from %s' % self.load_path)
            return

        model = Sequential()
        for i, n in enumerate(self.neurons):
            if i == 0:
                model.add(Dense(n, input_shape=obs_size, init='uniform', activation='relu'))
            else:
                model.add(Dense(n, init='uniform', activation='relu'))

        model.add(Dense(action_size[0], init='uniform', activation='linear'))
        opt = Adam(lr=self.learning_rate)
        model.compile(loss='mse', optimizer=opt)

        self.model = model
