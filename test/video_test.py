import flet as ft
import base64
import cv2
import asyncio

from test.fake_camera import FakeCamera
from services.camera_stream import CameraStreamManager


class VideoTestPage:

    def __init__(self, page):
        self.page = page

        self.stream_manager = CameraStreamManager()

        self.cameras = [
            FakeCamera("test1", "Test Camera 1"),
            FakeCamera("test2", "Test Camera 2"),
            FakeCamera("test3", "Test Camera 3"),
        ]

        self.images = {}
        self.running = True

        self.grid = ft.GridView(
            expand=True,
            runs_count=2,
            max_extent=500,
            spacing=15,
            run_spacing=15,
        )

    async def start(self):

        for camera in self.cameras:

            stream = self.stream_manager.add_camera(
                camera
            )

            stream.connect()

            image = ft.Image(
                src = b"",
                width=560,
                height=350,
                fit="contain",
            )

            self.images[
                camera.camera_id
            ] = image

            card = ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column(
                        [
                            ft.Text(
                                camera.name,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                            image,
                            ft.Text("LIVE"),
                        ]
                    ),
                )
            )

            self.grid.controls.append(card)

        self.page.update()

        self.page.run_task(
            self.update_frames
        )

    async def update_frames(self):

        while self.running:

            for camera in self.cameras:

                stream = (
                    self.stream_manager.get_stream(
                        camera.camera_id
                    )
                )

                if stream is None:
                    continue

                frame = stream.get_frame()

                if frame is None:
                    continue

                success, encoded = cv2.imencode(
                    ".jpg",
                    frame,
                    [
                        cv2.IMWRITE_JPEG_QUALITY,
                        75,
                    ],
                )

                if not success:
                    continue

                image_data = encoded.tobytes()
                

                self.images[
                    camera.camera_id
                ].src = image_data

            try:
                if self.page.session is not None:
                    self.page.update()

            except RuntimeError:
                self.running = False
                break

            await asyncio.sleep(0.05)

    def stop(self):
        self.running = False
        self.stream_manager.stop_all()

    def build(self):

        return ft.Column(
            [
                ft.Text(
                    "MULTI-CAMERA VIDEO TEST",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                ),
                self.grid,
            ],
            expand=True,
        )


def main(page: ft.Page):

    page.title = "IP Camera Video Test"

    page.window.width = 1200
    page.window.height = 800

    test_page = VideoTestPage(page)

    page.add(
        test_page.build()
    )

    page.run_task(
        test_page.start
    )


if __name__ == "__main__":
    ft.run(main)