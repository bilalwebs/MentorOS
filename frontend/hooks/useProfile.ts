"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { profileApi } from "@/lib/api/profile";
import { getApiErrorMessage } from "@/lib/api/client";
import type { ProfileUpdatePayload } from "@/types";

export function useProfile() {
  return useQuery({ queryKey: ["profile"], queryFn: profileApi.getMe });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ProfileUpdatePayload) => profileApi.updateMe(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      queryClient.invalidateQueries({ queryKey: ["memory-timeline"] });
      toast.success("Profile updated");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Failed to update profile")),
  });
}
