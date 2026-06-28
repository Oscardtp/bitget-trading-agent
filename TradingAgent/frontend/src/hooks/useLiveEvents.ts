"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { LiveEvent } from "@/lib/types";
import { fetchEvents } from "@/lib/api";

const MAX_EVENTS = 100;

export function useLiveEvents() {
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Load historical events on mount
  useEffect(() => {
    let active = true;
    const loadHistory = async () => {
      try {
        const historical = await fetchEvents(MAX_EVENTS);
        if (active && historical.length > 0) {
          // Convert EventResponse to LiveEvent format
          const mapped: LiveEvent[] = historical.map((e) => ({
            event_type: e.event_type,
            timestamp: e.timestamp,
            trade_id: e.trade_id,
            data: e.data,
          }));
          setEvents(mapped);
        }
      } catch {
        // Silent fail - will retry on next mount
      }
    };
    loadHistory();
    return () => { active = false; };
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket("ws://localhost:8000/ws/live");

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onmessage = (e) => {
      try {
        const data: LiveEvent = JSON.parse(e.data);
        setEvents((prev) => {
          const next = [data, ...prev];
          // FIFO: keep only last MAX_EVENTS
          return next.slice(0, MAX_EVENTS);
        });
      } catch {}
    };

    ws.onclose = () => {
      setIsConnected(false);
      wsRef.current = null;
      reconnectTimer.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { events, isConnected };
}
