import { clearTokens, getAccessToken, getRefreshToken, saveTokens } from "@/lib/auth";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

async function refreshTokens(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    clearTokens();
    return false;
  }

  const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
    cache: "no-store"
  });

  if (!response.ok) {
    clearTokens();
    return false;
  }

  const payload = await response.json();
  saveTokens(payload.access_token, payload.refresh_token);
  return true;
}

async function request<T>(path: string, init?: RequestInit, retried = false): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set("Content-Type", "application/json");

  const token = typeof window !== "undefined" ? getAccessToken() : null;
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store"
  });

  if (response.status === 401 && !retried && path !== "/auth/login" && path !== "/auth/refresh") {
    const refreshed = await refreshTokens();
    if (refreshed) {
      return request<T>(path, init, true);
    }
  }

  if (!response.ok) {
    let detail = `Yeu cau that bai: ${response.status}`;
    try {
      const payload = await response.json();
      if (typeof payload?.detail === "string") {
        detail = payload.detail;
      } else if (Array.isArray(payload?.detail) && payload.detail[0]?.msg) {
        detail = payload.detail[0].msg;
      }
    } catch {
      detail = `Yeu cau that bai: ${response.status}`;
    }
    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined
    }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined
    }),
  logout: async () => {
    const refreshToken = getRefreshToken();
    const accessToken = getAccessToken();
    try {
      if (refreshToken && accessToken) {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
          cache: "no-store"
        });
      }
    } finally {
      clearTokens();
    }
  }
};
