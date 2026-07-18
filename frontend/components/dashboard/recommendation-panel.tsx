"use client";

import Link from "next/link";
import { Loader2, Sparkles, ArrowRight } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useGenerateRecommendation } from "@/hooks/useRecommendations";

export function RecommendationPanel() {
  const generate = useGenerateRecommendation();

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          <CardTitle className="text-base">AI Recommendation</CardTitle>
        </div>
        <CardDescription>Grounded in everything MentorOS remembers about you.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {generate.isPending ? (
          <div className="flex items-center gap-2 py-4 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" /> Generating your roadmap…
          </div>
        ) : generate.data ? (
          <p className="line-clamp-4 whitespace-pre-line text-sm text-muted-foreground">{generate.data.content}</p>
        ) : (
          <p className="text-sm text-muted-foreground">
            Get a personalized learning roadmap in one click — built from your skills, projects, and career goal.
          </p>
        )}

        <div className="flex gap-2">
          <Button size="sm" disabled={generate.isPending} onClick={() => generate.mutate("roadmap")}>
            {generate.data ? "Regenerate" : "Generate Roadmap"}
          </Button>
          <Button asChild size="sm" variant="ghost">
            <Link href="/recommendations">
              More options <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
