import { apiClient } from "@/lib/api/client";
import type { InsightType, RecommendationResult } from "@/types";

const ENDPOINT_BY_TYPE: Record<InsightType, string> = {
  roadmap: "/recommendations/roadmap",
  skill_gap: "/recommendations/skill-gap",
  project_recommendation: "/recommendations/projects",
};

export const recommendationsApi = {
  generate: (type: InsightType) =>
    apiClient.post<RecommendationResult>(ENDPOINT_BY_TYPE[type]).then((r) => r.data),
};
