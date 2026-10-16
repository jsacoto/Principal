-- PostgreSQL DDL generated from SQLAlchemy models.
-- UPS Digital Maturity Observatory v1

CREATE TABLE dimensions (
  id SERIAL NOT NULL,
  code VARCHAR(8) NOT NULL,
  name VARCHAR(180) NOT NULL,
  description TEXT NOT NULL,
  weight FLOAT NOT NULL,
  target_maturity FLOAT NOT NULL,
  color VARCHAR(16) NOT NULL,
  PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_dimensions_code ON dimensions (code);

CREATE TABLE index_logs (
  id SERIAL NOT NULL,
  computed_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  igmd FLOAT NOT NULL,
  ioc FLOAT NOT NULL,
  ioc5 FLOAT NOT NULL,
  iko FLOAT NOT NULL,
  iko5 FLOAT NOT NULL,
  igtd FLOAT NOT NULL,
  details JSON NOT NULL,
  source VARCHAR(50) NOT NULL,
  PRIMARY KEY (id)
);
CREATE INDEX ix_index_logs_computed_at ON index_logs (computed_at);

CREATE TABLE objectives (
  id SERIAL NOT NULL,
  code VARCHAR(8) NOT NULL,
  legacy_code VARCHAR(8),
  name VARCHAR(220) NOT NULL,
  description TEXT NOT NULL,
  weight FLOAT NOT NULL,
  PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_objectives_code ON objectives (code);

CREATE TABLE traceability_records (
  id SERIAL NOT NULL,
  from_type VARCHAR(40) NOT NULL,
  from_key VARCHAR(100) NOT NULL,
  to_type VARCHAR(40) NOT NULL,
  to_key VARCHAR(100) NOT NULL,
  relation VARCHAR(80) NOT NULL,
  weight FLOAT,
  source VARCHAR(60) NOT NULL,
  note TEXT NOT NULL,
  PRIMARY KEY (id)
);
CREATE INDEX ix_traceability_records_to_type ON traceability_records (to_type);
CREATE INDEX ix_traceability_records_from_key ON traceability_records (from_key);
CREATE INDEX ix_traceability_records_to_key ON traceability_records (to_key);
CREATE INDEX ix_traceability_records_from_type ON traceability_records (from_type);

CREATE TABLE initiatives (
  id SERIAL NOT NULL,
  code VARCHAR(20) NOT NULL,
  title VARCHAR(300) NOT NULL,
  objective_id INTEGER,
  scope VARCHAR(120),
  description TEXT NOT NULL,
  reported_progress FLOAT NOT NULL,
  verified_progress FLOAT,
  progress_verified_at TIMESTAMP WITHOUT TIME ZONE,
  progress_verified_by VARCHAR(180),
  progress_verification_note TEXT NOT NULL,
  status VARCHAR(60) NOT NULL,
  notion_url TEXT,
  data_origin VARCHAR(40) NOT NULL,
  last_synced_at TIMESTAMP WITHOUT TIME ZONE,
  is_reference_16 BOOLEAN NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY(objective_id) REFERENCES objectives (id)
);
CREATE UNIQUE INDEX ix_initiatives_code ON initiatives (code);

CREATE TABLE key_results (
  id SERIAL NOT NULL,
  objective_id INTEGER NOT NULL,
  code VARCHAR(24) NOT NULL,
  title TEXT NOT NULL,
  direction VARCHAR(40) NOT NULL,
  current_value FLOAT NOT NULL,
  target_value FLOAT NOT NULL,
  baseline_value FLOAT,
  unit VARCHAR(40) NOT NULL,
  weight FLOAT NOT NULL,
  source VARCHAR(50) NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY(objective_id) REFERENCES objectives (id) ON DELETE CASCADE,
  UNIQUE (code)
);
CREATE INDEX ix_key_results_objective_id ON key_results (objective_id);

CREATE TABLE kpis (
  id SERIAL NOT NULL,
  code VARCHAR(24) NOT NULL,
  title TEXT NOT NULL,
  dimension_id INTEGER,
  objective_id INTEGER,
  direction VARCHAR(40) NOT NULL,
  current_value FLOAT NOT NULL,
  target_value FLOAT NOT NULL,
  unit VARCHAR(40) NOT NULL,
  weight FLOAT NOT NULL,
  source VARCHAR(50) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (code),
  FOREIGN KEY(dimension_id) REFERENCES dimensions (id),
  FOREIGN KEY(objective_id) REFERENCES objectives (id)
);
CREATE INDEX ix_kpis_dimension_id ON kpis (dimension_id);
CREATE INDEX ix_kpis_objective_id ON kpis (objective_id);

CREATE TABLE activities (
  id SERIAL NOT NULL,
  initiative_id INTEGER NOT NULL,
  external_id VARCHAR(40) NOT NULL,
  parent_external_id VARCHAR(40),
  activity_type VARCHAR(24) NOT NULL,
  title TEXT NOT NULL,
  progress FLOAT,
  state VARCHAR(60),
  priority VARCHAR(30),
  start_date DATE,
  end_date DATE,
  observation TEXT NOT NULL,
  notion_url TEXT,
  evidence_count INTEGER NOT NULL,
  raw_data JSON NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_activity_external UNIQUE (initiative_id, external_id),
  FOREIGN KEY(initiative_id) REFERENCES initiatives (id) ON DELETE CASCADE
);
CREATE INDEX ix_activities_initiative_id ON activities (initiative_id);

CREATE TABLE initiative_dimensions (
  id SERIAL NOT NULL,
  initiative_id INTEGER NOT NULL,
  dimension_id INTEGER NOT NULL,
  contribution_level INTEGER NOT NULL,
  source VARCHAR(60) NOT NULL,
  validated BOOLEAN NOT NULL,
  note TEXT NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_initiative_dimension UNIQUE (initiative_id, dimension_id),
  FOREIGN KEY(initiative_id) REFERENCES initiatives (id) ON DELETE CASCADE,
  FOREIGN KEY(dimension_id) REFERENCES dimensions (id) ON DELETE CASCADE
);
CREATE INDEX ix_initiative_dimensions_initiative_id ON initiative_dimensions (initiative_id);
CREATE INDEX ix_initiative_dimensions_dimension_id ON initiative_dimensions (dimension_id);

CREATE TABLE initiative_leaders (
  id SERIAL NOT NULL,
  initiative_id INTEGER NOT NULL,
  name VARCHAR(180) NOT NULL,
  email VARCHAR(180),
  notion_user_id VARCHAR(100),
  role VARCHAR(60) NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY(initiative_id) REFERENCES initiatives (id) ON DELETE CASCADE
);
CREATE INDEX ix_initiative_leaders_initiative_id ON initiative_leaders (initiative_id);

CREATE TABLE activity_assignees (
  id SERIAL NOT NULL,
  activity_id INTEGER NOT NULL,
  name VARCHAR(180),
  email VARCHAR(180),
  notion_user_id VARCHAR(100),
  source VARCHAR(40) NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY(activity_id) REFERENCES activities (id) ON DELETE CASCADE
);
CREATE INDEX ix_activity_assignees_activity_id ON activity_assignees (activity_id);

CREATE TABLE evidence (
  id SERIAL NOT NULL,
  activity_id INTEGER NOT NULL,
  label VARCHAR(240) NOT NULL,
  url TEXT,
  kind VARCHAR(40) NOT NULL,
  verified BOOLEAN NOT NULL,
  verified_at TIMESTAMP WITHOUT TIME ZONE,
  PRIMARY KEY (id),
  FOREIGN KEY(activity_id) REFERENCES activities (id) ON DELETE CASCADE
);
CREATE INDEX ix_evidence_activity_id ON evidence (activity_id);
