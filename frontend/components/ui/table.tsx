import { ReactNode } from "react";

export function DataTable({
  headers,
  children,
  title,
  subtitle
}: {
  headers: string[];
  children: ReactNode;
  title?: string;
  subtitle?: string;
}) {
  return (
    <div className="overflow-hidden rounded-[28px] border border-[#e3eaf4] bg-white shadow-[0_10px_30px_rgba(15,23,42,0.05)]">
      {title || subtitle ? (
        <div className="border-b border-[#e9eef6] px-5 py-4">
          {title ? <p className="text-base font-semibold text-slate-900">{title}</p> : null}
          {subtitle ? <p className="mt-1 text-sm text-slate-500">{subtitle}</p> : null}
        </div>
      ) : null}
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="surface-muted text-left text-[11px] uppercase tracking-[0.2em] text-mute">
            <tr>
              {headers.map((header) => (
                <th key={header} className="px-5 py-4 font-semibold">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="[&_tr:last-child]:border-b-0">{children}</tbody>
        </table>
      </div>
    </div>
  );
}
