"use client";

import { Languages } from "lucide-react";

import { useI18n } from "@/lib/i18n";

export function LanguageSwitcher() {
  const { language, setLanguage, t } = useI18n();

  return (
    <div className="flex items-center gap-2 rounded-2xl border border-line px-3 py-2 text-sm text-mute">
      <Languages size={16} />
      <span className="hidden md:inline">{t("language")}</span>
      <button
        className={`rounded-xl px-2 py-1 ${language === "vi" ? "bg-slate-900 text-white" : "text-mute"}`}
        onClick={() => setLanguage("vi")}
        type="button"
      >
        VI
      </button>
      <button
        className={`rounded-xl px-2 py-1 ${language === "en" ? "bg-slate-900 text-white" : "text-mute"}`}
        onClick={() => setLanguage("en")}
        type="button"
      >
        EN
      </button>
    </div>
  );
}

