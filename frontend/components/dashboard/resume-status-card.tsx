"use client";

import Link from "next/link";
import { FileText, CheckCircle2, UploadCloud } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useResumes } from "@/hooks/useResume";
import { formatDate } from "@/lib/utils";

export function ResumeStatusCard() {
  const { data: resumes, isLoading } = useResumes();
  const latest = resumes?.[0];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-primary" />
          <CardTitle className="text-base">Resume Status</CardTitle>
        </div>
        <CardDescription>Keep your resume current so extraction stays accurate.</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton className="h-16 w-full" />
        ) : latest ? (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle2 className="h-4 w-4 text-success" />
              <span className="font-medium">{latest.original_filename}</span>
            </div>
            <p className="text-xs text-muted-foreground">
              Uploaded {formatDate(latest.created_at)}
              {latest.parsed_at && <> · Parsed {formatDate(latest.parsed_at)}</>}
            </p>
            <Button asChild variant="outline" size="sm" className="w-full">
              <Link href="/resume">
                <UploadCloud className="h-4 w-4" /> Upload new version
              </Link>
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">No resume uploaded yet.</p>
            <Button asChild size="sm" className="w-full">
              <Link href="/resume">
                <UploadCloud className="h-4 w-4" /> Upload your resume
              </Link>
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
