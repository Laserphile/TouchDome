#! /usr/bin/env python

#pypaint5.py
"""
pypaint5.py
Step 5 in bulding a comprehensive paint program in pygame

This script adds extra functionality to the basic class
1.. Add a Cirlce tool and manage its mouse events
2.. Add a keyoard event to switch between line and circle

Many of the comments may seem redundant, but they are here for programmers
who are just starting out in pygame or python
"""

import sys, pygame, math
from pygame.locals import *

class draw_item:
    """This class holds items that are to blitted onto the canvas"""
    def __init__(self):
        self.surface = None
        self.left = 0
        self.top = 0

    def add(self,surface,left,top):
        self.surface = surface
        self.left = left
        self.top = top



class pypaint5:

    def __init__(self):
        pygame.init()

        self.BLACK = 0,0,0
        self.WHITE = 255,255,255
        self.GREY1 = 100,100,100
        self.QUIT = False
        self.mousebutton = None
        self.mousedown = False
        self.toolset = ["Line","Circle"]
        self.mouse_buttons = ["Left Button","Middle Button","Right Button","Wheel Up","Wheel Down"]
        self.draw_list = []
        self.mouseX = self.mouseY = 0
        self.draw_tool = "Line"
        self.drawstartX = -1
        self.drawendX = -1
        self.drawstartX = -1
        self.drawendY = -1
        self.draw_toggle = False
        #initialize system
        self.initialize()


    def initialize(self):

        #Setup the pygame screen
        self.screen_width = 800
        self.screen_height = 600
        self.screen_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(self.screen_size)

        #setup a generic drawing surface/canvas with
        self.canvas = pygame.Surface((self.screen_width, self.screen_height))

        #setup a work canvas with black as the transparent colour
        self.work_canvas = pygame.Surface((self.screen_width, self.screen_height))
        self.work_canvas.set_colorkey(self.BLACK)

        #setup a paint canvas
        self.paint_canvas = pygame.Surface((self.screen_width, self.screen_height))

    def radius(self,rectangle):
        x1,y1,x2,y2 = rectangle
        x = (x2-x1)
        y = (y2-y1)
        if x >= y:
            rad = x
        else:
            rad = y
        if rad < 3:
            rad = 3
        return rad/2

    def center(self,rectangle):
        x1,y1,x2,y2 = rectangle
        x = abs(x1-x2)
        y = abs(y1-y2)
        x1 += x/2
        y1 += y/2
        return (x1,y1)

    def mouse_handler(self,events):

        """Because this paint program is mainly mouse driven,
           we want to manage all aspects of the mouse, so we use
           a mouse_handler. """

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mousedown = True
                self.mousebutton = event.button
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mousedown = False
                self.mousebutton = event.button
            self.mouseX, self.mouseY = pygame.mouse.get_pos()

        #manage tool events
        if self.draw_tool == "Line":
            self.draw_line_template()
        if self.draw_tool == "Circle":
            self.draw_circle_template()

        #show mouse state
        self.show_mousestate()


    def draw_circle_template(self):
        #on left mouse down we set the basic values
        if self.draw_toggle == False and self.mousedown and self.mousebutton == 1:
            self.drawstartX = self.mouseX
            self.drawendX = self.mouseX
            self.drawstartY = self.mouseY
            self.drawendY = self.mouseY
            self.draw_toggle = True

        #while mouse is down we draw the circle template to the work canvas
        elif self.draw_toggle == True and self.mousedown and self.mousebutton == 1:
            self.drawendX = self.mouseX
            self.drawendY = self.mouseY
            #We clear the work canvas with black
            self.work_canvas.fill(self.BLACK)
            #draw guide lines
            pygame.draw.line(self.work_canvas,
                             (self.GREY1),
                             (0,self.drawstartY),
                             (2000,self.drawstartY),
                             1)
            pygame.draw.line(self.work_canvas,
                             (self.GREY1),
                             (self.drawstartX,0),
                             (self.drawstartX,2000),
                             1)

            #We draw a circle into the work_canvas in GREY1
            try:
               pygame.draw.circle(self.work_canvas,
                             (self.GREY1),
                             self.center((self.drawstartX,self.drawstartY,self.drawendX,self.drawendY)),
                             self.radius((self.drawstartX,self.drawstartY,self.drawendX,self.drawendY)),
                             1)
            except:  #we cant have a thickness larger than the radius, so catch the exception
                pass
            #blit the work_canvas onto the canvas
            self.draw_tool_template()

        #when we release the left mouse, we draw a white circle to the paint canvas
        elif self.draw_toggle == True and not self.mousedown and self.mousebutton == 1:
            self.draw_toggle = False
            #We draw a circle into the paint_canvas in WHITE
            try:
               pygame.draw.circle(self.paint_canvas,
                             (self.WHITE),
                             self.center((self.drawstartX,self.drawstartY,self.drawendX,self.drawendY)),
                             self.radius((self.drawstartX,self.drawstartY,self.drawendX,self.drawendY)),
                             2)
            except:  #we cant have a thickness larger than the radius, so catch the exception
                pass


    def draw_line_template(self):

        #on left mouse down we set the basic values
        if self.draw_toggle == False and self.mousedown and self.mousebutton == 1:
            self.drawstartX = self.mouseX
            self.drawendX = self.mouseX
            self.drawstartY = self.mouseY
            self.drawendY = self.mouseY
            self.draw_toggle = True

        #while mouse is down we draw the line template to the work canvas
        elif self.draw_toggle == True and self.mousedown and self.mousebutton == 1:
            self.drawendX = self.mouseX
            self.drawendY = self.mouseY
            #We clear the work canvas with black
            self.work_canvas.fill(self.BLACK)
            #We draw a line into the work_canvas in GREY1
            pygame.draw.line(self.work_canvas,
                             (self.GREY1),
                             (self.drawstartX,self.drawstartY),
                             (self.drawendX,self.drawendY),
                             1)
            #blit the work_canvas onto the canvas
            self.draw_tool_template()

        #when we release the left mouse, we draw a white line to the paint canvas
        elif self.draw_toggle == True and not self.mousedown and self.mousebutton == 1:
            self.draw_toggle = False
            #We draw a line into the paint_canvas in WHITE
            pygame.draw.line(self.paint_canvas,
                             (self.WHITE),
                             (self.drawstartX,self.drawstartY),
                             (self.drawendX,self.drawendY),
                             2)

    def show_mousestate(self):
        """Show the mouse position and button press on the screen"""
        if self.mousebutton and self.mousedown:
            info = "ESC to quit, L for lines, C for Circles "
            info += " ...Mouse: "+str(self.mouse_buttons[self.mousebutton-1])
        else:
            info = "ESC to quit, L for lines, C for Circles "
        info += " ...Mouse X= "+str(self.mouseX)+" Y: "+str(self.mouseY)
        info += " LeftButtonDown: " + str(self.draw_toggle)

        #load font
        font = pygame.font.Font(None, 20)
        textimg = font.render(info, 1, self.WHITE)

        #add text to the draw items list
        item = draw_item()
        item.add(textimg,10,10)
        self.draw_list.append(item)

    def draw_tool_template(self):
        """We use a work canvas to display a tool template before
           we commit it to the canvas for rendering to the screen"""
        #add tool_template to the draw items list
        item = draw_item()
        item.add(self.work_canvas,0,0)
        self.draw_list.append(item)

    def canvas_draw(self):
        """We use this method to manage items that are to be drawn onto
           the canvas from a draw list"""

        #NB: for now we clear the canvas with black
        self.canvas.fill(self.BLACK)

        #we first blit our paint canvas
        self.canvas.blit(self.paint_canvas,(0,0))

        #We get all the draw items from the list, and blit them to the canvas
        for i in self.draw_list:
            self.canvas.blit(i.surface,(i.left,i.top))


    def draw(self):
        """We use a generic surface / Canvas onto which we draw anything
           Then we blit this canvas onto the display screen"""
        self.canvas_draw()
        self.screen.blit(self.canvas, (0, 0))

    def clear(self):
        """We clear the draw list in preperation for drawing on the canvas"""
        self.draw_list = []

    def run(self):
        """This method provides the main application loop.
           It continues to run until either the ESC key is pressed
           or the window is closed
        """
        while 1:

            #we clear and prepare the draw_list for the canvas
            self.clear()
            events = pygame.event.get()
            for e in events:

                #Set quit state when window is closed
                if e.type == pygame.QUIT :
                    self.QUIT = True
                if e.type == KEYDOWN:
                    #Set quit state on Esc key press
                    if e.key == K_ESCAPE:
                        self.QUIT = True
                    #Toggle Line drawing
                    if e.key == K_l:
                        self.draw_tool = "Line"
                    #Toggle Circle drawing
                    if e.key == K_c:
                        self.draw_tool = "Circle"


            if self.QUIT:
                #Exit pygame gracefully
                pygame.quit()
                sys.exit(0)

            #call the mouse handler with current events
            self.mouse_handler(events)

            #Process any drawing that needs to be done
            self.draw()

            #flip the display
            pygame.display.flip()



if __name__ == "__main__":
    mypaint = pypaint5()
    mypaint.run()
