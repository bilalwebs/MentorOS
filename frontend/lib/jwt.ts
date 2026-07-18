/**
 * lib/jwt.ts
 *
 * Client-side JWT decoding for scheduling proactive refresh — this is
 * NOT for trusting the token's contents (the backend is the only source
 * of truth for auth validity). We only read the `exp` claim to know when
 * to silently refresh, so a malformed/foreign token just fails to parse
 * and we treat it as "no expiry info" rather than crashing.
 */

interface DecodedJwt {
  exp?: number;
  sub?: string;
}

export function decodeJwt(token: string): DecodedJwt | null {
  try {
    const payload = token.split(".")[1];
    if (!payload) return null;
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(
      atob(normalized)
        .split("")
        .map((c) => "%" + c.charCodeAt(0).toString(16).padStart(2, "0"))
        .join("")
    );
    return JSON.parse(json) as DecodedJwt;
  } catch {
    return null;
  }
}

/** Returns milliseconds until token expiry, or null if it can't be determined. */
export function msUntilExpiry(token: string): number | null {
  const decoded = decodeJwt(token);
  if (!decoded?.exp) return null;
  return decoded.exp * 1000 - Date.now();
}
