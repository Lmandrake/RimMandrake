#!/usr/bin/env python3
"""selftest_codebase_health.py — the colour rules of codebase_health.py, offline.

    python3 src/RimMandrake/Utils/selftest_codebase_health.py

⛔ TOUCHES NOTHING. No git call, no ledger read, no file written. It imports
codebase_health.py and exercises the four pure decisions the picture rests on:

  1. PRECEDENCE. Red must beat blue, green and grey; a review-clean file named
     by an open bug is red, not green. Everything on the page is wrong if this
     inverts, and it is exactly the kind of ordering a refactor silently flips.

  2. UNKNOWN IS NOT GREY. Grey asserts "measured, and dirty". When git could
     not be consulted, or a recorded review sha no longer resolves, or the file
     is not decodable, the answer must be UNMEASURED. This repo has been bitten
     repeatedly by a tool reporting a confident wrong state, so a regression
     that folds unknown into grey must fail loudly here.

  3. A TOKEN NAMES A FILE ONLY IF IT UNAMBIGUOUSLY IS ONE. An invented
     bug-to-file mapping is worse than no mapping: two files sharing a basename
     must resolve to neither, and a path that does not exist must resolve to
     nothing at all.

  4. PROSE FILTERING. An item's `verify` / `criteria` sections name the tool
     that CHECKS the bug; reading them painted validate_patch.py red on someone
     else's defect. Likewise `python3 foo.py` and `foo.py --flag` are a command
     being run, not the subject of the item.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import codebase_health as ch  # noqa: E402

FAILS = []


def eq(got, want, what):
    if got != want:
        FAILS.append("%s: got %r, want %r" % (what, got, want))


def classify(**kw):
    """classify() with everything known and nothing set, unless overridden."""
    args = dict(path="a.py", loc_measured=True, uncommitted=set(), doing_files={},
                bug_files={}, verdict="dirty", wt_known=True, ledger_known=True)
    args.update(kw)
    return ch.classify(**args)[0]


# ---- 1. precedence -------------------------------------------------------
eq(classify(bug_files={"a.py": ["X_1"]}), "red", "bug alone is red")
eq(classify(bug_files={"a.py": ["X_1"]}, verdict="clean"), "red",
   "RED BEATS GREEN — a review-clean file named by an open bug is red")
eq(classify(bug_files={"a.py": ["X_1"]}, uncommitted={"a.py"}), "red",
   "RED BEATS BLUE")
eq(classify(bug_files={"a.py": ["X_1"]}, loc_measured=False), "red",
   "RED BEATS UNMEASURED — a known bug is known whatever else is not")
eq(classify(uncommitted={"a.py"}, verdict="clean"), "blue",
   "BLUE BEATS GREEN — uncommitted work invalidates a clean mark")
eq(classify(doing_files={"a.py": ["X_1"]}), "blue", "an open `doing` item is blue")
eq(classify(verdict="clean"), "green", "clean review with no other signal is green")
eq(classify(), "grey", "the default, measured, is grey")

# ---- 2. unknown is never grey -------------------------------------------
eq(classify(wt_known=False), "unmeasured", "git status unreadable -> UNMEASURED")
eq(classify(ledger_known=False), "unmeasured", "ledger unreplayable -> UNMEASURED")
eq(classify(verdict="unknown"), "unmeasured", "stale review sha -> UNMEASURED")
eq(classify(loc_measured=False), "unmeasured", "undecodable file -> UNMEASURED")
eq(classify(wt_known=False, verdict="clean"), "unmeasured",
   "a clean mark does not rescue an undetermined working tree")
for bad in ("wt_known", "ledger_known"):
    eq(classify(**{bad: False}) == "grey", False, "%s=False must never be grey" % bad)

# ---- 3. a token names a file only if it unambiguously is one -------------
PATHS = {"src/a/util.py", "src/b/util.py", "src/a/only.py", "top.py"}
BASE, SUF = ch.build_index(PATHS)
res = lambda t: ch.resolve_token(t, PATHS, BASE, SUF)      # noqa: E731
eq(res("src/a/util.py"), "src/a/util.py", "exact path resolves")
eq(res("./src/a/util.py"), "src/a/util.py", "a leading ./ is stripped")
eq(res("a/only.py"), "src/a/only.py", "a unique path fragment resolves")
eq(res("only.py"), "src/a/only.py", "a unique basename resolves")
eq(res("util.py"), None, "AMBIGUOUS basename resolves to nothing — never a guess")
eq(res("does/not/exist.py"), None, "a non-existent path names nothing")
eq(res("top.py"), "top.py", "a root-level file resolves")

# ---- 4. prose filtering --------------------------------------------------
MD = """Preamble names `src/a/only.py`.

## spec
The defect is in `src/b/util.py`.

## verify
Run `top.py` and check.

## criteria
- [ ] `src/a/util.py` is unchanged.

## Watch out
`src/a/util.py` lies about this.
"""
kept = ch.descriptive_prose(MD)
eq("only.py" in kept, True, "preamble is kept")
eq("src/b/util.py" in kept, True, "the spec section is kept")
eq("top.py" in kept, False, "the verify section is DROPPED")
eq(kept.count("src/a/util.py"), 0, "criteria and watch-out sections are DROPPED")

for blob, why in (
    ("python3 deploy.py --mod X", "python3 <tool> is an invocation"),
    ("ran deploy.py --apply now", "<tool> --flag is an invocation"),
):
    m = ch.PATH_TOKEN.search(blob)
    eq(ch.is_invocation(blob, m.start(), m.end()), True, why)
for blob, why in (
    ("the bug lives in deploy.py and nowhere else", "a bare mention is not an invocation"),
    ("deploy.py: 1/1 match, 0 errors", "a result line is not an invocation"),
):
    m = ch.PATH_TOKEN.search(blob)
    eq(ch.is_invocation(blob, m.start(), m.end()), False, why)

# ---- shape checks --------------------------------------------------------
eq(sorted(ch.STATUSES), sorted(["red", "blue", "green", "grey", "unmeasured"]),
   "the five statuses the page's legend documents")
eq(all(os.path.isfile(os.path.join(ch.VENDOR, n)) for n in
       ("d3.min.js", "d3-weighted-voronoi.min.js",
        "d3-voronoi-map.min.js", "d3-voronoi-treemap.min.js")), True,
   "all four vendored browser libraries are present to inline")

if FAILS:
    print("FAIL selftest_codebase_health.py")
    for f in FAILS:
        print("  " + f)
    sys.exit(1)
print("ok  selftest_codebase_health.py — precedence, unknown-is-not-grey, "
      "path resolution, prose filtering")
