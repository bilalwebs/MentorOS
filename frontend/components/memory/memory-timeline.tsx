"use client";

import { useMemo, useState } from "react";
import { Brain } from "lucide-react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EmptyState } from "@/components/common/empty-state";
import { LoadingState } from "@/components/common/loading-state";
import { MemoryCard } from "@/components/memory/memory-card";
import { useMemoryTimeline } from "@/hooks/useMemory";
import type { MemoryStatus } from "@/types";

type FilterValue = "all" | MemoryStatus;

export function MemoryTimeline() {
  const { data: memories, isLoading } = useMemoryTimeline();
  const [filter, setFilter] = useState<FilterValue>("all");

  const filtered = useMemo(() => {
    if (!memories) return [];
    if (filter === "all") return memories;
    return memories.filter((m) => m.status === filter);
  }, [memories, filter]);

  if (isLoading) return <LoadingState rows={5} />;

  if (!memories || memories.length === 0) {
    return (
      <EmptyState
        icon={Brain}
        title="No memories yet"
        description="As you add skills, projects, goals, and use AI recommendations, MentorOS builds a persistent memory here."
      />
    );
  }

  return (
    <div className="space-y-4">
      <Tabs value={filter} onValueChange={(v) => setFilter(v as FilterValue)}>
        <TabsList>
          <TabsTrigger value="all">All ({memories.length})</TabsTrigger>
          <TabsTrigger value="active">Active ({memories.filter((m) => m.status === "active").length})</TabsTrigger>
          <TabsTrigger value="superseded">
            Superseded ({memories.filter((m) => m.status === "superseded").length})
          </TabsTrigger>
          <TabsTrigger value="archived">Archived ({memories.filter((m) => m.status === "archived").length})</TabsTrigger>
        </TabsList>
      </Tabs>

      {filtered.length === 0 ? (
        <EmptyState icon={Brain} title={`No ${filter} memories`} />
      ) : (
        <div className="space-y-3">
          {filtered.map((memory) => (
            <MemoryCard key={memory.id} memory={memory} />
          ))}
        </div>
      )}
    </div>
  );
}
