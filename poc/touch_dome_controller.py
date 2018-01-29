import cv2
import numpy as np
from video_blob_detect import find_fingers


def apply_color(frame, point_array, radius, color):
    for center in point_array:
        cv2.circle(frame, center, radius, color, -1)


# Create a black image
img = np.zeros((960, 1280, 3), np.uint8)
# hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
while True:
    # Capture frame-by-frame
    cap = cv2.VideoCapture(0)
    _, camera_frame = cap.read()

    centers = find_fingers(camera_frame, False)
    apply_color(img, centers, 10, (295, 79, 100))
    cv2.imshow('finger finder', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print('exiting')
        cap.release()
        cv2.destroyAllWindows()
