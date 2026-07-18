import { PageHeader } from "@/components/common/page-header";
import { MemoryTimeline } from "@/components/memory/memory-timeline";

export default function MemoryPage() {
  return (
    <div>
      <PageHeader
        title="Memory Timeline"
        description="Everything your AI mentor remembers — including what it has forgotten and why."
      />
      <MemoryTimeline />
    </div>
  );
}
