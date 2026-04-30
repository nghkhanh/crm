"use client";

import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { useI18n } from "@/lib/i18n";

export function ManagementPlaceholderPage({
  titleKey,
  descriptionKey,
}: {
  titleKey: string;
  descriptionKey: string;
}) {
  const { t } = useI18n();

  return (
    <div className="space-y-6">
      <PageHeader title={t(titleKey)} description={t(descriptionKey)} />

      <section className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <Card className="rounded-[28px] p-6">
          <p className="section-eyebrow">{t("vision_line_workspace")}</p>
          <h3 className="mt-3 text-2xl font-semibold tracking-[-0.04em] text-slate-900">{t(titleKey)}</h3>
          <p className="mt-3 text-sm leading-7 text-slate-500">{t(descriptionKey)}</p>
          <div className="mt-6 grid gap-3 md:grid-cols-3">
            <div className="rounded-[22px] bg-[#f6f9ff] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">{t("workflow")}</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{t("workflow_ready")}</p>
            </div>
            <div className="rounded-[22px] bg-[#f6f9ff] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">{t("integration")}</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{t("integration_pending")}</p>
            </div>
            <div className="rounded-[22px] bg-[#f6f9ff] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">{t("ownership")}</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{t("internal_team")}</p>
            </div>
          </div>
        </Card>

        <Card className="rounded-[28px] p-6">
          <p className="text-sm font-medium text-slate-500">{t("recommended_scope")}</p>
          <div className="mt-4 space-y-3">
            {[t("scope_queue"), t("scope_assignment"), t("scope_processing"), t("scope_audit")].map((item) => (
              <div key={item} className="rounded-[20px] border border-[#e3eaf4] px-4 py-3 text-sm text-slate-700">
                {item}
              </div>
            ))}
          </div>
        </Card>
      </section>
    </div>
  );
}
