"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { skillsApi } from "@/lib/api/skills";
import { getApiErrorMessage } from "@/lib/api/client";
import type { SkillCreatePayload } from "@/types";

export function useSkills() {
  return useQuery({ queryKey: ["skills"], queryFn: skillsApi.list });
}

export function useAddSkill() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: SkillCreatePayload) => skillsApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["skills"] });
      queryClient.invalidateQueries({ queryKey: ["memory-timeline"] });
      toast.success("Skill added");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Failed to add skill")),
  });
}

export function useDeleteSkill() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => skillsApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["skills"] });
      toast.success("Skill removed");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Failed to remove skill")),
  });
}
