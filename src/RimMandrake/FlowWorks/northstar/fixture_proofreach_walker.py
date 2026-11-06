#!/usr/bin/env python3
"""Release fixture for UNDERPASS_REACH_VERIFY_WALK_UNDER_FOR_REAL's HARNESS wait (PROOFREACH_FIX_PAWNLESS_READ_HAS_NO_WALKER).

RM_SuspensionProofs.ProofReach reports reachPawnless: the pawnless PassDoors CanReach vanilla Pawn_PathFollower.StartPath
asks before every walk. In the game StartPath's Harmony prefix (RM_Patch_PathFollower_ReachWalker) registers the walker
first, so the Superdeep veto judges that pawn's own view; a probe that asks the same read bare judges the default (deck)
grid and a floor pawn reads False. This reads ProofReach's source at --rev and judges whether that read is wrapped in
RM_Patch_PathFollower_ReachWalker.As(p, ...).

  --rev REV   a git revision (default HEAD); WORKTREE reads the file on disk
Prints FIXTURE_VERDICT: PASS (exit 0) | FAIL (exit 1); a source it cannot read prints UNMEASURED (exit 2), no verdict."""
import argparse
import os
import re
import subprocess
import sys

REL = "src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_SuspensionProofs.cs"
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))


def source(rev):
    if rev == "WORKTREE":
        with open(os.path.join(ROOT, REL), encoding="utf-8") as f:
            return f.read()
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (rev, REL)], capture_output=True, text=True)
    if r.returncode != 0:
        raise OSError(r.stderr.strip() or "git show failed")
    return r.stdout


def method_body(src, name):
    """The body of `public static string <name>(` up to its matching brace, or None."""
    m = re.search(r"public\s+static\s+string\s+%s\s*\(" % re.escape(name), src)
    if not m:
        return None
    i = src.find("{", m.end())
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[i:j + 1]
    return None


def judge(src):
    """-> (verdict, why). PASS only when the pawnless PassDoors CanReach that sets reachPawnless sits inside
    RM_Patch_PathFollower_ReachWalker.As(p, ...)."""
    body = method_body(src, "ProofReach")
    if body is None:
        return "FAIL", "no ProofReach method"
    code = "\n".join(l.split("//", 1)[0] for l in body.splitlines())
    m = re.search(r"bool\s+reachPawnless\s*=(.*?);", code, re.S)
    if not m:
        return "FAIL", "ProofReach sets no reachPawnless"
    expr = re.sub(r"\s+", " ", m.group(1)).strip()
    if "TraverseMode.PassDoors" not in expr or "CanReach(" not in expr:
        return "FAIL", "reachPawnless is not the pawnless PassDoors CanReach: %s" % expr
    w = re.match(r"RM_Patch_PathFollower_ReachWalker\.As\(\s*p\s*,\s*\(\)\s*=>", expr)
    if not w:
        return "FAIL", "the pawnless read has no walker registered: %s" % expr
    return "PASS", "the pawnless read runs inside RM_Patch_PathFollower_ReachWalker.As(p, ...)"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rev", default="HEAD")
    a = ap.parse_args(argv)
    try:
        src = source(a.rev)
    except OSError as e:
        print("UNMEASURED: cannot read %s at %s: %s" % (REL, a.rev, e))
        return 2
    verdict, why = judge(src)
    print("%s at %s: %s" % (REL, a.rev, why))
    print("FIXTURE_VERDICT: %s" % verdict)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
