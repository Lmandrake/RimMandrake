#!/usr/bin/env python3
"""selftest_testq_blocks.py - the testq blocks that map a past-blind mod's stage-6 checks to the chains SteveDesktop's
filler walks (testq_blocks.py; item RIMMANDRAKE_AUTHOR_TESTQ_BLOCKS_STEVE_SITS_IDLE_BY_RULE).

  python3 selftest_testq_blocks.py               every check; exit 1 on any failure
  python3 selftest_testq_blocks.py --mutant M    the same checks with guard M reverted: must exit 1
  python3 selftest_testq_blocks.py --mutants     run every mutant; exit 0 only if each one is caught

The fixture checks use a temp design/concepts tree and a stand-in suite. The REPO checks read the real tables: every mod
past blind has its derived blocks committed (the nightly recheck: a mod that reaches Stage 6 without them fails here),
and FlowWorks' first block is admitted by pipeline_admit. No queue, ssh, ledger or game is touched.
"""
import argparse
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REAL_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TMP = tempfile.mkdtemp(prefix="testq_blocks_")
ROOT = os.path.join(TMP, "repo")

import pipeline_admit as PA  # noqa: E402
import testq_blocks as B  # noqa: E402
import coverage as C  # noqa: E402

FAILS = []
MUTANTS = ("entry_rule", "driver_rule", "multi_driver_guard", "kind_guard", "hand_block_kept", "blind_guard",
           "layout_kept", "fill_walks_pipeline")


def check(ok, msg):
    print("%s  %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


FILE = "src/RimMandrake/Mod/northstar/x.py"
CHAINS = ["c_entry", "c_one", "c_a", "c_b"]
SCRIPTS = {"src/RimMandrake/Mod/northstar/one.py": ["c_one"], "src/RimMandrake/Mod/northstar/two.py": ["c_a", "c_b"]}
TESTS = {
    "sc_entry": {"stage": "6", "kind": "live_minimal", "entry": "c_entry", "file": FILE},
    "sc_driver": {"stage": "6", "kind": "live_minimal", "entry": "posts", "file": "src/RimMandrake/Mod/northstar/one.py"},
    "sc_two": {"stage": "6", "kind": "live_minimal", "entry": "x", "file": "src/RimMandrake/Mod/northstar/two.py"},
    "sc_full": {"stage": "6", "kind": "live_full", "entry": "c_entry", "file": FILE},
    "sc_scene": {"stage": "6", "kind": "live_minimal", "entry": "scene_x", "file": FILE},
    "sc_hand": {"stage": "6", "kind": "live_minimal", "entry": "scene_y", "file": FILE, "testq": {"rows": ["r_hand"]}},
    "sc_stale": {"stage": "6", "kind": "live_minimal", "entry": "gone", "file": FILE,
                 "testq": {"chains": ["c_gone"], "by": B.BY}},
    "T_OFF": {"stage": "4-5", "kind": "offline", "entry": "c_entry", "file": FILE},
}


def concept(mod, stage, ascii_layout=False, tests=None):
    d = os.path.join(ROOT, "design", "concepts", mod, "version")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "VERSION.json"), "w") as f:
        json.dump({"mod": mod, "version": "0.1.0", "state": "locked"}, f)
    with open(os.path.join(d, "stage_record.json"), "w") as f:
        json.dump({"mod": mod, "version": "0.1.0", "stage": stage}, f)
    tt = {"mod": mod, "version": "0.1.0", "note": "café", "tests": TESTS if tests is None else tests}
    with open(os.path.join(d, "test_table.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(tt, indent=1, ensure_ascii=ascii_layout) + ("" if ascii_layout else "\n"))


def run_checks():
    os.environ["TESTQ_PIPELINE_ROOT"] = ROOT
    got, why = B.derive("Mod", TESTS, CHAINS, SCRIPTS)
    check(got.get("sc_entry") == "c_entry", "an entry that IS a modcheck chain names that chain")
    check(got.get("sc_driver") == "c_one", "a file a one-chain live driver runs names that driver's chain")
    check(got.get("sc_two") is None and "2 chains" in why.get("sc_two", ""),
          "a driver serving several chains names none, and says so")
    check(got.get("sc_full") is None, "a live_full check is not SteveDesktop's (it runs the minimal tier)")
    check(got.get("sc_scene") is None and "no modcheck chain" in why.get("sc_scene", ""),
          "an entry no chain or driver runs is unmapped with its reason")
    check("T_OFF" not in got, "an offline (stage 4-5) entry is not a stage-6 check")

    for mod, stage, asc in (("Ready", "in_game", False), ("Ascii", "in_game", True), ("Blind", "blind_challenge", False)):
        concept(mod, stage, asc)
    B.suite_facts = lambda mod, root: (CHAINS, SCRIPTS)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = B.main(["apply", "Ready", "Ascii", "Blind"])
    check(rc == 2 and "REFUSED Blind" in out.getvalue(), "apply refuses a mod still at the blind challenge")
    tb = json.load(open(B.table_path(ROOT, "Blind"), encoding="utf-8"))["tests"]
    check("testq" not in tb["sc_entry"], "a blind-stage table is left as the judge saw it")
    tr = json.load(open(B.table_path(ROOT, "Ready"), encoding="utf-8"))["tests"]
    check(tr["sc_entry"].get("testq") == {"chains": ["c_entry"], "by": B.BY}, "apply writes the derived block")
    check(tr["sc_hand"].get("testq") == {"rows": ["r_hand"]}, "a hand-written block is never touched")
    check("testq" not in tr["sc_stale"], "a derived block whose chain no longer derives is dropped")
    for mod, asc in (("Ready", False), ("Ascii", True)):
        s = open(B.table_path(ROOT, mod), encoding="utf-8").read()
        check(s == json.dumps(json.loads(s), indent=1, ensure_ascii=asc) + ("" if asc else "\n"),
              "apply keeps %s's JSON layout (ensure_ascii %s), so the diff is the blocks only" % (mod, asc))
    check(PA.refusal("Ready", {"chains": ["c_entry", "c_one"]}, "BENCH.filler", ROOT) is None,
          "pipeline_admit admits the written chains")
    check(PA.refusal("Ready", {"chains": ["c_a"]}, "BENCH.filler", ROOT) is None,
          "a chain no block names is admitted too (owner 2026-11-17 dropped the 2026-11-14 pipeline-only limit)")
    with contextlib.redirect_stdout(io.StringIO()):
        check(B.main(["check"]) == 0, "check passes once every past-blind mod's blocks are written")
        concept("Late", "in_game", tests={k: {x: y for x, y in t.items() if x != "testq"} for k, t in TESTS.items()})
        check(B.main(["check"]) == 1, "check fails for a mod that reached Stage 6 with no blocks")
    os.environ.pop("TESTQ_FILL_MODS", None)
    fm = C.fill_mods()
    check("Ready" in fm and "Late" not in fm and "Blind" not in fm,
          "the tick's filler walks a past-blind mod with blocks, wired or not, and no other")

    # REPO: the real tables, read with the real suites
    os.environ["TESTQ_PIPELINE_ROOT"] = REAL_ROOT
    r = subprocess.run([sys.executable, os.path.join(HERE, "testq_blocks.py"), "check"], capture_output=True, text=True,
                       env=dict(os.environ, TESTQ_PIPELINE_ROOT=REAL_ROOT), timeout=120)
    check(r.returncode == 0, "REPO: every mod past blind has its derived testq blocks committed (%s)" % (
        (r.stdout.strip().splitlines() or ["no output"])[-1]))
    check(PA.refusal("FlowWorks", {"chains": ["plot_H_depth_ladder"]}, "BENCH.filler", REAL_ROOT) is None,
          "REPO: SteveDesktop may take FlowWorks' plot_H_depth_ladder (sc_dig_and_read)")


def apply_mutant(m):
    real_derive, real_wanted, real_dump, real_fill = B.derive, B.wanted, B.dump_like, C.pipeline_mods
    if m == "entry_rule":
        B.derive = lambda mod, t, chains, scripts: real_derive(mod, t, [], scripts)
    elif m == "driver_rule":
        B.derive = lambda mod, t, chains, scripts: real_derive(mod, t, chains, {})
    elif m == "multi_driver_guard":
        B.derive = lambda mod, t, chains, scripts: real_derive(mod, t, chains, {k: v[:1] for k, v in scripts.items()})
    elif m == "kind_guard":
        B.KINDS = ("live_minimal", "live_full")
    elif m == "hand_block_kept":
        B.BY = None
    elif m == "blind_guard":
        PA.PAST_BLIND = PA.PAST_BLIND + ("blind_challenge",)
    elif m == "layout_kept":
        B.dump_like = lambda obj, path: json.dumps(obj, indent=1, ensure_ascii=False) + "\n"
    elif m == "fill_walks_pipeline":
        C.pipeline_mods = lambda: []
    _ = (real_wanted, real_dump, real_fill)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutant", choices=MUTANTS)
    ap.add_argument("--mutants", action="store_true")
    a = ap.parse_args()
    if a.mutants:
        missed = []
        for m in MUTANTS:
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mutant", m], capture_output=True,
                               text=True, timeout=300)
            print("%s  mutant %s" % ("caught" if r.returncode else "MISSED", m))
            if not r.returncode:
                missed.append(m)
        print("%s: %d of %d mutants caught" % ("PASS" if not missed else "FAIL", len(MUTANTS) - len(missed), len(MUTANTS)))
        return 1 if missed else 0
    if a.mutant:
        apply_mutant(a.mutant)
    run_checks()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
