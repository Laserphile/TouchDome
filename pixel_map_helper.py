# Take an image and resize to something sane
# Using mouse clicks associate that pixel coordinate with an arbitrary pixel number.
# Mark down the transition to new groups of pixels

import numpy as np
import cv2

global mouseX,mouseY,b
mouseX,mouseY = 0,0

b = np.array([0,0,0], np.uint8)
l = 1

def draw_circle(event,x,y,flags,param):
    global mouseX,mouseY,b,l
    mouseX,mouseY = x,y
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(img,(x,y),5,(255,0,0),-1)
        a = np.array([x,y,l])
        b = np.vstack((a,b))
        l = b[0]
        l = l[2] + 1
        print b
        mouseX,mouseY = x,y

img = cv2.imread('h2o_sign.png',1)

cv2.namedWindow('image')
cv2.setMouseCallback('image',draw_circle)



while(1):
    cv2.imshow('image',img)
    k = cv2.waitKey(20) & 0xFF
    if k == 27:
        np.savetxt('pixels.txt', b)
        np.save('pixels', b)
        break
    elif k == ord('a'):
        print array
