"""
Input control — hit keys: Player 1 = Space, Player 2 = 1 (or numpad 1)
"""

import pygame


class Controller:
    KEY_HIT_P1 = pygame.K_SPACE
    KEY_HIT_P2_MAIN = pygame.K_1
    KEY_HIT_P2_ALT = pygame.K_KP1

    @staticmethod
    def is_player_hit(keys: pygame.key.ScancodeWrapper, player: int) -> bool:
        """Return True if the player pressed their hit key."""
        if player == 1:
            return keys[Controller.KEY_HIT_P1]
        else:
            return (keys[Controller.KEY_HIT_P2_MAIN]
                    or keys[Controller.KEY_HIT_P2_ALT])

    @staticmethod
    def is_any_key_down(events: list) -> bool:
        """Return True if any key was pressed (for title screen)."""
        for e in events:
            if e.type == pygame.KEYDOWN:
                return True
        return False
