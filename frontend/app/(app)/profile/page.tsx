import { PageHeader } from "@/components/common/page-header";
import { ProfileForm } from "@/components/profile/profile-form";

export default function ProfilePage() {
  return (
    <div>
      <PageHeader title="Profile" description="This information grounds everything your AI mentor recommends." />
      <ProfileForm />
    </div>
  );
}
