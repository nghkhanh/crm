import clsx from "clsx";

export function Badge({
  children,
  tone = "neutral"
}: {
  children: React.ReactNode;
  tone?: "neutral" | "success" | "danger" | "warning";
}) {
  return (
    <span
      className={clsx(
        "inline-flex rounded-full px-3 py-1 text-xs font-semibold",
        tone === "success" && "bg-green-100 text-success",
        tone === "danger" && "bg-red-100 text-danger",
        tone === "warning" && "bg-amber-100 text-warning",
        tone === "neutral" && "bg-slate-100 text-slate-700"
      )}
    >
      {children}
    </span>
  );
}

