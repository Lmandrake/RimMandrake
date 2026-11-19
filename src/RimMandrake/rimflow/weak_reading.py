"""weak_reading.py - how a WEAK verdict is read (acted_weak: the narrow rule; a WEAK that names no strong proof reads
as PASS); moved from relentless_wall.py.

Moved verbatim from rimflow/relentless_wall.py (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES):
only the functions live code reaches (design/RimMandrake/retired_eras_index_2026-11-18.md).
"""
from __future__ import annotations

import re


def narrow_word(word, reasons):
    """The verdict under the narrower WEAK: a gap counts only when it is a hunk of this commit's own diff. Shadow only:
    nothing acts on it. A WEAK with no tag is UNTAGGED, never guessed."""
    if word != "WEAK":
        return word
    head = (reasons or "").lstrip().upper()
    return "WEAK" if head.startswith("GAP:DIFF") else "PASS" if head.startswith("GAP:OTHER") else "UNTAGGED"


def acted_weak(word, reasons):
    """The narrower WEAK is the live rule (owner by card 2026-11-03, "Narrow it now": 172 of 207 shadowed WEAKs were
    PASS under it). A WEAK holds only on GAP:DIFF, a hunk of this commit's own change put back with the proof still
    green; GAP:OTHER (a mutant the checker wrote elsewhere) is a PASS; an untagged WEAK stays WEAK, never guessed."""
    n = narrow_word(word, reasons)
    n = "WEAK" if n == "UNTAGGED" else n
    return n if n != "WEAK" or names_strong(reasons) else "PASS"


_STRONG = re.compile(r"(?i)\bSTRONG:\s*\S.{8,}")
_LETS = re.compile(r"(?i)\bLETS THROUGH:\s*\S.{8,}")


def names_strong(reasons):
    """JUDGE_WEAK_RETHINK_NAME_THE_STRONG_PROOF (owner 2026-11-05): a WEAK holds only when it names the strong proof and
    the product defect the current proof lets through. Measured before the change: 269 returns in
    7 days, 2 of a 15-sample fixed a product defect; the rest rewrote a test for a check the Judge had already run."""
    return bool(_STRONG.search(reasons or "") and _LETS.search(reasons or ""))
