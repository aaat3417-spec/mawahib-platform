import { useEffect, useState } from "react";

import PageHeader from "../components/PageHeader.jsx";
import StatCard from "../components/StatCard.jsx";
import { api } from "../services/api";

export default function Profile() {
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    api.get("/users/me/profile").then(({ data }) => setProfile(data));
  }, []);

  if (!profile) {
    return <div className="panel p-6">Loading profile...</div>;
  }

  return (
    <>
      <PageHeader title="Profile" eyebrow="Portfolio and progress" />
      <section className="panel overflow-hidden">
        <div className="bg-slate-950 p-6 text-white dark:bg-white dark:text-slate-950">
          <p className="text-sm font-semibold opacity-70">{profile.role.replace("_", " ")}</p>
          <h1 className="mt-1 text-3xl font-bold">{profile.full_name}</h1>
          <p className="mt-2 opacity-80">{profile.team_name || "No team yet"} · {profile.email}</p>
        </div>
        <div className="grid gap-4 p-5 md:grid-cols-4">
          <StatCard label="Points" value={profile.points} />
          <StatCard label="Rank" value={profile.rank ? `#${profile.rank}` : "Unranked"} />
          <StatCard label="Completed tasks" value={profile.completed_tasks} />
          <StatCard label="Excellent work" value={profile.statistics?.excellent_work || 0} />
        </div>
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <div className="panel p-5">
          <h2 className="font-bold">Badges</h2>
          <div className="mt-4 flex flex-wrap gap-2">
            {profile.badges.map((badge) => (
              <span key={badge} className="rounded-full bg-amber-100 px-3 py-1 text-sm font-semibold text-amber-800 dark:bg-amber-500/15 dark:text-amber-200">{badge}</span>
            ))}
            {profile.badges.length === 0 && <p className="text-sm text-slate-500">Badges will appear here as achievements grow.</p>}
          </div>
        </div>
        <div className="panel p-5">
          <h2 className="font-bold">Achievements</h2>
          <div className="mt-4 space-y-3">
            {profile.achievements.map((item) => (
              <div key={item.submission_id} className="rounded-lg bg-slate-50 p-4 dark:bg-slate-800">
                <p className="font-semibold">{item.task_title}</p>
                <p className="text-sm text-slate-500">{item.category} · {item.points} points</p>
              </div>
            ))}
            {profile.achievements.length === 0 && <p className="text-sm text-slate-500">No accepted submissions yet.</p>}
          </div>
        </div>
      </section>
    </>
  );
}

