import { useEffect, useState } from "react";

import PageHeader from "../components/PageHeader.jsx";
import { api } from "../services/api";

export default function Leaderboard() {
  const [period, setPeriod] = useState("all");
  const [students, setStudents] = useState([]);
  const [teams, setTeams] = useState([]);

  useEffect(() => {
    api.get("/leaderboard/students", { params: { period } }).then(({ data }) => setStudents(data));
    api.get("/leaderboard/teams", { params: { period } }).then(({ data }) => setTeams(data));
  }, [period]);

  return (
    <>
      <PageHeader
        title="Leaderboard"
        eyebrow="Weekly, monthly, and all-time ranking"
        action={
          <select className="input w-full sm:w-48" value={period} onChange={(event) => setPeriod(event.target.value)}>
            <option value="all">All time</option>
            <option value="monthly">Monthly</option>
            <option value="weekly">Weekly</option>
          </select>
        }
      />
      <section className="mb-6 rounded-lg bg-slate-950 p-5 text-white shadow-soft dark:bg-white dark:text-slate-950">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-300 dark:text-teal-700">Ranking season</p>
            <h2 className="mt-2 text-3xl font-bold tracking-tight">{periodLabel(period)} champions</h2>
            <p className="mt-2 max-w-2xl text-sm text-slate-300 dark:text-slate-600">
              Celebrate consistent progress across individual students and teams. Rankings update from accepted work and point events.
            </p>
          </div>
          <div className="rounded-lg bg-white/10 px-4 py-3 dark:bg-slate-100">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-300 dark:text-slate-500">Tracked</p>
            <p className="mt-1 text-lg font-bold">{students.length} students · {teams.length} teams</p>
          </div>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-2">
        <RankingPanel title="Top students" rows={students} nameKey="full_name" tone="student" />
        <RankingPanel title="Top teams" rows={teams} nameKey="name" tone="team" />
      </div>
    </>
  );
}

function RankingPanel({ title, rows, nameKey, tone }) {
  const topThree = rows.slice(0, 3);
  const maxPoints = Math.max(1, ...rows.map((row) => row.points));

  return (
    <section className="panel p-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="label">{tone === "team" ? "Team performance" : "Student excellence"}</p>
          <h2 className="mt-1 font-bold">{title}</h2>
        </div>
        <span className="rounded-full bg-teal-50 px-3 py-1 text-xs font-bold text-teal-700 dark:bg-teal-500/10 dark:text-teal-200">
          {rows.length} ranked
        </span>
      </div>

      {topThree.length > 0 && (
        <div className="mt-5 grid gap-3 sm:grid-cols-3">
          {topThree.map((row) => (
            <div key={row.id} className={`rounded-lg p-4 text-center shadow-sm ${podiumStyle(row.rank)}`}>
              <p className="text-xs font-bold uppercase tracking-wide opacity-80">Rank #{row.rank}</p>
              <p className="mt-2 truncate text-lg font-bold">{row[nameKey]}</p>
              <p className="mt-1 text-sm font-semibold opacity-80">{row.points} pts</p>
              {row.members !== undefined && <p className="mt-1 text-xs opacity-70">{row.members} members</p>}
            </div>
          ))}
        </div>
      )}

      <div className="mt-5 space-y-3">
        {rows.map((row) => (
          <div key={row.id} className="rounded-lg bg-slate-50 p-4 ring-1 ring-slate-100 dark:bg-slate-800 dark:ring-slate-700">
            <div className="flex items-center justify-between gap-4">
              <div className="flex min-w-0 items-center gap-3">
                <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-slate-950 font-bold text-white dark:bg-white dark:text-slate-950">
                #{row.rank}
                </span>
                <div className="min-w-0">
                  <p className="truncate font-semibold">{row[nameKey]}</p>
                  {row.members !== undefined && <p className="text-sm text-slate-500">{row.members} members</p>}
                </div>
              </div>
              <p className="shrink-0 text-lg font-bold text-teal-700 dark:text-teal-300">{row.points} pts</p>
            </div>
            <div className="mt-3 h-2 rounded-full bg-slate-200 dark:bg-slate-700">
              <div
                className="h-full rounded-full bg-gradient-to-r from-teal-700 to-emerald-400"
                style={{ width: `${Math.max(4, (row.points / maxPoints) * 100)}%` }}
              />
            </div>
          </div>
        ))}
        {rows.length === 0 && <p className="text-sm text-slate-500">No ranking data yet.</p>}
      </div>
    </section>
  );
}

function periodLabel(period) {
  if (period === "weekly") return "Weekly";
  if (period === "monthly") return "Monthly";
  return "All-time";
}

function podiumStyle(rank) {
  if (rank === 1) return "bg-amber-100 text-amber-900 dark:bg-amber-300 dark:text-amber-950";
  if (rank === 2) return "bg-slate-200 text-slate-900 dark:bg-slate-600 dark:text-white";
  return "bg-teal-100 text-teal-900 dark:bg-teal-500/20 dark:text-teal-100";
}
