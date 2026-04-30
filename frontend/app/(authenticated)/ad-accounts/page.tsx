"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/ui/page-header";
import { DataTable } from "@/components/ui/table";
import { apiClient } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { formatPlatform } from "@/lib/display";
import { AdAccount } from "@/types";

export default function AdAccountsPage() {
  const { language, t } = useI18n();
  const [accounts, setAccounts] = useState<AdAccount[]>([]);
  const [message, setMessage] = useState<string | null>(null);

  async function loadAccounts() {
    apiClient.get<AdAccount[]>("/ad-accounts").then(setAccounts).catch(() => setAccounts([]));
  }

  useEffect(() => {
    loadAccounts();
  }, []);

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

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("ad_accounts")}
        action={<button className="btn-primary" onClick={syncAccounts}>{t("sync_facebook")}</button>}
      />
      {message ? <div className="stat-chip">{message}</div> : null}
      <DataTable
        headers={[t("account_id"), t("account_name"), t("status"), t("balance"), t("spend_today_table"), t("spend_7d"), t("platform"), t("last_synced")]}
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
            <td className="px-5 py-4">${account.spend_7d}</td>
            <td className="px-5 py-4">{formatPlatform(account.platform, language)}</td>
            <td className="px-5 py-4 text-mute">{account.last_synced_at ? new Date(account.last_synced_at).toLocaleString() : "-"}</td>
          </tr>
        ))}
      </DataTable>
    </div>
  );
}
