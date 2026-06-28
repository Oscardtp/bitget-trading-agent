"use client";

import { useState, useEffect } from "react";
import { HealthResponse } from "@/lib/types";
import { fetchHealth } from "@/lib/api";

export function useHealth() {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    let active = true;
    const poll = async () => {
      try {
        const h = await fetchHealth();
        if (active) setHealth(h);
      } catch {}
    };
    poll();
    const interval = setInterval(poll, 10000);
    return () => { active = false; clearInterval(interval); };
  }, []);

  return health;
}
