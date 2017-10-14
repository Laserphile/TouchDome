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


def main(input_file, output_file):
    led_canvas_array = []
    img = cv2.imread(input_file, 1)

    def handle_mouse_events(event, x, y, _flags, master_array):
        if event == cv2.EVENT_LBUTTONDOWN:
            handle_mouse_click(x, y, master_array)

    def handle_mouse_click(x, y, master_array):
        cv2.circle(img, (x, y), 5, (255, 0, 0), -1)
        new_array = [x, y, len(master_array)]
        master_array.append(new_array)
        print(np.array(master_array))

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
    out_file = sys.argv[2] if len(sys.argv) > 2 else None
    main(in_file, out_file)
