import { useEffect, useState } from "react";

import Alert from "../components/Alert.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingPanel from "../components/LoadingPanel.jsx";
import PageHeader from "../components/PageHeader.jsx";
import { useLanguage } from "../i18n/LanguageContext.jsx";
import { api, apiErrorMessage } from "../services/api";

export default function Announcements() {
  const { formatDate, t } = useLanguage();
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/announcements")
      .then(({ data }) => setAnnouncements(data))
      .catch((err) => setError(apiErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <PageHeader title={t("announcementsTitle")} eyebrow={t("announcementsEyebrow")} />
      {error && <Alert tone="error" className="mb-4">{error}</Alert>}
      {loading && <LoadingPanel label={t("loadingAnnouncements")} />}
      {!loading && !error && announcements.length === 0 && (
        <EmptyState title={t("noActiveAnnouncements")} body={t("noActiveAnnouncementsBody")} />
      )}
      <div className="grid gap-4 lg:grid-cols-2">
        {!loading && !error && announcements.map((item) => (
          <article key={item.id} className="panel p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="label">{item.is_pinned ? t("pinnedAnnouncement") : t("announcement")}</p>
                <h2 className="mt-1 text-xl font-bold">{item.title}</h2>
              </div>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold dark:bg-slate-800">
                {formatDate(item.created_at)}
              </span>
            </div>
            <p className="mt-4 whitespace-pre-line leading-7 text-slate-600 dark:text-slate-300">{item.body}</p>
          </article>
        ))}
      </div>
    </>
  );
}
