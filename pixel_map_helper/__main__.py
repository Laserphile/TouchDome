# Take an image and resize to something sane
# Using mouse clicks associate that pixel coordinate with an arbitrary pixel number.

# TODO
# Use a button press to mark down the transition to new groups of pixels
# Make a "snap" grid that is a few pixels wide to allow for easier vertical/horizontal alignment
#

# DONE
# Make a line tool that allows you to stretch an arbitrary number of pixels between two mouse clicks
# Allow resizing of loaded image (can easily do this manually beforehand)

import numpy as np
import cv2
import sys
import os
from pprint import pformat

NUMBER_OF_LEDS_UI_NAME = 'LEDs'
MAIN_WINDOW = 'image_window'
COLOUR_GREEN = (0, 255, 0)
COLOUR_RED = (0, 0, 255)
COLOUR_BLUE = (255, 0, 0)


def create_circle(canvas, color, x, y):
    cv2.circle(canvas, (x, y), 5, color, -1)

def nothing(x):
    pass


def main(input_file, output_file):
    led_canvas_array = []
    canvas = cv2.imread(input_file, 1)

    def handle_mouse_events(event, x, y, _flags, master_array):
        if event == cv2.EVENT_LBUTTONDOWN:
            handle_left_mouse_click(x, y, master_array, COLOUR_BLUE)
        if event == cv2.EVENT_FLAG_RBUTTON:
            handle_right_click(x, y, master_array, COLOUR_RED)

    def handle_left_mouse_click(x, y, master_array, color):
        create_circle(canvas, color, x, y)
        new_coordinate = [x, y]
        master_array.append(new_coordinate)
        print(pformat(master_array))

    def handle_right_click(x, y, master_array, color):
        number_of_leds = 0
        number_of_leds = cv2.getTrackbarPos(NUMBER_OF_LEDS_UI_NAME, MAIN_WINDOW)
        if number_of_leds < 2:
            print("can't draw less than 2 leds.")
            return
        create_circle(canvas, COLOUR_GREEN, x, y)

        def handle_second_click(event, x2, y2, _flags, number_of_leds):
            if event == cv2.EVENT_LBUTTONDOWN:
                print('actual first point:' + 'x(' + str(x) + ') ' + 'y(' + str(y) + ")")
                print('actual last point:' + 'x(' + str(x2) + ') ' + 'y(' + str(y2) + ")")
                create_circle(canvas, COLOUR_GREEN, x2, y2)
                length_of_x_line = x2 - x
                length_of_y_line = y2 - y

                for i in range(number_of_leds):
                    new_x = int(round(x + (length_of_x_line / (number_of_leds - 1)) * i))
                    new_y = int(round(y + (length_of_y_line / (number_of_leds - 1)) * i))
                    print(str(i + 1) + ' point:' + 'x(' + str(new_x) + ') ' + 'y(' + str(new_y) + ")")
                    # first dot in line is blue, rest are red
                    if i == 0:
                        handle_left_mouse_click(new_x, new_y, master_array, COLOUR_BLUE)
                    else:
                        handle_left_mouse_click(new_x, new_y, master_array, color)

                cv2.setMouseCallback(MAIN_WINDOW, handle_mouse_events, led_canvas_array)

        cv2.setMouseCallback(MAIN_WINDOW, handle_second_click, number_of_leds)

    # This allows window to be resized

    window_flags = 0
    window_flags |= cv2.WINDOW_NORMAL
    # window_flags |= cv2.WINDOW_AUTOSIZE
    # window_flags |= cv2.WINDOW_FREERATIO
    window_flags |= cv2.WINDOW_KEEPRATIO

    cv2.namedWindow(MAIN_WINDOW, flags=window_flags)
    cv2.setMouseCallback(MAIN_WINDOW, handle_mouse_events, led_canvas_array)
    cv2.createTrackbar(NUMBER_OF_LEDS_UI_NAME, MAIN_WINDOW, 2, 128, nothing)

    # Main loop

    while True:
        cv2.imshow(MAIN_WINDOW, canvas)
        keycode = (cv2.waitKey(20) & 0xFF)
        if keycode == 27:
            # esc key pressed, save output
            filename = output_file if output_file is not None else input("Enter a file name:")
            np_array = np.array(led_canvas_array)
            np.savetxt(filename, np_array)
            np.save(filename, np_array)
            break
        elif keycode == 8:
            # backspace pressed, delete last point
            del led_canvas_array[-1]
            canvas = cv2.imread(input_file, 1)
            for point in led_canvas_array:
                create_circle(canvas, COLOUR_RED, *point)



if __name__ == '__main__':
    in_file = sys.argv[1] if len(sys.argv) > 1 else 'Images/h2o_sign.png'
    if not os.path.isfile(in_file):
        raise UserWarning("not a file: %s" % in_file)
    out_file = ('test_output/' + sys.argv[2]) if len(sys.argv) > 2 else None
    main(in_file, out_file)
