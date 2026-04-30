"use client";

const ACCESS_TOKEN_KEY = "crm_access_token";
const REFRESH_TOKEN_KEY = "crm_refresh_token";

export function saveTokens(accessToken: string, refreshToken: string) {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function getAccessToken() {
  return typeof window === "undefined" ? null : localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken() {
  return typeof window === "undefined" ? null : localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function setAccessToken(accessToken: string) {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
}
