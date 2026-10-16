import type { ExecutiveSummary, Initiative, QualityIssue, WhatIf } from './types';

const API = '/backend';

async function json<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, { cache: 'no-store', ...init });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `HTTP ${response.status}`);
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
