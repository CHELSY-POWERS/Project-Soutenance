import { C, KPI, Badge, SeverityDots } from "../UI";

export default function LogsTab({ logAlerts, sqliAlerts, scanning, onScan }) {

  // Count live alerts (detected by file watcher, not manual scan)
  const liveAlerts = (logAlerts?.alerts || []).filter(a => a.live === true);
  const hasLive    = liveAlerts.length > 0;

  return (
    <>
      {/* LIVE ALERT BANNER — only shows when file watcher detected something */}
      {hasLive && (
        <div style={{
          background: "#f43f5e18",
          border: "2px solid #f43f5e",
          borderRadius: 10,
          padding: "12px 20px",
          marginBottom: 20,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          animation: "pulseBorder 1.5s ease-in-out infinite",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{
              width: 10, height: 10, borderRadius: "50%",
              background: "#f43f5e",
              boxShadow: "0 0 10px #f43f5e",
            }} />
            <span style={{ color: "#f43f5e", fontWeight: 800, fontSize: 13, letterSpacing: 1 }}>
              ⚡ {liveAlerts.length} LIVE THREAT{liveAlerts.length > 1 ? 'S' : ''} DETECTED
            </span>
            <span style={{ color: C.muted, fontSize: 11 }}>
              — automatically detected by real-time file watcher
            </span>
          </div>
          <span style={{ color: C.muted, fontSize: 10, fontFamily: "monospace" }}>
            Last: {new Date(liveAlerts[0]?.timestamp).toLocaleTimeString()}
          </span>
        </div>
      )}

      {/* KPI Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 24 }}>
        <KPI title="Total Alerts"   value={logAlerts?.total ?? 0}  sub="From all log sources"   accent={C.accent} />
        <KPI title="High Threats"   value={logAlerts?.high ?? 0}   sub="Immediate attention"    accent={C.red}    />
        <KPI title="Medium Threats" value={logAlerts?.medium ?? 0} sub="Needs investigation"    accent={C.yellow} />
        <KPI title="SQLi Attacks"   value={sqliAlerts?.total ?? 0} sub="SQL injection attempts" accent={C.purple} />
      </div>

      {/* Source breakdown */}
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

      {/* SQLi Section */}
      {sqliAlerts?.total > 0 ? (
        <div style={{ background: "#f43f5e08", border: `2px solid #f43f5e44`, borderRadius: 12, marginBottom: 24, overflow: "hidden" }}>
          <div style={{ padding: "14px 20px", borderBottom: `1px solid #f43f5e33`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ color: C.red, fontWeight: 700, fontSize: 13 }}>💉 SQL Injection Attempts Detected</span>
            <span style={{ color: C.red, fontSize: 11, fontWeight: 700 }}>{sqliAlerts.total} attacks</span>
          </div>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: `1px solid #f43f5e22` }}>
                {["Time", "IP Address", "Method", "URI", "Pattern"].map(h => (
                  <th key={h} style={{ padding: "10px 16px", textAlign: "left", color: C.muted, fontSize: 10, letterSpacing: 1, textTransform: "uppercase" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sqliAlerts.attacks?.slice(0, 10).map((a, i) => (
                <tr key={i} style={{ borderBottom: `1px solid #f43f5e11` }}>
                  <td style={{ padding: "10px 16px", color: C.muted, fontSize: 11, fontFamily: "monospace" }}>{new Date(a.timestamp).toLocaleTimeString()}</td>
                  <td style={{ padding: "10px 16px", color: C.red, fontFamily: "monospace", fontSize: 12, fontWeight: 700 }}>{a.ip || 'N/A'}</td>
                  <td style={{ padding: "10px 16px", color: C.muted, fontSize: 11 }}>{a.method || 'GET'}</td>
                  <td style={{ padding: "10px 16px", color: C.yellow, fontSize: 10, fontFamily: "monospace", maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.uri || a.request || 'N/A'}</td>
                  <td style={{ padding: "10px 16px" }}>
                    <span style={{ background: "#f43f5e22", color: C.red, border: "1px solid #f43f5e44", borderRadius: 4, padding: "2px 6px", fontSize: 10, fontWeight: 700 }}>
                      {a.pattern || a.attack_type || 'SQLi'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{ background: "#22d3a011", border: `1px solid #22d3a033`, borderRadius: 10, padding: "12px 20px", marginBottom: 24, color: C.green, fontSize: 12 }}>
          ✓ No SQL injection attempts detected in Apache logs
        </div>
      )}

      {/* Manual scan button */}
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 20 }}>
        <button onClick={onScan} disabled={scanning} style={{
          background: scanning ? C.border : C.accent,
          color: scanning ? C.muted : C.bg,
          border: "none", borderRadius: 8,
          padding: "10px 24px", cursor: scanning ? "not-allowed" : "pointer",
          fontWeight: 700, fontSize: 13, fontFamily: "inherit", letterSpacing: 1,
        }}>
          {scanning ? '⏳ Scanning...' : '🔍 Run Log Scan'}
        </button>
        <span style={{ color: C.muted, fontSize: 11 }}>
          Manual scan of all log files. Live threats above are detected automatically.
        </span>
      </div>

      {/* Alerts table */}
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, overflow: "hidden" }}>
        <div style={{ padding: "14px 20px", borderBottom: `1px solid ${C.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ color: C.text, fontSize: 13, letterSpacing: 1, textTransform: "uppercase" }}>
            📋 Log Analysis Results
          </span>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            {hasLive && (
              <span style={{ background: "#f43f5e22", color: C.red, border: "1px solid #f43f5e44", borderRadius: 10, padding: "2px 8px", fontSize: 10, fontWeight: 700 }}>
                {liveAlerts.length} live
              </span>
            )}
            <span style={{ color: C.muted, fontSize: 11 }}>{logAlerts?.alerts?.length ?? 0} events</span>
          </div>
        </div>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: `1px solid ${C.border}` }}>
              {["Time", "Source", "Event Type", "IP Address", "User", "Threat", "Score", ""].map(h => (
                <th key={h} style={{ padding: "12px 16px", textAlign: "left", color: C.muted, fontSize: 10, letterSpacing: 1, textTransform: "uppercase" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {logAlerts?.alerts?.length > 0 ? logAlerts.alerts.slice(0, 50).map((alert, i) => (
              <tr key={i} style={{
                borderBottom: `1px solid ${C.border}`,
                background: alert.live
                  ? "#f43f5e14"   // red tint for live alerts
                  : i % 2 === 0 ? "#f43f5e05" : "transparent",
              }}>
                <td style={{ padding: "10px 16px", color: C.muted, fontSize: 11, fontFamily: "monospace" }}>
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </td>
                <td style={{ padding: "10px 16px", color: C.muted, fontSize: 11 }}>{alert.source}</td>
                <td style={{ padding: "10px 16px", color: C.text, fontSize: 12, fontWeight: 600 }}>
                  {alert.event_type?.replace(/_/g, ' ')}
                </td>
                <td style={{ padding: "10px 16px", color: C.accent, fontFamily: "monospace", fontSize: 11 }}>
                  {alert.ip_address || 'N/A'}
                </td>
                <td style={{ padding: "10px 16px", color: C.muted, fontSize: 11 }}>{alert.username || 'N/A'}</td>
                <td style={{ padding: "10px 16px" }}>
                  <span style={{
                    background: alert.threat_level === 'HIGH' ? "#f43f5e22" : "#fbbf2422",
                    color: alert.threat_level === 'HIGH' ? C.red : C.yellow,
                    border: `1px solid ${alert.threat_level === 'HIGH' ? '#f43f5e44' : '#fbbf2444'}`,
                    borderRadius: 4, padding: "2px 6px", fontSize: 10, fontWeight: 700,
                  }}>
                    {alert.threat_level}
                  </span>
                </td>
                <td style={{ padding: "10px 16px", fontFamily: "monospace", fontSize: 12,
                  color: alert.anomaly_score > 0.8 ? C.red : C.yellow, fontWeight: 700 }}>
                  {typeof alert.anomaly_score === 'number' ? alert.anomaly_score.toFixed(2) : 'N/A'}
                </td>
                {/* LIVE badge */}
                <td style={{ padding: "10px 16px" }}>
                  {alert.live && (
                    <span style={{
                      background: "#f43f5e33", color: C.red,
                      border: "1px solid #f43f5e66",
                      borderRadius: 4, padding: "2px 6px",
                      fontSize: 9, fontWeight: 800, letterSpacing: 1,
                    }}>
                      ⚡ LIVE
                    </span>
                  )}
                </td>
              </tr>
            )) : (
              <tr>
                <td colSpan="8" style={{ padding: 40, textAlign: "center", color: C.muted }}>
                  No alerts yet — run a log scan or wait for live detection
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <style>{`
        @keyframes pulseBorder {
          0%, 100% { box-shadow: 0 0 0 0 #f43f5e44; }
          50%       { box-shadow: 0 0 0 6px #f43f5e11; }
        }
      `}</style>
    </>
  );
}