export type LayerMetric = {
  normalized: number;
  score_5: number;
  label: string;
  color: string;
};

export type DimensionMetric = {
  code: string;
  name: string;
  coverage: number;
  maturity: number;
  maturity_label: string;
  weight: number;
  target: number;
  initiatives: string[];
};

export type ObjectiveMetric = {
  code: string;
  legacy_code?: string | null;
  name: string;
  compliance: number;
  score_5: number;
  weight: number;
};

export type ExecutiveSummary = {
  igtd: number;
  igmd: LayerMetric;
  ioc: LayerMetric;
  iko: LayerMetric;
  layer_weights: { igmd: number; ioc: number; iko: number };
  dimensions: DimensionMetric[];
  objectives: ObjectiveMetric[];
  reference_maturity: Record<string, number>;
  heatmap: Record<string, Record<string, number>>;
  portfolio_count: number;
  activity_count: number;
  evidence_count: number;
  data_notes: string[];
};

export type Leader = {
  name: string;
  email?: string | null;
  role: string;
  source: string;
};

export type Activity = {
  id: number;
  external_id: string;
  parent_external_id?: string | null;
  activity_type: string;
  title: string;
  progress?: number | null;
  state?: string | null;
  priority?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  observation: string;
  evidence_count: number;
  notion_url?: string | null;
  assignees: Leader[];
};

export type Initiative = {
  id: number;
  code: string;
  title: string;
  objective_code?: string | null;
  objective_name?: string | null;
  scope?: string | null;
  description: string;
  reported_progress: number;
  verified_progress?: number | null;
  progress_verified_at?: string | null;
  progress_verified_by?: string | null;
  progress_verification_note: string;
  analytical_progress: number;
  status: string;
  notion_url?: string | null;
  leaders: Leader[];
  contributions: Record<string, number>;
  activities: Activity[];
};

export type WhatIf = {
  initiative_code: string;
  original_progress_percent: number;
  simulated_progress_percent: number;
  original_igmd: number;
  simulated_igmd: number;
  original_igtd: number;
  simulated_igtd: number;
  delta_igtd: number;
  dimension_deltas: Record<string, number>;
};

export type QualityIssue = {
  severity: string;
  initiative: string;
  activity?: string | null;
  type: string;
  message: string;
};

export type AuthUser = {
  id: number;
  email: string;
  name: string;
  role: 'admin' | 'responsible';
  is_active: boolean;
  initiative_codes: string[];
};

export type EvidenceUpload = {
  id: number;
  activity_id: number;
  original_name: string;
  content_type: string;
  size_bytes: number;
  description: string;
  uploaded_at: string;
  uploaded_by?: string | null;
  download_url: string;
};

export type ManagedInitiative = Initiative & {
  uploads?: EvidenceUpload[];
};

export type AdminUser = AuthUser & {
  created_at: string;
};

export type InitiativeTemplate = {
  source: string;
  notion_template_fields: string[];
  objectives: Array<{ code: string; legacy_code?: string | null; name: string }>;
  dimensions: Array<{ code: string; name: string }>;
  state_options: string[];
  priority_options: string[];
  contribution_levels: number[];
};


export type ScheduleForecast = {
  model: string;
  generated_on: string;
  target_date: string;
  scope: string;
  assumption: string;
  current: { igmd: number; igtd: number; dimensions: Record<string, number> };
  projected: { igmd: number; igtd: number; dimensions: Record<string, number> };
  delta: { igmd: number; igtd: number; dimensions: Record<string, number> };
  schedule_coverage: { scheduled_activities: number; total_activities: number; ratio: number };
  initiatives: Array<{ code: string; current_progress: number; projected_progress: number; scheduled_activities: number; total_activities: number }>;
  limitations: string[];
};

export type ApiCatalogEntry = {
  method: string;
  path: string;
  summary: string;
  tags: string[];
  authentication: 'public' | 'session-cookie';
  frontend_function?: string | null;
  database_entities: string[];
  operation_id?: string | null;
};

export type ApiCatalog = {
  name: string;
  api_version: string;
  contract_version: string;
  openapi: string;
  swagger_ui: string;
  redoc: string;
  swaggerhub_catalog: string;
  endpoint_count: number;
  endpoints: ApiCatalogEntry[];
};
