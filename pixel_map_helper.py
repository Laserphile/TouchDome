# Take an image and resize to something sane
# Using mouse clicks associate that pixel coordinate with an arbitrary pixel number.

# TODO
# Make a line tool that allows you to stretch an arbitrary number of pixels between two mouse clicks
# Use a button press to mark down the transition to new groups of pixels
# Make a "snap" grid that is a few pixels wide to allow for easier vertical/horizontal alignment
# Allow resizing of loaded image (can easily do this manually beforehand)
#
#


import numpy as np
import cv2

mouseX = 0
mouseY = 0

b = np.array([0, 0, 0], np.uint8)
l = 1


def draw_circle(event, x, y):
    global mouseX, mouseY, b, l
    mouseX, mouseY = x, y
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(img, (x, y), 5, (255, 0, 0), -1)
        a = np.array([x, y, l])
        b = np.vstack((a, b))
        l = b[0]
        l = l[2] + 1
        print(b)
        mouseX, mouseY = x, y


img = cv2.imread('Images/h2o_sign.png', 1)

cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_circle)

while 1:
    cv2.imshow('image', img)
    k = cv2.waitKey(20) & 0xFF
    if k == 27:
        print("Enter a file name:")
        filename = raw_input()
        np.savetxt(filename, b)
        np.save(filename, b)
        break
