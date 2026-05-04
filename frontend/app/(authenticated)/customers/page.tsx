"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { Card } from "@/components/ui/card";
import { DataTable } from "@/components/ui/table";
import { apiClient } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { Customer } from "@/types";

export default function CustomersPage() {
  const { t } = useI18n();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [editingCustomerId, setEditingCustomerId] = useState<number | null>(null);
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

  function resetForm() {
    setEditingCustomerId(null);
    setFullName("");
    setEmail("");
    setPhone("");
  }

  async function submitCustomer(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);

    if (!email.trim()) {
      setMessage(t("email_required"));
      return;
    }

    const payload = {
      full_name: fullName,
      email: email.trim(),
      phone: phone.trim() || null
    };

    try {
      if (editingCustomerId) {
        await apiClient.patch(`/customers/${editingCustomerId}`, payload);
        setMessage(t("customer_updated"));
      } else {
        await apiClient.post("/customers", {
          ...payload,
          wallet_balance: "0.00",
          status: "active"
        });
        setMessage(t("create_customer_success"));
      }

      resetForm();
      await loadCustomers();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : editingCustomerId ? t("customer_update_failed") : t("create_customer_failed"));
    }
  }

  async function removeCustomer(customer: Customer) {
    setMessage(null);
    if (!window.confirm(t("customer_delete_confirm", { name: customer.full_name }))) {
      return;
    }

    try {
      await apiClient.delete(`/customers/${customer.id}`);
      setMessage(t("customer_deleted"));
      if (editingCustomerId === customer.id) {
        resetForm();
      }
      await loadCustomers();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : t("customer_delete_failed"));
    }
  }

  return (
    <div className="space-y-6">
      <Card className="surface-muted">
        <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="section-eyebrow">Customer Intake</p>
            <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-900">
              {editingCustomerId ? t("update_customer") : t("create_customer")}
            </h3>
          </div>
          <span className="stat-chip">{customers.length} records</span>
        </div>
        <form className="grid gap-3 md:grid-cols-4" onSubmit={submitCustomer}>
          <input className="field" placeholder={t("customer_name")} value={fullName} onChange={(event) => setFullName(event.target.value)} />
          <input className="field" placeholder={t("email")} type="email" required value={email} onChange={(event) => setEmail(event.target.value)} />
          <input className="field" placeholder={t("phone")} value={phone} onChange={(event) => setPhone(event.target.value)} />
          <div className="flex gap-3">
            <button className="btn-primary flex-1" type="submit">
              {editingCustomerId ? t("update_customer") : t("create_customer")}
            </button>
            {editingCustomerId ? (
              <button className="btn-secondary" onClick={resetForm} type="button">
                {t("cancel")}
              </button>
            ) : null}
          </div>
        </form>
        {message ? <p className="mt-3 text-sm text-mute">{message}</p> : null}
      </Card>
      <DataTable
        headers={[t("customer_table_id"), t("customer_table_name"), t("email"), t("customer_table_phone"), t("customer_table_wallet"), t("created_at"), t("operation")]}
      >
        {customers.map((customer) => (
          <tr key={customer.id} className="border-b border-[#edf2f8]">
            <td className="px-5 py-4 font-medium text-ink">#{customer.id}</td>
            <td className="px-5 py-4 font-medium text-ink">
              <Link className="transition hover:text-[#1d4ed8]" href={`/customers/${customer.id}`}>
                {customer.full_name}
              </Link>
            </td>
            <td className="px-5 py-4 text-mute">{customer.email ?? "-"}</td>
            <td className="px-5 py-4 text-mute">{customer.phone ?? "-"}</td>
            <td className="px-5 py-4 text-ink">${customer.wallet_balance}</td>
            <td className="px-5 py-4 text-mute">{new Date(customer.created_at).toLocaleDateString()}</td>
            <td className="px-5 py-4">
              <div className="flex gap-3">
                <Link
                  className="text-sm font-medium text-[#1d4ed8] transition hover:text-[#1e40af]"
                  href={`/customers/${customer.id}`}
                >
                  {t("view_detail")}
                </Link>
                <button
                  className="text-sm font-medium text-rose-600 transition hover:text-rose-700"
                  onClick={() => removeCustomer(customer)}
                  type="button"
                >
                  {t("delete")}
                </button>
              </div>
            </td>
          </tr>
        ))}
      </DataTable>
    </div>
  );
}
