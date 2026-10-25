# Fixture allowlist

Files in `code/` whose bytes equal a file of the supplied challenge dataset. The package check (`code/release/checks.py`)
rejects every such file **except** these exact paths with these exact sha256 values (`FIXTURE_ALLOWLIST.json` is the
machine-readable copy; `code/tests/test_release.py` derives the set of copies from disk and requires it to equal this list).

| path | sha256 | equals | why it is here |
|---|---|---|---|
| `code/evaluation/custom_cases/clean_primary_dirty_replica/dataset/deletion_rules.csv` | `e12d47ca4cbecc4a…` | `dataset/deletion_rules.csv` | the custom case applies the official deletion policy unchanged; the scenario is independently authored, the policy content is reused, not invented |
| `code/evaluation/custom_cases/historical_email_replica/dataset/deletion_rules.csv` | `e12d47ca4cbecc4a…` | `dataset/deletion_rules.csv` | the custom case applies the official deletion policy unchanged; the scenario is independently authored, the policy content is reused, not invented |
| `code/evaluation/custom_cases/post_cutoff_evidence_ignored/dataset/deletion_rules.csv` | `e12d47ca4cbecc4a…` | `dataset/deletion_rules.csv` | the custom case applies the official deletion policy unchanged; the scenario is independently authored, the policy content is reused, not invented |
| `code/evaluation/custom_cases/success_claim_contradicted/dataset/deletion_rules.csv` | `e12d47ca4cbecc4a…` | `dataset/deletion_rules.csv` | the custom case applies the official deletion policy unchanged; the scenario is independently authored, the policy content is reused, not invented |
| `code/evaluation/custom_cases/tombstone_pair/dataset/deletion_rules.csv` | `e12d47ca4cbecc4a…` | `dataset/deletion_rules.csv` | the custom case applies the official deletion policy unchanged; the scenario is independently authored, the policy content is reused, not invented |

No broad exception exists: a different dataset file at one of these paths, or this file at any other path, is rejected.
