import { apiClient } from "@/lib/api/client";
import type { ProjectCreatePayload, ProjectRead } from "@/types";

export const projectsApi = {
  list: () => apiClient.get<ProjectRead[]>("/projects").then((r) => r.data),
  create: (payload: ProjectCreatePayload) => apiClient.post<ProjectRead>("/projects", payload).then((r) => r.data),
  remove: (id: number) => apiClient.delete(`/projects/${id}`).then(() => undefined),
};
