import numpy as np
import cv2

cap = cv2.VideoCapture(0)
mask = cv2.imread('round_mask_1920_1080.png',0)
#ret, mask = cv2.threshold(mask, 220, 255, cv2.THRESH_BINARY_INV);


while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.flip(gray,1)
    #gray = gray + mask
    gray = cv2.bitwise_and(gray, gray, mask = mask)


    # Display the resulting frame
    cv2.imshow('image',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
