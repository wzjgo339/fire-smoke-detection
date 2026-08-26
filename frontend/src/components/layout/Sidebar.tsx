import { NavLink } from "react-router-dom";
import { LayoutDashboard, Image, Video, History, Flame } from "lucide-react";
import { cn } from "../../lib/utils";

const links = [
  { to: "/", icon: LayoutDashboard, label: "仪表盘" },
  { to: "/detect/image", icon: Image, label: "图像检测" },
  { to: "/detect/video", icon: Video, label: "视频检测" },
  { to: "/history", icon: History, label: "历史记录" },
];

export function Sidebar() {
  return (
    <aside className="w-60 border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 flex flex-col h-screen sticky top-0">
      <div className="flex items-center gap-2 px-5 py-5 border-b border-gray-200 dark:border-gray-800">
        <Flame className="w-7 h-7 text-fire" />
        <div>
          <h1 className="text-sm font-bold text-gray-900 dark:text-white leading-tight">Fire Detection</h1>
          <p className="text-[10px] text-gray-400 dark:text-gray-500">YOLOv8m · TensorRT</p>
        </div>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white"
                  : "text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/50 hover:text-gray-700 dark:hover:text-gray-300"
              )
            }
          >
            <Icon className="w-4.5 h-4.5" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-800">
        <p className="text-[10px] text-gray-400 dark:text-gray-500">Fire & Smoke Detection v1.0</p>
      </div>
    </aside>
  );
}
