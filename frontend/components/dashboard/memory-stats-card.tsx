"use client";

import { useMemo } from "react";
import { Brain } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useMemoryTimeline } from "@/hooks/useMemory";

const STATUS_COLORS: Record<string, string> = {
  active: "hsl(142 71% 45%)",
  superseded: "hsl(220 10% 60%)",
  archived: "hsl(0 72% 55%)",
};

export function MemoryStatsCard() {
  const { data: memories, isLoading } = useMemoryTimeline();

  const stats = useMemo(() => {
    if (!memories) return null;
    const counts = { active: 0, superseded: 0, archived: 0 };
    for (const m of memories) counts[m.status] += 1;
    const avgImportance =
      memories.filter((m) => m.status === "active").reduce((sum, m) => sum + m.importance_score, 0) /
      (counts.active || 1);
    return { counts, total: memories.length, avgImportance };
  }, [memories]);

  const chartData = stats
    ? [
        { name: "Active", value: stats.counts.active, key: "active" },
        { name: "Superseded", value: stats.counts.superseded, key: "superseded" },
        { name: "Archived", value: stats.counts.archived, key: "archived" },
      ].filter((d) => d.value > 0)
    : [];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Brain className="h-4 w-4 text-primary" />
          <CardTitle className="text-base">Memory Statistics</CardTitle>
        </div>
        <CardDescription>What your AI mentor currently remembers.</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading || !stats ? (
          <Skeleton className="h-48 w-full" />
        ) : stats.total === 0 ? (
          <p className="py-10 text-center text-sm text-muted-foreground">No memories recorded yet.</p>
        ) : (
          <div className="flex flex-col items-center gap-4 sm:flex-row">
            <div className="h-40 w-40 shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={chartData} dataKey="value" nameKey="name" innerRadius={40} outerRadius={65} paddingAngle={3}>
                    {chartData.map((entry) => (
                      <Cell key={entry.key} fill={STATUS_COLORS[entry.key]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex-1 space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-muted-foreground">
                  <span className="h-2 w-2 rounded-full" style={{ background: STATUS_COLORS.active }} /> Active
                </span>
                <span className="font-medium">{stats.counts.active}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-muted-foreground">
                  <span className="h-2 w-2 rounded-full" style={{ background: STATUS_COLORS.superseded }} /> Superseded
                </span>
                <span className="font-medium">{stats.counts.superseded}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-muted-foreground">
                  <span className="h-2 w-2 rounded-full" style={{ background: STATUS_COLORS.archived }} /> Archived
                </span>
                <span className="font-medium">{stats.counts.archived}</span>
              </div>
              <div className="mt-2 flex items-center justify-between border-t pt-2">
                <span className="text-muted-foreground">Avg. importance (active)</span>
                <span className="font-medium">{Math.round(stats.avgImportance * 100)}%</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
