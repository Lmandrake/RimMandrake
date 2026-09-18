#!/usr/bin/env python3
"""selftest_canon_census.py — the three-bucket classifier, on fixtures.

    python3 src/RimMandrake/Utils/selftest_canon_census.py

Builds a throwaway `canon_references/`-shaped tree in a temp dir (never
touches the real design/RimStarWars/canon_references/) and asserts:

  1. A `**RULED**` block classifies as "ruled".
  2. All FOUR known empty-boilerplate wordings measured on the real corpus
     (2026-09-17: "owner"/"the owner" x race/creature/species/chassis, plus
     one with an extra trailing sentence) classify as "unruled".
  3. A genuinely blank `## ruling` body classifies as "non-conforming"
     (the `zeer` shape).
  4. Free-form prose with no `**RULED**` marker classifies as "non-conforming"
     (the `gizka` shape) — this module's deliberate choice, see its
     docstring "THE GIZKA DECISION".
  5. `census()` totals and buckets agree across a small mixed fixture.
  6. `--lint` exits 1 iff there is at least one non-conforming entry, and 0
     otherwise.
  7. `--list <bucket>` prints exactly the slugs in that bucket.
"""
import io
import contextlib
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import canon_census as CC  # noqa: E402

FAILS = []


def eq(got, want, what):
    if got != want:
        FAILS.append("%s: got %r, want %r" % (what, got, want))


def make_entry(root, slug, ruling_body):
    d = os.path.join(root, slug)
    os.makedirs(d, exist_ok=True)
    text = (
        "# %s\n\n**defName**: `Fake_%s`\n\n"
        "## Sourced text (Wookieepedia)\nfake.\n\n"
        "## Visual brief\nfake.\n\n"
        "## Must show\n- [ ] fake\n\n"
        "## Engine limits\nnone known.\n\n"
        "## ruling\n%s\n"
    ) % (slug, slug, ruling_body)
    with open(os.path.join(d, "description.md"), "w", encoding="utf-8") as fh:
        fh.write(text)


def run_cli(*args):
    """Invoke main() as the CLI would, capturing stdout and the exit code."""
    old_argv = sys.argv
    buf = io.StringIO()
    sys.argv = ["canon_census.py"] + list(args)
    try:
        with contextlib.redirect_stdout(buf):
            try:
                rc = CC.main()
            except SystemExit as e:
                rc = e.code or 0
    finally:
        sys.argv = old_argv
    return rc, buf.getvalue()


TMP = tempfile.mkdtemp(prefix="canon_census_selftest_")

# ---- 1. RULED marker -------------------------------------------------------
make_entry(TMP, "ruled_one", "**RULED**\n2026-09-17, owner: fake ruling text.")

# ---- 2. every empty-boilerplate wording that really occurs -----------------
# MEASURED against the live corpus 2026-09-18: SEVEN distinct wordings across the
# 111 unruled entries, not the four the assessment claimed. They differ by
# "owner"/"the owner", by the noun (race/creature/species/chassis) and in one droid
# entry by a trailing sentence still inside the parens. Counts at that measurement:
# race 66, creature 19, the-owner-chassis 17, chassis 5, the-owner-race 2,
# the-owner-chassis-with-trailer 1, species 1.
WORDINGS = [
    "unruled_race", "(empty — owner has not reviewed this race yet)",
    "unruled_creature", "(empty — owner has not reviewed this creature yet)",
    "unruled_species", "(empty — owner has not reviewed this species yet)",
    "unruled_chassis", "(empty — the owner has not reviewed this chassis yet)",
    "unruled_chassis_short", "(empty — owner has not reviewed this chassis yet)",
    "unruled_race_the", "(empty — the owner has not reviewed this race yet)",
    "unruled_chassis_extra",
    "(empty — the owner has not reviewed this chassis yet. \U0001F534 extra "
    "trailing sentence still inside the parens.)",
    # Not in the corpus today, kept because the parser is shape-based and must not
    # start depending on the exact noun list.
    "unruled_species_the", "(empty — the owner has not reviewed this species yet)",
]
for slug, body in zip(WORDINGS[0::2], WORDINGS[1::2]):
    make_entry(TMP, slug, body)

# ---- 3. genuinely blank (zeer shape) ---------------------------------------
make_entry(TMP, "blank_one", "")

# ---- 4. free-form prose, no marker (gizka shape) ---------------------------
make_entry(
    TMP, "prose_one",
    '2026-09-16, owner: "Check your canon." Upheld on re-inspection: fake prose ruling.',
)

# ---- unit classify() checks -------------------------------------------------
eq(CC.classify("**RULED**\nsomething")[0], "ruled", "a body carrying **RULED** classifies ruled")
for slug, body in zip(WORDINGS[0::2], WORDINGS[1::2]):
    eq(CC.classify(body)[0], "unruled", "wording %r classifies unruled" % slug)
eq(CC.classify("")[0], "non-conforming", "a blank body classifies non-conforming")
eq(CC.classify(None)[0], "non-conforming", "a missing ## ruling heading classifies non-conforming")
prose = '2026-09-16, owner: "Check your canon." Upheld on re-inspection: fake prose ruling.'
bucket, reason = CC.classify(prose)
eq(bucket, "non-conforming", "free-form prose with no marker classifies non-conforming (gizka shape)")
eq(reason is not None and "RULED" in reason, True,
   "the non-conforming reason for free-form prose names the missing marker")

# ---- 5. census() totals and buckets on the mixed fixture -------------------
result = CC.census(TMP)
# Derived from the fixture list, not hardcoded: adding a real boilerplate wording is
# how this file stays honest, and a count that has to be edited by hand to do that
# turns a new wording into a test failure instead of new coverage.
N_UNRULED = len(WORDINGS) // 2
N_RULED, N_NONCONF = 1, 2
eq(result["total"], N_UNRULED + N_RULED + N_NONCONF,
   "census counts every fixture entry")
eq(len(result["ruled"]), N_RULED, "exactly one fixture entry is ruled")
eq(len(result["unruled"]), N_UNRULED,
   "every boilerplate wording fixture classifies unruled")
eq(len(result["non-conforming"]), 2, "exactly two fixture entries are non-conforming")
eq(sorted(s for s, _ in result["non-conforming"]), ["blank_one", "prose_one"],
   "the non-conforming bucket names exactly the blank and free-form-prose entries")
eq([s for s, _ in result["ruled"]], ["ruled_one"], "the ruled bucket names exactly the RULED entry")

# ---- 6. --lint exit code ----------------------------------------------------
rc, out = run_cli("--dir", TMP, "--lint")
eq(rc, 1, "--lint exits 1 while non-conforming entries exist")
eq("blank_one" in out, True, "--lint's output names the blank entry")
eq("prose_one" in out, True, "--lint's output names the free-form-prose entry")

clean_dir = tempfile.mkdtemp(prefix="canon_census_selftest_clean_")
make_entry(clean_dir, "ruled_two", "**RULED**\nfake.")
make_entry(clean_dir, "unruled_two", "(empty — owner has not reviewed this race yet)")
rc, out = run_cli("--dir", clean_dir, "--lint")
eq(rc, 0, "--lint exits 0 when every entry is ruled or unruled boilerplate")

# ---- 7. --list <bucket> -----------------------------------------------------
rc, out = run_cli("--dir", TMP, "--list", "ruled")
eq(out.strip(), "ruled_one", "--list ruled prints exactly the ruled slug")
rc, out = run_cli("--dir", TMP, "--list", "non-conforming")
lines = sorted(l.split("\t")[0] for l in out.strip().splitlines())
eq(lines, ["blank_one", "prose_one"], "--list non-conforming prints exactly those two slugs")

shutil.rmtree(TMP, ignore_errors=True)
shutil.rmtree(clean_dir, ignore_errors=True)

if FAILS:
    print("FAIL selftest_canon_census.py")
    for f in FAILS:
        print("  " + f)
    sys.exit(1)
print("ok  selftest_canon_census.py — ruled/unruled/non-conforming classification, "
      "all SEVEN real boilerplate wordings, gizka/zeer shapes, --lint and --list")
