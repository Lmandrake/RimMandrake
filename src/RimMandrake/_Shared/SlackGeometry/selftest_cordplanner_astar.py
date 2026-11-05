#!/usr/bin/env python3
"""CORDPLANNER_ASTAR_SHRINK_TO_ZERO_ALLOC gate (hose/wire advisory 2026-10-28 §4 #4): CordPlanner's A* runs on reusable stamped
flat arrays and an indexed binary heap with a fixed (f, g, cell) tie-break, and returns the routes the old per-call
Dictionary + SortedSet search did (GSS must be identical on load).

    python3 src/RimMandrake/_Shared/SlackGeometry/selftest_cordplanner_astar.py            # check (no dotnet needed)
    python3 src/RimMandrake/_Shared/SlackGeometry/selftest_cordplanner_astar.py --record   # Windows host: run + record

S1 source: the A* half of CordPlanner.cs (comments stripped) names no Dictionary, SortedSet or HashSet; it holds a
   [ThreadStatic] scratch with Stamp/G/Came/Pos/Heap arrays and a heap ordered F, then G, then the cell.
S2 recorded run: the C# check (GimmeSomeSlack SelfTest AStarHeapChecks.cs: the old search kept verbatim as reference, a
   seeded random-world sweep, the stamp wrap, a 0-byte warmed AStarInto) runs only under dotnet.exe, a Windows program, so
   --record runs selftest_gimmesomeslack.py and writes LOG with the sha256 of CordPlanner.cs and AStarHeapChecks.cs. The
   check requires those hashes to match the tree (a stale log is red), H1/H2/H3 PASS, "N/N checks passed", run exit 0, and
   a can-fail probe (tie-break flipped in the heap) in which H1 FAILED.
Sanity: a planted `new Dictionary<Cell, double>` in the search is caught; a log with a wrong hash is refused.
Exit 0 PASS, 1 FAIL."""
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
PLANNER = os.path.join(HERE, "CordPlanner.cs")
CHECKS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "Source", "SelfTest", "AStarHeapChecks.cs")
LOG = "/mnt/d/ClaudeWork/rimmandrake/evidence/CORDPLANNER_ASTAR_SHRINK_TO_ZERO_ALLOC/gss_selftest.log"
GSS_SELFTEST = os.path.join(REPO, "src", "RimMandrake", "Utils", "selftest_gimmesomeslack.py")
TIE = "return k != 0 ? k < 0 : CellOf(a).CompareTo(CellOf(b)) < 0;"


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(re.sub(r'"(\\.|[^"\\])*"', '""', ln).split("//")[0] for ln in text.split("\n"))


def astar_half(text):
    """CordPlanner from its first line up to FindPath: the scratch, the heap, Search and the four A* entry points."""
    a, b = text.find("internal static class CordPlanner"), text.find("public static List<Cell> FindPath")
    return text[a:b] if 0 <= a < b else ""


def source_problems(text):
    code = astar_half(strip_comments(text))
    if not code:
        return ["CordPlanner.cs: the A* half (class start .. FindPath) was not found"]
    probs = ["the A* names %s (a per-call collection)" % t for t in ("Dictionary<", "SortedSet<", "HashSet<") if t in code]
    for need in ("[ThreadStatic]", "Stamp", "Came", "Pos", "Heap", "F[a].CompareTo(F[b])", "G[a].CompareTo(G[b])",
                 "CellOf(a).CompareTo(CellOf(b)) < 0", "private static bool Search(", "public static bool AStarInto(",
                 "public static bool AStarDiveInto("):
        if need not in code:
            probs.append("the A* lacks " + need)
    return probs


def log_problems(log, planner_sha, checks_sha):
    probs = []
    if "sha256 CordPlanner.cs %s" % planner_sha not in log:
        probs.append("log was not recorded on this CordPlanner.cs (sha256 %s)" % planner_sha[:12])
    if "sha256 AStarHeapChecks.cs %s" % checks_sha not in log:
        probs.append("log was not recorded on this AStarHeapChecks.cs (sha256 %s)" % checks_sha[:12])
    main, _, probe = log.partition("== probe: tie-break flipped")
    for h in ("H1", "H2", "H3"):
        if not re.search(r"^astar heap PASS %s " % h, main, re.M):
            probs.append("run: %s did not PASS" % h)
    if not re.search(r"^astar heap PASS H3 .* allocate 0 bytes", main, re.M):
        probs.append("run: the warmed searches did not allocate 0 bytes")
    m = re.search(r"^(\d+)/(\d+) checks passed$", main, re.M)
    if not m or m.group(1) != m.group(2):
        probs.append("run: GSS selftest not all checks passed (%s)" % (m.group(0) if m else "no total line"))
    if not re.search(r"^== run exit=0$", main, re.M):
        probs.append("run: GSS selftest exit was not 0")
    if not re.search(r"^astar heap FAIL H1 .*diverged [1-9]", probe, re.M):
        probs.append("probe: with the tie-break flipped H1 did not fail (the check cannot see a route change)")
    return probs


def record():
    with open(PLANNER, encoding="utf-8") as f:
        good = f.read()
    if TIE not in good:
        print("record: the tie-break line is not in CordPlanner.cs")
        return 1
    out = ["sha256 CordPlanner.cs " + sha(PLANNER), "sha256 AStarHeapChecks.cs " + sha(CHECKS)]
    r = subprocess.run([sys.executable, GSS_SELFTEST], cwd=REPO, capture_output=True, text=True, timeout=520)
    out += [r.stdout + r.stderr, "== run exit=%d" % r.returncode, "== probe: tie-break flipped"]
    try:
        with open(PLANNER, "w", encoding="utf-8", newline="") as f:
            f.write(good.replace(TIE, TIE.replace("< 0;", "> 0;")))
        p = subprocess.run([sys.executable, GSS_SELFTEST, "--no-export"], cwd=REPO, capture_output=True, text=True, timeout=520)
        out += [p.stdout + p.stderr, "== probe exit=%d" % p.returncode]
    finally:
        with open(PLANNER, "w", encoding="utf-8", newline="") as f:
            f.write(good)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("recorded " + LOG)
    return 0


def main(argv):
    if "--record" in argv:
        rc = record()
        if rc:
            return rc
    with open(PLANNER, encoding="utf-8") as f:
        text = f.read()
    probs = ["S1 " + p for p in source_problems(text)]
    if not os.path.exists(LOG):
        probs.append("S2 no recorded run at " + LOG + " (run --record on a Windows host)")
    else:
        with open(LOG, encoding="utf-8") as f:
            probs += ["S2 " + p for p in log_problems(f.read(), sha(PLANNER), sha(CHECKS))]
    planted = text.replace("Scratch s = scratch ??", "var leak = new Dictionary<Cell, double>(); Scratch s = scratch ??")
    if not any("Dictionary<" in p for p in source_problems(planted)):
        probs.append("sanity: a planted Dictionary in the search was not caught")
    if os.path.exists(LOG):
        with open(LOG, encoding="utf-8") as f:
            if not log_problems(f.read(), "0" * 64, sha(CHECKS)):
                probs.append("sanity: a log recorded on another CordPlanner.cs was accepted")
    print("cordplanner astar gate: %s" % ("PASS" if not probs else "FAIL"))
    for p in probs:
        print("  " + p)
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
