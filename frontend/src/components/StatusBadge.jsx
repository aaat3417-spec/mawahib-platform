import { useLanguage } from "../i18n/LanguageContext.jsx";

const styles = {
  Pending: "bg-amber-100 text-amber-800 dark:bg-amber-500/15 dark:text-amber-200",
  Accepted: "bg-emerald-100 text-emerald-800 dark:bg-emerald-500/15 dark:text-emerald-200",
  "Needs Revision": "bg-blue-100 text-blue-800 dark:bg-blue-500/15 dark:text-blue-200",
  Rejected: "bg-rose-100 text-rose-800 dark:bg-rose-500/15 dark:text-rose-200"
};

const labelKeys = {
  Pending: "statusPending",
  Accepted: "statusAccepted",
  "Needs Revision": "statusNeedsRevision",
  Rejected: "statusRejected"
};

export default function StatusBadge({ status }) {
  const { t } = useLanguage();
  if (!status) {
    return <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300">{t("statusOpen")}</span>;
  }
  return <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${styles[status] || styles.Pending}`}>{t(labelKeys[status] || "statusPending")}</span>;
}
