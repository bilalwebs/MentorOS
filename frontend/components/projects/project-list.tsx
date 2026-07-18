"use client";

import { FolderKanban } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/common/empty-state";
import { LoadingState } from "@/components/common/loading-state";
import { ConfirmDeleteButton } from "@/components/common/confirm-delete-button";
import { useDeleteProject, useProjects } from "@/hooks/useProjects";
import { formatDate } from "@/lib/utils";

export function ProjectList() {
  const { data: projects, isLoading } = useProjects();
  const deleteProject = useDeleteProject();

  if (isLoading) return <LoadingState rows={3} />;

  if (!projects || projects.length === 0) {
    return <EmptyState icon={FolderKanban} title="No projects yet" description="Add a project to build your portfolio history." />;
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {projects.map((project) => (
        <Card key={project.id}>
          <CardHeader className="flex flex-row items-start justify-between space-y-0">
            <div>
              <CardTitle className="text-base">{project.title}</CardTitle>
              <p className="mt-1 text-xs text-muted-foreground">Added {formatDate(project.created_at)}</p>
            </div>
            <ConfirmDeleteButton
              itemLabel={project.title}
              isPending={deleteProject.isPending}
              onConfirm={() => deleteProject.mutate(project.id)}
            />
          </CardHeader>
          <CardContent>
            {project.description && <p className="text-sm text-muted-foreground">{project.description}</p>}
            {project.tech_stack.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1.5">
                {project.tech_stack.map((tech) => (
                  <Badge key={tech} variant="secondary">
                    {tech}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
