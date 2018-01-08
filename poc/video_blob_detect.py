# Takes the video from the touch input dome and outputs the coordinates of where you are touching
# TODO:
# Generate x,y coordinates from keypoints

import numpy as np
import cv2

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
params.minCircularity = 0.2
# Filter by Convexity
params.filterByConvexity = False
params.minConvexity = 0.2
# Filter by Inertia
params.filterByInertia = True
params.minInertiaRatio = 0.6
# Filter by Inertia
params.filterByColor = True
params.blobColor = 255

output_array = []

while True:
    # Capture frame-by-frame
    cap = cv2.VideoCapture(0)
    _, input_frame = cap.read()

    input_frame = cv2.flip(input_frame, 1)
    brightness_scale_factor = 1
    input_frame = cv2.cvtColor(input_frame, cv2.COLOR_BGR2GRAY) * brightness_scale_factor
    input_frame = cv2.bitwise_not(input_frame)

    # the below variables et the cutoff points for color differentiation
    gs_lower_color = np.array(135, dtype="uint8")
    gs_upper_color = np.array(255, dtype="uint8")

    # Blurring the image will cutout noise and give you better contours with less points
    mask = cv2.blur(input_frame, (20, 60))

    mask = cv2.inRange(mask, gs_lower_color, gs_upper_color)

    ret2, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)

    mask, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)


    for cnt in contours:
        if 4 < len(cnt) < 300:
            ellipse = cv2.fitEllipse(cnt)
            cv2.ellipse(mask, ellipse, (0, 255, 0), 2)

    # cv2.drawContours(mask, contours, -1, (255, 255, 0), 3)

    cv2.imshow('mask', mask)
    print('waiting on user input')
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print('calibration image taken')
        break

# while ret:
#     # Our operations on the frame come here
#     brightness_scale_factor = 0.89
#     input_frame = cv2.cvtColor(input_frame, cv2.COLOR_BGR2GRAY) * brightness_scale_factor
#     input_frame = cv2.flip(input_frame, 1)
#     input_frame = input_frame.astype(np.uint8)
#
#     frame_diff = input_frame - calibrate_frame
#     final_frame = cv2.bitwise_not(frame_diff)
#     # final_frame = cv2.bitwise_and(final_frame, final_frame, mask=mask)
#     cv2.imshow('frame', final_frame)
#
#     # Set up the detector with default parameters.
#     params = cv2.SimpleBlobDetector_Params()
#
#     # Change thresholds
#     params.minThreshold = 0
#     params.maxThreshold = 100
#
#     # Filter by Area.
#     params.filterByArea = True
#     params.minArea = 200
#
#     # Filter by Circularity
#     params.filterByCircularity = False
#     params.minCircularity = 0.8
#
#     # Filter by Convexity
#     params.filterByConvexity = False
#     params.minConvexity = 0.87
#
#     # Filter by Inertia
#     params.filterByInertia = True
#     params.minInertiaRatio = 0.6
#
#     # Filter by Inertia
#     params.filterByColor = True
#     params.blobColor = 255
#
#     detector = cv2.SimpleBlobDetector_create(params)
#
#     # Detect blobs.
#     keypoints = detector.detect(final_frame)
#     number_of_blobs = len(keypoints)
#     print(number_of_blobs)
#     frame_array = []
#     for i in range(0, number_of_blobs):
#         x = int(round(keypoints[i].pt[0]))  # i is the index of the blob you want to get the position
#         y = int(round(keypoints[i].pt[1]))
#         print(x, y)
#         frame_array.append([x, y])
#
#     output_array.append(frame_array)
#     # Draw detected blobs as red circles.
#     # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
#     im_with_keypoints = cv2.drawKeypoints(final_frame,
#                                           keypoints,
#                                           np.array([]),
#                                           (255, 0, 0),
#                                           cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
#     # Display the resulting frame
#     cv2.imshow('frame', im_with_keypoints)
#
#     # Capture frame-by-frame
#     ret, input_frame = cap.read()
#     # input_frame = cv2.imread('Images/test_images/two_fingers.jpg')
#
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         print('calibration image taken')
#         break

# When everything done, release the capture
output_file = 'test_output/touch_out'
filename = output_file if output_file is not None else input("Enter a file name:")
np_array = np.array(output_array)
np.save(filename, np_array)

cv2.destroyAllWindows()
