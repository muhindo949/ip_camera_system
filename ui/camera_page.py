import flet as ft
import cv2
import asyncio
from services.onvif_service import ONVIFService
from scanner.network_scanner import NetworkScanner
from services.camera_discovery import CameraDiscovery
from services.camera_stream import CameraStreamManager

class CameraPage:
    def __init__(self, page):
        self.page = page
        self.discovery = CameraDiscovery(
            timeout = 2
        )
        self.network_scanner = (
            NetworkScanner()
        )
        self.onvif_service = (
            ONVIFService()
        )
        self.stream_manager = (
            CameraStreamManager()
        )

        self.camera_cards = {}
        self.monitoring = True
        self.status_text = ft.Text(
            "Starting camera monitoring..."
        )

      
        self.camera_grid = ft.GridView(
            expand = True,
            runs_count = 2,
            max_extent = 500,
            spacing = 15,
            run_spacing = 15,
        )

        

        self.search_button = ft.Button(
            "Search for Cameras",
            on_click = self.manual_search,
        )


    async def start(self):
        self.page.run_task(
            self.monitor_cameras
        )
        self.page.run_task(
            self.update_video_frames
        )

    async def monitor_cameras(self):
        await asyncio.sleep(1)
        while self.monitoring:
            try:
                self.status_text.value = (
                    "Searching for cameras..."
                )
                self.page.update()

                cameras = await asyncio.to_thread(
                    self.discovery.discover
                )

                await self.process_discovered_cameras(
                    cameras
                )
                self.status_text.value = (
                    f"{len(cameras)} camera(s) currently detected"
                )
                self.page.update()

            except Exception as error:
                print(
                    f"Camera monitoring error: {error}"
                )

            await asyncio.sleep(60)



    async def process_discovered_cameras(
            self,
            cameras,
    ):
        discovered_ids = set()
        for camera in cameras:
            discovered_ids.add(
                camera.camera_id

            )
            if camera.camera_id not in self.camera_cards:
                await self.add_camera(
                    camera
                )

        existing_ids = list(
            self.camera_cards.keys()
        )

        for camera_id in existing_ids:
            if camera_id not in discovered_ids:
                self.remove_camera(
                    camera_id
                )


    async def add_camera(self, camera):
        print(
            f"New camera detected: {camera.ip_address}"
        )
        camera.username = ""
        camera.password = ""

        card = self.create_camera_card(
            camera
        )
        self.camera_cards[
            camera.camera_id
        ] = {
            "camera": camera,
            "card": card,
        }

        self.camera_grid.controls.append(
            card
        )

        self.page.update()


    def create_camera_card(
            self,
            camera,
    ):
        image = ft.Image(
            src = b"",
            width = 560,
            height = 350,
            fit = "contain",
        )

        status = ft.Text(
            "Detected"
        )
        username = ft.TextField(
            label = "Username",
            width = 250,
        )

        password = ft.TextField(
            label = "Password",
            password = True,
            width = 250,
        )

        connect_button = ft.Button(
            "Connect",
            on_click = lambda e:
            self.connect_camera(
                camera,
                username,
                password,
                status,
            ),
        )

        stop_button = ft.Button(
            "Stop",
            on_click = lambda e:
            self.stop_camera(
                camera,
                status,
            ),
        )

        return ft.Card(
            content = ft.Container(
                padding = 15,
                content = ft.Column(
                    [
                        ft.Text(
                            camera.name,
                            size = 20,
                            weight = ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            f"IP: {camera.ip_address}"
                        ),
                        image,
                        status,

                        ft.Row(
                            [
                                username,
                                password,
                            ]
                        ),
                        ft.Row(
                            [
                                connect_button,
                                stop_button,
                            ]
                        ),
                    ]
                ),
            )
        )


    async def connect_camera(
            self,
            camera,
            username,
            password,
            status,
    ):
        status.value = (
            "Getting RTSP stream..."
        )
        self.page.update()

        camera.username = (
            username.value.strip()
        )

        camera.password = (
            password.value
        )

        rtsp_url = (
            await self.onvif_service.get_rtsp_url(
                camera,
                camera.username,
                camera.password,
            )
        )

        if not rtsp_url:
            status.value = (
                "could not get RTSP URL"
            )

            self.page.update()

            return

        print(f"RTSP URL found for {camera.name}")

        camera.stream_url = (
            rtsp_url
        )

        stream = (
            self.stream_manager.add_camera(
                camera
            )
        )
        status.value = ("Connecting to video...")
        self.page.update()

        connected = stream.connect()
        if connected:
            status.value = "LIVE"

        else:
            status.value = (
                "RTSP connection failed"
            )

        self.page.update()


    def stop_camera(
            self,
            camera,
            status,
    ):
        self.stream_manager.remove_camera(
            camera.camera_id
        )
        status.value = "Stopped"

        self.page.update()


    async def update_video_frames(self):
        while self.monitoring:
            try:
                for camera_id, data in list(
                    self.camera_cards.items()
                ):
                    camera = data["camera"]

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

                    success, encoded = (
                        cv2.imencode(
                            ".jpg",
                            frame,
                            [
                                cv2.IMWRITE_JPEG_QUALITY,
                                75,
                            ],
                        )
                    )

                    if not success:
                        continue

                    image_data = encoded.tobytes()
                  
                    card = data["card"]
                    image = self.find_image(
                        card
                    )
                    if image is not None:
                        image.src = image_data
                        
                if self.monitoring:
                    self.page.update()

                await asyncio.sleep(0.05)
            except RuntimeError as error:
                print(
                    f"Video update stopped: {error}"
                )
                break

            except Exception as error:
                print(
                    f"Video update error: error"
                )
                await asyncio.sleep(0.5)


    def find_image(self, card):
        def search(control):
            if isinstance(control,ft.Image,):
                return control

            if hasattr(
                control,
                "controls",
            ):
                for child in (control.controls):
                    result = search(child)
                    if result is not None:
                        return result

            if hasattr(
                control,
                "content",
            ):
                return search(control.content)

            return None

        return search(card)


    def remove_camera(
            self,
            camera_id,
    ):
        data = self.camera_cards.get(
            camera_id
        )
        if data is None:
            return

        self.stream_manager.remove_camera(
            camera_id
        )

        card = data["card"]

        if  card in self.camera_grid.controls:
            self.camera_grid.controls.remove(
                card
            )

        del self.camera_cards[camera_id]

        self.page.update()

    async def manual_search(self, e):
        self.status_text.value = ("Searching...")
        self.page.update()

        cameras = await asyncio.to_thread(
            self.discovery.discover
        )

        await self.process_discovered_cameras(
            cameras
        )
        self.status_text.value = (
            f"{len(cameras)} camera(s) found"
        )
        self.page.update()

    def build(self):
        return ft.Column(
            [
                ft.Text(
                    "IP CAMERA SYSTEM",
                    size = 28,
                    weight = ft.FontWeight.BOLD,
                ),
                self.status_text,
                self.search_button,

                ft.Divider(),

                self.camera_grid,
            ],
            expand = True,
        )

    def stop(self):
        self.monitoring = False
        self.stream_manager.stop_all()


    




