#!/bin/sh
set -eu

ADMIN_SEED_NAME="${ADMIN_SEED_NAME:-초기 관리자}"
ADMIN_SEED_EMAIL="${ADMIN_SEED_EMAIL:-}"
ADMIN_SEED_PASSWORD="${ADMIN_SEED_PASSWORD:-}"
ADMIN_SEED_DEPARTMENT="${ADMIN_SEED_DEPARTMENT:-인사}"
ADMIN_SEED_RANK="${ADMIN_SEED_RANK:-부장}"

if [ -z "$ADMIN_SEED_EMAIL" ] || [ -z "$ADMIN_SEED_PASSWORD" ]; then
  echo "Skipping admin seed because ADMIN_SEED_EMAIL or ADMIN_SEED_PASSWORD is not set."
  exit 0
fi

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set=admin_name="$ADMIN_SEED_NAME" \
  --set=admin_email="$ADMIN_SEED_EMAIL" \
  --set=admin_password="$ADMIN_SEED_PASSWORD" \
  --set=admin_department="$ADMIN_SEED_DEPARTMENT" \
  --set=admin_rank="$ADMIN_SEED_RANK" <<'SQL'
INSERT INTO users (
  name,
  email,
  password_hash,
  department,
  rank,
  hire_date,
  annual_leave_total,
  annual_leave_used,
  employment_status,
  is_active
)
VALUES (
  :'admin_name',
  :'admin_email',
  crypt(:'admin_password', gen_salt('bf')),
  :'admin_department',
  :'admin_rank',
  CURRENT_DATE,
  15,
  0,
  'active',
  TRUE
)
ON CONFLICT (email) DO NOTHING;
SQL
