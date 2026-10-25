-- Northstar account_service SQL snapshot export
-- Captured at: 2026-08-28T06:00:00Z
-- Database topology: reporting_replica
-- Tables: customer_profiles_reporting_replica
CREATE TABLE customer_profiles_reporting_replica (
  resource_id TEXT PRIMARY KEY,
  user_id TEXT,
  full_name TEXT,
  email TEXT,
  phone TEXT,
  account_status TEXT,
  updated_at TEXT
);
INSERT INTO customer_profiles_reporting_replica VALUES ('account_9111','user_9111','Ravindra Castellanos','ravi.castellanos@tidewharf.example','+34-555-019-111','ACTIVE','2026-08-11T16:40:00Z');
INSERT INTO customer_profiles_reporting_replica VALUES ('account_9112','user_9112','Ravinder Castellano','r.castellano@tidewharf.example','+34-555-019-112','ACTIVE','2026-08-25T01:00:00Z');
