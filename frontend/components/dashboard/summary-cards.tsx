"use client";

import { Sparkles, FolderKanban, Award, Target } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useSkills } from "@/hooks/useSkills";
import { useProjects } from "@/hooks/useProjects";
import { useCertificates } from "@/hooks/useCertificates";
import { useCareerGoals } from "@/hooks/useCareerGoals";

function StatCard({
  icon: Icon,
  label,
  value,
  isLoading,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  isLoading: boolean;
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 p-5">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent">
          <Icon className="h-5 w-5 text-accent-foreground" />
        </div>
        <div className="min-w-0">
          <p className="text-xs text-muted-foreground">{label}</p>
          {isLoading ? <Skeleton className="mt-1 h-6 w-12" /> : <p className="truncate text-lg font-bold">{value}</p>}
        </div>
      </CardContent>
    </Card>
  );
}

export function SummaryCards() {
  const { data: skills, isLoading: skillsLoading } = useSkills();
  const { data: projects, isLoading: projectsLoading } = useProjects();
  const { data: certificates, isLoading: certsLoading } = useCertificates();
  const { data: goals, isLoading: goalsLoading } = useCareerGoals();

  const activeGoal = goals?.find((g) => g.status === "active");

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard icon={Sparkles} label="Skills tracked" value={skills?.length ?? 0} isLoading={skillsLoading} />
      <StatCard icon={FolderKanban} label="Projects" value={projects?.length ?? 0} isLoading={projectsLoading} />
      <StatCard icon={Award} label="Certificates" value={certificates?.length ?? 0} isLoading={certsLoading} />
      <StatCard
        icon={Target}
        label="Career goal"
        value={activeGoal ? activeGoal.goal_text : "Not set"}
        isLoading={goalsLoading}
      />
    </div>
  );
}
