from pygejm.constants import game_width, hud_height, hud_width
from pygame import Rect
from pygame.color import Color
import pygame


class Hud:
    def __init__(self):
        self.rect = Rect(game_width, 0, hud_width, hud_height)
        self.names = []
        self.healths = []

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 15)

    def update(self, actors):
        for i, actor in enumerate(actors):
            name_text = self.font.render(actor.name, False, Color('black'))
            name_point = (self.rect.x, self.rect.y + i * 45)

            health_text = self.font.render("{:.1e}".format(actor.health), False, Color('black'))
            health_point = (self.rect.x, self.rect.y + 20 + i * 45)

            self.names.append((name_text, name_point))
            self.healths.append((health_text, health_point))

    def render(self, screen):
        pygame.draw.rect(screen, Color('black'), self.rect)
        [screen.blit(t[0], t[1]) for t in self.names]
        [screen.blit(t[0], t[1]) for t in self.healths]
