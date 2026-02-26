import { C, MetricRow } from "../UI";

export default function MetricsTab({ summary }) {
  const { detection, performance, model } = summary;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, padding: 28 }}>
        <p style={{ margin: "0 0 24px", color: C.text, fontSize: 13, letterSpacing: 1, textTransform: "uppercase" }}>Classification Metrics</p>
        <MetricRow label="Accuracy"  value={performance.accuracy}  color={C.accent} />
        <MetricRow label="Precision" value={performance.precision} color={C.green}  />
        <MetricRow label="Recall"    value={performance.recall}    color={C.yellow} />
        <MetricRow label="F1-Score"  value={performance.f1_score}  color={C.purple} />
      </div>
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, padding: 28 }}>
        <p style={{ margin: "0 0 24px", color: C.text, fontSize: 13, letterSpacing: 1, textTransform: "uppercase" }}>Model Information</p>
        {[
          ["Algorithm",     model.algorithm],
          ["Status",        model.is_trained ? "Trained ✓" : "Not Trained"],
          ["Training Date", model.training_date ? String(model.training_date).slice(0, 10) : "2026-02-21"],
          ["Total Events",  detection.total_events.toLocaleString()],
          ["Anomaly Rate",  `${detection.anomaly_rate}%`],
        ].map(([k, v]) => (
          <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "12px 0", borderBottom: `1px solid ${C.border}` }}>
            <span style={{ color: C.muted, fontSize: 12 }}>{k}</span>
            <span style={{ color: C.text, fontSize: 12, fontWeight: 700, fontFamily: "monospace" }}>{v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
