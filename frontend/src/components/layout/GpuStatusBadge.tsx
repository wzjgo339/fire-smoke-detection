import { useEffect, useState } from "react";
import { Cpu } from "lucide-react";
import { fetchHealth } from "../../services/healthApi";

export function GpuStatusBadge() {
  const [info, setInfo] = useState<{ used: number; total: number; pct: number; name: string } | null>(null);

  useEffect(() => {
    let active = true;
    const poll = async () => {
      try {
        const h = await fetchHealth();
        if (active && h.gpu?.name) {
          setInfo({
            name: h.gpu.name,
            used: h.gpu.memory_used_mb,
            total: h.gpu.memory_total_mb,
            pct: h.gpu.utilization_pct ?? 0,
          });
        }
      } catch { /* ignore */ }
    };
    poll();
    const iv = setInterval(poll, 15000);
    return () => { active = false; clearInterval(iv); };
  }, []);

  if (!info) return null;

  return (
    <div className="flex items-center gap-2 text-xs text-gray-400 dark:text-gray-500">
      <Cpu className="w-3.5 h-3.5" />
      <span>{info.used}/{info.total} MB</span>
      <span className="w-1.5 h-1.5 rounded-full bg-green-500" title="GPU OK" />
    </div>
  );
}
