"use client";

import { useEffect, useState } from "react";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/ui/page-header";
import { apiClient } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { FacebookValidation, IntegrationHealth, SystemSetting } from "@/types";

export default function SettingsPage() {
  const { t } = useI18n();
  const [values, setValues] = useState<Record<string, string>>({
    fb_system_user_token: "",
    fb_business_id: "",
    lark_webhook_url: "",
    backend_public_base_url: "",
    frontend_public_base_url: "",
    agency_usdt_wallet: "",
    trongrid_api_key: "",
    sepay_webhook_secret: "",
    default_commission_rate: "5"
  });
  const [message, setMessage] = useState<string | null>(null);
  const [health, setHealth] = useState<IntegrationHealth[]>([]);
  const [facebookValidation, setFacebookValidation] = useState<FacebookValidation | null>(null);

  useEffect(() => {
    apiClient
      .get<SystemSetting[]>("/settings")
      .then((items) => {
        const nextValues = { ...values };
        items.forEach((item) => {
          nextValues[item.key] = item.value;
        });
        setValues(nextValues);
      })
      .catch(() => setMessage(null));
  }, []);

  const settingsRows = [
    { key: "fb_system_user_token", label: t("fb_system_token") },
    { key: "fb_business_id", label: "Facebook Business ID" },
    { key: "lark_webhook_url", label: t("lark_webhook") },
    { key: "backend_public_base_url", label: t("backend_public_base_url") },
    { key: "frontend_public_base_url", label: t("frontend_public_base_url") },
    { key: "agency_usdt_wallet", label: t("agency_usdt_wallet") },
    { key: "trongrid_api_key", label: "TronGrid API Key" },
    { key: "sepay_webhook_secret", label: "SePay Webhook Secret" },
    { key: "default_commission_rate", label: t("default_commission_rate") }
  ];

  const healthMap = new Map(health.map((item) => [item.name, item]));
  const sepayHealth = healthMap.get("sepay");
  const trongridHealth = healthMap.get("trongrid");

  return (
    <div className="space-y-6">
      <PageHeader title={t("settings")} />
      <Card className="surface-muted">
        <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <p className="section-eyebrow">Integration Vault</p>
          <span className="stat-chip">{settingsRows.length} keys</span>
        </div>
        <form
          className="space-y-4"
          onSubmit={async (event) => {
            event.preventDefault();
            setMessage(null);
            try {
              await apiClient.patch("/settings", values);
              setMessage(t("settings_saved"));
            } catch (error) {
              setMessage(error instanceof Error ? error.message : t("settings_save_failed"));
            }
          }}
        >
          {settingsRows.map((row) => (
            <div key={row.label} className="flex flex-col gap-3 rounded-[22px] border border-[#e3eaf4] bg-white p-4 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="font-medium text-ink">{row.label}</p>
                <p className="text-sm text-mute">{row.key === "default_commission_rate" ? `${t("configured_via")} ${row.label}` : t("stored_in_system")}</p>
              </div>
              <input
                className="field md:max-w-[420px]"
                value={values[row.key] ?? ""}
                onChange={(event) => setValues((current) => ({ ...current, [row.key]: event.target.value }))}
              />
            </div>
          ))}
          <div className="flex items-center justify-between">
            {message ? <p className="text-sm text-mute">{message}</p> : <span />}
            <button className="btn-primary" type="submit">
              {t("save_settings")}
            </button>
          </div>
        </form>
      </Card>
      <Card>
        <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h3 className="text-lg font-semibold text-ink">{t("live_validation")}</h3>
            <p className="mt-1 text-sm text-mute">{t("live_validation_description")}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              className="btn-secondary"
              type="button"
              onClick={async () => {
                try {
                  const result = await apiClient.get<FacebookValidation>("/integrations/facebook/validate");
                  setFacebookValidation(result);
                } catch (error) {
                  setMessage(error instanceof Error ? error.message : t("settings_save_failed"));
                }
              }}
            >
              {t("validate_facebook_credentials")}
            </button>
            <button
              className="btn-primary"
              type="button"
              onClick={async () => {
                try {
                  const result = await apiClient.get<IntegrationHealth[]>("/integrations/health");
                  setHealth(result);
                } catch (error) {
                  setMessage(error instanceof Error ? error.message : t("settings_save_failed"));
                }
              }}
            >
              {t("check_integrations")}
            </button>
          </div>
        </div>
        <div className="mb-6 grid gap-3 xl:grid-cols-3">
          <div className="rounded-[22px] border border-[#e3eaf4] p-4">
            <div className="flex items-center justify-between gap-3">
              <p className="font-medium text-ink">{t("facebook_live_check")}</p>
              {facebookValidation ? (
                <Badge tone={facebookValidation.valid ? "success" : "danger"}>
                  {t("reachable")}: {facebookValidation.valid ? "yes" : "no"}
                </Badge>
              ) : (
                <Badge tone="warning">{t("validation_not_run")}</Badge>
              )}
            </div>
            <p className="mt-2 text-sm text-mute">{t("live_validation_note_facebook")}</p>
            <p className="mt-3 text-sm text-slate-700">
              {facebookValidation?.message ?? t("validation_not_run")}
            </p>
            <p className="mt-2 text-sm text-slate-700">Business ID: {facebookValidation?.business_id || "-"}</p>
            <p className="mt-1 text-sm text-slate-700">Business Name: {facebookValidation?.business_name || "-"}</p>
            <p className="mt-1 text-sm text-slate-700">Owned Ad Accounts: {facebookValidation?.ad_accounts_count ?? "-"}</p>
          </div>
          <div className="rounded-[22px] border border-[#e3eaf4] p-4">
            <div className="flex items-center justify-between gap-3">
              <p className="font-medium text-ink">{t("sepay_live_check")}</p>
              {sepayHealth ? (
                <Badge tone={sepayHealth.configured ? "success" : "warning"}>
                  {t("configured")}: {sepayHealth.configured ? "yes" : "no"}
                </Badge>
              ) : (
                <Badge tone="warning">{t("validation_not_run")}</Badge>
              )}
            </div>
            <p className="mt-2 text-sm text-mute">{t("live_validation_note_sepay")}</p>
            <p className="mt-3 text-sm text-slate-700">{sepayHealth?.message ?? t("validation_not_run")}</p>
          </div>
          <div className="rounded-[22px] border border-[#e3eaf4] p-4">
            <div className="flex items-center justify-between gap-3">
              <p className="font-medium text-ink">{t("trongrid_live_check")}</p>
              {trongridHealth ? (
                <div className="flex gap-2">
                  <Badge tone={trongridHealth.configured ? "success" : "warning"}>
                    {t("configured")}: {trongridHealth.configured ? "yes" : "no"}
                  </Badge>
                  <Badge tone={trongridHealth.reachable ? "success" : "danger"}>
                    {t("reachable")}: {trongridHealth.reachable ? "yes" : "no"}
                  </Badge>
                </div>
              ) : (
                <Badge tone="warning">{t("validation_not_run")}</Badge>
              )}
            </div>
            <p className="mt-2 text-sm text-mute">{t("live_validation_note_trongrid")}</p>
            <p className="mt-3 text-sm text-slate-700">{trongridHealth?.message ?? t("validation_not_run")}</p>
          </div>
        </div>
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-ink">{t("integration_status")}</h3>
          {health.map((item) => (
            <div key={item.name} className="rounded-[22px] border border-[#e3eaf4] p-4">
              <div className="flex items-center justify-between gap-3">
                <p className="font-medium capitalize text-ink">{item.name}</p>
                <div className="flex gap-2">
                  <Badge tone={item.configured ? "success" : "warning"}>{t("configured")}: {item.configured ? "yes" : "no"}</Badge>
                  <Badge tone={item.reachable ? "success" : "danger"}>{t("reachable")}: {item.reachable ? "yes" : "no"}</Badge>
                </div>
              </div>
              <p className="mt-2 text-sm text-mute">{item.message}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
