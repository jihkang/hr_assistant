CREATE TYPE department_enum AS ENUM (
  '인사',
  '개발',
  '마케팅',
  '재무',
  '영업',
  '운영'
);

CREATE TYPE rank_enum AS ENUM (
  '사장',
  '부사장',
  '부서장',
  '부장',
  '과장',
  '대리',
  '사원'
);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  email CITEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  department department_enum NOT NULL,
  rank rank_enum NOT NULL,
  hire_date DATE NOT NULL,
  annual_leave_total INTEGER NOT NULL CHECK (annual_leave_total >= 0),
  annual_leave_used INTEGER NOT NULL DEFAULT 0 CHECK (annual_leave_used >= 0),
  annual_leave_remaining INTEGER GENERATED ALWAYS AS (annual_leave_total - annual_leave_used) STORED,
  employment_status TEXT NOT NULL DEFAULT 'active'
    CHECK (employment_status IN ('active', 'leave', 'resigned')),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  last_login_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT annual_leave_remaining_non_negative CHECK (annual_leave_remaining >= 0)
);

CREATE INDEX idx_users_department ON users(department);
CREATE INDEX idx_users_rank ON users(rank);

CREATE TABLE user_rank_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  previous_rank rank_enum NOT NULL,
  new_rank rank_enum NOT NULL,
  change_type TEXT NOT NULL CHECK (change_type IN ('promotion', 'demotion', 'correction')),
  reason TEXT,
  changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_user_rank_history_user_id ON user_rank_history(user_id);
CREATE INDEX idx_user_rank_history_changed_at ON user_rank_history(changed_at DESC);

CREATE TABLE assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  serial_number TEXT UNIQUE,
  status TEXT NOT NULL DEFAULT 'available'
    CHECK (status IN ('available', 'reserved', 'rented', 'maintenance', 'retired')),
  location TEXT,
  owner_department department_enum,
  requires_approval BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_assets_category ON assets(category);
CREATE INDEX idx_assets_owner_department ON assets(owner_department);
CREATE INDEX idx_assets_available_status ON assets(status) WHERE status = 'available';

CREATE TABLE asset_rentals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
  requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  approved_at TIMESTAMPTZ,
  returned_at TIMESTAMPTZ,
  status TEXT NOT NULL CHECK (status IN ('requested', 'approved', 'denied', 'returned')),
  note TEXT
);

CREATE INDEX idx_asset_rentals_asset_id ON asset_rentals(asset_id);
CREATE INDEX idx_asset_rentals_user_id ON asset_rentals(user_id);
CREATE INDEX idx_asset_rentals_status_open ON asset_rentals(status)
WHERE status IN ('requested', 'approved');

CREATE TABLE policy_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  document_type TEXT NOT NULL,
  source TEXT,
  department department_enum,
  visibility TEXT NOT NULL DEFAULT 'public'
    CHECK (visibility IN ('public', 'restricted', 'confidential')),
  effective_date DATE,
  content TEXT NOT NULL,
  embedding VECTOR,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_policy_documents_visibility ON policy_documents(visibility);
CREATE INDEX idx_policy_documents_department ON policy_documents(department);
CREATE INDEX idx_policy_documents_effective_date ON policy_documents(effective_date DESC);

CREATE TABLE chat_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  prompt TEXT NOT NULL,
  response TEXT NOT NULL,
  citations JSONB NOT NULL DEFAULT '[]'::jsonb,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  langsmith_trace_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_chat_logs_user_id ON chat_logs(user_id);
CREATE INDEX idx_chat_logs_created_at ON chat_logs(created_at DESC);

CREATE TABLE langsmith_traces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trace_id TEXT NOT NULL UNIQUE,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE OR REPLACE VIEW user_admin_eligibility AS
SELECT
  u.id,
  u.name,
  u.email,
  u.department,
  u.rank,
  CASE
    WHEN u.department = '인사' AND u.rank IN ('사장', '부사장', '부서장', '부장', '과장') THEN TRUE
    WHEN u.department <> '인사' AND u.rank IN ('사장', '부사장', '부서장', '부장') THEN TRUE
    ELSE FALSE
  END AS is_admin
FROM users AS u;

CREATE TRIGGER trg_users_set_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_assets_set_updated_at
BEFORE UPDATE ON assets
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_policy_documents_set_updated_at
BEFORE UPDATE ON policy_documents
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
