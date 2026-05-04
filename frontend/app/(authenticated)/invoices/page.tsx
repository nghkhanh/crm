"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { DataTable } from "@/components/ui/table";
import { apiClient } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { useI18n } from "@/lib/i18n";
import { Customer, Invoice } from "@/types";

const PUBLIC_API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api").replace(/\/api$/, "");

export default function InvoicesPage() {
  const { t } = useI18n();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customerId, setCustomerId] = useState("");
  const [filterCustomerId, setFilterCustomerId] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  async function openInvoice(invoiceId: number) {
    setMessage(null);
    const token = getAccessToken();
    if (!token) {
      setMessage(t("login_failed"));
      return;
    }

    try {
      const response = await fetch(`${PUBLIC_API_BASE}/api/invoices/${invoiceId}/export`, {
        headers: {
          Authorization: `Bearer ${token}`
        },
        cache: "no-store"
      });

      if (!response.ok) {
        let detail = `Yeu cau that bai: ${response.status}`;
        try {
          const payload = await response.json();
          if (typeof payload?.detail === "string") {
            detail = payload.detail;
          }
        } catch {
          detail = `Yeu cau that bai: ${response.status}`;
        }
        throw new Error(detail);
      }

      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      window.open(objectUrl, "_blank", "noopener,noreferrer");
      window.setTimeout(() => URL.revokeObjectURL(objectUrl), 60_000);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : t("invoice_open_failed"));
    }
  }

  async function loadInvoices() {
    const params = new URLSearchParams();
    if (filterCustomerId) {
      params.set("customer_id", filterCustomerId);
    }
    if (filterStatus) {
      params.set("status", filterStatus);
    }
    const query = params.toString() ? `?${params.toString()}` : "";
    apiClient.get<Invoice[]>(`/invoices${query}`).then(setInvoices).catch(() => setInvoices([]));
  }

  useEffect(() => {
    loadInvoices();
    apiClient.get<{ items: Customer[] }>("/customers").then((data) => setCustomers(data.items)).catch(() => setCustomers([]));
  }, [filterCustomerId, filterStatus]);

  return (
    <div className="space-y-6">
      <Card className="surface-muted">
        <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="section-eyebrow">Billing Run</p>
            <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-900">{t("generate_invoice")}</h3>
          </div>
          <span className="stat-chip">{invoices.length} invoices</span>
        </div>
        <form
          className="grid gap-3 md:grid-cols-4"
          onSubmit={async (event) => {
            event.preventDefault();
            try {
              await apiClient.post("/invoices/generate", {
                customer_id: Number(customerId),
                period_start: periodStart,
                period_end: periodEnd
              });
              setMessage(t("invoice_generated"));
              await loadInvoices();
            } catch (error) {
              setMessage(error instanceof Error ? error.message : t("invoice_generate_failed"));
            }
          }}
        >
          <select className="field" value={customerId} onChange={(event) => setCustomerId(event.target.value)}>
            <option value="">{t("customer_label")}</option>
            {customers.map((customer) => (
              <option key={customer.id} value={customer.id}>{`#${customer.id} - ${customer.full_name}`}</option>
            ))}
          </select>
          <input className="field" type="date" value={periodStart} onChange={(event) => setPeriodStart(event.target.value)} />
          <input className="field" type="date" value={periodEnd} onChange={(event) => setPeriodEnd(event.target.value)} />
          <button className="btn-primary" type="submit">{t("generate_invoice")}</button>
        </form>
        {message ? <p className="mt-3 text-sm text-mute">{message}</p> : null}
      </Card>
      <Card className="surface-muted">
        <div className="grid gap-3 md:grid-cols-2">
          <select className="field" value={filterCustomerId} onChange={(event) => setFilterCustomerId(event.target.value)}>
            <option value="">{t("customer_label")}</option>
            {customers.map((customer) => (
              <option key={customer.id} value={customer.id}>{`#${customer.id} - ${customer.full_name}`}</option>
            ))}
          </select>
          <select className="field" value={filterStatus} onChange={(event) => setFilterStatus(event.target.value)}>
            <option value="">{t("status")}</option>
            <option value="draft">{t("draft")}</option>
            <option value="sent">{t("sent")}</option>
            <option value="paid">{t("paid")}</option>
          </select>
        </div>
      </Card>
      <DataTable
        headers={[t("invoice_number"), t("customer_id_name"), t("period"), t("total_topup"), t("fee"), t("commission"), t("status")]}
      >
        {invoices.map((invoice) => (
          <tr key={invoice.id} className="border-b border-[#edf2f8]">
            <td className="px-5 py-4">
              <div className="flex flex-col gap-2">
                <span className="font-medium text-slate-900">{invoice.invoice_number ?? `#${invoice.id}`}</span>
                {invoice.file_url ? (
                  <button
                    className="text-left text-sm font-medium text-[#1d4ed8]"
                    onClick={() => openInvoice(invoice.id)}
                    type="button"
                  >
                    {t("invoice_open")}
                  </button>
                ) : null}
              </div>
            </td>
            <td className="px-5 py-4">
              <div className="flex flex-col">
                <span className="font-medium text-ink">#{invoice.customer_id}</span>
                <span className="text-mute">{customers.find((customer) => customer.id === invoice.customer_id)?.full_name ?? "-"}</span>
              </div>
            </td>
            <td className="px-5 py-4">{invoice.period_start} {t("from_to")} {invoice.period_end}</td>
            <td className="px-5 py-4">${invoice.total_topup}</td>
            <td className="px-5 py-4">${invoice.total_fee}</td>
            <td className="px-5 py-4">${invoice.total_commission}</td>
            <td className="px-5 py-4">
              <div className="flex items-center gap-2">
                <Badge tone={invoice.status === "paid" ? "success" : invoice.status === "sent" ? "warning" : "neutral"}>{invoice.status === "paid" ? t("paid") : invoice.status === "sent" ? t("sent") : t("draft")}</Badge>
                <select
                  className="field max-w-[150px] py-2"
                  value={invoice.status}
                  onChange={async (event) => {
                    try {
                      await apiClient.patch(`/invoices/${invoice.id}/status`, { status: event.target.value, file_url: invoice.file_url ?? null });
                      setMessage(t("invoice_status_updated"));
                      await loadInvoices();
                    } catch (error) {
                      setMessage(error instanceof Error ? error.message : t("invoice_status_failed"));
                    }
                  }}
                >
                  <option value="draft">{t("draft")}</option>
                  <option value="sent">{t("sent")}</option>
                  <option value="paid">{t("paid")}</option>
                </select>
              </div>
            </td>
          </tr>
        ))}
      </DataTable>
    </div>
  );
}
