import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import StatCard from "../components/StatCard.jsx";
import { api } from "../services/api";

export default function Dashboard() {
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {
    api.get("/statistics/dashboard").then(({ data }) => setDashboard(data));
  }, []);

  if (!dashboard) {
    return <div className="panel animate-pulse p-6">Loading dashboard...</div>;
  }

  const weeklyTotal = dashboard.weekly_progress.reduce((sum, day) => sum + day.submissions, 0);
  const maxSubmissions = Math.max(1, ...dashboard.weekly_progress.map((day) => day.submissions));

  return (
    <>
      <section className="mb-6 overflow-hidden rounded-lg bg-gradient-to-br from-teal-800 via-teal-700 to-emerald-600 p-5 text-white shadow-soft sm:p-7">
        <div className="grid gap-6 lg:grid-cols-[1fr_220px] lg:items-center">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-100">Student command center</p>
            <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">{dashboard.welcome_message}</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-teal-50 sm:text-base">
              Stay close to deadlines, keep your submissions moving, and build a portfolio that tells the story of your growth.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link className="rounded-lg bg-white px-4 py-2 text-sm font-bold text-teal-800 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg" to="/tasks">
                Continue tasks
              </Link>
              <Link className="rounded-lg border border-white/30 px-4 py-2 text-sm font-bold text-white transition hover:-translate-y-0.5 hover:bg-white/10" to="/leaderboard">
                View rankings
              </Link>
            </div>
          </div>
          <div className="rounded-lg border border-white/20 bg-white/10 p-5 text-center backdrop-blur">
            <ProgressRing value={dashboard.progress_percentage} />
            <p className="mt-3 text-sm font-semibold text-teal-50">Required task progress</p>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total points" value={dashboard.total_points} detail="Accepted work and bonuses" icon="P" accent="teal" trend={weeklyTotal ? `${weeklyTotal} this week` : undefined} />
        <StatCard label="Current rank" value={dashboard.current_rank ? `#${dashboard.current_rank}` : "Unranked"} detail="All-time student ranking" icon="R" accent="amber" />
        <StatCard label="Completed tasks" value={dashboard.completed_tasks} detail="Accepted submissions" icon="C" accent="sky" />
        <StatCard label="Progress" value={`${dashboard.progress_percentage}%`} detail="Required completion" icon="%" accent="rose" />
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="panel p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="label">Activity</p>
              <h2 className="mt-1 font-bold">Weekly progress</h2>
            </div>
            <span className="rounded-full bg-teal-50 px-3 py-1 text-sm font-semibold text-teal-700 dark:bg-teal-500/10 dark:text-teal-200">
              {weeklyTotal} submissions
            </span>
          </div>
          <div className="mt-6 grid h-56 grid-cols-7 items-end gap-2 sm:gap-3">
            {dashboard.weekly_progress.map((day) => {
              const height = `${Math.max(10, (day.submissions / maxSubmissions) * 100)}%`;
              return (
                <div key={day.date} className="flex h-full flex-col justify-end text-center">
                  <div className="relative flex flex-1 items-end rounded-lg bg-slate-100 p-1 dark:bg-slate-800">
                    <div className="w-full rounded-md bg-gradient-to-t from-teal-700 to-emerald-400 shadow-sm" style={{ height }} />
                  </div>
                  <p className="mt-2 text-xs font-semibold text-slate-500">{new Date(day.date).toLocaleDateString(undefined, { weekday: "short" })}</p>
                  <p className="text-xs text-slate-400">{day.submissions}</p>
                </div>
              );
            })}
          </div>
        </div>
        <div className="panel p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="label">Focus</p>
              <h2 className="mt-1 font-bold">Upcoming deadlines</h2>
            </div>
            <Link className="text-sm font-semibold text-teal-700 dark:text-teal-300" to="/tasks">All tasks</Link>
          </div>
          <div className="mt-4 space-y-3">
            {dashboard.upcoming_deadlines.length === 0 && <p className="text-sm text-slate-500">No upcoming deadlines.</p>}
            {dashboard.upcoming_deadlines.map((task, index) => (
              <Link key={task.id} to="/tasks" className="flex items-center gap-3 rounded-lg border border-slate-200 p-3 transition hover:-translate-y-0.5 hover:bg-slate-50 hover:shadow-md dark:border-slate-800 dark:hover:bg-slate-800">
                <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-slate-950 text-sm font-bold text-white dark:bg-white dark:text-slate-950">
                  {index + 1}
                </span>
                <div className="min-w-0">
                  <p className="truncate font-semibold">{task.title}</p>
                  <p className="text-sm text-slate-500">{new Date(task.deadline).toLocaleString()} · {task.points} pts</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="mt-6 panel p-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="label">Community</p>
            <h2 className="mt-1 font-bold">Recent announcements</h2>
          </div>
          <Link className="text-sm font-semibold text-teal-700 dark:text-teal-300" to="/announcements">Open board</Link>
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {dashboard.recent_announcements.map((item) => (
            <div key={item.id} className="rounded-lg bg-slate-50 p-4 ring-1 ring-slate-100 dark:bg-slate-800 dark:ring-slate-700">
              <p className="font-semibold">{item.is_pinned ? "Pinned · " : ""}{item.title}</p>
              <p className="mt-1 text-sm text-slate-500">{new Date(item.created_at).toLocaleDateString()}</p>
            </div>
          ))}
          {dashboard.recent_announcements.length === 0 && <p className="text-sm text-slate-500">No recent announcements.</p>}
        </div>
      </section>
    </>
  );
}

function ProgressRing({ value }) {
  const safeValue = Math.max(0, Math.min(100, Number(value) || 0));
  return (
    <div
      className="mx-auto grid h-36 w-36 place-items-center rounded-full"
      style={{ background: `conic-gradient(#ffffff ${safeValue * 3.6}deg, rgba(255,255,255,0.2) 0deg)` }}
    >
      <div className="grid h-28 w-28 place-items-center rounded-full bg-teal-800/90">
        <span className="text-3xl font-bold">{safeValue}%</span>
      </div>
    </div>
  );
}
