const API_BASE = 'http://localhost:5000/api';

const api = {
  getDashboardSummary: async () => {
    const res = await fetch(`${API_BASE}/dashboard/summary`);
    if (!res.ok) throw new Error('Backend not reachable');
    return res.json();
  },
  getDetectionResults: async (page = 1, perPage = 20, filter = 'all') => {
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

export default api;
