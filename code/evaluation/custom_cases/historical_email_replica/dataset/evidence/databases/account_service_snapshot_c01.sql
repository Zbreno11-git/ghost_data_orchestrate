-- Northstar account_service SQL snapshot export
-- Captured at: 2026-08-12T09:30:00Z
-- Database topology: failover_replica
-- Tables: customer_profiles_primary, customer_profiles_failover_replica
CREATE TABLE customer_profiles_primary (
  resource_id TEXT PRIMARY KEY,
  user_id TEXT,
  full_name TEXT,
  email TEXT,
  phone TEXT,
  account_status TEXT,
  updated_at TEXT
);
CREATE TABLE customer_profiles_failover_replica (
  resource_id TEXT PRIMARY KEY,
  user_id TEXT,
  full_name TEXT,
  email TEXT,
  phone TEXT,
  account_status TEXT,
  updated_at TEXT
);
INSERT INTO customer_profiles_primary VALUES ('account_9002','user_9002','Marisol Quintana','m.quintana@orchidmail.example','+1-555-0142','ACTIVE','2026-07-30T14:05:00Z');
INSERT INTO customer_profiles_failover_replica VALUES ('account_9001','user_9001','Marisol Quintanar','m.quintanar@orchidmail.example','+1-555-0187','ACTIVE','2026-04-02T11:20:00Z');
INSERT INTO customer_profiles_failover_replica VALUES ('account_9002','user_9002','Marisol Quintana','m.quintana@orchidmail.example','+1-555-0142','ACTIVE','2026-07-30T14:05:00Z');
