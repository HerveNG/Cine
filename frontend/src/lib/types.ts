export type UserType = "AUTHOR" | "DIRECTOR" | "PRODUCER" | "INSTITUTION" | "ADMIN";

export interface User {
  id: number;
  email: string;
  nom: string | null;
  prenom: string | null;
  pays: string | null;
  ville: string | null;
  profession: string | null;
  photo_url: string | null;
  user_type: UserType;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export type ProjectType =
  | "DOCUMENTARY"
  | "FEATURE_FILM"
  | "SHORT_FILM"
  | "TV_SERIES"
  | "WEB_SERIES"
  | "FICTION"
  | "ANIMATION";

export type ProjectStatus =
  | "IDEA"
  | "DEVELOPMENT"
  | "WRITING"
  | "PRE_PRODUCTION"
  | "PRODUCTION"
  | "POST_PRODUCTION"
  | "COMPLETED";

export interface Project {
  id: number;
  user_id: number;
  title: string;
  project_type: ProjectType;
  genre: string | null;
  country: string | null;
  language: string | null;
  duration_minutes: number | null;
  logline: string | null;
  short_synopsis: string | null;
  long_synopsis: string | null;
  theme: string | null;
  target_audience: string | null;
  status: ProjectStatus;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  projects_count: number;
  documents_generated: number;
  compatible_opportunities: number;
  upcoming_deadlines: number;
}

export const PROJECT_TYPE_LABELS: Record<ProjectType, string> = {
  DOCUMENTARY: "Documentaire",
  FEATURE_FILM: "Long métrage",
  SHORT_FILM: "Court métrage",
  TV_SERIES: "Série TV",
  WEB_SERIES: "Web-série",
  FICTION: "Fiction",
  ANIMATION: "Animation",
};

export const PROJECT_STATUS_LABELS: Record<ProjectStatus, string> = {
  IDEA: "Idée",
  DEVELOPMENT: "Développement",
  WRITING: "Écriture",
  PRE_PRODUCTION: "Préproduction",
  PRODUCTION: "Production",
  POST_PRODUCTION: "Postproduction",
  COMPLETED: "Terminé",
};
