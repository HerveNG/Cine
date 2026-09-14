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
  budget_currency: string | null;
  status: ProjectStatus;
  created_at: string;
  updated_at: string;
}

export interface BudgetLineItem {
  id: number;
  category_id: number;
  label: string;
  quantity: string;
  unit_cost: string;
  notes: string | null;
  subtotal: string;
  created_at: string;
}

export interface BudgetCategory {
  id: number;
  project_id: number;
  name: string;
  position: number;
  line_items: BudgetLineItem[];
  subtotal: string;
}

export interface BudgetSummary {
  currency: string | null;
  categories: BudgetCategory[];
  total: string;
}

export interface ProductionMilestone {
  id: number;
  project_id: number;
  title: string;
  start_date: string;
  end_date: string | null;
  notes: string | null;
  created_at: string;
}

export type DocumentType =
  | "LOGLINE"
  | "SYNOPSIS_SHORT"
  | "SYNOPSIS_LONG"
  | "NOTE_INTENTION"
  | "TRAITEMENT"
  | "PITCH";

export interface AIDocument {
  id: number;
  project_id: number;
  document_type: DocumentType;
  version: number;
  content: string;
  instructions: string | null;
  provider: string;
  created_at: string;
}

export const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
  LOGLINE: "Logline",
  SYNOPSIS_SHORT: "Synopsis court",
  SYNOPSIS_LONG: "Synopsis long",
  NOTE_INTENTION: "Note d'intention",
  TRAITEMENT: "Traitement",
  PITCH: "Pitch",
};

export const DOCUMENT_TYPES = Object.keys(DOCUMENT_TYPE_LABELS) as DocumentType[];

export interface FundingOpportunity {
  id: number;
  name: string;
  organization: string;
  description: string;
  url: string;
  eligible_project_types: string[];
  eligible_countries: string[];
  eligible_stages: string[];
  min_duration_minutes: number | null;
  max_duration_minutes: number | null;
  amount_label: string;
  application_info: string;
  created_at: string;
}

export interface FundingMatch {
  opportunity: FundingOpportunity;
  score: number;
  project_type_match: boolean;
  country_match: boolean;
  stage_match: boolean;
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
