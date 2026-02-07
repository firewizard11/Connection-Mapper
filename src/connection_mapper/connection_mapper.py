import matplotlib.pyplot as plt
import networkx as nx
import threading

from scapy.all import AsyncSniffer, Raw, IP, get_if_list, get_if_addr


class ConnectionMapper:
    
    def __init__(self):
        self.mutex = threading.Lock()
        self.cap_count = 0
        self.sniffing = False

        self.sniffer = AsyncSniffer(
            prn=lambda x: self.process_packet(x),
            filter="ip"
        )

        self.central_nodes = tuple(self.get_device_ips())
        print(f"[INFO] Found Device IPs: {self.central_nodes}")

        self.map = nx.DiGraph()

    def start_capture(self):
        self.sniffer.start()
        self.sniffing = True

        if self.sniffer.exception is not None:
            self.stop_capture()
            return

        print("[INFO] Capturing Packets")

    def stop_capture(self):
        if not self.sniffing:
            print("[INFO] Not Capturing Packets")
            return
        
        try:
            result = self.sniffer.stop()
            if result is not None:
                print(f"[INFO] Captured {len(result)} Packets")
            print("[INFO] Stopped packet capture")
        except PermissionError:
            print("[FAIL] Please run program as admin")
        except Exception as e:
            print("[FAIL] " + e)

        self.sniffing = False

    def process_packet(self, raw_packet: Raw):
        ip_data = raw_packet[IP]
        src = ip_data.src
        dst = ip_data.dst

        if src in self.central_nodes:
            src = self.central_nodes
        
        elif dst in self.central_nodes:
            dst = self.central_nodes

        with self.mutex:
            self.cap_count += 1
            self.map.add_edge(src, dst)

    def draw_map(self):
        print("[INFO] Drawing Map")
        with self.mutex:
            if self.map.number_of_nodes() < 20:
                with_labels = True
            else:
                with_labels = False

            nx.draw(self.map, with_labels=with_labels)
            plt.show()

    def get_device_ips(self) -> list[str]:
        device_ips = []
        for interface in get_if_list():
            ip = get_if_addr(interface)
            if ip != "0.0.0.0":
                device_ips.append(ip)

        return device_ips
    
    def get_status(self) -> dict:
        status = {}
        with self.mutex:
            status["capturing"] = self.sniffing
            status["cap_count"] = self.cap_count
            status["node_count"] = self.map.number_of_nodes()
        return status
