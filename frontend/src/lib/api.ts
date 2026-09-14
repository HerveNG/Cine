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

async function request<T>(
  path: string,
  options: RequestInit & { token?: string | null } = {}
): Promise<T> {
  const { token, headers, ...rest } = options;
  const res = await fetch(`${API_URL}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
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

  me: (token: string) => request<User>("/auth/me", { token }),

  listProjects: (token: string) => request<Project[]>("/projects", { token }),

  getProject: (token: string, id: number) => request<Project>(`/projects/${id}`, { token }),

  createProject: (
    token: string,
    payload: {
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
    }
  ) =>
    request<Project>("/projects", {
      method: "POST",
      token,
      body: JSON.stringify(payload),
    }),

  updateProject: (
    token: string,
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
      token,
      body: JSON.stringify(payload),
    }),

  deleteProject: (token: string, id: number) =>
    request<void>(`/projects/${id}`, { method: "DELETE", token }),

  dashboardStats: (token: string) => request<DashboardStats>("/dashboard/stats", { token }),

  listDocuments: (token: string, projectId: number) =>
    request<AIDocument[]>(`/projects/${projectId}/documents`, { token }),

  listDocumentVersions: (token: string, projectId: number, documentType: DocumentType) =>
    request<AIDocument[]>(`/projects/${projectId}/documents/${documentType}/versions`, {
      token,
    }),

  generateDocument: (
    token: string,
    projectId: number,
    documentType: DocumentType,
    instructions?: string
  ) =>
    request<AIDocument>(`/projects/${projectId}/documents/generate`, {
      method: "POST",
      token,
      body: JSON.stringify({ document_type: documentType, instructions }),
    }),

  regenerateDocument: (token: string, projectId: number, documentId: number) =>
    request<AIDocument>(`/projects/${projectId}/documents/${documentId}/regenerate`, {
      method: "POST",
      token,
    }),

  improveDocument: (token: string, projectId: number, documentId: number, instruction: string) =>
    request<AIDocument>(`/projects/${projectId}/documents/${documentId}/improve`, {
      method: "POST",
      token,
      body: JSON.stringify({ instruction }),
    }),

  shortenDocument: (token: string, projectId: number, documentId: number) =>
    request<AIDocument>(`/projects/${projectId}/documents/${documentId}/shorten`, {
      method: "POST",
      token,
    }),

  listFundingOpportunities: (
    token: string,
    filters: { project_type?: string; country?: string; search?: string } = {}
  ) => {
    const params = new URLSearchParams();
    if (filters.project_type) params.set("project_type", filters.project_type);
    if (filters.country) params.set("country", filters.country);
    if (filters.search) params.set("search", filters.search);
    const query = params.toString();
    return request<FundingOpportunity[]>(
      `/funding-opportunities${query ? `?${query}` : ""}`,
      { token }
    );
  },

  getFundingMatches: (token: string, projectId: number) =>
    request<FundingMatch[]>(`/projects/${projectId}/funding-matches`, { token }),

  getBudget: (token: string, projectId: number) =>
    request<BudgetSummary>(`/projects/${projectId}/budget`, { token }),

  createBudgetCategory: (token: string, projectId: number, name: string) =>
    request<BudgetCategory>(`/projects/${projectId}/budget/categories`, {
      method: "POST",
      token,
      body: JSON.stringify({ name }),
    }),

  deleteBudgetCategory: (token: string, projectId: number, categoryId: number) =>
    request<void>(`/projects/${projectId}/budget/categories/${categoryId}`, {
      method: "DELETE",
      token,
    }),

  createBudgetLineItem: (
    token: string,
    projectId: number,
    categoryId: number,
    payload: { label: string; quantity: string; unit_cost: string; notes?: string }
  ) =>
    request<BudgetLineItem>(`/projects/${projectId}/budget/categories/${categoryId}/items`, {
      method: "POST",
      token,
      body: JSON.stringify(payload),
    }),

  updateBudgetLineItem: (
    token: string,
    projectId: number,
    itemId: number,
    payload: Partial<{ label: string; quantity: string; unit_cost: string; notes: string }>
  ) =>
    request<BudgetLineItem>(`/projects/${projectId}/budget/items/${itemId}`, {
      method: "PUT",
      token,
      body: JSON.stringify(payload),
    }),

  deleteBudgetLineItem: (token: string, projectId: number, itemId: number) =>
    request<void>(`/projects/${projectId}/budget/items/${itemId}`, {
      method: "DELETE",
      token,
    }),

  listMilestones: (token: string, projectId: number) =>
    request<ProductionMilestone[]>(`/projects/${projectId}/milestones`, { token }),

  createMilestone: (
    token: string,
    projectId: number,
    payload: { title: string; start_date: string; end_date?: string; notes?: string }
  ) =>
    request<ProductionMilestone>(`/projects/${projectId}/milestones`, {
      method: "POST",
      token,
      body: JSON.stringify(payload),
    }),

  deleteMilestone: (token: string, projectId: number, milestoneId: number) =>
    request<void>(`/projects/${projectId}/milestones/${milestoneId}`, {
      method: "DELETE",
      token,
    }),

  getUsage: (token: string) => request<UsageSummary>("/subscription/usage", { token }),
};
