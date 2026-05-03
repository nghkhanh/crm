"use client";

import { useEffect, useState } from "react";

import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { DataTable } from "@/components/ui/table";
import { apiClient } from "@/lib/api";
import {
  formatReconciliationChannel,
  formatReconciliationStatus,
  formatTransactionSource,
  formatTransactionStatus,
  formatTransactionType,
} from "@/lib/display";
import { useI18n } from "@/lib/i18n";
import { Customer, ReconciliationRecord, Transaction } from "@/types";

export default function TransactionsPage() {
  const { language, t } = useI18n();
  const [activeTab, setActiveTab] = useState<"transactions" | "reconciliations">("transactions");
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [reconciliations, setReconciliations] = useState<ReconciliationRecord[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customerId, setCustomerId] = useState("");
  const [type, setType] = useState("topup_bank");
  const [amount, setAmount] = useState("");
  const [reference, setReference] = useState("");
  const [transactionMessage, setTransactionMessage] = useState<string | null>(null);
  const [reconciliationMessage, setReconciliationMessage] = useState<string | null>(null);
  const [reconciliationCustomerId, setReconciliationCustomerId] = useState("");
  const [reconciliationChannel, setReconciliationChannel] = useState("");
  const [reconciliationStatus, setReconciliationStatus] = useState("");

  async function loadTransactions() {
    apiClient.get<Transaction[]>("/transactions").then(setTransactions).catch(() => setTransactions([]));
  }

  async function loadReconciliations() {
    setReconciliationMessage(null);
    try {
      const params = new URLSearchParams();
      if (reconciliationCustomerId) {
        params.set("customer_id", reconciliationCustomerId);
      }
      if (reconciliationChannel) {
        params.set("channel", reconciliationChannel);
      }
      if (reconciliationStatus) {
        params.set("status", reconciliationStatus);
      }
      const query = params.toString();
      const result = await apiClient.get<ReconciliationRecord[]>(
        `/transactions/reconciliations/list${query ? `?${query}` : ""}`,
      );
      setReconciliations(result);
    } catch (error) {
      setReconciliations([]);
      setReconciliationMessage(error instanceof Error ? error.message : null);
    }
  }

  useEffect(() => {
    loadTransactions();
    loadReconciliations();
    apiClient.get<{ items: Customer[] }>("/customers").then((data) => setCustomers(data.items)).catch(() => setCustomers([]));
  }, []);

  async function createTransaction(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTransactionMessage(null);
    try {
      await apiClient.post("/transactions", {
        customer_id: Number(customerId),
        type,
        amount,
        reference: reference || null
      });
      setCustomerId("");
      setType("topup_bank");
      setAmount("");
      setReference("");
      setTransactionMessage(t("create_transaction_success"));
      await loadTransactions();
    } catch (error) {
      setTransactionMessage(error instanceof Error ? error.message : t("create_transaction_failed"));
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader title={t("transactions")} />
      <Card className="surface-muted">
        <div className="flex gap-2">
          <button
            className={activeTab === "transactions" ? "btn-primary" : "btn-secondary"}
            type="button"
            onClick={() => setActiveTab("transactions")}
          >
            {t("transactions")}
          </button>
          <button
            className={activeTab === "reconciliations" ? "btn-primary" : "btn-secondary"}
            type="button"
            onClick={() => setActiveTab("reconciliations")}
          >
            {t("reconciliations")}
          </button>
        </div>
      </Card>
      {activeTab === "transactions" ? (
        <>
          <Card className="surface-muted">
            <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <h3 className="text-xl font-semibold tracking-[-0.03em] text-slate-900">{t("create_transaction")}</h3>
              <span className="stat-chip">{transactions.length} entries</span>
            </div>
            <form className="grid gap-3 md:grid-cols-5" onSubmit={createTransaction}>
              <select className="field" value={customerId} onChange={(event) => setCustomerId(event.target.value)}>
                <option value="">{t("customer_label")}</option>
                {customers.map((customer) => (
                  <option key={customer.id} value={customer.id}>{`#${customer.id} - ${customer.full_name}`}</option>
                ))}
              </select>
              <select className="field" value={type} onChange={(event) => setType(event.target.value)}>
                <option value="topup_bank">{t("topup_bank")}</option>
                <option value="topup_usdt">{t("topup_usdt")}</option>
                <option value="fee">{t("fee")}</option>
                <option value="commission">{t("commission")}</option>
                <option value="adjustment">{t("adjustment")}</option>
              </select>
              <input className="field" placeholder={t("usd_amount")} value={amount} onChange={(event) => setAmount(event.target.value)} />
              <input className="field" placeholder={t("reference")} value={reference} onChange={(event) => setReference(event.target.value)} />
              <button className="btn-primary" type="submit">{t("create_transaction")}</button>
            </form>
            {transactionMessage ? <p className="mt-3 text-sm text-mute">{transactionMessage}</p> : null}
          </Card>
          <DataTable
            headers={[t("customer_id_name"), t("type"), t("transaction_source"), t("transaction_status"), t("amount"), t("balance_before"), t("balance_after"), t("reference"), t("note"), t("created_at")]}
          >
            {transactions.map((transaction) => (
              <tr key={transaction.id} className="border-b border-[#edf2f8]">
                <td className="px-5 py-4">
                  <div className="flex flex-col">
                    <span className="font-medium text-ink">#{transaction.customer_id}</span>
                    <span className="text-mute">{customers.find((customer) => customer.id === transaction.customer_id)?.full_name ?? "-"}</span>
                  </div>
                </td>
                <td className="px-5 py-4">{formatTransactionType(transaction.type, language)}</td>
                <td className="px-5 py-4">{formatTransactionSource(transaction.source, language)}</td>
                <td className="px-5 py-4">{formatTransactionStatus(transaction.status, language)}</td>
                <td className="px-5 py-4 font-medium text-slate-900">${transaction.amount}</td>
                <td className="px-5 py-4">${transaction.balance_before}</td>
                <td className="px-5 py-4">${transaction.balance_after}</td>
                <td className="px-5 py-4">{transaction.reference ?? "-"}</td>
                <td className="px-5 py-4 text-mute">{transaction.note ?? "-"}</td>
                <td className="px-5 py-4">{new Date(transaction.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </DataTable>
        </>
      ) : (
        <>
          <Card className="surface-muted">
            <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <h3 className="text-xl font-semibold tracking-[-0.03em] text-slate-900">{t("reconciliations")}</h3>
              <span className="stat-chip">{reconciliations.length} entries</span>
            </div>
            <form
              className="grid gap-3 md:grid-cols-4"
              onSubmit={async (event) => {
                event.preventDefault();
                await loadReconciliations();
              }}
            >
              <select
                className="field"
                value={reconciliationCustomerId}
                onChange={(event) => setReconciliationCustomerId(event.target.value)}
              >
                <option value="">{t("customer_label")}</option>
                {customers.map((customer) => (
                  <option key={customer.id} value={customer.id}>{`#${customer.id} - ${customer.full_name}`}</option>
                ))}
              </select>
              <select className="field" value={reconciliationChannel} onChange={(event) => setReconciliationChannel(event.target.value)}>
                <option value="">{t("reconciliation_all_channels")}</option>
                <option value="bank">{t("bank")}</option>
                <option value="usdt">{t("usdt")}</option>
              </select>
              <select className="field" value={reconciliationStatus} onChange={(event) => setReconciliationStatus(event.target.value)}>
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
            {reconciliationMessage ? <p className="mt-3 text-sm text-mute">{reconciliationMessage}</p> : null}
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
            {reconciliations.map((record) => (
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
                <td className="px-5 py-4">{record.reference || record.wallet_address || "-"}</td>
                <td className="px-5 py-4">{new Date(record.created_at).toLocaleString()}</td>
                <td className="px-5 py-4 text-xs text-mute">
                  <pre className="max-w-[320px] overflow-x-auto whitespace-pre-wrap break-all">
                    {JSON.stringify(record.raw_payload, null, 2)}
                  </pre>
                </td>
              </tr>
            ))}
          </DataTable>
        </>
      )}
    </div>
  );
}
