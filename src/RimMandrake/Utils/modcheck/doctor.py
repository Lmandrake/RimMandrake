#!/usr/bin/env python3
"""modcheck.doctor -- asserts that the five mod registries actually agree.

Spec: infrastructure/DETERMINISM_ASSESSMENT.md SS4 (C2 -- `modcheck doctor`).
Read that before changing this file; it is the design record, not this
docstring.

Five independent registries are keyed on the same bare string -- a mod's
repo folder name -- and nothing today asserts the join between them:

    1. src/{RimMandrake,RimStarWars,RimUtinni}/<Name>/            (FOUNDRY)
    2. design/validation_walks/<tier>/<Name>.md                   (agents)
    3. that walk's own `subject:` header path + declared packageId (agents)
    4. infrastructure/state/modcheck_status.json                  (status.py)
    5. the rimflow capability registry (`model.replay().capabilities`)

`doctor` REPORTS AND STOPS. It never repairs anything -- SS4 and SS10.5 are
emphatic that an automated sweep that repointed stale `subject:` paths is
what CREATED the worst finding here (several walks now legitimately claim
the same folder). Which walk owns a shared folder is the owner's decision;
this module's job ends at naming the collision and printing the remedy verb
a human runs.

Pure, offline, stdlib + this repo's own modules only. No game, no bridge.
Every check function is (data) -> findings so it can be exercised against a
fixture repo in the selftest without touching the real ledger or the real
`modcheck_status.json` -- only `run()`/`main()` do real I/O.

Findings are (severity, cls, subject, detail) 4-tuples, severities "FAIL"
(blocks the selftest / CLI exit code) or "WARN" (prints, never gates) --
same two-severity discipline as `walklint.py`, this module's sibling and
model.

CLAUDE.md's two traps this module is built to not fall into:
  - "An existence test is not an identity test" -- every folder resolution
    here checks for `About/About.xml`, never just `os.path.isdir` (that is
    exactly how `src/RimMandrake/Pits`, containing only `__pycache__`,
    would otherwise pass).
  - "On a failed read say UNMEASURED, never 0 findings" -- `run()` raises
    loudly (never returns an empty, exit-0-looking result) if
    `modcheck_status.json` or the rimflow ledger fails to load or loads
    empty, and the CLI counts are asserted positive by the selftest.
"""
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
_UTILS = os.path.dirname(_HERE)          # src/RimMandrake/Utils
_RM = os.path.dirname(_UTILS)            # src/RimMandrake
if _RM not in sys.path:
    sys.path.insert(0, _RM)

import runner       # noqa: E402  runner.ROOT is the real repo root
import status       # noqa: E402  the GREEN/STALE registry this module audits
import walklint      # noqa: E402  reuse find_walks(repo_root) -- already tested
from rimflow import model  # noqa: E402  the capability registry's only reader

FAIL = "FAIL"
WARN = "WARN"

TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")

ORPHAN_WALK = "ORPHAN_WALK"                     # walk basename -> no src folder
WALK_NO_ABOUT = "WALK_NO_ABOUT"                 # folder exists, holds no About.xml
SUBJECT_MISSING = "SUBJECT_MISSING"             # no `subject:` header at all
SUBJECT_MISMATCH = "SUBJECT_MISMATCH"           # subject: path != resolved folder
PACKAGEID_MISMATCH = "PACKAGEID_MISMATCH"       # subject:'s packageId != About.xml's
SUBJECT_COLLISION = "SUBJECT_COLLISION"         # 2+ walks declare the same subject
ORPHAN_STATUS = "ORPHAN_STATUS"                 # status.json key -> no src folder
STATUS_DISAGREEMENT = "STATUS_DISAGREEMENT"     # stored status != status.check()
ORPHAN_CAPABILITY = "ORPHAN_CAPABILITY"         # capability name -> no src folder
WALK_WITHOUT_CAPABILITY = "WALK_WITHOUT_CAPABILITY"   # walk's mod has no cap row
CAPABILITY_WITHOUT_WALK = "CAPABILITY_WITHOUT_WALK"   # cap row's mod has no walk

_SUBJECT_LINE_RE = re.compile(r"^subject:\s*(\S+)", re.IGNORECASE)
_SUBJECT_PKGID_RE = re.compile(r"packageid:?\s*`?([A-Za-z0-9_.]+)`?",
                               re.IGNORECASE)
_PACKAGEID_TAG_RE = re.compile(r"<packageId>([^<]+)</packageId>",
                               re.IGNORECASE)


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def mod_name_from_walk(walk_path):
    return os.path.splitext(os.path.basename(walk_path))[0]


# ------------------------------------------------------------- resolution
def find_mod_folder(repo_root, mod):
    """(dir_or_None, ambiguous_bool) for `mod`'s repo folder name, searched
    across the three tiers -- the same lookup as `runner.find_mod_dir`, but
    parameterized on `repo_root` (never raises) so this module is testable
    against a fixture and never depends on the live repo's ROOT global."""
    hits = []
    for tier in TIERS:
        cand = os.path.join(repo_root, "src", tier, mod)
        if os.path.isdir(cand):
            hits.append(cand)
    if not hits:
        return None, False
    if len(hits) > 1:
        return None, True
    return hits[0], False


def has_about(mod_dir):
    return bool(mod_dir) and os.path.isfile(
        os.path.join(mod_dir, "About", "About.xml"))


def about_packageid(mod_dir):
    """The first `<packageId>` in `mod_dir`'s About.xml, or None if there is
    no About.xml or no tag -- never raises."""
    about = os.path.join(mod_dir, "About", "About.xml")
    if not os.path.isfile(about):
        return None
    m = _PACKAGEID_TAG_RE.search(_read(about))
    return m.group(1).strip() if m else None


def parse_subject(walk_path):
    """(subject_path, subject_packageid) from a walk's `subject:` header --
    the FIRST line starting with `subject:`, never a fixed line index
    (CLAUDE.md: "read the first matching line, never an index"). Both are
    None if the walk carries no such line at all."""
    for line in _read(walk_path).splitlines():
        stripped = line.strip()
        m = _SUBJECT_LINE_RE.match(stripped)
        if m:
            pkg_m = _SUBJECT_PKGID_RE.search(stripped)
            return m.group(1), (pkg_m.group(1) if pkg_m else None)
    return None, None


# --------------------------------------------------------------- assertions
def check_walks(repo_root, walks=None):
    """Assertions 1-5 of SS4's table: every walk's basename resolves to
    exactly one folder holding About.xml, its `subject:` agrees with that
    folder, its declared packageId agrees with that folder's About.xml, and
    no two walks share a `subject:`. Returns (findings, counts)."""
    if walks is None:
        walks = walklint.find_walks(repo_root)
    findings = []
    subjects = {}   # normalized subject path -> [walk paths]

    for w in walks:
        mod = mod_name_from_walk(w)
        mod_dir, ambiguous = find_mod_folder(repo_root, mod)

        if ambiguous:
            findings.append((FAIL, ORPHAN_WALK, w,
                             "`%s` exists in more than one tier -- "
                             "ambiguous, cannot resolve" % mod))
        elif mod_dir is None:
            findings.append((FAIL, ORPHAN_WALK, w,
                             "no src/<tier>/%s folder exists" % mod))
        elif not has_about(mod_dir):
            findings.append((FAIL, WALK_NO_ABOUT, w,
                             "%s holds no About/About.xml" %
                             os.path.relpath(mod_dir, repo_root)))

        subj_path, subj_pkgid = parse_subject(w)
        if subj_path is None:
            findings.append((WARN, SUBJECT_MISSING, w,
                             "no `subject:` header line"))
        else:
            norm = subj_path.rstrip("/")
            subjects.setdefault(norm, []).append(w)

            if mod_dir is not None:
                resolved_rel = os.path.relpath(mod_dir, repo_root).replace(
                    os.sep, "/")
                if norm != resolved_rel:
                    findings.append((FAIL, SUBJECT_MISMATCH, w,
                                     "subject: says %r, resolves to %r"
                                     % (norm, resolved_rel)))

            if subj_pkgid is not None and mod_dir is not None and has_about(mod_dir):
                real_pkgid = about_packageid(mod_dir)
                if real_pkgid and subj_pkgid.lower() != real_pkgid.lower():
                    findings.append((WARN, PACKAGEID_MISMATCH, w,
                                     "subject: declares packageId %r, "
                                     "About.xml says %r"
                                     % (subj_pkgid, real_pkgid)))

    for norm, ws in sorted(subjects.items()):
        if len(ws) > 1:
            findings.append((FAIL, SUBJECT_COLLISION, norm,
                             "%d walks all declare subject: %s -- %s"
                             % (len(ws), norm,
                                ", ".join(sorted(mod_name_from_walk(x)
                                                 for x in ws)))))

    counts = {"walks": len(walks), "subject_collisions":
              sum(1 for ws in subjects.values() if len(ws) > 1)}
    return findings, counts


def check_status(repo_root, status_data):
    """Assertions 6-7: every `modcheck_status.json` key resolves to a
    folder, and its recorded `status` field agrees with a fresh
    `status.check()` re-derivation. `status_data` is passed in (not loaded
    here) so this is testable against a fixture without touching the real
    registry."""
    findings = []
    for mod, entry in sorted(status_data.items()):
        mod_dir, ambiguous = find_mod_folder(repo_root, mod)
        if mod_dir is None:
            reason = ("ambiguous folder" if ambiguous
                      else "no such mod folder")
            findings.append((FAIL, ORPHAN_STATUS, mod,
                             "modcheck_status.json has an entry for %r "
                             "but %s -- recorded status was %r"
                             % (mod, reason, entry.get("status"))))
            continue
        recomputed = status.check(mod, mod_dir)
        recorded = entry.get("status")
        # `status.check()` decorates a non-GREEN verdict with a human-
        # readable reason in parens (e.g. "RED (last run failed)") -- that
        # is the SAME verdict as the raw stored field, not a disagreement.
        # Compare only the leading token, so the real bug this assertion
        # exists to catch -- a stored GREEN whose hash has since moved,
        # which `check()` calls STALE -- is what actually fires.
        recomputed_verdict = recomputed.split(" (", 1)[0]
        if recomputed_verdict != recorded:
            findings.append((FAIL, STATUS_DISAGREEMENT, mod,
                             "modcheck_status.json says %r, "
                             "status.check() says %r"
                             % (recorded, recomputed)))
    return findings, {"status_entries": len(status_data)}


def check_capabilities(repo_root, capability_names):
    """Assertion 8: every rimflow capability name resolves to a folder."""
    findings = []
    for name in sorted(capability_names):
        mod_dir, ambiguous = find_mod_folder(repo_root, name)
        if mod_dir is None:
            reason = "ambiguous folder" if ambiguous else "no such mod folder"
            findings.append((FAIL, ORPHAN_CAPABILITY, name,
                             "rimflow capability %r resolves to %s"
                             % (name, reason)))
    return findings, {"capabilities": len(capability_names)}


def check_cross_registry(walk_mod_names, capability_names):
    """Assertion 9: every mod with a walk has a capability row, and vice
    versa. WARN, not FAIL -- SS4 lists this as the weakest of the nine
    (some absorbed mods legitimately have neither any more)."""
    findings = []
    walk_set = set(walk_mod_names)
    cap_set = set(capability_names)
    for mod in sorted(walk_set - cap_set):
        findings.append((WARN, WALK_WITHOUT_CAPABILITY, mod,
                         "has a validation walk but no rimflow capability "
                         "row"))
    for mod in sorted(cap_set - walk_set):
        findings.append((WARN, CAPABILITY_WITHOUT_WALK, mod,
                         "has a rimflow capability row but no validation "
                         "walk"))
    return findings


# --------------------------------------------------------------- top level
def run(repo_root=None):
    """Everything `doctor` asserts. Returns (findings, counts).

    Raises RuntimeError -- never returns a quiet empty result -- if
    `modcheck_status.json` or the rimflow ledger fails to load, or loads
    with zero entries: CLAUDE.md's "reading nothing and exiting 0 is this
    repo's signature silent failure," repeated verbatim in SS4's own "cost
    and risk" section."""
    repo_root = repo_root or runner.ROOT
    findings = []
    counts = {}

    walks = walklint.find_walks(repo_root)
    if not walks:
        raise RuntimeError(
            "UNMEASURED: design/validation_walks under %r matched zero "
            "walk files -- refusing to report a clean bill of health on "
            "an empty read." % repo_root)
    w_findings, w_counts = check_walks(repo_root, walks)
    findings.extend(w_findings)
    counts.update(w_counts)

    try:
        status_data = status.load()
    except Exception as e:
        raise RuntimeError(
            "UNMEASURED: could not load %s: %s" % (status.LOG_PATH, e))
    if not status_data:
        raise RuntimeError(
            "UNMEASURED: %s loaded but holds zero entries." % status.LOG_PATH)
    s_findings, s_counts = check_status(repo_root, status_data)
    findings.extend(s_findings)
    counts.update(s_counts)

    try:
        events = model.read(model.EVENTS)
        world = model.replay(events)
    except Exception as e:
        raise RuntimeError(
            "UNMEASURED: could not replay the rimflow ledger (%s): %s"
            % (model.EVENTS, e))
    capabilities = world.capabilities
    if not capabilities:
        raise RuntimeError(
            "UNMEASURED: rimflow capability registry replayed to zero "
            "entries.")
    c_findings, c_counts = check_capabilities(repo_root, capabilities.keys())
    findings.extend(c_findings)
    counts.update(c_counts)

    walk_mod_names = {mod_name_from_walk(w) for w in walks}
    findings.extend(check_cross_registry(walk_mod_names, capabilities.keys()))

    return findings, counts


_REMEDY = {
    ORPHAN_WALK: "This walk's mod folder does not exist under src/. If the "
                "mod was renamed, `git mv` the walk to match. If it was "
                "absorbed into another mod, merge or delete this walk "
                "(owner's call).",
    WALK_NO_ABOUT: "The resolved folder holds no About/About.xml -- it was "
                  "almost certainly merged into another mod and left "
                  "behind. Delete or repoint this walk (owner's call).",
    SUBJECT_MISSING: "Add a `subject: <path>  (packageId <id>)` header line "
                     "to this walk.",
    SUBJECT_MISMATCH: "`git mv` this walk to match its resolved folder, or "
                      "edit its `subject:` line to the folder it actually "
                      "describes -- do not let an automated sweep repoint "
                      "this (SS4/SS10.5: that is what created the shared-"
                      "subject collisions in the first place).",
    PACKAGEID_MISMATCH: "The walk's declared packageId does not match the "
                        "resolved folder's About.xml. Fix whichever one is "
                        "wrong.",
    SUBJECT_COLLISION: "Multiple walks claim the same folder; only one "
                       "basename can ever be reached by `modcheck run`. "
                       "Decide (owner's call) whether to merge them into "
                       "one walk, keep the rest as per-feature walks under "
                       "a new `feature:` key, or delete the redundant ones.",
    ORPHAN_STATUS: "`infrastructure/state/modcheck_status.json` has a row "
                  "for a mod that no longer exists. If it was renamed or "
                  "absorbed, retire the old rimflow capability with "
                  "`rimflow capability retire <name> --owner-said ...` and "
                  "leave the stale status row as history, or remove it by "
                  "hand if the owner says to.",
    STATUS_DISAGREEMENT: "The stored `status` field disagrees with a fresh "
                         "`status.check()`. Usually the mod's hash changed "
                         "since the last recorded run -- run `modcheck run "
                         "<mod>` to refresh it, or `modcheck declare <mod> "
                         "minor --why ...` if the change was trivial.",
    ORPHAN_CAPABILITY: "This rimflow capability name resolves to no mod "
                       "folder. `rimflow capability retire <name> "
                       "--owner-said ...` if the mod is genuinely gone, or "
                       "correct the name if it was a typo.",
    WALK_WITHOUT_CAPABILITY: "This mod has a validation walk but no rimflow "
                             "capability row -- `rimflow capability set "
                             "<name> ...` once its maturity is known, or "
                             "leave it if the mod predates the capability "
                             "registry.",
    CAPABILITY_WITHOUT_WALK: "This mod has a rimflow capability row but no "
                             "validation walk -- author one, or note in the "
                             "capability's evidence why it has none.",
}

_SYMBOL = {FAIL: "\U0001F534", WARN: "\U0001F7E0"}


def format_finding(f):
    severity, cls, subject, detail = f
    remedy = _REMEDY.get(cls, "Fix it.")
    return "%s %-24s %s\n    %s\n    remedy: %s" % (
        _SYMBOL.get(severity, "?"), cls, subject, detail, remedy)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    repo_root = argv[0] if argv else runner.ROOT
    try:
        findings, counts = run(repo_root)
    except RuntimeError as e:
        print(str(e))
        return 2

    print("modcheck doctor: %d walks, %d status entries, %d capability "
          "rows" % (counts.get("walks", 0), counts.get("status_entries", 0),
                    counts.get("capabilities", 0)))
    for f in sorted(findings, key=lambda x: (x[1], x[2])):
        print(format_finding(f))
    n_fail = sum(1 for f in findings if f[0] == FAIL)
    n_warn = sum(1 for f in findings if f[0] == WARN)
    print("%d FAIL, %d WARN" % (n_fail, n_warn))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
