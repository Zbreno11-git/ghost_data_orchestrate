"""C4.4 live check: rule + LLM intent on the 32 samples and the hand-written fixtures (ledgered via the gateway).

Run: .venv/bin/python scripts/intent_check.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "code" / "tests"))

from ghostaudit.config import load_config  # noqa: E402
from ghostaudit.ingest.manifest import read_csv  # noqa: E402
from ghostaudit.intent import classify_all  # noqa: E402
from ghostaudit.llm.gateway import Gateway  # noqa: E402
from test_intent import MIXED_DELETION, NOT_APPLICABLE  # noqa: E402

cfg = load_config()
rows = read_csv(ROOT / "dataset" / "sample_deletion_requests.csv")
rows += [{"case_id": f"fx_mixed_{i}", "request_text": t} for i, t in enumerate(MIXED_DELETION)]
rows += [{"case_id": f"fx_na_{i}", "request_text": t} for i, t in enumerate(NOT_APPLICABLE)]
out = classify_all(rows, Gateway("c4.4-intent", cfg), cfg)
expect = {r["case_id"]: (not r["case_id"].startswith("fx_na_")) for r in rows}
wrong = [(c, i) for c, i in out.items() if i.authorizes_deletion is not expect[c]]
samples = sum(out[r["case_id"]].authorizes_deletion is True for r in rows if r["case_id"].startswith("case_"))
print(f"samples deletion {samples}/32; fixtures right {len(rows) - 32 - len([w for w in wrong if w[0].startswith('fx')])}"
      f"/{len(rows) - 32}; low-confidence {sum(i.confidence == 'low' for i in out.values())}")
for c, i in wrong:
    print("WRONG", c, i)
for c, i in out.items():
    if i.confidence == "low":
        print("LOW", c, i.reason[:160])
