import { useEffect, useState } from "react";

import Alert from "../components/Alert.jsx";
import LoadingPanel from "../components/LoadingPanel.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatCard from "../components/StatCard.jsx";
import { api, apiErrorMessage } from "../services/api";

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [form, setForm] = useState({ full_name: "", bio: "", avatar_url: "" });
  const [message, setMessage] = useState(null);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  function loadProfile() {
    setError("");
    api.get("/users/me/profile")
      .then(({ data }) => {
        setProfile(data);
        setForm({
          full_name: data.full_name || "",
          bio: data.bio || "",
          avatar_url: data.avatar_url || ""
        });
      })
      .catch((err) => setError(apiErrorMessage(err)));
  }

  async function updateProfile(event) {
    event.preventDefault();
    setMessage(null);
    setSaving(true);
    try {
      await api.patch("/users/me", {
        full_name: form.full_name,
        bio: form.bio,
        avatar_url: form.avatar_url || null
      });
      setMessage({ tone: "success", text: "Profile updated." });
      loadProfile();
    } catch (err) {
      setMessage({ tone: "error", text: apiErrorMessage(err) });
    } finally {
      setSaving(false);
    }
  }

  if (error) {
    return <Alert tone="error">{error}</Alert>;
  }

  if (!profile) {
    return <LoadingPanel label="Loading profile..." />;
  }

  return (
    <>
      <PageHeader title="Profile" eyebrow="Portfolio and progress" />
      {message && <Alert tone={message.tone} className="mb-4">{message.text}</Alert>}
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
        <form className="panel p-5 xl:col-span-2" onSubmit={updateProfile} noValidate>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="label">Portfolio settings</p>
              <h2 className="mt-1 font-bold">Update profile</h2>
            </div>
            <button className="btn-primary disabled:cursor-not-allowed disabled:opacity-60" disabled={saving}>
              {saving ? "Saving..." : "Save profile"}
            </button>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <label className="block">
              <span className="label">Name</span>
              <input className="input mt-1" value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} required />
            </label>
            <label className="block">
              <span className="label">Avatar URL</span>
              <input className="input mt-1" placeholder="https://..." value={form.avatar_url} onChange={(event) => setForm({ ...form, avatar_url: event.target.value })} />
            </label>
            <label className="block md:col-span-2">
              <span className="label">Bio</span>
              <textarea className="input mt-1 min-h-28" maxLength={2000} value={form.bio} onChange={(event) => setForm({ ...form, bio: event.target.value })} />
            </label>
          </div>
        </form>
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
