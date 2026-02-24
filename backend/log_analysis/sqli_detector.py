"""
SQL Injection Detector
Analyses web requests specifically for SQLi attacks
Can analyse both Apache logs and direct URL inputs
"""

import re
import json
from datetime import datetime


class SQLiDetector:
    """
    Dedicated SQL Injection detection engine
    Detects multiple categories of SQLi attacks
    """

    # SQLi attack categories with their patterns
    SQLI_PATTERNS = {

        'union_based': {
            'patterns': [
                re.compile(r'union\s+select', re.I),
                re.compile(r'union\s+all\s+select', re.I),
            ],
            'severity': 5,
            'description': 'UNION-based SQL Injection — attacker extracting data'
        },

        'boolean_based': {
            'patterns': [
                re.compile(r"'\s*or\s*'?\d+'?\s*=\s*'?\d+", re.I),
                re.compile(r"'\s*or\s*1\s*=\s*1", re.I),
                re.compile(r'--\s*$', re.I),
                re.compile(r"admin'--", re.I),
                re.compile(r"'\s*#", re.I),
            ],
            'severity': 5,
            'description': 'Boolean-based SQLi — login bypass attempt'
        },

        'time_based': {
            'patterns': [
                re.compile(r'sleep\s*\(\s*\d+\s*\)', re.I),
                re.compile(r'benchmark\s*\(', re.I),
                re.compile(r'waitfor\s+delay', re.I),
                re.compile(r'pg_sleep', re.I),
            ],
            'severity': 4,
            'description': 'Time-based blind SQLi — stealthy data extraction'
        },

        'error_based': {
            'patterns': [
                re.compile(r'extractvalue\s*\(', re.I),
                re.compile(r'updatexml\s*\(', re.I),
                re.compile(r'floor\s*\(\s*rand', re.I),
            ],
            'severity': 4,
            'description': 'Error-based SQLi — extracting data via error messages'
        },

        'schema_enumeration': {
            'patterns': [
                re.compile(r'information_schema', re.I),
                re.compile(r'sys\.tables', re.I),
                re.compile(r'sysobjects', re.I),
                re.compile(r'pg_tables', re.I),
            ],
            'severity': 4,
            'description': 'Database enumeration — mapping database structure'
        },

        'dangerous_commands': {
            'patterns': [
                re.compile(r'drop\s+table', re.I),
                re.compile(r'drop\s+database', re.I),
                re.compile(r'truncate\s+table', re.I),
                re.compile(r'xp_cmdshell', re.I),
                re.compile(r'exec\s*\(', re.I),
            ],
            'severity': 5,
            'description': 'Dangerous SQL commands — data destruction or RCE'
        },

        'encoding_bypass': {
            'patterns': [
                re.compile(r'char\s*\(\d+', re.I),
                re.compile(r'0x[0-9a-f]{4,}', re.I),
                re.compile(r'%27', re.I),     # URL encoded '
                re.compile(r'%20or%20', re.I), # URL encoded OR
            ],
            'severity': 3,
            'description': 'Encoded SQLi — attempting to bypass filters'
        },
    }

    def analyze_request(self, url_or_request):
        """
        Analyze a URL or HTTP request for SQLi patterns
        Returns detection result with details
        """
        detections = []

        for attack_type, config in self.SQLI_PATTERNS.items():
            for pattern in config['patterns']:
                if pattern.search(url_or_request):
                    detections.append({
                        'attack_type':   attack_type,
                        'severity':      config['severity'],
                        'description':   config['description'],
                    })
                    break  # One match per category is enough

        if not detections:
            return {
                'is_sqli':     False,
                'severity':    0,
                'attack_types': [],
                'description': 'No SQLi detected',
                'timestamp':   datetime.now().isoformat(),
            }

        # Get highest severity
        max_severity = max(d['severity'] for d in detections)
        attack_types = [d['attack_type'] for d in detections]
        descriptions = [d['description'] for d in detections]

        return {
            'is_sqli':      True,
            'severity':     max_severity,
            'attack_types': attack_types,
            'description':  ' | '.join(descriptions),
            'timestamp':    datetime.now().isoformat(),
        }

    def analyze_log_line(self, apache_log_line):
        """
        Parse and analyze one Apache log line for SQLi
        """
        # Extract the request part from Apache log
        import re
        match = re.search(r'"(GET|POST|PUT|DELETE)\s+(\S+)', apache_log_line)
        if not match:
            return None

        request = match.group(2)
        result  = self.analyze_request(request)

        if result['is_sqli']:
            # Extract IP
            ip_match = re.match(r'([\d.]+)', apache_log_line)
            ip = ip_match.group(1) if ip_match else 'unknown'

            result['ip_address'] = ip
            result['request']    = request[:200]
            result['source']     = 'apache2'

        return result if result['is_sqli'] else None

    def scan_apache_log(self, log_path='/var/log/apache2/access.log', last_n_lines=500):
        """
        Scan Apache access log for SQLi attacks
        """
        alerts = []

        try:
            with open(log_path, 'r', errors='ignore') as f:
                lines = f.readlines()

            # Only check last N lines
            recent_lines = lines[-last_n_lines:]

            for line in recent_lines:
                result = self.analyze_log_line(line.strip())
                if result:
                    alerts.append(result)

        except PermissionError:
            print(f"[WARNING] Cannot read {log_path} — run with sudo")
        except FileNotFoundError:
            print(f"[WARNING] Log file not found: {log_path}")

        return alerts


# ── Test / Demo ──────────────────────────────────────────────────────
if __name__ == '__main__':
    detector = SQLiDetector()

    print("="*60)
    print("SQL INJECTION DETECTOR TEST")
    print("="*60)

    test_requests = [
        # Normal requests
        ("Normal login",          "/login?user=chelsy&pass=1234"),
        ("Normal search",         "/search?q=network+security"),

        # SQLi attacks
        ("Boolean bypass",        "/login?user=admin'--&pass=anything"),
        ("OR bypass",             "/login?user=' OR '1'='1"),
        ("UNION extraction",      "/search?q=1 UNION SELECT username,password FROM users"),
        ("Time-based blind",      "/search?q=1'; SLEEP(5)--"),
        ("Schema enumeration",    "/search?q=1 UNION SELECT table_name FROM information_schema.tables"),
        ("Drop table",            "/admin?cmd=DROP TABLE students"),
        ("Encoded bypass",        "/search?q=%27%20OR%201%3D1"),
    ]

    for name, request in test_requests:
        result = detector.analyze_request(request)
        if result['is_sqli']:
            print(f"\n🚨 ATTACK DETECTED: {name}")
            print(f"   Types:    {', '.join(result['attack_types'])}")
            print(f"   Severity: {result['severity']}/5")
            print(f"   Details:  {result['description'][:80]}")
        else:
            print(f"\n✅ Clean:  {name}")

    print("\n" + "="*60)
    print("Scanning real Apache logs...")
    alerts = detector.scan_apache_log()
    print(f"Found {len(alerts)} SQLi attempts in your Apache logs")
    if alerts:
        for a in alerts[:3]:
            print(f"  🚨 {a['attack_types']} from {a['ip_address']}")
