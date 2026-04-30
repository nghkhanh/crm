import type { Route } from "next";
import {
  CreditCard,
  LayoutDashboard,
  Network,
  Scale,
  Receipt,
  Settings,
  Ticket,
  Users,
  UserCog,
  FileText,
} from "lucide-react";

export type NavigationItem = {
  href: Route;
  labelKey: string;
  icon: typeof LayoutDashboard;
};

export type NavigationSection = {
  titleKey: string;
  items: NavigationItem[];
};

export const navigationSections: NavigationSection[] = [
  {
    titleKey: "nav_section_core",
    items: [
      { href: "/dashboard", labelKey: "dashboard", icon: LayoutDashboard },
      { href: "/customers", labelKey: "customers", icon: Users },
      { href: "/ad-accounts", labelKey: "ad_accounts", icon: CreditCard },
      { href: "/transactions", labelKey: "transactions", icon: Receipt },
      { href: "/reconciliations", labelKey: "reconciliations", icon: Scale },
      { href: "/invoices", labelKey: "invoices", icon: FileText },
      { href: "/tickets", labelKey: "tickets", icon: Ticket },
      { href: "/referrals", labelKey: "referrals", icon: Network },
      { href: "/personnel-management", labelKey: "personnel_management", icon: UserCog },
      { href: "/settings", labelKey: "settings", icon: Settings },
    ],
  },
];

export const managementPlaceholderRoutes: Record<string, { titleKey: string; descriptionKey: string }> = {
  "/application-ads": { titleKey: "application_ads", descriptionKey: "application_ads_description" },
  "/account-application": { titleKey: "account_application", descriptionKey: "account_application_description" },
  "/opening-record": { titleKey: "opening_record", descriptionKey: "opening_record_description" },
  "/wallet": { titleKey: "wallet", descriptionKey: "wallet_description" },
  "/advertising-guidance": { titleKey: "advertising_guidance", descriptionKey: "advertising_guidance_description" },
  "/account-management": { titleKey: "account_management", descriptionKey: "account_management_description" },
  "/facebook-request": { titleKey: "facebook_request", descriptionKey: "facebook_request_description" },
  "/google-request": { titleKey: "google_request", descriptionKey: "google_request_description" },
  "/tiktok-request": { titleKey: "tiktok_request", descriptionKey: "tiktok_request_description" },
  "/tiktok-sea-request": { titleKey: "tiktok_sea_request", descriptionKey: "tiktok_sea_request_description" },
  "/cid-management": { titleKey: "cid_management", descriptionKey: "cid_management_description" },
  "/other-media-request": { titleKey: "other_media_request", descriptionKey: "other_media_request_description" },
  "/request-history": { titleKey: "request_history", descriptionKey: "request_history_description" },
  "/business-management": { titleKey: "business_management", descriptionKey: "business_management_description" },
  "/team-management": { titleKey: "team_management", descriptionKey: "team_management_description" },
  "/help-center": { titleKey: "help_center", descriptionKey: "help_center_description" },
};
