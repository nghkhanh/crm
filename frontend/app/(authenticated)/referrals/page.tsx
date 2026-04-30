"use client";

import { useEffect, useState } from "react";

import { PageHeader } from "@/components/ui/page-header";
import { DataTable } from "@/components/ui/table";
import { apiClient } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { Referral } from "@/types";

export default function ReferralsPage() {
  const { t } = useI18n();
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [message, setMessage] = useState<string | null>(null);

  async function loadReferrals() {
    apiClient.get<Referral[]>("/referrals").then(setReferrals).catch(() => setReferrals([]));
  }

  useEffect(() => {
    loadReferrals();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("referrals")}
        action={
          <button
            className="btn-primary"
            onClick={async () => {
              setMessage(null);
              try {
                const payload = await apiClient.post<{ updated: number }>("/referrals/calculate");
                setMessage(t("referrals_recalculated", { updated: payload.updated }));
                await loadReferrals();
              } catch (error) {
                setMessage(error instanceof Error ? error.message : t("referrals_recalculate_failed"));
              }
            }}
          >
            {t("recalculate_referrals")}
          </button>
        }
      />
      {message ? <p className="text-sm text-mute">{message}</p> : null}
      <DataTable
        headers={[t("referrer"), t("referee"), t("commission_rate"), t("total_earned"), t("created_at")]}
      >
        {referrals.map((referral) => (
          <tr key={referral.id} className="border-b border-[#edf2f8]">
            <td className="px-5 py-4">{referral.referrer_name ?? `#${referral.referrer_id}`}</td>
            <td className="px-5 py-4">{referral.referee_name ?? `#${referral.referee_id}`}</td>
            <td className="px-5 py-4">{referral.commission_rate}%</td>
            <td className="px-5 py-4 font-medium text-slate-900">${referral.total_earned}</td>
            <td className="px-5 py-4">{new Date(referral.created_at).toLocaleDateString()}</td>
          </tr>
        ))}
      </DataTable>
    </div>
  );
}
