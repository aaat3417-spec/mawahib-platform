import { useEffect, useMemo, useState } from "react";

import PageHeader from "../components/PageHeader.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import { api, apiErrorMessage } from "../services/api";
import { taskCategories } from "../services/constants";

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [category, setCategory] = useState("");
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState({ link_url: "", github_url: "", notes: "", file: null });
  const [message, setMessage] = useState("");

  useEffect(() => {
    loadTasks();
  }, []);

  function loadTasks() {
    const params = category ? { category } : {};
    api.get("/tasks", { params }).then(({ data }) => setTasks(data));
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
    setMessage("");
    const payload = new FormData();
    payload.append("link_url", form.link_url);
    payload.append("github_url", form.github_url);
    payload.append("notes", form.notes);
    if (form.file) {
      payload.append("file", form.file);
    }
    try {
      await api.post(`/submissions/tasks/${selected.id}`, payload);
      setMessage("Submission uploaded successfully.");
      setSelected(null);
      setForm({ link_url: "", github_url: "", notes: "", file: null });
      loadTasks();
    } catch (err) {
      setMessage(apiErrorMessage(err));
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
      {message && <p className="mb-4 rounded-lg bg-teal-50 px-4 py-3 text-sm text-teal-800 dark:bg-teal-500/10 dark:text-teal-200">{message}</p>}
      <div className="space-y-6">
        {Object.entries(grouped).map(([group, groupTasks]) => (
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
                  <button className="btn-primary mt-5" onClick={() => setSelected(task)}>Submit work</button>
                </article>
              ))}
            </div>
          </section>
        ))}
      </div>

      {selected && (
        <div className="fixed inset-0 z-30 grid place-items-center overflow-y-auto bg-slate-950/70 p-4">
          <form className="max-h-[90vh] w-full max-w-xl overflow-y-auto rounded-lg bg-white p-6 shadow-soft dark:bg-slate-900" onSubmit={submitTask}>
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
              <input className="input" type="file" accept="application/pdf,image/png,image/jpeg,image/webp" onChange={(event) => setForm({ ...form, file: event.target.files?.[0] || null })} />
            </div>
            <button className="btn-primary mt-5 w-full">Upload submission</button>
          </form>
        </div>
      )}
    </>
  );
}
