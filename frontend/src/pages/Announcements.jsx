import { useEffect, useState } from "react";

import PageHeader from "../components/PageHeader.jsx";
import { api } from "../services/api";

export default function Announcements() {
  const [announcements, setAnnouncements] = useState([]);

  useEffect(() => {
    api.get("/announcements").then(({ data }) => setAnnouncements(data));
  }, []);

  return (
    <>
      <PageHeader title="Announcements" eyebrow="Pinned updates, schedules, and community news" />
      <div className="grid gap-4 lg:grid-cols-2">
        {announcements.map((item) => (
          <article key={item.id} className="panel p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="label">{item.is_pinned ? "Pinned announcement" : "Announcement"}</p>
                <h2 className="mt-1 text-xl font-bold">{item.title}</h2>
              </div>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold dark:bg-slate-800">
                {new Date(item.created_at).toLocaleDateString()}
              </span>
            </div>
            <p className="mt-4 whitespace-pre-line leading-7 text-slate-600 dark:text-slate-300">{item.body}</p>
          </article>
        ))}
      </div>
      {announcements.length === 0 && <div className="panel p-6 text-slate-500">No announcements are active right now.</div>}
    </>
  );
}

