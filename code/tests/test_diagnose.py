"""S6 C6.1: the evaluator's "no supporting fact" verdict searches decoded content, never raw bytes.

The four PDFs are FlateDecode-compressed, so every identifier they contain is invisible to a byte search
(measured 2026-10-25: 10 of 10). A parser miss must never be reported as a dataset gap.
"""
import pytest

from evaluation.diagnose import World


@pytest.fixture(scope="module")
def world(dataset_dir):
    return World(dataset_dir)


def test_an_id_inside_a_compressed_pdf_is_found(world, dataset_dir):
    # support_001 is the only resource id that no source other than a PDF carries (measured 2026-10-25), so only
    # PDF decoding can find it; the raw bytes of the PDFs do not contain it.
    rid = "support_001"
    raw = b"".join(p.read_bytes() for p in (dataset_dir / "evidence" / "documents").glob("*.pdf"))
    assert rid.encode() not in raw
    assert world.in_decoded(rid)


def test_an_id_in_no_source_is_not_found(world):
    assert not world.in_decoded("audit_record_6645")
    assert not world.in_decoded("support_00")          # a prefix of a real id is not a whole-word hit
