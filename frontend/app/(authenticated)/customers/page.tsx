"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { DataTable } from "@/components/ui/table";
import { apiClient } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { Customer } from "@/types";

export default function CustomersPage() {
  const { t } = useI18n();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  async function loadCustomers() {
    apiClient.get<{ items: Customer[] }>("/customers").then((data) => setCustomers(data.items)).catch(() => setCustomers([]));
  }

  useEffect(() => {
    loadCustomers();
  }, []);

  async function createCustomer(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);
    try {
      await apiClient.post("/customers", {
        full_name: fullName,
        email: email || null,
        phone: phone || null,
        wallet_balance: "0.00",
        status: "active"
      });
      setFullName("");
      setEmail("");
      setPhone("");
      setMessage(t("create_customer_success"));
      await loadCustomers();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : t("create_customer_failed"));
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader title={t("customers")} />
      <Card className="surface-muted">
        <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="section-eyebrow">Customer Intake</p>
            <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-900">{t("create_customer")}</h3>
          </div>
          <span className="stat-chip">{customers.length} records</span>
        </div>
        <form className="grid gap-3 md:grid-cols-4" onSubmit={createCustomer}>
          <input className="field" placeholder={t("customer_name")} value={fullName} onChange={(event) => setFullName(event.target.value)} />
          <input className="field" placeholder={t("email")} value={email} onChange={(event) => setEmail(event.target.value)} />
          <input className="field" placeholder={t("phone")} value={phone} onChange={(event) => setPhone(event.target.value)} />
          <button className="btn-primary" type="submit">{t("create_customer")}</button>
        </form>
        {message ? <p className="mt-3 text-sm text-mute">{message}</p> : null}
      </Card>
      <DataTable
        headers={[t("customer_table_id"), t("customer_table_name"), t("email"), t("customer_table_phone"), t("customer_table_wallet"), t("status"), t("created_at")]}
      >
        {customers.map((customer) => (
          <tr key={customer.id} className="border-b border-[#edf2f8]">
            <td className="px-5 py-4 font-medium text-ink">#{customer.id}</td>
            <td className="px-5 py-4 font-medium text-ink">{customer.full_name}</td>
            <td className="px-5 py-4 text-mute">{customer.email ?? "-"}</td>
            <td className="px-5 py-4 text-mute">{customer.phone ?? "-"}</td>
            <td className="px-5 py-4 text-ink">${customer.wallet_balance}</td>
            <td className="px-5 py-4">
              <Badge tone={customer.status === "active" ? "success" : "danger"}>{customer.status === "active" ? t("active") : t("inactive")}</Badge>
            </td>
            <td className="px-5 py-4 text-mute">{new Date(customer.created_at).toLocaleDateString()}</td>
          </tr>
        ))}
      </DataTable>
    </div>
  );
}
