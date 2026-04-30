"use client";

import { useEffect, useState } from "react";

import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { DataTable } from "@/components/ui/table";
import { apiClient } from "@/lib/api";
import { formatReconciliationChannel, formatReconciliationStatus } from "@/lib/display";
import { useI18n } from "@/lib/i18n";
import { Customer, ReconciliationRecord } from "@/types";

export default function ReconciliationsPage() {
  const { language, t } = useI18n();
  const [records, setRecords] = useState<ReconciliationRecord[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customerId, setCustomerId] = useState("");
  const [channel, setChannel] = useState("");
  const [status, setStatus] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  async function loadReconciliations() {
    setMessage(null);
    try {
      const params = new URLSearchParams();
      if (customerId) {
        params.set("customer_id", customerId);
      }
      if (channel) {
        params.set("channel", channel);
      }
      if (status) {
        params.set("status", status);
      }
      const query = params.toString();
      const result = await apiClient.get<ReconciliationRecord[]>(
        `/transactions/reconciliations/list${query ? `?${query}` : ""}`,
      );
      setRecords(result);
    } catch (error) {
      setRecords([]);
      setMessage(error instanceof Error ? error.message : null);
    }
  }

  useEffect(() => {
    loadReconciliations();
    apiClient.get<{ items: Customer[] }>("/customers").then((data) => setCustomers(data.items)).catch(() => setCustomers([]));
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader title={t("reconciliations")} />
      <Card className="surface-muted">
        <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="section-eyebrow">Payment Matching</p>
            <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-900">{t("reconciliation_filters")}</h3>
          </div>
          <span className="stat-chip">{records.length} entries</span>
        </div>
        <form
          className="grid gap-3 md:grid-cols-4"
          onSubmit={async (event) => {
            event.preventDefault();
            await loadReconciliations();
          }}
        >
          <select className="field" value={customerId} onChange={(event) => setCustomerId(event.target.value)}>
            <option value="">{t("customer_label")}</option>
            {customers.map((customer) => (
              <option key={customer.id} value={customer.id}>{`#${customer.id} - ${customer.full_name}`}</option>
            ))}
          </select>
          <select className="field" value={channel} onChange={(event) => setChannel(event.target.value)}>
            <option value="">{t("reconciliation_all_channels")}</option>
            <option value="bank">{t("bank")}</option>
            <option value="usdt">{t("usdt")}</option>
          </select>
          <select className="field" value={status} onChange={(event) => setStatus(event.target.value)}>
            <option value="">{t("reconciliation_all_statuses")}</option>
            <option value="credited">{t("credited")}</option>
            <option value="unmatched">{t("unmatched")}</option>
            <option value="duplicate">{t("duplicate")}</option>
            <option value="ignored">{t("ignored")}</option>
          </select>
          <button className="btn-primary" type="submit">
            {t("reconciliations")}
          </button>
        </form>
        {message ? <p className="mt-3 text-sm text-mute">{message}</p> : null}
      </Card>
      <DataTable
        headers={[
          t("reconciliation_channel"),
          t("reconciliation_state"),
          t("customer_id_name"),
          t("amount"),
          t("reconciliation_external_id"),
          t("reconciliation_reference_or_wallet"),
          t("created_at"),
          t("reconciliation_raw_payload"),
        ]}
      >
        {records.map((record) => (
          <tr key={record.id} className="border-b border-[#edf2f8] align-top">
            <td className="px-5 py-4">{formatReconciliationChannel(record.channel, language)}</td>
            <td className="px-5 py-4">{formatReconciliationStatus(record.status, language)}</td>
            <td className="px-5 py-4">
              {record.customer_id ? (
                <div className="flex flex-col">
                  <span className="font-medium text-ink">#{record.customer_id}</span>
                  <span className="text-mute">{customers.find((customer) => customer.id === record.customer_id)?.full_name ?? "-"}</span>
                </div>
              ) : (
                "-"
              )}
            </td>
            <td className="px-5 py-4 font-medium text-slate-900">${record.amount}</td>
            <td className="px-5 py-4">{record.external_id}</td>
            <td className="px-5 py-4">
              {record.reference || record.wallet_address || "-"}
            </td>
            <td className="px-5 py-4">{new Date(record.created_at).toLocaleString()}</td>
            <td className="px-5 py-4 text-xs text-mute">
              <pre className="max-w-[320px] overflow-x-auto whitespace-pre-wrap break-all">
                {JSON.stringify(record.raw_payload, null, 2)}
              </pre>
            </td>
          </tr>
        ))}
      </DataTable>
    </div>
  );
}
