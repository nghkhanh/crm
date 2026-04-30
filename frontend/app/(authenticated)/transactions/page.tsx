"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { DataTable } from "@/components/ui/table";
import { apiClient } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { formatTransactionSource, formatTransactionStatus, formatTransactionType } from "@/lib/display";
import { Customer, Transaction } from "@/types";

export default function TransactionsPage() {
  const { language, t } = useI18n();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customerId, setCustomerId] = useState("");
  const [type, setType] = useState("topup_bank");
  const [amount, setAmount] = useState("");
  const [reference, setReference] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  async function loadTransactions() {
    apiClient.get<Transaction[]>("/transactions").then(setTransactions).catch(() => setTransactions([]));
  }

  useEffect(() => {
    loadTransactions();
    apiClient.get<{ items: Customer[] }>("/customers").then((data) => setCustomers(data.items)).catch(() => setCustomers([]));
  }, []);

  async function createTransaction(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);
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
      setMessage(t("create_transaction_success"));
      await loadTransactions();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : t("create_transaction_failed"));
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader title={t("transactions")} />
      <Card className="surface-muted">
        <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="section-eyebrow">Wallet Control</p>
            <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-900">{t("create_transaction")}</h3>
          </div>
          <div className="flex items-center gap-2">
            <span className="stat-chip">{transactions.length} entries</span>
            <Link className="btn-secondary" href="/reconciliations">
              {t("reconciliations")}
            </Link>
          </div>
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
        {message ? <p className="mt-3 text-sm text-mute">{message}</p> : null}
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
    </div>
  );
}
