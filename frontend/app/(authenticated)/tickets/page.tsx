"use client";

import { useEffect, useMemo, useState } from "react";

import { Card } from "@/components/ui/card";
import { apiClient } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { formatPlatform, formatTicketStatus, formatTicketType } from "@/lib/display";
import { Customer, Ticket, TicketTimelineEntry, UserProfile } from "@/types";

const columns: Ticket["status"][] = ["pending", "processing", "done", "rejected"];

export default function TicketsPage() {
  const { language, t } = useI18n();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [staff, setStaff] = useState<UserProfile[]>([]);
  const [customerId, setCustomerId] = useState("");
  const [assignedTo, setAssignedTo] = useState("");
  const [ticketType, setTicketType] = useState("support");
  const [platform, setPlatform] = useState("facebook");
  const [note, setNote] = useState("");
  const [filterAssignedTo, setFilterAssignedTo] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [expandedTicketId, setExpandedTicketId] = useState<number | null>(null);
  const [timelineByTicket, setTimelineByTicket] = useState<Record<number, TicketTimelineEntry[]>>({});

  async function loadTickets() {
    const query = filterAssignedTo ? `?assigned_to=${filterAssignedTo}` : "";
    apiClient.get<Ticket[]>(`/tickets${query}`).then(setTickets).catch(() => setTickets([]));
  }

  useEffect(() => {
    loadTickets();
    apiClient.get<{ items: Customer[] }>("/customers").then((data) => setCustomers(data.items)).catch(() => setCustomers([]));
    apiClient.get<UserProfile[]>("/auth/staff").then(setStaff).catch(() => setStaff([]));
  }, [filterAssignedTo]);

  const grouped = useMemo(
    () =>
      columns.reduce<Record<string, Ticket[]>>((acc, status) => {
        acc[status] = tickets.filter((ticket) => ticket.status === status);
        return acc;
      }, {}),
    [tickets]
  );

  const customerMap = useMemo(
    () => Object.fromEntries(customers.map((customer) => [customer.id, customer.full_name])),
    [customers]
  );

  async function loadTimeline(ticketId: number) {
    const timeline = await apiClient.get<TicketTimelineEntry[]>(`/tickets/${ticketId}/timeline`);
    setTimelineByTicket((current) => ({ ...current, [ticketId]: timeline }));
  }

  return (
    <div className="space-y-6">
      <Card className="surface-muted">
        <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="section-eyebrow">Support Desk</p>
            <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-900">{t("create_ticket")}</h3>
          </div>
          <span className="stat-chip">{tickets.length} tickets</span>
        </div>
        <form
          className="grid gap-3 md:grid-cols-2 xl:grid-cols-5"
          onSubmit={async (event) => {
            event.preventDefault();
            setMessage(null);
            try {
              await apiClient.post("/tickets", {
                customer_id: Number(customerId),
                assigned_to: assignedTo ? Number(assignedTo) : null,
                type: ticketType,
                platform,
                priority: "normal",
                note: note || null,
                form_data: {}
              });
              setCustomerId("");
              setAssignedTo("");
              setTicketType("support");
              setPlatform("facebook");
              setNote("");
              setMessage(t("create_ticket_success"));
              await loadTickets();
            } catch (error) {
              setMessage(error instanceof Error ? error.message : t("create_ticket_failed"));
            }
          }}
        >
          <select className="field" value={customerId} onChange={(event) => setCustomerId(event.target.value)}>
            <option value="">{t("customer_label")}</option>
            {customers.map((customer) => (
              <option key={customer.id} value={customer.id}>{`#${customer.id} - ${customer.full_name}`}</option>
            ))}
          </select>
          <select className="field" value={assignedTo} onChange={(event) => setAssignedTo(event.target.value)}>
            <option value="">{t("ticket_assignee")}</option>
            {staff.map((user) => (
              <option key={user.id} value={user.id}>{user.full_name}</option>
            ))}
          </select>
          <select className="field" value={ticketType} onChange={(event) => setTicketType(event.target.value)}>
            <option value="support">{t("support")}</option>
            <option value="open_account">{t("open_account")}</option>
          </select>
          <select className="field" value={platform} onChange={(event) => setPlatform(event.target.value)}>
            <option value="facebook">Facebook</option>
            <option value="tiktok">TikTok</option>
            <option value="google">Google</option>
          </select>
          <input className="field xl:col-span-2" placeholder={t("note")} value={note} onChange={(event) => setNote(event.target.value)} />
          <button className="btn-primary" type="submit">{t("create_ticket")}</button>
        </form>
        {message ? <p className="mt-3 text-sm text-mute">{message}</p> : null}
      </Card>
      <Card className="surface-muted">
        <div className="grid gap-3 md:grid-cols-3">
          <select className="field" value={filterAssignedTo} onChange={(event) => setFilterAssignedTo(event.target.value)}>
            <option value="">{t("ticket_all_assignees")}</option>
            {staff.map((user) => (
              <option key={user.id} value={user.id}>{user.full_name}</option>
            ))}
          </select>
        </div>
      </Card>
      <div className="grid gap-4 xl:grid-cols-4">
        {columns.map((status) => (
          <Card key={status} className="surface-muted">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-mute">{t(status)}</h3>
              <span className="stat-chip">{grouped[status]?.length ?? 0}</span>
            </div>
            <div className="space-y-3">
              {(grouped[status] ?? []).map((ticket) => (
                <div key={ticket.id} className="rounded-[22px] border border-[#dbe5f0] bg-white p-4 shadow-[0_8px_20px_rgba(15,23,42,0.04)]">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <h4 className="truncate text-base font-semibold tracking-[-0.02em] text-slate-900">
                        {customerMap[ticket.customer_id] ?? `#${ticket.customer_id}`}
                      </h4>
                    </div>
                    <span className="rounded-full bg-[#f3f7fc] px-3 py-1 text-xs font-medium text-slate-600">
                      #{ticket.id}
                    </span>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2 text-xs">
                    <span className="rounded-full bg-[#f3f7fc] px-3 py-1 font-medium text-slate-600">
                      {formatTicketType(ticket.type, language)}
                    </span>
                    <span className="rounded-full bg-[#f3f7fc] px-3 py-1 font-medium text-slate-600">
                      {formatPlatform(ticket.platform, language)}
                    </span>
                  </div>
                  {ticket.note ? (
                    <div className="mt-3 rounded-[16px] bg-[#f8fbff] px-3 py-3 text-sm text-slate-600">
                      {ticket.note}
                    </div>
                  ) : null}
                  <p className="mt-3 text-sm text-slate-500">
                    {t("ticket_assignee")}: {ticket.assigned_user_name || "-"}
                  </p>
                  {expandedTicketId === ticket.id ? (
                    <div className="mt-4 rounded-[18px] border border-[#e8eef7] bg-[#f8fbff] p-4 text-sm text-slate-600">
                      <p><span className="font-semibold text-slate-900">{t("ticket_customer_label")} :</span> {customerMap[ticket.customer_id] ?? `#${ticket.customer_id}`}</p>
                      <p className="mt-2"><span className="font-semibold text-slate-900">{t("ticket_platform_label")} :</span> {formatPlatform(ticket.platform, language)}</p>
                      <p className="mt-2"><span className="font-semibold text-slate-900">{t("ticket_status_label")} :</span> {formatTicketStatus(ticket.status, language)}</p>
                      <p className="mt-2"><span className="font-semibold text-slate-900">ID :</span> #{ticket.id}</p>
                      <div className="mt-4 border-t border-[#e2e8f0] pt-4">
                        <p className="font-semibold text-slate-900">{t("ticket_timeline")}</p>
                        <div className="mt-2 space-y-2">
                          {(timelineByTicket[ticket.id] ?? []).length ? (
                            (timelineByTicket[ticket.id] ?? []).map((entry) => (
                              <div key={entry.id} className="rounded-[14px] bg-white px-3 py-2 text-xs text-slate-600">
                                <p className="font-medium text-slate-900">{entry.action}</p>
                                <p className="mt-1">{entry.user_name || t("system_user")} · {new Date(entry.created_at).toLocaleString()}</p>
                              </div>
                            ))
                          ) : (
                            <p className="text-xs text-slate-500">{t("ticket_no_timeline")}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : null}
                  <div className="mt-4 flex flex-wrap items-center gap-2">
                    <button
                      className="btn-secondary py-2 text-sm"
                      onClick={async () => {
                        const next = expandedTicketId === ticket.id ? null : ticket.id;
                        setExpandedTicketId(next);
                        if (next === ticket.id) {
                          await loadTimeline(ticket.id);
                        }
                      }}
                      type="button"
                    >
                      {expandedTicketId === ticket.id ? t("ticket_hide_detail") : t("ticket_view_detail")}
                    </button>
                    <button
                      className="btn-primary py-2 text-sm"
                      onClick={async () => {
                        try {
                          await apiClient.patch(`/tickets/${ticket.id}`, { status: "done", note: ticket.note ?? null });
                          setMessage(t("ticket_updated"));
                          await loadTickets();
                        } catch (error) {
                          setMessage(error instanceof Error ? error.message : t("ticket_update_failed"));
                        }
                      }}
                      type="button"
                    >
                      {t("ticket_mark_done")}
                    </button>
                  </div>
                  <div className="mt-4 grid gap-2">
                    <select
                      className="field py-2 text-sm"
                      value={ticket.assigned_to ?? ""}
                      onChange={async (event) => {
                        try {
                          await apiClient.patch(`/tickets/${ticket.id}`, {
                            assigned_to: event.target.value ? Number(event.target.value) : null,
                            note: ticket.note ?? null
                          });
                          setMessage(t("ticket_updated"));
                          await loadTickets();
                        } catch (error) {
                          setMessage(error instanceof Error ? error.message : t("ticket_update_failed"));
                        }
                      }}
                    >
                      <option value="">{t("ticket_assignee")}</option>
                      {staff.map((user) => (
                        <option key={user.id} value={user.id}>{user.full_name}</option>
                      ))}
                    </select>
                    <select
                      className="field py-2 text-sm"
                      value={ticket.status}
                      onChange={async (event) => {
                        try {
                          await apiClient.patch(`/tickets/${ticket.id}`, { status: event.target.value, note: null });
                          setMessage(t("ticket_updated"));
                          await loadTickets();
                        } catch (error) {
                          setMessage(error instanceof Error ? error.message : t("ticket_update_failed"));
                        }
                      }}
                    >
                      {columns.map((option) => (
                        <option key={option} value={option}>{t(option)}</option>
                      ))}
                    </select>
                    <button
                      className="btn-secondary py-2 text-sm"
                      onClick={async () => {
                        try {
                          await apiClient.post(`/tickets/${ticket.id}/push-lark`);
                          setMessage(t("lark_pushed"));
                        } catch (error) {
                          setMessage(error instanceof Error ? error.message : t("lark_push_failed"));
                        }
                      }}
                      type="button"
                    >
                      {t("push_lark")}
                    </button>
                  </div>
                  <div className="mt-3 border-t border-[#edf2f8] pt-3">
                    <div className="text-xs text-slate-400">{new Date(ticket.created_at).toLocaleString()}</div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
