"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { DataTable } from "@/components/ui/table";
import { apiClient } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { formatFacebookPaymentStatus } from "@/lib/display";
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
      {message ? <div className="stat-chip">{message}</div> : null}
      <Card className="surface-muted">
        <div className="mb-4 flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex flex-wrap gap-2">
            <span className="stat-chip">{accounts.length} accounts</span>
            <span className="stat-chip">
              {t("payment_due")}: $
              {accounts.reduce((sum, account) => sum + Number(account.amount_due || 0), 0).toFixed(2)}
            </span>
            <span className="stat-chip">
              {t("prepaid_balance_label")}: $
              {accounts.reduce((sum, account) => sum + Number(account.prepaid_balance || 0), 0).toFixed(2)}
            </span>
            <span className="stat-chip">
              {t("payment_status")}: {accounts.filter((account) => account.payment_status === "overdue").length}
            </span>
          </div>
          <button className="btn-primary" onClick={syncAccounts} type="button">
            {t("sync_facebook")}
          </button>
        </div>
        <form className="grid gap-3 xl:grid-cols-[1.4fr_0.9fr_0.8fr_0.8fr_0.8fr_auto]" onSubmit={updatePaymentControl}>
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
          <button className="btn-secondary xl:h-full" type="submit" disabled={!editingAccountId}>
            {t("update_payment_control")}
          </button>
        </form>
      </Card>
      <DataTable
        headers={[
          t("account_id"),
          t("account_name"),
          t("status"),
          t("balance"),
          t("spend_today_table"),
          t("payment_due"),
          t("payment_status"),
        ]}
      >
        {accounts.map((account) => (
          <tr key={account.id} className="border-b border-[#edf2f8]">
            <td className="px-5 py-4">{account.account_id}</td>
            <td className="px-5 py-4 font-medium">{account.account_name}</td>
            <td className="px-5 py-4">
              <Badge tone={account.status === "ACTIVE" ? "success" : "danger"}>{account.status === "ACTIVE" ? t("active") : t("disabled")}</Badge>
            </td>
            <td className="px-5 py-4">${account.balance}</td>
            <td className="px-5 py-4">${account.spend_today}</td>
            <td className="px-5 py-4">${account.amount_due}</td>
            <td className="px-5 py-4">
              <Badge tone={account.payment_status === "healthy" ? "success" : account.payment_status === "due" ? "warning" : "danger"}>
                {formatFacebookPaymentStatus(account.payment_status, language)}
              </Badge>
            </td>
          </tr>
        ))}
      </DataTable>
    </div>
  );
}
