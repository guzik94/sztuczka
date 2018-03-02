import numpy as np
from keras.models import Model
from keras.layers import Dense, Input
from keras.layers.merge import Add
from keras.optimizers import Adam
import keras.backend as K
import tensorflow as tf

from pygejm.acts import actor_actions


n_action = len(actor_actions)


# determines how to assign values to each state, i.e. takes the state
# and action (two-input model) and determines the corresponding value
class ActorCritic:
    def build_model(self, observation_shape, action_shape):
        self.sess = tf.Session()
        K.set_session(self.sess)
        # ===================================================================== #
        #                               Actor Model                             #
        # Chain rule: find the gradient of chaging the actor network params in  #
        # getting closest to the final value network predictions, i.e. de/dA    #
        # Calculate de/dA as = de/dC * dC/dA, where e is error, C critic, A act #
        # ===================================================================== #
        self.observation_shape = observation_shape
        self.action_shape = action_shape

        self.actor_state_input, self.actor_model = self.create_actor_model()
        _, self.target_actor_model = self.create_actor_model()

        self.actor_critic_grad = tf.placeholder(tf.float32,
                                                [None, self.action_shape[0]])  # where we will feed de/dC (from critic)

        actor_model_weights = self.actor_model.trainable_weights
        self.actor_grads = tf.gradients(self.actor_model.output,
                                        actor_model_weights,
                                        -self.actor_critic_grad)  # dC/dA (from actor)
        grads = zip(self.actor_grads, actor_model_weights)
        self.optimize = tf.train.AdamOptimizer(self.learning_rate).apply_gradients(grads)

        # ===================================================================== #
        #                              Critic Model                             #
        # ===================================================================== #

        self.critic_state_input, self.critic_action_input, self.critic_model = self.create_critic_model()
        _, _, self.target_critic_model = self.create_critic_model()

        self.critic_grads = tf.gradients(self.critic_model.output,
                                         self.critic_action_input)  # where we calcaulte de/dC for feeding above

        # Initialize for later gradient calculations
        self.sess.run(tf.initialize_all_variables())
        self.__built = True

    def __init__(self):
        self.actor_state_input = None
        self.actor_model = None
        self.target_actor_model = None
        self.actor_critic_grad = None
        self.actor_grads = None
        self.optimize = None
        self.critic_state_input = None
        self.critic_action_input = None
        self.critic_model = None
        self.target_critic_model = None
        self.critic_grads = None
        self.__built = False

        self.action_shape = None
        self.observation_shape = None
        self.sess = None
        self.critic_model = None

        self.learning_rate = 0.5
        self.epsilon = 1.0
        self.gamma = .95
        self.tau = .125

    @property
    def not_built(self):
        return not self.__built

    # ========================================================================= #
    #                              Model Definitions                            #
    # ========================================================================= #

    def create_actor_model(self):
        state_input = Input(shape=self.observation_shape)
        h1 = Dense(24, activation='relu')(state_input)
        h2 = Dense(48, activation='relu')(h1)
        h3 = Dense(24, activation='relu')(h2)
        output = Dense(self.action_shape[0], activation='relu')(h3)

        model = Model(input=state_input, output=output)
        adam = Adam(lr=0.5)
        model.compile(loss="mse", optimizer=adam)
        return state_input, model

    def create_critic_model(self):
        state_input = Input(shape=self.observation_shape)
        state_h1 = Dense(24, activation='relu')(state_input)
        state_h2 = Dense(48)(state_h1)

        action_input = Input(shape=self.action_shape)
        action_h1 = Dense(48)(action_input)

        merged = Add()([state_h2, action_h1])
        merged_h1 = Dense(24, activation='relu')(merged)
        output = Dense(1, activation='relu')(merged_h1)
        model = Model(input=[state_input, action_input], output=output)

        adam = Adam(lr=0.5)
        model.compile(loss="mse", optimizer=adam)

        return state_input, action_input, model

    # ========================================================================= #
    #                               Model Training                              #
    # ========================================================================= #

    def _train_actor(self, experience):
        for sample in experience:
            cur_state, action, reward, new_state = sample
            predicted_action = self.actor_model.predict(cur_state)
            grads = self.sess.run(self.critic_grads, feed_dict={
                self.critic_state_input: cur_state,
                self.critic_action_input: predicted_action
            })[0]

            self.sess.run(self.optimize, feed_dict={
                self.actor_state_input: cur_state,
                self.actor_critic_grad: grads
            })

    def _train_critic(self, experience):
        for sample in experience:
            last_state, last_action, last_reward, new_state = sample

            last_action_categ = n_action * [0]
            last_action_categ[last_action-1] = 1
            last_action_categ = np.array(last_action_categ).reshape(1, -1)

            last_state = np.array(last_state).reshape(1, -1)

            target_action = self.target_actor_model.predict(new_state)
            future_reward = self.target_critic_model.predict([new_state, target_action])[0][0]
            last_reward += self.gamma * future_reward

            last_action = np.array([[last_action]])
            last_reward = np.array([last_reward])

            print(last_state)
            print('reward: %r' % last_reward)

            self.critic_model.fit([last_state, last_action_categ],
                                  last_reward, verbose=0)

    def train(self, experience):
        self._train_critic(experience)
        self._train_actor(experience)

    def predict(self, cur_state):
        return self.actor_model.predict(cur_state)
