import numpy as np
import sys


def main(lep_map_file, touch_map_file):
    led_map = np.load(lep_map_file)
    touch_map = np.load(touch_map_file)

    h = 303
    s = 68
    v = 66
    pink = np.array([h, s, v])

    mapped_frames = []
    for frame in touch_map:
        mapped_frames.append(map_frame(frame, led_map, pink))
    print('led_map')
    print(led_map)
    print('touch_map')
    print(touch_map)
    return np.array(mapped_frames)


def map_frame(frame, led_map, color):
    frame_array = []
    for touch_point in frame:
        closest_point = {
            'point': None,
            'distance': sys.maxsize
        }
        for led_point in led_map:
            distance = np.linalg.norm(touch_point - led_point)
            if distance < closest_point['distance']:
                closest_point['point'] = led_point
                closest_point['distance'] = distance
        frame_array.append(np.array([closest_point['point'], color]))

    return np.array(frame_array)


if __name__ == '__main__':
    lep_file = ('test_output/' + sys.argv[1]) if len(sys.argv) > 1 else 'test_output/led_map_test.npy'
    touch_file = ('test_output/' + sys.argv[2]) if len(sys.argv) > 2 else 'test_output/touch_out.npy'
    mapped_points = main(lep_file, touch_file)
    print('mapped_points')
    print(mapped_points)
