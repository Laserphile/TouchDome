from SimpleCV import *
import pyautogui

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
        matrix = result.getNumpy()
        #print matrix

        # https://stackoverflow.com/questions/4588628/find-indices-of-elements-equal-to-zero-from-numpy-array
        # https://stackoverflow.com/questions/27175400/how-to-find-the-index-of-a-value-in-2d-array-in-python

        matrix_coords = zip(*np.where(matrix == 255)) # I don't understand this, help me Jon

        if matrix_coords:
                finger_coords = matrix_coords[(0)]
                finger_coords = np.delete(finger_coords, 2, 0)
                x = np.delete(finger_coords, 1, 0)
                y = np.delete(finger_coords, 0, 0)
                pyautogui.moveTo(x*10, y*6) # Drives the host OS cursor

                print finger_coords
        if disp.mouseLeft:
            break
        result.save(disp)
