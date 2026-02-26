export const C = {
  bg:      "#0b0f1a",
  surface: "#111827",
  border:  "#1e293b",
  accent:  "#00d4ff",
  green:   "#22d3a0",
  red:     "#f43f5e",
  yellow:  "#fbbf24",
  purple:  "#a78bfa",
  text:    "#e2e8f0",
  muted:   "#64748b",
};

export const Badge = ({ label, type }) => {
  const colors = {
    anomaly:    { bg: "#f43f5e22", text: "#f43f5e", border: "#f43f5e55" },
    normal:     { bg: "#22d3a022", text: "#22d3a0", border: "#22d3a055" },
    suspicious: { bg: "#fbbf2422", text: "#fbbf24", border: "#fbbf2455" },
    HIGH:       { bg: "#f43f5e22", text: "#f43f5e", border: "#f43f5e55" },
    MEDIUM:     { bg: "#fbbf2422", text: "#fbbf24", border: "#fbbf2455" },
    LOW:        { bg: "#22d3a022", text: "#22d3a0", border: "#22d3a055" },
  };
  const s = colors[type] || colors.normal;
  return (
    <span style={{
      background: s.bg, color: s.text, border: `1px solid ${s.border}`,
      borderRadius: 6, padding: "2px 10px", fontSize: 11,
      fontWeight: 700, letterSpacing: 1, textTransform: "uppercase",
    }}>{label}</span>
  );
};

export const KPI = ({ title, value, sub, accent }) => (
  <div style={{
    background: C.surface, border: `1px solid ${C.border}`,
    borderRadius: 12, padding: "22px 24px",
    position: "relative", overflow: "hidden",
  }}>
    <div style={{
      position: "absolute", top: 0, left: 0, width: 4, height: "100%",
      background: accent || C.accent, borderRadius: "12px 0 0 12px",
    }} />
    <p style={{ margin: 0, color: C.muted, fontSize: 12, letterSpacing: 1, textTransform: "uppercase" }}>{title}</p>
    <p style={{ margin: "8px 0 4px", color: C.text, fontSize: 32, fontWeight: 800, fontFamily: "monospace" }}>{value}</p>
    {sub && <p style={{ margin: 0, color: C.muted, fontSize: 12 }}>{sub}</p>}
  </div>
);

export const MetricRow = ({ label, value, color }) => (
  <div style={{ marginBottom: 14 }}>
    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
      <span style={{ color: C.muted, fontSize: 13 }}>{label}</span>
      <span style={{ color: C.text, fontWeight: 700, fontFamily: "monospace", fontSize: 13 }}>{value}%</span>
    </div>
    <div style={{ height: 6, background: C.border, borderRadius: 4, overflow: "hidden" }}>
      <div style={{ width: `${value}%`, height: "100%", background: color, borderRadius: 4, transition: "width 1s ease" }} />
    </div>
  </div>
);

export const SeverityDots = ({ severity }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
    {[1,2,3,4,5].map(n => (
      <div key={n} style={{ width: 8, height: 8, borderRadius: 2, background: n <= severity ? "#f43f5e" : "#1e293b" }} />
    ))}
    <span style={{ color: "#f43f5e", fontSize: 11, fontFamily: "monospace", fontWeight: 700, marginLeft: 4 }}>
      {severity}/5
    </span>
  </div>
);
