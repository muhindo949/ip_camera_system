import flet as ft
import asyncio
import cv2

from test.fake_discovery import FakeDiscovery
from services.camera_stream import CameraStreamManager


class DynamicTestPage:

    def __init__(self, page):
        self.page = page

        self.discovery = FakeDiscovery()
        self.stream_manager = CameraStreamManager()

        self.camera_cards = {}

        self.running = True

        self.status = ft.Text(
            "No cameras currently"
        )

        self.grid = ft.GridView(
            expand=True,
            runs_count=2,
            max_extent=500,
            spacing=15,
            run_spacing=15,
        )

    async def start(self):

        self.page.run_task(
            self.monitor_cameras
        )

        self.page.run_task(
            self.update_frames
        )

        self.page.run_task(
            self.simulate_cameras
        )

    async def simulate_cameras(self):

        # Start with no cameras
        await asyncio.sleep(3)

        # Camera 1 appears
        self.discovery.add_camera(1)

        await asyncio.sleep(5)

        # Camera 2 appears
        self.discovery.add_camera(2)

        await asyncio.sleep(5)

        # Camera 3 appears
        self.discovery.add_camera(3)

        await asyncio.sleep(7)

        # Camera 1 disappears
        self.discovery.remove_camera(1)

        await asyncio.sleep(7)

        # Camera 2 disappears
        self.discovery.remove_camera(2)

        await asyncio.sleep(5)

        self.running = False

    async def monitor_cameras(self):

        while self.running:

            cameras = self.discovery.discover()

            await self.process_cameras(
                cameras
            )

            if len(cameras) == 0:
                self.status.value = (
                    "No cameras currently"
                )
            else:
                self.status.value = (
                    f"{len(cameras)} camera(s) detected"
                )

            try:
                self.page.update()
            except RuntimeError:
                self.running = False
                break

            await asyncio.sleep(1)

    async def process_cameras(
        self,
        cameras,
    ):

        discovered_ids = set()

        for camera in cameras:

            discovered_ids.add(
                camera.camera_id
            )

            if camera.camera_id not in self.camera_cards:

                print(
                    f"Adding {camera.name} to UI"
                )

                stream = (
                    self.stream_manager.add_camera(
                        camera
                    )
                )

                stream.connect()

                image = ft.Image(
                    src=b"",
                    width=560,
                    height=350,
                    fit="contain",
                )

                self.camera_cards[
                    camera.camera_id
                ] = {
                    "camera": camera,
                    "image": image,
                }

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
                                ft.Text(
                                    f"IP: {camera.ip_address}"
                                ),
                                image,
                                ft.Text(
                                    "LIVE"
                                ),
                            ]
                        ),
                    )
                )

                self.camera_cards[
                    camera.camera_id
                ]["card"] = card

                self.grid.controls.append(
                    card
                )

        existing_ids = list(
            self.camera_cards.keys()
        )

        for camera_id in existing_ids:

            if camera_id not in discovered_ids:

                print(
                    f"Removing camera {camera_id}"
                )

                self.stream_manager.remove_camera(
                    camera_id
                )

                card = self.camera_cards[
                    camera_id
                ]["card"]

                if card in self.grid.controls:
                    self.grid.controls.remove(
                        card
                    )

                del self.camera_cards[
                    camera_id
                ]

    async def update_frames(self):

        while self.running:

            for camera_id, data in list(
                self.camera_cards.items()
            ):

                stream = (
                    self.stream_manager.get_stream(
                        camera_id
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

                data["image"].src = (
                    encoded.tobytes()
                )

            try:
                self.page.update()
            except RuntimeError:
                self.running = False
                break

            await asyncio.sleep(0.05)

    def build(self):

        return ft.Column(
            [
                ft.Text(
                    "DYNAMIC CAMERA TEST",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                ),
                self.status,
                ft.Divider(),
                self.grid,
            ],
            expand=True,
        )

    def stop(self):

        self.running = False

        self.stream_manager.stop_all()


def main(page: ft.Page):

    page.title = "Dynamic Camera Test"

    page.window.width = 1200
    page.window.height = 800

    test_page = DynamicTestPage(page)

    page.add(
        test_page.build()
    )

    page.run_task(
        test_page.start
    )


if __name__ == "__main__":
    ft.run(main)