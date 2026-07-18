import { apiClient } from "@/lib/api/client";
import type { ProfileRead, ProfileUpdatePayload } from "@/types";

export const profileApi = {
  getMe: () => apiClient.get<ProfileRead>("/profile/me").then((r) => r.data),
  updateMe: (payload: ProfileUpdatePayload) =>
    apiClient.put<ProfileRead>("/profile/me", payload).then((r) => r.data),
};
