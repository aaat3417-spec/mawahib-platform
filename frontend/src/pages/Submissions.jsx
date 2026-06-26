import { useEffect, useState } from "react";

import Alert from "../components/Alert.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingPanel from "../components/LoadingPanel.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import { useAuth } from "../hooks/useAuth.jsx";
import { useLanguage } from "../i18n/LanguageContext.jsx";
import { api, apiErrorMessage } from "../services/api";
import { submissionStatuses } from "../services/constants";

export default function Submissions() {
  const { canReview } = useAuth();
  const { formatDateTime, t } = useLanguage();
  const [submissions, setSubmissions] = useState([]);
  const [reviewing, setReviewing] = useState(null);
  const [review, setReview] = useState({ status: "Accepted", feedback: "", excellent_work: false, helping_members_points: false });
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [savingReview, setSavingReview] = useState(false);

  useEffect(() => {
    load();
  }, []);

  function load() {
    setLoading(true);
    setError("");
    api.get("/submissions")
      .then(({ data }) => setSubmissions(data))
      .catch((err) => setError(apiErrorMessage(err)))
      .finally(() => setLoading(false));
  }

  function openReview(item) {
    setReviewing(item);
    setReview({
      status: item.status,
      feedback: item.feedback || "",
      excellent_work: false,
      helping_members_points: false
    });
  }

  async function submitReview(event) {
    event.preventDefault();
    setSavingReview(true);
    setMessage(null);
    try {
      await api.patch(`/submissions/${reviewing.id}/review`, review);
      setMessage({ tone: "success", text: t("reviewSaved") });
      setReviewing(null);
      load();
    } catch (err) {
      setMessage({ tone: "error", text: apiErrorMessage(err) });
    } finally {
      setSavingReview(false);
    }
  }

  async function openFile(item) {
    if (!item.file_url) {
      return;
    }
    try {
      const { data } = await api.get(item.file_url, { responseType: "blob" });
      const url = URL.createObjectURL(data);
      window.open(url, "_blank", "noopener,noreferrer");
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (err) {
      setMessage({ tone: "error", text: apiErrorMessage(err) });
    }
  }

  return (
    <>
      <PageHeader title={t("submissionsTitle")} eyebrow={t("submissionsEyebrow")} />
      {message && <Alert tone={message.tone} className="mb-4">{message.text}</Alert>}
      {error && <Alert tone="error" className="mb-4">{error}</Alert>}
      {loading && <LoadingPanel label={t("loadingSubmissions")} />}
      {!loading && !error && submissions.length === 0 && (
        <EmptyState
          title={canReview ? t("noReviewTitle") : t("noSubmissionsTitle")}
          body={canReview ? t("noReviewBody") : t("noSubmissionsBody")}
        />
      )}
      {!loading && !error && submissions.length > 0 && (
      <div className="panel overflow-hidden">
        <div className="grid gap-3 p-3 md:hidden">
          {submissions.map((item) => (
            <SubmissionCard
              key={item.id}
              item={item}
              canReview={canReview}
              formatDateTime={formatDateTime}
              t={t}
              onReview={() => openReview(item)}
              onFile={() => openFile(item)}
            />
          ))}
        </div>
        <div className="overflow-x-auto">
          <table className="hidden min-w-full divide-y divide-slate-200 text-sm dark:divide-slate-800 md:table">
            <thead className="bg-slate-50 dark:bg-slate-800">
              <tr>
                {[t("tasks"), t("student"), t("team"), t("status"), t("submitted"), t("proof"), t("action")].map((heading) => (
                  <th key={heading} className="px-4 py-3 text-left font-semibold">{heading}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {submissions.map((item) => (
                <tr key={item.id}>
                  <td className="px-4 py-3 font-semibold">{item.task_title}</td>
                  <td className="px-4 py-3">{item.student_name}</td>
                  <td className="px-4 py-3">{item.team_name || t("noTeam")}</td>
                  <td className="px-4 py-3"><StatusBadge status={item.status} /></td>
                  <td className="px-4 py-3">{formatDateTime(item.submitted_at)}</td>
                  <td className="px-4 py-3">
                    <div className="space-y-1">
                      {item.link_url && <a className="block text-teal-700 dark:text-teal-300" href={item.link_url} target="_blank" rel="noreferrer">{t("link")}</a>}
                      {item.github_url && <a className="block text-teal-700 dark:text-teal-300" href={item.github_url} target="_blank" rel="noreferrer">GitHub</a>}
                      {item.file_url && (
                        <button className="block text-left text-teal-700 dark:text-teal-300" type="button" onClick={() => openFile(item)}>
                          {t("file")}
                        </button>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {canReview ? <button className="btn-secondary" onClick={() => openReview(item)}>{t("review")}</button> : item.feedback || t("awaitingFeedback")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      )}

      {reviewing && (
        <div className="fixed inset-0 z-30 grid place-items-center overflow-y-auto bg-slate-950/70 p-4">
          <form className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-lg bg-white p-6 shadow-soft dark:bg-slate-900" onSubmit={submitReview}>
            <div className="flex items-start justify-between">
              <div>
                <p className="label">{t("review")}</p>
                <h2 className="mt-1 text-xl font-bold">{reviewing.task_title}</h2>
              </div>
              <button type="button" className="btn-secondary" onClick={() => setReviewing(null)}>{t("close")}</button>
            </div>
            <div className="mt-5 space-y-4">
              <select className="input" value={review.status} onChange={(event) => setReview({ ...review, status: event.target.value })}>
                {submissionStatuses.map((status) => <option key={status}>{status}</option>)}
              </select>
              <textarea className="input min-h-28" placeholder={t("feedback")} value={review.feedback} onChange={(event) => setReview({ ...review, feedback: event.target.value })} />
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={review.excellent_work} onChange={(event) => setReview({ ...review, excellent_work: event.target.checked })} />
                {t("excellentBonus")}
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={review.helping_members_points} onChange={(event) => setReview({ ...review, helping_members_points: event.target.checked })} />
                {t("helpingBonus")}
              </label>
            </div>
            <button className="btn-primary mt-5 w-full disabled:cursor-not-allowed disabled:opacity-60" disabled={savingReview}>
              {savingReview ? t("savingReview") : t("saveReview")}
            </button>
          </form>
        </div>
      )}
    </>
  );
}

function SubmissionCard({ item, canReview, formatDateTime, t, onReview, onFile }) {
  return (
    <article className="rounded-lg bg-slate-50 p-4 ring-1 ring-slate-100 dark:bg-slate-800 dark:ring-slate-700">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate font-bold">{item.task_title}</p>
          <p className="mt-1 text-sm text-slate-500">{item.student_name} · {item.team_name || t("noTeam")}</p>
        </div>
        <StatusBadge status={item.status} />
      </div>
      <p className="mt-3 text-xs font-semibold text-slate-500">{formatDateTime(item.submitted_at)}</p>
      <div className="mt-4 flex flex-wrap gap-2 text-sm font-semibold">
        {item.link_url && <a className="rounded-lg bg-white px-3 py-2 text-teal-700 dark:bg-slate-900 dark:text-teal-300" href={item.link_url} target="_blank" rel="noreferrer">{t("link")}</a>}
        {item.github_url && <a className="rounded-lg bg-white px-3 py-2 text-teal-700 dark:bg-slate-900 dark:text-teal-300" href={item.github_url} target="_blank" rel="noreferrer">GitHub</a>}
        {item.file_url && <button className="rounded-lg bg-white px-3 py-2 text-teal-700 dark:bg-slate-900 dark:text-teal-300" type="button" onClick={onFile}>{t("file")}</button>}
      </div>
      <div className="mt-4">
        {canReview ? (
          <button className="btn-secondary w-full" type="button" onClick={onReview}>{t("review")}</button>
        ) : (
          <p className="rounded-lg bg-white p-3 text-sm text-slate-600 dark:bg-slate-900 dark:text-slate-300">
            {item.feedback || t("awaitingFeedback")}
          </p>
        )}
      </div>
    </article>
  );
}
