#!/usr/bin/env python3
"""modcheck.walklint -- every identifier a validation walk names must exist.

Spec: infrastructure/DETERMINISM_ASSESSMENT.md SS3 (C1 -- walklint). Read that
before changing this file; it is the design record, not this docstring.

A `design/validation_walks/<tier>/<Name>.md` is prose an agent executes by
hand. Nothing today checks that a packageId, defName, class name or filename
it names still exists -- so a rename or merge leaves a walk step asserting
the ABSENCE of a string that can now never appear, a test that cannot fail.
`lint()` is a pure, offline, stdlib-only function that finds those.

Report, never repair: this module never edits a walk. Every finding carries
a remedy line a human runs. Not a commit hook -- callable module + selftest
only (SS3, "do NOT make it a PreToolUse commit hook").

Scope (SS3, "what it cannot capture"): OUR identifiers only --
`mandrake.*` packageIds and `RM_/RSW_/RUT_` symbols. Third-party ids
(vanillaracesexpanded.phytokin, PeteTimesSix.ResearchReinvented, ...) are
unmeasurable offline and are never flagged.

Escape hatch, copied in spirit from `.claude/hooks/block_canon_contradiction.py`:
a walk line legitimately naming a dead identifier (e.g. recording a rename)
suppresses its own finding with

    <!-- walklint-ok: reason -->

on the line itself or the line immediately above.

Findings are (severity, cls, walk_path, line_no, token) 5-tuples.
Severities: "FAIL" (blocks a selftest / CLI exit code) or "WARN" (prints,
never gates). Classes: VACUOUS, BAD_SUBJECT, BAD_PACKAGEID (all FAIL);
UNKNOWN_ID, BAD_FILE (both WARN) -- matching SS3's 5-class list in severity
order.

The one dangerous failure mode (SS3, "cost and risk"): a glob that silently
matches nothing, so the tool reports zero findings and exits 0. `build_index`
and `lint` both return their input counts so a caller -- and the selftest --
can assert them positive.
"""

import os
import re
import sys

FAIL = "FAIL"
WARN = "WARN"

VACUOUS = "VACUOUS"
BAD_SUBJECT = "BAD_SUBJECT"
BAD_PACKAGEID = "BAD_PACKAGEID"
UNKNOWN_ID = "UNKNOWN_ID"
BAD_FILE = "BAD_FILE"

_ESCAPE_RE = re.compile(r"<!--\s*walklint-ok:\s*.+?-->")

# A step asserting the ABSENCE of something. Broadened beyond the original
# "Config error" pattern per SS3's instruction to generalise the verb forms.
_ABSENCE_RE = re.compile(
    r"contains no|produces no|does not (?:appear|log|contain)"
    r"|never (?:logs|appears|names)|zero errors",
    re.IGNORECASE,
)

# `mandrake.<anything>` -- our own packageId shape. Trailing punctuation
# (backtick/quote/paren/comma/colon) is stripped by the caller, not here.
_PKGID_RE = re.compile(r"\bmandrake\.[A-Za-z0-9_.]+\b", re.IGNORECASE)

# A backticked our-tier symbol: `RM_Foo`, `RSW_WS_Bar`, `RUT_Baz`.
_BACKTICK_SYMBOL_RE = re.compile(r"`((?:RM_|RSW_|RUT_)[A-Za-z0-9_]+)`")

# A backticked filename with one of the tracked extensions.
_BACKTICK_FILE_RE = re.compile(
    r"`([^`\s]+\.(?:xml|cs|png|dll))`", re.IGNORECASE
)

# Bare (unbacktick-scoped) RM_/RSW_/RUT_ token, for indexing our own C# source.
_BARE_SYMBOL_RE = re.compile(r"\b(?:RM_|RSW_|RUT_)[A-Za-z0-9_]+\b")

# C# type declarations, for indexing our own C# source.
_CS_TYPE_RE = re.compile(
    r"\b(?:class|struct|enum|interface)\s+([A-Za-z_][A-Za-z0-9_]*)"
)

_DEFNAME_RE = re.compile(r"<defName>([^<]+)</defName>")
_NAME_ATTR_RE = re.compile(r'\bName="([^"]+)"')
_PACKAGEID_TAG_RE = re.compile(r"<packageId>([^<]+)</packageId>")

_FILE_ALLOWLIST = {"ModsConfig.xml", "Player.log"}

_TRAILING_PUNCT = ".,:;)`'\"]"


def _strip_punct(tok):
    return tok.rstrip(_TRAILING_PUNCT)


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


# --------------------------------------------------------------- discovery
def find_walks(repo_root):
    """Every `design/validation_walks/<tier>/*.md`, sorted for determinism."""
    base = os.path.join(repo_root, "design", "validation_walks")
    out = []
    if not os.path.isdir(base):
        return out
    for tier in sorted(os.listdir(base)):
        tdir = os.path.join(base, tier)
        if not os.path.isdir(tdir):
            continue
        for name in sorted(os.listdir(tdir)):
            if name.endswith(".md"):
                out.append(os.path.join(tdir, name))
    return out


# ------------------------------------------------------------------- index
def build_index(repo_root):
    """Our own packageIds, XML names and RM_/RSW_/RUT_ symbols, plus every
    basename under src/. Returns a dict of sets, so a caller can report
    (and the selftest can assert) each index's size independently."""
    packageids = set()
    xml_names = set()
    cs_symbols = set()
    basenames = set()

    src = os.path.join(repo_root, "src")
    for dirpath, _dirnames, filenames in os.walk(src):
        for fn in filenames:
            basenames.add(fn)
            full = os.path.join(dirpath, fn)
            low = fn.lower()
            if low == "about.xml":
                text = _read(full)
                m = _PACKAGEID_TAG_RE.search(text)
                if m:
                    packageids.add(m.group(1).strip())
                # Fall through: About.xml is also scanned for defName/Name
                # below like any other xml, which is harmless (it has none).
            if low.endswith(".xml"):
                text = _read(full)
                xml_names.update(_DEFNAME_RE.findall(text))
                xml_names.update(_NAME_ATTR_RE.findall(text))
            elif low.endswith(".cs"):
                text = _read(full)
                cs_symbols.update(_CS_TYPE_RE.findall(text))
                cs_symbols.update(_BARE_SYMBOL_RE.findall(text))

    return {
        "packageids": packageids,
        "xml_names": xml_names,
        "cs_symbols": cs_symbols,
        "basenames": basenames,
    }


def _symbol_index(index):
    return index["xml_names"] | index["cs_symbols"]


# ------------------------------------------------------------- escape hatch
def _escaped_lines(lines):
    """Line numbers (1-indexed) a `walklint-ok` marker suppresses: the line
    the marker is on, and the line right after it (SS3: "on the line or the
    line above" -- read from the flagged line's point of view)."""
    escaped = set()
    for i, line in enumerate(lines, start=1):
        if _ESCAPE_RE.search(line):
            escaped.add(i)
            escaped.add(i + 1)
    return escaped


# ------------------------------------------------------------------ linting
def lint_walk(path, index, repo_root):
    """Findings for one walk file. Pure: no I/O beyond reading `path`."""
    text = _read(path)
    lines = text.splitlines()
    escaped = _escaped_lines(lines)
    packageids = index["packageids"]
    symbols = _symbol_index(index)
    basenames = index["basenames"]

    findings = []

    def emit(severity, cls, line_no, token):
        if line_no in escaped:
            return
        findings.append((severity, cls, path, line_no, token))

    # 1/2: subject: header names a directory holding an About/About.xml.
    subject_seen = False
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.lower().startswith("subject:"):
            subject_seen = True
            rest = stripped.split(":", 1)[1].strip()
            token = rest.split()[0] if rest.split() else ""
            about = os.path.join(repo_root, token, "About", "About.xml")
            if not token or not os.path.isfile(about):
                emit(FAIL, BAD_SUBJECT, i, token or "(missing)")
            break  # only the first subject: line matters
    if not subject_seen:
        emit(FAIL, BAD_SUBJECT, 1, "(no subject: header)")

    # 3/1: every mandrake.* token, classified VACUOUS vs BAD_PACKAGEID by
    # whether its line is an absence assertion.
    for i, line in enumerate(lines, start=1):
        absence = bool(_ABSENCE_RE.search(line))
        for m in _PKGID_RE.finditer(line):
            token = _strip_punct(m.group(0))
            if token not in packageids:
                cls = VACUOUS if absence else BAD_PACKAGEID
                emit(FAIL, cls, i, token)

    # 4: backticked RM_/RSW_/RUT_ tokens unknown to the XML+C# index.
    for i, line in enumerate(lines, start=1):
        for m in _BACKTICK_SYMBOL_RE.finditer(line):
            token = m.group(1)
            if token not in symbols:
                emit(WARN, UNKNOWN_ID, i, token)

    # 5: backticked filenames absent from src/.
    for i, line in enumerate(lines, start=1):
        for m in _BACKTICK_FILE_RE.finditer(line):
            token = m.group(1)
            base = os.path.basename(token)
            if "*" in token or base.startswith("_"):
                continue  # a glob pattern, not a filename
            if base in _FILE_ALLOWLIST:
                continue
            if base not in basenames:
                emit(WARN, BAD_FILE, i, token)

    return findings


def lint(repo_root, index=None):
    """All findings across every walk under `repo_root`.

    Returns (findings, counts) where counts is
    {"walks": n, "packageids": n, "symbols": n} -- the positive-count
    assertion the selftest and the CLI both need (SS3, "cost and risk").
    """
    walks = find_walks(repo_root)
    if index is None:
        index = build_index(repo_root)
    findings = []
    for w in walks:
        findings.extend(lint_walk(w, index, repo_root))
    counts = {
        "walks": len(walks),
        "packageids": len(index["packageids"]),
        "symbols": len(_symbol_index(index)),
    }
    return findings, counts


_REMEDY = {
    VACUOUS: "This step asserts the ABSENCE of `%s`, which does not exist -- "
             "it can never fail. Fix the identifier, delete the step, or "
             "mark it `<!-- walklint-ok: reason -->` if it deliberately "
             "records a dead id.",
    BAD_SUBJECT: "`subject:` names `%s`, which holds no About/About.xml. "
                 "Point it at the mod's real src/ directory.",
    BAD_PACKAGEID: "`%s` is not declared by any About.xml under src/. "
                   "Fix the packageId or mark the line "
                   "`<!-- walklint-ok: reason -->`.",
    UNKNOWN_ID: "`%s` is not a known defName/Name/class in src/. Fix the "
                "identifier or mark the line "
                "`<!-- walklint-ok: reason -->`.",
    BAD_FILE: "`%s` is not a filename under src/. Fix it or mark the line "
              "`<!-- walklint-ok: reason -->`.",
}

_SYMBOL = {FAIL: "\U0001F534", WARN: "\U0001F7E0"}  # red/orange circles


def format_finding(f):
    severity, cls, path, line_no, token = f
    remedy = _REMEDY.get(cls, "Fix `%s`.") % token
    return "%s %-13s %s:%d  `%s`\n    %s" % (
        _SYMBOL.get(severity, "?"), cls, path, line_no, token, remedy)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    repo_root = argv[0] if argv else os.getcwd()
    findings, counts = lint(repo_root)
    print("walklint: %d walks, %d packageIds, %d symbols indexed"
          % (counts["walks"], counts["packageids"], counts["symbols"]))
    for f in findings:
        print(format_finding(f))
    n_fail = sum(1 for f in findings if f[0] == FAIL)
    n_warn = sum(1 for f in findings if f[0] == WARN)
    print("%d FAIL, %d WARN" % (n_fail, n_warn))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
