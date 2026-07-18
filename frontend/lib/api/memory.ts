import { apiClient } from "@/lib/api/client";
import type { MemoryRead } from "@/types";

export const memoryApi = {
  timeline: () => apiClient.get<MemoryRead[]>("/memory/timeline").then((r) => r.data),
  remove: (id: number) => apiClient.delete(`/memory/${id}`).then(() => undefined),
};
