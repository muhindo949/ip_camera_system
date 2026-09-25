import cv2
import numpy as np

class FakeCamera:
    def __init__(self, camera_id, name):
        self.camera_id = camera_id
        self.name = name
        self.ip_address = "127.0.0.1"

        self.username = ""
        self.password = ""

        self.stream_url = "fake://camera"

        self.connected = False
        self.online = False


    def get_connection_url(self):
        return self.stream_url

    def create_frame(self):
        frame = np.zeros(
            (480, 640, 3),
            dtype = np.uint8
        )

        cv2.putText(
            frame,
            self.name,
            (150, 220),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (255,255,255),
            3,
        )
        cv2.putText(
            frame,
            "TEST VIDEO",
            (200,200),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255,255,255),
            2,
        )
        return frame