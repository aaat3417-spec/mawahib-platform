import { useEffect, useState } from "react";

import PageHeader from "../components/PageHeader.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import { useAuth } from "../hooks/useAuth.jsx";
import { api, apiErrorMessage } from "../services/api";
import { submissionStatuses } from "../services/constants";

export default function Submissions() {
  const { canReview } = useAuth();
  const [submissions, setSubmissions] = useState([]);
  const [reviewing, setReviewing] = useState(null);
  const [review, setReview] = useState({ status: "Accepted", feedback: "", excellent_work: false, helping_members_points: false });
  const [message, setMessage] = useState("");

  useEffect(() => {
    load();
  }, []);

  function load() {
    api.get("/submissions").then(({ data }) => setSubmissions(data));
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
    try {
      await api.patch(`/submissions/${reviewing.id}/review`, review);
      setMessage("Review saved.");
      setReviewing(null);
      load();
    } catch (err) {
      setMessage(apiErrorMessage(err));
    }
  }

  return (
    <>
      <PageHeader title="Submissions" eyebrow="Review status and feedback" />
      {message && <p className="mb-4 rounded-lg bg-slate-100 px-4 py-3 text-sm dark:bg-slate-800">{message}</p>}
      <div className="panel overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm dark:divide-slate-800">
            <thead className="bg-slate-50 dark:bg-slate-800">
              <tr>
                {["Task", "Student", "Team", "Status", "Submitted", "Proof", "Action"].map((heading) => (
                  <th key={heading} className="px-4 py-3 text-left font-semibold">{heading}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {submissions.map((item) => (
                <tr key={item.id}>
                  <td className="px-4 py-3 font-semibold">{item.task_title}</td>
                  <td className="px-4 py-3">{item.student_name}</td>
                  <td className="px-4 py-3">{item.team_name || "No team"}</td>
                  <td className="px-4 py-3"><StatusBadge status={item.status} /></td>
                  <td className="px-4 py-3">{new Date(item.submitted_at).toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <div className="space-y-1">
                      {item.link_url && <a className="block text-teal-700 dark:text-teal-300" href={item.link_url} target="_blank" rel="noreferrer">Link</a>}
                      {item.github_url && <a className="block text-teal-700 dark:text-teal-300" href={item.github_url} target="_blank" rel="noreferrer">GitHub</a>}
                      {item.file_path && <a className="block text-teal-700 dark:text-teal-300" href={`/${item.file_path}`} target="_blank" rel="noreferrer">File</a>}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {canReview ? <button className="btn-secondary" onClick={() => openReview(item)}>Review</button> : item.feedback || "Awaiting review"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {reviewing && (
        <div className="fixed inset-0 z-30 grid place-items-center overflow-y-auto bg-slate-950/70 p-4">
          <form className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-lg bg-white p-6 shadow-soft dark:bg-slate-900" onSubmit={submitReview}>
            <div className="flex items-start justify-between">
              <div>
                <p className="label">Review submission</p>
                <h2 className="mt-1 text-xl font-bold">{reviewing.task_title}</h2>
              </div>
              <button type="button" className="btn-secondary" onClick={() => setReviewing(null)}>Close</button>
            </div>
            <div className="mt-5 space-y-4">
              <select className="input" value={review.status} onChange={(event) => setReview({ ...review, status: event.target.value })}>
                {submissionStatuses.map((status) => <option key={status}>{status}</option>)}
              </select>
              <textarea className="input min-h-28" placeholder="Feedback" value={review.feedback} onChange={(event) => setReview({ ...review, feedback: event.target.value })} />
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={review.excellent_work} onChange={(event) => setReview({ ...review, excellent_work: event.target.checked })} />
                Excellent work bonus (+50)
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={review.helping_members_points} onChange={(event) => setReview({ ...review, helping_members_points: event.target.checked })} />
                Helped members bonus (+20)
              </label>
            </div>
            <button className="btn-primary mt-5 w-full">Save review</button>
          </form>
        </div>
      )}
    </>
  );
}
