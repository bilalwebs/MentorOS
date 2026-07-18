"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { memoryApi } from "@/lib/api/memory";
import { getApiErrorMessage } from "@/lib/api/client";

export function useMemoryTimeline() {
  return useQuery({ queryKey: ["memory-timeline"], queryFn: memoryApi.timeline });
}

export function useForgetMemory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => memoryApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["memory-timeline"] });
      toast.success("Memory forgotten");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Failed to delete memory")),
  });
}
