import type {
  AuthResponse,
  DashboardStats,
  Project,
  ProjectStatus,
  ProjectType,
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
};
