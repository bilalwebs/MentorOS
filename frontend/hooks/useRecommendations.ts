"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { recommendationsApi } from "@/lib/api/recommendations";
import { getApiErrorMessage } from "@/lib/api/client";
import type { InsightType } from "@/types";

export function useGenerateRecommendation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (type: InsightType) => recommendationsApi.generate(type),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["memory-timeline"] });
      toast.success("Recommendation generated");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "AI generation failed — please try again")),
  });
}
