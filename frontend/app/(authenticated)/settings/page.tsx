"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { DataTable } from "@/components/ui/table";
import { apiClient } from "@/lib/api";
import { formatWalletGasStatus, formatWalletSweepStatus } from "@/lib/display";
import { useI18n } from "@/lib/i18n";
import { BankTreasurySnapshot, Customer, FacebookValidation, IntegrationHealth, SystemSetting, UsdtWalletInventory } from "@/types";

type SettingsField = {
  key: string;
  label: string;
  placeholder?: string;
  multiline?: boolean;
};

type SettingsSection = {
  title: string;
  description: string;
  integration?: "facebook" | "sepay" | "trongrid" | "smit";
  fields: SettingsField[];
};

export default function SettingsPage() {
  const { t, language } = useI18n();
  const [values, setValues] = useState<Record<string, string>>({
    fb_system_user_token: "",
    fb_business_id: "",
    lark_webhook_url: "",
    backend_public_base_url: "",
    frontend_public_base_url: "",
    agency_usdt_wallet: "",
    trongrid_api_key: "",
    usdt_trc20_contract: "",
    usdt_trx_low_threshold: "30",
    usdt_sweep_min_balance: "1",
    sepay_webhook_secret: "",
    sepay_api_token: "",
    sepay_bank_account_id: "",
    smit_base_url: "",
    smit_api_key: "",
    smit_sync_url_template: "",
    default_commission_rate: "5"
  });
  const [message, setMessage] = useState<string | null>(null);
  const [health, setHealth] = useState<IntegrationHealth[]>([]);
  const [facebookValidation, setFacebookValidation] = useState<FacebookValidation | null>(null);
  const [bankSnapshots, setBankSnapshots] = useState<BankTreasurySnapshot[]>([]);
  const [walletPool, setWalletPool] = useState<UsdtWalletInventory[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [walletForm, setWalletForm] = useState({ address: "", label: "", note: "" });
  const [autoSaveState, setAutoSaveState] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [checking, setChecking] = useState<Record<string, boolean>>({});

  const initializedRef = useRef(false);
  const lastSavedSnapshotRef = useRef("");

  const sections: SettingsSection[] = [
    {
      title: "Facebook",
      description:
        language === "vi"
          ? "Dùng để xác thực BM và đồng bộ dữ liệu tài khoản quảng cáo."
          : "Used for BM validation and ad account sync.",
      integration: "facebook",
      fields: [
        { key: "fb_system_user_token", label: t("fb_system_token"), multiline: true, placeholder: "EA..." },
        { key: "fb_business_id", label: "Facebook Business ID", placeholder: "3176491322551721" }
      ]
    },
    {
      title: "SePay",
      description:
        language === "vi"
          ? "Dùng để nhận webhook chuyển khoản và đọc trạng thái tài khoản ngân hàng công ty."
          : "Used for inbound bank transfer webhooks and company bank account status.",
      integration: "sepay",
      fields: [
        { key: "sepay_webhook_secret", label: "SePay Webhook Secret", placeholder: "secret" },
        { key: "sepay_api_token", label: t("sepay_api_token"), placeholder: "token" },
        { key: "sepay_bank_account_id", label: t("sepay_bank_account_id"), placeholder: "12345" }
      ]
    },
    {
      title: "USDT / TronGrid",
      description:
        language === "vi"
          ? "Dùng để xác nhận topup USDT TRC20, theo dõi gas TRX và chuẩn bị sweep về ví chính."
          : "Used to validate TRC20 USDT topups, track TRX gas, and prepare sweep to the agency wallet.",
      integration: "trongrid",
      fields: [
        { key: "agency_usdt_wallet", label: t("agency_usdt_wallet"), placeholder: "T..." },
        { key: "trongrid_api_key", label: "TronGrid API Key", placeholder: "api-key" },
        { key: "usdt_trc20_contract", label: t("usdt_trc20_contract"), placeholder: "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj" },
        { key: "usdt_trx_low_threshold", label: t("usdt_trx_low_threshold"), placeholder: "30" },
        { key: "usdt_sweep_min_balance", label: t("usdt_sweep_min_balance"), placeholder: "1" }
      ]
    },
    {
      title: "SMIT",
      description:
        language === "vi"
          ? "Dùng khi account ads lấy spend từ đối tác thay vì Facebook Graph API."
          : "Used when ad account spend comes from a partner connector instead of Facebook Graph API.",
      integration: "smit",
      fields: [
        { key: "smit_base_url", label: t("smit_base_url"), placeholder: "https://api.partner.com" },
        { key: "smit_api_key", label: t("smit_api_key"), placeholder: "api-key" },
        { key: "smit_sync_url_template", label: t("smit_sync_url_template"), placeholder: "/accounts/{account_id}/summary" }
      ]
    },
    {
      title: language === "vi" ? "Hệ thống" : "System",
      description:
        language === "vi"
          ? "URL callback, webhook Lark và cấu hình mặc định cho toàn CRM."
          : "Callback URLs, Lark webhook, and CRM-wide defaults.",
      fields: [
        { key: "lark_webhook_url", label: t("lark_webhook"), placeholder: "https://open.larksuite.com/..." },
        { key: "backend_public_base_url", label: t("backend_public_base_url"), placeholder: "https://api.example.com" },
        { key: "frontend_public_base_url", label: t("frontend_public_base_url"), placeholder: "https://app.example.com" },
        { key: "default_commission_rate", label: t("default_commission_rate"), placeholder: "5" }
      ]
    }
  ];

  async function loadSettings() {
    const items = await apiClient.get<SystemSetting[]>("/settings");
    const nextValues = { ...values };
    items.forEach((item) => {
      nextValues[item.key] = item.value;
    });
    setValues(nextValues);
    lastSavedSnapshotRef.current = JSON.stringify(nextValues);
    initializedRef.current = true;
  }

  async function loadChecks() {
    const [healthResult, facebookResult] = await Promise.all([
      apiClient.get<IntegrationHealth[]>("/integrations/health"),
      apiClient.get<FacebookValidation>("/integrations/facebook/validate")
    ]);
    setHealth(healthResult);
    setFacebookValidation(facebookResult);
  }

  async function loadTreasury() {
    const [snapshots, wallets, customerResult] = await Promise.all([
      apiClient.get<BankTreasurySnapshot[]>("/treasury/bank-snapshots").catch(() => []),
      apiClient.get<UsdtWalletInventory[]>("/treasury/usdt-wallets").catch(() => []),
      apiClient.get<{ items: Customer[] }>("/customers").catch(() => ({ items: [] }))
    ]);
    setBankSnapshots(snapshots);
    setWalletPool(wallets);
    setCustomers(customerResult.items);
  }

  async function checkIntegration(target: "facebook" | "sepay" | "trongrid" | "smit") {
    setChecking((current) => ({ ...current, [target]: true }));
    setMessage(null);
    try {
      if (target === "facebook") {
        const [healthResult, facebookResult] = await Promise.all([
          apiClient.get<IntegrationHealth[]>("/integrations/health"),
          apiClient.get<FacebookValidation>("/integrations/facebook/validate")
        ]);
        setHealth(healthResult);
        setFacebookValidation(facebookResult);
      } else {
        const healthResult = await apiClient.get<IntegrationHealth[]>("/integrations/health");
        setHealth(healthResult);
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : t("settings_save_failed"));
    } finally {
      setChecking((current) => ({ ...current, [target]: false }));
    }
  }

  useEffect(() => {
    Promise.all([loadSettings(), loadTreasury()]).catch(() => setMessage(null));
  }, []);

  const valuesSnapshot = useMemo(() => JSON.stringify(values), [values]);

  useEffect(() => {
    if (!initializedRef.current) {
      return;
    }
    if (valuesSnapshot === lastSavedSnapshotRef.current) {
      return;
    }

    const timeoutId = window.setTimeout(async () => {
      setAutoSaveState("saving");
      setMessage(null);
      try {
        await apiClient.patch("/settings", values);
        lastSavedSnapshotRef.current = valuesSnapshot;
        setAutoSaveState("saved");
      } catch (error) {
        setAutoSaveState("error");
        setMessage(error instanceof Error ? error.message : t("settings_save_failed"));
      }
    }, 800);

    return () => window.clearTimeout(timeoutId);
  }, [values, valuesSnapshot, t]);

  const healthMap = new Map(health.map((item) => [item.name, item]));
  const latestBankSnapshot = bankSnapshots[0];

  function renderSectionBadge(section: SettingsSection) {
    if (!section.integration) {
      return null;
    }
    if (section.integration === "facebook") {
      if (!facebookValidation) {
        return <Badge tone="warning">{t("validation_not_run")}</Badge>;
      }
      return <Badge tone={facebookValidation.valid ? "success" : "danger"}>{facebookValidation.valid ? "OK" : "Error"}</Badge>;
    }
    const item = healthMap.get(section.integration);
    if (!item) {
      return <Badge tone="warning">{t("validation_not_run")}</Badge>;
    }
    return <Badge tone={item.reachable ? "success" : item.configured ? "warning" : "danger"}>{item.message}</Badge>;
  }

  return (
    <div className="space-y-6">
      <Card className="surface-muted">
        <div className="flex items-center justify-between">
          <div className="text-sm text-mute">
            {autoSaveState === "saving" ? "Dang luu..." : autoSaveState === "saved" ? "Da luu tu dong" : message ?? ""}
          </div>
        </div>
        <div className="mt-4 space-y-4">
          {sections.map((section) => (
            <section key={section.title} className="rounded-[22px] border border-[#e3eaf4] bg-white p-5">
              <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-ink">{section.title}</h3>
                  <p className="mt-1 text-sm text-mute">{section.description}</p>
                </div>
                <div className="flex items-center gap-2">
                  {section.integration ? (
                    <button
                      className="rounded-full border border-[#d9e3f0] px-3 py-1 text-xs font-medium text-slate-600 transition hover:border-[#93c5fd] hover:text-[#1d4ed8]"
                      type="button"
                      onClick={() => checkIntegration(section.integration!)}
                    >
                      {checking[section.integration] ? "Dang kiem tra..." : "Kiểm tra"}
                    </button>
                  ) : null}
                  <div className="max-w-[320px]">{renderSectionBadge(section)}</div>
                </div>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                {section.fields.map((field) => (
                  <label key={field.key} className={field.multiline ? "md:col-span-2" : ""}>
                    <span className="mb-2 block text-sm font-medium text-ink">{field.label}</span>
                    {field.multiline ? (
                      <textarea
                        className="field min-h-[120px] font-mono text-sm"
                        placeholder={field.placeholder}
                        value={values[field.key] ?? ""}
                        onChange={(event) => setValues((current) => ({ ...current, [field.key]: event.target.value }))}
                      />
                    ) : (
                      <input
                        className="field"
                        placeholder={field.placeholder}
                        value={values[field.key] ?? ""}
                        onChange={(event) => setValues((current) => ({ ...current, [field.key]: event.target.value }))}
                      />
                    )}
                  </label>
                ))}
              </div>
            </section>
          ))}
        </div>
      </Card>

      <Card>
        <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h3 className="text-lg font-semibold text-ink">{t("bank_treasury")}</h3>
            <p className="mt-1 text-sm text-mute">Snapshot số dư tài khoản công ty từ SePay để đội vận hành theo dõi ngay trong CRM.</p>
          </div>
          <button
            className="btn-primary"
            type="button"
            onClick={async () => {
              try {
                const snapshot = await apiClient.post<BankTreasurySnapshot>("/treasury/bank-snapshots/sync");
                setBankSnapshots((current) => [snapshot, ...current]);
                setMessage(t("bank_balance_synced"));
              } catch (error) {
                setMessage(error instanceof Error ? error.message : t("bank_balance_sync_failed"));
              }
            }}
          >
            {t("sync_bank_balance")}
          </button>
        </div>
        <div className="grid gap-3 md:grid-cols-4">
          <div className="rounded-[18px] border border-[#e3eaf4] p-4">
            <p className="text-sm text-mute">Tài khoản</p>
            <p className="mt-2 font-medium text-ink">{latestBankSnapshot?.account_number || values.sepay_bank_account_id || "-"}</p>
          </div>
          <div className="rounded-[18px] border border-[#e3eaf4] p-4">
            <p className="text-sm text-mute">Số dư</p>
            <p className="mt-2 font-medium text-ink">{latestBankSnapshot ? `${latestBankSnapshot.balance} ${latestBankSnapshot.currency}` : "-"}</p>
          </div>
          <div className="rounded-[18px] border border-[#e3eaf4] p-4">
            <p className="text-sm text-mute">Khả dụng</p>
            <p className="mt-2 font-medium text-ink">{latestBankSnapshot?.available_balance ? `${latestBankSnapshot.available_balance} ${latestBankSnapshot.currency}` : "-"}</p>
          </div>
          <div className="rounded-[18px] border border-[#e3eaf4] p-4">
            <p className="text-sm text-mute">Lần đồng bộ</p>
            <p className="mt-2 font-medium text-ink">{latestBankSnapshot?.synced_at ? new Date(latestBankSnapshot.synced_at).toLocaleString() : "-"}</p>
          </div>
        </div>
      </Card>

      <Card>
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-ink">{t("usdt_wallet_pool")}</h3>
          <p className="mt-1 text-sm text-mute">Kho ví nạp TRC20, theo dõi số dư TRX để trả gas và hàng chờ sweep về ví chính.</p>
        </div>
        <form
          className="grid gap-3 md:grid-cols-4"
          onSubmit={async (event) => {
            event.preventDefault();
            try {
              const wallet = await apiClient.post<UsdtWalletInventory>("/treasury/usdt-wallets", walletForm);
              setWalletPool((current) => [wallet, ...current]);
              setWalletForm({ address: "", label: "", note: "" });
              setMessage(t("wallet_pool_added"));
            } catch (error) {
              setMessage(error instanceof Error ? error.message : t("wallet_pool_add_failed"));
            }
          }}
        >
          <input className="field" placeholder="T..." value={walletForm.address} onChange={(event) => setWalletForm((current) => ({ ...current, address: event.target.value }))} />
          <input className="field" placeholder={t("label")} value={walletForm.label} onChange={(event) => setWalletForm((current) => ({ ...current, label: event.target.value }))} />
          <input className="field" placeholder={t("note")} value={walletForm.note} onChange={(event) => setWalletForm((current) => ({ ...current, note: event.target.value }))} />
          <button className="btn-primary" type="submit">{t("add_wallet_to_pool")}</button>
        </form>
        <div className="mt-4">
          <DataTable headers={["Địa chỉ", t("customer_label"), t("trx_balance"), t("usdt_balance_label"), t("gas_status"), t("sweep_status"), t("created_at"), t("operation")]}>
            {walletPool.map((wallet) => (
              <tr key={wallet.id} className="border-b border-[#edf2f8]">
                <td className="px-5 py-4 font-medium text-ink">{wallet.address}</td>
                <td className="px-5 py-4 text-mute">
                  {wallet.customer_id ? `#${wallet.customer_id} - ${customers.find((customer) => customer.id === wallet.customer_id)?.full_name ?? ""}` : "-"}
                </td>
                <td className="px-5 py-4">{wallet.trx_balance}</td>
                <td className="px-5 py-4">{wallet.usdt_balance}</td>
                <td className="px-5 py-4">{formatWalletGasStatus(wallet.gas_status, language)}</td>
                <td className="px-5 py-4">{formatWalletSweepStatus(wallet.sweep_status, language)}</td>
                <td className="px-5 py-4 text-mute">{new Date(wallet.created_at).toLocaleDateString()}</td>
                <td className="px-5 py-4">
                  <div className="flex gap-3">
                    <button
                      className="text-sm font-medium text-slate-700 transition hover:text-slate-900"
                      type="button"
                      onClick={async () => {
                        try {
                          const refreshed = await apiClient.post<UsdtWalletInventory>(`/treasury/usdt-wallets/${wallet.id}/refresh`);
                          setWalletPool((current) => current.map((item) => (item.id === wallet.id ? refreshed : item)));
                        } catch (error) {
                          setMessage(error instanceof Error ? error.message : t("wallet_refresh_failed"));
                        }
                      }}
                    >
                      {t("refresh_wallet")}
                    </button>
                    <button
                      className="text-sm font-medium text-[#1d4ed8] transition hover:text-[#1e40af]"
                      type="button"
                      onClick={async () => {
                        try {
                          const queued = await apiClient.post<UsdtWalletInventory>(`/treasury/usdt-wallets/${wallet.id}/queue-sweep`, { note: wallet.note ?? null });
                          setWalletPool((current) => current.map((item) => (item.id === wallet.id ? queued : item)));
                          setMessage(t("wallet_sweep_queued"));
                        } catch (error) {
                          setMessage(error instanceof Error ? error.message : t("wallet_sweep_failed"));
                        }
                      }}
                    >
                      {t("queue_sweep")}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </DataTable>
        </div>
      </Card>
    </div>
  );
}
