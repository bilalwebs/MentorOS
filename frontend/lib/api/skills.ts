import { apiClient } from "@/lib/api/client";
import type { SkillCreatePayload, SkillRead } from "@/types";

export const skillsApi = {
  list: () => apiClient.get<SkillRead[]>("/skills").then((r) => r.data),
  create: (payload: SkillCreatePayload) => apiClient.post<SkillRead>("/skills", payload).then((r) => r.data),
  remove: (id: number) => apiClient.delete(`/skills/${id}`).then(() => undefined),
};
