import socket
import uuid
import xml.etree.ElementTree as ET
from models.camera import Camera

class CameraDiscovery:
    def __init__(self, timeout = 3):
        self.timeout = timeout
        self.cameras = {}


    def discover(self):
        print("searching for ONVIF cameras...")

        responses = self.send_probe()
        discovered = {}

        for response in responses:
            camera = self.parse_response(
                response
            )
            if camera is not None:
                discovered[
                    camera.ip_address
                ] = camera

        self.cameras = discovered

        print(
            f"Found {len(self.cameras)} camera(s)"
        )

        return list(
            self.cameras.values()
        )

    def send_probe(self):
        message_id = (
            f"uuid:{uuid.uuid4()}"
        )

        probe = f"""<?xml version="1.0" encoding="UTF-8"?>
<e:Envelope
    xmlns:e="http://www.w3.org/2003/05/soap-envelope"
    xmlns:w="http://schemas.xmlsoap.org/ws/2004/08/addressing"
    xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery"
    xmlns:dn="http://www.onvif.org/ver10/network/wsdl">
    <e:Header>
        <w:MessageID>{message_id}</w:MessageID>
        <w:To>
            urn:schemas-xmlsoap-org:ws:2005:04:discovery
        </w:To>
        <w:Action>
            http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe
        </w:Action>
    </e:Header>
    <e:Body>
        <d:Probe>
            <d:Types>
                dn:NetworkVideoTransmitter
            </d:Types>
        </d:Probe>
    </e:Body>
</e:Envelope>
"""
        multicast_address = ("239.255.255.250")
        multicast_port = 3702
        responses = []

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP,
        )
        try:
            sock.setsockopt(
                socket.IPPROTO_IP,
                socket.IP_MULTICAST_TTL,
                2,
            )

            sock.settimeout(
                self.timeout
            )

            sock.sendto(
                probe.encode("utf-8"),
                (
                    multicast_address,
                    multicast_port,
                ),

            )

            while True:
                try:
                    data, address = (
                        sock.recvfrom(65535)
                    )
                    responses.append(
                        (
                            data.decode(
                                "utf-8",
                                error = "ignore",
                            ),
                            address,
                        )
                    )

                except socket.timeout:
                    break

        except Exception as error:
            print(f"ONVIF discovery error: {error}")

        finally:
            sock.close()

        return responses

    def parse_response(
            self,
            response,
    ):
        xml_data, address = response
        ip_address = address[0]

        try:
            root = ET.fromstring(
                xml_data
            )

        except ET.ParseError:
            return None

        xaddrs = []

        for element in root.iter():
            if element.tag.endswith(
                "XAddrs"
            ):
                if element.text:
                    xaddrs.extend(
                        element.text.split()
                    )

        port = 80
        protocol = "http"
        onvif_url = ""
        stream_url = ""

        for url in xaddrs:
            if url.startswith(
                "https://"
            ):
                protocol = "http"

            stream_url = url
            break

        if ":" in stream_url:
            try:
                after_protocol = (
                    stream_url.split(
                        "://",
                        1
                    )[1]
                )
                host_port = (
                    after_protocol.split(
                        "/",
                        1
                    )[0]
                )

                if ":" in host_port:
                    port = int(
                        host_port.rsplit(
                            ":",
                            1
                        )[1]
                    )

            except (
                ValueError,
                IndexError,
            ):
                port = 80

        camera = Camera(
            camera_id = ip_address,
            name = f"Camera {ip_address}",
            ip_address = ip_address,
            protocol = protocol,
            port = port,
            onvif_url = onvif_url,
        )

        camera.online = True
        return camera

    def get_cameras(self):
        return list(
            self.cameras.values()
        )





































    # def send_probe(self):

    #     message_id = f"uuid:{uuid.uuid4()}"

    #     probe = f"""<?xml version="1.0" encoding="UTF-8"?>
    # <e:Envelope
    #     xmlns:e="http://www.w3.org/2003/05/soap-envelope"
    #     xmlns:w="http://schemas.xmlsoap.org/ws/2004/08/addressing"
    #     xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery"
    #     xmlns:dn="http://www.onvif.org/ver10/network/wsdl">

    #     <e:Header>

    #         <w:MessageID>
    #             {message_id}
    #         </w:MessageID>

    #         <w:To>
    #             urn:schemas-xmlsoap-org:ws:2005:04:discovery
    #         </w:To>

    #         <w:Action>
    #             http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe
    #         </w:Action>

    #     </e:Header>

    #     <e:Body>

    #         <d:Probe>

    #             <d:Types>
    #                 dn:NetworkVideoTransmitter
    #             </d:Types>

    #         </d:Probe>

    #     </e:Body>

    # </e:Envelope>
    # """

    #     multicast_address = "239.255.255.250"
    #     multicast_port = 3702

    #     responses = []

    #     sock = socket.socket(
    #         socket.AF_INET,
    #         socket.SOCK_DGRAM,
    #         socket.IPPROTO_UDP,
    #     )

    #     try:

    #         # Use the Wi-Fi interface
    #         local_ip = self.get_local_ip()

    #         sock.setsockopt(
    #             socket.IPPROTO_IP,
    #             socket.IP_MULTICAST_IF,
    #             socket.inet_aton(local_ip),
    #         )

    #         sock.setsockopt(
    #             socket.SOL_SOCKET,
    #             socket.SO_REUSEADDR,
    #             1,
    #         )

    #         sock.settimeout(
    #             self.timeout
    #         )

    #         print(
    #             f"Sending ONVIF probe from {local_ip}"
    #         )

    #         sock.sendto(
    #             probe.encode("utf-8"),
    #             (
    #                 multicast_address,
    #                 multicast_port,
    #             ),
    #         )

    #         while True:

    #             try:

    #                 data, address = sock.recvfrom(
    #                     65535
    #                 )

    #                 print(
    #                     f"ONVIF response from {address[0]}"
    #                 )

    #                 responses.append(
    #                     (
    #                         data.decode(
    #                             "utf-8",
    #                             errors="ignore",
    #                         ),
    #                         address,
    #                     )
    #                 )

    #             except socket.timeout:

    #                 break

    #     except Exception as error:

    #         print(
    #             f"ONVIF discovery error: {error}"
    #         )

    #     finally:

    #         sock.close()

    #     return responses

    # def get_local_ip(self):

    #     sock = socket.socket(
    #         socket.AF_INET,
    #         socket.SOCK_DGRAM,
    #     )

    #     try:

    #         sock.connect(
    #             ("8.8.8.8", 80)
    #         )

    #         return sock.getsockname()[0]

    #     finally:

    #         sock.close()