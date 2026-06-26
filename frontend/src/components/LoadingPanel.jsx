export default function LoadingPanel({ label = "Loading..." }) {
  return (
    <div className="panel p-6">
      <div className="flex items-center gap-3">
        <span className="h-3 w-3 animate-pulse rounded-full bg-teal-600 dark:bg-teal-300" />
        <p className="text-sm font-semibold text-slate-600 dark:text-slate-300">{label}</p>
      </div>
      <div className="mt-5 space-y-3">
        <div className="h-3 w-3/4 animate-pulse rounded-full bg-slate-200 dark:bg-slate-800" />
        <div className="h-3 w-1/2 animate-pulse rounded-full bg-slate-200 dark:bg-slate-800" />
      </div>
    </div>
  );
}
