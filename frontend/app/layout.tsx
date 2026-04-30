import "./globals.css";

import type { Metadata } from "next";
import { I18nProvider } from "@/lib/i18n";

export const metadata: Metadata = {
  title: "CRM Nội Bộ",
  description: "CRM nội bộ cho vận hành agency Facebook Ads"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <body>
        <I18nProvider>{children}</I18nProvider>
      </body>
    </html>
  );
}
