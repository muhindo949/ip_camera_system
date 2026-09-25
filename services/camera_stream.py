import cv2
import threading
import time


class CameraStream:
    def __init__(self, camera):
        self.camera = camera
        self.capture = None
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.latest_frame = None


    #
    def _fake_read_loop(self):
        while self.running:
            frame = self.camera.create_frame()

            with self.lock:
                self.latest_frame = frame

            time.sleep(0.03)

        self.camera.connected = False
    
    # 


    def connect(self):
        url = self.camera.get_connection_url()


        #
        if url == "fake://camera":
            self.camera.connected = True
            self.camera.online = True
            self.running = True

            self.thread = threading.Thread(
                target=self._fake_read_loop,
                daemon=True,
            )
            self.thread.start()

            print(
                f"{self.camera.name} connected (FAKE)"
            )

            return True

        #
        

        if not url:
            print(f"No RTSP url for {self.camera.name}")
            return False

        print(f"Connecting to {self.camera.name}: {url}")

        self.capture = cv2.VideoCapture(
            url,
            cv2.CAP_FFMPEG,
            )
        
        if not self.capture.isOpened():
            print(
                f"Could not connect to {self.camera.name}"
            )
            self.camera.connected = False
            self.camera.online = False
            self.capture.release()
            self.capture = None

            return False
        

        self.camera.connected = True
        self.camera.online = True
        self.running = True

        self.thread = threading.Thread(
            target = self._read_loop,
            daemon = True,
        )
        self.thread.start()

        print(
            f"{self.camera.name} connected"
        )

        return True


    def _read_loop(self):
        while self.running:
            if self.capture is None:
                break

            success, frame = (
                self.capture.read()
            )
            if not success:

                print(
                    f"Lost video from {self.camera.name}"
                )
                self.camera.connected = False
                time.sleep(1)

                continue

            with self.lock:
                self.latest_frame = frame

        self.camera.connected = False

    def get_frame(self):
        with self.lock:
            if self.latest_frame is None:
                return None

            return self.latest_frame.copy()

        


    def read_frame(self):
        if self.capture is None:
            return None
        if not self.running:
            return None

        success, frame = self.capture.read()
        if not success:
            return None

        return frame

    def stop(self):
        self.running = False
        if self.capture is not None:
            self.capture.release()
            self.capture = None

        self.camera.connected = False

        print(
            f"{self.camera.name} disconnected"
        )

class CameraStreamManager:
    def __init__(self):
        self.streams = {}

    def add_camera(self, camera):
        if camera.camera_id in self.streams:
            return self.streams[
                camera.camera_id
            ]

        stream = CameraStream(camera)
        self.streams[
            camera.camera_id
        ] = stream

        return stream
    

    def get_stream(self, camera_id):
        return self.streams.get(camera_id)

    def remove_camera(self, camera_id):
        stream = self.streams.get(camera_id)
        if stream is None:
            return

        stream.stop()

        del self.streams[camera_id]


    def get_all_streams(self):
        return self.streams

    def stop_all(self):
        for stream in list(
            self.streams.values()
        ):
            stream.stop()

        self.streams.clear()