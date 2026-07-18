"use client";

import Link from "next/link";
import { Sparkles, FolderKanban, UploadCloud, Target } from "lucide-react";
import { Button } from "@/components/ui/button";

const ACTIONS = [
  { href: "/skills", label: "Add Skill", icon: Sparkles },
  { href: "/projects", label: "Add Project", icon: FolderKanban },
  { href: "/resume", label: "Upload Resume", icon: UploadCloud },
  { href: "/career-goals", label: "Set Career Goal", icon: Target },
];

export function QuickActions() {
  return (
    <div className="flex flex-wrap gap-2">
      {ACTIONS.map(({ href, label, icon: Icon }) => (
        <Button key={href} asChild variant="outline" size="sm">
          <Link href={href}>
            <Icon className="h-4 w-4" /> {label}
          </Link>
        </Button>
      ))}
    </div>
  );
}
