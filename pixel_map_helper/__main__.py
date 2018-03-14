# Take an image and resize to something sane
# Using mouse clicks associate that pixel coordinate with an arbitrary pixel number.

# TODO
# Make a line tool that allows you to stretch an arbitrary number of pixels between two mouse clicks
# Use a button press to mark down the transition to new groups of pixels
# Make a "snap" grid that is a few pixels wide to allow for easier vertical/horizontal alignment
# Allow resizing of loaded image (can easily do this manually beforehand)
#

import numpy as np
import cv2
import sys
import os
from pprint import pformat


def main(input_file, output_file):
    led_canvas_array = []
    img = cv2.imread(input_file, 1)

    def handle_mouse_events(event, x, y, _flags, master_array):
        if event == cv2.EVENT_LBUTTONDOWN:
            blue = (255, 0, 0)
            handle_left_mouse_click(x, y, master_array, blue)
        if event == cv2.EVENT_FLAG_RBUTTON:
            red = (0, 0, 255)
            handle_right_click(x, y, master_array, red)

    def handle_left_mouse_click(x, y, master_array, color):
        create_circle(color, x, y)
        new_array = [x, y]
        master_array.append(new_array)
        print(pformat(master_array))

    def handle_right_click(x, y, master_array, color):
        number_of_leds = 0
        green = (0, 255, 0)
        create_circle(green, x, y)
        while number_of_leds < 1:
            number_of_leds = ask_for_a_number()

        def handle_second_click(event, x2, y2, _flags, number_of_leds):
            if event == cv2.EVENT_LBUTTONDOWN:
                print('actual first point:' + 'x(' + str(x) + ') ' + 'y(' + str(y) + ")")
                print('actual last point:' + 'x(' + str(x2) + ') ' + 'y(' + str(y2) + ")")
                create_circle(green, x2, y2)
                length_of_x_line = x2 - x
                length_of_y_line = y2 - y

                for i in range(number_of_leds):
                    new_x = int(round(x + (length_of_x_line / (number_of_leds - 1)) * i))
                    new_y = int(round(y + (length_of_y_line / (number_of_leds - 1)) * i))
                    print(str(i + 1) + ' point:' + 'x(' + str(new_x) + ') ' + 'y(' + str(new_y) + ")")
                    handle_left_mouse_click(new_x, new_y, master_array, color)

                cv2.setMouseCallback('image', handle_mouse_events, led_canvas_array)

        cv2.setMouseCallback('image', handle_second_click, number_of_leds)

    def ask_for_a_number():
        number_of_leds_string = input("Enter number of LEDs (must be greater than 1)")
        try:
            leds = int(number_of_leds_string)
            print("creating " + number_of_leds_string + " points")
            return leds
        except ValueError:
            leds = 0
            print('Please enter a number')
        return leds

    def create_circle(color, x, y):
        cv2.circle(img, (x, y), 5, color, -1)

    cv2.namedWindow('image')
    cv2.setMouseCallback('image', handle_mouse_events, led_canvas_array)

    execute_main_loop(img, led_canvas_array, output_file)


def execute_main_loop(img, led_canvas_array, output_file):
    while True:
        cv2.imshow('image', img)
        esc_key_pressed = (cv2.waitKey(20) & 0xFF) == 27
        if esc_key_pressed:
            filename = output_file if output_file is not None else input("Enter a file name:")
            np_array = np.array(led_canvas_array)
            np.savetxt(filename, np_array)
            np.save(filename, np_array)
            break


if __name__ == '__main__':
    in_file = sys.argv[1] if len(sys.argv) > 1 else 'Images/h2o_sign.png'
    if not os.path.isfile(in_file):
        raise UserWarning("not a file: %s" % in_file)
    out_file = ('test_output/' + sys.argv[2]) if len(sys.argv) > 2 else None
    main(in_file, out_file)
