#!/usr/bin/env python3
"""Gate G16 (runbook 06 §2): contaminated test fixtures — every Saves/RM_TestSite_*.rws through the three
start-save censuses (G11's instruments) against a profile, resumable, plus a quarantine plan.

    g16_fixture_census.py run   [--modlist XML] [--out DIR] [--only SUBSTR] [--redo] [--budget SEC]
    g16_fixture_census.py table [--out DIR]                       # the per-save verdict table (markdown)
    g16_fixture_census.py quarantine [--out DIR] [--apply --game-is-down]   # move CONTAMINATED saves aside

Per save, three read-only tools (they never write the save):
  class  save_class_census.py <save> --modsconfig <list> --json        FATAL Class= under areaManager = map never loads
  def    save_def_census.py   <save> --modsconfig <list> --json        THING rows with an absent def = spawn errors
  adopt  save_adoption_check.py --save <save> --modlist <list> --json  unresolved names / lostOnLoad grid hashes
Tool exit codes are kept as-is: 0 clean, 1 findings, 2/3 the tool refused (instrument blind) = UNMEASURED.
Verdict: CLEAN (all three 0) · CONTAMINATED (any 1 and none blind) · UNMEASURED (any blind, timeout or crash).
Results land in <out>/<save stem>.<tool>.json + .log and <out>/results.json; a re-run skips finished rows
unless --redo, so a 600 s helper watchdog never loses work (each call has its own timeout).
Default list: the DEV profile (fixtures are for development on the dev world); pass --modlist for another.
Quarantine moves files to Saves/_quarantine_<date>/ (never deletes); the plan prints without --apply.
"""
import argparse
import datetime
import glob
import json
import os
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

UT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_DEFAULT = os.path.join(common.MODLISTS, "ModsConfig.DEV.RULED_2026-10-20.xml")
OUT_DEFAULT = "/mnt/d/ClaudeWork/remake/g16_fixtures"
try:
    import game_paths
    SAVES = game_paths.SAVES
except Exception:  # pragma: no cover
    SAVES = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves"


def tools(save, modlist, out, stem):
    j = lambda t: os.path.join(out, "%s.%s.json" % (stem, t))
    return {
        "class": [sys.executable, os.path.join(UT, "save_class_census.py"), save, "--modsconfig", modlist, "--json", j("class")],
        "def": [sys.executable, os.path.join(UT, "save_def_census.py"), save, "--modsconfig", modlist, "--json", j("def")],
        "adopt": [sys.executable, os.path.join(UT, "save_adoption_check.py"), "--save", save, "--modlist", modlist,
                  "--json", j("adopt")],
    }


def fixtures(saves_dir, only=None):
    fs = sorted(glob.glob(os.path.join(saves_dir, "RM_TestSite_*.rws")))
    return [f for f in fs if not only or only in os.path.basename(f)]


def verdict(rcs):
    if any(rc not in (0, 1) for rc in rcs.values()) or len(rcs) < 3:
        return "UNMEASURED"
    return "CONTAMINATED" if any(rc == 1 for rc in rcs.values()) else "CLEAN"


def load_results(out):
    p = os.path.join(out, "results.json")
    return json.load(open(p)) if os.path.isfile(p) else {}


def save_results(out, res):
    tmp = os.path.join(out, "results.json.tmp")
    json.dump(res, open(tmp, "w"), indent=1)
    os.replace(tmp, os.path.join(out, "results.json"))


def run(a, saves_dir=None, runner=subprocess.run):
    os.makedirs(a.out, exist_ok=True)
    res = load_results(a.out)
    fs = fixtures(saves_dir or SAVES, a.only)
    if not fs:
        print("UNMEASURED no Saves/RM_TestSite_*.rws found in %s" % (saves_dir or SAVES))
        return 2
    t0 = time.time()
    for f in fs:
        stem = os.path.basename(f)[:-4]
        row = res.setdefault(stem, {"save": f, "rc": {}, "modlist": a.modlist})
        if row.get("modlist") != a.modlist:
            row.update({"rc": {}, "modlist": a.modlist})
        for t, cmd in tools(f, a.modlist, a.out, stem).items():
            if t in row["rc"] and not a.redo:
                continue
            if a.budget and time.time() - t0 > a.budget:
                save_results(a.out, res)
                print("BUDGET reached after %.0f s; re-run to continue (finished rows are kept)" % (time.time() - t0))
                return 4
            try:
                p = runner(cmd, capture_output=True, text=True, timeout=a.timeout)
                rc, log = p.returncode, (p.stdout or "") + (p.stderr or "")
            except subprocess.TimeoutExpired:
                rc, log = 124, "TIMEOUT after %d s" % a.timeout
            open(os.path.join(a.out, "%s.%s.log" % (stem, t)), "w").write(log)
            row["rc"][t] = rc
            row["size"] = os.path.getsize(f)
            row["mtime"] = datetime.datetime.fromtimestamp(os.path.getmtime(f)).isoformat(timespec="seconds")
            save_results(a.out, res)
            print("  %-48s %-5s rc=%d" % (stem, t, rc))
        row["verdict"] = verdict(row["rc"])
        save_results(a.out, res)
    return table(a)


def table(a):
    res = load_results(a.out)
    if not res:
        print("UNMEASURED no results in %s" % a.out)
        return 2
    lines = ["| fixture | class | def | adopt | verdict | worst finding |", "|---|---|---|---|---|---|"]
    count = {}
    for stem in sorted(res):
        r = res[stem]
        v = r.get("verdict") or verdict(r["rc"])
        count[v] = count.get(v, 0) + 1
        rc = r["rc"]
        worst = ("FATAL Class= (map never loads)" if rc.get("class") == 1 else
                 "THING rows with absent defs (spawn errors)" if rc.get("def") == 1 else
                 "unresolved refs / lost grid hashes only (Scribe drops)" if rc.get("adopt") == 1 else "-")
        lines.append("| %s | %s | %s | %s | %s | %s |" % (stem, *(rc.get(t, "-") for t in ("class", "def", "adopt")), v, worst))
    md = "\n".join(lines) + "\n\nrc: 0 clean · 1 findings · 2/3 tool refused · 124 timeout. counts %s\n" % json.dumps(count, sort_keys=True)
    open(os.path.join(a.out, "TABLE.md"), "w").write(md)
    print(md)
    return 1 if count.get("CONTAMINATED") else (2 if count.get("UNMEASURED") else 0)


def quarantine(a, saves_dir=None):
    res = load_results(a.out)
    bad = [r["save"] for r in res.values() if (r.get("verdict") or verdict(r["rc"])) == "CONTAMINATED"]
    qd = os.path.join(saves_dir or SAVES, "_quarantine_%s" % datetime.date.today().isoformat())
    for s in bad:
        print("  mv %s -> %s/" % (s, qd))
    print("PLAN %d CONTAMINATED fixtures%s" % (len(bad), "" if a.apply else " (dry run; --apply --game-is-down moves)"))
    if not a.apply:
        return 0
    if not a.game_is_down:
        print("REFUSED --apply needs --game-is-down")
        return 3
    os.makedirs(qd, exist_ok=True)
    for s in bad:
        if os.path.exists(s):
            shutil.move(s, os.path.join(qd, os.path.basename(s)))
    print("MOVED %d" % len(bad))
    return 0


def main(argv=None, saves_dir=None, runner=subprocess.run):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("run", "table", "quarantine"))
    ap.add_argument("--modlist", default=DEV_DEFAULT)
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--only")
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--timeout", type=int, default=500)
    ap.add_argument("--budget", type=int, default=0, help="stop starting new tool runs after SEC seconds")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--game-is-down", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return run(a, saves_dir, runner)
    if a.cmd == "table":
        return table(a)
    return quarantine(a, saves_dir)


if __name__ == "__main__":
    sys.exit(main())
