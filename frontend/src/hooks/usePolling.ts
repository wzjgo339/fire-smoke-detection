import { useEffect, useRef } from "react";

export function usePolling(callback: () => Promise<boolean | void>, intervalMs: number, enabled: boolean) {
  const savedCallback = useRef(callback);
  savedCallback.current = callback;

  useEffect(() => {
    if (!enabled) return;
    let active = true;
    const tick = async () => {
      if (!active) return;
      const done = await savedCallback.current();
      if (done || !active) return;
      setTimeout(tick, intervalMs);
    };
    tick();
    return () => { active = false; };
  }, [intervalMs, enabled]);
}
