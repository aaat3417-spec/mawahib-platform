export default function StatCard({ label, value, detail, accent = "teal", icon = "•", trend }) {
  const accents = {
    teal: "from-teal-500 to-emerald-400 text-teal-700 dark:text-teal-200",
    amber: "from-amber-500 to-yellow-400 text-amber-700 dark:text-amber-200",
    rose: "from-rose-500 to-orange-400 text-rose-700 dark:text-rose-200",
    sky: "from-sky-500 to-cyan-400 text-sky-700 dark:text-sky-200"
  };
  const accentClass = accents[accent] || accents.teal;

  return (
    <div className="soft-card relative overflow-hidden">
      <div className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${accentClass.split(" ").slice(0, 2).join(" ")}`} />
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="label">{label}</p>
          <p className="mt-3 text-3xl font-bold tracking-tight text-slate-950 dark:text-white">{value ?? "0"}</p>
        </div>
        <span className={`grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-slate-100 text-lg font-bold dark:bg-slate-800 ${accentClass.split(" ").slice(2).join(" ")}`}>
          {icon}
        </span>
      </div>
      <div className="mt-4 flex min-h-5 items-center justify-between gap-3">
        {detail && <p className="text-sm text-slate-500 dark:text-slate-400">{detail}</p>}
        {trend && <p className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-200">{trend}</p>}
      </div>
    </div>
  );
}
