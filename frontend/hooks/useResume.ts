"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { resumeApi } from "@/lib/api/resume";
import { getApiErrorMessage } from "@/lib/api/client";

export function useResumes() {
  return useQuery({ queryKey: ["resumes"], queryFn: resumeApi.list });
}

export function useUploadResume() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => resumeApi.upload(file),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
      queryClient.invalidateQueries({ queryKey: ["skills"] });
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["certificates"] });
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      queryClient.invalidateQueries({ queryKey: ["career-goals"] });
      queryClient.invalidateQueries({ queryKey: ["memory-timeline"] });
      const { skills, projects, certificates } = result.extracted;
      toast.success(`Resume processed: ${skills} skills, ${projects} projects, ${certificates} certificates added`);
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Failed to process resume")),
  });
}
