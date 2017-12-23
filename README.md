A camera is used to record touches on a semi-transparent surface.

## Requirements
Requires Python3

Install prerequisite packages with
```
pip install -r requirements.txt
```

## Structure

touch_detect.py shows clear image of touch.
touch_coordinates.py pulls touch coordinates from the image in x and y pixels
camera_mask_test.py examples of using static images as a mask
pixel_map_helper.py load an image of a physical array of pixels and use mouse clicks to map the LED locations
