import { Language } from "@/lib/i18n";

export function formatPlatform(platform: string, language: Language) {
  const map: Record<string, string> = {
    facebook: "Facebook",
    tiktok: "TikTok",
    google: "Google"
  };
  return map[platform] ?? platform;
}

export function formatSpendProvider(provider: string, language: Language) {
  const map: Record<Language, Record<string, string>> = {
    vi: {
      facebook_graph: "Facebook API",
      smit: "SMIT",
    },
    en: {
      facebook_graph: "Facebook API",
      smit: "SMIT",
    },
  };
  return map[language][provider] ?? provider;
}

export function formatFacebookPaymentStatus(status: string, language: Language) {
  const map: Record<Language, Record<string, string>> = {
    vi: {
      healthy: "Ổn định",
      due: "Cần nạp",
      overdue: "Rủi ro",
    },
    en: {
      healthy: "Healthy",
      due: "Due",
      overdue: "At Risk",
    },
  };
  return map[language][status] ?? status;
}

export function formatTransactionType(type: string, language: Language) {
  const map: Record<Language, Record<string, string>> = {
    vi: {
      topup_bank: "Nạp ngân hàng",
      topup_usdt: "Nạp USDT",
      fee: "Phí",
      commission: "Hoa hồng",
      adjustment: "Điều chỉnh"
    },
    en: {
      topup_bank: "Bank Topup",
      topup_usdt: "USDT Topup",
      fee: "Fee",
      commission: "Commission",
      adjustment: "Adjustment"
    }
  };
  return map[language][type] ?? type;
}

export function formatTransactionSource(source: string, language: Language) {
  const map: Record<Language, Record<string, string>> = {
    vi: { manual: "Thủ công", sepay: "SePay", trongrid: "TronGrid" },
    en: { manual: "Manual", sepay: "SePay", trongrid: "TronGrid" }
  };
  return map[language][source] ?? source;
}

export function formatTransactionStatus(status: string, language: Language) {
  const map: Record<Language, Record<string, string>> = {
    vi: { posted: "Đã ghi sổ", pending: "Chờ xác nhận", failed: "Thất bại" },
    en: { posted: "Posted", pending: "Pending", failed: "Failed" }
  };
  return map[language][status] ?? status;
}

export function formatReconciliationChannel(channel: string, language: Language) {
  const map: Record<Language, Record<string, string>> = {
    vi: { bank: "Ngân hàng", usdt: "USDT" },
    en: { bank: "Bank", usdt: "USDT" }
  };
  return map[language][channel] ?? channel;
}

export function formatReconciliationStatus(status: string, language: Language) {
  const map: Record<Language, Record<string, string>> = {
    vi: {
      credited: "Đã cộng ví",
      unmatched: "Chưa khớp",
      duplicate: "Trùng lặp",
      ignored: "Bỏ qua"
    },
    en: {
      credited: "Credited",
      unmatched: "Unmatched",
      duplicate: "Duplicate",
      ignored: "Ignored"
    }
  };
  return map[language][status] ?? status;
}

export function formatTicketType(type: string, language: Language) {
  const map: Record<Language, Record<string, string>> = {
    vi: {
      open_account: "Mở tài khoản",
      support: "Hỗ trợ"
    },
    en: {
      open_account: "Open Account",
      support: "Support"
    }
  };
  return map[language][type] ?? type;
}

export function formatTicketStatus(status: string, language: Language) {
  const map: Record<Language, Record<string, string>> = {
    vi: {
      pending: "Đang chờ",
      processing: "Đang xử lý",
      done: "Hoàn tất",
      rejected: "Từ chối"
    },
    en: {
      pending: "Pending",
      processing: "Processing",
      done: "Done",
      rejected: "Rejected"
    }
  };
  return map[language][status] ?? status;
}

export function formatTicketRequestLabel(status: string, language: Language) {
  const map: Record<Language, Record<string, string>> = {
    vi: {
      pending: "Có 1 yêu cầu mới",
      processing: "Yêu cầu đang được xử lý",
      done: "Yêu cầu đã hoàn thành",
      rejected: "Yêu cầu đã bị từ chối"
    },
    en: {
      pending: "New request received",
      processing: "Request in progress",
      done: "Request completed",
      rejected: "Request rejected"
    }
  };
  return map[language][status] ?? status;
}

export function formatTicketPriority(priority: string, language: Language) {
  const map: Record<Language, Record<string, string>> = {
    vi: {
      low: "Thap",
      normal: "Binh thuong",
      high: "Cao",
      urgent: "Khan"
    },
    en: {
      low: "Low",
      normal: "Normal",
      high: "High",
      urgent: "Urgent"
    }
  };
  return map[language][priority] ?? priority;
}
