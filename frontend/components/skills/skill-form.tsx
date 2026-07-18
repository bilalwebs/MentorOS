"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useAddSkill } from "@/hooks/useSkills";
import type { SkillLevel } from "@/types";

export function SkillForm() {
  const [name, setName] = useState("");
  const [level, setLevel] = useState<SkillLevel>("beginner");
  const addSkill = useAddSkill();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    addSkill.mutate(
      { name: name.trim(), level },
      { onSuccess: () => setName("") }
    );
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2 sm:flex-row">
      <Input
        placeholder="e.g. Python, React, Public Speaking"
        value={name}
        onChange={(e) => setName(e.target.value)}
        className="flex-1"
      />
      <Select value={level} onValueChange={(v) => setLevel(v as SkillLevel)}>
        <SelectTrigger className="sm:w-40">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="beginner">Beginner</SelectItem>
          <SelectItem value="intermediate">Intermediate</SelectItem>
          <SelectItem value="advanced">Advanced</SelectItem>
        </SelectContent>
      </Select>
      <Button type="submit" disabled={addSkill.isPending || !name.trim()}>
        <Plus className="h-4 w-4" /> Add Skill
      </Button>
    </form>
  );
}
