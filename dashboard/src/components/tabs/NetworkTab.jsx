import { C, KPI, SeverityDots } from "../UI";

export default function NetworkTab({ networkAlerts }) {
  return (
    <>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 24 }}>
        <KPI title="Total Alerts" value={networkAlerts?.total ?? 0}      sub="Network events captured"    accent={C.accent} />
        <KPI title="High Threats" value={networkAlerts?.high ?? 0}       sub="Immediate attention"        accent={C.red}    />
        <KPI title="Unique IPs"   value={networkAlerts?.unique_ips ?? 0} sub="Suspicious devices seen"    accent={C.yellow} />
        <KPI title="Attack Types" value={Object.keys(networkAlerts?.attack_types ?? {}).length} sub="Different methods" accent={C.purple} />
      </div>

      {networkAlerts?.attack_types && Object.keys(networkAlerts.attack_types).length > 0 && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
          {Object.entries(networkAlerts.attack_types).map(([type, count]) => (
            <div key={type} style={{ background: C.surface, border: `1px solid #f43f5e44`, borderRadius: 10, padding: 16, textAlign: "center" }}>
              <p style={{ margin: "0 0 6px", color: C.red, fontSize: 24, fontWeight: 800, fontFamily: "monospace" }}>{count}</p>
              <p style={{ margin: 0, color: C.muted, fontSize: 10, textTransform: "uppercase", letterSpacing: 1 }}>{type.replace(/_/g, ' ')}</p>
            </div>
          ))}
        </div>
      )}

      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, overflow: "hidden", marginBottom: 20 }}>
        <div style={{ padding: "16px 24px", borderBottom: `1px solid ${C.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ color: C.text, fontSize: 13, letterSpacing: 1, textTransform: "uppercase" }}>🌐 Live Network Traffic Analysis</span>
          <span style={{ color: networkAlerts?.total > 0 ? C.red : C.green, fontSize: 11, fontWeight: 700 }}>
            {networkAlerts?.total > 0 ? `⚠ ${networkAlerts.total} threats detected` : '✓ Network clean'}
          </span>
        </div>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: `1px solid ${C.border}` }}>
              {["Time", "Source IP", "Destination IP", "Attack Type", "Description", "Severity"].map(h => (
                <th key={h} style={{ padding: "12px 16px", textAlign: "left", color: C.muted, fontSize: 11, letterSpacing: 1, textTransform: "uppercase" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {networkAlerts?.alerts?.length > 0 ? networkAlerts.alerts.slice().reverse().map((alert, i) => (
              <tr key={i} style={{ borderBottom: `1px solid ${C.border}`, background: i % 2 === 0 ? "#f43f5e06" : "transparent" }}>
                <td style={{ padding: "11px 16px", color: C.muted, fontSize: 11, fontFamily: "monospace" }}>{new Date(alert.timestamp).toLocaleTimeString()}</td>
                <td style={{ padding: "11px 16px", color: C.red, fontFamily: "monospace", fontSize: 12, fontWeight: 700 }}>{alert.src_ip}</td>
                <td style={{ padding: "11px 16px", color: C.muted, fontFamily: "monospace", fontSize: 11 }}>{alert.dst_ip}</td>
                <td style={{ padding: "11px 16px" }}>
                  <span style={{ background: "#f43f5e22", color: C.red, border: "1px solid #f43f5e44", borderRadius: 4, padding: "2px 8px", fontSize: 10, fontWeight: 700, textTransform: "uppercase" }}>
                    {alert.attack_type.replace(/_/g, ' ')}
                  </span>
                </td>
                <td style={{ padding: "11px 16px", color: C.muted, fontSize: 11 }}>{alert.description}</td>
                <td style={{ padding: "11px 16px" }}><SeverityDots severity={alert.severity} /></td>
              </tr>
            )) : (
              <tr><td colSpan="6" style={{ padding: 40, textAlign: "center", color: C.muted }}>No network alerts yet — start the network monitor first</td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24 }}>
        <p style={{ margin: "0 0 12px", color: C.text, fontSize: 13, fontWeight: 700 }}>🖥️ Start Network Monitor</p>
        <div style={{ background: C.bg, borderRadius: 8, padding: 16, fontFamily: "monospace", fontSize: 12, color: C.accent, lineHeight: 2 }}>
          sudo /home/chelsy/ai-ids-project/venv/bin/python /home/chelsy/ai-ids-project/backend/log_analysis/network_monitor.py --interface wlp4s0
        </div>
        <p style={{ margin: "12px 0 0", color: C.muted, fontSize: 11 }}>Run in a separate terminal. Dashboard auto-refreshes every 30 seconds.</p>
      </div>
    </>
  );
}
