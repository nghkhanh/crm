"use client";

import { useEffect, useState } from "react";

import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { DataTable } from "@/components/ui/table";
import { apiClient } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { formatPlatform, formatTicketStatus, formatTicketType, formatTransactionType } from "@/lib/display";
import { AdAccount, Customer, CustomerUsdtAddress, Ticket, Transaction } from "@/types";

type CustomerDetails = {
  profile: Customer;
  ad_accounts: AdAccount[];
  recent_transactions: Transaction[];
  tickets: Ticket[];
  usdt_addresses: CustomerUsdtAddress[];
};

export default function CustomerDetailPage({ params }: { params: { id: string } }) {
  const { language, t } = useI18n();
  const [details, setDetails] = useState<CustomerDetails | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [usdtForm, setUsdtForm] = useState({ address: "", label: "" });

  async function loadDetails() {
    apiClient.get<CustomerDetails>(`/customers/${params.id}`).then(setDetails).catch(() => setDetails(null));
  }

  useEffect(() => {
    loadDetails();
  }, [params.id]);

  if (!details) {
    return <div className="text-sm text-mute">{t("customer_profile_loading")}</div>;
  }

  return (
    <div className="space-y-6">
      <PageHeader title={details.profile.full_name} description={t("customer_detail_description")} />
      <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <Card>
          <h3 className="text-lg font-semibold text-ink">{t("profile")}</h3>
          <form
            className="mt-4 grid gap-3 text-sm"
            onSubmit={async (event) => {
              event.preventDefault();
              setMessage(null);
              try {
                await apiClient.patch(`/customers/${params.id}`, {
                  full_name: details.profile.full_name,
                  email: details.profile.email || null,
                  phone: details.profile.phone || null,
                  status: details.profile.status,
                  note: details.profile.note || null
                });
                setMessage(t("customer_updated"));
                await loadDetails();
              } catch (error) {
                setMessage(error instanceof Error ? error.message : t("customer_update_failed"));
              }
            }}
          >
            <input className="rounded-2xl border border-line px-4 py-3" value={details.profile.full_name} onChange={(event) => setDetails((current) => current ? { ...current, profile: { ...current.profile, full_name: event.target.value } } : current)} />
            <input className="rounded-2xl border border-line px-4 py-3" value={details.profile.email ?? ""} onChange={(event) => setDetails((current) => current ? { ...current, profile: { ...current.profile, email: event.target.value } } : current)} />
            <input className="rounded-2xl border border-line px-4 py-3" value={details.profile.phone ?? ""} onChange={(event) => setDetails((current) => current ? { ...current, profile: { ...current.profile, phone: event.target.value } } : current)} />
            <select className="rounded-2xl border border-line px-4 py-3" value={details.profile.status} onChange={(event) => setDetails((current) => current ? { ...current, profile: { ...current.profile, status: event.target.value as Customer["status"] } } : current)}>
              <option value="active">{t("active")}</option>
              <option value="inactive">{t("inactive")}</option>
            </select>
            <textarea className="rounded-2xl border border-line px-4 py-3" rows={3} value={details.profile.note ?? ""} onChange={(event) => setDetails((current) => current ? { ...current, profile: { ...current.profile, note: event.target.value } } : current)} />
            <p>{t("wallet_balance")}: ${details.profile.wallet_balance}</p>
            <button className="rounded-2xl bg-brand px-4 py-3 text-sm font-semibold text-white" type="submit">{t("update_customer")}</button>
            {message ? <p className="text-sm text-mute">{message}</p> : null}
          </form>
        </Card>
        <Card>
          <h3 className="text-lg font-semibold text-ink">{t("tickets_label")}</h3>
          <div className="mt-4 space-y-3 text-sm text-mute">
            {details.tickets.length ? details.tickets.map((ticket) => <p key={ticket.id}>#{ticket.id} · {formatTicketType(ticket.type, language)} · {formatTicketStatus(ticket.status, language)}</p>) : <p>{t("no_tickets")}</p>}
          </div>
        </Card>
      </div>
      <Card>
        <div className="flex items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-ink">{t("usdt_deposit_addresses")}</h3>
            <p className="mt-1 text-sm text-mute">{t("usdt_deposit_addresses_description")}</p>
          </div>
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_0.6fr_auto]">
          <input
            className="field"
            placeholder={t("usdt_address")}
            value={usdtForm.address}
            onChange={(event) => setUsdtForm((current) => ({ ...current, address: event.target.value }))}
          />
          <input
            className="field"
            placeholder={t("label")}
            value={usdtForm.label}
            onChange={(event) => setUsdtForm((current) => ({ ...current, label: event.target.value }))}
          />
          <button
            className="btn-primary"
            onClick={async () => {
              setMessage(null);
              try {
                await apiClient.post(`/customers/${params.id}/usdt-addresses`, {
                  address: usdtForm.address,
                  label: usdtForm.label || null,
                  network: "trc20",
                });
                setUsdtForm({ address: "", label: "" });
                setMessage(t("usdt_address_added"));
                await loadDetails();
              } catch (error) {
                setMessage(error instanceof Error ? error.message : t("usdt_address_add_failed"));
              }
            }}
          >
            {t("add_usdt_address")}
          </button>
        </div>
        <div className="mt-4 space-y-3">
          {details.usdt_addresses.length ? (
            details.usdt_addresses.map((address) => (
              <div key={address.id} className="rounded-[18px] border border-line px-4 py-4">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="font-medium text-ink">{address.address}</p>
                    <p className="mt-1 text-sm text-mute">
                      {(address.label || t("no_label"))} · {address.network.toUpperCase()} · {address.status}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      {t("last_seen")}: {address.last_seen_at ? new Date(address.last_seen_at).toLocaleString() : "-"}
                    </p>
                  </div>
                  <button
                    className="btn-secondary"
                    onClick={async () => {
                      setMessage(null);
                      try {
                        await apiClient.patch(`/customers/${params.id}/usdt-addresses/${address.id}`, {
                          status: address.status === "active" ? "inactive" : "active",
                        });
                        await loadDetails();
                      } catch (error) {
                        setMessage(error instanceof Error ? error.message : t("usdt_address_update_failed"));
                      }
                    }}
                  >
                    {address.status === "active" ? t("deactivate") : t("activate")}
                  </button>
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-mute">{t("no_usdt_addresses")}</p>
          )}
        </div>
      </Card>
      <DataTable headers={[t("account_id"), t("account_name"), t("platform"), t("status"), t("balance"), t("spend_today_table")]}>
        {details.ad_accounts.map((account) => (
          <tr key={account.id} className="border-t border-line">
            <td className="px-4 py-4">{account.account_id}</td>
            <td className="px-4 py-4">{account.account_name}</td>
            <td className="px-4 py-4">{formatPlatform(account.platform, language)}</td>
            <td className="px-4 py-4">{account.status === "ACTIVE" ? t("active") : t("disabled")}</td>
            <td className="px-4 py-4">${account.balance}</td>
            <td className="px-4 py-4">${account.spend_today}</td>
          </tr>
        ))}
      </DataTable>
      <DataTable headers={[t("type"), t("amount"), t("reference"), t("created_at")]}>
        {details.recent_transactions.map((transaction) => (
          <tr key={transaction.id} className="border-t border-line">
            <td className="px-4 py-4">{formatTransactionType(transaction.type, language)}</td>
            <td className="px-4 py-4">${transaction.amount}</td>
            <td className="px-4 py-4">{transaction.reference ?? "-"}</td>
            <td className="px-4 py-4">{new Date(transaction.created_at).toLocaleString()}</td>
          </tr>
        ))}
      </DataTable>
    </div>
  );
}
