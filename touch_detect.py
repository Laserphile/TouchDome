from SimpleCV import *

cam = Camera()
disp = Display()

while disp.isNotDone():
        img = cam.getImage()
        img = img.greyscale()
        img = img.crop(x=960,y=540,w=1080,h=1080,centered=True)
        img = img.flipHorizontal()
        img = img.scale(200,200)
        comparison_img = img
        if disp.mouseLeft:
            break
        img.save(disp)

time.sleep(1)

while disp.isNotDone():
        img = cam.getImage()
        img = img.greyscale()
        img = img.crop(x=960,y=540,w=1080,h=1080,centered=True)
        img = img.flipHorizontal()
        img = img.scale(200,200)
        result = img - comparison_img
        result = result * 6
        result = result.binarize(60)
        result = result.invert()
        if disp.mouseLeft:
            break
        result.save(disp)
