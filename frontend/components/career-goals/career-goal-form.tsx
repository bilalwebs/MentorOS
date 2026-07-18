"use client";

import { useState } from "react";
import { Target } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useSetCareerGoal } from "@/hooks/useCareerGoals";

export function CareerGoalForm({ hasActiveGoal }: { hasActiveGoal: boolean }) {
  const [goalText, setGoalText] = useState("");
  const setCareerGoal = useSetCareerGoal();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!goalText.trim()) return;
    setCareerGoal.mutate({ goal_text: goalText.trim() }, { onSuccess: () => setGoalText("") });
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2 sm:flex-row">
      <Input
        placeholder="e.g. Become a Machine Learning Engineer"
        value={goalText}
        onChange={(e) => setGoalText(e.target.value)}
        className="flex-1"
      />
      <Button type="submit" disabled={setCareerGoal.isPending || !goalText.trim()}>
        <Target className="h-4 w-4" /> {hasActiveGoal ? "Update Goal" : "Set Goal"}
      </Button>
    </form>
  );
}
