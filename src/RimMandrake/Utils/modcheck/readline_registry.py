#!/usr/bin/env python3
"""modcheck.readline_registry -- the shared read-line registry, and a lint

that a `shared`-tagged read-line id in any walk actually exists in it.

Spec: `design/validation_walks/_read_line_registry.md` (the registry itself,
and the citation convention) plus `READ_LINE_REGISTRY_SHARED_1` (owner ruling
2026-09-16: read-line ids are GLOBAL, with one shared registry for recurring
demands; mod-specific lines stay local). Amends
`design/RimMandrake/north_star_validation_spec.md` §10.1, which rules "one id
namespace across both axes" but is silent on per-mod vs global scope.

This module is deliberately independent of `northstar.py`'s `## north star`
parsing: the read axis's own hashing (spec §6a, `NORTHSTAR_HASH_SCOPE_1`'s
owed axis-scoped-hash machinery) is not built yet, so `northstar.parse()`
does not recognise `### must read` / `### cannot read` at all today. This
module reads those headings itself, offline, from raw text -- report only,
never repair, exactly like `walklint`.

A walk cites a registry entry by tagging its evidence-class parenthetical
with `, shared`:

    - [ ] `some_registered_id` (absolute, shared) -- prose copied verbatim

A citation is DANGLING (FAIL) when the tagged id is not a member of the
registry -- a typo, a removed entry, or an id that was never promoted. That
is the one thing this module checks; it does not (yet) diff the citing
walk's prose against the registry's canonical text, so a citation that has
drifted in WORDING but kept the right id is not caught here -- see the
registry file's own propagation warning.
"""

import os
import re
import sys

FAIL = "FAIL"

DANGLING_CITATION = "DANGLING_CITATION"

REGISTRY_REL_PATH = os.path.join("design", "validation_walks",
                                 "_read_line_registry.md")

# A checklist line naming an id and, optionally, a parenthesised class list:
#   - [ ] `some_id` (absolute, shared) -- prose
#   - [ ] `some_id` -- prose                       (no class at all)
_CHECKLIST_LINE = re.compile(
    r"^\s*-\s*\[[ xX]\]\s*`([A-Za-z0-9_]+)`\s*(?:\(([^)]*)\))?"
)

_READ_HEADING = re.compile(r"^###\s+(must read|cannot read)\b", re.IGNORECASE)
_ANY_H2 = re.compile(r"^##\s+")
_ANY_H3 = re.compile(r"^###\s+")


def registry_path(repo_root):
    return os.path.join(repo_root, REGISTRY_REL_PATH)


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


_REGISTRY_HEADING = re.compile(r"^##\s+registry\b", re.IGNORECASE)


def load_registry(repo_root):
    """The registry's own ids, as a set. Raises if the file is missing --
    a caller with no registry to check against should not report a silent
    zero, exactly per the "cost and risk" rule `walklint.lint` follows.

    Only lines inside the `## registry` section count, and a fenced code
    block (the "how to cite" example uses one) is skipped -- otherwise the
    file's own worked example of a citation would register itself as an
    entry."""
    path = registry_path(repo_root)
    if not os.path.isfile(path):
        raise FileNotFoundError(
            "no shared read-line registry at %s -- "
            "READ_LINE_REGISTRY_SHARED_1 is not built" % path)
    ids = set()
    inside_section = False
    in_fence = False
    for line in _read(path).splitlines():
        if _REGISTRY_HEADING.match(line.strip()):
            inside_section = True
            continue
        if inside_section and _ANY_H2.match(line.strip()) \
                and not _REGISTRY_HEADING.match(line.strip()):
            inside_section = False
        if not inside_section:
            continue
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = _CHECKLIST_LINE.match(line)
        if m:
            ids.add(m.group(1))
    return ids


def _read_sections(text):
    """Lines belonging to any `### must read` / `### cannot read` block,
    across the whole file (there may be more than one `## north star`
    section in principle; this module does not assume there is exactly
    one). Stops each block at the next `##` or `###` heading."""
    out = []
    inside = False
    for line in text.splitlines():
        if _READ_HEADING.match(line.strip()):
            inside = True
            continue
        if inside and (_ANY_H2.match(line) or _ANY_H3.match(line)):
            inside = False
        if inside:
            out.append(line)
    return out


def find_walks(repo_root):
    """Every walk under `design/validation_walks/<tier>/*.md`. The registry
    file itself lives one level up (not inside a tier directory) and is
    never returned here."""
    import walklint
    return walklint.find_walks(repo_root)


def citations_in(path):
    """`[(line_no, id, class_field)]` for every checklist line inside a
    `### must read` / `### cannot read` block of `path` whose class field
    contains the literal token `shared`."""
    text = _read(path)
    out = []
    inside = False
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if _READ_HEADING.match(stripped):
            inside = True
            continue
        if inside and (_ANY_H2.match(stripped) or _ANY_H3.match(stripped)):
            inside = False
        if not inside:
            continue
        m = _CHECKLIST_LINE.match(line)
        if not m:
            continue
        req_id, cls_field = m.group(1), (m.group(2) or "")
        tokens = [t.strip().lower() for t in cls_field.split(",")]
        if "shared" in tokens:
            out.append((i, req_id, cls_field.strip()))
    return out


def lint_walk(path, registry_ids):
    """Findings for one walk: a `(FAIL, DANGLING_CITATION, path, line_no,
    id)` tuple per `shared`-tagged id absent from the registry."""
    findings = []
    for line_no, req_id, _cls in citations_in(path):
        if req_id not in registry_ids:
            findings.append((FAIL, DANGLING_CITATION, path, line_no, req_id))
    return findings


def lint(repo_root):
    """All dangling-citation findings across every walk, plus counts so a
    caller can refuse a silent zero the way `walklint.lint` does.

    Returns (findings, counts) where
      counts = {"walks": n, "registry_ids": n, "citations": n}
    """
    registry_ids = load_registry(repo_root)
    walks = find_walks(repo_root)
    findings = []
    n_citations = 0
    for w in walks:
        cites = citations_in(w)
        n_citations += len(cites)
        for line_no, req_id, _cls in cites:
            if req_id not in registry_ids:
                findings.append((FAIL, DANGLING_CITATION, w, line_no, req_id))
    counts = {"walks": len(walks), "registry_ids": len(registry_ids),
              "citations": n_citations}
    return findings, counts


def format_finding(f):
    severity, cls, path, line_no, token = f
    return ("\U0001F534 %-18s %s:%d  `%s`\n"
            "    tagged `shared` but not in %s -- fix the id, add the "
            "entry, or drop the `shared` tag if this line is genuinely "
            "local." % (cls, path, line_no, token, REGISTRY_REL_PATH))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    repo_root = argv[0] if argv else os.getcwd()
    try:
        findings, counts = lint(repo_root)
    except FileNotFoundError as exc:
        print("UNMEASURED: %s" % exc)
        return 2
    print("readline_registry: %d walks, %d registry ids, %d `shared` "
          "citations checked" % (counts["walks"], counts["registry_ids"],
                                 counts["citations"]))
    for f in findings:
        print(format_finding(f))
    print("%d FAIL" % len(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
