import { apiClient } from "@/lib/api/client";
import type { Token, UserCreatePayload, UserLoginPayload, UserRead } from "@/types";

export const authApi = {
  register: (payload: UserCreatePayload) =>
    apiClient.post<UserRead>("/auth/register", payload).then((r) => r.data),

  login: (payload: UserLoginPayload) =>
    apiClient.post<Token>("/auth/login", payload).then((r) => r.data),

  me: () => apiClient.get<UserRead>("/auth/me").then((r) => r.data),

  refresh: () => apiClient.post<Token>("/auth/refresh").then((r) => r.data),
};
