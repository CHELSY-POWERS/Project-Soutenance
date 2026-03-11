import { useState } from "react";
import { C, Badge } from "../UI";

const PAGE_SIZE = 50;

export default function ResultsTab({ results, filter, setFilter }) {
  const [page, setPage] = useState(0);

  const filtered = results.filter(r => filter === 'all' || r.prediction === filter);
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated  = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  // Reset to page 0 when filter changes
  const handleFilter = (f) => { setFilter(f); setPage(0); };

  // Fix score display: Isolation Forest raw score meaning:
  // High score (close to 1) = normal traffic (not isolated easily)
  // Low score (close to 0)  = anomaly (isolated quickly by the tree)
  // So we flip the colour — high score = green (normal), low score = red (anomaly)
  const scoreColor = (score, prediction) => {
    if (prediction === 'anomaly') return C.red;
    return C.green;
  };

  // Score interpretation label
  const scoreLabel = (score, prediction) => {
    if (prediction === 'anomaly') {
      if (score < 0.3) return 'Strongly anomalous';
      if (score < 0.5) return 'Anomalous';
      return 'Borderline';
    }
    if (score > 0.8) return 'Clearly normal';
    if (score > 0.6) return 'Normal';
    return 'Borderline';
  };

  return (
    <>
      {/* Filter buttons + event count */}
      <div style={{ display: "flex", gap: 10, marginBottom: 20, alignItems: "center" }}>
        {["all", "normal", "anomaly"].map(f => (
          <button key={f} onClick={() => handleFilter(f)} style={{
            background: filter === f ? C.accent : C.surface,
            color:      filter === f ? C.bg : C.muted,
            border:     `1px solid ${filter === f ? C.accent : C.border}`,
            borderRadius: 8, padding: "8px 20px", cursor: "pointer",
            fontSize: 12, fontFamily: "inherit", letterSpacing: 1,
            textTransform: "uppercase", transition: "all .2s",
          }}>{f}</button>
        ))}
        <span style={{ marginLeft: "auto", color: C.muted, fontSize: 12 }}>
          {filtered.length.toLocaleString()} events total
          {totalPages > 1 && ` — page ${page + 1} of ${totalPages}`}
        </span>
      </div>

      {/* Table */}
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, overflow: "hidden", marginBottom: 16 }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: `1px solid ${C.border}` }}>
              {["Event ID", "Analysis Date", "Prediction", "Isolation Score", "Confidence"].map(h => (
                <th key={h} style={{
                  padding: "14px 20px", textAlign: "left", color: C.muted,
                  fontSize: 11, letterSpacing: 1, textTransform: "uppercase", fontWeight: 600
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginated.length > 0 ? paginated.map((r) => (
              <tr key={r.event_id} style={{
                borderBottom: `1px solid ${C.border}`,
                background: r.prediction === "anomaly" ? "#f43f5e08" : "transparent"
              }}>
                {/* Event ID */}
                <td style={{ padding: "12px 20px", color: C.muted, fontSize: 12, fontFamily: "monospace" }}>
                  #{String(r.event_id).padStart(4, "0")}
                </td>

                {/* Analysis Date — renamed from Timestamp */}
                <td style={{ padding: "12px 20px", color: C.muted, fontSize: 11 }}>
                  {new Date(r.timestamp).toLocaleString()}
                  <span style={{ display: "block", fontSize: 10, color: "#555", marginTop: 2 }}>
                    batch analysis
                  </span>
                </td>

                {/* Prediction badge */}
                <td style={{ padding: "12px 20px" }}>
                  <Badge label={r.prediction} type={r.prediction} />
                </td>

                {/* Isolation Score — fixed colour logic + tooltip */}
                <td style={{ padding: "12px 20px" }}>
                  <span style={{
                    fontFamily: "monospace", fontSize: 13,
                    color: scoreColor(r.anomaly_score, r.prediction),
                    fontWeight: 700
                  }}>
                    {r.anomaly_score.toFixed(4)}
                  </span>
                  <span style={{ display: "block", fontSize: 10, color: C.muted, marginTop: 2 }}>
                    {scoreLabel(r.anomaly_score, r.prediction)}
                  </span>
                </td>

                {/* Confidence bar */}
                <td style={{ padding: "12px 20px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div style={{ width: 60, height: 5, background: C.border, borderRadius: 4, overflow: "hidden" }}>
                      <div style={{
                        width: `${(r.confidence * 100).toFixed(0)}%`,
                        height: "100%", background: C.accent, borderRadius: 4
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

      {/* Pagination controls */}
      {totalPages > 1 && (
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 12 }}>
          <button
            onClick={() => setPage(0)}
            disabled={page === 0}
            style={{
              background: page === 0 ? C.border : C.surface,
              color: page === 0 ? C.muted : C.text,
              border: `1px solid ${C.border}`, borderRadius: 6,
              padding: "6px 12px", cursor: page === 0 ? "not-allowed" : "pointer",
              fontSize: 12, fontFamily: "inherit"
            }}>« First</button>

          <button
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
            style={{
              background: page === 0 ? C.border : C.surface,
              color: page === 0 ? C.muted : C.text,
              border: `1px solid ${C.border}`, borderRadius: 6,
              padding: "6px 12px", cursor: page === 0 ? "not-allowed" : "pointer",
              fontSize: 12, fontFamily: "inherit"
            }}>‹ Prev</button>

          {/* Page number buttons — show 5 around current */}
          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
            const start = Math.max(0, Math.min(page - 2, totalPages - 5));
            const p = start + i;
            return (
              <button key={p} onClick={() => setPage(p)} style={{
                background: p === page ? C.accent : C.surface,
                color:      p === page ? C.bg : C.muted,
                border: `1px solid ${p === page ? C.accent : C.border}`,
                borderRadius: 6, padding: "6px 12px",
                cursor: "pointer", fontSize: 12, fontFamily: "inherit",
                fontWeight: p === page ? 700 : 400,
              }}>{p + 1}</button>
            );
          })}

          <button
            onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
            disabled={page === totalPages - 1}
            style={{
              background: page === totalPages - 1 ? C.border : C.surface,
              color: page === totalPages - 1 ? C.muted : C.text,
              border: `1px solid ${C.border}`, borderRadius: 6,
              padding: "6px 12px",
              cursor: page === totalPages - 1 ? "not-allowed" : "pointer",
              fontSize: 12, fontFamily: "inherit"
            }}>Next ›</button>

          <button
            onClick={() => setPage(totalPages - 1)}
            disabled={page === totalPages - 1}
            style={{
              background: page === totalPages - 1 ? C.border : C.surface,
              color: page === totalPages - 1 ? C.muted : C.text,
              border: `1px solid ${C.border}`, borderRadius: 6,
              padding: "6px 12px",
              cursor: page === totalPages - 1 ? "not-allowed" : "pointer",
              fontSize: 12, fontFamily: "inherit"
            }}>Last »</button>

          <span style={{ color: C.muted, fontSize: 11 }}>
            Showing {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, filtered.length)} of {filtered.length.toLocaleString()}
          </span>
        </div>
      )}
    </>
  );
}