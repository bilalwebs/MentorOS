"use client";

import { Brain, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ConfirmDeleteButton } from "@/components/common/confirm-delete-button";
import { useForgetMemory } from "@/hooks/useMemory";
import { formatDate, humanizeEnum, timeAgo } from "@/lib/utils";
import type { MemoryRead } from "@/types";

const STATUS_VARIANT: Record<string, "success" | "secondary" | "destructive"> = {
  active: "success",
  superseded: "secondary",
  archived: "destructive",
};

export function MemoryCard({ memory }: { memory: MemoryRead }) {
  const forgetMemory = useForgetMemory();

  return (
    <div className="flex flex-col gap-2 rounded-lg border bg-card p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <Badge variant="outline">{humanizeEnum(memory.memory_type)}</Badge>
          <Badge variant={STATUS_VARIANT[memory.status]}>{humanizeEnum(memory.status)}</Badge>
        </div>
        <ConfirmDeleteButton
          itemLabel="this memory"
          isPending={forgetMemory.isPending}
          onConfirm={() => forgetMemory.mutate(memory.id)}
        />
      </div>

      <p className="text-sm">{memory.content_text}</p>

      <div className="flex items-center gap-2">
        <span className="text-xs text-muted-foreground">Importance</span>
        <Progress value={memory.importance_score * 100} className="h-1.5 max-w-[120px]" />
        <span className="text-xs text-muted-foreground">{Math.round(memory.importance_score * 100)}%</span>
      </div>

      <div className="flex items-center gap-3 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <Clock className="h-3 w-3" /> Created {formatDate(memory.created_at)}
        </span>
        <span>Last used {timeAgo(memory.last_accessed_at)}</span>
      </div>

      {memory.superseded_by_id && (
        <p className="text-xs text-muted-foreground">
          <Brain className="mr-1 inline h-3 w-3" />
          Replaced by a newer memory (#{memory.superseded_by_id})
        </p>
      )}
    </div>
  );
}
