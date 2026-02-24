"""
Real-time Log Anomaly Detector
Connects log parser + AI scorer to detect threats
"""

import os
import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from log_analysis.log_parser import LogMonitor
from log_analysis.log_scorer import LogScorer

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class LogAnomalyDetector:

    def __init__(self):
        self.monitor = LogMonitor()
        self.scorer  = LogScorer()
        self.alerts  = []

    def analyze_event(self, event):
        """Analyze one log event and return a full alert"""

        # Score and classify the event
        classification = self.scorer.classify_event(event)

        alert = {
            'timestamp':    event['timestamp'],
            'source':       event['source'],
            'event_type':   event['event_type'],
            'ip_address':   event.get('ip_address', 'N/A'),
            'username':     event.get('username', 'N/A'),
            'severity':     event.get('severity', 0),
            'prediction':   classification['prediction'],
            'anomaly_score': classification['anomaly_score'],
            'threat_level': classification['threat_level'],
            'is_anomaly':   classification['is_anomaly'],
            'details': {
                'is_root_attempt':  event.get('is_root_attempt', 0),
                'is_invalid_user':  event.get('is_invalid_user', 0),
                'is_suspicious':    event.get('is_suspicious', 0),
                'failed_logins':    event.get('failed_logins', 0),
                'status_code':      event.get('status_code', None),
            }
        }

        return alert

    def run_once(self):
        """Scan all logs once and return new alerts"""
        events     = self.monitor.collect_events()
        new_alerts = []

        for event in events:
            alert = self.analyze_event(event)

            if alert['is_anomaly']:
                new_alerts.append(alert)
                self.alerts.append(alert)

                # Color code by threat level
                icon = '🔴' if alert['threat_level'] == 'HIGH' else '🟡'
                print(f"{icon} [{alert['threat_level']}] "
                      f"{alert['event_type']} | "
                      f"IP: {alert['ip_address']} | "
                      f"Score: {alert['anomaly_score']} | "
                      f"Source: {alert['source']}")

        return new_alerts

    def run_continuous(self, interval=10):
        """Monitor logs continuously every N seconds"""
        print(f"\n🔍 Real-time monitoring started...")
        print(f"   Scanning every {interval} seconds")
        print(f"   Press CTRL+C to stop\n")

        while True:
            try:
                new_alerts = self.run_once()
                if not new_alerts:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ No new threats")

                self._save_alerts()
                time.sleep(interval)

            except KeyboardInterrupt:
                print("\n⛔ Monitoring stopped.")
                break

    def _save_alerts(self):
        """Save alerts to JSON for Flask API"""
        results_dir = os.path.join(BACKEND_DIR, 'results')
        os.makedirs(results_dir, exist_ok=True)

        recent = self.alerts[-500:]
        with open(os.path.join(results_dir, 'log_alerts.json'), 'w') as f:
            json.dump(recent, f, indent=2, default=str)

    def get_summary(self):
        """Return summary statistics"""
        total  = len(self.alerts)
        high   = sum(1 for a in self.alerts if a['threat_level'] == 'HIGH')
        medium = sum(1 for a in self.alerts if a['threat_level'] == 'MEDIUM')

        return {
            'total_alerts':   total,
            'high_threats':   high,
            'medium_threats': medium,
            'low_threats':    total - high - medium,
            'sources': {
                'auth_log': sum(1 for a in self.alerts if a['source'] == 'auth.log'),
                'apache':   sum(1 for a in self.alerts if a['source'] == 'apache2'),
                'syslog':   sum(1 for a in self.alerts if a['source'] == 'syslog'),
            }
        }


if __name__ == '__main__':
    detector = LogAnomalyDetector()

    print("\n🧪 Scanning your real system logs...\n")
    alerts = detector.run_once()
    detector._save_alerts()

    print(f"\n📊 Scan Complete:")
    summary = detector.get_summary()
    print(f"   Total threats:  {summary['total_alerts']}")
    print(f"   🔴 High:        {summary['high_threats']}")
    print(f"   🟡 Medium:      {summary['medium_threats']}")
    print(f"   Auth log:       {summary['sources']['auth_log']}")
    print(f"   Apache:         {summary['sources']['apache']}")
    print(f"   Syslog:         {summary['sources']['syslog']}")

    if alerts:
        print(f"\n🚨 Sample Alert:")
        print(json.dumps(alerts[0], indent=2, default=str))
    else:
        print("\n✅ No threats in current logs")
