"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { Card } from "@/components/ui/card";
import { saveTokens } from "@/lib/auth";
import { useI18n } from "@/lib/i18n";

export default function LoginPage() {
  const router = useRouter();
  const { t } = useI18n();
  const [email, setEmail] = useState("nghkhanh203@gmail.com");
  const [password, setPassword] = useState("changeme123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api"}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      if (!response.ok) {
        throw new Error(t("invalid_login"));
      }
      const data = await response.json();
      saveTokens(data.access_token, data.refresh_token);
      router.push("/dashboard");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : t("login_failed"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top_right,rgba(29,78,216,0.08),transparent_26%),linear-gradient(180deg,#f7fbff_0%,#eef4fb_100%)] p-6">
      <div className="grid w-full max-w-6xl gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        <section className="relative overflow-hidden rounded-[36px] border border-[#1e293b] bg-[linear-gradient(180deg,#0f172a_0%,#101b31_100%)] p-10 text-white shadow-[0_30px_80px_rgba(15,23,42,0.18)]">
          <div className="absolute right-[-60px] top-[-60px] h-64 w-64 rounded-full bg-[rgba(59,130,246,0.18)] blur-3xl" />
          <div className="absolute bottom-[-40px] left-[-20px] h-44 w-44 rounded-full bg-[rgba(255,255,255,0.05)] blur-2xl" />
          <h1 className="relative mt-6 max-w-lg text-[54px] font-semibold leading-[1.02] tracking-[-0.04em]">{t("login_hero_title")}</h1>
          <p className="relative mt-6 max-w-xl text-[15px] leading-7 text-slate-300">
            {t("login_hero_description")}
          </p>
        </section>
        <Card className="flex items-center rounded-[36px] p-8 lg:p-10">
          <form className="w-full space-y-5" onSubmit={onSubmit}>
            <div>
              <p className="text-xs uppercase tracking-[0.32em] text-slate-400">{t("sign_in")}</p>
              <h2 className="mt-3 text-[38px] font-semibold tracking-[-0.04em] text-slate-900">{t("welcome_back")}</h2>
            </div>
            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-500">{t("email")}</span>
              <input
                className="w-full rounded-[20px] border border-[#dfe7f1] bg-[#fbfdff] px-4 py-3.5 outline-none transition focus:border-[#93c5fd] focus:ring-4 focus:ring-[#dbeafe]"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </label>
            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-500">{t("password")}</span>
              <input
                className="w-full rounded-[20px] border border-[#dfe7f1] bg-[#fbfdff] px-4 py-3.5 outline-none transition focus:border-[#93c5fd] focus:ring-4 focus:ring-[#dbeafe]"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
            {error ? <p className="text-sm text-danger">{error}</p> : null}
            <button
              className="w-full rounded-[20px] bg-[#1d4ed8] px-4 py-3.5 font-semibold text-white transition hover:bg-[#1e40af]"
              disabled={loading}
              type="submit"
            >
              {loading ? t("signing_in") : t("sign_in")}
            </button>
          </form>
        </Card>
      </div>
    </main>
  );
}
