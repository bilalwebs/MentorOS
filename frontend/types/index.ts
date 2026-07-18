/**
 * types/index.ts
 *
 * Every type here mirrors a backend Pydantic schema field-for-field
 * (see backend/app/schemas/*.py). Keeping this file in exact sync with
 * the API contract is what lets the rest of the frontend trust its data
 * shapes without runtime validation on every response.
 */

// ---------------------------------------------------------------- Enums

export type SkillLevel = "beginner" | "intermediate" | "advanced";

export type GoalStatus = "active" | "achieved" | "superseded";

export type MemoryStatus = "active" | "superseded" | "archived";

export type MemoryType =
  | "profile"
  | "skill"
  | "project"
  | "career_goal"
  | "resume"
  | "certificate"
  | "learning_history"
  | "ai_insight";

export type InsightType = "roadmap" | "skill_gap" | "project_recommendation";

// ---------------------------------------------------------------- Auth

export interface UserRead {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface UserCreatePayload {
  email: string;
  password: string;
}

export interface UserLoginPayload {
  email: string;
  password: string;
}

// ------------------------------------------------------------- Profile

export interface ProfileRead {
  id: number;
  user_id: number;
  full_name: string;
  bio: string | null;
  target_role: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProfileUpdatePayload {
  full_name?: string;
  bio?: string;
  target_role?: string;
}

// --------------------------------------------------------------- Skill

export interface SkillRead {
  id: number;
  name: string;
  level: SkillLevel;
  source: string;
  created_at: string;
}

export interface SkillCreatePayload {
  name: string;
  level: SkillLevel;
}

// ------------------------------------------------------------- Project

export interface ProjectRead {
  id: number;
  title: string;
  description: string | null;
  tech_stack: string[];
  created_at: string;
}

export interface ProjectCreatePayload {
  title: string;
  description?: string;
  tech_stack: string[];
}

// --------------------------------------------------------- Certificate

export interface CertificateRead {
  id: number;
  title: string;
  issuer: string | null;
  date_earned: string | null;
  created_at: string;
}

export interface CertificateCreatePayload {
  title: string;
  issuer?: string;
  date_earned?: string;
}

// -------------------------------------------------------- Career Goal

export interface CareerGoalRead {
  id: number;
  goal_text: string;
  status: GoalStatus;
  superseded_by_id: number | null;
  created_at: string;
}

export interface CareerGoalCreatePayload {
  goal_text: string;
}

// -------------------------------------------------------------- Memory

export interface MemoryRead {
  id: number;
  memory_type: MemoryType;
  content_text: string;
  importance_score: number;
  status: MemoryStatus;
  source_table: string | null;
  superseded_by_id: number | null;
  created_at: string;
  last_accessed_at: string;
}

// -------------------------------------------------------------- Resume

export interface ResumeRead {
  id: number;
  original_filename: string;
  parsed_at: string | null;
  created_at: string;
}

export interface ResumeUploadResult {
  resume_id: number;
  filename: string;
  extracted: {
    skills: number;
    projects: number;
    certificates: number;
    profile_updated: boolean;
    career_goal_set: boolean;
  };
}

// ------------------------------------------------------ Recommendations

export interface RecommendationResult {
  insight_type: InsightType;
  content: string;
  based_on_memory_count: number;
  generated_at: string;
}

// ----------------------------------------------------------------- API

export interface ApiError {
  detail: string;
}
