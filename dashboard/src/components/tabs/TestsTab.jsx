import { useState, useEffect } from "react";
import { C, KPI } from "../UI";
import { testApi } from "../../services/api";

const ATTACKS = [
  { id: 'sqli',       label: 'SQL Injection',  icon: '💉', desc: 'Simulates boolean bypass, UNION extraction, time-based blind and schema enumeration attacks in Apache logs', color: C.red    },
  { id: 'portscan',   label: 'Port Scan',       icon: '🔍', desc: 'Scans common ports (SSH, HTTP, MySQL, Redis) on localhost to trigger port scan detection',                  color: C.yellow },
  { id: 'bruteforce', label: 'Brute Force',     icon: '🔨', desc: 'Simulates 6 failed SSH login attempts to trigger brute force detection in auth.log',                       color: C.purple },
  { id: 'ping_flood', label: 'Ping Flood',      icon: '🌊', desc: 'Sends 25 rapid ICMP packets to trigger ICMP flood detection on the network monitor',                       color: C.accent },
];

export default function TestsTab({ onAttackComplete }) {
  const [running,        setRunning]        = useState(null);
  const [results,        setResults]        = useState([]);
  const [monitorRunning, setMonitorRunning] = useState(false);
  const [monitorLoading, setMonitorLoading] = useState(false);
  const [clearing,       setClearing]       = useState(false);
  const [interface_,     setInterface]      = useState('wlp4s0');

  // Check monitor status on mount
  useEffect(() => {
    checkMonitorStatus();
    const interval = setInterval(checkMonitorStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkMonitorStatus = async () => {
    try {
      const data = await testApi.getMonitorStatus();
      setMonitorRunning(data.running);
    } catch {}
  };

  const handleAttack = async (attackId) => {
    setRunning(attackId);
    const attack = ATTACKS.find(a => a.id === attackId);

    try {
      addLog(`🚀 Launching ${attack.label} simulation...`, 'info');
      const result = await testApi.simulateAttack(attackId);

      if (result.success) {
        addLog(`✅ ${attack.label} completed!`, 'success');
        result.details?.forEach(d => addLog(`   → ${d}`, 'detail'));
        if (result.next_step) addLog(`💡 Next: ${result.next_step}`, 'info');
        addLog(`⏳ Refreshing alerts in 3 seconds...`, 'info');

        setTimeout(() => {
          onAttackComplete?.();
          addLog(`🔄 Alerts refreshed — check Logs and Network tabs!`, 'success');
        }, 3000);
      } else {
        addLog(`❌ Failed: ${result.error}`, 'error');
      }
    } catch (e) {
      addLog(`❌ Error: ${e.message}`, 'error');
    } finally {
      setRunning(null);
    }
  };

  const handleMonitorToggle = async () => {
    setMonitorLoading(true);
    try {
      if (monitorRunning) {
        const result = await testApi.stopNetworkMonitor();
        addLog(result.success ? '🛑 Network monitor stopped' : `❌ ${result.message}`, result.success ? 'info' : 'error');
      } else {
        addLog(`🌐 Starting network monitor on ${interface_}...`, 'info');
        const result = await testApi.startNetworkMonitor(interface_);
        addLog(result.success ? `✅ Monitor started (PID: ${result.pid})` : `❌ ${result.error}`, result.success ? 'success' : 'error');
        if (result.success) addLog('👂 Now listening for suspicious traffic...', 'detail');
      }
      await checkMonitorStatus();
    } catch (e) {
      addLog(`❌ Error: ${e.message}`, 'error');
    } finally {
      setMonitorLoading(false);
    }
  };

  const handleClearAlerts = async () => {
    setClearing(true);
    try {
      const result = await testApi.clearAlerts();
      addLog(result.success ? '🗑️ All network alerts cleared — ready for fresh demo!' : `❌ ${result.error}`, result.success ? 'success' : 'error');
      onAttackComplete?.();
    } catch (e) {
      addLog(`❌ Error: ${e.message}`, 'error');
    } finally {
      setClearing(false);
    }
  };

  const addLog = (msg, type = 'info') => {
    setResults(prev => [{
      msg,
      type,
      time: new Date().toLocaleTimeString()
    }, ...prev].slice(0, 50));
  };

  const logColor = { success: C.green, error: C.red, info: C.accent, detail: C.muted };

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ margin: '0 0 6px', color: C.text, fontSize: 18, fontWeight: 800 }}>🧪 Test & Simulation Panel</h2>
        <p style={{ margin: 0, color: C.muted, fontSize: 12 }}>
          Simulate real attacks from the browser — no terminal needed. Results appear live in Logs and Network tabs.
        </p>
      </div>

      {/* Network Monitor Control */}
      <div style={{ background: C.surface, border: `2px solid ${monitorRunning ? C.green : C.border}`, borderRadius: 12, padding: 24, marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{ width: 14, height: 14, borderRadius: '50%', background: monitorRunning ? C.green : C.muted, boxShadow: monitorRunning ? `0 0 10px ${C.green}` : 'none', transition: 'all 0.3s' }} />
            <div>
              <p style={{ margin: 0, color: C.text, fontWeight: 700, fontSize: 14 }}>Network Monitor</p>
              <p style={{ margin: 0, color: C.muted, fontSize: 11 }}>
                {monitorRunning ? '🟢 Running — capturing live network traffic' : '⚫ Stopped — not capturing traffic'}
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div>
              <p style={{ margin: '0 0 4px', color: C.muted, fontSize: 10, textTransform: 'uppercase' }}>Interface</p>
              <input
                value={interface_}
                onChange={e => setInterface(e.target.value)}
                disabled={monitorRunning}
                style={{ background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6, padding: '6px 10px', color: C.text, fontFamily: 'monospace', fontSize: 12, width: 100 }}
              />
            </div>
            <button onClick={handleMonitorToggle} disabled={monitorLoading} style={{
              background: monitorRunning ? '#f43f5e22' : '#22d3a022',
              color: monitorRunning ? C.red : C.green,
              border: `1px solid ${monitorRunning ? C.red : C.green}`,
              borderRadius: 8, padding: '10px 24px', cursor: monitorLoading ? 'not-allowed' : 'pointer',
              fontWeight: 700, fontSize: 13, fontFamily: 'inherit', transition: 'all 0.2s',
            }}>
              {monitorLoading ? '⏳ ...' : monitorRunning ? '🛑 Stop Monitor' : '▶️ Start Monitor'}
            </button>
            <button onClick={handleClearAlerts} disabled={clearing} style={{
              background: 'transparent', color: C.muted,
              border: `1px solid ${C.border}`, borderRadius: 8,
              padding: '10px 16px', cursor: 'pointer', fontSize: 12, fontFamily: 'inherit',
            }}>
              {clearing ? '⏳' : '🗑️ Clear Alerts'}
            </button>
          </div>
        </div>
      </div>

      {/* Attack Buttons */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16, marginBottom: 24 }}>
        {ATTACKS.map(attack => (
          <div key={attack.id} style={{
            background: C.surface,
            border: `1px solid ${running === attack.id ? attack.color : C.border}`,
            borderRadius: 12, padding: 24,
            transition: 'border-color 0.2s',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
              <div>
                <p style={{ margin: '0 0 4px', fontSize: 24 }}>{attack.icon}</p>
                <p style={{ margin: 0, color: C.text, fontWeight: 700, fontSize: 14 }}>{attack.label}</p>
              </div>
              {running === attack.id && (
                <div style={{ width: 20, height: 20, border: `2px solid ${attack.color}`, borderTop: '2px solid transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
              )}
            </div>
            <p style={{ margin: '0 0 16px', color: C.muted, fontSize: 11, lineHeight: 1.6 }}>{attack.desc}</p>
            <button
              onClick={() => handleAttack(attack.id)}
              disabled={running !== null}
              style={{
                background: running === attack.id ? `${attack.color}33` : `${attack.color}22`,
                color: attack.color,
                border: `1px solid ${attack.color}55`,
                borderRadius: 8, padding: '10px 20px',
                cursor: running !== null ? 'not-allowed' : 'pointer',
                fontWeight: 700, fontSize: 12, fontFamily: 'inherit',
                width: '100%', transition: 'all 0.2s',
                opacity: running !== null && running !== attack.id ? 0.5 : 1,
              }}
            >
              {running === attack.id ? '⏳ Running...' : `Launch ${attack.label}`}
            </button>
          </div>
        ))}
      </div>

      {/* Live Log */}
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, overflow: 'hidden' }}>
        <div style={{ padding: '14px 20px', borderBottom: `1px solid ${C.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ color: C.text, fontSize: 13, letterSpacing: 1, textTransform: 'uppercase' }}>📋 Live Activity Log</span>
          <button onClick={() => setResults([])} style={{ background: 'none', border: 'none', color: C.muted, cursor: 'pointer', fontSize: 11 }}>Clear</button>
        </div>
        <div style={{ padding: 16, minHeight: 200, maxHeight: 300, overflowY: 'auto', fontFamily: 'monospace' }}>
          {results.length === 0 ? (
            <p style={{ color: C.muted, fontSize: 12, textAlign: 'center', marginTop: 60 }}>
              Launch an attack simulation to see live activity here...
            </p>
          ) : results.map((log, i) => (
            <div key={i} style={{ display: 'flex', gap: 12, marginBottom: 6 }}>
              <span style={{ color: C.muted, fontSize: 11, whiteSpace: 'nowrap' }}>{log.time}</span>
              <span style={{ color: logColor[log.type] || C.text, fontSize: 12 }}>{log.msg}</span>
            </div>
          ))}
        </div>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
