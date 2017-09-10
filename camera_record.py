from SimpleCV import *

cam = Camera()
disp = Display()

vs = VideoStream("myvideo.avi", 30, True)

while disp.isNotDone():
        img = cam.getImage()
        img = img.greyscale()
        img = img.crop(x=960,y=540,w=1080,h=1080,centered=True)
        img = img.scale(540,540)
        img = img.flipHorizontal()
        #img = img.scale(400,400)
        #img = img.binarize(50)
        if disp.mouseLeft:
            break
        img.save(disp)
        img.save(vs)
