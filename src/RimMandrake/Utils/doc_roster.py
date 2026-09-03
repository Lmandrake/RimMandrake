#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""doc_roster.py — regenerate the two hand-kept directory listings.

    python3 src/RimMandrake/Utils/doc_roster.py            # check only, exit 1 on drift
    python3 src/RimMandrake/Utils/doc_roster.py --write    # rewrite both

WHY THIS EXISTS
---------------
The 2026-08-20 documentation audit measured the cost of hand-kept indexes:
`skills/README.md` had 16 commits, **11 of them literally "New skill: X"**, and it
had still drifted — `rimworld-scenario-building` sat as a stray bullet BELOW the
table it belonged in, and the table named skills whose folders are not there.

A list that must be hand-edited every time something is added is a list that will
be wrong. Both listings here are derived from the files themselves:

  skills/README.md   the "when" table, from each SKILL.md's own `name` and
                     `description` frontmatter — the SAME text that decides when
                     the skill loads, so the roster cannot disagree with reality.
  design/INDEX.md    every design doc, grouped by directory, titled by its own H1.

🔑 Only the regions between the BEGIN/END markers are touched. The ownership
table, the tier rule and every hand-written ruling are left exactly alone — those
are decisions, not data, and no generator may own them.
"""
import argparse
import os
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
BEGIN = "<!-- doc_roster:BEGIN — generated, do not hand-edit -->"
END = "<!-- doc_roster:END -->"


def frontmatter(md: pathlib.Path) -> dict:
    text = md.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    out, key = {}, None
    for line in text[3:end].splitlines():
        m = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            out[key] = val.strip('"').strip("'")
        elif key and line.strip():
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def first_sentence(s: str, cap: int = 130) -> str:
    s = " ".join(s.split())
    # Not a naive split on ". " — descriptions are full of `.py`, `1.6` and `.md`.
    # Those never match: the period there is not followed by whitespace+capital
    # (an extension or version number continues in lowercase/digits), so the
    # lookahead alone already protects them - no lookbehind needed, and the
    # obvious one (excluding a preceding letter/digit) is wrong: it blocks
    # every ordinary sentence, which ends in a word.
    m = re.search(r"\.(?=\s+[A-Z])", s)
    if m:
        s = s[: m.start()]
    if len(s) <= cap:
        return s
    cut = s[:cap].rsplit(" ", 1)[0]      # never break a word or a `path/like/this`
    return cut.rstrip(" ,;:—-") + "…"


def skills_block() -> str:
    rows = []
    for d in sorted((REPO / "skills").iterdir()):
        md = d / "SKILL.md"
        if not d.is_dir() or not md.exists():
            continue
        fm = frontmatter(md)
        name = fm.get("name") or d.name
        desc = first_sentence(fm.get("description", ""))
        if not desc:
            desc = "⚠️ no description — this skill will not load reliably"
        rows.append(f"| `{name}` | {desc} |")
    head = ("| skill | when it loads |\n|---|---|\n"
            "| _(generated from each skill's own `description` — the text that actually "
            "decides when it loads, so no second copy can disagree)_ | |")
    return "\n".join([head] + rows)


# ⭐ The index carries each doc's STATUS, and that is the point of the column.
# `save_authoring_pipeline.md` opened with "⛔ DEAD DOCUMENT" on 2026-08-18 and this
# index still listed it beside every live doc, indistinguishable, for two days. A
# reader picking a document off an index has not opened it yet — the warning has to
# reach them HERE or it does not reach them in time.
#
# ⚠️ The status is read from the doc, never stored here: INDEX.md is generated and a
# status typed into it would be deleted by the next --write. To change what this
# column says, change the `<!-- status: ... -->` line in the document itself.
STATUS_RE = re.compile(r"<!--\s*status:\s*(.+?)\s*-->", re.I | re.S)
STATUS_MARK = {"dead": "⛔ dead", "superseded-by": "→ superseded",
               "aspirational": "☁ aspirational", "live": ""}


def doc_status(text: str, head_lines: int = 40) -> str:
    """-> a short status mark for the index, '' for live, '—' when unmarked.

    Only the head is read: a status buried at line 900 is not a status, because
    nobody would have got that far before believing the document.
    """
    m = STATUS_RE.search("\n".join(text.splitlines()[:head_lines]))
    if not m:
        return "—"                       # unmarked. NOT the same as live.
    raw = m.group(1)
    kind = raw.split(";")[0].split(":")[0].strip().lower()
    mark = STATUS_MARK.get(kind, "? " + kind)
    # ⚠️ A doc can be live in its RULINGS and dead in its NUMBERS, and the four statuses
    # cannot say so. `worldgen_interactive_def.md` is exactly that: its banner reads "THE
    # RULINGS IN THIS FILE STAND. ITS MEASUREMENTS DO NOT" — it is cited for decisions
    # that are current while every figure in it measures a planet that no longer exists.
    # Marked `live`, the machine-readable half of that warning was simply lost, and
    # `live` is the status that invites quoting. So one optional extra field:
    #     <!-- status: live ; numbers-superseded-by: <path> ; <date> ; <why> -->
    if "numbers-superseded-by" in raw.lower():
        mark = (mark + " · " if mark else "") + "⚠ do not quote its numbers"
    if kind == "superseded-by":
        # Name the successor here too. "Superseded" without a forwarding address
        # tells the reader to stop and gives them nowhere to go.
        target = raw.split(":", 1)[1].split(";")[0].strip() if ":" in raw else ""
        if target:
            mark += " `%s`" % os.path.basename(target)
    return mark


def design_index() -> str:
    root = REPO / "design"
    by_dir: dict[str, list[tuple[str, str, str]]] = {}
    for md in sorted(root.rglob("*.md")):
        rel = md.relative_to(root)
        if rel.name in ("INDEX.md", "README.md"):
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        title = ""
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        by_dir.setdefault(str(rel.parent), []).append(
            (rel.name, title, doc_status(text)))
    out = []
    unmarked = sum(1 for v in by_dir.values() for e in v if e[2] == "—")
    if unmarked:
        out.append("\n⚠️ **%d doc(s) carry no `<!-- status: -->` line and show `—` below.**"
                   " Unmarked is not the same as live: it means nobody has said."
                   % unmarked)
    for d in sorted(by_dir):
        out.append(f"\n### `design/{d}/`\n" if d != "." else "\n### `design/`\n")
        out.append("| doc | title | status |")
        out.append("|---|---|---|")
        for name, title, status in by_dir[d]:
            out.append(f"| `{name}` | {title or '—'} | {status} |")
    return "\n".join(out)


def splice(path: pathlib.Path, block: str, header: str = "") -> bool:
    """Replace the marked region. Returns True if the file changed."""
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    new_region = f"{BEGIN}\n{header}{block}\n{END}"
    if BEGIN in old and END in old:
        pre, rest = old.split(BEGIN, 1)
        _, post = rest.split(END, 1)
        new = pre + new_region + post
    else:
        new = (old.rstrip("\n") + "\n\n" + new_region + "\n") if old else new_region + "\n"
    if new == old:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="rewrite the generated regions (default: check only)")
    args = ap.parse_args()

    targets = [
        (REPO / "skills" / "README.md", skills_block(), ""),
        (REPO / "design" / "INDEX.md", design_index(),
         "# design/ — every document, by directory\n\n"
         "⚠️ **Generated by `src/RimMandrake/Utils/doc_roster.py`. Do not hand-edit.**\n"
         "This is an index, not doctrine — the tier rule and the promotion test live in\n"
         "`design/README.md` and are written by hand.\n"),
    ]
    drift = []
    for path, block, header in targets:
        before = path.read_text(encoding="utf-8") if path.exists() else ""
        changed = splice(path, block, header)
        if changed and not args.write:
            path.write_text(before, encoding="utf-8")   # check-only: put it back
        if changed:
            drift.append(path.relative_to(REPO))

    if not drift:
        print("doc_roster: both listings in sync")
        return 0
    verb = "rewrote" if args.write else "OUT OF SYNC"
    for p in drift:
        print(f"doc_roster: {verb} {p}")
    return 0 if args.write else 1


if __name__ == "__main__":
    sys.exit(main())
