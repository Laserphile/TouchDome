from SimpleCV import *

cam = Camera()
disp = Display()

img = cam.getImage()
img = img.greyscale()
img = img.crop(x=960,y=540,w=1080,h=1080,centered=True)
img = img.scale(540,540)
comparison_img = img.flipHorizontal()


while disp.isNotDone():
        img = cam.getImage()
        img = img.greyscale()
        img = img.crop(x=960,y=540,w=1080,h=1080,centered=True)
        img = img.flipHorizontal()
        img = img.scale(540,540)
        result = img - comparison_img
        if disp.mouseLeft:
                break
        result.save(disp)
