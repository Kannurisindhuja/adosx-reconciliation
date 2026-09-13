# Architectural Decisions

### 1. Ingestion Strategy: Raw Storage vs. Eager Validation
- **Decision:** Store raw text fields and normalize references during parsing; avoid strict DB check constraints on foreign keys between systems.
- **Alternative:** Strict foreign keys and database-level data validation constraints.
- **Reasoning:** System B exports deliberately contain orphan references and malformed IDs; strict database constraints would cause row drops during ingestion.

### 2. Multi-Tenancy Enforcement Layer
- **Decision:** Require mandatory `org_id` query filtering at the API service layer.
- **Alternative:** Separate database schemas or row-level tenant authorization in full auth middleware.
- **Reasoning:** The brief explicitly waived authentication while strictly mandating tenant boundary safety; query-layer scoping is concise and leak-proof.

### 3. Comparison Compute: On-Demand Service vs. Database SQL Joins
- **Decision:** Reconcile data in Python domain service using dictionary mappings.
- **Alternative:** Complex SQL full outer joins with regex normalization functions.
- **Reasoning:** In-memory Python reconciliation on 120-row datasets is easily testable via unit tests without spinning up a live test database.