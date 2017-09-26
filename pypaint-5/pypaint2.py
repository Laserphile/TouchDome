#! /usr/bin/env python

#pypaint2.py
"""
pypaint2.py
Step 2 in bulding a comprehensive paint program in pygame

This script wraps the environment functionality in simple classes
Many of the comments may seem redundant, but they are here for programmers
who are just starting out in pygame or python
"""

import sys, pygame
from pygame.locals import *

class pypaint2:

    def __init__(self):
        self.initialize()

    def initialize(self):
        #Quit flag
        self.QUIT = None

        #Setup the pygame screen
        self.screen_size = (400, 300)
        self.screen = pygame.display.set_mode(self.screen_size)

    def run(self):
        """This method provides the main application loop.
           It continues to run until either the ESC key is pressed
           or the window is closed
        """
        while 1:
            self.events = pygame.event.get()
            for e in self.events:
                #Set quit state when window is closed
                if e.type == pygame.QUIT :
                    self.QUIT = 1
                if e.type == KEYDOWN:
                    #Set quit state on Esc key press
                    if e.key == K_ESCAPE:
                        self.QUIT = 1
            if self.QUIT:
                #Exit pygame gracefully
                pygame.quit()
                sys.exit(0)


if __name__ == "__main__":
    mypaint = pypaint2()
    mypaint.run()
