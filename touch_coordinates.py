import numpy as np
import cv2

cap = cv2.VideoCapture(0)
mask = cv2.imread('round_mask_1920_1080.png',0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = frame.astype(np.uint8)
    frame = cv2.flip(frame,1)
    calibrate_frame = frame

    # Display the resulting frame
    cv2.imshow('frame',calibrate_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    current_frame = cv2.flip(frame,1)
    current_frame = current_frame * 0.9
    frame = current_frame - calibrate_frame
    frame = frame.astype(np.uint8)
    ret, frame = cv2.threshold(frame,127,255,cv2.THRESH_BINARY_INV)
    frame = cv2.bitwise_and(frame, frame, mask = mask)
    #frame = cv2.resize(frame, (200,200), fx=1, fy=1)

    matrix = np.asarray(frame)
    matrix_coords = zip(*np.where(matrix == 255))
    #print matrix
    if matrix_coords:
            x = matrix_coords[(0)]
            print x

    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
