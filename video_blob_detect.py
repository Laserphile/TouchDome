# Takes the video from the touch input dome and outputs the coordinates of where you are touching
# TODO:
# Generate x,y coordinates from keypoints 

import numpy as np
import cv2

cap = cv2.VideoCapture(0)
mask = cv2.imread('Images/round_mask_1920_1080.png', 0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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
    #frame = cv2.bitwise_and(frame, frame, mask=mask)

    # Set up the detector with default parameters.
    params = cv2.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = 0
    params.maxThreshold = 100

    # Filter by Area.
    params.filterByArea = True
    params.minArea = 200

    # Filter by Circularity
    params.filterByCircularity = False
    params.minCircularity = 0.8

    # Filter by Convexity
    params.filterByConvexity = False
    params.minConvexity = 0.87

    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0.6

    # Filter by Inertia
    params.filterByColor = True
    params.blobColor = 255

    detector = cv2.SimpleBlobDetector_create(params)

    # Detect blobs.
    keypoints = detector.detect(frame)
    print(keypoints)

    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    im_with_keypoints = cv2.drawKeypoints(frame, keypoints, np.array([]), (255,0,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # Display the resulting frame
    cv2.imshow('frame', im_with_keypoints)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
