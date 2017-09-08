from SimpleCV import *

cam = Camera()
disp = Display()
normaldisplay = True

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

    if disp.mouseRight:
        normaldisplay = not(normaldisplay)
        print "Display Mode:", "Normal" if normaldisplay else "Segmented"

    img = cam.getImage()
    # my code starts
    img = img.greyscale()
    img = img.flipHorizontal()
    img = img.crop(x=960,y=540,w=1080,h=1080,centered=True)
    img = img.scale(200,200)
    result = img - comparison_img
    result = result * 6
    result = result.binarize(60)
    result = result.invert()
    #my code ends
    dist = img.colorDistance(Color.BLACK).dilate(2)
    segmented = dist.stretch(200,200)
    blobs = segmented.findBlobs()
    if blobs:
        circles = blobs.filter([b.isCircle(0.2) for b in blobs])
        if circles:
            img.drawCircle((circles[-1].x, circles[-1].y), circles[-1].radius(),SimpleCV.Color.BLUE,3)

    if normaldisplay:
        img.save(disp)
    else:
        segmented.save(disp)
