"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  User,
  FileText,
  Sparkles,
  FolderKanban,
  Award,
  Target,
  Brain,
  Settings,
  GraduationCap,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/profile", label: "Profile", icon: User },
  { href: "/resume", label: "Resume", icon: FileText },
  { href: "/skills", label: "Skills", icon: Sparkles },
  { href: "/projects", label: "Projects", icon: FolderKanban },
  { href: "/certificates", label: "Certificates", icon: Award },
  { href: "/career-goals", label: "Career Goals", icon: Target },
  { href: "/memory", label: "Memory Timeline", icon: Brain },
  { href: "/recommendations", label: "AI Recommendations", icon: Sparkles },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <div className="flex h-full flex-col gap-2 p-4">
      <Link href="/dashboard" className="flex items-center gap-2 px-2 py-3" onClick={onNavigate}>
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <GraduationCap className="h-5 w-5" />
        </div>
        <span className="text-lg font-bold tracking-tight">MentorOS</span>
      </Link>

      <nav className="flex flex-1 flex-col gap-1">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              onClick={onNavigate}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="rounded-lg bg-accent/50 p-3 text-xs text-muted-foreground">
        <p className="font-medium text-accent-foreground">MentorOS remembers</p>
        <p className="mt-1">Every skill, project, and goal you add feeds your AI mentor&apos;s persistent memory.</p>
      </div>
    </div>
  );
}
