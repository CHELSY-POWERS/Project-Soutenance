import { C, Badge } from "../UI";

export default function ResultsTab({ results, filter, setFilter }) {
  const filtered = results.filter(r => filter === 'all' || r.prediction === filter);
  return (
    <>
      <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
        {["all", "normal", "anomaly"].map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{
            background: filter === f ? C.accent : C.surface,
            color: filter === f ? C.bg : C.muted,
            border: `1px solid ${filter === f ? C.accent : C.border}`,
            borderRadius: 8, padding: "8px 20px", cursor: "pointer",
            fontSize: 12, fontFamily: "inherit", letterSpacing: 1,
            textTransform: "uppercase", transition: "all .2s",
          }}>{f}</button>
        ))}
        <span style={{ marginLeft: "auto", color: C.muted, fontSize: 12, alignSelf: "center" }}>{filtered.length} events</span>
      </div>
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: `1px solid ${C.border}` }}>
              {["Event ID", "Timestamp", "Prediction", "Anomaly Score", "Confidence"].map(h => (
                <th key={h} style={{ padding: "14px 20px", textAlign: "left", color: C.muted, fontSize: 11, letterSpacing: 1, textTransform: "uppercase", fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length > 0 ? filtered.map((r) => (
              <tr key={r.event_id} style={{ borderBottom: `1px solid ${C.border}`, background: r.prediction === "anomaly" ? "#f43f5e08" : "transparent" }}>
                <td style={{ padding: "12px 20px", color: C.muted, fontSize: 12, fontFamily: "monospace" }}>#{String(r.event_id).padStart(4, "0")}</td>
                <td style={{ padding: "12px 20px", color: C.muted, fontSize: 11 }}>{new Date(r.timestamp).toLocaleString()}</td>
                <td style={{ padding: "12px 20px" }}><Badge label={r.prediction} type={r.prediction} /></td>
                <td style={{ padding: "12px 20px", fontFamily: "monospace", fontSize: 13, color: r.anomaly_score > 0.5 ? C.red : C.green, fontWeight: 700 }}>{r.anomaly_score.toFixed(4)}</td>
                <td style={{ padding: "12px 20px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div style={{ width: 60, height: 5, background: C.border, borderRadius: 4, overflow: "hidden" }}>
                      <div style={{ width: `${(r.confidence * 100).toFixed(0)}%`, height: "100%", background: C.accent, borderRadius: 4 }} />
                    </div>
                    <span style={{ color: C.muted, fontSize: 11, fontFamily: "monospace" }}>{(r.confidence * 100).toFixed(0)}%</span>
                  </div>
                </td>
              </tr>
            )) : (
              <tr><td colSpan="5" style={{ padding: 40, textAlign: "center", color: C.muted }}>No {filter} events found</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}
