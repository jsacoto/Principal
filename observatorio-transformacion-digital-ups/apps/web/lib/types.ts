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
