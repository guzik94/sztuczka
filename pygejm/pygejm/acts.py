from pygejm.constants import *
from pygejm.visible_object import VisibleObject


class ActionVars:
    def __init__(self, id, dx=0, dy=0, dhealth=0, name=None):
        self.id = id
        self.dx = dx
        self.dy = dy
        self.dhealth = dhealth
        self.name = name


class Action(VisibleObject):
    def __init__(self, action_vars, rect=None):
        super().__init__(rect, action_vars.id)
        self.action_vars = action_vars
        self.rect = rect

    def act(self, actor):
        actor.rect.x += self.action_vars.dx
        actor.rect.y += self.action_vars.dy
        actor.health += self.action_vars.dhealth

        return actor


actions = {}
actor_actions = []


def register_action(action, for_actor=True):
    if action.id in actions.keys():
        raise AssertionError('Trying to register action with id that is already there.')
    actions[action.id] = action
    if for_actor:
        actor_actions.append(action)


# none
register_action(ActionVars(id=none_action_id, name='none'))
# food
register_action(ActionVars(id=food_id, dhealth=food_health, name='food'), for_actor=False)

# actor actions
register_action(ActionVars(id=up_id, dy=-1, name='up'))
register_action(ActionVars(id=right_id, dx=1, name='right'))
register_action(ActionVars(id=down_id, dy=1, name='down'))
register_action(ActionVars(id=left_id, dx=-1, name='left'))
