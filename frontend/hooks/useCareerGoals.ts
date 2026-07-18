"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { careerGoalsApi } from "@/lib/api/careerGoals";
import { getApiErrorMessage } from "@/lib/api/client";
import type { CareerGoalCreatePayload } from "@/types";

export function useCareerGoals() {
  return useQuery({ queryKey: ["career-goals"], queryFn: careerGoalsApi.list });
}

export function useSetCareerGoal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CareerGoalCreatePayload) => careerGoalsApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["career-goals"] });
      queryClient.invalidateQueries({ queryKey: ["memory-timeline"] });
      toast.success("Career goal updated — your previous goal is preserved in your memory timeline");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Failed to set career goal")),
  });
}
