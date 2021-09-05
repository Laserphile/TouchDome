# Takes the video from the touch input dome and outputs the coordinates of where you are touching

import numpy as np
import cv2


def draw_cross(img, center, length):
    cv2.line(img, tuple(np.subtract(center, (length, 0))), tuple(np.add(center, (length, 0))),
             (255, 0, 0), 2)
    cv2.line(img, tuple(np.subtract(center, (0, length))), tuple(np.add(center, (0, length))),
             (255, 0, 0), 2)
    return img


def find_fingers(input_frame, picture_mode=True):
    flipped_frame = cv2.flip(input_frame, 1)
    # TODO: detect if black and white
    bw_input_frame = input_frame
    # bw_input_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2GRAY)

    bitwised_framed = cv2.bitwise_not(bw_input_frame)

    # the below variables get the cutoff points for color differentiation
    gs_lower_color = np.array(135, dtype="uint8")
    gs_upper_color = np.array(255, dtype="uint8")

    # Blurring the image will cutout noise and give you better contours with less points
    blurred_frame = cv2.blur(bitwised_framed, (20, 60))

    color_cut_frame = cv2.inRange(
        blurred_frame, gs_lower_color, gs_upper_color)

    ret2, final_frame = cv2.threshold(
        color_cut_frame, 254, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(
        final_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        print("contour not found")
        return final_frame

    final_frame = cv2.cvtColor(final_frame, cv2.COLOR_GRAY2RGB)

    # Changing me will change what opencv draws circles around.
    #   Too high and everything is a circle, too low and fingers are not seen.
    contour_min_sensitivity = 20
    contour_max_sensitivity = 200

    output_array = []

    for cnt in contours:
        is_finger_contour = contour_min_sensitivity < len(
            cnt) < contour_max_sensitivity

        if is_finger_contour:
            circle = cv2.minEnclosingCircle(cnt)
            center = tuple(np.ceil(circle[0]).astype(int))
            if picture_mode:
                radius = np.ceil(circle[1]).astype(int)
                draw_cross(final_frame, center, radius)
            else:
                output_array.append(center)

    return final_frame if picture_mode else output_array


def initialise_blob_detect():  # Set up the detector with default parameters.
    # Set up the detector with default parameters.
    params = cv2.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = 16
    params.maxThreshold = 100

    # Filter by Area (2d pixel count).
    params.filterByArea = True
    # params.filterByArea = False
    params.minArea = 10 * 10
    params.maxArea = 250 * 250

    # Filter by Circularity
    params.filterByCircularity = False
    params.minCircularity = 0.8

    # Filter by Convexity
    params.filterByConvexity = False
    params.minConvexity = 0.87

    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0.01

    # Filter by Color
    params.filterByColor = True
    # params.filterByColor = False
    params.blobColor = 255

    detector = cv2.SimpleBlobDetector_create(params)
    return detector


def matt_blob_detect(frame, detector):
    keypoints = detector.detect(frame)
    im_with_keypoints = cv2.drawKeypoints(frame, keypoints, np.array(
        []), (255, 0, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    return keypoints, im_with_keypoints


def calibrate(frame):
    # print("i just calibrated baby", end='\r')
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def to_black_and_white(frame):
    # print("i just bw'd baby", end='\r')
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def subtract_frames(this_frame, other_frame):
    # return this_frame - (0.85 * other_frame)

    assert(this_frame.shape == other_frame.shape)

    # return 0.85 * this_frame - other_frame

    # return np.fromiter(
    #     (np.max(this_pixel - 0.85 * other_pixel, 0)
    #         for this_pixel, other_pixel in np.nditer([this_frame, other_frame])),
    #     dtype=np.uint8
    # ).reshape(
    #     this_frame.shape
    # )
    # result = np.max(this_frame - other_frame, 0)
    # result = this_frame - other_frame
    result = np.maximum(this_frame - other_frame + 127,
                        [127]).reshape(this_frame.shape) - 127
    return result.astype(np.uint8)


if __name__ == '__main__':
    cap = cv2.VideoCapture(1401)
    # cap = cv2.VideoCapture(0)
    # try:
    bw_calibrate_frame = None
    # bw_calibrate_frame = cv2.imread("autocalibrate.jpg", cv2.IMREAD_GRAYSCALE)
    if bw_calibrate_frame is None:
        _, camera_frame = cap.read()
        bw_calibrate_frame = calibrate(camera_frame)

    mode = 'r'

    blob_detector = initialise_blob_detect()

    while True:
        # Capture frame-by-frame
        _, camera_frame = cap.read()
        wait_key = cv2.waitKey(10) & 0xFF
        if wait_key == ord('q'):
            print('\nexiting')
            cv2.destroyAllWindows()
            exit(0)
        elif wait_key == ord('c'):
            print("\ncalibrating")
            bw_calibrate_frame = calibrate(camera_frame)
            cv2.imshow("calibration", bw_calibrate_frame)
        # elif wait_key == ord('r'):
        #     print("\nshowing raw")
        #     cv2.imshow("raw", camera_frame)
        # else:
        #     frame = find_fingers(camera_frame)
        #     cv2.imshow('finger finder', frame)

        cv2.imshow("raw", camera_frame)

        bw_camera_frame = to_black_and_white(camera_frame)
        # cv2.BackgroundSubtractor()
        bw_subtracted_frame = subtract_frames(
            bw_camera_frame, bw_calibrate_frame)
        cv2.imshow("subtracted", bw_subtracted_frame)

        # bw_threshold_frame = cv2.threshold(bw_subtracted_frame, 127, 255, cv2.THRESH_BINARY_INV)
        _, bw_threshold_frame = cv2.threshold(
            bw_subtracted_frame, 16, 255, cv2.THRESH_BINARY)
        cv2.imshow("threshold", bw_threshold_frame)

        # finger_frame = find_fingers(bw_subtracted_frame)
        # cv2.imshow('finger finder', finger_frame)
        keypoints, im_with_keypoints = matt_blob_detect(
            bw_threshold_frame, blob_detector)
        cv2.imshow("keypoints", im_with_keypoints)
        print(f"keypoints: {keypoints}", end='\r')

        print('waiting on user input', end='\r')
