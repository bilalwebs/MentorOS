"use client";

import { useRef, useState } from "react";
import { FileText, Loader2, UploadCloud } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useUploadResume } from "@/hooks/useResume";

const ACCEPTED_EXTENSIONS = [".pdf", ".txt"];
const MAX_SIZE_BYTES = 5 * 1024 * 1024;

export function ResumeUploader() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const uploadResume = useUploadResume();

  const validateAndUpload = (file: File) => {
    setLocalError(null);
    const extension = "." + file.name.split(".").pop()?.toLowerCase();
    if (!ACCEPTED_EXTENSIONS.includes(extension)) {
      setLocalError("Only PDF or .txt files are supported.");
      return;
    }
    if (file.size > MAX_SIZE_BYTES) {
      setLocalError("File is too large (max 5MB).");
      return;
    }
    uploadResume.mutate(file);
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setIsDragging(false);
            const file = e.dataTransfer.files?.[0];
            if (file) validateAndUpload(file);
          }}
          onClick={() => inputRef.current?.click()}
          className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-10 text-center transition-colors ${
            isDragging ? "border-primary bg-accent/40" : "border-muted-foreground/25 hover:border-primary/50"
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.txt"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) validateAndUpload(file);
              e.target.value = "";
            }}
          />

          {uploadResume.isPending ? (
            <>
              <Loader2 className="mb-3 h-8 w-8 animate-spin text-primary" />
              <p className="font-medium">Processing your resume…</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Extracting skills, projects, and certificates with AI. This may take a few seconds.
              </p>
            </>
          ) : (
            <>
              <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-accent">
                <UploadCloud className="h-6 w-6 text-accent-foreground" />
              </div>
              <p className="font-medium">Drop your resume here, or click to browse</p>
              <p className="mt-1 text-sm text-muted-foreground">PDF or .txt, up to 5MB</p>
              <Button type="button" variant="secondary" className="mt-4" onClick={(e) => e.stopPropagation()}>
                <FileText className="h-4 w-4" /> Choose file
              </Button>
            </>
          )}
        </div>
        {localError && <p className="mt-2 text-sm text-destructive">{localError}</p>}
      </CardContent>
    </Card>
  );
}
