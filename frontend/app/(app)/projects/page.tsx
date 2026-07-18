import { PageHeader } from "@/components/common/page-header";
import { ProjectForm } from "@/components/projects/project-form";
import { ProjectList } from "@/components/projects/project-list";

export default function ProjectsPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Projects" description="Your portfolio history — used to suggest what to build next." />
      <ProjectForm />
      <ProjectList />
    </div>
  );
}
