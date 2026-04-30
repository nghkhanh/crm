"use client";

import { Card } from "@/components/ui/card";
import { useI18n } from "@/lib/i18n";

export function TrendBars({
  title,
  items
}: {
  title: string;
  items: Array<{ label: string; value: number }>;
}) {
  const { t } = useI18n();
  const max = Math.max(...items.map((item) => item.value), 1);

  return (
    <Card>
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-ink">{title}</h3>
          <p className="text-sm text-mute">{t("chart_subtitle")}</p>
        </div>
      </div>
      <div className="flex h-56 items-end gap-2">
        {items.map((item) => (
          <div key={item.label} className="flex flex-1 flex-col items-center gap-2">
            <div className="w-full rounded-t-2xl bg-brand/90" style={{ height: `${(item.value / max) * 100}%` }} />
            <span className="text-[11px] text-mute">{item.label}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
