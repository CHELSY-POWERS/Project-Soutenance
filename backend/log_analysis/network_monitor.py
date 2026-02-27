"""
Network Traffic Monitor
Captures real network packets from WiFi and analyses them with AI
Detects: port scans, brute force, DoS, suspicious connections
"""

import sys
import os
import json
import time
from datetime import datetime
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("[ERROR] Scapy not installed. Run: pip install scapy")


class NetworkMonitor:

    def __init__(self):
        self.ip_connections  = defaultdict(list)
        self.ip_ports        = defaultdict(set)
        self.ip_bytes        = defaultdict(int)
        self.alerts          = []
        self.packet_count    = 0
        self.start_time      = time.time()

        self.PORT_SCAN_THRESHOLD   = 10
        self.BRUTE_FORCE_THRESHOLD = 5
        self.DOS_THRESHOLD         = 100

        self.SUSPICIOUS_PORTS = {4444, 1337, 31337, 6667, 6668, 6669, 9001, 9030}
        self.SENSITIVE_PORTS  = {
            22: 'SSH', 23: 'Telnet', 3306: 'MySQL',
            5432: 'PostgreSQL', 6379: 'Redis',
            27017: 'MongoDB', 445: 'SMB', 3389: 'RDP'
        }

    def analyse_packet(self, packet):
        self.packet_count += 1

        if not packet.haslayer(IP):
            return

        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        now    = time.time()

        self.ip_bytes[src_ip] += len(packet)

        if packet.haslayer(TCP):
            tcp      = packet[TCP]
            dst_port = tcp.dport
            flags    = tcp.flags

            self.ip_ports[src_ip].add(dst_port)
            self.ip_connections[src_ip].append(now)
            self.ip_connections[src_ip] = [
                t for t in self.ip_connections[src_ip] if now - t < 10
            ]

            # Port scan
            if len(self.ip_ports[src_ip]) >= self.PORT_SCAN_THRESHOLD:
                self._alert(src_ip, dst_ip, 'port_scan', 4,
                    f'Port scan — {len(self.ip_ports[src_ip])} ports probed')
                self.ip_ports[src_ip].clear()

            # Brute force
            if dst_port in self.SENSITIVE_PORTS:
                recent = len(self.ip_connections[src_ip])
                if recent >= self.BRUTE_FORCE_THRESHOLD:
                    service = self.SENSITIVE_PORTS[dst_port]
                    self._alert(src_ip, dst_ip, 'brute_force', 5,
                        f'Brute force on {service} — {recent} attempts in 10s',
                        {'service': service, 'port': dst_port})
                    self.ip_connections[src_ip].clear()

            # Suspicious port
            if dst_port in self.SUSPICIOUS_PORTS:
                self._alert(src_ip, dst_ip, 'suspicious_port', 4,
                    f'Connection to suspicious port {dst_port} — possible backdoor',
                    {'port': dst_port})

            # SYN flood
            if str(flags) == 'S':
                recent = len(self.ip_connections[src_ip])
                if recent >= self.DOS_THRESHOLD:
                    self._alert(src_ip, dst_ip, 'syn_flood', 5,
                        f'SYN flood DoS — {recent} SYN packets in 10s')
                    self.ip_connections[src_ip].clear()

        elif packet.haslayer(UDP):
            self.ip_connections[src_ip].append(now)
            if len(self.ip_connections[src_ip]) >= self.DOS_THRESHOLD:
                self._alert(src_ip, dst_ip, 'udp_flood', 4,
                    f'UDP flood — {len(self.ip_connections[src_ip])} packets in 10s')
                self.ip_connections[src_ip].clear()

        elif packet.haslayer(ICMP):
            self.ip_connections[src_ip].append(now)
            if len(self.ip_connections[src_ip]) >= 20:
                self._alert(src_ip, dst_ip, 'icmp_flood', 3,
                    f'ICMP flood — {len(self.ip_connections[src_ip])} pings in 10s')
                self.ip_connections[src_ip].clear()

        # Data exfiltration
        if self.ip_bytes[src_ip] >= 10_000_000:
            self._alert(src_ip, dst_ip, 'data_exfiltration', 4,
                f'Possible data exfiltration — {self.ip_bytes[src_ip]//1_000_000}MB transferred')
            self.ip_bytes[src_ip] = 0

    def _alert(self, src_ip, dst_ip, attack_type, severity, description, details={}):
        now = time.time()
        # Avoid duplicate alerts within 30 seconds
        for a in self.alerts[-20:]:
            if (a.get('src_ip') == src_ip and
                a.get('attack_type') == attack_type and
                now - a.get('_ts', 0) < 30):
                return

        alert = {
            'timestamp':   datetime.now().isoformat(),
            '_ts':         now,
            'src_ip':      src_ip,
            'dst_ip':      dst_ip,
            'attack_type': attack_type,
            'severity':    severity,
            'description': description,
            'details':     details,
            'threat_level': 'HIGH' if severity >= 4 else 'MEDIUM',
            'source':      'network',
        }

        self.alerts.append(alert)
        if len(self.alerts) > 200:
            self.alerts = self.alerts[-200:]

        self._save()

        icon = "🔴" if severity >= 4 else "🟡"
        print(f"{icon} [{attack_type.upper()}] {src_ip} → {dst_ip} | {description}")

    def _save(self):
        path = os.path.join(BASE_DIR, 'results', 'network_alerts.json')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        clean = [{k: v for k, v in a.items() if k != '_ts'} for a in self.alerts]
        with open(path, 'w') as f:
            json.dump(clean, f, indent=2)

    def get_stats(self):
        elapsed = time.time() - self.start_time
        return {
            'packets_captured':  self.packet_count,
            'packets_per_second': round(self.packet_count / max(elapsed, 1), 1),
            'unique_ips':        len(self.ip_connections),
            'total_alerts':      len(self.alerts),
            'high_alerts':       sum(1 for a in self.alerts if a.get('threat_level') == 'HIGH'),
            'monitoring_seconds': round(elapsed),
        }

    def start(self, interface=None, duration=None):
        if not SCAPY_AVAILABLE:
            print("[ERROR] Scapy not available")
            return

        print("=" * 60)
        print("🌐 NETWORK TRAFFIC MONITOR — AI-IDS")
        print("=" * 60)
        print(f"Interface : {interface or 'auto-detect'}")
        print(f"Detecting : Port Scans, Brute Force, DoS, Backdoors, Exfiltration")
        print("Press CTRL+C to stop monitoring")
        print("=" * 60)

        try:
            sniff(iface=interface, prn=self.analyse_packet,
                  store=False, timeout=duration)
        except KeyboardInterrupt:
            print("\n[STOPPED] Monitoring stopped")
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            stats = self.get_stats()
            print(f"\n📊 {stats['packets_captured']} packets captured | {stats['total_alerts']} alerts generated")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', '-i', default=None)
    parser.add_argument('--duration',  '-d', default=None, type=int)
    args = parser.parse_args()

    monitor = NetworkMonitor()
    monitor.start(interface=args.interface, duration=args.duration)
