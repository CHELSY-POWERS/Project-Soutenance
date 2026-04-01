import { useEffect, useRef, useState, useCallback } from 'react';
import { io } from 'socket.io-client';

const SOCKET_URL = 'http://localhost:5000';

export default function useSocket({ onLogAlert, onNetworkAlert, onSystemStatus }) {
  const socketRef           = useRef(null);
  const [connected,     setConnected]     = useState(false);
  const [lastAlertTime, setLastAlertTime] = useState(null);
  const [alertCount,    setAlertCount]    = useState(0);

  const connect = useCallback(() => {
    if (socketRef.current?.connected) return;
    const socket = io(SOCKET_URL, {
      transports: ['polling', 'websocket'],  // polling first, then upgrade
      reconnection: true,
      reconnectionDelay: 2000,
      reconnectionAttempts: 10,
      timeout: 10000,
    });
    socket.on('connect', () => {
      console.log('[WS] Connected! Transport:', socket.io.engine.transport.name);
      setConnected(true);
    });
    socket.on('disconnect', (reason) => {
      console.log('[WS] Disconnected:', reason);
      setConnected(false);
    });
    socket.on('connect_error', (err) => {
      console.log('[WS] Connection error:', err.message);
    });
    socket.on('new_live_alert', (data) => {
      console.log('[WS] Live alert:', data.message);
      setLastAlertTime(new Date());
      setAlertCount(c => c + 1);
      if (data.type === 'log' || data.type === 'sqli') onLogAlert?.(data.alert);
      else if (data.type === 'network') onNetworkAlert?.(data.alert);
    });
    socket.on('new_log_alerts', (data) => {
      console.log('[WS] Bulk scan:', data.total, 'alerts');
      setLastAlertTime(new Date());
      setAlertCount(c => c + data.total);
      onLogAlert?.(null, data);
    });
    socket.on('system_status', (data) => { onSystemStatus?.(data); });
    socketRef.current = socket;
  }, [onLogAlert, onNetworkAlert, onSystemStatus]);

  useEffect(() => {
    connect();
    return () => { socketRef.current?.disconnect(); };
  }, [connect]);

  const resetAlertCount = () => setAlertCount(0);
  return { connected, lastAlertTime, alertCount, resetAlertCount, socket: socketRef.current };
}
