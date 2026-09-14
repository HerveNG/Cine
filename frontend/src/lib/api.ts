import type {
  AIDocument,
  AuthResponse,
  BudgetCategory,
  BudgetLineItem,
  BudgetSummary,
  DashboardStats,
  DocumentType,
  FundingMatch,
  FundingOpportunity,
  Notification,
  Project,
  ProjectStatus,
  ProjectType,
  ProductionMilestone,
  UsageSummary,
  User,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const { headers, ...rest } = options;
  const res = await fetch(`${API_URL}${path}`, {
    ...rest,
    // Sends and accepts the httpOnly access_token cookie — the only way
    // this app authenticates. The token itself never touches frontend
    // JS (no Authorization header, no localStorage) — see
    // lib/auth-context.tsx.
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore body parse errors
    }
    throw new ApiError(detail, res.status);
  }

  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

export interface RegisterPayload {
  email: string;
  password: string;
  nom?: string;
  prenom?: string;
  pays?: string;
  ville?: string;
  profession?: string;
  user_type?: string;
}

export const api = {
  register: (payload: RegisterPayload) =>
    request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  login: (email: string, password: string) =>
    request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  logout: () => request<void>("/auth/logout", { method: "POST" }),

  me: () => request<User>("/auth/me"),

  listProjects: () => request<Project[]>("/projects"),

  getProject: (id: number) => request<Project>(`/projects/${id}`),

  createProject: (payload: {
    title: string;
    project_type: ProjectType;
    genre?: string;
    country?: string;
    language?: string;
    duration_minutes?: number;
    logline?: string;
    short_synopsis?: string;
    long_synopsis?: string;
    theme?: string;
    target_audience?: string;
  }) =>
    request<Project>("/projects", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateProject: (
    id: number,
    payload: Partial<{
      title: string;
      project_type: ProjectType;
      genre: string;
      country: string;
      language: string;
      duration_minutes: number;
      logline: string;
      short_synopsis: string;
      long_synopsis: string;
      theme: string;
      target_audience: string;
      budget_currency: string;
      status: ProjectStatus;
    }>
  ) =>
    request<Project>(`/projects/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),

  deleteProject: (id: number) => request<void>(`/projects/${id}`, { method: "DELETE" }),

  dashboardStats: () => request<DashboardStats>("/dashboard/stats"),

  listDocuments: (projectId: number) => request<AIDocument[]>(`/projects/${projectId}/documents`),

  listDocumentVersions: (projectId: number, documentType: DocumentType) =>
    request<AIDocument[]>(`/projects/${projectId}/documents/${documentType}/versions`),

  generateDocument: (projectId: number, documentType: DocumentType, instructions?: string) =>
    request<AIDocument>(`/projects/${projectId}/documents/generate`, {
      method: "POST",
      body: JSON.stringify({ document_type: documentType, instructions }),
    }),

  regenerateDocument: (projectId: number, documentId: number) =>
    request<AIDocument>(`/projects/${projectId}/documents/${documentId}/regenerate`, {
      method: "POST",
    }),

  improveDocument: (projectId: number, documentId: number, instruction: string) =>
    request<AIDocument>(`/projects/${projectId}/documents/${documentId}/improve`, {
      method: "POST",
      body: JSON.stringify({ instruction }),
    }),

  shortenDocument: (projectId: number, documentId: number) =>
    request<AIDocument>(`/projects/${projectId}/documents/${documentId}/shorten`, {
      method: "POST",
    }),

  listFundingOpportunities: (
    filters: { project_type?: string; country?: string; search?: string } = {}
  ) => {
    const params = new URLSearchParams();
    if (filters.project_type) params.set("project_type", filters.project_type);
    if (filters.country) params.set("country", filters.country);
    if (filters.search) params.set("search", filters.search);
    const query = params.toString();
    return request<FundingOpportunity[]>(`/funding-opportunities${query ? `?${query}` : ""}`);
  },

  getFundingMatches: (projectId: number) =>
    request<FundingMatch[]>(`/projects/${projectId}/funding-matches`),

  getBudget: (projectId: number) => request<BudgetSummary>(`/projects/${projectId}/budget`),

  createBudgetCategory: (projectId: number, name: string) =>
    request<BudgetCategory>(`/projects/${projectId}/budget/categories`, {
      method: "POST",
      body: JSON.stringify({ name }),
    }),

  deleteBudgetCategory: (projectId: number, categoryId: number) =>
    request<void>(`/projects/${projectId}/budget/categories/${categoryId}`, {
      method: "DELETE",
    }),

  createBudgetLineItem: (
    projectId: number,
    categoryId: number,
    payload: { label: string; quantity: string; unit_cost: string; notes?: string }
  ) =>
    request<BudgetLineItem>(`/projects/${projectId}/budget/categories/${categoryId}/items`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateBudgetLineItem: (
    projectId: number,
    itemId: number,
    payload: Partial<{ label: string; quantity: string; unit_cost: string; notes: string }>
  ) =>
    request<BudgetLineItem>(`/projects/${projectId}/budget/items/${itemId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),

  deleteBudgetLineItem: (projectId: number, itemId: number) =>
    request<void>(`/projects/${projectId}/budget/items/${itemId}`, { method: "DELETE" }),

  listMilestones: (projectId: number) =>
    request<ProductionMilestone[]>(`/projects/${projectId}/milestones`),

  createMilestone: (
    projectId: number,
    payload: { title: string; start_date: string; end_date?: string; notes?: string }
  ) =>
    request<ProductionMilestone>(`/projects/${projectId}/milestones`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  deleteMilestone: (projectId: number, milestoneId: number) =>
    request<void>(`/projects/${projectId}/milestones/${milestoneId}`, { method: "DELETE" }),

  getUsage: () => request<UsageSummary>("/subscription/usage"),

  followFundingOpportunity: (opportunityId: number) =>
    request<FundingOpportunity>(`/funding-opportunities/${opportunityId}/follow`, {
      method: "POST",
    }),

  unfollowFundingOpportunity: (opportunityId: number) =>
    request<FundingOpportunity>(`/funding-opportunities/${opportunityId}/follow`, {
      method: "DELETE",
    }),

  listNotifications: () => request<Notification[]>("/notifications"),

  markNotificationRead: (notificationId: number) =>
    request<Notification>(`/notifications/${notificationId}/read`, { method: "PUT" }),

  markAllNotificationsRead: () => request<void>("/notifications/read-all", { method: "PUT" }),
};
