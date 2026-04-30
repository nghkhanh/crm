import { Card } from "@/components/ui/card";

export function MetricCard({
  label,
  value,
  hint
}: {
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <Card className="relative overflow-hidden bg-white">
      <div className="absolute right-0 top-0 h-20 w-20 rounded-bl-[32px] bg-[#edf3ff]" />
      <p className="relative text-sm font-medium text-slate-500">{label}</p>
      <p className="relative mt-5 text-[32px] font-semibold tracking-[-0.03em] text-slate-900">{value}</p>
      <p className="relative mt-2 text-xs uppercase tracking-[0.18em] text-slate-400">{hint}</p>
    </Card>
  );
}
