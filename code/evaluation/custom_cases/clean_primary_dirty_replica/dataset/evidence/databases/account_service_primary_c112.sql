-- Northstar account_service SQL snapshot export
-- Captured at: 2026-09-05T06:00:00Z
-- Database topology: primary_only
-- Tables: customer_profiles_primary
CREATE TABLE customer_profiles_primary (
  resource_id TEXT PRIMARY KEY,
  user_id TEXT,
  full_name TEXT,
  email TEXT,
  phone TEXT,
  account_status TEXT,
  updated_at TEXT
);
INSERT INTO customer_profiles_primary VALUES ('account_9112','user_9112','Ravinder Castellano','r.castellano@tidewharf.example','+34-555-019-112','ACTIVE','2026-08-25T01:00:00Z');
