const API_BASE = 'http://localhost:5000/api';

const api = {
  getDashboardSummary: async () => {
    const res = await fetch(`${API_BASE}/dashboard/summary`);
    if (!res.ok) throw new Error('Backend not reachable');
    return res.json();
  },
  getDetectionResults: async (page = 1, perPage = 22544, filter = 'all') => {
    const res = await fetch(`${API_BASE}/detection/results?page=${page}&per_page=${perPage}&filter=${filter}`);
    if (!res.ok) throw new Error('Failed to fetch results');
    return res.json();
  },
  getStatistics: async () => {
    const res = await fetch(`${API_BASE}/statistics`);
    if (!res.ok) throw new Error('Failed to fetch statistics');
    return res.json();
  },
  getLogAlerts: async () => {
    const res = await fetch(`${API_BASE}/logs/alerts`);
    if (!res.ok) throw new Error('Failed to fetch log alerts');
    return res.json();
  },
  triggerLogScan: async () => {
    const res = await fetch(`${API_BASE}/logs/scan`, { method: 'POST' });
    return res.json();
  },
  getSQLiAlerts: async () => {
    const res = await fetch(`${API_BASE}/logs/sqli`);
    if (!res.ok) throw new Error('Failed to fetch SQLi alerts');
    return res.json();
  },
  getNetworkAlerts: async () => {
    const res = await fetch(`${API_BASE}/network/alerts`);
    if (!res.ok) throw new Error('Failed to fetch network alerts');
    return res.json();
  },
};

export const testApi = {
  simulateAttack: async (attackType) => {
    const res = await fetch(`${API_BASE}/test/simulate-attack`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ attack_type: attackType })
    });
    return res.json();
  },
  startNetworkMonitor: async (iface = 'wlp4s0') => {
    const res = await fetch(`${API_BASE}/test/network-monitor/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ interface: iface })
    });
    return res.json();
  },
  stopNetworkMonitor: async () => {
    const res = await fetch(`${API_BASE}/test/network-monitor/stop`, { method: 'POST' });
    return res.json();
  },
  getMonitorStatus: async () => {
    const res = await fetch(`${API_BASE}/test/network-monitor/status`);
    return res.json();
  },
  clearAlerts: async () => {
    const res = await fetch(`${API_BASE}/test/clear-alerts`, { method: 'POST' });
    return res.json();
  },
};

export default api;
