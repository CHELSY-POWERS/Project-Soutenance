import { useState, useEffect } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell,
  LineChart, Line
} from "recharts";

// ── API Service - connects to REAL Flask backend ────────────────────────────
const API_BASE = 'http://localhost:5000/api';

const api = {
  getDashboardSummary: async () => {
    const response = await fetch(`${API_BASE}/dashboard/summary`);
    if (!response.ok) throw new Error('Backend not reachable');
    return await response.json();
  },

  getDetectionResults: async (page = 1, perPage = 20, filter = 'all') => {
    const response = await fetch(
      `${API_BASE}/detection/results?page=${page}&per_page=${perPage}&filter=${filter}`
    );
    if (!response.ok) throw new Error('Failed to fetch results');
    return await response.json();
  },

  getStatistics: async () => {
    const response = await fetch(`${API_BASE}/statistics`);
    if (!response.ok) throw new Error('Failed to fetch statistics');
    return await response.json();
  },
};

// ── Colour palette ──────────────────────────────────────────────────────────
const C = {
  bg:        "#0b0f1a",
  surface:   "#111827",
  border:    "#1e293b",
  accent:    "#00d4ff",
  accentDim: "#0ea5c9",
  green:     "#22d3a0",
  red:       "#f43f5e",
  yellow:    "#fbbf24",
  text:      "#e2e8f0",
  muted:     "#64748b",
};

// ── Components ──────────────────────────────────────────────────────────────
const Badge = ({ label, type }) => {
  const colors = {
    anomaly: { bg: "#f43f5e22", text: C.red,   border: "#f43f5e55" },
    normal:  { bg: "#22d3a022", text: C.green, border: "#22d3a055" },
  };
  const s = colors[type] || colors.normal;
  return (
    <span style={{
      background: s.bg, color: s.text,
      border: `1px solid ${s.border}`,
      borderRadius: 6, padding: "2px 10px",
      fontSize: 11, fontWeight: 700, letterSpacing: 1,
      textTransform: "uppercase",
    }}>
      {label}
    </span>
  );
};

const KPI = ({ title, value, sub, accent }) => (
  <div style={{
    background: C.surface,
    border: `1px solid ${C.border}`,
    borderRadius: 12,
    padding: "22px 24px",
    position: "relative",
    overflow: "hidden",
  }}>
    <div style={{
      position: "absolute", top: 0, left: 0,
      width: 4, height: "100%",
      background: accent || C.accent,
      borderRadius: "12px 0 0 12px",
    }} />
    <p style={{ margin: 0, color: C.muted, fontSize: 12, letterSpacing: 1, textTransform: "uppercase" }}>
      {title}
    </p>
    <p style={{ margin: "8px 0 4px", color: C.text, fontSize: 32, fontWeight: 800, fontFamily: "monospace" }}>
      {value}
    </p>
    {sub && <p style={{ margin: 0, color: C.muted, fontSize: 12 }}>{sub}</p>}
  </div>
);

const MetricRow = ({ label, value, color }) => (
  <div style={{ marginBottom: 14 }}>
    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
      <span style={{ color: C.muted, fontSize: 13 }}>{label}</span>
      <span style={{ color: C.text, fontWeight: 700, fontFamily: "monospace", fontSize: 13 }}>
        {value}%
      </span>
    </div>
    <div style={{ height: 6, background: C.border, borderRadius: 4, overflow: "hidden" }}>
      <div style={{
        width: `${value}%`, height: "100%",
        background: color, borderRadius: 4,
        transition: "width 1s ease",
      }} />
    </div>
  </div>
);

// ── MAIN COMPONENT ──────────────────────────────────────────────────────────
export default function AIDashboard() {
  const [summary, setSummary]   = useState(null);
  const [results, setResults]   = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [filter, setFilter]     = useState("all");
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (summary) {
      loadResults();
    }
  }, [filter, summary]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [summaryData, statsData] = await Promise.all([
        api.getDashboardSummary(),
        api.getStatistics().catch(() => null), // Optional
      ]);
      
      setSummary(summaryData);
      setStatistics(statsData);
      setLoading(false);
    } catch (err) {
      setError('Cannot connect to backend. Make sure Flask server is running on http://localhost:5000');
      setLoading(false);
      console.error('Backend connection error:', err);
    }
  };

  const loadResults = async () => {
    try {
      const data = await api.getDetectionResults(1, 20, filter);
      setResults(data.results || []);
    } catch (err) {
      console.error('Failed to load results:', err);
    }
  };

  if (loading) return (
    <div style={{
      minHeight: "100vh", background: C.bg,
      display: "flex", alignItems: "center", justifyContent: "center",
    }}>
      <div style={{ textAlign: "center" }}>
        <div style={{
          width: 48, height: 48, border: `3px solid ${C.border}`,
          borderTop: `3px solid ${C.accent}`,
          borderRadius: "50%", margin: "0 auto 16px",
          animation: "spin 1s linear infinite",
        }} />
        <p style={{ color: C.muted, fontFamily: "monospace" }}>Connecting to AI Backend…</p>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );

  if (error) return (
    <div style={{
      minHeight: "100vh", background: C.bg,
      display: "flex", alignItems: "center", justifyContent: "center",
      padding: 40,
    }}>
      <div style={{
        background: C.surface, border: `2px solid ${C.red}`,
        borderRadius: 12, padding: 40, maxWidth: 600, textAlign: "center",
      }}>
        <div style={{ fontSize: 48, marginBottom: 20 }}>⚠️</div>
        <h2 style={{ color: C.text, margin: "0 0 16px" }}>Backend Connection Failed</h2>
        <p style={{ color: C.muted, marginBottom: 24 }}>{error}</p>
        <div style={{ 
          background: C.bg, padding: 16, borderRadius: 8,
          fontFamily: "monospace", fontSize: 13, color: C.accent,
          textAlign: "left",
        }}>
          <div>1. Open terminal</div>
          <div>2. cd ~/ai-ids-project</div>
          <div>3. source venv/bin/activate</div>
          <div>4. python backend/app.py</div>
        </div>
        <button onClick={loadData} style={{
          marginTop: 24, background: C.accent, color: C.bg,
          border: "none", padding: "12px 32px", borderRadius: 8,
          cursor: "pointer", fontWeight: 700, fontSize: 14,
        }}>
          Retry Connection
        </button>
      </div>
    </div>
  );

  const { detection, performance, model } = summary;

  // Chart data
  const barData = [
    { name: "Accuracy",  value: performance.accuracy,  fill: C.accent },
    { name: "Precision", value: performance.precision, fill: C.green },
    { name: "Recall",    value: performance.recall,    fill: C.yellow },
    { name: "F1-Score",  value: performance.f1_score,  fill: "#a78bfa" },
  ];

  const scoreData = statistics?.top_anomalies?.slice(0, 20).map((a, i) => ({
    idx: i + 1,
    score: a.anomaly_score,
  })) || [];

  const filtered = results.filter(r => 
    filter === 'all' || r.prediction === filter
  );

  const tabs = ["overview", "results", "metrics"];

  return (
    <div style={{
      minHeight: "100vh", background: C.bg,
      color: C.text, fontFamily: "'IBM Plex Mono', 'Courier New', monospace",
    }}>

      {/* ── TOP BAR ── */}
      <header style={{
        background: C.surface, borderBottom: `1px solid ${C.border}`,
        padding: "0 32px", display: "flex",
        alignItems: "center", justifyContent: "space-between",
        height: 60,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 10, height: 10, borderRadius: "50%",
            background: C.green,
            boxShadow: `0 0 8px ${C.green}`,
            animation: "pulse 2s ease-in-out infinite",
          }} />
          <span style={{ color: C.accent, fontWeight: 800, fontSize: 15, letterSpacing: 2 }}>
            AI-IDS
          </span>
          <span style={{ color: C.muted, fontSize: 12 }}>
            Autonomous Intrusion Detection System
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <span style={{ color: C.muted, fontSize: 11 }}>
            {model.algorithm}
          </span>
          <Badge label="LIVE" type="normal" />
        </div>
      </header>

      {/* ── TABS ── */}
      <div style={{
        background: C.surface, borderBottom: `1px solid ${C.border}`,
        padding: "0 32px", display: "flex", gap: 4,
      }}>
        {tabs.map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)} style={{
            background: "none", border: "none",
            borderBottom: activeTab === tab ? `2px solid ${C.accent}` : "2px solid transparent",
            color: activeTab === tab ? C.accent : C.muted,
            padding: "14px 20px 12px",
            cursor: "pointer", fontSize: 12,
            letterSpacing: 1, textTransform: "uppercase",
            fontFamily: "inherit", transition: "color .2s",
          }}>
            {tab}
          </button>
        ))}
      </div>

      {/* ── CONTENT ── */}
      <main style={{ padding: "32px", maxWidth: 1200, margin: "0 auto" }}>

        {/* ── OVERVIEW TAB ── */}
        {activeTab === "overview" && (
          <>
            {/* KPI Row */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: 16, marginBottom: 32,
            }}>
              <KPI
                title="Total Events"
                value={detection.total_events.toLocaleString()}
                sub="Network events analysed"
                accent={C.accent}
              />
              <KPI
                title="Normal"
                value={detection.normal_events.toLocaleString()}
                sub={`${(100 - detection.anomaly_rate).toFixed(1)}% of total`}
                accent={C.green}
              />
              <KPI
                title="Anomalies"
                value={detection.anomalous_events.toLocaleString()}
                sub={`${detection.anomaly_rate}% detected`}
                accent={C.red}
              />
              <KPI
                title="Accuracy"
                value={`${performance.accuracy}%`}
                sub="Model performance"
                accent="#a78bfa"
              />
            </div>

            {/* Charts Row */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: 20, marginBottom: 32,
            }}>
              {/* Bar chart */}
              <div style={{
                background: C.surface, border: `1px solid ${C.border}`,
                borderRadius: 12, padding: 24,
              }}>
                <p style={{
                  margin: "0 0 20px", color: C.text,
                  fontSize: 13, letterSpacing: 1, textTransform: "uppercase",
                }}>
                  AI Model Performance
                </p>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={barData}>
                    <CartesianGrid strokeDasharray="3 3" stroke={C.border} />
                    <XAxis dataKey="name" tick={{ fill: C.muted, fontSize: 11 }} />
                    <YAxis domain={[0, 100]} tick={{ fill: C.muted, fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{ background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8 }}
                      labelStyle={{ color: C.muted }}
                      formatter={v => [`${v}%`]}
                    />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                      {barData.map((entry, i) => (
                        <Cell key={i} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Anomaly scores */}
              <div style={{
                background: C.surface, border: `1px solid ${C.border}`,
                borderRadius: 12, padding: 24,
              }}>
                <p style={{
                  margin: "0 0 20px", color: C.text,
                  fontSize: 13, letterSpacing: 1, textTransform: "uppercase",
                }}>
                  Top Anomaly Scores
                </p>
                {scoreData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={scoreData}>
                      <CartesianGrid strokeDasharray="3 3" stroke={C.border} />
                      <XAxis dataKey="idx" tick={{ fill: C.muted, fontSize: 10 }} />
                      <YAxis tick={{ fill: C.muted, fontSize: 10 }} />
                      <Tooltip
                        contentStyle={{ background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8 }}
                        labelStyle={{ color: C.muted }}
                      />
                      <Line
                        type="monotone" dataKey="score"
                        stroke={C.accent} strokeWidth={2}
                        dot={{ fill: C.accent, r: 3 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div style={{ height: 200, display: "flex", alignItems: "center", justifyContent: "center", color: C.muted }}>
                    Run detection to see anomaly distribution
                  </div>
                )}
              </div>
            </div>

            {/* Detection / False-positive rate */}
            <div style={{
              display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20,
            }}>
              <div style={{
                background: "#22d3a011", border: `1px solid ${C.green}33`,
                borderRadius: 12, padding: 24,
              }}>
                <p style={{ margin: "0 0 8px", color: C.muted, fontSize: 12, letterSpacing: 1, textTransform: "uppercase" }}>
                  Detection Rate
                </p>
                <p style={{ margin: "0 0 4px", color: C.green, fontSize: 36, fontWeight: 800 }}>
                  {performance.detection_rate}%
                </p>
                <p style={{ margin: 0, color: C.muted, fontSize: 12 }}>
                  Attacks successfully detected by AI
                </p>
              </div>
              <div style={{
                background: "#f43f5e11", border: `1px solid ${C.red}33`,
                borderRadius: 12, padding: 24,
              }}>
                <p style={{ margin: "0 0 8px", color: C.muted, fontSize: 12, letterSpacing: 1, textTransform: "uppercase" }}>
                  False Positive Rate
                </p>
                <p style={{ margin: "0 0 4px", color: C.red, fontSize: 36, fontWeight: 800 }}>
                  {performance.false_positive_rate}%
                </p>
                <p style={{ margin: 0, color: C.muted, fontSize: 12 }}>
                  Normal traffic incorrectly flagged
                </p>
              </div>
            </div>
          </>
        )}

        {/* ── RESULTS TAB ── */}
        {activeTab === "results" && (
          <>
            {/* Filter Buttons */}
            <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
              {["all", "normal", "anomaly"].map(f => (
                <button key={f} onClick={() => setFilter(f)} style={{
                  background: filter === f ? C.accent : C.surface,
                  color: filter === f ? C.bg : C.muted,
                  border: `1px solid ${filter === f ? C.accent : C.border}`,
                  borderRadius: 8, padding: "8px 20px",
                  cursor: "pointer", fontSize: 12,
                  fontFamily: "inherit", letterSpacing: 1,
                  textTransform: "uppercase", transition: "all .2s",
                }}>
                  {f}
                </button>
              ))}
              <span style={{ marginLeft: "auto", color: C.muted, fontSize: 12, alignSelf: "center" }}>
                {filtered.length} events
              </span>
            </div>

            {/* Table */}
            <div style={{
              background: C.surface, border: `1px solid ${C.border}`,
              borderRadius: 12, overflow: "hidden",
            }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ borderBottom: `1px solid ${C.border}` }}>
                    {["Event ID", "Timestamp", "Prediction", "Anomaly Score", "Confidence"].map(h => (
                      <th key={h} style={{
                        padding: "14px 20px", textAlign: "left",
                        color: C.muted, fontSize: 11,
                        letterSpacing: 1, textTransform: "uppercase",
                        fontWeight: 600,
                      }}>
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filtered.length > 0 ? filtered.map((r) => (
                    <tr key={r.event_id} style={{
                      borderBottom: `1px solid ${C.border}`,
                      background: r.prediction === "anomaly" ? "#f43f5e08" : "transparent",
                    }}>
                      <td style={{ padding: "12px 20px", color: C.muted, fontSize: 12, fontFamily: "monospace" }}>
                        #{String(r.event_id).padStart(4, "0")}
                      </td>
                      <td style={{ padding: "12px 20px", color: C.muted, fontSize: 11 }}>
                        {new Date(r.timestamp).toLocaleString()}
                      </td>
                      <td style={{ padding: "12px 20px" }}>
                        <Badge label={r.prediction} type={r.prediction} />
                      </td>
                      <td style={{
                        padding: "12px 20px", fontFamily: "monospace", fontSize: 13,
                        color: r.anomaly_score > 0.5 ? C.red : C.green,
                        fontWeight: 700,
                      }}>
                        {r.anomaly_score.toFixed(4)}
                      </td>
                      <td style={{ padding: "12px 20px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                          <div style={{ width: 60, height: 5, background: C.border, borderRadius: 4, overflow: "hidden" }}>
                            <div style={{
                              width: `${(r.confidence * 100).toFixed(0)}%`,
                              height: "100%", background: C.accent, borderRadius: 4,
                            }} />
                          </div>
                          <span style={{ color: C.muted, fontSize: 11, fontFamily: "monospace" }}>
                            {(r.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan="5" style={{ padding: 40, textAlign: "center", color: C.muted }}>
                        No {filter} events found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </>
        )}

        {/* ── METRICS TAB ── */}
        {activeTab === "metrics" && (
          <div style={{
            display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24,
          }}>
            <div style={{
              background: C.surface, border: `1px solid ${C.border}`,
              borderRadius: 12, padding: 28,
            }}>
              <p style={{ margin: "0 0 24px", color: C.text, fontSize: 13, letterSpacing: 1, textTransform: "uppercase" }}>
                Classification Metrics
              </p>
              <MetricRow label="Accuracy"  value={performance.accuracy}  color={C.accent} />
              <MetricRow label="Precision" value={performance.precision} color={C.green} />
              <MetricRow label="Recall"    value={performance.recall}    color={C.yellow} />
              <MetricRow label="F1-Score"  value={performance.f1_score}  color="#a78bfa" />
            </div>

            <div style={{
              background: C.surface, border: `1px solid ${C.border}`,
              borderRadius: 12, padding: 28,
            }}>
              <p style={{ margin: "0 0 24px", color: C.text, fontSize: 13, letterSpacing: 1, textTransform: "uppercase" }}>
                Model Information
              </p>
              {[
                ["Algorithm",       model.algorithm],
                ["Status",          model.is_trained ? "Trained ✓" : "Not Trained"],
                ["Training Date",   new Date(model.training_date).toLocaleDateString()],
                ["Total Events",    detection.total_events.toLocaleString()],
                ["Anomaly Rate",    `${detection.anomaly_rate}%`],
              ].map(([k, v]) => (
                <div key={k} style={{
                  display: "flex", justifyContent: "space-between",
                  padding: "12px 0",
                  borderBottom: `1px solid ${C.border}`,
                }}>
                  <span style={{ color: C.muted, fontSize: 12 }}>{k}</span>
                  <span style={{ color: C.text, fontSize: 12, fontWeight: 700, fontFamily: "monospace" }}>{v}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50%       { opacity: 0.3; }
        }
      `}</style>
    </div>
  );
}