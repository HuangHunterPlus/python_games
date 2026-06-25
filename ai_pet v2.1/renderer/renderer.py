import os
import pygame
from config import PET_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT, SCALE
from renderer.sprites import draw_pet, OVERLAY_FUNCTIONS, set_animal


def _find_chinese_font():
    paths = [
        "C:\\Windows\\Fonts\\simsun.ttc",
        "C:\\Windows\\Fonts\\msyh.ttc",
        "C:\\Windows\\Fonts\\simhei.ttf",
        "C:\\Windows\\Fonts\\fangso.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return pygame.font.Font(p, 14)
            except Exception:
                continue
    return pygame.font.Font(None, 16)


class PetRenderer:
    def __init__(self):
        self.base_size = PET_SIZE
        self.scale = SCALE
        self.surf_size = int(self.base_size * self.scale)
        self.offset_x = (WINDOW_WIDTH - self.surf_size) // 2
        self.offset_y = WINDOW_HEIGHT - self.surf_size - 20
        self.frame = 0
        self._font = None

    def _get_font(self):
        if self._font is None:
            self._font = _find_chinese_font()
        return self._font

    def render(self, surface: pygame.Surface, state: str,
               dialogue: str = None, overlay: tuple = None,
               animal_type: str = "cat"):
        surface.fill((0, 0, 0, 0))

        set_animal(animal_type)
        pet_surf = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
        draw_pet(pet_surf, state, self.frame)

        if overlay:
            overlay_type, progress = overlay
            func = OVERLAY_FUNCTIONS.get(overlay_type)
            if func:
                func(pet_surf, self.frame, progress)

        scaled = pygame.transform.smoothscale(pet_surf, (self.surf_size, self.surf_size))
        surface.blit(scaled, (self.offset_x, self.offset_y))

        if dialogue:
            self._draw_dialogue(surface, dialogue)

        self.frame += 1

    def _draw_dialogue(self, surface: pygame.Surface, text: str):
        font = self._get_font()
        max_width = WINDOW_WIDTH - 40
        words = []
        for segment in text.split("\n"):
            line = ""
            for char in segment:
                test = line + char
                if font.size(test)[0] > max_width:
                    words.append(line)
                    line = char
                else:
                    line = test
            words.append(line)

        line_h = 20
        box_h = len(words) * line_h + 16
        box_w = WINDOW_WIDTH - 24
        box_x = 12
        box_y = 8

        bubble_bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bubble_bg.fill((255, 255, 255, 230))
        pygame.draw.rect(bubble_bg, (200, 200, 200, 200),
                        (0, 0, box_w, box_h), 1, border_radius=8)
        surface.blit(bubble_bg, (box_x, box_y))

        for i, word in enumerate(words):
            rendered = font.render(word, True, (50, 50, 50))
            text_x = box_x + 10
            text_y = box_y + 8 + i * line_h
            surface.blit(rendered, (text_x, text_y))

    def get_pet_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.offset_x, self.offset_y,
            self.surf_size, self.surf_size,
        )
