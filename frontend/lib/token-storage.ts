/**
 * lib/token-storage.ts
 *
 * Single source of truth for where the JWT lives (localStorage) and how
 * it's read/written. Centralizing this means the token storage mechanism
 * (localStorage vs cookie, key name, etc.) can change in one place without
 * hunting through every hook/component that needs the token.
 */

const TOKEN_KEY = "mentoros_access_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
}
