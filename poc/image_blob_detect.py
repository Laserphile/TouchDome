# BLOB detect in image

import cv2
import numpy as np
import math

# Read images
calibrate_frame = cv2.imread("Images/test_images/calibrate.jpg", cv2.IMREAD_GRAYSCALE)
current_frame = cv2.imread("Images/test_images/five_fingers.jpg", cv2.IMREAD_GRAYSCALE) *0.85
current_frame = current_frame.astype(np.uint8)
mask = cv2.imread('Images/round_mask_1920_1080.png', 0)

frame = current_frame - calibrate_frame
#frame = frame.astype(np.uint8)
#frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY_INV)
frame = cv2.bitwise_not(frame)
frame = cv2.bitwise_and(frame, frame, mask=mask)



def Initialise_blob_detect(): # Set up the detector with default parameters.
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
    return detector

detector = Initialise_blob_detect()


def blob_detect():
    keypoints = detector.detect(frame) # Detect blobs.

    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    im_with_keypoints = cv2.drawKeypoints(frame, keypoints, np.array([]), (255,0,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    return keypoints, im_with_keypoints

keypoints, im_with_keypoints = blob_detect()

coords=[] #make an empty array to fill with coordinates

def blobs_to_coords(): # put the angle in degree and distance in pixels of each blob from the center of the image
    number_of_blobs = len(keypoints)
    print("number of blobs: ", number_of_blobs)
    ycenter = frame.shape[0]/2 #find the center of the frame. frame.shape returns rows, columns, and channels (if the image is color)
    xcenter = frame.shape[1]/2
    cv2.circle(im_with_keypoints, (int(xcenter), int(ycenter)), 10, (0, 255, 0), -1) #place a cricle at the center
    cv2.circle(im_with_keypoints, (10, 10), 10, (0, 255, 0), -1) #place a circle at the xy origin corner

    i = 0
    while i < number_of_blobs:
        x = int(round(keypoints[i].pt[0])) #i is the index of the blob you want to get the position
        y = int(round(keypoints[i].pt[1]))
        #print("x, y:", x, y)
        cv2.circle(im_with_keypoints, (x, y), 20, (255, 0, 0), -1) #Adds a blue circle over the detected blob

        #plan is to get the distance from center and angle
        #use math.atan2 and math.dist
        #math.atan2 returns -pi to +pi
        #0 degrees is along the x axis and increases in a clockwise direction up to 180 and decreases to -180 in an anti-clockwise direction
        y = y - ycenter
        x = x - xcenter
        #print("x, y:", x, y)
        radians = math.atan2(y, x)
        distance = round(math.hypot(y, x),0)
        degrees = round(math.degrees(radians),0)+180
        coords.append([degrees,distance])
        print("degrees", degrees, "distance:", distance)
        i = i + 1 #increment the for loop

blobs_to_coords() 

#we want to have an arbitrary number of radial slices. if it is in a certain section it should be sent to a different OSC server
segment_count = 10 #how many different control segments
segment_size = 360/segment_count


number_of_blobs = len(keypoints)

i = 0
x = 0
a = 0
for i in range(0, number_of_blobs): # Iterate through all the blobs we found
    degrees = coords[x][0]
    for a in range(0,segment_count):
        if degrees>a*segment_size and degrees<(a+1)*segment_size: # Check which segment the blob is in.
            print(a)
            coords[x][0] = a # Swap the angle for which segment the blob is in

    x=x+1

#I want to get the average distance of blobs within each segment and use this to output to OSC

#this code doesn't work at all
#i = 0
#while i<segment_count:
#    if coords[i][0] in segment_count:
#        print("segment ",coords[i][0],": ",coords[i][1])
#    i=i+1

print(coords)

cv2.imwrite("Images/test_images/output.jpg", im_with_keypoints)

# Show keypoints
# cv2.imshow("Keypoints", im_with_keypoints)
# cv2.waitKey(0)


