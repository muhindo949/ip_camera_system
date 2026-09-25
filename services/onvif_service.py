from onvif import ONVIFCamera

class ONVIFService:
    async def get_rtsp_url(
            self,
            camera,
            username = "",
            password= "",
    ):
        try:
            onvif_camera = ONVIFCamera(
                camera.ip_address,
                camera.port,
                username,
                password,
            )

            await onvif_camera.update_xaddrs()
            media = onvif_camera.create_media_service()
            profiles = await media.GetProfiles()

            if not profiles:
                print(
                    f"No media profiles found for {camera.ip_address}"
                )
                await onvif_camera.close()

                return None

            profile  = profiles[0]
            request = media.create_type(
                "GetStreamUri"
            )

            request.ProfileToken = profile.token
            request.StreamSetup = {
                "Stream": "RTP-Unicast",
                "Transport": {
                    "protocol": "RTSP"
                },
            }

            response = await media.GetStreamUri(
                request
            )

            rtsp_url = str(response.Uri)
            await onvif_camera.close()
            return rtsp_url

        except Exception as error:
            print(
                f"ONVIF error for {camera.ip_address}: {error}"
            )
            return None
        






















