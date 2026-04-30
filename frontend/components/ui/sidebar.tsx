"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { useI18n } from "@/lib/i18n";
import { navigationSections } from "@/lib/navigation";

export function Sidebar() {
  const pathname = usePathname();
  const { t } = useI18n();

  return (
    <aside className="flex h-full w-full flex-col rounded-[32px] bg-[linear-gradient(180deg,#0f172a_0%,#111c34_100%)] px-4 py-5 text-white shadow-[0_24px_60px_rgba(15,23,42,0.18)]">
      <div className="mb-8 rounded-[24px] border border-white/10 bg-white/5 px-4 py-4 backdrop-blur">
        <p className="text-[11px] uppercase tracking-[0.42em] text-slate-400">Blue Media Group</p>
        <h1 className="mt-3 text-[24px] font-semibold tracking-[-0.03em] text-white">Vision Line</h1>
        <p className="mt-2 text-sm text-slate-300">Operational command center</p>
      </div>
      <nav className="space-y-5 overflow-y-auto pr-1">
        {navigationSections.map((section) => (
          <div key={section.titleKey}>
            <p className="mb-2 px-4 text-[10px] uppercase tracking-[0.28em] text-slate-500">{t(section.titleKey)}</p>
            <div className="space-y-2">
              {section.items.map((item) => {
                const Icon = item.icon;
                const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={clsx(
                      "flex items-center gap-3 rounded-[18px] px-4 py-3 text-sm transition",
                      active ? "bg-white text-slate-950 shadow-[0_10px_24px_rgba(255,255,255,0.12)]" : "text-slate-300 hover:bg-white/8 hover:text-white"
                    )}
                  >
                    <span className={clsx("flex h-9 w-9 items-center justify-center rounded-[14px]", active ? "bg-[#edf3ff] text-[#1d4ed8]" : "bg-white/5 text-slate-300")}>
                      <Icon size={18} />
                    </span>
                    <span className="font-medium">{t(item.labelKey)}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>
    </aside>
  );
}
