"use client";

import { Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/common/empty-state";
import { LoadingState } from "@/components/common/loading-state";
import { ConfirmDeleteButton } from "@/components/common/confirm-delete-button";
import { useDeleteSkill, useSkills } from "@/hooks/useSkills";
import { humanizeEnum } from "@/lib/utils";

const LEVEL_VARIANT: Record<string, "secondary" | "default" | "success"> = {
  beginner: "secondary",
  intermediate: "default",
  advanced: "success",
};

export function SkillList() {
  const { data: skills, isLoading } = useSkills();
  const deleteSkill = useDeleteSkill();

  if (isLoading) return <LoadingState rows={4} />;

  if (!skills || skills.length === 0) {
    return (
      <EmptyState
        icon={Sparkles}
        title="No skills yet"
        description="Add your first skill above, or upload a resume to extract skills automatically."
      />
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {skills.map((skill) => (
        <div
          key={skill.id}
          className="flex items-center gap-2 rounded-full border bg-card py-1 pl-3 pr-1 shadow-sm"
        >
          <span className="text-sm font-medium">{skill.name}</span>
          <Badge variant={LEVEL_VARIANT[skill.level]}>{humanizeEnum(skill.level)}</Badge>
          <ConfirmDeleteButton
            itemLabel={skill.name}
            isPending={deleteSkill.isPending}
            onConfirm={() => deleteSkill.mutate(skill.id)}
          />
        </div>
      ))}
    </div>
  );
}
