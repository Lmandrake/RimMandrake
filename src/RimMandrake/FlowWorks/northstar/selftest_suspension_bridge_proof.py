"""The suspension bridge functional script runs every path offline (suspension_bridge_proof.py --mock, FakeBridge): each
section's rows are written and every mock verdict is PASS except rows marked owed. Can-fail: a FakeBridge answering a
refusal for the length row makes it FAIL. Proves the SCRIPT, never the game (live rows stay owed to FOUNDRY).

    python3 src/RimMandrake/FlowWorks/northstar/selftest_suspension_bridge_proof.py
"""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import suspension_bridge_proof as SBP  # noqa: E402


def run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = SBP.main(argv)
    return rc, buf.getvalue()


def main():
    fails = []
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "mock.json")
        rc, txt = run(["--mock", out])
        rows = json.load(open(out, encoding="utf-8"))["rows"]
        if rc != 0:
            fails.append("mock run exit %s: %s" % (rc, txt.strip().splitlines()[-1]))
        ids = [r["id"] for r in rows]
        for sec in SBP.SECTIONS:
            if not any(("== section %s" % sec) in line for line in txt.splitlines()):
                fails.append("section %s never ran" % sec)
        if any(r["status"] != "SKIP" for r in rows):
            fails.append("a mock row claimed a live verdict")
        if len(ids) != len(set(ids)):
            fails.append("duplicate row ids")
        # can-fail: a refusal where the build must pass turns the first row's mock verdict to FAIL
        orig = SBP.FakeBridge.static
        SBP.FakeBridge.static = lambda self, m, a: ("BUILD ok=False anchors=0 decks=0 blueprints=0 reason=x" if m == "ProofBuild"
                                                    else orig(self, m, a))
        try:
            rc2, _ = run(["--mock", os.path.join(d, "bad.json"), "--only", "posts"])
        finally:
            SBP.FakeBridge.static = orig
        if rc2 == 0:
            fails.append("can-fail BROKEN: a refused build still passed the mock")
        # review 2026-10-20: with NO bridge built, every row that stands on one is UNMEASURED (never a vacuous PASS, never a FAIL)
        SBP.FakeBridge.static = lambda self, m, a: ("BUILD ok=False anchors=0 decks=0 blueprints=0 reason=x" if m == "ProofBuild"
                                                    else orig(self, m, a))
        try:
            nb = os.path.join(d, "nobuild.json")
            run(["--mock", nb, "--only", "posts,grate,underpass,waters"])
        finally:
            SBP.FakeBridge.static = orig
        got = {r["id"]: r["detail"].get("mock") for r in json.load(open(nb, encoding="utf-8"))["rows"]}
        for rid in ("SB_rails_off_some_fall", "SB_rails_on_nobody_falls", "GRATE_fire_burns_people_above", "GRATE_pour_drains_to_body",
                    "GRATE_item_stays_on_deck", "UND_floor_path_walks_under", "UND_both_arrive", "UND_shallow_trench_is_a_wall",
                    "UND_item_slides_to_open_floor", "UND_shot_solid_deck", "UND_shot_grate_deck", "UND_crush_below_and_wreck",
                    "WAT_flood_damages_timber_not_steel"):
            if got.get(rid) != "UNMEASURED":
                fails.append("no bridge built: %s reads %s, want UNMEASURED" % (rid, got.get(rid)))
        # review 2026-10-20 (round 3): a SITE/harness fault reads UNMEASURED, a genuine mod fault still reads FAIL
        ocall, ostat = SBP.FakeBridge.call, SBP.FakeBridge.static

        def verdicts(name, only, call=None, static=None):
            if call:
                SBP.FakeBridge.call = call
            if static:
                SBP.FakeBridge.static = static
            try:
                path = os.path.join(d, name + ".json")
                run(["--mock", path, "--only", only])
            finally:
                SBP.FakeBridge.call, SBP.FakeBridge.static = ocall, ostat
            return {r["id"]: r["detail"].get("mock") for r in json.load(open(path, encoding="utf-8"))["rows"]}

        def noclock(self, tool, **kw):
            return {"success": False, "message": "no"} if tool == "rimworld/step_game_ticks" else ocall(self, tool, **kw)
        # the mock's data would PASS regardless of the clock, so each case feeds the answer a never-ticked game would give
        swing_none = lambda self, m, a: "SWING none" if m == "ProofSwing" else ostat(self, m, a)  # noqa: E731
        got = verdicts("noclock", "posts", call=noclock, static=swing_none)
        for rid in ("SB_load_over_rating_whole_span_falls", "SB_anchor_lost_swings_from_that_end"):
            if got.get(rid) != "UNMEASURED":
                fails.append("clock never moved: %s reads %s, want UNMEASURED" % (rid, got.get(rid)))
        got = verdicts("clockswing", "posts", static=swing_none)
        if got.get("SB_anchor_lost_swings_from_that_end") != "FAIL":
            fails.append("over-correction: anchor destroyed, clock ran, no swing reads %s, want FAIL" % got.get("SB_anchor_lost_swings_from_that_end"))
        stays = lambda self, m, a: (ostat(self, m, a).replace("SPAN none", "SPAN tier=steel load=1 rating=120 state=Over decks=2")  # noqa: E731
                                    if m == "ProofSpan" else ostat(self, m, a))
        got = verdicts("noclockjet", "jetty", call=noclock, static=stays)
        if got.get("JET_overload_drops_whole_at_root") != "UNMEASURED":
            fails.append("clock never moved: jetty row reads %s, want UNMEASURED" % got.get("JET_overload_drops_whole_at_root"))
        got = verdicts("noclockflood", "waters", call=noclock)
        if got.get("WAT_flood_damages_timber_not_steel") != "UNMEASURED":
            fails.append("clock never moved: flood row reads %s, want UNMEASURED" % got.get("WAT_flood_damages_timber_not_steel"))
        got = verdicts("norails", "posts", static=lambda self, m, a: "RAILS none" if m == "ProofRails" else ostat(self, m, a))
        for rid in ("SB_rails_off_some_fall", "SB_rails_on_nobody_falls"):
            if got.get(rid) != "UNMEASURED":
                fails.append("railings never switched: %s reads %s, want UNMEASURED" % (rid, got.get(rid)))
        got = verdicts("swingrefused", "posts", static=lambda self, m, a: "REFUSED: x" if m == "ProofSwing" else ostat(self, m, a))
        if got.get("SB_anchor_lost_swings_from_that_end") != "UNMEASURED":
            fails.append("refused swing probe reads %s, want UNMEASURED" % got.get("SB_anchor_lost_swings_from_that_end"))
        got = verdicts("noput", "underpass", static=lambda self, m, a: "REFUSED: x" if m == "ProofPutUnder" else ostat(self, m, a))
        if got.get("UND_crush_below_and_wreck") == "FAIL":
            fails.append("a pawn never put under the deck scored a mod FAIL on the crush row")
        # over-correction guard: a real mod fault (rails off, open edge, nobody falls) must still be FAIL
        got = verdicts("realfail", "posts", static=lambda self, m, a: ("KNOCK trials=20 fell=0 railed=False edge=True" if m == "ProofKnock"
                                                                        else ostat(self, m, a)))
        if got.get("SB_rails_off_some_fall") != "FAIL":
            fails.append("over-correction: rails off, open edge, 0 of 20 fell reads %s, want FAIL" % got.get("SB_rails_off_some_fall"))
        # jetty that never read Over (riders under the rating) is UNMEASURED, an Over that does not drop is FAIL
        got = verdicts("jetnotover", "jetty", static=lambda self, m, a: ostat(self, m, a).replace("state=Over", "state=Ok") if m == "ProofSpan" else ostat(self, m, a))
        if got.get("JET_overload_drops_whole_at_root") != "UNMEASURED":
            fails.append("jetty never Over reads %s, want UNMEASURED" % got.get("JET_overload_drops_whole_at_root"))
        got = verdicts("jetstays", "jetty", static=lambda self, m, a: ostat(self, m, a).replace("SPAN none", "SPAN tier=steel load=1 rating=120 state=Over decks=2") if m == "ProofSpan" else ostat(self, m, a))
        if got.get("JET_overload_drops_whole_at_root") != "FAIL":
            fails.append("over-correction: jetty Over but decks stand reads %s, want FAIL" % got.get("JET_overload_drops_whole_at_root"))
    for f in fails:
        print("FAIL " + f)
    print("suspension bridge proof mock: %d rows, %d sections, %s" % (len(ids), len(SBP.SECTIONS), "ok" if not fails else "FAIL"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
