import socket
import ipaddress
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

class NetworkScanner:
    def get_local_ip(self):
        """
        get the ip address of the device your using on the local network.
        """

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        )
        try:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]

        finally:
            sock.close()


    def get_network(self):
        """
        get the network CIDR from the linux routing table.
        """
        try:
            result = subprocess.run(
                [
                    "ip",
                    "-4",
                    "route",
                ],
                capture_output  = True,
                text = True,
                check = True,
            )

            for line in result.stdout.splitlines():
                parts = line.split()
                if not parts:
                    continue

                destination = parts[0]

                if destination == "default":
                    continue
                if "/" not in destination:
                    continue

                try:
                    network = ipaddress.ip_network(
                        destination,
                        strict = False,
                    )
                    if network.is_private:
                        return network

                except ValueError:
                    continue

        except Exception as error:
            print(f"Could not determin network: {error}")


        """
        fallback
        """
        local_ip = self.get_local_ip()
        parts = local_ip.split(".")

        network = (
            f"{parts[0]}."
            f"{parts[1]}."
            f"{parts[2]}.0/24"
        )
        return ipaddress.ip_network(
            network,
            strict = False,
        )

    def check_port(self, ip_address, port):
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        sock.settimeout(0.3)

        try:
            result = sock.connect_ex(
                (ip_address, port)
            ) 
            return result == 0

        except Exception:
            return False

        finally:
            sock.close()



    def scan_devices(self, ip_address):
        """
        scan the local network for devices that responds to ping-like TCP connections.
        """

        """
        common ip or network-service ports
        """
        ports = [
            80, #HTTP
            443, #HTTPS
            554, #RTSP
            8000, #some camera systems
            8080, #HTTP alternate
            8899, #some camera systems
        ]
        open_ports = []
        for port in ports:
            if self.check_port(
                ipaddress,
                port,
            ):
                open_ports.append(port)

        if open_ports:
            return {
                "ip": ip_address,
                "ports": open_ports,
            }
        return None

    def scan(self):
        network = self.get_network()
        print(
            f"scanning network: {network}"
        )

        devices = []

        addresses = [
            str(ip)
            for ip in network.hosts()
        ]
        print(f"checking {len(addresses)} address...")

        with ThreadPoolExecutor(
            max_workers = 100
        ) as executor:
            futures = [
                executor.submit(
                    self.scan_devices,
                    ip,
                )
                for ip in addresses
            ]
            for future in as_completed(futures):
                result = future.result()

                if result:
                    devices.append(result)

                    print(
                        f"Found device: {result['ip']} ports  {result['ports']}"
                    )
            
        return devices