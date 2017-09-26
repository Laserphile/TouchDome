#! /usr/bin/env python

#pypaint1.py
"""
pypaint1.py
Step 1 in bulding a comprehensive paint program in pygame

This is a skeleton script, setting up a sample window with
events to exit the system cleanly... It does nothing else.
"""

import sys, pygame
from pygame.locals import *

size = width, height = 400, 300
screen = pygame.display.set_mode(size)


QUIT = 0
while 1:
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT :
            QUIT = 1
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                QUIT = 1
    if QUIT:
        pygame.quit()
        sys.exit(0)
