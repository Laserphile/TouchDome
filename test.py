'''
This is how to track a white ball example using SimpleCV
The parameters may need to be adjusted to match the RGB color
of your object.
The demo video can be found at:
'''
print __doc__

from SimpleCV import *

display = SimpleCV.Display() #create the display to show the image
cam = SimpleCV.Camera() # initalize the camera
normaldisplay = True # mode toggle for segment detection and display

while display.isNotDone():
        img = cam.getImage()
        img = img.greyscale()
        img = img.crop(x=960,y=540,w=1080,h=1080,centered=True)
        img = img.flipHorizontal()
        img = img.scale(200,200)
        comparison_img = img
        if display.mouseLeft:
            break
        img.save(display)

time.sleep(1)

while display.isNotDone(): # loop until we tell the program to stop

    if display.mouseRight: # if right mouse clicked, change mode
        normaldisplay = not(normaldisplay)
        print "Display Mode:", "Normal" if normaldisplay else "Segmented"

    #img = cam.getImage().flipHorizontal() # grab image from camera
    img = cam.getImage()
    img = img.greyscale()
    img = img.crop(x=960,y=540,w=1080,h=1080,centered=True)
    img = img.flipHorizontal()
    img = img.scale(200,200)
    result = img - comparison_img
    result = result * 6
    result = result.binarize(60)
    segmented = result.invert()

    #dist = img.colorDistance(SimpleCV.Color.BLACK).dilate(2) # try to separate colors in image
    #segmented = dist.stretch(200,255) # really try to push out white colors
    blobs = segmented.findBlobs() # search the image for blob objects
    if blobs: # if blobs are found
        circles = blobs.filter([b.isCircle(0.2) for b in blobs]) # filter out only circle shaped blobs
        if circles:
            img.drawCircle((circles[-1].x, circles[-1].y), circles[-1].radius(),SimpleCV.Color.BLUE,3) # draw the circle on the main image

    if normaldisplay: # if normal display mode
        img.show()
    else: # segmented mode
        segmented.show()
