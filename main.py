import flet as ft
from ui.camera_page import CameraPage
from ui.login_page import LoginPage

def main(page: ft.Page):
    page.title = "IP Camera Access System"
    page.window.width = 1200
    page.window.height = 800

    page.padding = 20

    def show_camera_page():
        page.controls.clear()
        camera_page = CameraPage(page)

        page.add(
            camera_page.build()
        )
        page.run_task(
            camera_page.start
        )
        page.update()

    login_page  = LoginPage(
        page,
        on_login_success = show_camera_page,
    )
    page.add(
        login_page.build()
    )


if __name__ == "__main__":
    ft.run(main)