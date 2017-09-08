from SimpleCV import *

cam = Camera()
disp = Display()

while disp.isNotDone():
        img = cam.getImage()
        img = img.greyscale()
        img = img.crop(x=960,y=540,w=1080,h=1080,centered=True)
        img = img.flipHorizontal()
        img = img.scale(400,400)
        img = img.highPassFilter(0.02,0.02,grayscale=True)
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
        img = img.scale(400,400)
        img = img.highPassFilter(0.02,0.02,grayscale=True)
        result = img - comparison_img
        result = result * 6
        result = result.binarize(50)

        if disp.mouseLeft:
            break
        result.save(disp)
