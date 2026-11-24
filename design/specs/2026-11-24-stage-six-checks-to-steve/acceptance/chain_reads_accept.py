#!/usr/bin/env python3
"""Outcome check of RIMMANDRAKE_DECLARE_READS_OF_GUARD_CHAINS_LEAVE_PASSED_CHANGES_NOTHING, on the live tables and real history.

The record is wasted_reruns.json: each filler rerun, 2026-11-17..24, of a passed chain at another code version that passed
again (236). The most-rerun chains are the 62 that it holds twice or more. Three things hold:
  read    each most-rerun chain has a readable relation (gaps.untouched is not None) at its last rerun
  spared  at least SPARED of those 62 last reruns are untouched: they would not run again
  again   each declared chain runs again when C# it declares is changed (a planted commit on HEAD), and stands when C# that
          none of them declares is changed
`--all` counts every one of the 236 (about 10 minutes). Exit 0 holds, 1 fails, 2 could not look."""
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TQ = os.path.join(REPO, "src", "RimMandrake", "Utils", "testq")
os.environ["TESTQ_QUEUE"] = tempfile.mkdtemp(prefix="chain_reads_")      # no kept answer of the live queue
sys.path.insert(0, TQ)
import gaps as G  # noqa: E402

SPARED = 30
CORE = {"FlowWorks": {"plot_C_limitless_canal": "RM_FlowKernel.cs", "plot_C2_tar_and_fluids": "RM_FluidIdentity.cs",
                      "plot_D_limited_pond": "RM_LiquidBody.cs", "plot_E_fire": "RM_LiquidFire.cs", "plot_F_slime": "RM_SlimeSlip.cs",
                      "liquid_pump": "LiquidTypes/Building_LiquidPump.cs", "taken_by_land": "TakenByLand/RM_TakenByLand.cs",
                      "pit_exposure": "RM_PitExposure.cs"},
        "Pyrelands": {"firehawk_mapwide_carry": "JobGiver_RUT_FireHawkCarryEmber.cs"}}
NOBODY = {"FlowWorks": "Pits/Drawbridge/RM_DrawbridgeArt.cs", "Pyrelands": "PyrelandsWetRoots.cs"}


def plant(paths):
    """-> a commit on HEAD, reachable from no branch, with a field added to the first class of each file; None: could not."""
    env = dict(os.environ, GIT_INDEX_FILE=os.path.join(os.environ["TESTQ_QUEUE"], "index"), GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")

    def run(*a, **k):
        return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, env=env, check=True, **k).stdout
    run("read-tree", "HEAD")
    for p in paths:
        src = run("show", "HEAD:" + p)
        out = re.sub(r"(\bclass \w+[^{;]*\{)", r"\1 public int plantedByCheck;", src, count=1)
        if out == src:
            return None
        run("update-index", "--cacheinfo", "100644,%s,%s" % (run("hash-object", "-w", "--stdin", input=out).strip(), p))
    return run("commit-tree", run("write-tree").strip(), "-p", "HEAD", "-m", "planted").strip()


def reads_of(mod):
    r = subprocess.run([sys.executable, os.path.join(TQ, "gapprobe.py")], capture_output=True, text=True,
                       input=json.dumps({"mod": mod, "only": "reads"}))
    try:
        return json.loads(r.stdout.strip().splitlines()[-1]).get("reads")
    except (ValueError, IndexError):
        return None


def ask(mod, chain, old, new, reads):
    if len(G._REL) > 2:
        G._REL.clear()
    try:
        return G.untouched(mod, chain, old, new, mod_reads=reads)
    except TypeError:           # the build before: no mod_reads
        return G.untouched(mod, chain, old, new)


def main():
    rows = json.load(open(os.path.join(HERE, "wasted_reruns.json"), encoding="utf-8"))["reruns"]
    if G.git("cat-file", "-e", rows[-1]["new"]) is None:
        print("COULD NOT LOOK: %s is not in this repository's history" % rows[-1]["new"])
        return 2
    n = Counter((r["mod"], r["chain"]) for r in rows)
    if "--all" not in sys.argv:
        rows = [r for r in {(r["mod"], r["chain"]): r for r in rows}.values() if n[r["mod"], r["chain"]] >= 2]
    mods = sorted({r["mod"] for r in rows})
    with ThreadPoolExecutor(6) as ex:
        reads = dict(zip(mods, ex.map(reads_of, mods)))
    ans, bad = [], []
    for r in rows:
        ans.append(ask(r["mod"], r["chain"], r["old"], r["new"], reads[r["mod"]]))
    last = {(r["mod"], r["chain"]): a for r, a in zip(rows, ans)}
    blind = sorted(k for k, a in last.items() if n[k] >= 2 and a is None)
    if blind:
        bad.append("read: %d of %d most-rerun chains have no readable relation: %s" % (
            len(blind), sum(c >= 2 for c in n.values()), ", ".join("%s/%s" % k for k in blind[:8])))
    spared = sum(a is True for k, a in last.items() if n[k] >= 2)
    if spared < SPARED:
        bad.append("spared: %d of %d most-rerun chains' last reruns, fewer than %d" % (spared, sum(c >= 2 for c in n.values()), SPARED))
    for mod, chains in CORE.items():
        specs = getattr(G, "chain_specs", lambda *a: {})(mod, G.stage6_tests(mod) or {})
        src = "src/RimMandrake/%s/Source/" % mod
        hit, other = plant(sorted({src + c for c in chains.values()})), plant([src + NOBODY[mod]])
        if not hit or not other:
            print("COULD NOT LOOK: no class to plant in for %s" % mod)
            return 2
        for c in chains:
            if c not in specs:
                bad.append("again: %s/%s is not declared" % (mod, c))
                continue
            got = ask(mod, c, "HEAD", hit, reads[mod]), ask(mod, c, "HEAD", other, reads[mod])
            if got != (False, True):
                bad.append("again: %s/%s answers %s to a change of %s, and to one of %s" % (mod, c, got, chains[c], NOBODY[mod]))
    for b in bad:
        print("FAIL " + b)
    print("%s: of %d wasted reruns read, %d spared, %d run again (touched), %d unreadable" % (
        "FAIL" if bad else "PASS", len(rows), sum(a is True for a in ans), sum(a is False for a in ans), sum(a is None for a in ans)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
