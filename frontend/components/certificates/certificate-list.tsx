"use client";

import { Award } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/common/empty-state";
import { LoadingState } from "@/components/common/loading-state";
import { ConfirmDeleteButton } from "@/components/common/confirm-delete-button";
import { useCertificates, useDeleteCertificate } from "@/hooks/useCertificates";
import { formatDate } from "@/lib/utils";

export function CertificateList() {
  const { data: certificates, isLoading } = useCertificates();
  const deleteCertificate = useDeleteCertificate();

  if (isLoading) return <LoadingState rows={3} />;

  if (!certificates || certificates.length === 0) {
    return <EmptyState icon={Award} title="No certificates yet" description="Add certificates you've earned to strengthen your profile." />;
  }

  return (
    <div className="space-y-3">
      {certificates.map((cert) => (
        <Card key={cert.id}>
          <CardContent className="flex items-center justify-between gap-4 p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent">
                <Award className="h-4 w-4 text-accent-foreground" />
              </div>
              <div>
                <p className="text-sm font-medium">{cert.title}</p>
                <p className="text-xs text-muted-foreground">
                  {cert.issuer && <>{cert.issuer} · </>}
                  {cert.date_earned ? formatDate(cert.date_earned) : `Added ${formatDate(cert.created_at)}`}
                </p>
              </div>
            </div>
            <ConfirmDeleteButton
              itemLabel={cert.title}
              isPending={deleteCertificate.isPending}
              onConfirm={() => deleteCertificate.mutate(cert.id)}
            />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
