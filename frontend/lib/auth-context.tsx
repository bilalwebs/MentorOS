"use client";

/**
 * lib/auth-context.tsx
 *
 * Owns the client-side session: current user, login/register/logout, and
 * PROACTIVE token refresh. The axios interceptor (lib/api/client.ts)
 * handles refresh REACTIVELY (on a 401) — this context adds the proactive
 * half: it decodes the token's `exp` claim and schedules a silent refresh
 * a couple minutes before expiry, so an active user essentially never
 * hits a 401 in the first place. Together these two mechanisms are what
 * "automatic token refresh" means in this app.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api/auth";
import { getApiErrorMessage } from "@/lib/api/client";
import { msUntilExpiry } from "@/lib/jwt";
import { clearToken, getToken, setToken } from "@/lib/token-storage";
import type { UserRead } from "@/types";

const REFRESH_MARGIN_MS = 2 * 60 * 1000; // refresh 2 minutes before actual expiry

interface AuthContextValue {
  user: UserRead | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserRead | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const refreshTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearRefreshTimer = useCallback(() => {
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
      refreshTimerRef.current = null;
    }
  }, []);

  const scheduleProactiveRefresh = useCallback(
    (token: string) => {
      clearRefreshTimer();
      const msLeft = msUntilExpiry(token);
      if (msLeft === null) return;

      const delay = Math.max(msLeft - REFRESH_MARGIN_MS, 5_000);
      refreshTimerRef.current = setTimeout(async () => {
        try {
          const fresh = await authApi.refresh();
          setToken(fresh.access_token);
          scheduleProactiveRefresh(fresh.access_token);
        } catch {
          // Reactive interceptor will catch the eventual 401 and redirect;
          // no need to duplicate that logic here.
        }
      }, delay);
    },
    [clearRefreshTimer]
  );

  const logout = useCallback(() => {
    clearRefreshTimer();
    clearToken();
    setUser(null);
    router.push("/login");
  }, [clearRefreshTimer, router]);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setIsLoading(false);
      return;
    }

    authApi
      .me()
      .then((me) => {
        setUser(me);
        scheduleProactiveRefresh(token);
      })
      .catch(() => {
        clearToken();
        setUser(null);
      })
      .finally(() => setIsLoading(false));

    return clearRefreshTimer;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const tokenResponse = await authApi.login({ email, password });
      setToken(tokenResponse.access_token);
      const me = await authApi.me();
      setUser(me);
      scheduleProactiveRefresh(tokenResponse.access_token);
    },
    [scheduleProactiveRefresh]
  );

  const register = useCallback(async (email: string, password: string) => {
    await authApi.register({ email, password });
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, isLoading, isAuthenticated: !!user, login, register, logout }),
    [user, isLoading, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}

export { getApiErrorMessage };
