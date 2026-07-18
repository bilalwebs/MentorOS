import { PageHeader } from "@/components/common/page-header";
import { SkillForm } from "@/components/skills/skill-form";
import { SkillList } from "@/components/skills/skill-list";

export default function SkillsPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Skills" description="Track what you know — your AI mentor uses this for gap analysis and recommendations." />
      <SkillForm />
      <SkillList />
    </div>
  );
}
