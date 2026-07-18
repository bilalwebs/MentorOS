import { PageHeader } from "@/components/common/page-header";
import { RecommendationCard } from "@/components/recommendations/recommendation-card";

export default function RecommendationsPage() {
  return (
    <div>
      <PageHeader
        title="AI Recommendations"
        description="Every recommendation is grounded in your remembered skills, projects, and career goal — and gets saved back to memory."
      />
      <div className="grid gap-4 md:grid-cols-3">
        <RecommendationCard type="roadmap" />
        <RecommendationCard type="skill_gap" />
        <RecommendationCard type="project_recommendation" />
      </div>
    </div>
  );
}
