"""
Real-time Log Parser - Improved Version
Reads system, web, and firewall logs
Filters noise and deduplicates events
"""

import re
import os
from datetime import datetime, timedelta
from collections import defaultdict


class AuthLogParser:
    PATTERNS = {
        'failed_login':   re.compile(r'Failed password for (\S+) from ([\d.]+)'),
        'accepted_login': re.compile(r'Accepted password for (\S+) from ([\d.]+)'),
        'invalid_user':   re.compile(r'Invalid user (\S+) from ([\d.]+)'),
        'sudo_attempt':   re.compile(r'sudo:.*USER=(\S+).*COMMAND=(.+)'),
    }

    def parse_line(self, line):
        event = {
            'timestamp':       datetime.now().isoformat(),
            'source':          'auth.log',
            'event_type':      'unknown',
            'ip_address':      None,
            'username':        None,
            'failed_logins':   0,
            'is_root_attempt': 0,
            'is_invalid_user': 0,
            'severity':        0,
        }

        if m := self.PATTERNS['failed_login'].search(line):
            event['event_type']      = 'failed_login'
            event['username']        = m.group(1)
            event['ip_address']      = m.group(2)
            event['failed_logins']   = 1
            event['severity']        = 2
            event['is_root_attempt'] = 1 if m.group(1) == 'root' else 0

        elif m := self.PATTERNS['invalid_user'].search(line):
            event['event_type']      = 'invalid_user'
            event['username']        = m.group(1)
            event['ip_address']      = m.group(2)
            event['is_invalid_user'] = 1
            event['severity']        = 3

        elif m := self.PATTERNS['accepted_login'].search(line):
            event['event_type'] = 'successful_login'
            event['username']   = m.group(1)
            event['ip_address'] = m.group(2)
            event['severity']   = 1

        elif m := self.PATTERNS['sudo_attempt'].search(line):
            # Only flag sudo as root — normal sudo is not suspicious
            user = m.group(1)
            if user == 'root':
                event['event_type']      = 'sudo_as_root'
                event['username']        = user
                event['severity']        = 3
                event['is_root_attempt'] = 1
            else:
                return None  # Normal sudo — ignore
        else:
            return None

        return event


class ApacheLogParser:
    LOG_PATTERN = re.compile(
        r'([\d.]+) - - \[(.*?)\] "(.*?)" (\d+) (\d+|-) "(.*?)" "(.*?)"'
    )

    SUSPICIOUS = [
    # Directory traversal
    r'\.\.\/',
    r'etc/passwd',
    r'etc/shadow',

    # SQL Injection patterns
    r'union.*select',           # UNION based SQLi
    r'select.*from',            # Basic SELECT
    r'insert.*into',            # INSERT injection
    r'drop.*table',             # DROP TABLE — very dangerous
    r'delete.*from',            # DELETE injection
    r'update.*set',             # UPDATE injection
    r"'.*or.*'.*'.*'",         # OR bypass: ' or '1'='1
    r'1=1',                     # Classic always-true
    r'--\s',                    # SQL comment to bypass
    r'/\*.*\*/',                # SQL block comment
    r'xp_cmdshell',             # MSSQL command execution
    r'information_schema',      # Database enumeration
    r'sleep\(\d+\)',            # Blind SQLi time delay
    r'benchmark\(',             # MySQL time-based blind
    r'waitfor.*delay',          # MSSQL time-based blind
    r'char\(\d+\)',             # Character encoding bypass
    r'0x[0-9a-fA-F]+',         # Hex encoding bypass

    # XSS (Cross-site scripting)
    r'<script',
    r'javascript:',
    r'onerror=',
    r'onload=',
    r'alert\(',

    # Command injection
    r'exec\(',
    r'cmd=',
    r'system\(',
    r'passthru\(',

    # File inclusion
    r'\.php\?',
    r'\.env',
    r'\.git',
    r'wp-admin',
    r'wp-config',
]

    def parse_line(self, line):
        m = self.LOG_PATTERN.match(line)
        if not m:
            return None

        ip, timestamp, request, status, size, referer, user_agent = m.groups()
        status_code  = int(status)
        is_suspicious = any(
            re.search(p, request, re.IGNORECASE) for p in self.SUSPICIOUS
        )

        # Only report suspicious or error requests
        if not is_suspicious and status_code < 400:
            return None

        severity = 0
        if is_suspicious:
            severity = 4
        elif status_code in [401, 403]:
            severity = 3
        elif status_code >= 400:
            severity = 2

        return {
            'timestamp':    datetime.now().isoformat(),
            'source':       'apache2',
            'event_type':   'web_attack' if is_suspicious else 'web_error',
            'ip_address':   ip,
            'status_code':  status_code,
            'is_suspicious': int(is_suspicious),
            'severity':     severity,
            'request':      request[:100],
        }


class SyslogParser:
    PATTERNS = {
        'memory_exhaustion': re.compile(r'Out of memory|OOM killer'),
        'segfault':          re.compile(r'segfault|SIGSEGV'),
        'kernel_error':      re.compile(r'kernel:.*error', re.I),
    }

    # Track seen events to avoid duplicates
    def __init__(self):
        self.seen = defaultdict(int)

    def parse_line(self, line):
        event = {
            'timestamp':  datetime.now().isoformat(),
            'source':     'syslog',
            'event_type': 'system_event',
            'severity':   0,
        }

        if self.PATTERNS['memory_exhaustion'].search(line):
            event['event_type'] = 'memory_exhaustion'
            event['severity']   = 4
        elif self.PATTERNS['segfault'].search(line):
            event['event_type'] = 'crash'
            event['severity']   = 3
        elif self.PATTERNS['kernel_error'].search(line):
            event['event_type'] = 'kernel_error'
            event['severity']   = 3
        else:
            return None  # Ignore service_failure noise

        # Deduplicate — only report each type max 3 times
        self.seen[event['event_type']] += 1
        if self.seen[event['event_type']] > 3:
            return None

        return event


class LogMonitor:
    def __init__(self):
        self.auth_parser   = AuthLogParser()
        self.apache_parser = ApacheLogParser()
        self.syslog_parser = SyslogParser()

        self.log_files = {
            '/var/log/auth.log':           self.auth_parser,
            '/var/log/apache2/access.log': self.apache_parser,
            '/var/log/syslog':             self.syslog_parser,
        }

        self.file_positions = {}

    def get_new_lines(self, filepath):
        if not os.path.exists(filepath):
            return []

        last_pos  = self.file_positions.get(filepath, 0)
        new_lines = []

        with open(filepath, 'r', errors='ignore') as f:
            # First run — only read last 200 lines to avoid old noise
            if last_pos == 0:
                all_lines = f.readlines()
                new_lines = all_lines[-200:]
                self.file_positions[filepath] = f.tell()
            else:
                f.seek(last_pos)
                new_lines = f.readlines()
                self.file_positions[filepath] = f.tell()

        return new_lines

    def collect_events(self):
        all_events = []

        for filepath, parser in self.log_files.items():
            try:
                new_lines = self.get_new_lines(filepath)
                for line in new_lines:
                    event = parser.parse_line(line.strip())
                    if event:
                        all_events.append(event)
            except PermissionError:
                print(f"[WARNING] Cannot read {filepath} — run with sudo")
            except Exception as e:
                print(f"[ERROR] {filepath}: {e}")

        return all_events

    def event_to_features(self, event):
        return [
            event.get('severity',         0),
            event.get('failed_logins',    0),
            event.get('is_root_attempt',  0),
            event.get('is_invalid_user',  0),
            event.get('is_suspicious',    0),
            event.get('status_code', 200) / 500,
            1 if event.get('source') == 'auth.log'  else 0,
            1 if event.get('source') == 'apache2'   else 0,
            1 if event.get('source') == 'syslog'    else 0,
        ]


if __name__ == '__main__':
    print("Testing improved log parser...\n")
    auth = AuthLogParser()
    tests = [
        "Feb 21 14:32:11 server sshd[1]: Failed password for root from 192.168.1.100 port 22",
        "Feb 21 14:32:15 server sshd[1]: Invalid user admin from 10.0.0.5 port 4521",
        "Feb 21 14:33:01 server sshd[1]: Accepted password for chelsy from 192.168.1.1",
    ]
    for line in tests:
        r = auth.parse_line(line)
        if r:
            print(f"✅ {r['event_type']} | IP: {r['ip_address']} | Severity: {r['severity']}")
    print("\n✅ Parser ready!")
