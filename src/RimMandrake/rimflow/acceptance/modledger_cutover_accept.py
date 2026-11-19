#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_CUTOVER_PILOT_MODS_TO_LEDGER_SAME_DAY (plan
design/plans/2026-11-15-holder-pipeline-fusion-build.md step 4; spec §3.2, §3.8 step 4). Written by the filing seat;
the builder does not edit it (a wrong clause goes to the Conductor).

    python3 src/RimMandrake/rimflow/acceptance/modledger_cutover_accept.py ExplosiveKnockback GimmeSomeSlack FlowWorks

THE CONTRACT, per mod named. Each old hand-written store, `stage.json`, `journal.md` and `version/stage_record.json`
(relative to design/concepts/<Mod>/), is either
  (a) a generated view: a text file whose first line holds "modledger view, generated", or a JSON object with a
      top-level "_view" key, which `modledger.py lint --mod <Mod>` checks like the views under ledger/views/; or
  (b) gone from its place, with its last content kept read-only at archive_pre_ledger/<same relative path> (no write
      bit for anyone).
The mod's ledger lints clean against origin/main. And no writer is left outside modledger: measured at run time by
store_write_census.py (the Conductor's decision 2026-11-18 7:35 PM PST, item
RIMMANDRAKE_NARROW_CUTOVER_WRITER_CHECK_EIGHT_OF_THIRTEEN_READ; the clause it replaced matched source text, counted 8
readers among 13 "writers" and excused maturation.py, a real writer, for importing modledger inside a function): the
pipeline selftests and each candidate's own selftests run under a hook that records every module opening one of the
three stores for writing. A module the hook saw writing is a writer; one whose store-naming or writing scopes never
ran under any test is NOT MEASURED, named, and never counted as "does not write"; so is the whole clause when a test
started a Python child the hook could not follow.
Exit 0 with "PASS n/n" only when all pass (expected 3 mods x 4 checks + 1 writer check = 13); 3 when the census could
not look (its planted probe write was not caught), else 1 on any FAIL, else 2 when a module is NOT MEASURED.

    --writers-only --root R    the writer clause alone, on the tree at R (the selftest's fixture repos)
    --census record.json       read a census record (store_write_census.py --out) instead of running one; refused as
                               COULD NOT LOOK unless it is a whole census of this tree (same code, probe caught, tests
                               run, every current candidate present with a known verdict)
"""
import argparse
import json
import os
import stat
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import modledger as M                                            # noqa: E402
import store_write_census as C                                   # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("mods", nargs="*")
ap.add_argument("--writers-only", action="store_true")
ap.add_argument("--root", default=M.REPO_ROOT)
ap.add_argument("--census", help="a store_write_census.py --out record to read instead of running one")
A = ap.parse_args()
ROOT = os.path.abspath(A.root)
OLD = ("journal.md", os.path.join("version", "stage_record.json"))
res = []                                     # "PASS", "FAIL", "NOT MEASURED" or "COULD NOT LOOK", one per check


def check(name, ok, detail="", answer=None):
    a = answer or ("PASS" if ok else "FAIL")
    res.append(a)
    print(a + "  " + name + ("" if a == "PASS" else "  " + str(detail)))


def is_view(p):
    """A text view whose first line says so, or a JSON object with a top-level "_view" key; anything else, an
    unreadable file or one that is not UTF-8 included, is not a view."""
    try:
        with open(p, encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError):
        return False
    if p.endswith(".json"):
        try:
            v = json.loads(text)
        except ValueError:
            return False
        return isinstance(v, dict) and "_view" in v
    return "modledger view, generated" in text.split("\n", 1)[0]


def archived(c, rel):
    """The last content kept: a regular file at archive_pre_ledger/<rel> with no write bit for anyone."""
    a = os.path.join(c, "archive_pre_ledger", rel)
    return os.path.isfile(a) and not (os.stat(a).st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


for mod in ([] if A.writers_only else (A.mods or ["ExplosiveKnockback", "GimmeSomeSlack", "FlowWorks"])):
    c = os.path.join(ROOT, "design", "concepts", mod)
    for rel in OLD:
        p = os.path.join(c, rel)
        ok = is_view(p) or (not os.path.exists(p) and archived(c, rel))
        check("%s: %s is a generated view or archived read-only" % (mod, rel), ok,
              "still a hand-written file" if os.path.exists(p) else "gone, no read-only archive")
    try:
        findings, _ = M.lint(ROOT, mod, base="origin/main")
        check("%s: the mod ledger lints clean" % mod, bool(M.read(ROOT, mod)) and findings == [], findings[:3])
    except Exception as e:                      # a lint that cannot run has not answered: never a FAIL of the mod
        check("%s: the mod ledger lints clean" % mod, False, "the lint could not run: %s: %s" % (type(e).__name__, e),
              answer="COULD NOT LOOK")


VERDICTS = {"WRITER", "NOT_MEASURED", "NO_WRITE_SEEN"}


def whole(rec):
    """A record read from --census -> None when it is a whole census of this tree (or says itself it could not
    look), else why not."""
    if rec.get("status") != "ok":
        return None
    try:
        if rec.get("schema") != 2:
            return "schema %r, not 2" % rec.get("schema")
        if os.path.abspath(rec.get("root") or "") != ROOT or rec.get("fingerprint") != C.fingerprint(ROOT):
            return "it was taken on other code"
        if (rec.get("probe") or {}).get("caught") is not True:
            return "its probe write was not caught"
        if not rec.get("tests"):
            return "it ran no test"
        mods = rec.get("modules")
        if not isinstance(mods, dict) or any(not isinstance(v, dict) or v.get("verdict") not in VERDICTS
                                             for v in mods.values()):
            return "a module has no known verdict"
        lost = sorted(set(C.candidates(ROOT)) - set(mods))
        if lost:
            return "%d current candidates are not in it (%s)" % (len(lost), lost[:3])
        if not isinstance(rec.get("unhooked_children"), list) or not isinstance(rec.get("fixture_writes"), int):
            return "unhooked_children or fixture_writes is missing"
    except (OSError, TypeError, AttributeError) as e:
        return "it cannot be checked against the tree: %s: %s" % (type(e).__name__, e)
    return None


WHAT = "no writer of the old stores is left outside modledger"
if A.census:
    try:
        with open(A.census, encoding="utf-8") as f:
            rec = json.load(f)
        if not isinstance(rec, dict):
            raise ValueError("not a JSON object")
    except (OSError, ValueError) as e:
        rec = {"status": "could_not_look", "cause": "the census record %s cannot be read: %s" % (A.census, e)}
    why = whole(rec)
    if why:
        rec = {"status": "could_not_look", "cause": "the census record %s is not a whole census of this tree: %s"
               % (A.census, why)}
else:
    rec = C.census(ROOT)
if rec.get("status") != "ok":
    check(WHAT, False, rec.get("cause"), answer="COULD NOT LOOK")
else:
    mods = rec["modules"]
    writers = sorted(m for m, v in mods.items() if v["verdict"] == "WRITER")
    unmeasured = sorted(m for m, v in mods.items() if v["verdict"] == "NOT_MEASURED")
    seen = sum(1 for v in mods.values() if v["verdict"] == "NO_WRITE_SEEN")
    tests, unhooked = rec["tests"], rec["unhooked_children"]
    print("      census: %d tests (%d red, %d timed out, %d configured missing), %d fixture writes, %d Python children "
          "without the hook; %d writers, %d not measured, %d no write seen"
          % (len(tests), sum(1 for t in tests if t["rc"] not in (0, None)), sum(1 for t in tests if t["rc"] is None),
             len(rec.get("missing_tests") or []), rec["fixture_writes"], len(unhooked), len(writers),
             len(unmeasured), seen))
    for u in unhooked[:5]:
        print("      UNSEEN CHILD  %s, under %s (started from %s)" % (u.get("why"), u.get("test"),
                                                                    ", ".join(u.get("chain") or []) or "?"))
    for m in writers:
        e = mods[m]["example"]
        print("      WRITER        %s  (%d writes; e.g. %s %s under %s)" % (m, mods[m]["writes"], e["event"],
                                                                         os.path.basename(e["path"]) if e.get("path") else "an unresolved path",
                                                                         e["test"]))
    for m in unmeasured:
        print("      NOT MEASURED  %s  (never ran: %s)" % (m, "; ".join(mods[m]["never_ran"][:4])
                                                          + (" +%d" % (len(mods[m]["never_ran"]) - 4)
                                                             if len(mods[m]["never_ran"]) > 4 else "")))
    if writers:
        check(WHAT + " (%d writers measured)" % len(writers), False, writers[:12])
    elif unmeasured or unhooked:
        check(WHAT, False, "%d modules not measured: %s; %d Python children ran without the hook, unseen"
              % (len(unmeasured), unmeasured[:12], len(unhooked)), answer="NOT MEASURED")
    else:
        check(WHAT + " (%d modules seen, none writing)" % seen, True)
n = len(res)
if all(a == "PASS" for a in res):
    print("PASS %d/%d" % (n, n))
    sys.exit(0)
# a blind instrument outranks a fail, so its exit code is never read as an ordinary FAIL
print(", ".join("%s %d" % (a, res.count(a)) for a in ("COULD NOT LOOK", "FAIL", "NOT MEASURED") if a in res)
      + " of %d" % n)
sys.exit(next(code for a, code in (("COULD NOT LOOK", 3), ("FAIL", 1), ("NOT MEASURED", 2)) if a in res))
