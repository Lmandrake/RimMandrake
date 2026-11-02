#!/usr/bin/env python3
"""Selftest for GRAFFITI_NORTHSTAR_GREEN_FULL_1 -- the northstar_driver's full-list mode and Graffiti's full rung.
Offline: no bridge, no game, ModsConfig.xml and modcheck_status.json never touched, no mod root read.

  1 preflight.check_running_list: the RUNNING list (jawa/running_mods) against a list file -- identical PASS;
    a missing id, an extra id, a reorder FAIL; no packageIds / a raising call / an unreadable list UNMEASURED;
    the read-only `running-list` verb exits 0 only on an identical list.
  2 `run --mock --config full`: pre-flight carries running_list PASS, doc.config is 'full', the differences
    section is written, foreign-member compat rows sit in doc.compat and never in bars[]; a list the running
    game does not equal REFUSES the run (exit 2).
  3 record_result stores config 'full' in the modcheck entry and its run_id.
  4 full_list_diff.differences on a fake mod root: pool member, cleaning and camera name-matches, not-installed,
    the mod under test excluded.
  5 northstar_full.full_rung_verdict: a clean judged doc is GREEN; each single defect is not.
"""
import atexit
import copy
import json
import os
import shutil
import sys
import tempfile

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_full_list_mode_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (UTILS, os.path.join(UTILS, "modcheck"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

from northstar_driver import PASS, FAIL, UNMEASURED, cli               # noqa: E402
from northstar_driver import preflight as pf                            # noqa: E402
from northstar_driver.transport import MockGame, MockTransport          # noqa: E402
from northstar_driver.session import FastSession                        # noqa: E402
import full_list_diff                                                   # noqa: E402
import northstar_full                                                   # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else str(detail)[:300]))
    if not cond:
        FAILS.append(name)


def write_list(ids, name="ModsConfig.xml"):
    d = tempfile.mkdtemp()
    p = os.path.join(d, name)
    with open(p, "w") as f:
        f.write("<ModsConfigData><activeMods>%s</activeMods></ModsConfigData>" % "".join("<li>%s</li>" % i for i in ids))
    return p


class _Raising(object):
    def call(self, tool, **p):
        raise RuntimeError("bridge gone")


class _Fixed(object):
    def __init__(self, reply):
        self.reply = reply

    def call(self, tool, **p):
        return self.reply


def t1_running_list():
    game = MockGame(mods=("ludeon.rimworld", "a.b", "c.d"))
    with FastSession(transport=MockTransport(game), strict=False) as s:
        c = pf.check_running_list(s, write_list(["ludeon.rimworld", "a.b", "c.d"]))
        check("1 identical running list PASS", c.status == PASS, c.evidence)
        c = pf.check_running_list(s, write_list(["ludeon.rimworld", "a.b", "c.d", "e.f"]))
        check("1 an intended id not running FAIL (MISSING)", c.status == FAIL and "absent" in c.evidence, c.evidence)
        c = pf.check_running_list(s, write_list(["ludeon.rimworld", "a.b"]))
        check("1 a running id not intended FAIL (EXTRA)", c.status == FAIL and "not intended" in c.evidence, c.evidence)
        c = pf.check_running_list(s, write_list(["ludeon.rimworld", "c.d", "a.b"]))
        check("1 same ids, other order FAIL (REORDERED)", c.status == FAIL and "order" in c.evidence, c.evidence)
        c = pf.check_running_list(s, os.path.join(tempfile.mkdtemp(), "nope.xml"))
        check("1 unreadable intended list UNMEASURED", c.status == UNMEASURED, c.evidence)
    c = pf.check_running_list(_Raising(), write_list(["ludeon.rimworld"]))
    check("1 a raising bridge call UNMEASURED", c.status == UNMEASURED, c.evidence)
    c = pf.check_running_list(_Fixed({"success": True, "packageIds": []}), write_list(["ludeon.rimworld"]))
    check("1 a reply with no packageIds UNMEASURED, never a match", c.status == UNMEASURED, c.evidence)
    c = pf.check_running_list(_Fixed({"success": True, "packageIds": ["ludeon.rimworld", None]}),
                              write_list(["ludeon.rimworld"]))
    check("1 a bad entry is never dropped to reach equality (UNMEASURED)", c.status == UNMEASURED, c.evidence)
    c = pf.check_running_list(_Fixed(["ludeon.rimworld"]), write_list(["ludeon.rimworld"]))
    check("1 a non-dict reply UNMEASURED, no crash", c.status == UNMEASURED, c.evidence)
    import argparse
    ns = lambda ids: argparse.Namespace(mock=True, fault=None, pipeline=False, list=write_list(ids))  # noqa: E731
    check("1 `running-list` verb exits 0 on an identical list", cli.cmd_running_list(ns(["ludeon.rimworld"])) == 0)
    check("1 `running-list` verb exits 1 on a different list",
          cli.cmd_running_list(ns(["ludeon.rimworld", "x.y"])) == 1)


STUB_DIFF = {"pool_members": [], "cleaning": [], "camera": [], "full_only": [], "stub": True}


def stub_plan():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "plan_full_stub.py")
    with open(p, "w") as f:
        f.write("import sys\nsys.path.insert(0, %r)\nfrom northstar_plan import *  # noqa\n"
                "def full_list_differences(list_path):\n    return %r\n" % (HERE, STUB_DIFF))
    return p


def t2_mock_run():
    plan = stub_plan()
    out = os.path.join(tempfile.mkdtemp(), "r.json")
    rc = cli.main(["run", "--mock", "--mod", "Graffiti", "--plan", plan, "--config", "full",
                   "--list", write_list(["ludeon.rimworld"]), "--out", out])
    doc = json.load(open(out))
    pre = {c["name"]: c for c in doc["preflight"]}
    check("2 full-mode run was not refused", not doc.get("refused") and rc in (0, 1), (rc, doc.get("refused")))
    check("2 pre-flight running_list PASS", pre.get("running_list", {}).get("status") == PASS, pre.get("running_list"))
    check("2 doc.config == 'full'", doc.get("config") == "full", doc.get("config"))
    check("2 differences section written", doc.get("full_list_differences", {}).get("stub") is True,
          doc.get("full_list_differences"))
    compat = {r["id"] for r in doc.get("compat") or []}
    check("2 both foreign members reported in doc.compat",
          compat == {"spree_wall.compat_sacredgraffiti_marks", "spree_wall.compat_graffitiimperial_marks"}, compat)
    check("2 absent members read UNMEASURED there", all(r["status"] == UNMEASURED for r in doc["compat"]), doc["compat"])
    check("2 no compat row in bars[]", not [r for r in doc["bars"] if "compat_" in r["id"]],
          [r["id"] for r in doc["bars"] if "compat_" in r["id"]])
    sw = [r for r in doc["bars"] if r["id"].startswith("spree_wall.") or r["id"] in (
        "mark_actually_appears", "marks_visibly_various", "mark_sits_on_the_wall")]
    check("2 spree_wall's Graffiti rows unharmed by the compat rows (none UNMEASURED by upstream)",
          sw and not [r for r in sw if "earlier" in r.get("evidence", "")], [(r["id"], r["evidence"][:80]) for r in sw])
    out2 = os.path.join(tempfile.mkdtemp(), "r2.json")
    rc2 = cli.main(["run", "--mock", "--mod", "Graffiti", "--plan", plan, "--config", "full",
                    "--list", write_list(["ludeon.rimworld", "mandrake.rm.sacredgraffiti"]), "--out", out2])
    d2 = json.load(open(out2))
    check("2 running list != intended list REFUSES (exit 2)", rc2 == 2 and "running_list" in (d2.get("refused") or ""),
          (rc2, d2.get("refused")))
    out3 = os.path.join(tempfile.mkdtemp(), "r3.json")
    cli.main(["run", "--mock", "--mod", "Graffiti", "--plan", plan, "--out", out3])
    d3 = json.load(open(out3))
    check("2 default config is 'current' with no running_list check or differences",
          d3.get("config") == "current" and "running_list" not in {c["name"] for c in d3["preflight"]}
          and "full_list_differences" not in d3, (d3.get("config"), [c["name"] for c in d3["preflight"]]))


def t3_record():
    got = {}

    def rec(mod, mod_dir, run_id, all_green, walk=None, extra=None):
        got.update(run_id=run_id, extra=extra)
        return {"status": "X", "hash": "0" * 16}

    import status
    mod_dir = tempfile.mkdtemp()
    open(os.path.join(mod_dir, "a.txt"), "w").write("x")
    h = status.mod_hash(mod_dir)
    doc = {"config": "full", "bars": [{"id": "b", "status": PASS}], "all_green": True,
           "compat": [{"id": "spree_wall.compat_x", "status": UNMEASURED}]}
    cli.record_result(doc, "Graffiti", os.path.join(ROOT, "Transient", "x.json"), h, mod_dir, _record=rec)
    ex = got.get("extra") or {}
    check("3 recorded entry carries config 'full'", ex.get("config") == "full" and ex["source"]["config"] == "full", ex)
    check("3 run_id names the config", "[full]" in got.get("run_id", ""), got.get("run_id"))
    check("3 compat recorded apart from bars", ex.get("compat") == {"spree_wall.compat_x": UNMEASURED}
          and "spree_wall.compat_x" not in ex.get("bars", {}), ex)


def t3b_compat_partition():
    chains = [{"name": "ch", "components": [
        {"name": "own", "verdict": "PASS", "shows": ["bar_a"]},
        {"name": "compat_x_marks", "verdict": "FAIL", "shows": ["bar_a"]},
        {"name": "compat_y_marks", "verdict": "FAIL", "shows": []},
        {"name": "fn", "verdict": "PASS", "shows": []}]}]
    rows = cli._rows_from(chains, ["bar_a"], {})
    a = [r for r in rows if r["id"] == "bar_a"]
    check("3 a compat row claiming shows= never reaches the bar rollup",
          a and a[0]["status"] != FAIL and not [r for r in rows if "compat_" in r["id"]], rows)
    check("3 both compat rows reported apart",
          {r["id"] for r in cli.compat_rows(chains)} == {"ch.compat_x_marks", "ch.compat_y_marks"}, cli.compat_rows(chains))


def _mod(root, pid, name, desc="", about_extra="", xml=None):
    d = os.path.join(root, pid.replace(".", "_"))
    os.makedirs(os.path.join(d, "About"))
    open(os.path.join(d, "About", "About.xml"), "w").write(
        "<ModMetaData><packageId>%s</packageId><name>%s</name><description>%s</description>%s</ModMetaData>"
        % (pid, name, desc, about_extra))
    if xml:
        os.makedirs(os.path.join(d, "1.6", "Defs"))
        open(os.path.join(d, "1.6", "Defs", "m.xml"), "w").write(xml)
    return d


def t4_differences():
    r = tempfile.mkdtemp()
    dep = "<modDependencies><li><packageId>mandrake.rm.graffiti</packageId></li></modDependencies>"
    mark = ("<Defs><ThingDef ParentName='RM_BaseGraffiti'><defName>X_Mark</defName><modExtensions>"
            "<li Class='RimMandrake.Graffiti.ModExtension_Graffiti'><form>Tag</form></li></modExtensions>"
            "</ThingDef><ThingDef><defName>X_Plain</defName></ThingDef></Defs>")
    roots = {
        "x.pool": [_mod(r, "x.pool", "Pool Marks", "more marks", dep, mark)],
        "x.deponly": [_mod(r, "x.deponly", "Needs Graffiti", "no marks", dep, "<Defs/>")],
        "x.clean": [_mod(r, "x.clean", "Filth Reducer", "less mess")],
        "x.cam": [_mod(r, "x.cam", "Camera+", "zoom further")],
        "x.plain": [_mod(r, "x.plain", "Plain", "nothing")],
        "mandrake.rm.graffiti": [_mod(r, "mandrake.rm.graffiti", "Graffiti", "cleaning protection")],
    }
    full = write_list(["ludeon.rimworld", "mandrake.rm.graffiti", "x.pool", "x.deponly", "x.clean", "x.cam",
                       "x.plain", "x.gone"])
    mini = write_list(["ludeon.rimworld"], "MIN.xml")
    d = full_list_diff.differences(full, mini, roots=roots)
    check("4 full-only excludes minimal ids and the mod under test",
          d["full_only"] == ["x.pool", "x.deponly", "x.clean", "x.cam", "x.plain", "x.gone"], d["full_only"])
    check("4 pool member = depends on graffiti AND ships a ModExtension_Graffiti mark",
          d["pool_members"] == [{"packageId": "x.pool", "name": "Pool Marks", "markDefs": ["X_Mark"]}], d["pool_members"])
    check("4 cleaning name-match", [x["packageId"] for x in d["cleaning"]] == ["x.clean"], d["cleaning"])
    check("4 camera name-match", [x["packageId"] for x in d["camera"]] == ["x.cam"], d["camera"])
    check("4 a mod with no folder is named not_installed", d["not_installed"] == ["x.gone"], d["not_installed"])


COMPAT_REQ = {"spree_wall.compat_sacredgraffiti_marks"}


def green_doc():
    return {"mod": "Graffiti", "config": "full", "partial": False, "judge": {"model_requested": "opus"},
            "preflight": [{"name": "running_list", "status": PASS, "evidence": "identical"}],
            "expected": ["bar_a", "bar_b"],
            "bars": [{"id": "bar_a", "status": PASS}, {"id": "bar_b", "status": PASS},
                     {"id": "spree_wall.site_ready_spree_wall", "status": PASS, "functional": True}],
            "compat": [{"id": "spree_wall.compat_sacredgraffiti_marks", "status": PASS, "compat": True}],
            "full_list_differences": {"pool_members": [], "cleaning": [], "camera": [], "full_only": ["x.y"],
                                      "not_installed": []}}


def verdict(d):
    return northstar_full.full_rung_verdict(d, expected=["bar_a", "bar_b"], compat_required=COMPAT_REQ)


def t5_verdict():
    ok, why = verdict(green_doc())
    check("5 a clean judged full-list doc is GREEN", ok, why)
    defects = {
        "config current": lambda d: d.update(config="current"),
        "running_list FAIL": lambda d: d["preflight"][0].update(status=FAIL),
        "running_list absent": lambda d: d.update(preflight=[]),
        "refused": lambda d: d.update(refused="x"),
        "partial": lambda d: d.update(partial=True),
        "not judged": lambda d: d.pop("judge"),
        "a bar UNMEASURED": lambda d: d["bars"][1].update(status=UNMEASURED),
        "a functional row FAIL": lambda d: d["bars"][2].update(status=FAIL),
        "an expected bar missing": lambda d: d["bars"].pop(0),
        "a compat row in bars": lambda d: d["bars"].append({"id": "spree_wall.compat_x", "status": PASS}),
        "no compat section": lambda d: d.pop("compat"),
        "no differences": lambda d: d.pop("full_list_differences"),
        "differences errored": lambda d: d.update(full_list_differences={"error": "boom"}),
        "differences lists None (blind)": lambda d: d.update(full_list_differences={
            "pool_members": None, "cleaning": None, "camera": None}),
        "differences saw no full-only id": lambda d: d["full_list_differences"].update(full_only=[]),
        "differences left ids unclassified": lambda d: d["full_list_differences"].update(not_installed=["x.y"]),
        "the doc shrank its own expected+bars": lambda d: d.update(expected=["bar_a"], bars=[d["bars"][0]]),
        "a compat row missing": lambda d: d.update(compat=[]),
        "another mod's doc": lambda d: d.update(mod="Other"),
    }
    for name, f in defects.items():
        d = copy.deepcopy(green_doc())
        f(d)
        ok, why = verdict(d)
        check("5 NOT GREEN when %s" % name, not ok and why, why)
    exp, src = northstar_full.authoritative_expected()
    check("5 authoritative expected bars come from Graffiti's VALIDATED walk", len(exp) >= 8 and "VALIDATED" in src,
          (exp, src))
    real = copy.deepcopy(green_doc())
    real["bars"] = [{"id": e, "status": PASS} for e in exp] + [real["bars"][2]]
    real["compat"] = [{"id": i, "status": UNMEASURED} for i in northstar_full.compat_ids_required()]
    ok, why = northstar_full.full_rung_verdict(real)
    check("5 authoritative sources: a doc with every walk bar PASS and both compat rows is GREEN", ok, why)
    check("5 compat rows required = one per foreign member", northstar_full.compat_ids_required() == {
        "spree_wall.compat_sacredgraffiti_marks", "spree_wall.compat_graffitiimperial_marks"})
    real["bars"] = real["bars"][1:]
    ok, why = northstar_full.full_rung_verdict(real)
    check("5 authoritative sources: one walk bar absent is NOT GREEN", not ok, why)
    p = os.path.join(tempfile.mkdtemp(), "g.json")
    json.dump(green_doc(), open(p, "w"))
    check("5 --check exits 1 on the toy doc (its bars are not Graffiti's walk)", northstar_full.main(["--check", p]) == 1)
    check("5 a pre-existing --out refuses before any step (exit 2)",
          northstar_full.main(["--out", p, "--no-quicktest", "--no-record"]) == 2)
    rc, out = northstar_full._run(["/nonexistent/binary"], 5)
    check("5 a step that cannot start is rc 2, no exception", rc == 2 and "could not start" in out, out)


def t6_tiers():
    """PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS (owner 2026-11-02: "small mod lists should always be the way to test
    until a final verification pass on the whole huge mod list"). GRAFFITI A1 FAILed on a 23-mod game against the
    316-mod list: a small game is another tier, UNMEASURED for the final check, and the small proof passes on any game
    that holds Graffiti, Core and every DLC."""
    small = list(pf.CORE_AND_DLC) + ["mandrake.rm.graffiti"] + ["x.m%d" % i for i in range(16)]
    full = small + ["y.f%d" % i for i in range(293)]
    game = MockGame(mods=tuple(small))
    with FastSession(transport=MockTransport(game), strict=False) as s:
        c = pf.check_running_list(s, write_list(full))
        check("6 a 23-mod game against a 316-mod list is UNMEASURED (another tier), never FAIL",
              c.status == UNMEASURED and "not the full list" in c.evidence, c.evidence)
        need = cli.needs_for(["Graffiti"])
        check("6 Graffiti's needs: Core, every DLC, its own packageId",
              need[:len(pf.CORE_AND_DLC)] == list(pf.CORE_AND_DLC) and "mandrake.rm.graffiti" in need, need)
        c = pf.check_needed_mods(s, need)
        check("6 the small game holds Graffiti's needs: PASS", c.status == PASS, c.evidence)
        c = pf.check_needed_mods(s, need + ["mandrake.rm.sacredgraffiti"])
        check("6 a need not running is UNMEASURED 'not in the running load' (a restage reason), never FAIL",
              c.status == UNMEASURED and c.evidence.startswith("not in the running load"), c.evidence)
    game = MockGame(mods=tuple(full))
    with FastSession(transport=MockTransport(game), strict=False) as s:
        check("6 the full game holds the small needs too", pf.check_needed_mods(s, need).status == PASS)
        c = pf.check_running_list(s, write_list(full[:-1]))
        check("6 on the full tier a difference still FAILs", c.status == FAIL, c.evidence)
    check("6 exit codes: PASS 0, FAIL 1, UNMEASURED 2",
          (cli.exit_code(PASS), cli.exit_code(FAIL), cli.exit_code(UNMEASURED)) == (0, 1, 2))
    d = tempfile.mkdtemp()
    ab = os.path.join(d, "About.xml")
    with open(ab, "w") as f:
        f.write("<ModMetaData><packageId>A.B</packageId><modDependencies><li><packageId>brrainz.harmony</packageId>"
                "</li></modDependencies></ModMetaData>")
    check("6 about_needs: its packageId then its dependencies, lower case", pf.about_needs(ab) == ["a.b", "brrainz.harmony"],
          pf.about_needs(ab))
    with open(ab, "w") as f:
        f.write("<ModMetaData><name>x</name></ModMetaData>")
    check("6 an About.xml with no packageId cannot say what it needs: raises", _raises_any(pf.about_needs, ab))
    small_doc = copy.deepcopy(green_doc())
    small_doc.update(config="current", preflight=[])
    small_doc.pop("full_list_differences")
    ok, why = northstar_full.full_rung_verdict(small_doc, expected=["bar_a", "bar_b"], compat_required=(), tier="small")
    check("6 small tier: no running_list, no differences, current config: GREEN", ok, why)
    ok, _ = northstar_full.full_rung_verdict(small_doc, expected=["bar_a", "bar_b"], compat_required=COMPAT_REQ)
    check("6 the same doc is NOT the full rung", not ok)
    bad = copy.deepcopy(small_doc)
    bad["bars"][1]["status"] = FAIL
    ok, _ = northstar_full.full_rung_verdict(bad, expected=["bar_a", "bar_b"], compat_required=(), tier="small")
    check("6 small tier: a FAIL bar is still NOT GREEN", not ok)


def _raises_any(fn, *a):
    try:
        fn(*a)
    except Exception:       # noqa: BLE001
        return True
    return False


def main():
    t1_running_list()
    t2_mock_run()
    t3_record()
    t3b_compat_partition()
    t4_differences()
    t5_verdict()
    t6_tiers()
    print("RESULT: %s (%d failure(s))" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
