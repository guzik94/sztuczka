import unittest
from pygejm.constants import example_names, food_id
from pygejm.visible_actor import VisibleActor
from pygejm.game_utils.game_loop import GameLoop
from random import randint


class TestAnn(unittest.TestCase):
    def test_actor_makes_move(self):
        return
        gs = GameState()

        for l in range(1):
            actor_w = 10
            actor_h = 10
            gs.add_actor(VisibleActor(example_names[l],
                                      pygame.Rect((randint(0, game_width - actor_w - 1),
                                                   randint(0, game_width - actor_h - 1), actor_w, actor_h)),
                                      is_interactive=False,
                                      model_id='actor_critic'))

        for l in range(20):
            food_w = 20
            food_h = 20
            gs.add_action(Action(actions[food_id], pygame.Rect(
                (randint(0, game_width - food_w - 1), randint(0, game_width - food_h - 1), food_w, food_h))))

        gl = GameLoop()
        gl.run(gs, graphics_on=True, ticks=1000)


if __name__ == '__main__':
    unittest.main()
