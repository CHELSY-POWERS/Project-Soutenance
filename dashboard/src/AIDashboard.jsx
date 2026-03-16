import { useState, useEffect, useCallback } from "react";
import useSocket from "./hooks/useSocket";
import LiveBadge from "./components/LiveBadge";
import api from "./services/api";
import { C, Badge } from "./components/UI";
import OverviewTab  from "./components/tabs/OverviewTab";
import ResultsTab   from "./components/tabs/ResultsTab";
import MetricsTab   from "./components/tabs/MetricsTab";
import LogsTab      from "./components/tabs/LogsTab";
import NetworkTab  from "./components/tabs/NetworkTab";
import TestsTab    from "./components/tabs/TestsTab";

const TABS = ["overview", "results", "metrics", "logs", "network", "tests"];

export default function AIDashboard() {
  const [summary,       setSummary]       = useState(null);
  const [results,       setResults]       = useState([]);
  const [statistics,    setStatistics]    = useState(null);
  const [logAlerts,     setLogAlerts]     = useState(null);
  const [sqliAlerts,    setSQLiAlerts]    = useState(null);
  const [networkAlerts, setNetworkAlerts] = useState(null);
  const [filter,        setFilter]        = useState("all");
  const [loading,       setLoading]       = useState(true);
  const [scanning,      setScanning]      = useState(false);

  // WebSocket callbacks
  const handleLiveLogAlert = useCallback((alert, bulk) => {
    if (bulk) {
      loadData();
    } else if (alert) {
      setLogAlerts(prev => [alert, ...prev].slice(0, 200));
    }
  }, []);

  const handleLiveNetworkAlert = useCallback((alert) => {
    if (alert) {
      setNetworkAlerts(prev => ({
        ...prev,
        total: (prev.total || 0) + 1,
        alerts: [alert, ...(prev.alerts || [])].slice(0, 100),
      }));
    }
  }, []);

  const { connected, lastAlertTime, alertCount } = useSocket({
    onLogAlert:     handleLiveLogAlert,
    onNetworkAlert: handleLiveNetworkAlert,
  });
  const [error,         setError]         = useState(null);
  const [activeTab,     setActiveTab]     = useState("overview");

  useEffect(() => { loadData(); }, []);

  // Fast polling for live alerts (every 5s backup to WebSocket)
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const logData = await api.getLogAlerts();
        setLogAlerts(logData.alerts || []);
      } catch(e) {}
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const interval = setInterval(async () => {
      if (activeTab === 'network') {
        const data = await api.getNetworkAlerts().catch(() => null);
        setNetworkAlerts(data);
      }
    }, 30000);
    return () => clearInterval(interval);
  }, [activeTab]);

  useEffect(() => { if (summary) loadResults(); }, [filter, summary]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [summaryData, statsData, logData, sqliData, networkData] = await Promise.all([
        api.getDashboardSummary(),
        api.getStatistics().catch(() => null),
        api.getLogAlerts().catch(() => null),
        api.getSQLiAlerts().catch(() => null),
        api.getNetworkAlerts().catch(() => null),
      ]);
      setSummary(summaryData);
      setStatistics(statsData);
      setLogAlerts(logData);
      setSQLiAlerts(sqliData);
      setNetworkAlerts(networkData);
      setLoading(false);
    } catch (err) {
      setError('Cannot connect to backend. Make sure Flask is running on http://localhost:5000');
      setLoading(false);
    }
  };

  const loadResults = async () => {
    try {
      const data = await api.getDetectionResults(1, 22544, filter);
      setResults(data.results || []);
    } catch (err) {
      console.error('Failed to load results:', err);
    }
  };

  const handleLogScan = async () => {
    setScanning(true);
    try {
      await api.triggerLogScan();
      setTimeout(async () => {
        const [logData, sqliData] = await Promise.all([
          api.getLogAlerts().catch(() => null),
          api.getSQLiAlerts().catch(() => null),
        ]);
        setLogAlerts(logData);
        setSQLiAlerts(sqliData);
        setScanning(false);
      }, 8000);
    } catch (err) {
      setScanning(false);
    }
  };

  if (loading) return (
    <div style={{ minHeight: "100vh", background: C.bg, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ textAlign: "center" }}>
        <div style={{ width: 48, height: 48, border: `3px solid ${C.border}`, borderTop: `3px solid ${C.accent}`, borderRadius: "50%", margin: "0 auto 16px", animation: "spin 1s linear infinite" }} />
        <p style={{ color: C.muted, fontFamily: "monospace" }}>Connecting to AI Backend…</p>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );

  if (error) return (
    <div style={{ minHeight: "100vh", background: C.bg, display: "flex", alignItems: "center", justifyContent: "center", padding: 40 }}>
      <div style={{ background: C.surface, border: `2px solid ${C.red}`, borderRadius: 12, padding: 40, maxWidth: 600, textAlign: "center" }}>
        <div style={{ fontSize: 48, marginBottom: 20 }}>⚠️</div>
        <h2 style={{ color: C.text, margin: "0 0 16px" }}>Backend Connection Failed</h2>
        <p style={{ color: C.muted, marginBottom: 24 }}>{error}</p>
        <div style={{ background: C.bg, padding: 16, borderRadius: 8, fontFamily: "monospace", fontSize: 13, color: C.accent, textAlign: "left" }}>
          <div>1. cd ~/ai-ids-project/backend</div>
          <div>2. source ../venv/bin/activate</div>
          <div>3. python app.py</div>
        </div>
        <button onClick={loadData} style={{ marginTop: 24, background: C.accent, color: C.bg, border: "none", padding: "12px 32px", borderRadius: 8, cursor: "pointer", fontWeight: 700, fontSize: 14 }}>
          Retry Connection
        </button>
      </div>
    </div>
  );

  return (
    <div style={{ minHeight: "100vh", background: C.bg, color: C.text, fontFamily: "'IBM Plex Mono', 'Courier New', monospace" }}>

      {/* Top Bar */}
      <header style={{ background: C.surface, borderBottom: `1px solid ${C.border}`, padding: "0 32px", display: "flex", alignItems: "center", justifyContent: "space-between", height: 60 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 10, height: 10, borderRadius: "50%", background: C.green, boxShadow: `0 0 8px ${C.green}`, animation: "pulse 2s ease-in-out infinite" }} />
          <span style={{ color: C.accent, fontWeight: 800, fontSize: 15, letterSpacing: 2 }}>AI-IDS</span>
          <span style={{ color: C.muted, fontSize: 12 }}>Autonomous Intrusion Detection System</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <span style={{ color: C.muted, fontSize: 11 }}>{summary.model.algorithm}</span>
          <LiveBadge connected={connected} lastAlertTime={lastAlertTime} alertCount={alertCount} />
        </div>
      </header>

      {/* Tabs */}
      <div style={{ background: C.surface, borderBottom: `1px solid ${C.border}`, padding: "0 32px", display: "flex", gap: 4 }}>
        {TABS.map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)} style={{
            background: "none", border: "none",
            borderBottom: activeTab === tab ? `2px solid ${C.accent}` : "2px solid transparent",
            color: activeTab === tab ? C.accent : C.muted,
            padding: "14px 20px 12px", cursor: "pointer", fontSize: 12,
            letterSpacing: 1, textTransform: "uppercase", fontFamily: "inherit", transition: "color .2s",
          }}>{tab}</button>
        ))}
      </div>

      {/* Tab Content */}
      <main style={{ padding: "32px", maxWidth: 1200, margin: "0 auto" }}>
        {activeTab === "overview" && <OverviewTab  summary={summary}     statistics={statistics} />}
        {activeTab === "results"  && <ResultsTab   results={results}     filter={filter} setFilter={setFilter} />}
        {activeTab === "metrics"  && <MetricsTab   summary={summary} />}
        {activeTab === "logs"     && <LogsTab       logAlerts={logAlerts} sqliAlerts={sqliAlerts} scanning={scanning} onScan={handleLogScan} />}
        {activeTab === "network"  && <NetworkTab  networkAlerts={networkAlerts} />}
        {activeTab === "tests"    && <TestsTab    onAttackComplete={loadData} />}
      </main>

      <style>{`
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
      `}</style>
    </div>
  );
}
