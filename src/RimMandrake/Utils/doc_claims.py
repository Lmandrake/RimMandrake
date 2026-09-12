#!/usr/bin/env python3
"""doc_claims.py - split a doctrine file into atomic, numbered CLAIMS.

The point is that two independent assessments judge the SAME list. If each side
re-reads the prose, they are grading different things and their agreement means
nothing. So extraction is mechanical and deterministic here, and judgement is not.

A claim is one directive or one fact. Headings, code fences and tables are carried
as single units because splitting them destroys their meaning.

Phase 0 of the canon-storage plan (design/CANON_STORAGE_ARCHITECTURE_options.md,
owner-adopted 2026-09-12, queue item CANON_CLAIM_TAGGING_1) adds a tagging layer on
top of the same mechanical split: each claim also carries {entity, attribute, value,
provenance, certainty, valid_time}. This is heuristic, best-effort and additive —
`claims()` and the default CLI output are UNCHANGED so existing callers (the
two-blind-arms audit, CANON_DRAIN_1) keep working; pass --tag to get the Phase 0
shape. Nothing here fabricates a value it can't find: an untagged field is `null`,
never guessed. Phase 1 (CANON_CONSISTENCY_CHECKER_1 - contradiction/gap detection
over this shape) is a separate, later item; this file does not attempt it.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path


def claims(text: str):
    out = []
    buf: list[str] = []
    buf_start = None
    in_fence = False
    heading = ""
    in_table = False

    def flush(kind="prose", end_line=None):
        nonlocal buf_start, in_table
        body = "\n".join(buf).strip()
        start_line = buf_start
        buf.clear()
        buf_start = None
        was_table, in_table = in_table, False
        if not body:
            return
        if kind == "prose" and was_table:
            kind = "table"
        if kind == "prose":
            # one claim per sentence-ish bullet or paragraph line
            for part in re.split(r"(?<=[.!?])\s+(?=[A-Z🔴⛔✅⚠️🔑⭐📌])", body):
                part = part.strip()
                if len(part) > 3:
                    out.append({
                        "heading": heading, "kind": "prose", "text": part,
                        "line_start": start_line, "line_end": end_line,
                    })
        else:
            out.append({
                "heading": heading, "kind": kind, "text": body,
                "line_start": start_line, "line_end": end_line,
            })

    def append(line, lineno):
        nonlocal buf_start
        if not buf:
            buf_start = lineno
        buf.append(line)

    lines = text.split("\n")
    for lineno, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            if in_fence:
                append(line, lineno); flush("code", lineno); in_fence = False
            else:
                flush(end_line=lineno - 1); append(line, lineno); in_fence = True
            continue
        if in_fence:
            append(line, lineno); continue
        if line.startswith("#"):
            flush(end_line=lineno - 1); heading = line.lstrip("#").strip(); continue
        if line.strip().startswith("|"):
            append(line, lineno); in_table = True; continue
        if not line.strip():
            flush(end_line=lineno - 1); continue
        if in_table:
            # A table with no blank line before the next paragraph must not
            # absorb that paragraph into the table's single block — found live
            # 2026-09-12: prose glued straight onto a table lost its sentence
            # split and its own line range.
            flush(end_line=lineno - 1)
        append(line, lineno)
    flush(end_line=len(lines))

    for i, c in enumerate(out, 1):
        c["id"] = i
    return out


# ---------------------------------------------------------------------------
# Phase 0 tagging: {entity, attribute, value, provenance, certainty, valid_time}
#
# Certainty vocabulary is NOT invented here — it is the 3-rung ladder the
# architecture doc names (design/CANON_STORAGE_ARCHITECTURE_options.md, "3.
# Certainty"): BEDROCK (driving invariant, contradicting it is an error),
# RULED (decided, stable, citable — includes an explicit "this is superseded"
# ruling, which is itself a ruling), TENTATIVE (floated, not yet ruled, safe
# to prune). A claim with no textual marker for any tier gets certainty=null
# — "unspecified" is honest; guessing a tier is not.
# ---------------------------------------------------------------------------

_RULED_RE = re.compile(
    r"OWNER'S RULING|owner'?s? ruling|\bRULED\b|\bruled\b|\bCLOSED\b|\bDECIDED\b|"
    r"\bdecided\b|SUPERSEDED|\badopted\b|\(owner,\s*20\d{2}|—\s*owner,\s*20\d{2}"
)
_TENTATIVE_RE = re.compile(
    r"\bDRAFT\b|\bdraft\b|\bproposal\b|PLANNING DOC|not ruled|nothing.{0,40}ruled|"
    r"\bspeculative\b|\bcandidate\b|open question|\bTENTATIVE\b|\bprovisional\b|"
    r"under discussion"
)
_BEDROCK_RE = re.compile(
    r"\bbedrock\b|\binvariant\b|never changes|\bpermanently\b"
)

_DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")

_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_CODE_RE = re.compile(r"`([^`]+?)`")
_TITLECASE_RE = re.compile(r"\b([A-Z][a-zA-Z'’]*(?:\s+[A-Z][a-zA-Z'’]*){0,3})\b")
_STOP_ENTITY = {
    "The", "This", "That", "These", "Those", "Where", "When", "Owner", "Note",
    "It", "We", "He", "She", "They", "A", "An", "And", "But", "So", "If",
    "Because", "Per", "See", "Read", "No", "Not", "Never", "Always", "Status",
    "Nothing", "Everything", "One", "Only", "Every", "Each", "Do", "Does",
    "Except", "However", "Also", "For", "In", "On", "At", "As", "By", "With",
    "From", "To", "Of", "Its", "Their", "Until", "After", "Before", "Since",
}
_COPULA_RE = re.compile(
    r"\b(is|are|was|were|has|have|had|must|cannot|will|does not|do not|"
    r"contains|means|becomes|remains)\b", re.IGNORECASE
)


def _guess_entity(text: str, heading: str):
    """Best-effort subject tag: bold span > code span > Title-Case run > heading."""
    m = _BOLD_RE.search(text)
    if m and len(m.group(1)) < 80:
        return m.group(1).strip()
    m = _CODE_RE.search(text)
    if m and len(m.group(1)) < 80:
        return m.group(1).strip()
    for m in _TITLECASE_RE.finditer(text):
        cand = m.group(1)
        if cand.split()[0] not in _STOP_ENTITY:
            return cand
    return heading or None


def _guess_attribute_value(text: str):
    """Split on the first copula/verb: (predicate-ish attribute, rest-as-value).

    Prose that doesn't fit subject-verb shape (most of it, honestly — this is a
    storytelling corpus, not a fact table) gets attribute=None and value=the
    full claim text. That is the correct degrade, not a bug: family-A prose
    doesn't decompose into clean triples, and forcing it to would fabricate
    structure that isn't there.
    """
    m = _COPULA_RE.search(text)
    if not m:
        return None, text
    attribute = text[:m.end()].strip(" *_`-:—")
    value = text[m.end():].strip(" *_`-:—.")
    if not attribute or not value:
        return None, text
    words = attribute.split()
    if len(words) > 8:
        attribute = " ".join(words[-8:])
    return attribute, value


def _guess_certainty(text: str, heading: str):
    hay = f"{heading}\n{text}"
    if _BEDROCK_RE.search(hay):
        return "BEDROCK"
    if _RULED_RE.search(hay):
        return "RULED"
    if _TENTATIVE_RE.search(hay):
        return "TENTATIVE"
    return None


def _guess_valid_time(text: str, heading: str):
    m = _DATE_RE.search(text) or _DATE_RE.search(heading)
    return m.group(1) if m else None


def tag_claim(c: dict, doc_path: str) -> dict:
    text, heading = c["text"], c.get("heading", "")
    if c["kind"] == "prose":
        entity = _guess_entity(text, heading)
        attribute, value = _guess_attribute_value(text)
    else:
        # A table or code block is kept as one unit because splitting it
        # destroys its meaning (see module docstring) — so it has no single
        # subject/predicate to extract without fabricating one. The whole
        # block IS the value; entity/attribute stay null rather than guess.
        entity, attribute, value = None, None, text
    return {
        "id": c["id"],
        "entity": entity,
        "attribute": attribute,
        "value": value,
        "provenance": {
            "doc": doc_path,
            "heading": heading,
            "line_start": c.get("line_start"),
            "line_end": c.get("line_end"),
        },
        "certainty": _guess_certainty(text, heading),
        "valid_time": _guess_valid_time(text, heading),
        "kind": c["kind"],
        "text": text,
    }


def tagged_claims(text: str, doc_path: str):
    return [tag_claim(c, doc_path) for c in claims(text)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--out")
    ap.add_argument(
        "--tag", action="store_true",
        help="emit Phase 0 tagged claims (entity/attribute/value/provenance/"
             "certainty/valid_time) instead of raw claim spans",
    )
    a = ap.parse_args()
    src = Path(a.path)
    text = src.read_text(encoding="utf-8")
    cs = tagged_claims(text, str(src)) if a.tag else claims(text)
    payload = {"file": str(src), "claimCount": len(cs), "claims": cs}
    if a.out:
        Path(a.out).write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{src}: {len(cs)} claims" + (" (tagged)" if a.tag else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
