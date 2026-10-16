import type {
  AdminUser,
  AuthUser,
  ExecutiveSummary,
  Initiative,
  InitiativeTemplate,
  ManagedInitiative,
  QualityIssue,
  WhatIf,
} from './types';

const API = '/backend';

async function json<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, { cache: 'no-store', credentials: 'include', ...init });
  if (!response.ok) {
    const raw = await response.text();
    let message = raw || `HTTP ${response.status}`;
    try {
      const parsed = JSON.parse(raw);
      message = parsed.detail || message;
    } catch {}
    const error = new Error(message) as Error & { status?: number };
    error.status = response.status;
    throw error;
  }
  return response.json() as Promise<T>;
}

export function getSummary(scope = 'all') {
  return json<ExecutiveSummary>(`${API}/api/observatory/summary?scope=${scope}`);
}

export function getInitiatives(includeActivities = false, scope = 'all') {
  return json<Initiative[]>(`${API}/api/initiatives?scope=${scope}&include_activities=${includeActivities}`);
}

export function getInitiative(code: string) {
  return json<Initiative>(`${API}/api/initiatives/${encodeURIComponent(code)}`);
}

export function runWhatIf(code: string, progress: number, scope = 'all') {
  return json<WhatIf>(`${API}/api/observatory/what-if?scope=${scope}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ initiative_code: code, progress_percent: progress }),
  });
}

export function getQuality() {
  return json<{ count: number; critical: number; high: number; issues: QualityIssue[] }>(`${API}/api/observatory/data-quality`);
}

export function getGaps(scope = 'all') {
  return json<{initiatives:Array<{initiative:string;dimension:string;contribution:number;maturity:number;sensitivity:number}>;key_results:Array<{kr:string;compliance:number}>}>(`${API}/api/observatory/gaps?scope=${scope}`);
}

export function getDimensions() { return json<any[]>(`${API}/api/model/dimensions`); }
export function getObjectives() { return json<any[]>(`${API}/api/model/objectives`); }
export function getKeyResults() { return json<any[]>(`${API}/api/model/key-results`); }
export function getKpis() { return json<any[]>(`${API}/api/model/kpis`); }
export function getTraceability() { return json<any[]>(`${API}/api/model/traceability`); }

export function verifyInitiative(code: string, progress: number, verifiedBy: string, note: string) {
  return json<Initiative>(`${API}/api/initiatives/${encodeURIComponent(code)}/verification`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ progress_percent: progress, verified_by: verifiedBy, note }),
  });
}

// Authentication
export function login(email: string, password: string) {
  return json<{ user: AuthUser }>(`${API}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
}

export function logout() {
  return json<{ ok: boolean }>(`${API}/api/auth/logout`, { method: 'POST' });
}

export function getMe() {
  return json<{ user: AuthUser }>(`${API}/api/auth/me`);
}

export function changePassword(currentPassword: string, newPassword: string) {
  return json<{ ok: boolean }>(`${API}/api/auth/change-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  });
}

// Authorized management
export function getManagedInitiatives() {
  return json<ManagedInitiative[]>(`${API}/api/management/initiatives`);
}

export function getManagedInitiative(code: string) {
  return json<ManagedInitiative>(`${API}/api/management/initiatives/${encodeURIComponent(code)}`);
}

export function updateManagedActivity(activityId: number, payload: {
  progress?: number | null;
  state?: string | null;
  priority?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  observation?: string | null;
  justification: string;
}) {
  return json<{ ok: boolean; activity_id: number; progress?: number | null; state?: string | null }>(`${API}/api/management/activities/${activityId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export async function uploadActivityEvidence(activityId: number, file: File, description: string) {
  const form = new FormData();
  form.append('file', file);
  form.append('description', description);
  const response = await fetch(`${API}/api/management/activities/${activityId}/evidence`, {
    method: 'POST',
    body: form,
    credentials: 'include',
  });
  if (!response.ok) {
    const raw = await response.text();
    let message = raw || `HTTP ${response.status}`;
    try { message = JSON.parse(raw).detail || message; } catch {}
    throw new Error(message);
  }
  return response.json();
}

export function getInitiativeAudit(code: string) {
  return json<any>(`${API}/api/management/initiatives/${encodeURIComponent(code)}/audit`);
}

// Administration
export function getAdminUsers() {
  return json<AdminUser[]>(`${API}/api/admin/users`);
}

export function createAdminUser(payload: {
  name: string;
  email: string;
  password: string;
  role: 'admin' | 'responsible';
  initiative_codes: string[];
}) {
  return json<AdminUser>(`${API}/api/admin/users`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function updateAdminUser(userId: number, payload: Partial<{
  name: string;
  role: 'admin' | 'responsible';
  is_active: boolean;
  initiative_codes: string[];
}>) {
  return json<AdminUser>(`${API}/api/admin/users/${userId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function getInitiativeTemplate() {
  return json<InitiativeTemplate>(`${API}/api/admin/initiative-template`);
}

export function createInitiative(payload: any) {
  return json<{ ok: boolean; initiative: { code: string; title: string; reported_progress: number } }>(`${API}/api/admin/initiatives`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}
