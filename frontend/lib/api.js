const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(endpoint, options = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const headers = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const res = await fetch(`${API_URL}${endpoint}`, { ...options, headers });

  if (res.status === 401) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    throw new ApiError("Unauthorized", 401);
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(body.detail || "Request failed", res.status);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // Auth
  register: (data) => request("/auth/register", { method: "POST", body: JSON.stringify(data) }),
  login: (data) => request("/auth/login", { method: "POST", body: JSON.stringify(data) }),
  getMe: () => request("/auth/me"),

  // Projects
  getProjects: () => request("/projects"),
  createProject: (data) => request("/projects", { method: "POST", body: JSON.stringify(data) }),
  getProject: (id) => request(`/projects/${encodeURIComponent(id)}`),
  updateProject: (id, data) => request(`/projects/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteProject: (id) => request(`/projects/${encodeURIComponent(id)}`, { method: "DELETE" }),

  // Leads
  getLeads: (projectId, params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/leads/${encodeURIComponent(projectId)}${query ? `?${query}` : ""}`);
  },
  updateLeadStatus: (projectId, leadId, status) =>
    request(`/leads/${encodeURIComponent(projectId)}/leads/${encodeURIComponent(leadId)}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),
  getLeadStats: (projectId) => request(`/leads/${encodeURIComponent(projectId)}/stats`),

  // Billing
  getSubscription: () => request("/billing/subscription"),
  createCheckout: (data) => request("/billing/checkout", { method: "POST", body: JSON.stringify(data) }),
  createPortal: () => request("/billing/portal", { method: "POST" }),
};
