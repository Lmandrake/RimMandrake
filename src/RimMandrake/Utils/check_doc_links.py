#!/usr/bin/env python3
"""check_doc_links.py — a LIVE design doc may not send a reader into a DEAD one.

WHY
===
`design/RimMandrake/save_authoring_pipeline.md` opens with `⛔ DEAD DOCUMENT` and on
2026-08-20 was still linked from live documents and still listed in `design/INDEX.md`.
A reader arriving by link never sees the banner as a warning; they see it as the top
of the page they were sent to, and by then they are already reading it.

That is the whole failure mode this catches: the death of a document is recorded IN
the document, where only someone who already doubted it would look. Nothing has ever
checked the direction of travel.

    python3 src/RimMandrake/Utils/check_doc_links.py           # report; exit 1 on a violation
    python3 src/RimMandrake/Utils/check_doc_links.py --status  # the status of every doc

THE STATUS HEADER
=================
One HTML comment near the top of each design doc, so nothing renders:

    <!-- status: live -->
    <!-- status: superseded-by: <path> ; <date> ; <what changed> -->
    <!-- status: dead ; <date> ; <why> -->
    <!-- status: aspirational -->

An optional extra field says a doc is live but its FIGURES are not — the case four
statuses could not express, and the one that let `worldgen_interactive_def.md` sit at
`live` while every number in it measured a planet that no longer exists:

    <!-- status: live ; numbers-superseded-by: <path> ; <date> ; <why> -->

It does not change link enforcement; `design/INDEX.md` renders it as
"⚠ do not quote its numbers".

⚠️ A doc with NO header is reported as `unmarked`, and unmarked is NOT a pass — it is
the state 119 documents were in when this was written, and the state that let a dead
document keep collecting readers. It does not fail the build yet, because failing on
119 files teaches everyone to pass `--quiet`. It fails once `--require-status` is on.

WHAT COUNTS AS A VIOLATION
==========================
A link from a `live` (or unmarked, or `aspirational`) doc INTO a `dead` doc.

⛔ Deliberately NOT violations, and each for a reason:
  * a link out of a dead doc — it is dead; where it points no longer matters.
  * a link into a `superseded-by` doc — supersession is a forwarding address, not a
    grave. The successor is named in the header the reader lands on.
  * a link on a line marked historical (`~~`, `superseded`, `dead`, `⛔`) — that is
    citing the dead doc AS dead, which is exactly right and must stay legal. Kill this
    exemption and every correct supersession note becomes an error.
    ⚠️ Scoped to the whole LINE, including a whole table row — deliberately the
    OPPOSITE of `check_canon.py`, which scopes its markers to the cell. See the
    comment at the exemption itself for why the two must differ.

Stdlib only.
"""
import argparse
import os
import re
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DESIGN = os.path.join(ROOT, "design")

STATUS = re.compile(r"<!--\s*status:\s*(.+?)\s*-->", re.I | re.S)
LINK = re.compile(r"\[[^\]]*\]\(([^)\s#]+)[^)]*\)|`(design/[\w./-]+\.md)`")
# `deleted` and `removed` are here for the provenance note, which is the RIGHT way to
# cite a file that no longer exists: "rescued 2026-08-20 from <path>, which was deleted".
# Without them the checker reports a broken link on exactly the sentence that explains
# why the link is broken, and the only way to satisfy it is to delete the provenance.
HISTORICAL = re.compile(
    r"~~|superseded|\bdead\b|⛔|formerly|no longer|\bdeleted\b|\bremoved\b|"
    r"\bretired\b|\bmoved (here|from)\b", re.I)
FENCE = re.compile(r"^\s*(```|~~~)")
# A dead doc sometimes says so in prose before anyone writes the header. Catch that
# too, or the checker reports clean on the exact file that motivated it.
DEAD_PROSE = re.compile(r"⛔\s*\**\s*DEAD DOCUMENT|^#+\s*⛔.*\bDEAD\b", re.I | re.M)


def docs():
    out = []
    for dirpath, _d, files in os.walk(DESIGN):
        out += [os.path.join(dirpath, f) for f in files if f.endswith(".md")]
    return sorted(out)


def status_of(path, head_lines=40):
    """-> (status, detail). Reads only the head: a header buried at line 900 is not
    a header, because no reader would have got that far before believing the doc."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return "unreadable", ""
    head = "\n".join(text.splitlines()[:head_lines])
    m = STATUS.search(head)
    if m:
        raw = m.group(1)
        kind = raw.split(";")[0].split(":")[0].strip().lower()
        return (kind if kind in ("live", "dead", "aspirational", "superseded-by")
                else "unknown"), raw
    if DEAD_PROSE.search(head):
        return "dead", "declared dead in prose, with no status header"
    return "unmarked", ""


def links_from(path):
    """-> [(lineno, target, line)] for links that are not citing something as dead."""
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return out
    infence = False
    for i, line in enumerate(lines, 1):
        if FENCE.match(line):
            infence = not infence
            continue
        if infence:
            continue
        for m in LINK.finditer(line):
            target = m.group(1) or m.group(2)
            if not target or not target.endswith(".md"):
                continue
            # 🔑 THE EXEMPTION IS ROW-SCOPED HERE, AND CELL-SCOPED IN check_canon.py.
            # That looks inconsistent and is not. A NUMBER is a claim all by itself, so
            # a `~~` in a neighbouring cell says nothing about it — scoping to the line
            # there silently exempted a live 8.6% because the cell beside it struck
            # through a dead citation. A LINK in a table row is the opposite: the row IS
            # one statement about that document, and
            #     | ⛔ dead | [old](pipeline.md) | replaced by X |
            # is the canonical shape of a supersession table. Cell-scoping it would make
            # every correctly-written supersession table an error, which would teach
            # people to stop writing them.
            if HISTORICAL.search(line):
                continue                     # citing it AS dead — legal, and correct
            out.append((i, target, line.strip()))
    return out


def resolve(src, target):
    if target.startswith("design/"):
        return os.path.normpath(os.path.join(ROOT, target))
    return os.path.normpath(os.path.join(os.path.dirname(src), target))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true", help="print every doc's status")
    ap.add_argument("--require-status", action="store_true",
                    help="also fail on any doc with no status header")
    a = ap.parse_args()

    all_docs = docs()
    st = {p: status_of(p) for p in all_docs}

    if a.status:
        for p in all_docs:
            kind, detail = st[p]
            print("  %-10s %s%s" % (kind, os.path.relpath(p, ROOT),
                                    ("  — " + detail[:70]) if detail else ""))
        counts = {}
        for p in all_docs:
            counts[st[p][0]] = counts.get(st[p][0], 0) + 1
        print("\n%d docs: %s" % (len(all_docs), ", ".join(
            "%s %d" % (k, v) for k, v in sorted(counts.items(), key=lambda kv: -kv[1]))))
        return 0

    bad, missing_target = [], []
    for src in all_docs:
        if st[src][0] == "dead":
            continue                         # it is dead; where it points is moot
        for lineno, target, line in links_from(src):
            dst = resolve(src, target)
            if dst not in st:
                if dst.startswith(DESIGN):
                    missing_target.append((src, lineno, target))
                continue
            if st[dst][0] == "dead":
                bad.append((src, lineno, target, st[dst][1]))

    for src, lineno, target, why in bad:
        print("  %s:%d → %s" % (os.path.relpath(src, ROOT), lineno, target))
        print("      that document is DEAD%s" % ((" — " + why[:100]) if why else ""))
        print("      Either drop the link, or mark this citation as historical "
              "(`~~…~~`, or a line saying superseded/dead).")

    unmarked = [p for p in all_docs if st[p][0] == "unmarked"]
    print("\n%d docs checked. %d live→dead link(s), %d link(s) to a missing file, "
          "%d doc(s) with no status header."
          % (len(all_docs), len(bad), len(missing_target), len(unmarked)))
    if missing_target:
        for src, lineno, target in missing_target[:10]:
            print("  missing: %s:%d → %s" % (os.path.relpath(src, ROOT), lineno, target))
        if len(missing_target) > 10:
            print("  … and %d more" % (len(missing_target) - 10))
    if unmarked and not a.require_status:
        print("  ⚠️ unmarked is NOT a pass — run with --require-status once W3(a) "
              "has written the headers.")
    if not bad:
        print("✅ no live document links into a dead one.")
    return 1 if bad or (a.require_status and unmarked) else 0


if __name__ == "__main__":
    sys.exit(main())
