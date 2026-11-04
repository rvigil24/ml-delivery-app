"use client";

import { useEffect } from "react";

/** Lecturas periódicas, sin solaparse ni continuar tras cambiar de vista. */
export function useLiveRefresh(refresh: (signal: AbortSignal) => Promise<void>, enabled = true, immediate = false) {
  useEffect(() => {
    if (!enabled) return;
    let running = false;
    let disposed = false;
    let controller: AbortController | null = null;
    async function run() {
      if (disposed || running || document.hidden) return;
      running = true; controller = new AbortController();
      try { await refresh(controller.signal); }
      finally { running = false; }
    }
    const tick = () => { void run(); };
    const visibility = () => { if (document.hidden) controller?.abort(); else tick(); };
    const timer = window.setInterval(tick, 5000);
    document.addEventListener("visibilitychange", visibility);
    window.addEventListener("focus", tick);
    if (immediate) tick();
    return () => { disposed = true; controller?.abort(); window.clearInterval(timer); document.removeEventListener("visibilitychange", visibility); window.removeEventListener("focus", tick); };
  }, [refresh, enabled, immediate]);
}
