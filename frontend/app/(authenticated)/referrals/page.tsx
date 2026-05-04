"use client";

import { useEffect, useState } from "react";

import { Card } from "@/components/ui/card";
import { DataTable } from "@/components/ui/table";
import { apiClient } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { Customer, Referral } from "@/types";

const DEFAULT_COMMISSION_RATE = "5.00";

export default function ReferralsPage() {
  const { t } = useI18n();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [referrerId, setReferrerId] = useState("");
  const [refereeId, setRefereeId] = useState("");
  const [commissionRate, setCommissionRate] = useState(DEFAULT_COMMISSION_RATE);
  const [editingReferralId, setEditingReferralId] = useState<number | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function loadCustomers() {
    apiClient
      .get<{ items: Customer[] }>("/customers")
      .then((data) => setCustomers(data.items))
      .catch(() => setCustomers([]));
  }

  async function loadReferrals() {
    apiClient.get<Referral[]>("/referrals").then(setReferrals).catch(() => setReferrals([]));
  }

  useEffect(() => {
    loadCustomers();
    loadReferrals();
  }, []);

  function resetForm() {
    setEditingReferralId(null);
    setReferrerId("");
    setRefereeId("");
    setCommissionRate(DEFAULT_COMMISSION_RATE);
  }

  async function submitReferral(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);

    if (!referrerId || !refereeId) {
      setMessage(t("referral_select_customers_required"));
      return;
    }

    try {
      const payload = {
        referrer_id: Number(referrerId),
        referee_id: Number(refereeId),
        commission_rate: commissionRate
      };

      if (editingReferralId) {
        await apiClient.patch(`/referrals/${editingReferralId}`, payload);
        setMessage(t("referral_updated"));
      } else {
        await apiClient.post("/referrals", payload);
        setMessage(t("referral_created"));
      }

      resetForm();
      await loadReferrals();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : t("referral_save_failed"));
    }
  }

  return (
    <div className="space-y-6">
      <Card className="surface-muted">
        <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h3 className="text-lg font-semibold tracking-[-0.03em] text-slate-900">
              {editingReferralId ? t("edit_referral") : t("create_referral")}
            </h3>
          </div>
          <button
            className="btn-secondary"
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
            type="button"
          >
            {t("recalculate_referrals")}
          </button>
        </div>
        <form className="grid gap-3 md:grid-cols-4" onSubmit={submitReferral}>
          <select className="field" value={referrerId} onChange={(event) => setReferrerId(event.target.value)}>
            <option value="">{t("select_referrer")}</option>
            {customers.map((customer) => (
              <option key={`referrer-${customer.id}`} value={customer.id}>
                #{customer.id} - {customer.full_name}
              </option>
            ))}
          </select>
          <select className="field" value={refereeId} onChange={(event) => setRefereeId(event.target.value)}>
            <option value="">{t("select_referee")}</option>
            {customers.map((customer) => (
              <option key={`referee-${customer.id}`} value={customer.id}>
                #{customer.id} - {customer.full_name}
              </option>
            ))}
          </select>
          <input
            className="field"
            min="0"
            step="0.01"
            type="number"
            value={commissionRate}
            onChange={(event) => setCommissionRate(event.target.value)}
            placeholder={t("commission_rate")}
          />
          <div className="flex gap-3">
            <button className="btn-primary flex-1" type="submit">
              {editingReferralId ? t("update_referral") : t("create_referral")}
            </button>
            {editingReferralId ? (
              <button className="btn-secondary" onClick={resetForm} type="button">
                {t("cancel")}
              </button>
            ) : null}
          </div>
        </form>
        {message ? <p className="mt-3 text-sm text-mute">{message}</p> : null}
      </Card>

      <DataTable
        headers={[t("referrer"), t("referee"), t("commission_rate"), t("total_earned"), t("created_at"), t("operation")]}
      >
        {referrals.map((referral) => (
          <tr key={referral.id} className="border-b border-[#edf2f8]">
            <td className="px-5 py-4">{referral.referrer_name ?? `#${referral.referrer_id}`}</td>
            <td className="px-5 py-4">{referral.referee_name ?? `#${referral.referee_id}`}</td>
            <td className="px-5 py-4">{referral.commission_rate}%</td>
            <td className="px-5 py-4 font-medium text-slate-900">${referral.total_earned}</td>
            <td className="px-5 py-4">{new Date(referral.created_at).toLocaleDateString()}</td>
            <td className="px-5 py-4">
              <button
                className="text-sm font-medium text-slate-700 transition hover:text-slate-900"
                onClick={() => {
                  setEditingReferralId(referral.id);
                  setReferrerId(String(referral.referrer_id));
                  setRefereeId(String(referral.referee_id));
                  setCommissionRate(referral.commission_rate);
                  setMessage(null);
                }}
                type="button"
              >
                {t("edit")}
              </button>
            </td>
          </tr>
        ))}
      </DataTable>
    </div>
  );
}
