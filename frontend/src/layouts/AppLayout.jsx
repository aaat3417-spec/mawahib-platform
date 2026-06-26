import { useEffect, useState } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../hooks/useAuth.jsx";
import { api } from "../services/api";

const navItems = [
  ["Dashboard", "/", "D"],
  ["Tasks", "/tasks", "T"],
  ["Submissions", "/submissions", "S"],
  ["Leaderboard", "/leaderboard", "L"],
  ["Announcements", "/announcements", "A"],
  ["Profile", "/profile", "P"]
];

export default function AppLayout() {
  const { user, logout, isAdmin } = useAuth();
  const [dark, setDark] = useState(() => localStorage.getItem("mawahib_theme") === "dark");
  const [notifications, setNotifications] = useState([]);
  const location = useLocation();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("mawahib_theme", dark ? "dark" : "light");
  }, [dark]);

  useEffect(() => {
    api.get("/notifications").then(({ data }) => setNotifications(data)).catch(() => setNotifications([]));
  }, [location.pathname]);

  const unreadCount = notifications.filter((item) => !item.read_at).length;
  const mobileNavItems = isAdmin ? [...navItems, ["Admin", "/admin", "M"]] : navItems;

  async function markAllRead() {
    const unread = notifications.filter((item) => !item.read_at);
    if (unread.length === 0) {
      return;
    }
    setNotifications((items) => items.map((item) => (item.read_at ? item : { ...item, read_at: new Date().toISOString() })));
    await Promise.allSettled(unread.map((item) => api.patch(`/notifications/${item.id}/read`)));
  }

  return (
    <div className="min-h-screen bg-transparent pb-20 text-slate-900 dark:text-slate-100 lg:pb-0">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-72 border-r border-slate-200/80 bg-white/90 p-5 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90 lg:block">
        <Link to="/" className="block rounded-lg bg-gradient-to-br from-teal-700 to-emerald-600 p-4 text-white shadow-soft">
          <p className="text-sm font-semibold opacity-85">Mawahib</p>
          <p className="text-xl font-bold">Community Platform</p>
          <p className="mt-3 text-xs leading-5 text-teal-50">Tasks, teams, points, badges, and progress in one calm workspace.</p>
        </Link>
        <nav className="mt-8 space-y-1">
          {navItems.map(([label, to, initial]) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition ${
                  isActive
                    ? "bg-teal-50 text-teal-800 shadow-sm dark:bg-teal-500/15 dark:text-teal-200"
                    : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                }`
              }
            >
              <span className="grid h-8 w-8 place-items-center rounded-lg bg-white text-xs shadow-sm dark:bg-slate-900">{initial}</span>
              {label}
            </NavLink>
          ))}
          {isAdmin && (
            <NavLink
              to="/admin"
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition ${
                  isActive
                    ? "bg-teal-50 text-teal-800 shadow-sm dark:bg-teal-500/15 dark:text-teal-200"
                    : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                }`
              }
            >
              <span className="grid h-8 w-8 place-items-center rounded-lg bg-white text-xs shadow-sm dark:bg-slate-900">M</span>
              Admin Panel
            </NavLink>
          )}
        </nav>
        <div className="absolute inset-x-5 bottom-5 rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-900">
          <p className="text-sm font-semibold">{user?.full_name}</p>
          <p className="mt-1 text-xs capitalize text-slate-500 dark:text-slate-400">{user?.role?.replace("_", " ")}</p>
        </div>
      </aside>

      <div className="lg:pl-72">
        <header className="sticky top-0 z-10 border-b border-slate-200/80 bg-white/85 px-4 py-3 backdrop-blur dark:border-slate-800 dark:bg-slate-950/85 sm:px-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Mawahib workspace</p>
              <p className="font-semibold">Welcome, {user?.full_name?.split(" ")[0] || "member"}</p>
            </div>
            <div className="flex items-center gap-2 overflow-x-auto">
              <button
                className="hidden rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold text-slate-600 transition hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 sm:inline-flex"
                type="button"
                onClick={markAllRead}
                title="Mark notifications as read"
              >
                {unreadCount} unread
              </button>
              <button className="btn-secondary" onClick={() => setDark((value) => !value)}>
                {dark ? "Light" : "Dark"}
              </button>
              <button className="btn-secondary" onClick={logout}>
                Logout
              </button>
            </div>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
      <nav className="fixed inset-x-3 bottom-3 z-30 flex gap-1 overflow-x-auto rounded-lg border border-slate-200 bg-white/95 p-1 shadow-soft backdrop-blur dark:border-slate-800 dark:bg-slate-950/95 lg:hidden">
        {mobileNavItems.map(([label, to, initial]) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex min-w-[4.25rem] flex-1 flex-col items-center justify-center rounded-md px-1 py-2 text-[10px] font-semibold transition ${
                isActive ? "bg-teal-50 text-teal-800 dark:bg-teal-500/15 dark:text-teal-200" : "text-slate-500 dark:text-slate-400"
              }`
            }
          >
            <span className="text-sm">{initial}</span>
            <span className="mt-0.5 max-w-full truncate">{label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
