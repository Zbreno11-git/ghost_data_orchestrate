"""Intent (deterministic half of C4.4, A20 safeguard 5): an explicit deletion instruction wins over export,
correction or marketing words; without one, those requests are NOT_APPLICABLE; anything else is unknown."""
import pytest

from conftest import DATASET, read_csv
from ghostaudit.intent import classify

# Phrasings written for this test, not taken from the dataset, so they check generalization rather than recall.
MIXED_DELETION = [
    "Export my data and then delete my account.",
    "Send me a copy of my invoices first, then close my account and erase my personal data.",
    "Please correct my address on the last order, and after that remove my account entirely.",
    "Exportez mes données puis supprimez définitivement mon compte.",
    "Bitte exportieren Sie meine Daten und löschen Sie danach mein Konto.",
    "Envíenme una copia de mis datos y después eliminen mi cuenta.",
    "Exportem os meus dados e depois excluam a minha conta.",
]
NOT_APPLICABLE = [
    "Please send me a copy of everything you hold about me. Keep the account open.",
    "Please correct the spelling of my surname; don't delete anything.",
    "Remove me from the marketing newsletter only, I still use my account.",
    "Veuillez corriger mon adresse e-mail, ne supprimez rien.",
    "Bitte senden Sie mir eine Kopie meiner Daten. Mein Konto soll bestehen bleiben.",
    "Quiero darme de baja del boletín, pero no borren mi cuenta.",
    "Por favor, corrijam o meu nome; não excluam nada.",
]


@pytest.mark.parametrize("text", MIXED_DELETION)
def test_an_explicit_deletion_instruction_wins_over_other_request_words(text):
    i = classify(text)
    assert i.authorizes_deletion is True, i.reason


@pytest.mark.parametrize("text", NOT_APPLICABLE)
def test_non_deletion_requests_are_not_applicable(text):
    i = classify(text)
    assert i.authorizes_deletion is False, i.reason


def test_text_without_any_signal_is_unknown_not_a_guess():
    assert classify("Hello, I have a question about my order.").authorizes_deletion is None


def test_every_sample_request_authorizes_deletion():
    rows = read_csv(DATASET / "sample_deletion_requests.csv")
    assert len(rows) == 32
    assert [classify(r["request_text"]).authorizes_deletion for r in rows].count(True) == 32
