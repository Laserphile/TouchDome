import cv2 as cv

if __name__ == '__main__':
    capture_index = 0
    while capture_index < 2600:
        cap = cv.VideoCapture(capture_index)
        backend_idx = cap.get(cv.CAP_PROP_BACKEND)
        if backend_idx > 0:
            width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
            codec = cap.get(cv.CAP_PROP_FOURCC)
            backend = cap.getBackendName()
            print(f"index {capture_index}: {cap}, width {width} height {height} backend {backend} ({backend_idx}), codec {codec}")
            result = False
            camera_frame = None
            while not result:
                result, camera_frame = cap.read()
            cv.imshow(f'indx {capture_index}', camera_frame)

        wait_key = cv.waitKey(1) & 0xFF
        capture_index += 1
