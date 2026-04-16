import { useState, useEffect, useRef, useCallback } from "react";

const WS_BASE = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

export function useWebSocket(caseId) {
  const [status, setStatus] = useState(null);
  const [isEmergency, setIsEmergency] = useState(false);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const pingRef = useRef(null);

  const connect = useCallback(() => {
    if (!caseId) return;
    const ws = new WebSocket(`${WS_BASE}/ws/cases/${caseId}/status`);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      pingRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) ws.send("ping");
      }, 25000);
    };

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.type === "update") {
          setStatus(msg.data);
          if (typeof msg.data === "string" && msg.data.includes("EMERGENCY")) {
            setIsEmergency(true);
          }
        }
      } catch {}
    };

    ws.onclose = () => {
      setConnected(false);
      clearInterval(pingRef.current);
      // Reconnect after 3s
      setTimeout(connect, 3000);
    };

    ws.onerror = () => ws.close();
  }, [caseId]);

  useEffect(() => {
    connect();
    return () => {
      clearInterval(pingRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { status, isEmergency, connected };
}
