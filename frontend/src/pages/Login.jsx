import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth.jsx";
import { useLanguage } from "../i18n/LanguageContext.jsx";
import { apiErrorMessage } from "../services/api";

export default function Login() {
  const { user, login, setupOwner } = useAuth();
  const { t, toggleLanguage } = useLanguage();
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", password: "", full_name: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (user) {
    return <Navigate to="/" replace />;
  }

  async function submit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      if (mode === "setup") {
        await setupOwner(form);
      } else {
        await login(form.email, form.password);
      }
      navigate("/");
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <button
        className="fixed end-4 top-4 z-20 rounded-lg border border-white/15 bg-white/10 px-3 py-2 text-sm font-bold text-white backdrop-blur transition hover:bg-white/20"
        type="button"
        onClick={toggleLanguage}
      >
        {t("switchLanguage")}
      </button>
      <div className="grid min-h-screen lg:grid-cols-[1.08fr_0.92fr]">
        <section className="relative flex items-center overflow-hidden px-6 py-12 sm:px-10 lg:px-16">
          <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(15,118,110,0.35),rgba(15,23,42,0)_42%),linear-gradient(180deg,rgba(16,185,129,0.12),rgba(2,6,23,0))]" />
          <div className="relative max-w-3xl">
            <div className="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.18em] text-teal-100 backdrop-blur">
              {t("giftedCommunity")}
            </div>
            <h1 className="mt-6 text-4xl font-bold tracking-tight sm:text-6xl">Mawahib Community Platform</h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">
              {t("loginHeroBody")}
            </p>

            <div className="mt-10 grid gap-4 sm:grid-cols-3">
              {[
                ["100+", t("taskPoints")],
                ["6", t("achievementBadges")],
                ["5", t("communityTeams")]
              ].map(([value, label]) => (
                <div key={label} className="rounded-lg border border-white/10 bg-white/10 p-4 backdrop-blur">
                  <p className="text-2xl font-bold">{value}</p>
                  <p className="mt-1 text-sm text-slate-300">{label}</p>
                </div>
              ))}
            </div>

            <div className="mt-8 rounded-lg border border-white/10 bg-white/5 p-4 backdrop-blur">
              <div className="grid gap-3 sm:grid-cols-3">
                {[t("completeTasks"), t("earnPoints"), t("buildPortfolio")].map((item, index) => (
                  <div key={item} className="flex items-center gap-3">
                    <span className="grid h-8 w-8 place-items-center rounded-lg bg-teal-400 text-sm font-bold text-slate-950">{index + 1}</span>
                    <span className="text-sm font-semibold text-slate-100">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="flex items-center justify-center bg-slate-50 px-4 py-10 text-slate-950 dark:bg-slate-900 dark:text-white sm:px-6">
          <form className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-5 shadow-soft dark:border-slate-800 dark:bg-slate-950 sm:p-6" onSubmit={submit}>
            <div className="mb-6">
              <p className="label">{t("secureAccess")}</p>
              <h2 className="mt-1 text-2xl font-bold">{mode === "setup" ? t("createOwnerAccount") : t("welcomeBack")}</h2>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                {mode === "setup" ? t("setupSubtitle") : t("loginSubtitle")}
              </p>
            </div>

            <div className="mb-6 flex rounded-lg bg-slate-100 p-1 dark:bg-slate-800">
            <button
              type="button"
              className={`flex-1 rounded-md px-3 py-2 text-sm font-semibold ${mode === "login" ? "bg-white shadow-sm dark:bg-slate-950" : "text-slate-500"}`}
              onClick={() => setMode("login")}
            >
              {t("login")}
            </button>
            <button
              type="button"
              className={`flex-1 rounded-md px-3 py-2 text-sm font-semibold ${mode === "setup" ? "bg-white shadow-sm dark:bg-slate-950" : "text-slate-500"}`}
              onClick={() => setMode("setup")}
            >
              {t("firstOwner")}
            </button>
          </div>

          <div className="mt-6 space-y-4">
            {mode === "setup" && (
              <label className="block">
                <span className="label">{t("fullName")}</span>
                <input className="input mt-1" value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} required />
              </label>
            )}
            <label className="block">
              <span className="label">{t("email")}</span>
              <input className="input mt-1" type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required />
            </label>
            <label className="block">
              <span className="label">{t("password")}</span>
              <input className="input mt-1" type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} required minLength={8} maxLength={72} />
            </label>
          </div>
          {error && <p className="mt-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700 dark:bg-rose-500/10 dark:text-rose-200">{error}</p>}
          <button className="btn-primary mt-6 w-full" disabled={submitting}>
            {submitting ? t("working") : mode === "setup" ? t("createOwner") : t("login")}
          </button>
          <p className="mt-4 text-center text-xs text-slate-500 dark:text-slate-400">
            {t("accessFootnote")}
          </p>
        </form>
      </section>
      </div>
    </main>
  );
}
