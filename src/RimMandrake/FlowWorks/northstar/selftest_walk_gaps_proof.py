"""Offline checks for walk_gaps_proof.py: the pure verdicts and every FakeBridge fault's expected row. No bridge."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import walk_gaps_proof as W  # noqa: E402

fails = []


def check(name, cond):
    print("%-4s  %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        fails.append(name)


T = lambda s: W.parse(s)  # noqa: E731
b, a = T("TRAP descents=0 pos=1,1 held=False last=none"), T("TRAP descents=1 pos=1,1 held=True last=Human7@1,1")
check("decon: fell and held: PASS", W.decon_verdict(b, a, False, "Thing_Human7")[0] == "PASS")
check("can-fail decon: no descent: FAIL", W.decon_verdict(b, b, False, "Thing_Human7")[0] == "FAIL")
check("decon: cover still there = nobody did the job: UNMEASURED/SITE", W.decon_verdict(b, a, True, "Human7") == ("UNMEASURED", "SITE"))
check("decon: rider already held before: UNMEASURED", W.decon_verdict(a, a, False, "Human7")[0] == "UNMEASURED")
L = lambda r: T("LADDER present=True raised=%s" % r)  # noqa: E731
check("ladder raised as wanted: PASS", W.ladder_wait_verdict(L("True"), True)[0] == "PASS")
check("can-fail ladder: not raised: FAIL", W.ladder_wait_verdict(L("False"), True)[0] == "FAIL")
check("no ladder: UNMEASURED", W.ladder_wait_verdict(T("LADDER present=False"), True)[0] == "UNMEASURED")
PT = lambda f, h: T("PITTRAVEL pawn=x free=%s held=%s setting=True" % (f, h))  # noqa: E731
check("flyer free, not held: PASS", W.travel_free_verdict(PT("True", "False"), True)[0] == "PASS")
check("can-fail flyer held: FAIL", W.travel_free_verdict(PT("False", "True"), True)[0] == "FAIL")
check("person held control: PASS", W.travel_free_verdict(PT("False", "True"), False)[0] == "PASS")
check("nobody on the square: UNMEASURED", W.travel_free_verdict(T("PITTRAVEL pawn=none"), True)[0] == "UNMEASURED")
check("setting off: UNMEASURED", W.travel_free_verdict(T("PITTRAVEL pawn=x free=True held=False setting=False"), True)[0] == "UNMEASURED")
check("thrown: duck clean, person hurt: PASS", W.thrown_verdict([], ["Bruise"], True)[0] == "PASS")
check("can-fail thrown: duck hurt: FAIL", W.thrown_verdict(["Bruise"], ["Bruise"], True)[0] == "FAIL")
check("thrown control unhurt = blind read: UNMEASURED", W.thrown_verdict([], [], True)[0] == "UNMEASURED")
check("tanks: moved toward one level, conserved: PASS", W.tanks_verdict([10, 40, 80], [40, 40, 50], [100, 100, 100])[0] == "PASS")
check("can-fail tanks: nothing moved: FAIL", W.tanks_verdict([10, 40, 80], [10, 40, 80], [100, 100, 100])[0] == "FAIL")
check("can-fail tanks: units lost: FAIL", W.tanks_verdict([10, 40, 80], [40, 40, 40], [100, 100, 100])[0] == "FAIL")
check("tanks unread: UNMEASURED", W.tanks_verdict([None, 40, 80], [10, 40, 80], [100, 100, 100])[0] == "UNMEASURED")
check("ponds level within 1 cm: PASS", W.ponds_level_verdict(5, (900, 0), (450, 450), 9, True, True)[0] == "PASS")
check("can-fail ponds: no move: FAIL", W.ponds_level_verdict(0, (900, 0), (900, 0), 9, True, False)[0] == "FAIL")
check("ponds unlinked: UNMEASURED/SITE", W.ponds_level_verdict(0, (900, 0), (900, 0), 9, False, False) == ("UNMEASURED", "SITE"))
check("ponds still closing at the bound: UNMEASURED", W.ponds_level_verdict(3, (9000, 0), (6000, 3000), 9, True, True)[0] == "UNMEASURED")
check("ponds level but never read flowing: FAIL", W.ponds_level_verdict(5, (900, 0), (450, 450), 9, True, False)[0] == "FAIL")
check("no-mix: nothing moved + readout: PASS", W.ponds_nomix_verdict(0, (5, 1), (5, 1), True, "different liquids never mix")[0] == "PASS")
check("can-fail no-mix: moved: FAIL", W.ponds_nomix_verdict(2, (5, 1), (4, 2), True, "")[0] == "FAIL")
PP = "PUMPPORTS N=none E=reel:14:c S=free:15:c+free:16:r W=pipe coupled=2 corner=1 cornerCoupled=0"
sd, nm = W.ports_parse(PP)
check("ports parse: sides and counts", sd["S"] == ["free:15:c", "free:16:r"] and sd["N"] == [] and nm["cornerCoupled"] == 0)
check("ports: pipe W + coupled reel E: PASS", W.ports_sides_verdict(sd)[0] == "PASS")
check("can-fail ports: reel on E refused: FAIL", W.ports_sides_verdict(dict(sd, E=["reel:14:r"]))[0] == "FAIL")
check("ports: no pipe staged: UNMEASURED/SITE", W.ports_sides_verdict(dict(sd, W=[])) == ("UNMEASURED", "SITE"))
check("ports: lower id kept, other refused: PASS", W.ports_one_per_side_verdict(sd)[0] == "PASS")
check("can-fail ports: both coupled: FAIL", W.ports_one_per_side_verdict(dict(sd, S=["free:15:c", "free:16:c"]))[0] == "FAIL")
check("can-fail ports: higher id kept: FAIL", W.ports_one_per_side_verdict(dict(sd, S=["free:15:r", "free:16:c"]))[0] == "FAIL")
check("ports: one end only: UNMEASURED/SITE", W.ports_one_per_side_verdict(dict(sd, S=["free:15:c"])) == ("UNMEASURED", "SITE"))
check("ports: corner refused: PASS", W.ports_corner_verdict(nm)[0] == "PASS")
check("can-fail ports: corner coupled: FAIL", W.ports_corner_verdict(dict(nm, cornerCoupled=1))[0] == "FAIL")
check("ports: unread: UNMEASURED/HARNESS", W.ports_corner_verdict({}) == ("UNMEASURED", "HARNESS"))
check("no-mix: enum word readout: PASS", W.ponds_nomix_verdict(0, (5, 1), (5, 1), True, " | DifferentLiquids")[0] == "PASS")
check("no hook is listed missing", W.MISSING_HOOKS == {})
check("every row names an item and a criterion", all(W.ROW_ITEM.get(r) and W.ROW_ITEM[r][1] for r in W.ROW_IDS))
check("every row belongs to one scene", sorted(sum(W.SCENE_ROWS.values(), [])) == sorted(W.ROW_IDS))

EXPECT = {"": {}, "no_worker": {"COVER_DECON_DROPS_RIDER": ("UNMEASURED", "SITE")},
          "decon_no_fall": {"COVER_DECON_DROPS_RIDER": ("FAIL", "MOD")},
          "ladder_idle": {"LADDER_RAISED_FROM_BELOW": ("FAIL", "MOD"), "LADDER_NO_LOWER_FROM_BELOW": ("UNMEASURED", "SITE")},
          "lower_below": {"LADDER_NO_LOWER_FROM_BELOW": ("FAIL", "MOD")},
          "flyer_held": {"TRAVEL_FLYER_FREE_ON_FLOOR": ("FAIL", "MOD")},
          "person_free": {"TRAVEL_PERSON_HELD_CONTROL": ("FAIL", "MOD")},
          "no_marked": {"TRAVEL_MARKED_FREE": ("UNMEASURED", "SITE")},
          "thrown_hurt": {"TRAVEL_THROWN_FLYER_UNHURT": ("FAIL", "MOD")},
          "blind_health": {"TRAVEL_THROWN_FLYER_UNHURT": ("UNMEASURED", "HARNESS")},
          "store_only": {"TANKS_JOINED_ONE_LEVEL": ("FAIL", "MOD")},
          "no_link": {"PONDS_DIFFERENT_LIQUIDS_NO_MIX": ("UNMEASURED", "SITE"), "PONDS_HOSE_LEVEL": ("UNMEASURED", "SITE")},
          "pipe_gap": {"PONDS_DIFFERENT_LIQUIDS_NO_MIX": ("UNMEASURED", "SITE"), "PONDS_HOSE_LEVEL": ("UNMEASURED", "SITE")},
          "mixes": {"PONDS_DIFFERENT_LIQUIDS_NO_MIX": ("FAIL", "MOD")},
          "no_level": {"PONDS_HOSE_LEVEL": ("FAIL", "MOD")},
          "no_levellink": {"PONDS_DIFFERENT_LIQUIDS_NO_MIX": ("UNMEASURED", "HARNESS"), "PONDS_HOSE_LEVEL": ("UNMEASURED", "HARNESS")},
          "port_shared": {"PORTS_ONE_HOSE_PER_SIDE": ("FAIL", "MOD")},
          "corner_couples": {"PORTS_CORNER_REFUSED": ("FAIL", "MOD")},
          "no_lay": {"PORTS_ONE_HOSE_PER_SIDE": ("UNMEASURED", "SITE"), "PORTS_CORNER_REFUSED": ("UNMEASURED", "SITE")}}
tmp = tempfile.mkdtemp()
for fault, want in EXPECT.items():
    out = os.path.join(tmp, "wg_%s.json" % (fault or "clean"))
    argv = ["--mock", out] + (["--mock-faults", fault] if fault else [])
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        W.main(argv)
    got = {r["id"]: (r["detail"].get("mock"), r["class"]) for r in json.load(open(out))["rows"]}
    bad = {k: v for k, v in got.items() if v[0] != "PASS"}
    check("mock %-14s -> %s" % (fault or "clean", want or "all PASS"), bad == want and all(r["status"] == "SKIP" for r in json.load(open(out))["rows"]))
out = os.path.join(tmp, "wg_np.json")
with contextlib.redirect_stdout(io.StringIO()):
    W.main(["--mock", out, "--mock-faults", "no_proofs"])
check("no_proofs: every row UNMEASURED/HARNESS, none FAIL",
      all(r["detail"].get("mock") == "UNMEASURED" and r["class"] == "HARNESS" for r in json.load(open(out))["rows"]))

# ---- the PONDS rig geometry (P4, 2026-10-22: three belt runs read linked=False, moves=0 on the tank layout)
check("pond rig: the shipped layout makes one link (no problems)", W.pond_rig_problems(W.POND_RIG) == [])
tp = W.pond_rig_problems(W.TANK_RIG_20261022)
check("pond rig: the belt runs' tank layout is refused, naming the tank and the split", any("tank" in p for p in tp)
      and any("not on one pipe run" in p for p in tp))
cut = dict(W.POND_RIG, pipes=[c for c in W.POND_RIG["pipes"] if c != (12, 4)])
check("pond rig: a pipe run cut in two is refused", any("not on one pipe run" in p for p in W.pond_rig_problems(cut)))
check("pond rig: an end beside a pipe couples (no open port) and is refused",
      any("couples to a pipe" in p for p in W.pond_rig_problems(dict(W.POND_RIG, pipes=W.POND_RIG["pipes"] + [(4, -3)]))))
check("pond rig: an end beside the wrong pool is refused",
      any("other pool" in p for p in W.pond_rig_problems(dict(W.POND_RIG, pools=[(0, -4), (0, -1)], ends=[(3, -2), (3, 0)]))))
check("pond rig: an end inside its pool is refused", any("lies in a pool" in p for p in W.pond_rig_problems(dict(W.POND_RIG, ends=[(1, -3), (3, 9)]))))
check("pond rig: an end past the hose's reach is refused", any("reach" in p for p in W.pond_rig_problems(dict(W.POND_RIG, ends=[(3, -3), (3, 60)]))))
# the planted mis-coupling end to end: the old tank layout through the live path (mock) reads SITE, never PASS or FAIL
keep = W.POND_RIG
W.POND_RIG = W.TANK_RIG_20261022
try:
    out = os.path.join(tmp, "wg_tankrig.json")
    with contextlib.redirect_stdout(io.StringIO()):
        W.main(["--mock", out, "--only", "PONDS_DIFFERENT_LIQUIDS_NO_MIX,PONDS_HOSE_LEVEL"])
    rows = json.load(open(out))["rows"]
    check("planted tank rig: both PONDS rows UNMEASURED/SITE", len(rows) == 2 and all((r["detail"].get("mock"), r["class"]) == ("UNMEASURED", "SITE") for r in rows))
    check("planted tank rig: the coupling read shows one end per component",
          all(r["detail"].get("coupling") and any(c != (1, 1) and c != [1, 1] for c in r["detail"]["coupling"]) for r in rows))
finally:
    W.POND_RIG = keep
out = os.path.join(tmp, "wg_ponds.json")
with contextlib.redirect_stdout(io.StringIO()):
    W.main(["--mock", out, "--only", "PONDS_DIFFERENT_LIQUIDS_NO_MIX,PONDS_HOSE_LEVEL"])
rows = {r["id"]: r for r in json.load(open(out))["rows"]}
check("fixed rig (mock): coupling (1,1) on both reels, linked, levelled",
      all(list(map(list, r["detail"]["coupling"])) == [[1, 1], [1, 1]] and r["detail"]["linked"] for r in rows.values())
      and rows["PONDS_HOSE_LEVEL"]["detail"]["moves"] > 0)
print("%d FAIL" % len(fails))
sys.exit(1 if fails else 0)
