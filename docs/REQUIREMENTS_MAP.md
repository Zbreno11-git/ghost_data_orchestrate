# Requirements → checkpoints

FR/NFR IDs come from `docs/handoff/GHOST_DATA_VISION_REQUIREMENTS.md` §6 and §10. A requirement counts as met
only when its proving checkpoint is ✅ in `docs/SESSIONS.md`. The proving command is in `docs/plans/MASTER_PLAN.md`.

| ID | Requirement (short) | Proving checkpoint(s) |
|---|---|---|
| FR-01 | Deletion authorization incl. languages/mixed | C4.4 (+ custom NA cases) |
| FR-02 | Current + historical identifiers, no decoy merge | C3.1 |
| FR-03 | Discover copies across systems/formats | C2.1–C2.6 |
| FR-04 | Admissible state at audit_at | C3.2 |
| FR-05 | Claims vs observed state | C2.3, C3.4 |
| FR-06 | Replicas preserved | C2.2, C3.4 |
| FR-07 | Active data flows | C3.4, C3.5 |
| FR-08 | Restore risks with retention | C3.4, C3.5 |
| FR-09 | Apply deletion_rules.csv | C3.4 |
| FR-10 | Tombstone stable ref vs prohibited ids | C3.4 |
| FR-11 | Wrapper vs business fields | C2.3 |
| FR-12 | Anonymous resources via lineage | C3.1, C3.3 |
| FR-13 | Complete finding/remediation/verification sets | C3.5 |
| FR-14 | Eligible evidence citations | C1.3, C3.5 |
| FR-15 | Exact schema + order | C1.1–C1.3 |
| FR-16 | Bounded model/tool loop | C4.3 |
| FR-17 | fresh/live/resume/replay | C4.5, C5.5 |
| FR-18 | Public + custom evaluation | C1.4, C5.3 |
| FR-19 | Usage + cumulative budget | C4.1, C5.4 |
| FR-20 | Reproducible artifacts + transcripts | C0.2, C5.5, C7.3 |
| NFR-01 | Traceability | C2.6 |
| NFR-02 | Deterministic compilation | C1.2, C4.5 |
| NFR-03 | Honest uncertainty | C3.5 (unresolved list), A10 |
| NFR-04 | Budget discipline | C4.1 |
| NFR-05 | Interrupted-run recovery | C4.5 |
| NFR-06 | Portable local execution | C5.5 |
| NFR-07 | Input isolation | C3.2, C4.2 |
| NFR-08 | Reusable internals | package layout (S1–S4) |
| NFR-09 | Deadline awareness | timeline in SESSIONS |
| NFR-10 | Maintainable delivery | C5.3, C5.4 |
