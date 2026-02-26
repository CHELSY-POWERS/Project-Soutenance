import { C, KPI, Badge, SeverityDots } from "../UI";

export default function LogsTab({ logAlerts, sqliAlerts, scanning, onScan }) {
  return (
    <>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 24 }}>
        <KPI title="Total Alerts"   value={logAlerts?.total ?? 0}  sub="From all log sources"   accent={C.accent} />
        <KPI title="High Threats"   value={logAlerts?.high ?? 0}   sub="Immediate attention"    accent={C.red}    />
        <KPI title="Medium Threats" value={logAlerts?.medium ?? 0} sub="Needs investigation"    accent={C.yellow} />
        <KPI title="SQLi Attacks"   value={sqliAlerts?.total ?? 0} sub="SQL injection attempts" accent={C.purple} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 24 }}>
        {[
          { label: "🔐 auth.log", value: logAlerts?.sources?.auth_log ?? 0, desc: "SSH & login events",  color: C.green  },
          { label: "🌐 Apache2",  value: logAlerts?.sources?.apache ?? 0,   desc: "Web server requests", color: C.accent },
          { label: "⚙️ Syslog",   value: logAlerts?.sources?.syslog ?? 0,   desc: "System events",       color: C.yellow },
        ].map(({ label, value, desc, color }) => (
          <div key={label} style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20, display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ fontSize: 28, fontWeight: 800, fontFamily: "monospace", color }}>{value}</div>
            <div>
              <p style={{ margin: 0, color: C.text, fontSize: 13, fontWeight: 700 }}>{label}</p>
              <p style={{ margin: 0, color: C.muted, fontSize: 11 }}>{desc}</p>
            </div>
          </div>
        ))}
      </div>

      {sqliAlerts?.total > 0 ? (
        <div style={{ background: "#f43f5e08", border: `2px solid #f43f5e44`, borderRadius: 12, marginBottom: 24, overflow: "hidden" }}>
          <div style={{ background: "#f43f5e15", borderBottom: `1px solid #f43f5e33`, padding: "16px 24px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <span style={{ fontSize: 20 }}>🚨</span>
              <div>
                <p style={{ margin: 0, color: C.red, fontWeight: 800, fontSize: 13, letterSpacing: 1, textTransform: "uppercase" }}>SQL Injection Attacks Detected</p>
                <p style={{ margin: 0, color: C.muted, fontSize: 11 }}>{sqliAlerts.total} attempts — {sqliAlerts.high_severity} high severity</p>
              </div>
            </div>
            <div style={{ display: "flex", gap: 20 }}>
              <div style={{ textAlign: "center" }}>
                <p style={{ margin: 0, color: C.red, fontWeight: 800, fontSize: 24, fontFamily: "monospace" }}>{sqliAlerts.high_severity}</p>
                <p style={{ margin: 0, color: C.muted, fontSize: 10, textTransform: "uppercase" }}>High</p>
              </div>
              <div style={{ textAlign: "center" }}>
                <p style={{ margin: 0, color: C.yellow, fontWeight: 800, fontSize: 24, fontFamily: "monospace" }}>{sqliAlerts.medium_severity}</p>
                <p style={{ margin: 0, color: C.muted, fontSize: 10, textTransform: "uppercase" }}>Medium</p>
              </div>
            </div>
          </div>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: `1px solid ${C.border}` }}>
                {["IP Address", "Attack Type", "Malicious Request", "Severity"].map(h => (
                  <th key={h} style={{ padding: "12px 20px", textAlign: "left", color: C.muted, fontSize: 11, letterSpacing: 1, textTransform: "uppercase" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sqliAlerts.alerts.map((alert, i) => (
                <tr key={i} style={{ borderBottom: `1px solid #1e293b22` }}>
                  <td style={{ padding: "12px 20px", color: C.red, fontFamily: "monospace", fontSize: 12, fontWeight: 700 }}>{alert.ip_address}</td>
                  <td style={{ padding: "12px 20px" }}>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                      {alert.attack_types.map(t => (
                        <span key={t} style={{ background: "#f43f5e22", color: C.red, border: "1px solid #f43f5e44", borderRadius: 4, padding: "2px 8px", fontSize: 10, fontWeight: 700, textTransform: "uppercase" }}>
                          {t.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td style={{ padding: "12px 20px", color: C.muted, fontSize: 11, fontFamily: "monospace", maxWidth: 280, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{alert.request}</td>
                  <td style={{ padding: "12px 20px" }}><SeverityDots severity={alert.severity} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{ background: "#22d3a008", border: `1px solid ${C.green}33`, borderRadius: 12, padding: 20, marginBottom: 24, display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: 20 }}>✅</span>
          <div>
            <p style={{ margin: 0, color: C.green, fontWeight: 700, fontSize: 13 }}>No SQL Injection Attacks Detected</p>
            <p style={{ margin: 0, color: C.muted, fontSize: 11 }}>Apache logs are clean</p>
          </div>
        </div>
      )}

      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, overflow: "hidden", marginBottom: 20 }}>
        <div style={{ padding: "16px 24px", borderBottom: `1px solid ${C.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ color: C.text, fontSize: 13, letterSpacing: 1, textTransform: "uppercase" }}>🔍 Real-Time Log Analysis</span>
          <span style={{ color: C.muted, fontSize: 11 }}>{logAlerts?.alerts?.length ?? 0} alerts</span>
        </div>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: `1px solid ${C.border}` }}>
              {["Time", "Source", "Event Type", "User / IP", "Threat Level", "Score"].map(h => (
                <th key={h} style={{ padding: "12px 20px", textAlign: "left", color: C.muted, fontSize: 11, letterSpacing: 1, textTransform: "uppercase" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {logAlerts?.alerts?.length > 0 ? logAlerts.alerts.map((alert, i) => (
              <tr key={i} style={{ borderBottom: `1px solid ${C.border}`, background: alert.threat_level === 'HIGH' ? "#f43f5e08" : "transparent" }}>
                <td style={{ padding: "12px 20px", color: C.muted, fontSize: 11, fontFamily: "monospace" }}>{new Date(alert.timestamp).toLocaleTimeString()}</td>
                <td style={{ padding: "12px 20px" }}><span style={{ color: C.accent, fontSize: 11, fontFamily: "monospace", fontWeight: 700 }}>{alert.source}</span></td>
                <td style={{ padding: "12px 20px", color: C.text, fontSize: 12 }}>{alert.event_type}</td>
                <td style={{ padding: "12px 20px", color: C.muted, fontSize: 11, fontFamily: "monospace" }}>{alert.username || alert.ip_address || 'N/A'}</td>
                <td style={{ padding: "12px 20px" }}><Badge label={alert.threat_level} type={alert.threat_level} /></td>
                <td style={{ padding: "12px 20px", fontFamily: "monospace", fontSize: 13, fontWeight: 700, color: alert.anomaly_score > 0.6 ? C.red : C.yellow }}>{alert.anomaly_score?.toFixed(2)}</td>
              </tr>
            )) : (
              <tr><td colSpan="6" style={{ padding: 40, textAlign: "center", color: C.muted }}>No log alerts yet — click scan below</td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div style={{ textAlign: "center" }}>
        <button onClick={onScan} disabled={scanning} style={{
          background: scanning ? C.muted : C.accent, color: C.bg,
          border: "none", padding: "12px 32px", borderRadius: 8,
          cursor: scanning ? "not-allowed" : "pointer",
          fontWeight: 700, fontSize: 14, fontFamily: "inherit",
        }}>
          {scanning ? "⏳ Scanning..." : "🔍 Run New Log Scan"}
        </button>
        <p style={{ color: C.muted, fontSize: 11, marginTop: 8 }}>Scans auth.log, apache2/access.log, and syslog for threats including SQL injection</p>
      </div>
    </>
  );
}
