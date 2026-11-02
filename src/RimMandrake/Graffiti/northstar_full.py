#!/usr/bin/env python3
"""northstar_full.py -- Graffiti's FULL-LIST rung in one command (GRAFFITI_NORTHSTAR_GREEN_FULL_1).

WSL python3, repo root as cwd, the game freshly launched on the owner's full list (FULL.LATEST) and the bridge
held by the caller. It never launches, stops or swaps anything, and never touches ModsConfig.xml:

  python3 src/RimMandrake/Graffiti/northstar_full.py [--list <ModsConfig>] [--no-quicktest] [--no-judge]
  python3 src/RimMandrake/Graffiti/northstar_full.py --check <results.json>      # offline verdict only

  1 a FRESH quicktest map (bridgetools/prove_quicktest_world.py, python.exe) -- never the minimal session's map;
  2 northstar_driver `run --config full` (python.exe): pre-flight refuses unless the RUNNING list
    (jawa/running_mods = RunningModsListForReading) equals --list in ids and order; the site is the suite's own;
    foreign SacredGraffiti / GraffitiImperial marks land in doc["compat"], never in Graffiti's bars;
    doc["full_list_differences"] lists pool members, cleaning mods and camera mods;
  3 judge_cli.py (the visual half, claude -p);
  4 the verdict below, then the run is recorded in modcheck status with config `full`.

Exit 0 = every clause holds (GREEN on the full list); 1 = ran, not green; 2 = could not run a step.

--tier small (PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS, owner 2026-11-02: "small mod lists should always be the way to
test until a final verification pass on the whole huge mod list"): the same suite on WHATEVER game is up, as long as it
holds Graffiti and its dependencies (northstar_driver `needs-mods --mod Graffiti`, exit 2 when it does not). The run is
`--config current`; the verdict drops only the full-list clauses (config `full`, pre-flight running_list, the
full_list_differences section, a compat row per foreign member that a small list does not load). Every Graffiti bar,
the judge, partial/refused and compat-apart stay. The default `--tier full` is the FINAL verification (GREEN-FULL).

The verdict (full_rung_verdict) holds only when ALL of: the doc is Graffiti's and config is `full`; pre-flight
`running_list` PASS; the run was not refused and is not partial; it was judged; every row in bars[] (each north-star
bar and each functional row) is PASS and every bar of Graffiti's VALIDATED walk (read from the walk, never from the
doc) is present and PASS; compat rows are reported apart (none in bars[], one per foreign member in compat[]); and
the differences section has its lists, at least one full-only id, and no unclassified (not installed) id.
The results file must be new: an existing --out refuses, so an old GREEN can never be re-read as this run's.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DRIVER = os.path.join(ROOT, "src", "RimMandrake", "Utils", "northstar_driver")
PLAN = "src/RimMandrake/Graffiti/northstar_plan.py"
MOD = "Graffiti"


def authoritative_expected():
    """Graffiti's bar ids from its VALIDATED walk, read here -- never from the document being judged."""
    sys.path.insert(0, DRIVER)
    sys.path.insert(0, os.path.dirname(DRIVER))
    import cli
    return cli.expected_bars(MOD)


def compat_ids_required():
    """The compat row every foreign member must leave (its status is irrelevant to Graffiti's verdict)."""
    for d in (HERE, os.path.dirname(DRIVER)):
        if d not in sys.path:
            sys.path.insert(0, d)
    import validation
    return {"spree_wall.compat_%s_marks" % pid.rsplit(".", 1)[-1] for pid in validation.FOREIGN_DEFS}


def full_rung_verdict(doc, expected=None, compat_required=None, tier="full"):
    """(ok, [reasons it is not]) for a judged results doc. `expected` / `compat_required` default to the
    authoritative sources (the walk; validation.FOREIGN_DEFS); tests pass their own. tier "small" judges a
    `--config current` run on any list holding Graffiti: the full-list-only clauses are not asked."""
    full = tier == "full"
    sys.path.insert(0, os.path.dirname(DRIVER))
    from northstar_driver import bars as B
    from northstar_driver import PASS
    why = []
    if expected is None:
        expected, src = authoritative_expected()
        if not expected:
            why.append("no authoritative expected bars (%s)" % src)
    if compat_required is None:
        compat_required = compat_ids_required() if full else ()
    if doc.get("mod") != MOD:
        why.append("results are for %r, not %s" % (doc.get("mod"), MOD))
    want = "full" if full else "current"
    if doc.get("config") != want:
        why.append("config is %r, not %r" % (doc.get("config"), want))
    pre = {c.get("name"): c for c in doc.get("preflight") or []}
    rl = pre.get("running_list")
    if full and (not rl or rl.get("status") != PASS):
        why.append("pre-flight running_list %s" % ("absent" if not rl else "%s: %s" % (rl.get("status"),
                                                                                      str(rl.get("evidence"))[:200])))
    if doc.get("refused"):
        why.append("refused: %s" % str(doc["refused"])[:200])
    if doc.get("partial", True):
        why.append("partial (or unmarked) results")
    if not doc.get("judge"):
        why.append("not judged (judge_cli.py never ran on it)")
    rows = doc.get("bars") or []
    bad = [(r.get("id"), r.get("status")) for r in rows if r.get("status") != PASS]
    if bad:
        why.append("%d row(s) not PASS: %s" % (len(bad), bad[:12]))
    if expected and (not rows or not B.all_green(rows, expected)):
        have = {r.get("id") for r in rows if r.get("status") == PASS}
        why.append("authoritative bars missing or not PASS: %s" % [e for e in expected if e not in have][:12])
    if any(r.get("compat") or str(r.get("id", "")).split(".")[-1].startswith("compat_") for r in rows):
        why.append("a compat row sits in bars[] (must be reported apart)")
    compat = doc.get("compat")
    if not isinstance(compat, list):
        why.append("no compat section")
    else:
        miss = sorted(set(compat_required) - {r.get("id") for r in compat if isinstance(r, dict)})
        if miss:
            why.append("compat rows missing: %s" % miss)
    d = doc.get("full_list_differences")
    if not full:
        pass
    elif not isinstance(d, dict) or d.get("error"):
        why.append("full_list_differences missing or broken: %s" % (str(d)[:200],))
    else:
        bad = [k for k in ("pool_members", "cleaning", "camera", "full_only", "not_installed")
               if not isinstance(d.get(k), list)]
        if bad:
            why.append("full_list_differences lacks list(s): %s" % bad)
        elif not d["full_only"]:
            why.append("full_list_differences saw no full-only mod (a full list always has some): blind scan")
        elif d["not_installed"]:
            why.append("full_list_differences could not classify %d full-only id(s) (not installed): %s"
                       % (len(d["not_installed"]), d["not_installed"][:8]))
    return not why, why


def _run(argv, timeout):
    """(rc, output). A timeout or a failed launch is rc 2 with what output there was -- never an exception."""
    try:
        p = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired as ex:
        part = ex.stdout or ""
        part = part.decode("utf-8", "replace") if isinstance(part, bytes) else part
        return 2, "TIMEOUT after %d s\n%s" % (timeout, part)
    except OSError as ex:
        return 2, "could not start %s: %s" % (argv[0], ex)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def win_path(p):
    """A path python.exe can open: repo-relative stays relative (cwd is the repo); an absolute WSL path goes
    through `wslpath -w`."""
    if not os.path.isabs(p):
        return p
    rc, out = _run(["wslpath", "-w", p], 30)
    if rc != 0 or not out.strip():
        raise SystemExit("cannot convert %s for python.exe: %s" % (p, out.strip()))
    return out.strip()


def _record(doc, out, ok):
    sys.path.insert(0, DRIVER)
    sys.path.insert(0, os.path.dirname(DRIVER))
    import cli
    mod_dir, now = cli.mod_hash_now(MOD)
    doc = dict(doc, all_green=bool(ok))
    _entry, msg = cli.record_result(doc, MOD, out, doc.get("mod_hash") or now, mod_dir)
    return msg


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", help="results JSON: print the verdict, record nothing")
    ap.add_argument("--list", help="the list the running game must equal (default FULL.LATEST)")
    ap.add_argument("--tier", choices=("full", "small"), default="full",
                    help="small: any running list holding Graffiti + its dependencies, --config current, the full-list "
                         "clauses not asked; full (default): the FINAL verification on the whole list")
    ap.add_argument("--out")
    ap.add_argument("--no-quicktest", action="store_true", help="the map is already a FRESH quicktest")
    ap.add_argument("--no-judge", action="store_true", help="state half only (the verdict then fails: not judged)")
    ap.add_argument("--no-record", action="store_true")
    a = ap.parse_args(argv)
    if a.check:
        try:
            doc = json.load(open(a.check, encoding="utf-8"))
        except (OSError, ValueError) as ex:
            print("FULL RUNG NOT GREEN: results unreadable (%s)" % ex)
            return 1
        ok, why = full_rung_verdict(doc, tier=a.tier)
        print("%s RUNG %s%s" % (a.tier.upper(), "GREEN" if ok else "NOT GREEN", "" if ok else ": " + " | ".join(why)))
        return 0 if ok else 1
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out = a.out or os.path.join("Transient", "northstar", "Graffiti_%s_%s.json" % (a.tier, ts))
    out_abs = out if os.path.isabs(out) else os.path.join(ROOT, out)
    if os.path.exists(out_abs):     # this invocation must write its own results, never reuse an old file
        print("refused: %s already exists" % out)
        return 2
    if a.tier == "small":       # the game must hold what the suite needs; another tier is UNMEASURED, never a FAIL
        rc, txt = _run(["python.exe", "src/RimMandrake/Utils/northstar_driver/cli.py", "needs-mods", "--mod", MOD], 120)
        print("[0 needs] %s" % ((txt.strip().splitlines() or ["(no output)"])[-1][:200]), flush=True)
        if rc != 0:
            return 2
    if not a.no_quicktest:
        rc, txt = _run(["python.exe", "src/RimMandrake/bridgetools/prove_quicktest_world.py"], 420)
        print("[1 map] %s" % ((txt.strip().splitlines() or ["(no output)"])[-1][:160]), flush=True)
        if rc != 0:
            print("[1 map] fresh quicktest did not reach Playing:\n" + txt[-500:])
            return 2
    argv = ["python.exe", "src/RimMandrake/Utils/northstar_driver/cli.py", "run", "--mod", MOD, "--plan", PLAN,
            "--config", "full" if a.tier == "full" else "current", "--no-record", "--out", win_path(out)] + (
                ["--list", win_path(a.list)] if a.list and a.tier == "full" else [])
    rc, txt = _run(argv, 5400)
    print("[2 run] exit %s: %s" % (rc, ([l for l in txt.splitlines() if l.startswith(MOD + ":")] or ["?"])[-1][:200]),
          flush=True)
    if rc not in (0, 1) or not os.path.exists(out_abs):     # 2 = refused at pre-flight, or the run broke
        print("[2 run] refused or no results written:\n" + txt[-1200:])
        return 2
    if not a.no_judge:
        rc, txt = _run(["python3", "src/RimMandrake/Utils/northstar_driver/judge_cli.py", out_abs], 3000)
        print("[3 judge] exit %s: %s" % (rc, (txt.strip().splitlines() or ["?"])[-1][:200]), flush=True)
        if rc not in (0, 1):
            print("[3 judge] judge did not finish:\n" + txt[-800:])
            return 2
    doc = json.load(open(out_abs, encoding="utf-8"))
    ok, why = full_rung_verdict(doc, tier=a.tier)
    print("[4 verdict] %s RUNG %s%s" % (a.tier.upper(), "GREEN" if ok else "NOT GREEN", "" if ok else ": " + " | ".join(why)))
    if not a.no_record and not doc.get("refused"):
        print("[4 record] " + _record(doc, out, ok))
    print("results: %s" % out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
