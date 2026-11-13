#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_BUILD_PREFLIGHT_SPINE_TIMED_FROM_BIRTH (spec:
design/specs/2026-11-12-ticket-preflight-before-any-token.md, section 7 ticket 1). Written by the filing seat; the
builder does not edit it (a wrong clause goes to the Conductor, per the refusal-contract rule).

    python3 src/RimMandrake/rimflow/acceptance/preflight_spine_accept.py      # exit 0 and "PASS 30/30" when built

THE CONTRACT IT FIXES (the ticket body states the same):
    import ticket_preflight as TP          # src/RimMandrake/rimflow/ticket_preflight.py
    TP.run_text(text, proof_text="", *, item_id="ACCEPT", trigger="pickup", paths=None, defs=None, src=None,
                tiers=None, deadline_s=5.0, runs_path=None) -> dict
  paths  repo-relative tracked paths, or a zero-arg callable returning them (None: `git ls-files`)
  defs   a defindex raw dict {"capture", "mods", "defs": [[type, name, hash, pkg]]}, or a callable (None: the newest
         CACHED index; none cached reads UNMEASURED, the door never builds one)
  src    {defName: [[type, pkg]]}, or a callable (None: defindex.src_defs())
  tiers  {tier: [packageId]}, or a callable (None: modset_builder's tiers)
  result {"item", "trigger", "run_id", "total_ms", "cut_off", "checks": [{"id", "ref", "status", "ms", "evidence",
         "fix"}]}, status one of PASS / FAIL / UNMEASURED; `ref` is the declared value checked.
  Only `## refs` lines (file:, new:, def:, tier:) and the proof text's `live-tier:` line are read. Prose is not.
  Every run appends one JSON line to runs_path (None: $RIMFLOW_PREFLIGHT_RUNS, else
  ~/.local/state/rimmandrake/preflight/runs.jsonl) with run_id, item, trigger, total_ms, cut_off, checks[{id, ms,
  status}]. Report-only: nothing raises on a FAIL, and the CLI exits 0.
"""
import ast
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RIMFLOW, "..", "..", ".."))
sys.path.insert(0, RIMFLOW)
CLI = os.path.join(RIMFLOW, "cli.py")
ITEM = "RIMMANDRAKE_BUILD_PREFLIGHT_SPINE_TIMED_FROM_BIRTH"

RESULTS = []


def check(ok, what):
    RESULTS.append((bool(ok), what))
    print(("ok    " if ok else "FAIL  ") + what)


PATHS = ["src/A/real.py", "src/A/other.py", "design/x.md"]
DEFS = {"capture": "T", "mods": ["pkg.a", "pkg.b"],
        "defs": [["ThingDef", "RM_OnList", 1, "pkg.a"], ["ThingDef", "RM_OffList", 2, "pkg.b"],
                 ["PawnKindDef", "RM_Kind", 3, "pkg.a"]]}
SRC = {"RM_Ours": [["ThingDef", "pkg.a"]]}
TIERS = {"small": ["pkg.a"], "wide": ["pkg.a", "pkg.notdumped"]}


def refs(*lines):
    return "## spec\nA ticket.\n\n## refs\n" + "\n".join(lines) + "\n"


def obs(rep, cid, ref=None):
    return [c for c in rep["checks"] if c["id"] == cid and (ref is None or c.get("ref") == ref)]


def status(rep, cid, ref=None):
    return {c["status"] for c in obs(rep, cid, ref)}


def main():
    tmp = tempfile.mkdtemp(prefix="preflight_accept_")
    runs = os.path.join(tmp, "runs.jsonl")
    n_runs = [0]

    def run(text, proof_text="", **kw):
        kw.setdefault("paths", PATHS)
        kw.setdefault("defs", DEFS)
        kw.setdefault("src", SRC)
        kw.setdefault("tiers", TIERS)
        kw.setdefault("runs_path", runs)
        n_runs[0] += 1
        return TP.run_text(text, proof_text, **kw)

    try:
        import ticket_preflight as TP
    except Exception as e:
        print("FAIL  import ticket_preflight: %s: %s" % (type(e).__name__, e))
        print("PASS 0/30")
        return 1

    cases = []

    def case(fn):
        cases.append(fn)
        return fn

    @case
    def paths_real_missing_new():
        r = run(refs("file: src/A/real.py", "file: src/A/missing.py", "new: src/A/brandnew.py"))
        check(status(r, "B1", "src/A/real.py") == {"PASS"}, "B1 a tracked path reads PASS")
        miss = obs(r, "B1", "src/A/missing.py")
        check(miss and miss[0]["status"] == "FAIL", "B1 an untracked path reads FAIL")
        check(miss and miss[0].get("fix"), "B1 FAIL carries a proposed fix")
        check("FAIL" not in status(r, "B1", "src/A/brandnew.py") and obs(r, "B1", "src/A/brandnew.py"),
              "B1 a declared new: path is checked and not FAIL")

    @case
    def def_on_off_ours_nowhere():
        r = run(refs("def: ThingDef/RM_OnList", "def: RM_OffList", "def: RM_Ours", "def: RM_Nowhere", "tier: small"))
        check(status(r, "C1", "small") == {"PASS"}, "C1 a real tier reads PASS")
        check(status(r, "B4", "RM_OnList") == {"PASS"} and status(r, "C2", "RM_OnList") == {"PASS"},
              "B4+C2 a dumped def on the list reads PASS")
        off = obs(r, "C2", "RM_OffList")
        check(status(r, "B4", "RM_OffList") == {"PASS"} and off and off[0]["status"] == "FAIL",
              "C2 a real def whose mod is off the list reads FAIL")
        check(off and "pkg.b" in ((off[0].get("fix") or "") + (off[0].get("evidence") or "")),
              "C2 FAIL names the owning mod")
        check("FAIL" not in status(r, "B4", "RM_Ours") and obs(r, "B5", "RM_Ours"),
              "B5 a src-only def is 'ours, not loaded yet', never a B4 FAIL")
        check(status(r, "C2", "RM_Ours") == {"PASS"}, "C2 a src def of a listed package reads PASS")
        check(status(r, "B4", "RM_Nowhere") == {"FAIL"}, "B4 a def known nowhere reads FAIL")
        check("PASS" not in status(r, "C2", "RM_Nowhere"), "C2 a def known nowhere is not PASS")

    @case
    def tiers_and_dump_list():
        r = run(refs("tier: nosuch"))
        check(status(r, "C1", "nosuch") == {"FAIL"}, "C1 an unknown tier reads FAIL")
        r = run(refs("def: RM_Nowhere", "tier: wide"))
        c10 = obs(r, "C10")
        check(c10 and c10[0]["status"] == "FAIL" and "pkg.notdumped" in (c10[0].get("evidence") or ""),
              "C10 a list holding an undumped mod reads FAIL naming it")
        check(status(r, "B4", "RM_Nowhere") == {"UNMEASURED"}, "C10 turns a 'missing' def into UNMEASURED")
        r = run(refs("def: RM_OnList", "tier: small"))
        check(status(r, "C10") == {"PASS"}, "C10 a fully dumped list reads PASS")

    @case
    def proof_file_tier():
        r = run(refs("def: RM_OffList", "def: RM_OnList"), proof_text="live-tier: small\n")
        check(status(r, "C2", "RM_OffList") == {"FAIL"} and status(r, "C2", "RM_OnList") == {"PASS"},
              "C2 reads the list from the proof file's live-tier line")

    @case
    def malformed_and_prose():
        r = run(refs("def ThingDef/RM_OnList", "dfe: RM_OnList"))
        bad = [c for c in r["checks"] if c["status"] != "PASS" and "line" in (c.get("evidence") or "").lower()]
        check(len(bad) >= 2, "a line with no key and a line with an unknown key are each reported with its line")
        r = run("## spec\nSee `src/A/missing.py` and RM_Nowhere.\n")
        check(not [c for c in r["checks"] if c["status"] == "FAIL"], "prose mentions are not read (no FAIL)")
        r = run("")
        check(isinstance(r.get("total_ms"), (int, float)) and isinstance(r.get("checks"), list)
              and not [c for c in r["checks"] if c["status"] == "FAIL"], "an empty ticket returns a clean report")

    @case
    def blind_instruments():
        def broken():
            raise OSError("git ls-files exited 128")
        r = run(refs("file: src/A/real.py"), paths=broken)
        check(status(r, "B1", "src/A/real.py") == {"UNMEASURED"}, "B1 a failed git call reads UNMEASURED")

        def stuck():
            time.sleep(30)
            return PATHS
        t = time.monotonic()
        r = run(refs("file: src/A/real.py", "def: RM_OnList", "tier: small"), paths=stuck, deadline_s=2.0)
        wall = time.monotonic() - t
        check(wall < 8.0, "the deadline is real: a 30 s stuck index returns in %.1f s" % wall)
        check(status(r, "B1", "src/A/real.py") == {"UNMEASURED"} and r.get("cut_off") is True,
              "a deadline expiry reads UNMEASURED and cut_off")

    @case
    def timing_lines():
        lines = [json.loads(l) for l in open(runs)] if os.path.exists(runs) else []
        check(len(lines) == n_runs[0], "one timing line per run (%d lines, %d runs)" % (len(lines), n_runs[0]))
        check(lines and all({"run_id", "item", "trigger", "total_ms", "checks"} <= set(l) for l in lines),
              "every timing line carries run_id, item, trigger, total_ms, checks")
        check(len({l.get("run_id") for l in lines}) == len(lines), "run ids are unique")

    @case
    def cli_and_doors():
        env = dict(os.environ, RIMFLOW_PREFLIGHT_RUNS=os.path.join(tmp, "cli_runs.jsonl"))
        h = subprocess.run([sys.executable, CLI, "preflight", "--help"], cwd=REPO, env=env,
                           capture_output=True, text=True, timeout=60)
        check(h.returncode == 0, "rimflow preflight --help exits 0")
        p = subprocess.run([sys.executable, CLI, "preflight", ITEM, "--json"], cwd=REPO, env=env,
                           capture_output=True, text=True, timeout=120)
        try:
            rep = json.loads(p.stdout)
        except ValueError:
            rep = {}
        check(p.returncode == 0 and isinstance(rep.get("total_ms"), (int, float)),
              "rimflow preflight <real item> --json exits 0 with total_ms (report-only)")
        got = open(env["RIMFLOW_PREFLIGHT_RUNS"]).read().splitlines() if os.path.exists(env["RIMFLOW_PREFLIGHT_RUNS"]) else []
        check(len(got) == 1, "the CLI run wrote exactly one timing line")
        src = open(CLI).read()
        tree = ast.parse(src)
        door = [ast.get_source_segment(src, n) for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name in ("cmd_claim", "cmd_file")]
        others = [open(os.path.join(RIMFLOW, f)).read() for f in ("relentless.py", "detached_helper.py")]
        check(len(door) == 2 and not any("ticket_preflight" in d for d in door + others),
              "no door is touched: cmd_claim, cmd_file, relentless.py, detached_helper.py never call ticket_preflight")

    for fn in cases:
        try:
            fn()
        except Exception as e:
            check(False, "%s crashed: %s: %s" % (fn.__name__, type(e).__name__, e))
    passed = sum(1 for ok, _ in RESULTS if ok)
    total = 30
    print("PASS %d/%d" % (passed, total))
    return 0 if passed == total and len(RESULTS) == total else 1


if __name__ == "__main__":
    sys.exit(main())
