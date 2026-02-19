import ipaddress
import threading
from dataclasses import dataclass

import networkx as nx
from scapy.interfaces import get_working_ifaces, NetworkInterface
from scapy.layers.inet import IP
from scapy.sendrecv import AsyncSniffer


@dataclass(slots=True)
class CaptureStatus:
    is_capturing: bool
    packets_processed: int
    nodes_found: int


class ConnectionMapper:
    """ This class uses the network traffic generated from your device to create a directed graph

    Public API:
    - start_capture(): Starts the packet capture
    - stop_capture(): Stops the packet capture
    - get_status() -> CaptureStatus: Returns info on the capture (is_capturing, packets_processed, nodes_found)
    - get_map() -> nx.DiGraph: Returns a snapshot of the network graph at the point of calling
    """

    def __init__(self):
        # Device Attr
        self._public_interfaces = self._find_public_interfaces()

        if len(self._public_interfaces) == 0:
            raise ValueError("Couldn't find public interfaces")

        self._public_ifnames = []
        self._public_ipv4 = []
        
        for _if in self._public_interfaces:
            self._public_ifnames.append(_if.name)
            self._public_ipv4.append(_if.ip)
        
        # Capture Attr
        self._capture_status = CaptureStatus(False, 0, 0) # Must Lock
        self.lock = threading.Lock()
        self._capturer = AsyncSniffer(
            prn=lambda x: self._process_packet(x),
            iface=self._public_interfaces
        )

        # Graph Attr
        self._map = nx.DiGraph() # Must Lock
        self._map.add_node(tuple(self._public_ipv4), label="LOCAL", color="red")
        self._capture_status.nodes_found += 1

    def start_capture(self):
        try:
            self._capturer.start()
        except Exception as e:
            raise e
        
        self._capture_status.is_capturing = True

    def stop_capture(self):
        if not self._capture_status.is_capturing:
            return

        self._capturer.stop()
        with self.lock:
            if self._capture_status.is_capturing:
                self._capture_status.is_capturing = False

    def get_status(self) -> CaptureStatus:
        with self.lock:
            return self._capture_status

    def get_map(self) -> nx.DiGraph:
        with self.lock:
            return self._map.copy()

    def _find_public_interfaces(self) -> list[NetworkInterface]:
        """ Tries to find the public nic like wlan0 or Wi-Fi (excluding virtual) """
        interfaces = get_working_ifaces()
        public_ifs = []

        for _if in interfaces:
            if _if.ip is None or _if.ip == "":
                continue

            ip = ipaddress.IPv4Address(_if.ip)
            
            if ip.is_link_local:
                continue

            if ip.is_loopback:
                continue

            if not ip.is_private:
                continue

            ifname = _if.name.lower()
            if "vmware" in ifname or "virtual" in ifname or "hyper-v" in ifname:
                continue

            public_ifs.append(_if)

        return public_ifs
    
    def _process_packet(self, packet):
        if IP not in packet:
            return
        
        ip_data = packet[IP]
        src = ip_data.src
        dst = ip_data.dst

        if src not in self._public_ipv4 and dst not in self._public_ipv4:
            return

        with self.lock:
            self._add_conn(src, dst)
            self._capture_status.packets_processed += 1

    def _add_conn(self, src: str, dst: str):
        if src in self._public_ipv4:
            src = tuple(self._public_ipv4)
        else:
            self._add_node(src)

        if dst in self._public_ipv4:
            dst = tuple(self._public_ipv4)
        else:
            self._add_node(dst)

        self._map.add_edge(src, dst)

    def _add_node(self, ip: str):
        if ip in self._map.nodes:
            return
        
        ip_info = ipaddress.IPv4Address(ip)

        if ip_info.is_private:
            color = "orange"
        elif ip_info.is_global:
            color = "blue"
        else:
            color = "green"

        self._map.add_node(ip, label=ip, color=color)
        self._capture_status.nodes_found += 1
