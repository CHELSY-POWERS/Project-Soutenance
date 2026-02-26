import { C, KPI } from "../UI";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, LineChart, Line } from "recharts";

export default function OverviewTab({ summary, statistics }) {
  const { detection, performance } = summary;

  const barData = [
    { name: "Accuracy",  value: performance.accuracy,  fill: C.accent  },
    { name: "Precision", value: performance.precision, fill: C.green   },
    { name: "Recall",    value: performance.recall,    fill: C.yellow  },
    { name: "F1-Score",  value: performance.f1_score,  fill: C.purple  },
  ];

  const scoreData = statistics?.top_anomalies?.slice(0, 20).map((a, i) => ({
    idx: i + 1, score: a.anomaly_score,
  })) || [];

  return (
    <>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, marginBottom: 32 }}>
        <KPI title="Total Events" value={detection.total_events.toLocaleString()}     sub="Network events analysed"                               accent={C.accent} />
        <KPI title="Normal"       value={detection.normal_events.toLocaleString()}     sub={`${(100 - detection.anomaly_rate).toFixed(1)}% of total`} accent={C.green}  />
        <KPI title="Anomalies"    value={detection.anomalous_events.toLocaleString()}  sub={`${detection.anomaly_rate}% detected`}                 accent={C.red}    />
        <KPI title="Accuracy"     value={`${performance.accuracy}%`}                   sub="Model performance"                                     accent={C.purple} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 32 }}>
        <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24 }}>
          <p style={{ margin: "0 0 20px", color: C.text, fontSize: 13, letterSpacing: 1, textTransform: "uppercase" }}>AI Model Performance</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" stroke={C.border} />
              <XAxis dataKey="name" tick={{ fill: C.muted, fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fill: C.muted, fontSize: 11 }} />
              <Tooltip contentStyle={{ background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8 }} formatter={v => [`${v}%`]} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {barData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24 }}>
          <p style={{ margin: "0 0 20px", color: C.text, fontSize: 13, letterSpacing: 1, textTransform: "uppercase" }}>Top Anomaly Scores</p>
          {scoreData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={scoreData}>
                <CartesianGrid strokeDasharray="3 3" stroke={C.border} />
                <XAxis dataKey="idx" tick={{ fill: C.muted, fontSize: 10 }} />
                <YAxis tick={{ fill: C.muted, fontSize: 10 }} />
                <Tooltip contentStyle={{ background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8 }} />
                <Line type="monotone" dataKey="score" stroke={C.accent} strokeWidth={2} dot={{ fill: C.accent, r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: 200, display: "flex", alignItems: "center", justifyContent: "center", color: C.muted }}>
              Run detection to see anomaly distribution
            </div>
          )}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <div style={{ background: "#22d3a011", border: `1px solid ${C.green}33`, borderRadius: 12, padding: 24 }}>
          <p style={{ margin: "0 0 8px", color: C.muted, fontSize: 12, letterSpacing: 1, textTransform: "uppercase" }}>Detection Rate</p>
          <p style={{ margin: "0 0 4px", color: C.green, fontSize: 36, fontWeight: 800 }}>{performance.detection_rate}%</p>
          <p style={{ margin: 0, color: C.muted, fontSize: 12 }}>Attacks successfully detected by AI</p>
        </div>
        <div style={{ background: "#f43f5e11", border: `1px solid ${C.red}33`, borderRadius: 12, padding: 24 }}>
          <p style={{ margin: "0 0 8px", color: C.muted, fontSize: 12, letterSpacing: 1, textTransform: "uppercase" }}>False Positive Rate</p>
          <p style={{ margin: "0 0 4px", color: C.red, fontSize: 36, fontWeight: 800 }}>{performance.false_positive_rate}%</p>
          <p style={{ margin: 0, color: C.muted, fontSize: 12 }}>Normal traffic incorrectly flagged</p>
        </div>
      </div>
    </>
  );
}
