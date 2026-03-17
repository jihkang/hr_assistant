# Schema Proposal

## Principles
- **PostgreSQL-first**: rely on native enums and generated columns; avoid application-level denormalization.
- **Derived roles**: calculate `is_admin`/`role` from department + rank whenever possible; store only if needed for performance/documentation.
- **RAG support**: keep metadata for policy documents/knowledge sources to enforce LangGraph/LangSmith traceability.
- **Auditability**: track promotions/demotions in dedicated history tables rather than complicating the `users` record.

## Enums
```sql
CREATE TYPE department_enum AS ENUM ('인사','개발','마케팅','재무','영업','운영');
CREATE TYPE rank_enum AS ENUM ('사장','부사장','부서장','부장','과장','대리','사원');
```

## Users & Auth
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  department department_enum NOT NULL,
  rank rank_enum NOT NULL,
  hire_date DATE NOT NULL,
  annual_leave_total INTEGER NOT NULL CHECK (annual_leave_total >= 0),
  annual_leave_used INTEGER NOT NULL DEFAULT 0 CHECK (annual_leave_used >= 0),
  annual_leave_remaining INTEGER GENERATED ALWAYS AS (annual_leave_total - annual_leave_used) STORED,
  employment_status TEXT DEFAULT 'active',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  last_login_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT annual_leave_consistency CHECK (annual_leave_remaining >= 0)
);

CREATE INDEX idx_users_department ON users(department);
CREATE INDEX idx_users_rank ON users(rank);
CREATE INDEX idx_users_email ON users(email);
```

### Role derivation
- `is_admin` is derived: `(department = '인사' AND rank IN ('과장','부장','부서장','부사장','사장')) OR (department <> '인사' AND rank IN ('부장','부서장','부사장','사장'))`.
- If caching is necessary, add a generated column referencing the same expression; otherwise compute inside FastAPI/LangGraph workflow.

## Promotion/Demotion history
```sql
CREATE TABLE user_rank_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  previous_rank rank_enum NOT NULL,
  new_rank rank_enum NOT NULL,
  change_type TEXT CHECK (change_type IN ('promotion','demotion','correction')),
  reason TEXT,
  changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_user_rank_history_user ON user_rank_history(user_id);
```

## Assets / Rentals
```sql
CREATE TABLE assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  serial_number TEXT UNIQUE,
  status TEXT NOT NULL DEFAULT 'available',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE asset_rentals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE RESTRICT,
  requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  approved_at TIMESTAMPTZ,
  returned_at TIMESTAMPTZ,
  status TEXT NOT NULL CHECK (status IN ('requested','approved','denied','returned')),
  note TEXT
);

CREATE INDEX idx_asset_rentals_asset ON asset_rentals(asset_id);
CREATE INDEX idx_asset_rentals_user ON asset_rentals(user_id);
```

## Policy documents (RAG)
```sql
CREATE TABLE policy_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  document_type TEXT NOT NULL,
  source TEXT,
  department department_enum,
  visibility TEXT CHECK (visibility IN ('public','restricted','confidential')) NOT NULL DEFAULT 'public',
  effective_date DATE,
  content TEXT NOT NULL,
  vector VECTOR DEFAULT '{}'::vector, -- for pgvector
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_policy_documents_visibility ON policy_documents(visibility);
CREATE INDEX idx_policy_documents_department ON policy_documents(department);
CREATE INDEX idx_policy_documents_effective ON policy_documents(effective_date);
```

## Chat logs / LangSmith tracing
```sql
CREATE TABLE chat_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  prompt TEXT NOT NULL,
  response TEXT NOT NULL,
  citations TEXT[],
  metadata JSONB DEFAULT '{}'::jsonb,
  langsmith_trace_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_chat_logs_user ON chat_logs(user_id);

CREATE TABLE langsmith_traces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trace_id UUID NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Supporting tables
- `departments` lookup table if additional metadata is needed (owner, manager).
- `ranks` lookup table for ordering and promotion rules.
- `rag_sources` to enumerate supported RAG collections if LangGraph connectors require registration.

## Notes
- LangGraph workflows read/write via `chat_logs`/`langsmith_traces`; store trace IDs returned by LangSmith for reconciliation.
- Always validate `annual_leave_remaining` server-side before persisting updates.
- Create Postgres partial indexes on `assets(status)` and `asset_rentals(status)` if filtering by state is frequent.

_Created schema draft per current specs._
