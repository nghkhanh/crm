"use client";

import { useEffect, useMemo, useState } from "react";

import { DataTable } from "@/components/ui/table";
import { apiClient } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { StaffMember } from "@/types";

function roleLabel(role: StaffMember["role"]) {
  if (role === "admin") return "Quản trị";
  if (role === "sub_admin") return "Điều hành";
  if (role === "accountant") return "Kế toán";
  if (role === "cs") return "Chăm sóc khách hàng";
  return "Điều hành";
}

export default function PersonnelManagementPage() {
  const { t } = useI18n();
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    role: "sub_admin",
    phone: "",
    team_name: "",
    status: "enabled",
  });
  const [resetPasswordValue, setResetPasswordValue] = useState("");

  const loadStaff = () => apiClient.get<StaffMember[]>("/auth/staff").then(setStaff).catch(() => setStaff([]));

  useEffect(() => {
    loadStaff();
  }, []);

  const filteredStaff = useMemo(() => staff, [staff]);

  async function submitPersonnel() {
    setMessage(null);
    if (editingId) {
      const updated = await apiClient.patch<StaffMember>(`/auth/staff/${editingId}`, {
        full_name: form.full_name,
        role: form.role,
        phone: form.phone || null,
        status: form.status,
      });
      setStaff((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setMessage(t("personnel_saved_success"));
    } else {
      const created = await apiClient.post<StaffMember>("/auth/staff", {
        full_name: form.full_name,
        email: form.email,
        password: form.password,
        role: form.role,
        phone: form.phone || null,
        status: form.status,
      });
      setStaff((current) => [created, ...current]);
      setMessage(t("personnel_created_success"));
    }
    setEditingId(null);
    setResetPasswordValue("");
    setForm({
      full_name: "",
      email: "",
      password: "",
      role: "sub_admin",
      phone: "",
      team_name: "",
      status: "enabled",
    });
  }

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] border border-[#e3eaf4] bg-white p-6 shadow-[0_10px_30px_rgba(15,23,42,0.05)]">
        <div className="flex items-center justify-between gap-4">
          <h3 className="text-xl font-semibold tracking-[-0.03em] text-slate-900">
            {editingId ? t("edit_personnel") : t("add_personnel")}
          </h3>
          {editingId ? (
            <button
              className="btn-secondary"
              onClick={() => {
                setEditingId(null);
                setForm({ full_name: "", email: "", password: "", role: "sub_admin", phone: "", team_name: "", status: "enabled" });
              }}
            >
              {t("cancel")}
            </button>
          ) : null}
        </div>
        {message ? <p className="mt-4 text-sm text-mute">{message}</p> : null}

        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">{t("personnel_name")}</label>
            <input className="field" value={form.full_name} onChange={(event) => setForm((current) => ({ ...current, full_name: event.target.value }))} />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">{t("email")}</label>
            <input className="field" value={form.email} disabled={editingId !== null} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">{t("password")}</label>
            <input
              className="field"
              type="password"
              disabled={editingId !== null}
              placeholder={editingId ? t("password_edit_hint") : ""}
              value={form.password}
              onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
            />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">{t("role")}</label>
            <select className="field" value={form.role} onChange={(event) => setForm((current) => ({ ...current, role: event.target.value }))}>
              <option value="admin">Quản trị</option>
              <option value="sub_admin">Điều hành</option>
              <option value="cs">Chăm sóc khách hàng</option>
              <option value="accountant">Kế toán</option>
            </select>
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">{t("mobile_phone_number")}</label>
            <input className="field" value={form.phone} onChange={(event) => setForm((current) => ({ ...current, phone: event.target.value }))} />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">{t("status")}</label>
            <select className="field" value={form.status} onChange={(event) => setForm((current) => ({ ...current, status: event.target.value }))}>
              <option value="enabled">{t("enabled")}</option>
              <option value="disabled">{t("disabled")}</option>
            </select>
          </div>
          <div className="flex items-end">
            <button className="btn-primary w-full" onClick={() => void submitPersonnel()}>
              {editingId ? t("save_personnel") : t("add_personnel")}
            </button>
          </div>
        </div>
        {editingId ? (
          <div className="mt-6 grid gap-4 md:grid-cols-[1fr_auto]">
            <input
              className="field"
              type="password"
              placeholder={t("new_password")}
              value={resetPasswordValue}
              onChange={(event) => setResetPasswordValue(event.target.value)}
            />
            <button
              className="btn-secondary"
              onClick={async () => {
                setMessage(null);
                try {
                  await apiClient.post("/auth/admin/reset-password", {
                    email: form.email,
                    new_password: resetPasswordValue,
                  });
                  setResetPasswordValue("");
                  setMessage(t("password_reset_success"));
                } catch (error) {
                  setMessage(error instanceof Error ? error.message : t("password_reset_failed"));
                }
              }}
            >
              {t("reset_password")}
            </button>
          </div>
        ) : null}
      </section>

      <DataTable
        headers={[
          t("personnel_name"),
          t("email"),
          t("mobile_phone_number"),
          t("role"),
          t("status"),
          t("operation"),
        ]}
      >
        {filteredStaff.map((member) => (
          <tr key={member.id} className="border-b border-[#edf2f8]">
            <td className="px-5 py-4 font-medium text-slate-900">{member.full_name}</td>
            <td className="px-5 py-4 text-slate-600">{member.email}</td>
            <td className="px-5 py-4 text-slate-600">{member.phone || "--"}</td>
            <td className="px-5 py-4 text-slate-600">{roleLabel(member.role)}</td>
            <td className="px-5 py-4">
              <span
                className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                  member.status === "enabled" ? "bg-[#ecfdf3] text-[#15803d]" : "bg-[#fef2f2] text-[#b91c1c]"
                }`}
              >
                {member.status === "enabled" ? t("enabled") : t("disabled")}
              </span>
            </td>
            <td className="px-5 py-4">
              <div className="flex gap-2">
                <button
                  className="rounded-[14px] border border-[#dbe5f0] bg-[#f8fbff] px-3 py-2 text-xs font-semibold text-slate-700"
                  onClick={() => {
                    setEditingId(member.id);
                    setResetPasswordValue("");
                    setForm({
                      full_name: member.full_name,
                      email: member.email,
                      password: "",
                      role: member.role,
                      phone: member.phone || "",
                      team_name: member.team_name || "",
                      status: member.status,
                    });
                  }}
                >
                  {t("edit")}
                </button>
                <button
                  className="rounded-[14px] border border-[#dbe5f0] bg-[#f8fbff] px-3 py-2 text-xs font-semibold text-slate-700"
                  onClick={async () => {
                    setMessage(null);
                    try {
                      const updated = await apiClient.patch<StaffMember>(`/auth/staff/${member.id}`, {
                        status: member.status === "enabled" ? "disabled" : "enabled",
                      });
                      setStaff((current) => current.map((item) => (item.id === updated.id ? updated : item)));
                    } catch (error) {
                      setMessage(error instanceof Error ? error.message : t("ticket_update_failed"));
                    }
                  }}
                >
                  {member.status === "enabled" ? t("deactivate") : t("activate")}
                </button>
              </div>
            </td>
          </tr>
        ))}
      </DataTable>
    </div>
  );
}
