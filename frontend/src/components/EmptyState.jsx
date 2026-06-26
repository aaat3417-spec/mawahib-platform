export default function EmptyState({ title, body, action = null }) {
  return (
    <div className="panel p-6 text-center">
      <p className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Nothing here yet</p>
      <h2 className="mt-2 text-xl font-bold">{title}</h2>
      {body && <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500 dark:text-slate-400">{body}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
