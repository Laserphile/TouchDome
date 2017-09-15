from SimpleCV import *

cam = Camera()
disp = Display()

mask = Image("round_mask_1080.png").invert()

while disp.isNotDone():
        img = cam.getImage()
        img = img.greyscale()
        img = img.crop(x=960,y=540,w=1080,h=1080,centered=True)
        img = img - mask
        img = img.flipHorizontal()
        img = img.scale(100,100)
        comparison_img = img
        if disp.mouseLeft:
            break
        img.save(disp)

time.sleep(1)

while disp.isNotDone():
        img = cam.getImage()
        img = img.greyscale()
        img = img.crop(x=960,y=540,w=1080,h=1080,centered=True)
        img = img - mask
        img = img.flipHorizontal()
        img = img.scale(100,100)
        result = img - comparison_img
        result = result * 6
        result = result.binarize(60)
        result = result.invert()
        matrix = result.getNumpy()
        #print matrix

        #https://stackoverflow.com/questions/4588628/find-indices-of-elements-equal-to-zero-from-numpy-array
        #https://stackoverflow.com/questions/27175400/how-to-find-the-index-of-a-value-in-2d-array-in-python
        matrix_coords = zip(*np.where(matrix == 255))
        #matrix_empty = np.zeros((50,3))
        #matrix_full = matrix_coords + matrix_empty
        if matrix_coords:
                x = matrix_coords[(0)]
                x = np.delete(x, 2, 0)
                print x
        #print matrix_coords
        if disp.mouseLeft:
            break
        result.save(disp)
