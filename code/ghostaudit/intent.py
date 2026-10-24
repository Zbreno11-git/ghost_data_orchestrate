"""Does the request text authorize deletion? Deterministic half of C4.4 (the LLM half arrives in S4).

An explicit deletion instruction aimed at the account or the person's data wins, even when export, correction or
marketing words share the request ("export my data and then delete my account" is a deletion, A20). It does not
count when it is negated ("don't delete", "without removing") or narrowed to marketing lists. With no
instruction, a request for access, a copy, a correction or a marketing opt-out is NOT_APPLICABLE. Anything else is
`unknown`: never a guessed status.
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass

# deletion verbs/nouns, multilingual (EN, FR, DE, ES, PT, IT, NL, plus a few scripts seen in requests)
DELETE = re.compile(
    r"\b(delet\w*|remov\w*|eras\w*|purg\w*|wip\w*|clos(e|ing)\s+(my|the|this)\s+account|close\s+it\b|"
    r"forget\s+me|cancel\s+my\s+account|"
    r"suppr\w*|effac\w*|fermer\s+(mon|le)\s+compte|"
    r"l(o|oe|ö)sch\w*|entfern\w*|kundigen|kündig\w*|"
    r"elimin\w*|borr\w*|suprim\w*|"
    r"exclu\w*|apag\w*|encerr\w*\s+(a\s+)?(minha\s+)?conta|"
    r"cancell\w*|rimuov\w*|"
    r"verwijder\w*)"
    r"|削除|삭제|删除|удал\w*|حذف",
    re.I)
NEGATION = re.compile(r"\b(don'?t|do\s+not|never|without|not|no|ne|n'|nicht|kein\w*|sin|sem|senza|niet|não|nao|nunca)\b"
                      r"(\W+\w+){0,3}\W*$", re.I)
MARKETING_ONLY = re.compile(r"(from|de|aus|dalla|van)\s+(the\s+|les\s+|den\s+)?(marketing|newsletter|mailing|promot)\w*"
                            r"|marketing\w*\s+(lists?|emails?)\s+only|only\s+(from\s+)?marketing", re.I)
# Asking to confirm a deletion presumes and reaffirms it ("verify that my account was deleted", "confirm the profile
# is gone and that remaining records cannot identify me").
CONFIRM_DELETION = re.compile(
    r"\b(confirm|verify|check|make\s+sure|ensure)\b[^.?!]{0,60}\b(account|profile)\b[^.?!]{0,20}"
    r"\b(is|was|has\s+been|were)\s+(gone|deleted|removed|erased|closed)"
    r"|cannot\s+identify\s+me|can\s+no\s+longer\s+identify\s+me|no\s+longer\s+(be\s+)?(linked|identif)\w*", re.I)
NON_DELETION = re.compile(
    r"\b(cop(y|ie|ia)|kopie|download|export\w*|portab\w*|access|send\s+me|invoice\w*|"
    r"correct\w*|corri[gj]\w*|rectif\w*|misspel\w*|updat\w*|chang\w*|replac\w*|modif\w*|"
    r"unsubscrib\w*|opt.?out|marketing|newsletter|promotional|darme\s+de\s+baja|bolet[ií]n|"
    r"what\s+(personal\s+)?(data|information)\s+you\s+(hold|have|keep)|information\s+request|"
    r"keep\s+(the|my)\s+(account|profile)|leave\s+(the|my)\s+(account|profile)|continue\s+using|still\s+(use|want)|bestehen\s+bleiben|behalten)",
    re.I)


@dataclass(frozen=True)
class Intent:
    authorizes_deletion: bool | None    # None = unknown
    confidence: str                     # high | low
    reason: str


def _norm(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def classify(text: str) -> Intent:
    t = _norm(text)
    instructions = []
    for m in DELETE.finditer(t):
        before = t[max(0, m.start() - 40):m.start()]
        after = t[m.end():m.end() + 60]
        if NEGATION.search(before):
            continue
        if MARKETING_ONLY.search(after) or MARKETING_ONLY.search(before + m.group(0) + after):
            continue
        instructions.append(m.group(0))
    other = sorted({m.group(0).lower() for m in NON_DELETION.finditer(t)})
    confirm = CONFIRM_DELETION.search(t)
    if confirm and not NEGATION.search(t[max(0, confirm.start() - 40):confirm.start()]):
        instructions.append(confirm.group(0))
    if instructions:
        why = f"deletion instruction {instructions[0]!r}" + (f" (also {', '.join(other[:3])})" if other else "")
        return Intent(True, "high", why)
    if other:
        return Intent(False, "high" if len(other) > 1 else "low", f"non-deletion request: {', '.join(other[:4])}")
    return Intent(None, "low", "no deletion instruction and no recognized non-deletion request")


# --- LLM half (C4.4): batched classification, cross-checked against the rule above --------------------------

LLM_PROMPT = """You classify privacy requests. For each request decide whether the text authorizes deleting the
person's account or personal data. Mixed requests that also ask for an export, a copy or a correction still
authorize deletion if they explicitly ask for deletion. Requests only for access, a copy, an export, a correction
or a marketing opt-out do not. A request to confirm or verify that a deletion happened authorizes it. Texts may be
in any language. Answer for every case_id given, using only the text."""

LLM_SCHEMA = {"type": "object", "properties": {"results": {"type": "array", "items": {
    "type": "object", "properties": {"case_id": {"type": "string"}, "authorizes_deletion": {"type": "boolean"},
                                     "language": {"type": "string"}, "reason": {"type": "string"}},
    "required": ["case_id", "authorizes_deletion", "language", "reason"]}}}, "required": ["results"]}


def _ask(rows: list[dict], gateway, model: str, cfg: dict, purpose: str) -> dict[str, dict]:
    from google.genai import types
    i = cfg["intent"]
    items = [{"case_id": r["case_id"], "text": r["request_text"]} for r in rows]
    resp, _ = gateway.generate(
        model=model, purpose=purpose, est_input_tokens=200 + 80 * len(rows),
        contents=LLM_PROMPT + "\n\nREQUESTS (JSON):\n" + json.dumps(items, ensure_ascii=False),
        config=types.GenerateContentConfig(
            response_mime_type="application/json", response_json_schema=LLM_SCHEMA, temperature=0,
            max_output_tokens=i["max_output_tokens_per_case"] * len(rows) + 200,
            thinking_config=types.ThinkingConfig(thinking_level=i["thinking_level"][model])))
    got = {x["case_id"]: x for x in json.loads(resp.text)["results"]}
    return {r["case_id"]: got[r["case_id"]] for r in rows if r["case_id"] in got}


def classify_all(rows: list[dict], gateway, cfg: dict) -> dict[str, Intent]:
    """Rule + LLM for every request. Agreement → high; disagreement → one recheck on the check model; a remaining
    disagreement keeps the recheck's reading at low confidence (reported weak). A failed call keeps the rule."""
    i = cfg["intent"]
    rule = {r["case_id"]: classify(r["request_text"]) for r in rows}
    ordered = sorted(rows, key=lambda r: r["case_id"])
    llm: dict[str, dict] = {}
    for k in range(0, len(ordered), i["batch_size"]):
        batch = ordered[k:k + i["batch_size"]]
        try:
            llm.update(_ask(batch, gateway, i["model"], cfg, "intent-batch"))
        except Exception as exc:  # recorded per case below; never a status by itself
            for r in batch:
                llm.setdefault(r["case_id"], {"error": f"{type(exc).__name__}"})
    out = {}
    for r in ordered:
        cid, rl, l = r["case_id"], rule[r["case_id"]], llm.get(r["case_id"], {})
        if "authorizes_deletion" not in l:
            out[cid] = Intent(rl.authorizes_deletion, "low", f"rule only (LLM {l.get('error', 'missing')}): {rl.reason}")
            continue
        if rl.authorizes_deletion is l["authorizes_deletion"]:
            out[cid] = Intent(rl.authorizes_deletion, "high", f"rule and LLM agree ({l.get('language', '?')})")
            continue
        try:
            chk = _ask([r], gateway, i["check_model"], cfg, "intent-recheck").get(cid, {})
        except Exception as exc:
            chk = {"error": type(exc).__name__}
        if chk.get("authorizes_deletion") is l["authorizes_deletion"]:
            out[cid] = Intent(l["authorizes_deletion"], "low",
                              f"LLM and recheck overrule the rule ({rl.reason}); LLM: {l.get('reason', '')[:80]}")
        elif "authorizes_deletion" in chk and rl.authorizes_deletion is not None:
            out[cid] = Intent(rl.authorizes_deletion, "low", f"recheck sides with the rule; LLM said {l['reason'][:80]}")
        else:
            out[cid] = Intent(None, "low", f"rule {rl.authorizes_deletion}, LLM {l['authorizes_deletion']}, "
                                           f"recheck {chk.get('authorizes_deletion', chk.get('error'))}")
    return out
