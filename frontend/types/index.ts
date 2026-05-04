export type UserRole = "admin" | "cs" | "accountant" | "sub_admin";

export type UserProfile = {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  phone?: string | null;
  team_name?: string | null;
  status: "enabled" | "disabled";
};

export type StaffMember = UserProfile;

export type SystemSetting = {
  id: number;
  key: string;
  value: string;
  description?: string | null;
  created_at: string;
};

export type IntegrationHealth = {
  name: string;
  configured: boolean;
  reachable: boolean;
  message: string;
};

export type FacebookValidation = {
  valid: boolean;
  business_id: string;
  business_name?: string | null;
  ad_accounts_count?: number | null;
  message: string;
};

export type DashboardSummary = {
  total_customers: number;
  total_wallet_balance: number;
  total_spend_today: number;
  active_accounts_count: number;
  disabled_accounts_count: number;
  block_rate_quarter: number;
  block_rate_90d: number;
  pending_tickets_count: number;
  spend_trend_7d: Array<{ date: string; label: string; value: number }>;
  spend_trend_28d: Array<{ date: string; label: string; value: number }>;
};

export type Customer = {
  id: number;
  full_name: string;
  email?: string | null;
  phone?: string | null;
  note?: string | null;
  wallet_balance: string;
  status: "active" | "inactive";
  created_at: string;
};

export type CustomerUsdtAddress = {
  id: number;
  customer_id: number;
  network: "trc20";
  address: string;
  label?: string | null;
  status: "active" | "inactive";
  assigned_at: string;
  last_seen_at?: string | null;
  created_at: string;
};

export type BankTreasurySnapshot = {
  id: number;
  provider: "sepay";
  bank_account_id: string;
  account_number?: string | null;
  account_name?: string | null;
  currency: string;
  balance: string;
  available_balance?: string | null;
  status_message?: string | null;
  synced_at: string;
  created_at: string;
};

export type UsdtWalletInventory = {
  id: number;
  network: "trc20";
  address: string;
  label?: string | null;
  status: "available" | "assigned" | "disabled";
  customer_id?: number | null;
  customer_usdt_address_id?: number | null;
  trx_balance: string;
  usdt_balance: string;
  gas_status: "unknown" | "ok" | "low" | "missing";
  sweep_status: "idle" | "ready" | "pending" | "completed" | "failed";
  sweep_destination?: string | null;
  last_sweep_tx_id?: string | null;
  assigned_at?: string | null;
  last_balance_synced_at?: string | null;
  requested_sweep_at?: string | null;
  last_sweep_at?: string | null;
  note?: string | null;
  created_at: string;
};

export type AdAccount = {
  id: number;
  customer_id: number;
  platform: "facebook" | "tiktok" | "google";
  account_id: string;
  account_name: string;
  status: "ACTIVE" | "DISABLED";
  spend_provider: "facebook_graph" | "smit";
  balance: string;
  spend_today: string;
  spend_7d: string;
  spend_28d: string;
  spend_90d: string;
  amount_due: string;
  prepaid_balance: string;
  payment_threshold: string;
  payment_status: "healthy" | "due" | "overdue";
  last_payment_at?: string | null;
  last_synced_at?: string | null;
};

export type Transaction = {
  id: number;
  customer_id: number;
  type: string;
  source: "manual" | "sepay" | "trongrid";
  status: "posted" | "pending" | "failed";
  amount: string;
  balance_before: string;
  balance_after: string;
  reference?: string | null;
  note?: string | null;
  created_at: string;
};

export type ReconciliationRecord = {
  id: number;
  channel: "bank" | "usdt";
  status: "credited" | "unmatched" | "duplicate" | "ignored";
  customer_id?: number | null;
  transaction_id?: number | null;
  external_id: string;
  amount: string;
  reference?: string | null;
  wallet_address?: string | null;
  note?: string | null;
  raw_payload: Record<string, unknown>;
  created_at: string;
};

export type Invoice = {
  id: number;
  customer_id: number;
  invoice_number?: string | null;
  period_start: string;
  period_end: string;
  total_topup: string;
  total_fee: string;
  total_commission: string;
  file_url?: string | null;
  status: "draft" | "sent" | "paid";
  sent_at?: string | null;
  paid_at?: string | null;
  locked_at?: string | null;
  created_at: string;
};

export type Ticket = {
  id: number;
  customer_id: number;
  assigned_to?: number | null;
  assigned_user_name?: string | null;
  type: string;
  platform: string;
  status: "pending" | "processing" | "done" | "rejected";
  priority: "low" | "normal" | "high" | "urgent";
  form_data: Record<string, unknown>;
  lark_ticket_id?: string | null;
  note?: string | null;
  created_at: string;
};

export type TicketTimelineEntry = {
  id: number;
  user_id?: number | null;
  user_name?: string | null;
  action: string;
  metadata_json: Record<string, unknown>;
  created_at: string;
};

export type Referral = {
  id: number;
  referrer_id: number;
  referee_id: number;
  referrer_name?: string | null;
  referee_name?: string | null;
  commission_rate: string;
  total_earned: string;
  created_at: string;
};
