export function PageHeader({
  title,
  action
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-4 rounded-[28px] border border-[#e3eaf4] bg-white px-6 py-5 shadow-[0_10px_30px_rgba(15,23,42,0.05)] md:flex-row md:items-end md:justify-between">
      <div className="max-w-3xl">
        <h2 className="text-[30px] font-semibold tracking-[-0.04em] text-ink">{title}</h2>
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}
