"""
Database layer for AI-IDS — SQLite
Replaces JSON files with persistent storage.
Tables: alerts, network_alerts, detection_results
"""
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'results', 'ai_ids.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create all tables if they don't exist."""
    conn = get_conn()
    c = conn.cursor()

    c.executescript('''
        CREATE TABLE IF NOT EXISTS log_alerts (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp     TEXT DEFAULT (datetime('now')),
            source        TEXT,
            event_type    TEXT,
            ip_address    TEXT,
            username      TEXT,
            threat_level  TEXT,
            anomaly_score REAL,
            risk_score    REAL,
            mitre_id      TEXT,
            mitre_tactic  TEXT,
            mitre_name    TEXT,
            threat_category TEXT,
            raw_message   TEXT,
            live          INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS network_alerts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT DEFAULT (datetime('now')),
            src_ip      TEXT,
            dst_ip      TEXT,
            attack_type TEXT,
            description TEXT,
            severity    INTEGER,
            interface   TEXT
        );

        CREATE TABLE IF NOT EXISTS detection_results (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id      INTEGER,
            timestamp     TEXT,
            prediction    TEXT,
            anomaly_score REAL,
            confidence    REAL
        );

        CREATE INDEX IF NOT EXISTS idx_log_timestamp    ON log_alerts(timestamp);
        CREATE INDEX IF NOT EXISTS idx_log_threat       ON log_alerts(threat_level);
        CREATE INDEX IF NOT EXISTS idx_net_timestamp    ON network_alerts(timestamp);
        CREATE INDEX IF NOT EXISTS idx_det_prediction   ON detection_results(prediction);
    ''')

    conn.commit()
    conn.close()
    print(f"[DB] ✅ Database initialized at {DB_PATH}")

def save_log_alert(alert):
    """Save a single log alert to database."""
    try:
        conn = get_conn()
        mitre = alert.get('mitre', {})
        conn.execute('''
            INSERT INTO log_alerts
            (timestamp, source, event_type, ip_address, username,
             threat_level, anomaly_score, risk_score,
             mitre_id, mitre_tactic, mitre_name, threat_category,
             raw_message, live)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            alert.get('timestamp', datetime.now().isoformat()),
            alert.get('source'), alert.get('event_type'),
            alert.get('ip_address'), alert.get('username'),
            alert.get('threat_level'), alert.get('anomaly_score'),
            alert.get('risk_score'),
            mitre.get('id'), mitre.get('tactic'), mitre.get('name'),
            alert.get('threat_category'),
            alert.get('raw_message', '')[:500],
            1 if alert.get('live') else 0
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Save log alert error: {e}")

def save_network_alert(alert):
    """Save a network alert to database."""
    try:
        conn = get_conn()
        conn.execute('''
            INSERT INTO network_alerts
            (timestamp, src_ip, dst_ip, attack_type, description, severity)
            VALUES (?,?,?,?,?,?)
        ''', (
            alert.get('timestamp', datetime.now().isoformat()),
            alert.get('src_ip'), alert.get('dst_ip'),
            alert.get('attack_type'), alert.get('description'),
            alert.get('severity', 1)
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Save network alert error: {e}")

def get_log_alerts(limit=200, threat_level=None):
    """Get log alerts from database."""
    conn = get_conn()
    if threat_level:
        rows = conn.execute(
            'SELECT * FROM log_alerts WHERE threat_level=? ORDER BY timestamp DESC LIMIT ?',
            (threat_level, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            'SELECT * FROM log_alerts ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_network_alerts(limit=100):
    """Get network alerts from database."""
    conn = get_conn()
    rows = conn.execute(
        'SELECT * FROM network_alerts ORDER BY timestamp DESC LIMIT ?',
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def clear_alerts():
    """Clear all alerts from database."""
    conn = get_conn()
    conn.execute('DELETE FROM log_alerts')
    conn.execute('DELETE FROM network_alerts')
    conn.commit()
    conn.close()

def get_stats():
    """Get summary statistics."""
    conn = get_conn()
    stats = {
        'total_log_alerts':     conn.execute('SELECT COUNT(*) FROM log_alerts').fetchone()[0],
        'high_log_alerts':      conn.execute("SELECT COUNT(*) FROM log_alerts WHERE threat_level='HIGH'").fetchone()[0],
        'total_network_alerts': conn.execute('SELECT COUNT(*) FROM network_alerts').fetchone()[0],
        'live_alerts':          conn.execute('SELECT COUNT(*) FROM log_alerts WHERE live=1').fetchone()[0],
        'unique_ips':           conn.execute('SELECT COUNT(DISTINCT ip_address) FROM log_alerts').fetchone()[0],
    }
    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
    print("[DB] Tables created successfully")
