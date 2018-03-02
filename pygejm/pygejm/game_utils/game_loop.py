import pygame
from pygame.color import Color
from pygejm.constants import game_height, game_width, hud_width, up_id, down_id, left_id, right_id
import cProfile, pstats, io
from pygejm.game_utils.game_state import GameState
import pygejm.acts as acts


class GameLoop:
    def __init__(self):
        self.graphics_on = False
        self.screen = None
        self.ticks = 100
        self.keep_playing = True
        self.game_state = GameState()
        self.clock = pygame.time.Clock()
        self.time_passed = 0

    def __print_stats(self, pr):
        return
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

    def loop(self, max_loops=None):
        pr = cProfile.Profile()
        pr.enable()
        try:
            while self.keep_playing and (max_loops is None or self.time_passed < max_loops):
                try:
                    self.on_event()
                    self.on_act()
                    self.on_render()
                except StopIteration:
                    pygame.quit()

                self.clock.tick(self.ticks)
                self.time_passed += 1
                if self.time_passed % 1000 == 0:
                    print('Passed: %d' % self.time_passed)
        finally:
            self.__print_stats(pr)

        return self.game_state

    def on_act(self):
        self.game_state.update()

    def on_event(self):
        if not self.graphics_on:
            return
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                raise StopIteration

        actor_idxs = [idx for idx, x in enumerate(self.game_state.actors) if x.is_interactive]
        for actor_idx in actor_idxs:
            key = pygame.key.get_pressed()
            action_idx = 0

            if key[pygame.K_w]:
                action_idx = up_id
            if key[pygame.K_d]:
                action_idx = right_id
            if key[pygame.K_s]:
                action_idx = down_id
            if key[pygame.K_a]:
                action_idx = left_id

            self.game_state.actors[actor_idx].next_act = lambda _: acts.Action(acts.actions[action_idx])

    def on_render(self):
        if self.graphics_on:
            self.screen.fill(pygame.color.Color('white'))

            self.__render_sensors()

            for v in self.game_state.walls:
                pygame.draw.rect(self.screen, Color('purple'), v)
            for v in self.game_state.noactor_actions:
                pygame.draw.rect(self.screen, Color('green'), v.rect)
            for a in self.game_state.actors:
                pygame.draw.rect(self.screen, Color('black'), a.rect)
            self.game_state.hud.render(self.screen)

            pygame.display.flip()

    def __render_sensors(self):
        for key, sensor in self.game_state.sensors.items():
            rect = sensor.rect
            try:
                pygame.draw.rect(self.screen, Color('yellow'), rect)
            except TypeError:
                print('Invalid sensor rect. Got:\n', rect)

    def run(self, game_state, max_loops=None, ticks=100, graphics_on=False):
        self.ticks = ticks

        self.graphics_on = graphics_on
        self.game_state = game_state
        if self.graphics_on:
            self.screen = pygame.display.set_mode((game_width + hud_width, game_height))

        return self.loop(max_loops)
