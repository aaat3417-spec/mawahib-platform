export default function Alert({ children, tone = "info", className = "" }) {
  const tones = {
    error: "border-rose-200 bg-rose-50 text-rose-800 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-100",
    success: "border-teal-200 bg-teal-50 text-teal-800 dark:border-teal-500/30 dark:bg-teal-500/10 dark:text-teal-100",
    info: "border-slate-200 bg-slate-50 text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
  };

  return (
    <div className={`rounded-lg border px-4 py-3 text-sm font-semibold ${tones[tone] || tones.info} ${className}`} role="status" aria-live="polite">
      {children}
    </div>
  );
}
