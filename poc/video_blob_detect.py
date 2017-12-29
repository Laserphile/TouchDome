# Takes the video from the touch input dome and outputs the coordinates of where you are touching
# TODO:
# Generate x,y coordinates from keypoints

import numpy as np
import cv2

mask = cv2.imread('Images/round_mask_1920_1080.png', 0)
output_array = []

while True:
    # Capture frame-by-frame
    # ret, calibrate_frame = cap.read()
    calibrate_frame = cv2.imread('Images/test_images/calibrate.jpg')

    # Our operations on the frame come here
    calibrate_frame = cv2.cvtColor(calibrate_frame, cv2.COLOR_BGR2GRAY)
    calibrate_frame = cv2.flip(calibrate_frame, 1)

    # Display the resulting frame
    cv2.imshow('frame', calibrate_frame)
    print('waiting on user input')
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    break

cap = cv2.VideoCapture('Images/test_images/one_finger.mpeg')
ret, input_frame = cap.read()

while ret:
    # Our operations on the frame come here
    brightness_scale_factor = 0.89
    input_frame = cv2.cvtColor(input_frame, cv2.COLOR_BGR2GRAY) * brightness_scale_factor
    input_frame = cv2.flip(input_frame, 1)
    input_frame = input_frame.astype(np.uint8)

    frame_diff = input_frame - calibrate_frame
    final_frame = cv2.bitwise_not(frame_diff)
    # frame = cv2.bitwise_and(frame, frame, mask=mask)

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
    keypoints = detector.detect(final_frame)
    number_of_blobs = len(keypoints)
    print(number_of_blobs)
    frame_array = []
    for i in range(0, number_of_blobs):
        x = int(round(keypoints[i].pt[0]))  # i is the index of the blob you want to get the position
        y = int(round(keypoints[i].pt[1]))
        print(x, y)
        frame_array.append([x, y])

    output_array.append(frame_array)
    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    im_with_keypoints = cv2.drawKeypoints(final_frame,
                                          keypoints,
                                          np.array([]),
                                          (255, 0, 0),
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # Display the resulting frame
    cv2.imshow('frame', im_with_keypoints)

    # Capture frame-by-frame
    ret, input_frame = cap.read()
    # input_frame = cv2.imread('Images/test_images/two_fingers.jpg')

# When everything done, release the capture
output_file = 'test_output/touch_out'
filename = output_file if output_file is not None else input("Enter a file name:")
np_array = np.array(output_array)
np.save(filename, np_array)

cv2.destroyAllWindows()
