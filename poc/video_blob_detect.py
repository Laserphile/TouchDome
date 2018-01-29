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
    brightness_scale_factor = 1
    black_and_white_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2GRAY) * brightness_scale_factor
    bitwised_framed = cv2.bitwise_not(black_and_white_frame)

    # the below variables get the cutoff points for color differentiation
    gs_lower_color = np.array(135, dtype="uint8")
    gs_upper_color = np.array(255, dtype="uint8")

    # Blurring the image will cutout noise and give you better contours with less points
    blurred_frame = cv2.blur(bitwised_framed, (20, 60))

    color_cut_frame = cv2.inRange(blurred_frame, gs_lower_color, gs_upper_color)

    ret2, final_frame = cv2.threshold(color_cut_frame, 254, 255, cv2.THRESH_BINARY)

    final_frame, contours, hierarchy = cv2.findContours(final_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    final_frame = cv2.cvtColor(final_frame, cv2.COLOR_GRAY2RGB)

    # Changing me will change what opencv draws circles around.
    #   Too high and everything is a circle, too low and fingers are not seen.
    contour_min_sensitivity = 20
    contour_max_sensitivity = 200

    output_array = []

    for cnt in contours:
        is_finger_contour = contour_min_sensitivity < len(cnt) < contour_max_sensitivity

        if is_finger_contour:
            circle = cv2.minEnclosingCircle(cnt)
            center = tuple(np.ceil(circle[0]).astype(int))
            if picture_mode:
                radius = np.ceil(circle[1]).astype(int)
                draw_cross(final_frame, center, radius)
            else:
                output_array.append(center)

    return final_frame if picture_mode else output_array


if __name__ == '__main__':
    while True:
        # Capture frame-by-frame
        cap = cv2.VideoCapture(0)
        _, camera_frame = cap.read()

        frame = find_fingers(camera_frame)
        cv2.imshow('finger finder', frame)
        print('waiting on user input')
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print('exiting')
            cv2.destroyAllWindows()
