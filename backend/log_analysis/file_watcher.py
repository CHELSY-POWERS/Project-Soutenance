"""
Real-Time File Watcher — Iteration 3
Watches log files every 0.5s and emits WebSocket alerts instantly.
"""
import os, sys, json, time, threading
from datetime import datetime

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

class LogFileWatcher:
    WATCHED_FILES = [
        '/var/log/auth.log',
        '/var/log/apache2/access.log',
        '/var/log/syslog',
    ]
    SQLI_PATTERNS = [
        "union+select", "union select", "'+or+'", "1=1",
        "sleep(", "benchmark(", "information_schema",
        "' or 1", "admin'--", "%27", "0x",
    ]

    def __init__(self, socketio=None, emit_fn=None):
        self.socketio  = socketio
        self.emit_fn   = emit_fn
        self.positions = {}
        self.running   = False
        self.thread    = None
        try:
            from log_analysis.log_parser import AuthLogParser, ApacheLogParser, SyslogParser
            from log_analysis.log_scorer import LogScorer
            self.auth_parser   = AuthLogParser()
            self.apache_parser = ApacheLogParser()
            self.syslog_parser = SyslogParser()
            self.scorer        = LogScorer()
            print("[WATCHER] Parsers loaded successfully")
        except Exception as e:
            print(f"[WATCHER] Could not load parsers: {e}")
            self.auth_parser   = None
            self.apache_parser = None
            self.syslog_parser = None
            self.scorer        = None
        for path in self.WATCHED_FILES:
            if os.path.exists(path):
                try:
                    self.positions[path] = os.path.getsize(path)
                    print(f"[WATCHER] Watching: {path}")
                except PermissionError:
                    print(f"[WATCHER] No permission: {path} (needs sudo)")

    def _read_new_lines(self, path):
        if path not in self.positions:
            return []
        try:
            current_size = os.path.getsize(path)
            if current_size <= self.positions[path]:
                return []
            with open(path, 'r', errors='ignore') as f:
                f.seek(self.positions[path])
                new_lines = f.readlines()
                self.positions[path] = f.tell()
            return [l.strip() for l in new_lines if l.strip()]
        except (PermissionError, OSError):
            return []

    def _check_sqli(self, line):
        line_lower = line.lower()
        for pattern in self.SQLI_PATTERNS:
            if pattern in line_lower:
                return {
                    'timestamp':    datetime.now().isoformat(),
                    'source':       'apache2',
                    'event_type':   'sql_injection',
                    'attack_type':  'SQL_INJECTION',
                    'pattern':      pattern,
                    'raw_message':  line[:300],
                    'threat_level': 'HIGH',
                    'anomaly_score': 0.95,
                    'live':         True,
                }
        return None

    def _analyse_line(self, line, source):
        if not self.scorer:
            return None
        try:
            # Choose correct parser based on source
            if source == 'auth.log':
                parser = self.auth_parser
            elif source == 'apache':
                parser = self.apache_parser
            else:
                parser = self.syslog_parser

            if not parser:
                return None

            event = parser.parse_line(line)
            if not event:
                return None

            classification = self.scorer.classify_event(event)
            if not classification.get('is_anomaly'):
                return None

            return {
                'timestamp':     datetime.now().isoformat(),
                'source':        source,
                'event_type':    event.get('event_type', 'unknown'),
                'ip_address':    event.get('ip_address', 'N/A'),
                'username':      event.get('username', 'N/A'),
                'threat_level':  classification['threat_level'],
                'anomaly_score': classification['anomaly_score'],
                'raw_message':   line[:200],
                'live':          True,
            }
        except Exception as e:
            print(f"[WATCHER] Analyse error: {e}")
            return None

    def _save_alert(self, alert):
        try:
            path = os.path.join(BACKEND_DIR, 'results', 'log_alerts.json')
            alerts = []
            if os.path.exists(path):
                with open(path) as f:
                    alerts = json.load(f)
            alerts.insert(0, alert)
            with open(path, 'w') as f:
                json.dump(alerts[:500], f, default=str)
        except Exception as e:
            print(f"[WATCHER] Save error: {e}")

    def _emit(self, event_name, data):
        if self.socketio:
            try:
                self.socketio.emit(event_name, data)
            except Exception as e:
                print(f"[WATCHER] Emit error: {e}")
        if self.emit_fn:
            self.emit_fn(event_name, data)

    def _watch_loop(self):
        print("[WATCHER] Real-time watching started — checking every 0.5s")
        while self.running:
            try:
                for path in self.WATCHED_FILES:
                    if path not in self.positions:
                        continue
                    new_lines = self._read_new_lines(path)
                    if not new_lines:
                        continue
                    source = 'auth.log' if 'auth' in path else \
                             'apache'   if 'apache' in path else 'syslog'
                    print(f"[WATCHER] {len(new_lines)} new lines in {source}")
                    for line in new_lines:
                        if 'apache' in path:
                            sqli = self._check_sqli(line)
                            if sqli:
                                print(f"[WATCHER] LIVE SQLi detected!")
                                self._save_alert(sqli)
                                self._emit('new_live_alert', {'type': 'sqli', 'alert': sqli, 'message': 'SQL Injection detected!'})
                        alert = self._analyse_line(line, source)
                        if alert:
                            print(f"[WATCHER] LIVE threat: {alert['event_type']} — {alert['threat_level']}")
                            self._save_alert(alert)
                            self._emit('new_live_alert', {'type': 'log', 'alert': alert, 'message': f"New {alert['threat_level']} threat in {source}"})
            except Exception as e:
                print(f"[WATCHER] Loop error: {e}")
            time.sleep(0.5)

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread  = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
