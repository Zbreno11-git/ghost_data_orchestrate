"""Does the request text authorize deletion? Deterministic half of C4.4 (the LLM half arrives in S4).

An explicit deletion instruction aimed at the account or the person's data wins, even when export, correction or
marketing words share the request ("export my data and then delete my account" is a deletion, A20). It does not
count when it is negated ("don't delete", "without removing") or narrowed to marketing lists. With no
instruction, a request for access, a copy, a correction or a marketing opt-out is NOT_APPLICABLE. Anything else is
`unknown`: never a guessed status.
"""
from __future__ import annotations

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
