import { PageHeader } from "@/components/common/page-header";
import { ResumeUploader } from "@/components/resume/resume-uploader";
import { ResumeHistory } from "@/components/resume/resume-history";

export default function ResumePage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Resume Upload & Analysis" description="Upload once — AI extracts your skills, projects, and certificates automatically." />
      <ResumeUploader />
      <div>
        <h2 className="mb-3 text-sm font-semibold text-muted-foreground">Upload history</h2>
        <ResumeHistory />
      </div>
    </div>
  );
}
