import unittest
from pygejm.visible_actor import VisibleActor
from pygejm.acts import actions, Action, ActionVars, register_action
from pygejm.constants import actor_health, food_health, down_id, food_id, up_id, wall_id
from pygejm.visible_object import VisibleObject
from pygejm.game_utils.game_state import GameState
import pygame


class TestActor(unittest.TestCase):
    def test_acts_cannot_have_duplicate_id(self):
        with self.assertRaises(AssertionError):
            register_action(ActionVars(id=0, name='none'))
            register_action(ActionVars(id=0, name='asd'))

    def test_goes_up_down(self):
        gs = GameState()

        rect = pygame.Rect((100, 50, 10, 100))
        ac = VisibleActor('asd', rect)
        ac.next_act = lambda _: Action(actions[up_id])

        gs.add_actor(ac)

        gs.update()
        gs.update()
        self.assertEqual(ac.rect.y, 48)

        ac.next_act = lambda _: Action(actions[down_id])
        gs.update()

        self.assertEqual(ac.rect.y, 49)

    def test_action_with_rect(self):
        for i in range(100):
            gs = GameState()

            ac = VisibleActor('asd', pygame.Rect((100, 50, 10, 10)))
            ac.next_act = lambda _: Action(actions[down_id])

            food_action = Action(actions[food_id], rect=pygame.Rect((100, 70, 10, 10)))
            food_action2 = Action(actions[food_id], rect=pygame.Rect((100, 70, 10, 10)))

            gs.add_actor(ac)
            gs.add_action(food_action)
            gs.add_action(food_action2)

            [gs.update() for _ in range(10)]
            self.assertEqual(ac.health, actor_health)
            self.assertFalse(ac.rect.colliderect(food_action.rect))
            self.assertEqual(ac.rect.y, 60)
            # maja punkt wspolny, ale colliderect zwraca False
            self.assertEqual(ac.rect.bottom, food_action.rect.y)

            gs.update()
            self.assertTrue(ac.rect.colliderect(food_action.rect))
            self.assertEqual(ac.health, actor_health + 2*food_health)
            self.assertEqual(ac.rect.y, 61)

            gs.update()
            self.assertEqual(ac.health, actor_health + 2*food_health)
            self.assertEqual(ac.rect.y, 62)

    def test_wall_stops_actors(self):
        gs = GameState()

        ac = VisibleActor('asd', pygame.Rect((100, 50, 10, 10)))
        ac.next_act = lambda _: Action(actions[down_id])

        ac2 = VisibleActor('asd', pygame.Rect((130, 60, 10, 10)))
        ac2.next_act = lambda _: Action(actions[down_id])

        gs.add_actor(ac)
        gs.add_actor(ac2)
        gs.add_action(Action(actions[food_id], rect=pygame.Rect((120, 150, 20, 10))))
        gs.add_wall(VisibleObject(pygame.Rect((100, 300, 50, 10)), wall_id))

        for i in range(300):
            gs.update()
            self.assertFalse(ac.rect.colliderect(pygame.Rect((100, 300, 50, 10))))

        self.assertEqual(ac.rect.y, 290)


if __name__ == '__main__':
    unittest.main()
