from test.fake_camera import FakeCamera


class FakeDiscovery:

    def __init__(self):
        self.cameras = []

        self.camera1 = FakeCamera(
            "test1",
            "Test Camera 1",
        )

        self.camera2 = FakeCamera(
            "test2",
            "Test Camera 2",
        )

        self.camera3 = FakeCamera(
            "test3",
            "Test Camera 3",
        )

    def discover(self):

        return list(self.cameras)

    def add_camera(self, camera_number):

        camera = getattr(
            self,
            f"camera{camera_number}",
        )

        if camera not in self.cameras:
            self.cameras.append(camera)

            print(
                f"Fake camera {camera.name} appeared"
            )

    def remove_camera(self, camera_number):

        camera = getattr(
            self,
            f"camera{camera_number}",
        )

        if camera in self.cameras:
            self.cameras.remove(camera)

            print(
                f"Fake camera {camera.name} disappeared"
            )