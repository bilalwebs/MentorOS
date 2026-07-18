"use client";

import { PageHeader } from "@/components/common/page-header";
import { QuickActions } from "@/components/dashboard/quick-actions";
import { SummaryCards } from "@/components/dashboard/summary-cards";
import { MemoryStatsCard } from "@/components/dashboard/memory-stats-card";
import { SkillChart } from "@/components/dashboard/skill-chart";
import { ResumeStatusCard } from "@/components/dashboard/resume-status-card";
import { RecommendationPanel } from "@/components/dashboard/recommendation-panel";
import { ActivityTimeline } from "@/components/dashboard/activity-timeline";
import { useAuth } from "@/lib/auth-context";

export default function DashboardPage() {
  const { user } = useAuth();
  const firstName = user?.email?.split("@")[0];

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Welcome back${firstName ? `, ${firstName}` : ""}`}
        description="Here's what your AI mentor remembers and recommends today."
        actions={<QuickActions />}
      />

      <SummaryCards />

      <div className="grid gap-4 lg:grid-cols-2">
        <MemoryStatsCard />
        <SkillChart />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <RecommendationPanel />
        </div>
        <ResumeStatusCard />
      </div>

      <ActivityTimeline />
    </div>
  );
}
