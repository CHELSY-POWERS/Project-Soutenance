import { useState, useEffect } from 'react';
import { C } from './UI';

export default function LiveBadge({ connected, lastAlertTime, alertCount }) {
  const [pulse, setPulse] = useState(false);

  useEffect(() => {
    if (!lastAlertTime) return;
    setPulse(true);
    const t = setTimeout(() => setPulse(false), 2000);
    return () => clearTimeout(t);
  }, [lastAlertTime]);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div style={{
        width: 8, height: 8, borderRadius: '50%',
        background: connected ? C.green : C.red,
        boxShadow: connected ? `0 0 ${pulse ? '12px' : '6px'} ${C.green}` : 'none',
        transition: 'box-shadow 0.3s',
      }} />
      <span style={{
        fontSize: 11, fontWeight: 700, letterSpacing: 1,
        color: connected ? C.green : C.red, textTransform: 'uppercase',
      }}>
        {connected ? 'LIVE' : 'OFFLINE'}
      </span>
      {pulse && (
        <span style={{ fontSize: 10, color: '#fbbf24', fontWeight: 700 }}>
          ⚡ New alert!
        </span>
      )}
      {alertCount > 0 && (
        <span style={{
          background: '#f43f5e22', color: '#f43f5e',
          border: '1px solid #f43f5e44', borderRadius: 10,
          padding: '1px 7px', fontSize: 10, fontWeight: 700,
        }}>
          {alertCount} live
        </span>
      )}
    </div>
  );
}
