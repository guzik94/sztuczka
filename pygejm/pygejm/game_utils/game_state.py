import pygame
import copy
from pygejm.game_graphics import hud

from pygame import Rect
from pygejm.acts import Action, actions
from pygejm.observation import Observation
from pygejm.visible_object import VisibleObject
from pygejm.constants import (game_height, game_width,
                              wall_id,
                              wall_bump)


class GameState:
    def __init__(self):
        self.actors = []
        self.noactor_actions = []
        self.walls = []
        self.sensors = {}
        self.time_passed = 0
        self.hud = hud.Hud()
        self.observation = Observation()

        self.__create_walls()

    def __create_walls(self):
        self.walls.append(VisibleObject(Rect(0, 0, 1, game_height), wall_id))  # lewa
        self.walls.append(VisibleObject(Rect(0, 0, game_width, 1), wall_id))  # gorna
        self.walls.append(VisibleObject(Rect(0, game_height - 1, game_width, 1), wall_id))  # dolna
        self.walls.append(VisibleObject(Rect(game_width - 1, 0, 1, game_height), wall_id))  # prawa

    def __remove_dead_actors(self):
        actors_to_remove = []
        for idx in range(len(self.actors)):
            if self.actors[idx].health <= 0:
                actors_to_remove.append(self.actors[idx])
        for ac in actors_to_remove:
            self.actors.remove(ac)

    def update(self):
        if self.time_passed == 0:
            self.update_sensors_for_all_actors()
        if self.time_passed > 0 and len(self.noactor_actions) == 0:
            self.__spawn_food()

        self.__remove_dead_actors()

        noactor_actions_cp = copy.copy(self.noactor_actions)
        actors_rects_before = [x.rect.copy() for x in self.actors]

        for idx, a in enumerate(self.actors):
            actor_observation = self.get_observation(a)
            self.__apply_actor_action(idx, a.act(actor_observation))

        [self.__apply_noactor_action(a) for a in noactor_actions_cp]
        [self.__apply_const_action(a, actors_rects_before) for a in self.walls]

        # for idx in range(len(self.actors)):
        #	self.actors[idx].health -= 0.005

        self.update_sensors_for_all_actors()
        self.hud.update(self.actors)

        self.time_passed += 1

    def __spawn_food(self):
        return
        # print('Took %d iterations.' % self.time_passed)
        self.time_passed = 0
        food_w = 20
        food_h = 20
        for l in range(20):
            self.add_action(Action(actions[FOOD], pygame.Rect(
                (randint(0, game_width - food_w - 1), randint(0, game_width - food_h - 1), food_w, food_h))))

    def update_sensors_for_all_actors(self):
        for a in self.actors:
            self.observation.update_sensors(a)

    def get_observation(self, actor):
        vos = []
        vos.extend(self.actors)
        vos.extend(self.walls)
        vos.extend(self.noactor_actions)

        if not all(isinstance(o, VisibleObject) for o in vos):
            raise AssertionError('At least one not-a-VisibleObject in %r' % vos)

        return self.observation.get_observation(actor=actor, vos=vos,
                                                preproc_mode=['collide', 'scale'])

    def __apply_const_action(self, action_rect, actors_before):
        for idx, a in enumerate(self.actors):
            if a.rect.colliderect(action_rect):
                self.actors[idx].rect = actors_before[idx]
                self.actors[idx].health += wall_bump

    def __apply_noactor_action(self, action):
        for idx, a in enumerate(self.actors):
            if a.rect.colliderect(action.rect):
                self.actors[idx] = action.act(self.actors[idx])
                self.noactor_actions.remove(action)

    def __apply_actor_action(self, actor_idx, action):
        self.actors[actor_idx] = action.act(self.actors[actor_idx])

    def add_actor(self, actor):
        if not isinstance(actor, VisibleObject):
            raise AssertionError('Actor must be VisibleObject, got: %r' % actor)
        self.actors.append(actor)

    def add_action(self, action):
        if not isinstance(action, VisibleObject):
            raise AssertionError('Action must be VisibleObject, got: %r' % action)
        self.noactor_actions.append(action)

    def add_wall(self, wall):
        if not isinstance(wall, VisibleObject):
            raise AssertionError('Wall must be VisibleObject, got: %r' % wall)
        self.walls.append(wall)


