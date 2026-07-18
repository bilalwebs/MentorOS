import { apiClient } from "@/lib/api/client";
import type { CertificateCreatePayload, CertificateRead } from "@/types";

export const certificatesApi = {
  list: () => apiClient.get<CertificateRead[]>("/certificates").then((r) => r.data),
  create: (payload: CertificateCreatePayload) =>
    apiClient.post<CertificateRead>("/certificates", payload).then((r) => r.data),
  remove: (id: number) => apiClient.delete(`/certificates/${id}`).then(() => undefined),
};
