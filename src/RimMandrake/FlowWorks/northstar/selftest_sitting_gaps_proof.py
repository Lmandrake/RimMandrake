"""Offline checks for sitting_gaps_proof.py: the pure verdicts can go red, and every FakeBridge fault turns exactly its own
rows (the mutation harness). No bridge."""
import contextlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sitting_gaps_proof as G  # noqa: E402

fails = []


def check(name, cond):
    print("%-4s  %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        fails.append(name)


# ---- pure verdicts: each bar has a PASS, a can-fail and an UNMEASURED
ok_step = {"step": "WorldDrawLayer_Rivers.RegenerateNow", "status": "ok"}
check("river: clean redraw PASS", G.river_verdict(True, True, 0, ok_step, [])[0] == "PASS")
check("can-fail river: step threw", G.river_verdict(True, True, 0, dict(ok_step, status="failed"), [])[:2] == ("FAIL", "MOD"))
check("can-fail river: exception line", G.river_verdict(True, True, 0, ok_step, ["InvalidOperationException"])[0] == "FAIL")
check("river: setting off UNMEASURED/SITE", G.river_verdict(False, True, 0, ok_step, [])[:2] == ("UNMEASURED", "SITE"))
check("river: no rivers UNMEASURED/SITE", G.river_verdict(True, True, 0, ok_step, [], 0)[:2] == ("UNMEASURED", "SITE"))
check("river: lost journal is no clean log", G.river_verdict(True, True, 3, ok_step, [])[:2] == ("UNMEASURED", "HARNESS"))
check("river: dead sentinel is no clean log", G.river_verdict(True, False, 0, ok_step, [])[:2] == ("UNMEASURED", "HARNESS"))

conv, rows, reac = G.def_census()
check("census reads the shipped converters", len(conv) >= 3 and any(c[0] == "RM_FueledStill" for c in conv))
check("census: shipped content cannot stage the converter scene", G.census_verdict("converter", conv, rows, reac)[:2] == ("UNMEASURED", "SITE"))
check("census: shipped content cannot stage the reactor scene", G.census_verdict("reactor", conv, rows, reac)[:2] == ("UNMEASURED", "SITE"))
planted = dict(rows, RM_Liquid_Test=[("cool", "Crude", "RM_Liquid_Other")])
check("census: a planted second product makes a stageable pair (and the row says the stager is owed)",
      G.converter_pairs(conv, planted) and G.census_verdict("converter", conv, planted, reac)[:2] == ("UNMEASURED", "HARNESS"))
check("census: a planted second reaction is stageable", G.census_verdict("reactor", conv, rows, reac + ["RM_Reaction_X"])[1] == "HARNESS")
check("census never PASSes", all(G.census_verdict(k, conv, r, x)[0] != "PASS" for k in ("converter", "reactor")
                                  for r in (rows, planted) for x in (reac, reac + ["X"])))

lit = G.step_litres(G.SALT, "distill")
check("salt distil step read from the registry (400 L -> 200 L)", lit == (400.0, 200.0))
check("icy water has the Crude cool step the re-scope relies on", ("cool", "Crude", "RM_Liquid_FreshWater") in rows.get(G.ICY, []))
sv = dict(stood=True, reserve=2000, icy0=2000, icy1=2000, salt0=20000, salt1=8000, out0=0, out1=6000, inspect=["Turning x"])
check("still PASS", G.still_verdict(sv, 0.5)[0] == "PASS")
check("can-fail still: salt starved", G.still_verdict(dict(sv, salt1=20000, out1=0), 0.5)[:2] == ("FAIL", "MOD"))
check("can-fail still: reserve broken", G.still_verdict(dict(sv, icy1=0), 0.5)[:2] == ("FAIL", "MOD"))
check("can-fail still: product not salt x ratio", G.still_verdict(dict(sv, out1=5000), 0.5)[:2] == ("FAIL", "MOD"))
check("still: out of fuel UNMEASURED/SITE", G.still_verdict(dict(sv, salt1=20000, out1=0, inspect=["Out of fuel"]), 0.5)[:2] == ("UNMEASURED", "SITE"))
check("still: icy above the reserve UNMEASURED/SITE", G.still_verdict(dict(sv, icy0=2500, icy1=2500), 0.5)[:2] == ("UNMEASURED", "SITE"))
check("still: not stood UNMEASURED/SITE", G.still_verdict(dict(sv, stood=False), 0.5)[:2] == ("UNMEASURED", "SITE"))
check("still: a tank read missing UNMEASURED/HARNESS", G.still_verdict(dict(sv, out1=None), 0.5)[:2] == ("UNMEASURED", "HARNESS"))
check("still geometry: three tanks touch the still footprint, none overlaps it",
      all(max(abs(t[0] + dx - (G.STILL[0] + sx)) for dx in (0, 1) for sx in (0, 1)) >= 1 for t in (G.ICY_TANK, G.SALT_TANK, G.OUT_TANK))
      and all(any(abs(t[0] + dx - G.STILL[0] - sx) <= 1 and abs(t[1] + dz - G.STILL[1] - sz) <= 1
                  for dx in (0, 1) for dz in (0, 1) for sx in (0, 1) for sz in (0, 1)) for t in (G.ICY_TANK, G.SALT_TANK, G.OUT_TANK))
      and not any({(t[0] + dx, t[1] + dz) for dx in (0, 1) for dz in (0, 1)} & {(G.STILL[0] + sx, G.STILL[1] + sz) for sx in (0, 1) for sz in (0, 1)}
                  for t in (G.ICY_TANK, G.SALT_TANK, G.OUT_TANK)))

check("railing PASS", G.railing_verdict(True, 0, 6, ["WoodLog"] * 6, [])[0] == "PASS")
check("can-fail railing: stuff null", G.railing_verdict(True, 0, 6, [None] * 6, [])[0] == "FAIL")
check("can-fail railing: error line", G.railing_verdict(True, 0, 6, ["WoodLog"], ["x is madeFromStuff but stuff=null"])[0] == "FAIL")
check("railing: none placed UNMEASURED/SITE", G.railing_verdict(True, 0, 0, [], [])[:2] == ("UNMEASURED", "SITE"))

kv = G.parse
check("faucet tab PASS", G.faucet_tab_verdict("cat", "d", kv("ok=False"), kv("ok=True"), [], True)[0] == "PASS")
check("can-fail tab: bare ground accepted", G.faucet_tab_verdict("cat", "d", kv("ok=True"), kv("ok=True"), [], True)[0] == "FAIL")
check("can-fail tab: not listed", G.faucet_tab_verdict("cat", None, kv("ok=False"), kv("ok=True"), [], True)[0] == "FAIL")
check("can-fail tab: log error", G.faucet_tab_verdict("cat", "d", kv("ok=False"), kv("ok=True"), ["x"], True)[0] == "FAIL")
check("can-fail tab: FlowWorks' own category missing", G.faucet_tab_verdict(None, None, {}, {}, [], True, 5)[:2] == ("FAIL", "MOD"))
check("tab: an empty category listing is the tool UNMEASURED/HARNESS", G.faucet_tab_verdict(None, None, {}, {}, [], True, 0)[:2] == ("UNMEASURED", "HARNESS"))
check("tab: unreadable log never PASS", G.faucet_tab_verdict("cat", "d", kv("ok=False"), kv("ok=True"), [], False)[0] == "UNMEASURED")
d = G.DRINK_DL
check("drink dL is 1.5 L of decilitres", d == 15)
check("T30 PASS", G.faucet_drink_verdict(1000, 1000 - d, ["RM_DrinkFromFaucet"], 0.15, 0.65, [])[0] == "PASS")
check("can-fail T30: no drink", G.faucet_drink_verdict(1000, 1000, ["Wait_Wander"], 0.15, 0.15, [])[0] == "FAIL")
check("can-fail T30: rough thought", G.faucet_drink_verdict(1000, 1000 - d, ["RM_DrinkFromFaucet"], 0.1, 0.6,
                                                            ["RM_Thought_DrankRough"])[0] == "FAIL")
check("can-fail T30: not a whole drink", G.faucet_drink_verdict(1000, 990, ["RM_DrinkFromFaucet"], 0.1, 0.6, [])[0] == "FAIL")
check("T30: drank elsewhere UNMEASURED/SITE", G.faucet_drink_verdict(1000, 1000, ["RM_DrinkFromTerrain"], 0.1, 0.6, [])[:2] == ("UNMEASURED", "SITE"))
per = {lk: dict(styled=True, path="RimMandrake/FlowWorks/Faucet/%s/RM_PipeFaucet" % lk, badTex=False) for lk in G.LOOKS}
check("looks PASS", G.look_verdict(per)[0] == "PASS")
check("can-fail looks: Scrapper everywhere", G.look_verdict(dict(per, Modern=dict(per["Scrapper"])))[0] == "FAIL")
check("can-fail looks: pink", G.look_verdict(dict(per, Modern=dict(per["Modern"], badTex=True)))[0] == "FAIL")
check("looks: unstyled pipe UNMEASURED/SITE", G.look_verdict(dict(per, Modern=dict(per["Modern"], styled=False)))[:2] == ("UNMEASURED", "SITE"))
gr = {s: dict(spawned=True, path="RimMandrake/FlowWorks/Guardrail", chain=["Graphic_Appearances"], badTex=False) for s in ("WoodLog", "Steel")}
check("guardrail PASS", G.guardrail_verdict(gr)[0] == "PASS")
check("can-fail guardrail: fence art", G.guardrail_verdict(dict(gr, Steel=dict(gr["Steel"], path="Things/Fence_Atlas")))[0] == "FAIL")
check("guardrail: not spawned UNMEASURED/SITE", G.guardrail_verdict(dict(gr, Steel=dict(gr["Steel"], spawned=False)))[:2] == ("UNMEASURED", "SITE"))
c = (10, 10)
check("reel E: straight east is clean", G.reel_axis_problems(c, 1, [12.1, 11.0], [[12, 10], [13, 10], [14, 10]]) == [])
check("can-fail reel E: west nozzle + U-turn", len(G.reel_axis_problems(c, 1, [9.9, 11.0], [[9, 10], [10, 10], [12, 10]])) >= 2)
check("reel S: straight south is clean", G.reel_axis_problems(c, 2, [11.0, 9.9], [[10, 9], [10, 8]]) == [])
check("reel target leaves the footprint along the facing", G.reel_target(c, 0) == (10, 12 + G.REEL_REACH)
      and G.reel_target(c, 3) == (9 - G.REEL_REACH, 10))
check("reel verdict: refused lay UNMEASURED/SITE", G.reel_verdict({r: dict(laid=r != 2, problems=[]) for r in range(4)})[:2] == ("UNMEASURED", "SITE"))
check("s3 PASS", G.s3_verdict({"A": True, "B": True}, {"A": [], "B": []})[0] == "PASS")
check("can-fail s3: over the pump", G.s3_verdict({"A": True, "B": True}, {"A": [(9, 32)], "B": []})[0] == "FAIL")
check("s3: unlaid UNMEASURED/SITE", G.s3_verdict({"A": False, "B": True}, {})[:2] == ("UNMEASURED", "SITE"))
fb = G.s3_forbidden((0, 0), "A")
check("s3: hose A may not cross the pump, battery or reel B; its own reel is allowed",
      G.S3["pump"] in fb and G.S3["battery"] in fb and G.S3["reelB"] in fb and G.S3["reelA"] not in fb)
try:
    import water_scenes_walk as WS
    g = WS.s3_geom()
    sx, sz = WS.INTERIOR["S3"]
    sh = lambda p: (p[0] - sx, p[1] - sz + 30)  # noqa: E731
    same = all(sh(g[k]) == G.S3[k] for k in ("pump", "reelA", "reelB", "intake", "outflow", "battery")) \
        and sorted(sh(p) for p in g["pond"]) == sorted(G.S3["pond"]) and [sh(p) for p in g["canal"]] == G.S3["canal"]
    check("the S3 copy equals water_scenes_walk.s3_geom shifted to plot-local", same)
except Exception as ex:  # noqa: BLE001
    check("water_scenes_walk.s3_geom importable offline (%r)" % ex, False)
found = {q: True for q in G.SEARCH_QUERIES}
check("search PASS", G.search_verdict(True, {"t": 1}, found, False)[0] == "PASS")
check("can-fail search: one query misses", G.search_verdict(True, {"t": 1}, dict(found, pieces=False), False)[0] == "FAIL")
check("search: control shows the row UNMEASURED/HARNESS", G.search_verdict(True, {"t": 1}, found, True)[:2] == ("UNMEASURED", "HARNESS"))
W = lambda t, dug, m: kv("terrain=%s dug=%s waterM=%s" % (t, dug, m))  # noqa: E731
check("canal-lake PASS", G.canal_lake_verdict(W("WaterDeep", "True", 3), W("WaterDeep", "False", 3))[0] == "PASS")
check("can-fail canal-lake: two defs", G.canal_lake_verdict(W("RM_WaterChestDeepStill", "True", 3), W("WaterDeep", "False", 3))[0] == "FAIL")
check("canal-lake: dry canal UNMEASURED/SITE", G.canal_lake_verdict(W("Soil", "True", 0), W("WaterDeep", "False", 3))[:2] == ("UNMEASURED", "SITE"))
check("canal-lake: unequal depth UNMEASURED/SITE", G.canal_lake_verdict(W("WaterShallow", "True", 1), W("WaterDeep", "False", 3))[:2] == ("UNMEASURED", "SITE"))
lg = os.path.join(tempfile.mkdtemp(), "Player.log")
with open(lg, "w") as f:
    f.write("RimWorld 1.6\nConfig error in RM_PipeFaucet: x\nRM_PipeFaucet loaded fine\n")
check("player log: an error line naming the faucet is found, a plain line is not", G.player_log_errors(lg) == (True, ["Config error in RM_PipeFaucet: x"]))
check("player log: unreadable is not clean", G.player_log_errors(lg + ".missing") == (False, []))
check("every row names an item and a criterion", all(G.ROW_ITEM.get(r) and G.ROW_ITEM[r][1] for r in G.ROW_IDS))
check("every row belongs to one scene", sorted(sum(G.SCENE_ROWS.values(), [])) == sorted(G.ROW_IDS))

# ---- the mutation harness: each fault turns exactly its rows (the census rows are UNMEASURED/SITE on shipped content)
BASE = {"REACTOR_NEXT_REACTION_RUNS": ("UNMEASURED", "SITE")}
U, S, H, F, M = "UNMEASURED", "SITE", "HARNESS", "FAIL", "MOD"
EXPECT = {"": {},
          "river_throws": {"RIVER_LAYER_REDRAWS_CLEAN": (F, M)},
          "river_off": {"RIVER_LAYER_REDRAWS_CLEAN": (U, S)},
          "log_dead": {"RIVER_LAYER_REDRAWS_CLEAN": (U, H), "RAILING_HAS_STUFF": (U, H), "FAUCET_LOOKS_RESOLVE": (U, H)},
          "rail_nostuff": {"RAILING_HAS_STUFF": (F, M)},
          "rail_none": {"RAILING_HAS_STUFF": (U, S)},
          "no_pipenet_tab": {"FAUCET_TAB_PIPE_ONLY": (F, M)},
          "faucet_anywhere": {"FAUCET_TAB_PIPE_ONLY": (F, M)},
          "faucet_untabbed": {"FAUCET_TAB_PIPE_ONLY": (F, M)},
          "faucet_log_error": {"FAUCET_TAB_PIPE_ONLY": (F, M)},
          "faucet_dry": {"T30_pipe_faucet": (F, M)},
          "faucet_rough": {"T30_pipe_faucet": (F, M)},
          "other_water": {"T30_pipe_faucet": (U, S)},
          "faucet_nomatch": {"FAUCET_LOOKS_RESOLVE": (F, M), "FAUCET_TAKES_MODERN": (F, M)},
          "pipe_style_refused": {"FAUCET_LOOKS_RESOLVE": (U, S), "FAUCET_TAKES_MODERN": (U, S)},
          "rail_fence_art": {"GUARDRAIL_ATLAS_RESOLVES": (F, M)},
          "reel_fixed_west": {"REEL_FACINGS_LAY_ALONG_AXIS": (F, M)},
          "reel_lay_refused": {"REEL_FACINGS_LAY_ALONG_AXIS": (U, S)},
          "hose_over_pump": {"S3_HOSES_ON_BARE_GROUND": (F, M)},
          "search_misses": {"SETTINGS_SEARCH_FINDS_ROW": (F, M)},
          "search_unfiltered": {"SETTINGS_SEARCH_FINDS_ROW": (U, H)},
          "no_dialog": {"SETTINGS_SEARCH_FINDS_ROW": (U, H)},
          "canal_two_defs": {"CANAL_LAKE_ONE_DEF": (F, M)},
          "canal_dry": {"CANAL_LAKE_ONE_DEF": (U, S)},
          "still_starves": {"CONVERTER_BIG_RECIPE_RUNS": (F, M)},
          "still_no_reserve": {"CONVERTER_BIG_RECIPE_RUNS": (F, M)},
          "still_no_fuel": {"CONVERTER_BIG_RECIPE_RUNS": (U, S)}}
check("every FakeBridge fault has an expectation", sorted(k for k in EXPECT if k) == sorted(G.FakeBridge.FAULTS))
tmp = tempfile.mkdtemp()
for fault, want in EXPECT.items():
    out = os.path.join(tmp, "sg_%s.json" % (fault or "clean"))
    with contextlib.redirect_stdout(io.StringIO()):
        G.main(["--mock", out] + (["--mock-faults", fault] if fault else []))
    got_rows = json.load(open(out))["rows"]
    got = {r["id"]: (r["detail"].get("mock"), r["class"]) for r in got_rows}
    bad = {k: v for k, v in got.items() if v[0] != "PASS"}
    wanted = dict(BASE, **want)
    check("mock %-18s -> %s" % (fault or "clean", want or "all PASS but the census"), bad == wanted and len(got_rows) == len(G.ROW_IDS)
          and all(r["status"] == "SKIP" for r in got_rows))
    if bad != wanted:
        print("      got  %s\n      want %s" % (bad, wanted))
print("%d FAIL" % len(fails))
sys.exit(1 if fails else 0)
