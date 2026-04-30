"use client";

import { useEffect, useState } from "react";

import { TrendBars } from "@/components/ui/chart";
import { MetricCard } from "@/components/ui/metric-card";
import { PageHeader } from "@/components/ui/page-header";
import { apiClient } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { Card } from "@/components/ui/card";
import { DashboardSummary } from "@/types";

const fallbackSummary: DashboardSummary = {
  total_customers: 0,
  total_wallet_balance: 0,
  total_spend_today: 0,
  active_accounts_count: 0,
  disabled_accounts_count: 0,
  block_rate_quarter: 0,
  block_rate_90d: 0,
  pending_tickets_count: 0,
  spend_trend_7d: Array.from({ length: 7 }, (_, index) => ({
    date: new Date().toISOString(),
    label: `D-${6 - index}`,
    value: 0
  })),
  spend_trend_28d: Array.from({ length: 28 }, (_, index) => ({
    date: new Date().toISOString(),
    label: `${index + 1}`,
    value: 0
  }))
};

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary>(fallbackSummary);
  const { t } = useI18n();

  useEffect(() => {
    apiClient
      .get<DashboardSummary>("/dashboard/summary")
      .then(setSummary)
      .catch(() => setSummary(fallbackSummary));
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader title={t("dashboard")} />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label={t("total_customers")} value={summary.total_customers.toString()} hint={t("active_client_base")} />
        <MetricCard label={t("wallet_balance")} value={`$${summary.total_wallet_balance.toFixed(2)}`} hint={t("wallet_hint")} />
        <MetricCard label={t("spend_today")} value={`$${summary.total_spend_today.toFixed(2)}`} hint={t("spend_hint")} />
        <MetricCard label={t("pending_tickets")} value={summary.pending_tickets_count.toString()} hint={t("pending_hint")} />
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <MetricCard label={t("block_rate_quarter")} value={`${summary.block_rate_quarter.toFixed(2)}%`} hint={t("block_rate_quarter_hint")} />
        <MetricCard label={t("block_rate_90d")} value={`${summary.block_rate_90d.toFixed(2)}%`} hint={t("block_rate_90d_hint")} />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <TrendBars title={t("spend_trend_7d")} items={summary.spend_trend_7d} />
        <Card className="rounded-[28px] p-6">
          <p className="text-sm font-medium text-slate-500">Vision Line</p>
          <h3 className="mt-3 text-[28px] font-semibold tracking-[-0.04em] text-slate-900">Operations Snapshot</h3>
          <p className="mt-3 text-sm leading-7 text-slate-500">
            Internal overview for customer balances, account health, ticket workload, and ad spend movement.
          </p>
          <div className="mt-8 grid gap-3">
            <div className="rounded-[22px] bg-[#f6f9ff] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Accounts</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">{summary.active_accounts_count} / {summary.disabled_accounts_count}</p>
            </div>
            <div className="rounded-[22px] bg-[#f6f9ff] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Wallet</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">${summary.total_wallet_balance.toFixed(2)}</p>
            </div>
            <div className="rounded-[22px] bg-[#f6f9ff] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Tickets</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">{summary.pending_tickets_count}</p>
            </div>
          </div>
        </Card>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <TrendBars title={t("spend_trend_28d")} items={summary.spend_trend_28d.slice(-14)} />
        <Card className="rounded-[28px] p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">Overview</p>
              <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-900">Vision Line CRM</h3>
            </div>
            <div className="rounded-full bg-[#edf3ff] px-3 py-1 text-xs font-semibold text-[#1d4ed8]">Live</div>
          </div>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <div className="rounded-[22px] border border-[#e4ebf5] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Customers</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">{summary.total_customers}</p>
            </div>
            <div className="rounded-[22px] border border-[#e4ebf5] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Spend Today</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">${summary.total_spend_today.toFixed(2)}</p>
            </div>
          </div>
        </Card>
      </section>
    </div>
  );
}
