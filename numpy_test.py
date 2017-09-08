from SimpleCV import *

cam = Camera()
disp = Display()

while disp.isNotDone():
        img = cam.getImage()
        img = img.greyscale()
        img = img.crop(x=960,y=540,w=1080,h=1080,centered=True)
        img = img.flipHorizontal()
        img = img.scale(50,50)
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
        img = img.scale(50,50)
        result = img - comparison_img
        result = result * 6
        result = result.binarize(60)
        result = result.invert()
        matrix = result.getNumpy()
        #print matrix

        #https://stackoverflow.com/questions/4588628/find-indices-of-elements-equal-to-zero-from-numpy-array
        #https://stackoverflow.com/questions/27175400/how-to-find-the-index-of-a-value-in-2d-array-in-python
        matrix_coords = zip(*np.where(matrix == 255))

        print matrix_coords
        if disp.mouseLeft:
            break
        result.save(disp)
