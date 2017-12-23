import numpy as np
import cv2

cap = cv2.VideoCapture(0)
mask = cv2.imread('Images/round_mask_1920_1080.png', 0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = frame.astype(np.uint8)
    frame = cv2.flip(frame, 1)
    calibrate_frame = frame

    # Display the resulting frame
    cv2.imshow('frame', calibrate_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) * 0.89
    frame = cv2.flip(frame, 1)
    frame = frame.astype(np.uint8)

    frame = frame - calibrate_frame
    frame = cv2.bitwise_not(frame)
    #frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY_INV)
    #frame = cv2.bitwise_and(frame, frame, mask=mask)
    #frame = cv2.resize(frame, (1920 / 2, 1080 / 2), fx=1, fy=1)

    matrix = np.asarray(frame)
    matrix_coords = zip(*np.where(matrix == 255))

    img = np.zeros((1080 / 2, 1920 / 2, 3), np.uint8)
    old_img = img

    if matrix_coords:
        x = matrix_coords[0]
        cv2.circle(img, (x[1], x[0]), 20, (255, 255, 255), -1)
        print(x)

    # Display the resulting frame
    cv2.imshow('frame', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
