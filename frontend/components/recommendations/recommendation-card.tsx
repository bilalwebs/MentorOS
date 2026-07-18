"use client";

import { Loader2, Sparkles, Brain } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useGenerateRecommendation } from "@/hooks/useRecommendations";
import type { InsightType } from "@/types";

const COPY: Record<InsightType, { title: string; description: string; cta: string }> = {
  roadmap: {
    title: "Learning Roadmap",
    description: "A personalized 3-month plan grounded in your skills, projects, and career goal.",
    cta: "Generate Roadmap",
  },
  skill_gap: {
    title: "Skill Gap Analysis",
    description: "What's missing between where you are and where your career goal needs you to be.",
    cta: "Analyze Skill Gaps",
  },
  project_recommendation: {
    title: "Project Ideas",
    description: "Portfolio project ideas that build on skills you already have.",
    cta: "Suggest Projects",
  },
};

export function RecommendationCard({ type }: { type: InsightType }) {
  const generate = useGenerateRecommendation();
  const copy = COPY[type];
  const result = generate.data?.insight_type === type ? generate.data : undefined;

  return (
    <Card className="flex flex-col">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          <CardTitle className="text-base">{copy.title}</CardTitle>
        </div>
        <CardDescription>{copy.description}</CardDescription>
      </CardHeader>
      <CardContent className="flex-1">
        {generate.isPending ? (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" /> Retrieving memory and thinking…
          </div>
        ) : result ? (
          <div className="space-y-2">
            <p className="whitespace-pre-line text-sm">{result.content}</p>
            <p className="flex items-center gap-1 text-xs text-muted-foreground">
              <Brain className="h-3 w-3" /> Grounded in {result.based_on_memory_count} remembered facts about you
            </p>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">Nothing generated yet.</p>
        )}
      </CardContent>
      <CardFooter>
        <Button
          variant={result ? "outline" : "default"}
          className="w-full"
          disabled={generate.isPending}
          onClick={() => generate.mutate(type)}
        >
          {generate.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
          {result ? "Regenerate" : copy.cta}
        </Button>
      </CardFooter>
    </Card>
  );
}
