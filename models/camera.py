class Camera:
    def __init__(
            self,
            camera_id,
            name,
            ip_address,
            protocol = "rtsp",
            port = 554,
            username = "",
            password = "",
            onvif_url = "",
            stream_url = "",
    ):
        self.camera_id = camera_id
        self.name = name
        self.ip_address = ip_address
        self.protocol = protocol
        self.port = port
        self.username = username
        self.password = password

        """ONVIF devices-service url"""
        self.onvif_url = onvif_url

        """actual RTSP video url"""
        self.stream_url = stream_url

        self.connected = False
        self.online = False


    def get_connection_url(self):
        return self.stream_url
