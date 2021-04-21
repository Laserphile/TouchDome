# BLOB detect in image

import cv2
import numpy as np

# Read images
calibrate_frame = cv2.imread("Images/test_images/calibrate.jpg", cv2.IMREAD_GRAYSCALE)
current_frame = cv2.imread("Images/test_images/two_fingers.jpg", cv2.IMREAD_GRAYSCALE) *0.85
current_frame = current_frame.astype(np.uint8)
mask = cv2.imread('Images/round_mask_1920_1080.png', 0)

frame = current_frame - calibrate_frame
#frame = frame.astype(np.uint8)
#frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY_INV)
frame = cv2.bitwise_not(frame)
frame = cv2.bitwise_and(frame, frame, mask=mask)

# Set up the detector with default parameters.
params = cv2.SimpleBlobDetector_Params()

# Change thresholds
params.minThreshold = 0
params.maxThreshold = 100

# Filter by Area.
params.filterByArea = True
params.minArea = 150

# Filter by Circularity
params.filterByCircularity = False
params.minCircularity = 0.8

# Filter by Convexity
params.filterByConvexity = False
params.minConvexity = 0.87

# Filter by Inertia
params.filterByInertia = False
params.minInertiaRatio = 0.01

# Filter by Inertia
params.filterByColor = True
params.blobColor = 255

detector = cv2.SimpleBlobDetector_create(params)

# Detect blobs.
keypoints = detector.detect(frame)

# Draw detected blobs as red circles.
# cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
im_with_keypoints = cv2.drawKeypoints(frame, keypoints, np.array([]), (255,0,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

number_of_blobs = len(keypoints)
print(number_of_blobs)
if number_of_blobs==0:
    print("no blobs found")
i = 0
while i < number_of_blobs:
    x = int(round(keypoints[i].pt[0])) #i is the index of the blob you want to get the position
    y = int(round(keypoints[i].pt[1]))
    print(x, y)
    cv2.circle(im_with_keypoints, (x, y), 20, (255, 0, 0), -1)
    i = i + 1

cv2.imwrite("Images/test_images/output.jpg", im_with_keypoints)

# Show keypoints
# cv2.imshow("Keypoints", im_with_keypoints)
# cv2.waitKey(0)
