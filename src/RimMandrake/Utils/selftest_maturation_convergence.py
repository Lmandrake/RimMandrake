#!/usr/bin/env python3
"""selftest_maturation_convergence.py: the convergence reading (maturation_convergence.py) on fixture concepts.

Item RIMMANDRAKE_MEASURE_MATURATION_CONVERGENCE_PER_ROUND. Every fixture lives in a temp tree; nothing in design/ is read
or written. Points:
 1 falling: open 10 -> 6 -> 2 reads CONVERGING, with new / fixed / open per round
 2 flat: open 5 -> 5, new falling, reads FLAT
 3 rising: new 3 -> 3 -> 4 (not falling over three rounds) reads DIVERGING
 4 a missing round (a judge charged with no round on file; a cycle folder with no faults.json; a cycle number skipped)
   prints UNMEASURED cells, never a number, and the trend is read on the measured rounds alone
 5 an empty record (stage.json with no rounds, a 0-byte faults.json) reads UNMEASURED; an empty faults list is a
   measured zero (0 means measured zero)
 6 a malformed record (stage.json not JSON, faults.json not JSON, a non-dict round, a string gap count, a malformed
   verdict, an Exit block with no keys) reads UNMEASURED and does not crash
 7 in-game visits: pass / fail / unmeasured rows and strange_open from the SUMMARY.md Exit block; open falling reads
   CONVERGING
 8 a DIVERGING stage gives one Needs Conductor line with the numbers; a CONVERGING one gives none
 9 the Dispatch tick's reading carries the line and the convergence JSON (maturation_dispatch.tick, a dry pass)
10 MATURATION_NOW --print shows the Convergence table with the words
11 the --json CLI prints the reading and exits 0
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "rimflow"))

FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  -> %s" % str(detail)[:600]))
    if not ok:
        FAILS.append(name)


def w(root, rel, data):
    p = os.path.join(root, "design", "concepts", rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(data if isinstance(data, str) else json.dumps(data))


def rnd(judge, gaps, tags, verdict="not_covered", at="2026-11-15T00:00:00Z"):
    return {"judge": judge, "at": at, "verdict": verdict, "gaps": gaps, "tags": tags, "ids": [], "late": []}


def faults(*pairs):
    """(id, class, status) -> a faults.json list."""
    return [{"id": i, "class": c, "status": s} for i, c, s in pairs]


def exit_md(rows, strange):
    body = ", ".join("%s: %s" % kv for kv in rows.items())
    return ("# Visit\n\n## Exit\n\n```\ningame_rows: {%s}\nstrange_open: %d\nsavegame: C:\\x.rws\nexit_met: false\n```\n"
            % (body, strange))


def build_fixtures(root):
    # Falling: stage 3 open 10 -> 6 -> 2; the Designer claimed 3 fixes against the second judge
    w(root, "Falling/stage.json", {"coverage_rounds": [
        rnd("rm-coverage-judge-1", 10, {"first": 10}), rnd("rm-coverage-judge-2", 6, {"unfixed": 5, "late": 1}),
        rnd("rm-coverage-judge-3", 2, {"unfixed": 2})]})
    w(root, "Falling/coverage_fixes.json", {"against": "rm-coverage-judge-2", "claims": [{"gap": "g1"}, {"gap": "g2"},
                                                                                         {"gap": "g3"}]})
    # Flat: open 5 -> 5
    w(root, "Flat/stage.json", {"coverage_rounds": [rnd("j1", 5, {"first": 5}), rnd("j2", 5, {"unfixed": 4, "changed": 1})]})
    # Churn: open flat while fresh findings keep coming (new 2 2 2); Settling: open flat, new falling 4 2 1
    w(root, "Churn/stage.json", {"coverage_rounds": [rnd("j1", 4, {"first": 4})] + [
        rnd("j%d" % k, 4, {"unfixed": 2, "changed": 2}) for k in (2, 3, 4)]})
    w(root, "Settling/stage.json", {"coverage_rounds": [rnd("j1", 4, {"first": 4}), rnd("j2", 4, {"unfixed": 2, "late": 2}),
                                                        rnd("j3", 4, {"unfixed": 3, "regression": 1})]})
    # Rising: new 3 -> 3 -> 4, open 3 -> 5 -> 8; its blind cycles also rise
    w(root, "Rising/stage.json", {"coverage_rounds": [
        rnd("j1", 3, {"first": 3}), rnd("j2", 5, {"unfixed": 2, "late": 3}), rnd("j3", 8, {"unfixed": 4, "changed": 4})]})
    # Missing: a judge charged before rounds were kept (unmeasured), then two rounds; blind cycle 2 has no faults.json
    # and cycle 3 is skipped (no folder): cycles 1 and 4 measured
    w(root, "Missing/stage.json", {"budget": {"charges": [{"ref": "rm-coverage-judge-0", "at": "2026-11-01T00:00:00Z",
                                                            "tokens": 5}]},
                                   "coverage_rounds": [rnd("rm-coverage-judge-1", 4, {"first": 4}),
                                                       rnd("rm-coverage-judge-2", 2, {"unfixed": 2})]})
    w(root, "Missing/version/blind_challenge/cycle_1/lane2/faults.json",
      {"faults": faults(("A", "Problem", "FIXED abc1234"), ("B", "Problem", "PENDING"), ("C", "Polish", "PENDING"))})
    w(root, "Missing/version/blind_challenge/cycle_2/SUMMARY.md", "# cycle 2\n\n## Exit\n\n(pending)\n")
    w(root, "Missing/version/blind_challenge/cycle_4/lane2/faults.json",
      faults(("B", "Problem", "FIXED def5678")))
    # Empty: stage.json with no rounds; a 0-byte faults.json; an empty faults list (measured zero) in cycle 2
    w(root, "Empty/stage.json", {"coverage_rounds": []})
    w(root, "Empty/version/blind_challenge/cycle_1/lane2/faults.json", "")
    w(root, "Empty/version/blind_challenge/cycle_2/lane2/faults.json", {"faults": []})
    # Malformed: stage.json not JSON; faults.json not JSON; an Exit block with no keys
    w(root, "Malformed/stage.json", "{not json")
    w(root, "Malformed/version/blind_challenge/cycle_1/lane2/faults.json", "[{\"id\": ")
    w(root, "Malformed/version/blind_challenge/cycle_2/lane2/faults.json", {"faults": "not a list"})
    w(root, "Malformed/version/in_game/visit_1/SUMMARY.md", "# v\n\n## Exit\n\nwe did well\n")
    # Malformed2: rounds that are not dicts, a string gap count, a malformed verdict
    w(root, "Malformed2/stage.json", {"coverage_rounds": ["junk", rnd("j1", "seven", {"first": 7}),
                                                         rnd("j2", 5, {"unfixed": 5}, verdict="malformed"),
                                                         {"judge": "j3", "gaps": 3, "tags": "oops"}]})
    # InGame: two visits, open 4 -> 1
    w(root, "InGame/version/in_game/visit_1/SUMMARY.md",
      exit_md({"a": "pass", "b": "fail", "c": "fail", "d": "unmeasured", "e": "pass", "f": "pass"}, 1))
    w(root, "InGame/version/in_game/visit_2/SUMMARY.md",
      exit_md({"a": "pass", "b": "pass", "c": "pass", "d": "unmeasured", "e": "pass", "f": "pass"}, 0))
    # Diverging blind cycles: new 2 -> 3 -> 4
    w(root, "Rising/version/blind_challenge/cycle_1/lane2/faults.json",
      faults(("P1", "Problem", "PENDING"), ("P2", "Problem", "FIXED a1")))
    w(root, "Rising/version/blind_challenge/cycle_2/lane2/faults.json",
      faults(("P1", "Problem", "PENDING"), ("P3", "Problem", "PENDING"), ("P4", "Problem", "PENDING"),
             ("P5", "Polish", "PENDING")))
    w(root, "Rising/version/blind_challenge/cycle_3/lane2/faults.json",
      faults(("P6", "Problem", "PENDING"), ("P7", "Problem", "PENDING"), ("P8", "Problem", "PENDING"),
             ("P9", "Problem", "PENDING")))
    os.makedirs(os.path.join(root, "design", "concepts", "_skipped"), exist_ok=True)


def col(st, key):
    return [r.get(key) for r in st["rounds"]]


def main():
    root = tempfile.mkdtemp(prefix="maturation_convergence_")
    sd = tempfile.mkdtemp(prefix="maturation_convergence_state_")
    try:
        build_fixtures(root)
        try:
            import maturation_convergence as MC
        except ImportError as e:
            check("0 maturation_convergence imports", False, e)
            return 1
        d = MC.read_all(root)
        mods = d.get("mods") or {}
        check("0 every fixture folder is read, '_' folders skipped",
              sorted(mods) == sorted(["Churn", "Empty", "Falling", "Flat", "InGame", "Malformed", "Malformed2",
                                      "Missing", "Rising", "Settling"]), sorted(mods))

        s = mods["Falling"]["3"]
        check("1 falling: open 10 6 2", col(s, "open") == [10, 6, 2], s)
        check("1 falling: new 10 1 0", col(s, "new") == [10, 1, 0], s)
        check("1 falling: fixed None-then 5 4", col(s, "fixed")[1:] == [5, 4] and col(s, "fixed")[0] is None, s)
        check("1 falling: the fix claims ride on the judged round", col(s, "fix_claims") == [None, 3, None], s)
        check("1 falling reads CONVERGING", s["verdict"] == "CONVERGING", s)

        s = mods["Flat"]["3"]
        check("2 flat reads FLAT", s["verdict"] == "FLAT" and col(s, "open") == [5, 5], s)

        s = mods["Rising"]["3"]
        check("3 rising reads DIVERGING", s["verdict"] == "DIVERGING" and col(s, "new") == [3, 3, 4], s)
        b = mods["Rising"]["4+5"]
        check("3 rising blind cycles: new 2 3 4 reads DIVERGING",
              b["verdict"] == "DIVERGING" and col(b, "new") == [2, 3, 4] and col(b, "open") == [1, 3, 4], b)
        s = mods["Churn"]["3"]
        check("3 churn: open flat 4 4 4 4 but new 2 2 2 not falling over the last three rounds reads DIVERGING",
              s["verdict"] == "DIVERGING" and col(s, "open") == [4, 4, 4, 4] and col(s, "new") == [4, 2, 2, 2], s)
        s = mods["Settling"]["3"]
        check("3 settling: open flat 4 4 4 with new 4 2 1 falling reads FLAT",
              s["verdict"] == "FLAT" and col(s, "new") == [4, 2, 1], s)

        s = mods["Missing"]["3"]
        check("4 a judge charged with no round is an UNMEASURED round",
              len(s["rounds"]) == 3 and s["rounds"][0]["measured"] is False and s["rounds"][0]["open"] is None, s)
        check("4 the trend reads on the measured rounds (4 -> 2): CONVERGING", s["verdict"] == "CONVERGING", s)
        check("4 the fixed count after an unmeasured round is not guessed", s["rounds"][1]["fixed"] is None, s)
        b = mods["Missing"]["4+5"]
        check("4 blind: cycles 1..4, 2 and 3 unmeasured",
              [r["measured"] for r in b["rounds"]] == [True, False, False, True], b)
        check("4 blind: open 1 then 0 (Problem not FIXED), new counted against every earlier cycle",
              col(b, "open") == [1, None, None, 0] and col(b, "new") == [3, None, None, 0], b)
        check("4 blind: open reached 0, reads CONVERGING", b["verdict"] == "CONVERGING", b)
        check("4 missing rounds are named", "2" in str(b.get("missing")) and "3" in str(b.get("missing")), b)
        check("4 no ingame record reads UNMEASURED", mods["Missing"]["6"]["verdict"] == "UNMEASURED", mods["Missing"])

        s = mods["Empty"]["3"]
        check("5 a stage.json with no rounds reads UNMEASURED", s["verdict"] == "UNMEASURED" and s["rounds"] == [], s)
        b = mods["Empty"]["4+5"]
        check("5 a 0-byte faults.json is an UNMEASURED round",
              b["rounds"][0]["measured"] is False and b["rounds"][0]["open"] is None, b)
        check("5 an empty faults list is a measured zero",
              b["rounds"][1]["measured"] is True and b["rounds"][1]["open"] == 0, b)

        for st_name in ("3", "4+5", "6"):
            check("6 malformed stage %s reads UNMEASURED" % st_name, mods["Malformed"][st_name]["verdict"] == "UNMEASURED",
                  mods["Malformed"][st_name])
        b = mods["Malformed"]["4+5"]
        check("6 malformed faults rounds carry their reason", all(not r["measured"] and r.get("why") for r in b["rounds"]),
              b)
        s = mods["Malformed2"]["3"]
        check("6 junk rounds, a string count, a malformed verdict and string tags are each UNMEASURED, no crash",
              [r["measured"] for r in s["rounds"]] == [False, False, False, False] and s["verdict"] == "UNMEASURED", s)

        g = mods["InGame"]["6"]
        check("7 ingame rows pass/fail/unmeasured", [(r["pass"], r["fail"], r["unmeasured"], r["strange_open"])
                                                     for r in g["rounds"]] == [(3, 2, 1, 1), (5, 0, 1, 0)], g)
        check("7 ingame open 4 -> 1 reads CONVERGING", col(g, "open") == [4, 1] and g["verdict"] == "CONVERGING", g)
        check("7 ingame fixed 2 (b, c) and the strange one", g["rounds"][1]["fixed"] == 3, g)

        lines = MC.needs_lines(d)
        rising = [x for x in lines if x.startswith("Rising")]
        check("8 one line per DIVERGING stage (Rising 3 and 4+5, Churn 3) and none else",
              len(rising) == 2 and len(lines) == 3 and any(x.startswith("Churn Stage 3") for x in lines), lines)
        check("8 the line carries the numbers", any("3 -> 5 -> 8" in x and "3 -> 3 -> 4" in x for x in rising), lines)
        check("8 the line says it pauses nothing", all("pauses nothing" in x for x in lines), lines)

        # 9: the Dispatch tick (a dry pass, no mods advancing) carries the line and the JSON
        os.environ["RM_MATURATION_DISPATCH_DIR"] = sd
        import maturation_dispatch as MD
        cfg = dict(MD.load_cfg() if hasattr(MD, "load_cfg") else {}, advancing=[], enabled=False)
        fx = {"autonomy": False, "facts": lambda: {}, "account": lambda: (True, "test"),
              "releases": lambda: ([], [])}
        try:
            rd = MD.tick(root, cfg, False, fx=fx, now=1794800000.0, page=False)
        except Exception as e:      # noqa: BLE001
            rd = {"_crash": "%s: %s" % (e.__class__.__name__, e)}
        nc = rd.get("needs_conductor") or []
        check("9 the tick's Needs Conductor lines carry the DIVERGING line",
              any("Rising" in x and "DIVERGING" in x for x in nc), rd)
        check("9 the tick's reading carries the convergence words",
              (rd.get("convergence") or {}).get("Rising", {}).get("3", {}).get("verdict") == "DIVERGING", rd)
        check("9 a dry tick wrote no reading", not os.path.exists(os.path.join(sd, "reading.json")))

        # 10: the page
        p = subprocess.run([sys.executable, os.path.join(HERE, "maturation_now.py"), "--root", root, "--no-live",
                            "--print"], capture_output=True, text=True, timeout=300,
                           env=dict(os.environ, MATURATION_NOW_CLOCK="1794800000"))
        out = p.stdout
        check("10 the page prints", p.returncode == 0, p.stderr[-800:])
        check("10 the page has the Convergence section", "## Convergence" in out, out[-1500:])
        sec = out.split("## Convergence", 1)[-1].split("\n## ", 1)[0]
        check("10 the table names the words", all(x in sec for x in ("DIVERGING", "CONVERGING", "FLAT", "UNMEASURED")),
              sec[:1500])

        p = subprocess.run([sys.executable, os.path.join(HERE, "maturation_convergence.py"), "--root", root, "--json"],
                           capture_output=True, text=True, timeout=120)
        try:
            j = json.loads(p.stdout)
        except ValueError:
            j = {}
        check("11 --json prints the reading", p.returncode == 0 and "Rising" in (j.get("mods") or {}), p.stderr[-600:])
    finally:
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(sd, ignore_errors=True)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
