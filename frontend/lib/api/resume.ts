import { apiClient } from "@/lib/api/client";
import type { ResumeRead, ResumeUploadResult } from "@/types";

export const resumeApi = {
  list: () => apiClient.get<ResumeRead[]>("/resume").then((r) => r.data),
  upload: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient
      .post<ResumeUploadResult>("/resume/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },
};
