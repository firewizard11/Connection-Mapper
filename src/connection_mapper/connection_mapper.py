import ipaddress
import logging
import platform
import subprocess
import sys
import threading
from dataclasses import dataclass

import networkx as nx
from scapy.sendrecv import AsyncSniffer
from scapy.layers.inet import IP
from scapy.arch import get_if_list
from scapy.interfaces import get_if_addr


@dataclass(frozen=True, slots=True)
class CaptureStatus:
    is_capturing: bool
    packet_cnt: int
    node_cnt: int


class ConnectionMapper:
    
    def __init__(self, is_verbose: bool = False):
        self.logger = logging.getLogger("conn-map")
        if is_verbose:
            self._setup_logger()
        else:
            self._setup_logger(logging.CRITICAL)

        self.lock = threading.Lock()
        self.packet_cnt = 0
        self.is_capturing = False
        self.gateways = self._get_gateways()
        if len(self.gateways) == 0:
            self.logger.warning("Couldn't find gateways")


        self.sniffer = AsyncSniffer(
            prn=lambda x: self._process_packet(x),
            filter="ip"
        )

        self.central_nodes = tuple(self._get_device_ips())
        self.logger.info(f"Found Device IPs: {self.central_nodes}")

        self.map = nx.DiGraph()

    def start_capture(self):
        with self.lock:
            if self.is_capturing:
                self.logger.warning("Packet Capture already running")
                return

        try:
            self.sniffer.start()
        except PermissionError:
            self.logger.critical("Can't capture due to low permissions")
            return
        except Exception as e:
            self.logger.critical(f"Unhandled Exception: {e}")
            return

        with self.lock:
            self.is_capturing = True

        self.logger.info("Started Packet Capture")

    def stop_capture(self):
        with self.lock:
            if not self.is_capturing:
                self.logger.warning("Packet Capture not running")
                return
        
        try:
            self.sniffer.stop()
        except PermissionError:
            self.logger.critical("Can't capture due to low permissions")
        except Exception as e:
            self.logger.critical(f"Unhandled Exception: {e}")
        finally:
            with self.lock:
                self.is_capturing = False
                count = self.packet_cnt

        self.logger.info(f"Stopped Packet Capture (Packet Count = {count})")

    def get_map(self) -> nx.DiGraph:
        with self.lock:
            map_copy = self.map.copy()
            
        self.logger.info("Created map copy")
        return map_copy

    def get_status(self) -> CaptureStatus:
        with self.lock:
            status = CaptureStatus(
                self.is_capturing, 
                self.packet_cnt, 
                self.map.number_of_nodes()
            )

        return status

    def _get_device_ips(self) -> list[str]:
        device_ips = []
        for interface in get_if_list():
            ip = get_if_addr(interface)
            if ip != "0.0.0.0":
                device_ips.append(ip)

        return device_ips

    def _process_packet(self, packet):
        """Extracts the IP src and dst from the packet and adds them to self.map"""
        if IP not in packet:
            return

        ip_data = packet[IP]
        src = ip_data.src
        dst = ip_data.dst

        with self.lock:
            self._add_node(src)
            self._add_node(dst)
            self.packet_cnt += 1
            self.map.add_edge(src, dst)

    def _add_node(self, ip: str):
        """Classifies node and adds it to self.map with color and label attributes

        WARNING: Not thread safe (in this class assumes calling function has lock)

        Classifications (label, color):
        - This Device (LOCAL, red)
        - Local LAN (ip, green)
        - Multicast (MULTICAST, black)
        - Gateway (GATEWAY, purple)
        - Public IP (ip, blue)
        
        Called By:
        - _process_packet
        """
        if self.map.has_node(ip):
            return

        ip_info = ipaddress.IPv4Address(ip)

        if ip in self.central_nodes:
            self.map.add_node(ip, label="LOCAL", color="red")
        elif ip in self.gateways:
            self.map.add_node(ip, label="GATEWAY", color="purple")
        elif ip_info.is_multicast:
            self.map.add_node(ip, label="MULTICAST", color="black")
        elif ip_info.is_private:
            self.map.add_node(ip, label=ip, color="green")
        else:
            self.map.add_node(ip, label=ip, color="blue")

    def _get_gateways(self) -> set[str]:
        """Gets all gateway entries from the routing table and returns a set of their labels
        
        Platform Support:
        - Windows: Uses 'route print -4' command to find gateways
        - Linux: Uses 'ip route list' command to find gateways

        Called By:
        - __init__
        """
        os = platform.system()
        gateways = set()

        if os == "Windows":
            result = subprocess.run(["route", "print", "-4"], capture_output=True, text=True)
            output_lines = result.stdout.split("\n")
            start = None
            end = None

            for i in range(len(output_lines)):
                if "Active Routes" in output_lines[i]:
                    start = i

                elif start is not None and "=" in output_lines[i]:
                    end = i

            active_routes_entries = output_lines[start+2:end]
            for entry in active_routes_entries:
                entry_fields = entry.split()
                if (len(entry_fields) > 2):
                    gateway = entry_fields[2]
                    gateways.add(gateway)

        elif os == "Linux":
            result = subprocess.run(["ip", "route", "list"], capture_output=True, text=True)
            lines = result.stdout.split("\n")
            for line in lines:
                if "via" not in line:
                    continue

                parts = line.split()
                if len(parts) > 2:
                    gateway = parts[2]
                    gateways.add(gateway)

        else:
            self.logger.warning(f"Gateway Discovery not implemented for {os}")

        return gateways

    def _setup_logger(self, level = logging.INFO):
        self.logger.setLevel(level)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

        self.logger.handlers.clear()
        self.logger.addHandler(handler)

        self.logger.propagate = False