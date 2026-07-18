"use client";

import { Target, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/common/empty-state";
import { LoadingState } from "@/components/common/loading-state";
import { useCareerGoals } from "@/hooks/useCareerGoals";
import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";

export function CareerGoalList() {
  const { data: goals, isLoading } = useCareerGoals();

  if (isLoading) return <LoadingState rows={3} />;

  if (!goals || goals.length === 0) {
    return (
      <EmptyState
        icon={Target}
        title="No career goal set"
        description="Set a career goal above — it powers your AI roadmap and skill-gap recommendations."
      />
    );
  }

  return (
    <div className="space-y-3">
      {goals.map((goal) => (
        <div
          key={goal.id}
          className={cn(
            "flex items-start gap-3 rounded-lg border p-4",
            goal.status === "active" ? "border-primary/40 bg-accent/40" : "opacity-70"
          )}
        >
          <div className="mt-0.5">
            {goal.status === "active" ? (
              <Target className="h-4 w-4 text-primary" />
            ) : (
              <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
            )}
          </div>
          <div className="flex-1">
            <p className={cn("text-sm", goal.status === "active" ? "font-medium" : "text-muted-foreground line-through")}>
              {goal.goal_text}
            </p>
            <p className="mt-0.5 text-xs text-muted-foreground">Set {formatDate(goal.created_at)}</p>
          </div>
          <Badge variant={goal.status === "active" ? "default" : "secondary"}>
            {goal.status === "active" ? "Current" : "Superseded"}
          </Badge>
        </div>
      ))}
    </div>
  );
}
