import flet as ft
from authentication.login import Authentication

class LoginPage:
    def __init__(
            self,
            page,
            on_login_success,
    ):
        self.page = page
        self.on_login_success = (
            on_login_success
        )
        self.authentication = Authentication()

        self.username = ft.TextField(
            label = "Username",
            width = 350,
            autofocus = True,
        )

        self.password = ft.TextField(
            label = "Password",
            password = True,
            can_reveal_password = True,
            width = 350,
            on_submit = self.login,
        )

        self.status_text = ft.Text("",)


    def login(self, e):
        username = (self.username.value.strip())
        password = (self.password.value)

        if not username or not password:
            self.status_text.value = (
                "Please enter username and password"
            )
            self.page.update()
            return

        success = self.authentication.login(
            username,
            password,
        )
        if success:
            self.status_text.value = (
                "Login successful"
            )
            self.page.update()
            self.on_login_success()

        else:
            self.status_text.value = (
                "Invalid username or password"
            )
            self.password.value = ""
            self.page.update()


    def build(self):
        return ft.Container(
            expand = True,
            alignment = ft.Alignment.CENTER,
            content = ft.Column(
                [
                    ft.Text(
                        "IP CAMERA SYSTEM",
                        size = 30,
                        weight = ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Administrator Login",
                        size = 20,
                    ),
                    ft.Divider(),

                    self.username,
                    self.password,
                    self.status_text,

                    ft.ElevatedButton(
                        "LOGIN",
                        width = 350,
                        on_click = self.login,
                    ),
                ],
                horizontal_alignment = (
                    ft.CrossAxisAlignment.CENTER
                ),
                spacing = 15,
            ),
        )