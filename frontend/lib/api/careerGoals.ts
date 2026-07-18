import { apiClient } from "@/lib/api/client";
import type { CareerGoalCreatePayload, CareerGoalRead } from "@/types";

export const careerGoalsApi = {
  list: () => apiClient.get<CareerGoalRead[]>("/career-goals").then((r) => r.data),
  create: (payload: CareerGoalCreatePayload) =>
    apiClient.post<CareerGoalRead>("/career-goals", payload).then((r) => r.data),
};
