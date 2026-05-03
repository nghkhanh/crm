"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { DataTable } from "@/components/ui/table";
import { apiClient } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { formatFacebookPaymentStatus, formatPlatform, formatSpendProvider } from "@/lib/display";
import { AdAccount } from "@/types";

export default function AdAccountsPage() {
  const { language, t } = useI18n();
  const [accounts, setAccounts] = useState<AdAccount[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [editingAccountId, setEditingAccountId] = useState("");
  const [editForm, setEditForm] = useState({
    spend_provider: "facebook_graph",
    amount_due: "",
    prepaid_balance: "",
    payment_threshold: "",
  });

  async function loadAccounts() {
    apiClient.get<AdAccount[]>("/ad-accounts").then(setAccounts).catch(() => setAccounts([]));
  }

  function applyAccountToForm(account: AdAccount | undefined) {
    if (!account) {
      setEditForm({
        spend_provider: "facebook_graph",
        amount_due: "",
        prepaid_balance: "",
        payment_threshold: "",
      });
      return;
    }
    setEditForm({
      spend_provider: account.spend_provider,
      amount_due: account.amount_due,
      prepaid_balance: account.prepaid_balance,
      payment_threshold: account.payment_threshold,
    });
  }

  useEffect(() => {
    loadAccounts();
  }, []);

  useEffect(() => {
    if (!accounts.length) {
      setEditingAccountId("");
      applyAccountToForm(undefined);
      return;
    }
    const matchedAccount = accounts.find((account) => String(account.id) === editingAccountId);
    if (matchedAccount) {
      applyAccountToForm(matchedAccount);
      return;
    }
    const nextAccount = accounts[0];
    setEditingAccountId(String(nextAccount.id));
    applyAccountToForm(nextAccount);
  }, [accounts, editingAccountId]);

  async function syncAccounts() {
    setMessage(null);
    try {
      const result = await apiClient.post<{ synced: number; failed: number }>("/ad-accounts/sync");
      setMessage(t("sync_success", { synced: result.synced, failed: result.failed }));
      await loadAccounts();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : t("sync_failed"));
    }
  }

  async function updatePaymentControl(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editingAccountId) {
      return;
    }
    setMessage(null);
    try {
      await apiClient.patch(`/ad-accounts/${editingAccountId}`, {
        spend_provider: editForm.spend_provider,
        amount_due: editForm.amount_due || "0",
        prepaid_balance: editForm.prepaid_balance || "0",
        payment_threshold: editForm.payment_threshold || "0",
      });
      setMessage(t("ad_account_updated"));
      await loadAccounts();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : t("ad_account_update_failed"));
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("ad_accounts")}
        action={<button className="btn-primary" onClick={syncAccounts}>{t("sync_facebook")}</button>}
      />
      {message ? <div className="stat-chip">{message}</div> : null}
      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded-[22px] border border-[#e3eaf4] bg-white p-4">
          <p className="text-sm text-mute">{t("payment_due")}</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            $
            {accounts
              .reduce((sum, account) => sum + Number(account.amount_due || 0), 0)
              .toFixed(2)}
          </p>
        </div>
        <div className="rounded-[22px] border border-[#e3eaf4] bg-white p-4">
          <p className="text-sm text-mute">{t("prepaid_balance_label")}</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            $
            {accounts
              .reduce((sum, account) => sum + Number(account.prepaid_balance || 0), 0)
              .toFixed(2)}
          </p>
        </div>
        <div className="rounded-[22px] border border-[#e3eaf4] bg-white p-4">
          <p className="text-sm text-mute">{t("payment_status")}</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {accounts.filter((account) => account.payment_status === "overdue").length}
          </p>
          <p className="mt-1 text-sm text-mute">{language === "vi" ? "tài khoản rủi ro" : "accounts at risk"}</p>
        </div>
      </div>
      <Card className="surface-muted">
        <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <h3 className="text-xl font-semibold tracking-[-0.03em] text-slate-900">{t("payment_control")}</h3>
        </div>
        <form className="grid gap-3 md:grid-cols-5" onSubmit={updatePaymentControl}>
          <select
            className="field"
            value={editingAccountId}
            onChange={(event) => {
              const nextId = event.target.value;
              setEditingAccountId(nextId);
              applyAccountToForm(accounts.find((account) => String(account.id) === nextId));
            }}
          >
            <option value="">{t("ad_account_select")}</option>
            {accounts.map((account) => (
              <option key={account.id} value={account.id}>{`${account.account_name} (#${account.account_id})`}</option>
            ))}
          </select>
          <select
            className="field"
            value={editForm.spend_provider}
            onChange={(event) => setEditForm((current) => ({ ...current, spend_provider: event.target.value }))}
          >
            <option value="facebook_graph">Facebook API</option>
            <option value="smit">SMIT</option>
          </select>
          <input
            className="field"
            placeholder={t("payment_due")}
            value={editForm.amount_due}
            onChange={(event) => setEditForm((current) => ({ ...current, amount_due: event.target.value }))}
          />
          <input
            className="field"
            placeholder={t("prepaid_balance_label")}
            value={editForm.prepaid_balance}
            onChange={(event) => setEditForm((current) => ({ ...current, prepaid_balance: event.target.value }))}
          />
          <input
            className="field"
            placeholder={t("payment_threshold_label")}
            value={editForm.payment_threshold}
            onChange={(event) => setEditForm((current) => ({ ...current, payment_threshold: event.target.value }))}
          />
          <div className="md:col-span-5 flex justify-end">
            <button className="btn-primary" type="submit" disabled={!editingAccountId}>
              {t("update_payment_control")}
            </button>
          </div>
        </form>
      </Card>
      <DataTable
        headers={[
          t("account_id"),
          t("account_name"),
          t("status"),
          t("spend_provider"),
          t("balance"),
          t("spend_today_table"),
          t("spend_7d"),
          t("payment_due"),
          t("prepaid_balance_label"),
          t("payment_threshold_label"),
          t("payment_status"),
          t("platform"),
          t("last_synced"),
        ]}
      >
        {accounts.map((account) => (
          <tr key={account.id} className="border-b border-[#edf2f8]">
            <td className="px-5 py-4">{account.account_id}</td>
            <td className="px-5 py-4 font-medium">{account.account_name}</td>
            <td className="px-5 py-4">
              <Badge tone={account.status === "ACTIVE" ? "success" : "danger"}>{account.status === "ACTIVE" ? t("active") : t("disabled")}</Badge>
            </td>
            <td className="px-5 py-4">{formatSpendProvider(account.spend_provider, language)}</td>
            <td className="px-5 py-4">${account.balance}</td>
            <td className="px-5 py-4">${account.spend_today}</td>
            <td className="px-5 py-4">${account.spend_7d}</td>
            <td className="px-5 py-4">${account.amount_due}</td>
            <td className="px-5 py-4">${account.prepaid_balance}</td>
            <td className="px-5 py-4">${account.payment_threshold}</td>
            <td className="px-5 py-4">
              <Badge tone={account.payment_status === "healthy" ? "success" : account.payment_status === "due" ? "warning" : "danger"}>
                {formatFacebookPaymentStatus(account.payment_status, language)}
              </Badge>
            </td>
            <td className="px-5 py-4">{formatPlatform(account.platform, language)}</td>
            <td className="px-5 py-4 text-mute">{account.last_synced_at ? new Date(account.last_synced_at).toLocaleString() : "-"}</td>
          </tr>
        ))}
      </DataTable>
    </div>
  );
}
