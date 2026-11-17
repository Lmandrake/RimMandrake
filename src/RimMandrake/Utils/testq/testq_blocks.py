#!/usr/bin/env python3
"""testq/testq_blocks.py - write the `testq` blocks that map a mod's stage-6 checks to the modcheck chains SteveDesktop
runs (item RIMMANDRAKE_AUTHOR_TESTQ_BLOCKS_STEVE_SITS_IDLE_BY_RULE). coverage.pipeline_mods walks every past-blind mod
whose blocks name a chain, so a mod reaching Stage 6 is filled without being wired by hand; admission does not read the
blocks (the owner dropped the 2026-11-14 pipeline-only limit on 2026-11-17). This derives them from what modcheck
already runs, by one rule, no judgement:

  a stage-6 entry of kind live_minimal (SteveDesktop runs modcheck's minimal tier) names chain C when
    1. its `entry` IS a chain of the mod's modcheck suite (FlowWorks' extensions, Pyrelands' validation chains), or
    2. its `file` is the script of a live driver (suite.live_drivers) that serves exactly ONE chain, which is C.
  Anything else (concept_scenes.py, a C# proof, a driver serving several chains) gets no block and is listed as
  unmapped with its reason: it runs on Archmagi in the visit, or a chain is built for it first.

A derived block carries "by": "testq_blocks.py" and is rewritten on every apply; a block without that mark was written
by hand and is never touched. Blocks are written only for mods pipeline_admit.standing() already counts as past the
blind challenge (a blind-stage table stays as the judge saw it).

  testq_blocks.py derive MOD        the mapping, one line per stage-6 entry (read-only)
  testq_blocks.py apply MOD...      write the derived blocks into design/concepts/MOD/version/test_table.json
  testq_blocks.py check [MOD...]    exit 1 when a past-blind mod's committed blocks differ from the derivation
                                    (default: every mod past blind); selftest_testq_blocks.py runs it nightly
Selftest: selftest_testq_blocks.py.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pipeline_admit as PA  # noqa: E402

BY = "testq_blocks.py"
KINDS = ("live_minimal",)


def suite_facts(mod, root):
    """-> (chain names, {driver script repo-relative: [chains]}) of MOD's modcheck suite, read offline."""
    mc = os.path.join(root, "src", "RimMandrake", "Utils", "modcheck")
    if mc not in sys.path:
        sys.path.insert(0, mc)
    import runner
    d = os.path.join(root, "src", "RimMandrake", mod)
    if not os.path.isdir(d):
        d = runner.find_mod_dir(mod)
    suite = runner.load_validation(d)
    chains = [n for n, _ in suite.chains]
    rel = os.path.relpath(d, root)
    scripts = {}
    for drv in getattr(suite, "live_drivers", None) or []:
        if drv.get("script"):
            p = os.path.normpath(os.path.join(rel, drv["script"])).replace(os.sep, "/")
            scripts.setdefault(p, []).extend(drv.get("chains") or [])
    return chains, scripts


def derive(mod, tests, chains, scripts):
    """-> {test id: chain or None}, {test id: why unmapped}, over the stage-6 entries of TESTS."""
    got, why = {}, {}
    for tid, t in tests.items():
        if not isinstance(t, dict) or str(t.get("stage")) not in PA.BAR_STAGES:
            continue
        if t.get("kind") not in KINDS:
            got[tid], why[tid] = None, "kind %s: SteveDesktop runs the minimal tier" % t.get("kind")
            continue
        entry, f = t.get("entry"), (t.get("file") or "").replace("\\", "/")
        if entry in chains:
            got[tid] = entry
            continue
        served = sorted(set(scripts.get(os.path.normpath(f).replace(os.sep, "/")) or []))
        if len(served) == 1:
            got[tid] = served[0]
        else:
            got[tid] = None
            why[tid] = ("%s's driver serves %d chains (%s)" % (f, len(served), ",".join(served)) if served else
                        "entry %s of %s is no modcheck chain and no live driver runs that file" % (entry, f))
    return got, why


def table_path(root, mod):
    return os.path.join(root, "design", "concepts", mod, "version", "test_table.json")


def load(root, mod):
    with open(table_path(root, mod), encoding="utf-8") as f:
        return json.load(f)


def dump_like(obj, path):
    """-> OBJ as JSON in the layout PATH already has (the tables' makers differ in ensure_ascii and the last newline),
    so an apply's diff is the blocks and nothing else."""
    with open(path, encoding="utf-8") as f:
        s = f.read()
    old = json.loads(s)
    for ea in (False, True):
        for nl in ("\n", ""):
            if json.dumps(old, indent=1, ensure_ascii=ea) + nl == s:
                return json.dumps(obj, indent=1, ensure_ascii=ea) + nl
    return json.dumps(obj, indent=1, ensure_ascii=False) + "\n"


def blocks_of(tt):
    """-> {test id: its testq block} as committed."""
    return {k: t.get("testq") for k, t in (tt.get("tests") or {}).items() if isinstance(t, dict) and t.get("testq")}


def wanted(tt, got):
    """-> TT's tests with every derived block set to GOT (hand blocks kept, stale derived ones dropped)."""
    out = {}
    for k, t in (tt.get("tests") or {}).items():
        if not isinstance(t, dict):
            out[k] = t
            continue
        t = dict(t)
        hand = isinstance(t.get("testq"), dict) and t["testq"].get("by") != BY
        if not hand:
            t.pop("testq", None)
            if got.get(k):
                t["testq"] = {"chains": [got[k]], "by": BY}
        out[k] = t
    return out


def plan(mod, root=None):
    """-> {"mod", "standing", "got", "why", "tt", "tests"}; standing is pipeline_admit's (entry, why-not)."""
    root = root or PA.repo_root()
    st = PA.standing(mod, root)
    tt = load(root, mod)
    chains, scripts = suite_facts(mod, root)
    got, why = derive(mod, tt.get("tests") or {}, chains, scripts)
    return {"mod": mod, "standing": st, "got": got, "why": why, "tt": tt, "tests": wanted(tt, got)}


def cmd_derive(a):
    p = plan(a.mod)
    for k, c in p["got"].items():
        print("  %-28s %s" % (k, c if c else "-  " + p["why"][k]))
    n = sum(1 for c in p["got"].values() if c)
    print("%s: %d of %d stage-6 checks name a chain SteveDesktop can run%s" % (
        a.mod, n, len(p["got"]), "" if p["standing"][0] else "; NOT past blind: " + p["standing"][1]))
    return 0


def cmd_apply(a):
    rc = 0
    for mod in a.mods:
        root = PA.repo_root()
        p = plan(mod, root)
        if p["standing"][0] is None:
            print("REFUSED %s: %s (blocks are written only past the blind challenge)" % (mod, p["standing"][1]))
            rc = 2
            continue
        tt = dict(p["tt"], tests=p["tests"])
        n = sum(1 for c in p["got"].values() if c)
        if tt == p["tt"]:
            print("%s: %d blocks already current" % (mod, n))
            continue
        text = dump_like(tt, table_path(root, mod))
        with open(table_path(root, mod), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print("%s: wrote %d testq blocks into %s" % (mod, n, os.path.relpath(table_path(root, mod), root)))
    return rc


def cmd_check(a):
    root = PA.repo_root()
    mods = a.mods or sorted(PA.qualifying(root))
    bad = []
    for mod in mods:
        p = plan(mod, root)
        if p["standing"][0] is None:
            continue
        if p["tests"] != (p["tt"].get("tests") or {}):
            n = sum(1 for c in p["got"].values() if c)
            have = sum(1 for b in blocks_of(p["tt"]).values() if isinstance(b, dict) and b.get("by") == BY)
            bad.append("%s: %d derivable blocks, %d committed (run `python3 src/RimMandrake/Utils/testq/testq_blocks.py "
                       "apply %s` and publish its test_table.json)" % (mod, n, have, mod))
    for b in bad:
        print("STALE " + b)
    print("%s: %d past-blind mod(s) checked, %d stale" % ("FAIL" if bad else "PASS", len(mods), len(bad)))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    d = sp.add_parser("derive")
    d.add_argument("mod")
    d.set_defaults(fn=cmd_derive)
    w = sp.add_parser("apply")
    w.add_argument("mods", nargs="+")
    w.set_defaults(fn=cmd_apply)
    c = sp.add_parser("check")
    c.add_argument("mods", nargs="*")
    c.set_defaults(fn=cmd_check)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
