-- Northstar identity_service SQL snapshot export
-- Captured at: 2026-09-12T10:00:00Z
-- Database topology: reporting_replica
-- Tables: deleted_customer_references_primary, deleted_customer_references_reporting_replica
CREATE TABLE deleted_customer_references_primary (
  resource_id TEXT PRIMARY KEY,
  user_id TEXT,
  record_type TEXT,
  full_name TEXT,
  email TEXT,
  phone TEXT,
  email_hash TEXT,
  account_status TEXT,
  reference_purpose TEXT,
  updated_at TEXT
);
CREATE TABLE deleted_customer_references_reporting_replica (
  resource_id TEXT PRIMARY KEY,
  user_id TEXT,
  record_type TEXT,
  full_name TEXT,
  email TEXT,
  phone TEXT,
  email_hash TEXT,
  account_status TEXT,
  reference_purpose TEXT,
  updated_at TEXT
);
INSERT INTO deleted_customer_references_primary VALUES ('tombstone_9101','user_9101','ACCOUNT_TOMBSTONE',NULL,NULL,NULL,NULL,'DELETED','keep stable user_id for retained invoices and security audit references','2026-09-03T02:00:00Z');
INSERT INTO deleted_customer_references_primary VALUES ('tombstone_9102','user_9102','ACCOUNT_TOMBSTONE',NULL,NULL,NULL,NULL,'DELETED','keep stable user_id for retained invoices and security audit references','2026-09-03T02:10:00Z');
INSERT INTO deleted_customer_references_reporting_replica VALUES ('tombstone_9101','user_9101','ACCOUNT_TOMBSTONE',NULL,NULL,'+47-555-02-110','a624691ca30769f66964c99020de60cd5dc4d85e0eb920ddd536c986714491cb','DELETED','keep stable user_id for retained invoices and security audit references','2026-09-03T02:00:00Z');
INSERT INTO deleted_customer_references_reporting_replica VALUES ('tombstone_9102','user_9102','ACCOUNT_TOMBSTONE','Ottilie Brandvoll','ottilie.brandvoll@harrowlane.example',NULL,NULL,'DELETED','keep stable user_id for retained invoices and security audit references','2026-09-03T02:10:00Z');
