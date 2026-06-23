export default function PageHeader({ title, eyebrow, action }) {
  return (
    <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div>
        {eyebrow && <p className="label">{eyebrow}</p>}
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-950 dark:text-white">{title}</h1>
      </div>
      {action}
    </div>
  );
}
