import { useEffect, useMemo, useState } from "react";

import Alert from "../components/Alert.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingPanel from "../components/LoadingPanel.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import { api, apiErrorMessage } from "../services/api";
import { taskCategories } from "../services/constants";

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [category, setCategory] = useState("");
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState({ link_url: "", github_url: "", notes: "", file: null });
  const [message, setMessage] = useState(null);
  const [modalMessage, setModalMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function loadTasks() {
    setLoading(true);
    setError("");
    const params = category ? { category } : {};
    api.get("/tasks", { params })
      .then(({ data }) => setTasks(data))
      .catch((err) => setError(apiErrorMessage(err)))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadTasks();
  }, [category]);

  const grouped = useMemo(() => {
    return tasks.reduce((acc, task) => {
      acc[task.category] = acc[task.category] || [];
      acc[task.category].push(task);
      return acc;
    }, {});
  }, [tasks]);

  async function submitTask(event) {
    event.preventDefault();
    setMessage(null);
    setModalMessage("");
    const validationError = validateSubmissionForm(form);
    if (validationError) {
      setModalMessage(validationError);
      return;
    }
    setSubmitting(true);
    const payload = new FormData();
    payload.append("link_url", form.link_url);
    payload.append("github_url", form.github_url);
    payload.append("notes", form.notes);
    if (form.file) {
      payload.append("file", form.file);
    }
    try {
      await api.post(`/submissions/tasks/${selected.id}`, payload);
      setMessage({ tone: "success", text: "Submission uploaded successfully." });
      setSelected(null);
      setForm({ link_url: "", github_url: "", notes: "", file: null });
      loadTasks();
    } catch (err) {
      setModalMessage(apiErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <PageHeader
        title="Tasks"
        eyebrow="Choose meaningful work, submit proof, and earn points"
        action={
          <select className="input w-full sm:w-64" value={category} onChange={(event) => setCategory(event.target.value)}>
            <option value="">All categories</option>
            {taskCategories.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        }
      />
      {message && <Alert tone={message.tone} className="mb-4">{message.text}</Alert>}
      {error && <Alert tone="error" className="mb-4">{error}</Alert>}
      {loading && <LoadingPanel label="Loading tasks..." />}
      {!loading && !error && tasks.length === 0 && (
        <EmptyState
          title="No tasks available"
          body={category ? "No tasks match this category yet. Try all categories or check back later." : "Tasks created by admins and team leaders will appear here."}
        />
      )}
      <div className="space-y-6">
        {!loading && !error && Object.entries(grouped).map(([group, groupTasks]) => (
          <section key={group}>
            <h2 className="mb-3 text-lg font-bold">{group}</h2>
            <div className="grid gap-4 lg:grid-cols-2">
              {groupTasks.map((task) => (
                <article key={task.id} className="panel p-5">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="label">{task.difficulty} · {task.estimated_hours}h</p>
                      <h3 className="mt-1 text-lg font-bold">{task.title}</h3>
                    </div>
                    <StatusBadge status={task.submission_status} />
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{task.description}</p>
                  <div className="mt-4 flex flex-wrap gap-2 text-xs font-semibold">
                    <span className="rounded-full bg-slate-100 px-3 py-1 dark:bg-slate-800">{task.points} points</span>
                    <span className="rounded-full bg-slate-100 px-3 py-1 dark:bg-slate-800">{task.is_required ? "Required" : "Optional +30"}</span>
                    <span className="rounded-full bg-slate-100 px-3 py-1 dark:bg-slate-800">{new Date(task.deadline).toLocaleDateString()}</span>
                  </div>
                  {task.attachments?.length > 0 && (
                    <div className="mt-4 space-y-1 text-sm">
                      {task.attachments.map((attachment) => (
                        <a key={attachment} className="block text-teal-700 dark:text-teal-300" href={attachment} target="_blank" rel="noreferrer">
                          {attachment}
                        </a>
                      ))}
                    </div>
                  )}
                  <TaskActionButton task={task} onClick={() => {
                    setSelected(task);
                    setModalMessage("");
                  }} />
                </article>
              ))}
            </div>
          </section>
        ))}
      </div>

      {selected && (
        <div className="fixed inset-0 z-30 grid place-items-center overflow-y-auto bg-slate-950/70 p-4">
          <form className="max-h-[90vh] w-full max-w-xl overflow-y-auto rounded-lg bg-white p-6 shadow-soft dark:bg-slate-900" onSubmit={submitTask} noValidate>
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="label">Submit task</p>
                <h2 className="mt-1 text-xl font-bold">{selected.title}</h2>
              </div>
              <button className="btn-secondary" type="button" onClick={() => setSelected(null)}>Close</button>
            </div>
            <div className="mt-5 space-y-4">
              <input className="input" placeholder="Project or article link" value={form.link_url} onChange={(event) => setForm({ ...form, link_url: event.target.value })} />
              <input className="input" placeholder="GitHub repository" value={form.github_url} onChange={(event) => setForm({ ...form, github_url: event.target.value })} />
              <textarea className="input min-h-28" placeholder="Notes for reviewer" value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} />
              <input className="input" type="file" accept=".png,.jpg,.jpeg,.pdf,.txt,.md,.zip,application/pdf,image/png,image/jpeg,text/plain,text/markdown,application/zip" onChange={(event) => setForm({ ...form, file: event.target.files?.[0] || null })} />
            </div>
            {modalMessage && (
              <p className="mt-4 rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:bg-rose-500/10 dark:text-rose-200">
                {modalMessage}
              </p>
            )}
            <button className="btn-primary mt-5 w-full disabled:cursor-not-allowed disabled:opacity-60" disabled={submitting}>
              {submitting ? "Uploading..." : "Upload submission"}
            </button>
          </form>
        </div>
      )}
    </>
  );
}

function TaskActionButton({ task, onClick }) {
  if (task.submission_status === "Accepted") {
    return <button className="btn-secondary mt-5 w-full cursor-not-allowed opacity-70" type="button" disabled>Accepted</button>;
  }
  if (task.submission_status === "Pending") {
    return <button className="btn-secondary mt-5 w-full cursor-not-allowed opacity-70" type="button" disabled>Awaiting review</button>;
  }
  return (
    <button className="btn-primary mt-5 w-full sm:w-auto" type="button" onClick={onClick}>
      {task.submission_status === "Needs Revision" || task.submission_status === "Rejected" ? "Resubmit work" : "Submit work"}
    </button>
  );
}

function validateSubmissionForm(form) {
  const hasContent = Boolean(form.file || form.notes.trim() || form.link_url.trim() || form.github_url.trim());
  if (!hasContent) {
    return "Add a note, file, link, or GitHub repository before submitting.";
  }
  for (const [label, value] of [["Project link", form.link_url], ["GitHub repository", form.github_url]]) {
    if (!value.trim()) {
      continue;
    }
    try {
      const parsed = new URL(value);
      if (!["http:", "https:"].includes(parsed.protocol)) {
        return `${label} must start with http:// or https://.`;
      }
      if (label === "GitHub repository" && !parsed.hostname.toLowerCase().includes("github.com")) {
        return "GitHub repository must be a github.com URL.";
      }
    } catch {
      return `${label} is not a valid URL.`;
    }
  }
  return "";
}
