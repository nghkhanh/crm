"use client";

import { useEffect, useState } from "react";

import { LanguageSwitcher } from "@/components/ui/language-switcher";
import { apiClient } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { Bell, LogOut } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { UserProfile } from "@/types";

export function Topbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<UserProfile | null>(null);
  const { t } = useI18n();

  useEffect(() => {
    apiClient.get<UserProfile>("/auth/me").then(setUser).catch(() => setUser(null));
  }, []);

  if (!pathname.startsWith("/settings")) {
    return null;
  }

  return (
    <header className="flex flex-col gap-4 rounded-[26px] border border-[#e3eaf4] bg-white px-5 py-4 shadow-[0_10px_30px_rgba(15,23,42,0.05)] md:flex-row md:items-center md:justify-between">
      <div />
      <div className="flex items-center gap-3">
        <LanguageSwitcher />
        <button className="rounded-[18px] border border-[#e3eaf4] bg-[#f8fbff] p-3 text-slate-500">
          <Bell size={18} />
        </button>
        <div className="rounded-[18px] border border-[#e3eaf4] px-4 py-3">
          <p className="text-sm font-semibold text-slate-900">{user?.full_name ?? t("system_user")}</p>
          <p className="text-xs text-slate-500">{user?.email ?? t("loading")}</p>
        </div>
        <button
          className="rounded-[18px] border border-[#e3eaf4] bg-[#f8fbff] p-3 text-slate-500"
          onClick={async () => {
            await apiClient.logout();
            router.push("/login");
          }}
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
