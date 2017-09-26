#! /usr/bin/env python

#pypaint3.py
"""
pypaint3.py
Step 3 in bulding a comprehensive paint program in pygame

This script add extra functionality to the basic class
1.. Add a generic mouse handler
2.. Add a generic drawing canvas

Many of the comments may seem redundant, but they are here for programmers
who are just starting out in pygame or python
"""

import sys, pygame
from pygame.locals import *


class pypaint3:

    def __init__(self):
        pygame.init()
        
        self.BLACK = 0,0,0
        self.WHITE = 255,255,255
        self.QUIT = False
        self.mousebutton = None
        self.mousedown = False
        self.mouse_buttons = ["Left Button","Middle Button","Right Button","Wheel Up","Wheel Down"]

        #initialize system
        self.initialize()


    def initialize(self):

        #Setup the pygame screen
        self.screen_width = 400
        self.screen_height = 300
        self.screen_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(self.screen_size)

        #setup a generic drawing surface/canvas
        self.canvas = pygame.Surface((self.screen_width, self.screen_height))


    def mouse_handler(self,event):

        """Because this paint program is mainly mouse driven,
           we want to manage all aspects of the mouse, so we use
           a mouse_handler. """

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mousedown = True
            self.mousebutton = event.button
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mousedown = False
            self.mousebutton = event.button

        self.mouseX, self.mouseY = pygame.mouse.get_pos()

        self.show_mousestate()


    def show_mousestate(self):
        """Show the mouse position and button press on the screen"""
        if self.mousebutton and self.mousedown:
            info = "Mouse: "+str(self.mouse_buttons[self.mousebutton-1])
        else:
            info = "Mouse: "
        info += "X= "+str(self.mouseX)+" Y: "+str(self.mouseY)

        #NB: for now we clear the canvas with black
        self.canvas.fill(self.BLACK)

        #load font and blit to canvas
        font = pygame.font.Font(None, 20)
        textimg = font.render(info, 1, self.WHITE)
        self.canvas.blit(textimg, (10, 10))


    def draw(self):
        """We use a generic surface / Canvas onto which we draw anything
           Then we blit this canvas onto the display screen"""
        self.screen.blit(self.canvas, (0, 0))


    def run(self):
        """This method provides the main application loop.
           It continues to run until either the ESC key is pressed
           or the window is closed
        """
        while 1:

            events = pygame.event.get()
            for e in events:
                #pass event onto mouse handler only if something happens
                self.mouse_handler(e)

                #Set quit state when window is closed
                if e.type == pygame.QUIT :
                    self.QUIT = True
                if e.type == KEYDOWN:
                    #Set quit state on Esc key press
                    if e.key == K_ESCAPE:
                        self.QUIT = True

            if self.QUIT:
                #Exit pygame gracefully
                pygame.quit()
                sys.exit(0)


            #Process any drawing that needs to be done
            self.draw()

            #flip the display
            pygame.display.flip()



if __name__ == "__main__":
    mypaint = pypaint3()
    mypaint.run()
