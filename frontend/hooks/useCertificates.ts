"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { certificatesApi } from "@/lib/api/certificates";
import { getApiErrorMessage } from "@/lib/api/client";
import type { CertificateCreatePayload } from "@/types";

export function useCertificates() {
  return useQuery({ queryKey: ["certificates"], queryFn: certificatesApi.list });
}

export function useAddCertificate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CertificateCreatePayload) => certificatesApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["certificates"] });
      queryClient.invalidateQueries({ queryKey: ["memory-timeline"] });
      toast.success("Certificate added");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Failed to add certificate")),
  });
}

export function useDeleteCertificate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => certificatesApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["certificates"] });
      toast.success("Certificate removed");
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Failed to remove certificate")),
  });
}
