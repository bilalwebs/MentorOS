/**
 * lib/api/client.ts
 *
 * Single Axios instance for the whole app. Two interceptors do all the
 * auth work so individual hooks/services never think about tokens:
 *
 * - Request interceptor: attaches the current token as a Bearer header.
 * - Response interceptor: on a 401 (token expired/invalid), attempts ONE
 *   silent refresh via POST /auth/refresh, retries the original request
 *   with the new token, and only redirects to /login if the refresh
 *   itself fails (meaning the session is truly over, not just due for
 *   a renewal).
 *
 * A module-level `refreshPromise` ensures concurrent 401s (e.g. a page
 * that fires 4 requests at once right as the token expires) only trigger
 * ONE refresh call, not four racing ones.
 */

import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { clearToken, getToken, setToken } from "@/lib/token-storage";
import type { Token } from "@/types";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshPromise: Promise<string | null> | null = null;

async function performRefresh(): Promise<string | null> {
  const currentToken = getToken();
  if (!currentToken) return null;

  try {
    const response = await axios.post<Token>(
      `${API_BASE_URL}/auth/refresh`,
      {},
      { headers: { Authorization: `Bearer ${currentToken}` } }
    );
    setToken(response.data.access_token);
    return response.data.access_token;
  } catch {
    return null;
  }
}

function redirectToLogin() {
  clearToken();
  if (typeof window !== "undefined" && window.location.pathname !== "/login") {
    window.location.href = "/login";
  }
}

interface RetriableConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriableConfig | undefined;
    const status = error.response?.status;
    const url = originalRequest?.url || "";

    // Don't attempt refresh for the auth endpoints themselves — a failed
    // login/register/refresh call is a real failure, not a stale-token
    // situation, and retrying it would just loop.
    const isAuthEndpoint = url.includes("/auth/login") || url.includes("/auth/register") || url.includes("/auth/refresh");

    if (status === 401 && originalRequest && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true;

      if (!refreshPromise) {
        refreshPromise = performRefresh().finally(() => {
          refreshPromise = null;
        });
      }

      const newToken = await refreshPromise;

      if (newToken) {
        originalRequest.headers = originalRequest.headers || {};
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      }

      redirectToLogin();
    }

    return Promise.reject(error);
  }
);

/** Extracts a human-readable message from an API error response. */
export function getApiErrorMessage(error: unknown, fallback = "Something went wrong. Please try again."): string {
  if (axios.isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: string } | undefined)?.detail;
    if (typeof detail === "string") return detail;
    if (error.message) return error.message;
  }
  return fallback;
}
