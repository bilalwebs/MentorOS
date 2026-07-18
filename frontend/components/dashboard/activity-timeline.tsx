"use client";

import { Brain, Clock } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/common/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { useMemoryTimeline } from "@/hooks/useMemory";
import { humanizeEnum, timeAgo } from "@/lib/utils";

export function ActivityTimeline() {
  const { data: memories, isLoading } = useMemoryTimeline();
  const recent = memories?.slice(0, 6);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-primary" />
          <CardTitle className="text-base">Recent Activity</CardTitle>
        </div>
        <CardDescription>The latest things your AI mentor has learned or generated.</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        ) : !recent || recent.length === 0 ? (
          <EmptyState icon={Brain} title="No activity yet" />
        ) : (
          <ol className="space-y-4">
            {recent.map((memory, i) => (
              <li key={memory.id} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <span className="mt-1 h-2 w-2 rounded-full bg-primary" />
                  {i < recent.length - 1 && <span className="mt-1 h-full w-px flex-1 bg-border" />}
                </div>
                <div className="pb-1">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-[10px]">
                      {humanizeEnum(memory.memory_type)}
                    </Badge>
                    <span className="text-xs text-muted-foreground">{timeAgo(memory.created_at)}</span>
                  </div>
                  <p className="mt-1 line-clamp-1 text-sm">{memory.content_text}</p>
                </div>
              </li>
            ))}
          </ol>
        )}
      </CardContent>
    </Card>
  );
}
