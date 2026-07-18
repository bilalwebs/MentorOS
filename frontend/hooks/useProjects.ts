"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { projectsApi } from "@/lib/api/projects";
import { getApiErrorMessage } from "@/lib/api/client";
import type { ProjectCreatePayload } from "@/types";

export function useProjects() {
  return useQuery({ queryKey: ["projects"], queryFn: projectsApi.list });
}

export function useAddProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ProjectCreatePayload) => projectsApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["memory-timeline"] });
      toast.success("Project added");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Failed to add project")),
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => projectsApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      toast.success("Project removed");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Failed to remove project")),
  });
}
