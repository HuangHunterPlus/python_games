import pygame

KEY_TO_CHAR = {}
for i in range(26):
    kc = pygame.K_a + i
    KEY_TO_CHAR[kc] = chr(kc)

SCAN_TO_CHAR = {}
for i in range(26):
    SCAN_TO_CHAR[4 + i] = chr(97 + i)
