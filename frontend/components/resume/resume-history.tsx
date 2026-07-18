"use client";

import { FileText, CheckCircle2, Clock } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/common/empty-state";
import { LoadingState } from "@/components/common/loading-state";
import { useResumes } from "@/hooks/useResume";
import { formatDate } from "@/lib/utils";

export function ResumeHistory() {
  const { data: resumes, isLoading } = useResumes();

  if (isLoading) return <LoadingState rows={2} />;

  if (!resumes || resumes.length === 0) {
    return <EmptyState icon={FileText} title="No resumes uploaded yet" />;
  }

  return (
    <div className="space-y-3">
      {resumes.map((resume) => (
        <Card key={resume.id}>
          <CardContent className="flex items-center justify-between gap-4 p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent">
                <FileText className="h-4 w-4 text-accent-foreground" />
              </div>
              <div>
                <p className="text-sm font-medium">{resume.original_filename}</p>
                <p className="text-xs text-muted-foreground">Uploaded {formatDate(resume.created_at)}</p>
              </div>
            </div>
            <div className="flex items-center gap-1.5 text-xs">
              {resume.parsed_at ? (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5 text-success" />
                  <span className="text-muted-foreground">Parsed</span>
                </>
              ) : (
                <>
                  <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                  <span className="text-muted-foreground">Pending</span>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
