import { Moon, Sun } from "lucide-react";
import { GpuStatusBadge } from "./GpuStatusBadge";

interface Props {
  dark: boolean;
  onToggleDark: () => void;
}

export function TopBar({ dark, onToggleDark }: Props) {
  return (
    <header className="h-14 border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-950/80 backdrop-blur flex items-center justify-between px-6 sticky top-0 z-10">
      <div className="flex items-center gap-4">
        <GpuStatusBadge />
      </div>
      <button
        onClick={onToggleDark}
        className="p-2 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title={dark ? "切换亮色模式" : "切换暗色模式"}
      >
        {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
      </button>
    </header>
  );
}
