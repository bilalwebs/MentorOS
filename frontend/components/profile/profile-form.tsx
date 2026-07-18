"use client";

import { useEffect, useState } from "react";
import { Loader2, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { LoadingState } from "@/components/common/loading-state";
import { useProfile, useUpdateProfile } from "@/hooks/useProfile";

export function ProfileForm() {
  const { data: profile, isLoading } = useProfile();
  const updateProfile = useUpdateProfile();

  const [fullName, setFullName] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [bio, setBio] = useState("");

  // Sync local form state once the profile loads (or changes from elsewhere,
  // e.g. after a resume upload auto-fills it).
  useEffect(() => {
    if (profile) {
      setFullName(profile.full_name || "");
      setTargetRole(profile.target_role || "");
      setBio(profile.bio || "");
    }
  }, [profile]);

  if (isLoading) return <LoadingState rows={4} />;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfile.mutate({ full_name: fullName, target_role: targetRole, bio });
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-xl space-y-4">
      <div className="space-y-1.5">
        <Label htmlFor="full_name">Full name</Label>
        <Input id="full_name" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Ayesha Khan" />
      </div>
      <div className="space-y-1.5">
        <Label htmlFor="target_role">Target role</Label>
        <Input
          id="target_role"
          value={targetRole}
          onChange={(e) => setTargetRole(e.target.value)}
          placeholder="e.g. Machine Learning Engineer"
        />
      </div>
      <div className="space-y-1.5">
        <Label htmlFor="bio">Bio</Label>
        <Textarea id="bio" value={bio} onChange={(e) => setBio(e.target.value)} placeholder="A short summary about you" rows={4} />
      </div>
      <Button type="submit" disabled={updateProfile.isPending}>
        {updateProfile.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
        Save Profile
      </Button>
    </form>
  );
}
