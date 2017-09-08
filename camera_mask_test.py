from SimpleCV import *

cam = Camera()
disp = Display()

mask = Image("round_mask_1080.png").invert()

while disp.isNotDone():
        img = cam.getImage()
        img = img.crop(x=960,y=540,w=1080,h=1080,centered=True)
        img = img.greyscale()
        #img = img.crop(x=960,y=540,w=1080,h=1080,centered=True)
        img = img.flipHorizontal()
        #img = img.scale(400,400)
        #img = img.binarize(50)
        img = mask + img

        if disp.mouseLeft:
            break
        img.save(disp)
