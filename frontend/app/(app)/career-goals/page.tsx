"use client";

import { PageHeader } from "@/components/common/page-header";
import { CareerGoalForm } from "@/components/career-goals/career-goal-form";
import { CareerGoalList } from "@/components/career-goals/career-goal-list";
import { useCareerGoals } from "@/hooks/useCareerGoals";

export default function CareerGoalsPage() {
  const { data: goals } = useCareerGoals();
  const hasActiveGoal = !!goals?.some((g) => g.status === "active");

  return (
    <div className="space-y-6">
      <PageHeader
        title="Career Goals"
        description="Setting a new goal supersedes your old one — it's preserved in your memory timeline, not deleted."
      />
      <CareerGoalForm hasActiveGoal={hasActiveGoal} />
      <CareerGoalList />
    </div>
  );
}
