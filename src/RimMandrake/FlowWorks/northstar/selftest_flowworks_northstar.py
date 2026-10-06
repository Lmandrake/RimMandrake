#!/usr/bin/env python3
"""Offline selftest for the FlowWorks trial site tooling (FLOWWORKS_NORTHSTAR_SITE_PREP_1).

No game, no bridge, no ModsConfig.xml: every bridge answer comes from FakeFlowWorksGame, every
host path from a temp fixture. Proves: the `flowworks` tier and its refusal guards; the
settings table equals the shipped C#; the layout honours plan 3.4; config backup/restore is
byte-exact; prep builds and saves, refuses a second overwrite and stops (exit 3, nothing
saved) without the classification tool; preflight passes the clean prepped site and REFUSES
each deliberate dirt (rain, a pre-filled plot cell, a stray pawn, a cold cell, drifted
settings, a GameCondition, a temp-terrain overlay) naming the row.
"""
import io
import json
import os
import re
import shutil
import stat
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import site_spec as S  # noqa: E402
import preflight_flowworks as PF  # noqa: E402
import prep_site as PS  # noqa: E402
from fakegame import FakeFlowWorksGame, FakeTransport  # noqa: E402
from northstar_driver import PASS, FAIL, UNMEASURED  # noqa: E402
from northstar_driver.session import FastSession  # noqa: E402
import modset_builder as M  # noqa: E402

FAILS = []
TMP = tempfile.mkdtemp(prefix="ns_fw_selftest_")


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def sub(name):
    d = os.path.join(TMP, name)
    os.makedirs(d, exist_ok=True)
    return d


# ---------------------------------------------------------------- tier
def test_tier():
    check("tier `flowworks` exists", "flowworks" in M.TIERS)
    check("tier `pits` is gone (renamed)", "pits" not in M.TIERS)
    t = M.TIERS["flowworks"]
    check("tier wants bridge + flowworks only", t["want"] == [M.BRIDGE, "mandrake.rm.flowworks"], t["want"])
    check("tier dlc True", t["dlc"] is True)
    clean = ["brrainz.harmony", "ludeon.rimworld"] + list(M.DLC_IDS) + [M.BRIDGE, "mandrake.rm.flowworks"]
    check("guard: clean closure passes", M.tier_guard(t, clean) == [], M.tier_guard(t, clean))
    check("guard: mandrake.rm.pits refused", any("mandrake.rm.pits" in r for r in M.tier_guard(t, clean + ["mandrake.rm.pits"])))
    check("guard: alpha biomes refused", M.tier_guard(t, clean + ["sarg.alphabiomes"]) != [])
    check("guard: a manywaters donor refused", M.tier_guard(t, clean + ["someone.manywaters"]) != [])
    check("guard: a missing DLC refused",
          any("odyssey" in r for r in M.tier_guard(t, [p for p in clean if p != "ludeon.rimworld.odyssey"])))


# ---------------------------------------------------------------- settings vs C#
def test_settings_match_source():
    src_root = os.path.join(S.MOD_DIR, "So" + "urce")
    decl = re.compile(r"public\s+static\s+(bool|float|int)\s+(\w+)\s*=(?!>)\s*([^;]+);")
    for t, rel in S.SETTINGS_SOURCES.items():
        text = open(os.path.join(src_root, rel), encoding="utf-8").read()
        body = text[text.index("class %s" % t.rsplit(".", 1)[1]):]
        found = {}
        for kind, name, val in decl.findall(body):
            v = val.strip().rstrip("f")
            found[name] = (v == "true") if kind == "bool" else float(v)
        want = S.SETTINGS[t]
        check("settings %s: same field set as the C#" % t.rsplit(".", 1)[1], set(found) == set(want),
              "C# only %s / table only %s" % (sorted(set(found) - set(want)), sorted(set(want) - set(found))))
        bad = [f for f in want if f in found and not S.settings_equal(found[f], want[f])]
        check("settings %s: defaults equal the C#" % t.rsplit(".", 1)[1], not bad, bad)
    # 27 until PIT_LEGACY_CODE_RETIRE_1 (2026-10-02): escapeEnabled and pitCellExposureEnabled died with
    # the building pit; trapTriggerEnabled and fallDamageEnabled moved into RimMandrakeFlowWorksSettings.
    check("80 toggles (plan 2.5, after the pit retirement; +ladderPrisonDoorEnabled, LADDER_PRISON_DOOR_1; +spikesEnabled, CANAL_BOTTOM_SPIKES_1; +flowDoorsSealedFromPitEnabled +sluiceLetsBigThroughEnabled, FLOWWORKS_DOOR_FAMILY_1; +swaleEnabled, CRACKEDLANDS_MECHANICS_BUILD_1; +pitExposureEnabled, PIT_TEMPERATURE_SOFTENING_1; +pitDepthDrawOffsetEnabled, PIT_DEPTH_DRAW_OFFSET_1; +canalFireEnabled, FLOWWORKS_BUILD_PROGRAM_1 Phase 6; +pitDrowningEnabled +poisonFillEnabled, PIT_FILL_EFFECTS_1; +viscosityEnabled, Phase 3/7 viscosity; +12 from the 2026-10-05 build pass: 3 fire, 3 superdeep room, wall faces, bottle revert, pump, digFinds + digFindsLocalOnly + digFindLetter; +22 Rivers (merge 409d1f57c); +5 machinery (3e473f37c); +5 visual principles (wall material, lip occlusion, surface motion, wakes, scorch))", len(S.toggles()) == 80, len(S.toggles()))


# ---------------------------------------------------------------- layout
def test_layout():
    for n in (200, 225, 250, 275, 300):
        try:
            L = S.layout((n, n))
            check("layout fits %dx%d" % (n, n), S.validate_layout(L, (n, n)) == [])
        except ValueError as ex:
            check("layout fits %dx%d" % (n, n), False, ex)
    try:
        S.layout((174, 174))
        check("layout refuses 174x174 (below plan minimum)", False)
    except ValueError:
        check("layout refuses 174x174 (below plan minimum)", True)
    L = S.layout((200, 200))
    ids = [p["id"] for p in L]
    check("plot ids unique", len(ids) == len(set(ids)))
    sea = [b for p in L for b in p["bodies"] if b["limitless"]]
    check("one limitless body >= 80 cells on the edge", len(sea) == 1 and sea[0]["rect"][0] == 0
          and sea[0]["rect"][2] * sea[0]["rect"][3] >= 80, sea)
    broken = [dict(L[0], rect=(1, 1, 8, 3), buffered=S._buffered((1, 1, 8, 3)))] + L[1:]
    check("validate_layout catches a limited plot at the edge", S.validate_layout(broken, (200, 200)) != [])
    m = S.expected_cells(S.plot_by_id(L, "R"), (200, 200))
    check("manifest marks no cell roofed (the rain twin is roofed by its bar, not the golden)", sum(1 for v in m.values() if v["roof"] != "none") == 0)
    check("parse_ops expands runs", S.parse_ops("Soil:1,2,3,1;WaterDeep:5,5,1,2") ==
          {(1, 2): "Soil", (2, 2): "Soil", (3, 2): "Soil", (5, 5): "WaterDeep", (5, 6): "WaterDeep"})


# ---------------------------------------------------------------- backup / restore
def test_backup_restore():
    cfg, bk = sub("cfg"), sub("bk")
    mc = os.path.join(cfg, "ModsConfig.xml")
    with open(mc, "wb") as f:
        f.write(b"<ModsConfigData>\r\n<activeMods><li>ludeon.rimworld</li></activeMods>\r\n</ModsConfigData>\r\n")
    ms = os.path.join(cfg, "Mod_mandrake.rm.flowworks_RimMandrakeFlowWorksMod.xml")
    with open(ms, "wb") as f:
        f.write(b"<SettingsBlock>x</SettingsBlock>")
    orig = {p: open(p, "rb").read() for p in (mc, ms)}
    man = S.backup_configs(cfg, bk, stamp="T1")
    check("backup manifest verifies", S.verify_backup(man) == [])
    with open(mc, "wb") as f:
        f.write(b"<ModsConfigData>swapped</ModsConfigData>")
    created = os.path.join(cfg, "Mod_mandrake.rm.flowworks_RiverSteamMod.xml")
    with open(created, "wb") as f:
        f.write(b"new")
    res = S.restore_configs(man)
    check("restore reproduces exact bytes (CRLF kept)", all(open(p, "rb").read() == b for p, b in orig.items()))
    check("restore removes a ModSettings file the run created", not os.path.exists(created), res)
    e = json.load(open(man))["entries"][0]
    with open(os.path.join(bk, e["backup"]), "ab") as f:
        f.write(b" ")
    check("verify_backup catches a tampered backup", S.verify_backup(man) != [])


# ---------------------------------------------------------------- prep + preflight on the fake
def fixtures(run):
    d = sub(run)
    saves, shots = sub(run + "/saves"), sub(run + "/shots")
    prefs = os.path.join(d, "Prefs.xml")
    with open(prefs, "w") as f:
        f.write("<PrefsData><screenWidth>1920</screenWidth><screenHeight>1080</screenHeight>"
                "<fullscreen>False</fullscreen><uiScale>1</uiScale><langFolderName>English</langFolderName>"
                "<textureCompression>False</textureCompression><autosaveIntervalDays>14</autosaveIntervalDays>"
                "</PrefsData>")
    log = os.path.join(d, "Player.log")
    with open(log, "w") as f:
        f.write("RimWorld 1.6.4633 rev1261\nLoading mods...\nAll good.\n")
    bridge = os.path.join(d, "BRIDGE")
    with open(bridge, "w") as f:
        f.write("FOUNDRY holds the bridge since 10:00 -- FlowWorks trial\n")
    tier = ["brrainz.harmony", "ludeon.rimworld"] + list(M.DLC_IDS) + [M.BRIDGE, "mandrake.rm.flowworks"]
    mc = os.path.join(d, "ModsConfig.xml")
    with open(mc, "w") as f:
        f.write("<ModsConfigData><activeMods>%s</activeMods></ModsConfigData>"
                % "".join("<li>%s</li>" % i for i in tier))
    dep = sub(run + "/Mods/FlowWorks/Assemblies")
    for suf in ("", ".srchash"):
        shutil.copyfile(os.path.join(S.MOD_DIR, S.DLL_REL) + suf, os.path.join(dep, "RimMandrakeFlowWorks.dll" + suf))
    P = PF.Paths(config_dir=d, mods_config=mc, prefs=prefs, player_log=log, saves=saves,
                 deployed_mod=os.path.dirname(dep), mod_roots=[os.path.join(d, "Mods")], bridge_file=bridge,
                 sidecar=os.path.join(saves, S.GOLDEN_NAME + ".json"), expected_tier=tier,
                 backup_dir=sub(run + "/bk"))
    return P, saves, shots


def session(g):
    return FastSession(transport=FakeTransport(g), strict=False)


def quiet(*a):
    pass


def prepped(run, **gkw):
    P, saves, shots = fixtures(run)
    g = FakeFlowWorksGame(saves_dir=saves, shots_dir=shots, **gkw)
    g.dll_sha = S.sha256_file(os.path.join(P.deployed_mod, S.DLL_REL))
    with session(g) as s:
        sc = PS.prep(s, saves, "FOUNDRY", prefs=P.prefs, player_log=P.player_log, repo_copy_dir=None,
                     bridge_paths=P, log=quiet)
    return P, g, sc


def live(P, g, seat="FOUNDRY"):
    with session(g) as s:
        rows = PF.run_live(s, P, seat)
    return {c.name: c for c in rows}, rows


def test_prep():
    P, g, sc = prepped("prep", season="Spring")
    golden = os.path.join(P.saves, S.GOLDEN_NAME + ".rws")
    check("prep wrote the golden save", os.path.isfile(golden))
    check("golden save is read-only", not (os.stat(golden).st_mode & stat.S_IWRITE))
    check("sidecar carries the version contract",
          set(sc["contract"]) >= {"save_sha256", "game_build", "flowworks_dll_sha256", "defs_hash", "settings",
                                  "prep_version"}, sorted(sc["contract"]))
    check("game build parsed from Player.log", sc["contract"]["game_build"] == "1.6.4633 rev1261",
          sc["contract"]["game_build"])
    check("prep advanced the clock FORWARD to summer", sc["generation"]["season"] == "Summer",
          sc["generation"]["season"])
    check("4 bodies classified, C_sea limitless", len(sc["bodies"]) == 4 and sc["bodies"]["C_sea"]["record"]["limitless"])
    check("manifest covers every plot", set(sc["manifest"]) == {p["id"] for p in sc["plots"]})
    check("start pawns despawned and recorded", sorted(sc["despawned"]) == ["Colonist1", "Muffalo1"])
    check("render profile recorded", sc["render_profile"]["screenWidth"] == "1920")
    # never overwrite a golden save
    g2 = FakeFlowWorksGame(saves_dir=P.saves, shots_dir=P.saves)
    try:
        with session(g2) as s:
            PS.prep(s, P.saves, "FOUNDRY", repo_copy_dir=None, bridge_paths=P, log=quiet)
        check("second prep without --rebuild refuses", False)
    except PS.Refused as ex:
        check("second prep without --rebuild refuses at step 8", ex.step == "8", ex)
    # today's tool set: stop before saving
    P3, saves3, shots3 = fixtures("prep_notool")
    g3 = FakeFlowWorksGame(saves_dir=saves3, shots_dir=shots3, new_tools=False)
    try:
        with session(g3) as s:
            PS.prep(s, saves3, "FOUNDRY", repo_copy_dir=None, bridge_paths=P3, log=quiet)
        check("prep without body_report stops", False)
    except PS.Refused as ex:
        check("prep without body_report stops at step 6, exit 3", ex.step == "6" and ex.code == 3, ex)
    check("...and saved nothing", os.listdir(saves3) == [], os.listdir(saves3))
    # the wrong bridge holder refuses before touching anything
    P4, saves4, shots4 = fixtures("prep_bench")
    g4 = FakeFlowWorksGame(saves_dir=saves4, shots_dir=shots4)
    try:
        with session(g4) as s:
            PS.prep(s, saves4, "BENCH", repo_copy_dir=None, bridge_paths=P4, log=quiet)
        check("prep refuses when another seat holds the bridge", False)
    except PS.Refused as ex:
        check("prep refuses when another seat holds the bridge (step 1)", ex.step == "1" and g4.pawns, ex)
    return P, g


def test_preflight_clean(P, g):
    c, rows = live(P, g)
    bad = [(r.name, r.status, r.evidence) for r in rows if r.status != PASS]
    check("clean prepped site: every live row PASS", not bad, bad)
    check("every live row of plan 3.9 ran", set(c) == set(PF.ROWS) - set(PF.OFFLINE), sorted(set(PF.ROWS) - set(c)))
    out = io.StringIO()
    check("report exits 0 on a clean site", PF.report(rows, stream=out) == 0, out.getvalue()[-300:])


DIRT = (("rain", "P-E1"), ("prefilled", "P-S1"), ("prefilled", "P-S3"), ("stray_pawn", "P-S1"),
        ("stray_pawn", "P-E4"), ("cold", "P-E2"), ("settings_drift", "P-B4"), ("condition", "P-E1"),
        ("temp_terrain", "P-S1"))


def test_preflight_dirt(P, g0):
    for fault, rid in DIRT:
        g = FakeFlowWorksGame(faults=[fault], saves_dir=P.saves, shots_dir=P.saves)
        g.dll_sha = g0.dll_sha
        g.map_id, g.tile = g0.map_id, g0.tile
        g.finish_site(S.plots_from_json(json.load(open(P.sidecar))["plots"]))
        g.dirty(S.plots_from_json(json.load(open(P.sidecar))["plots"]))
        c, rows = live(P, g)
        check("dirt %-14s refused by %s" % (fault, rid), c[rid].status == FAIL, (c[rid].status, c[rid].evidence))
        out = io.StringIO()
        rc = PF.report(rows, stream=out)
        check("dirt %-14s -> exit 1 naming %s" % (fault, rid), rc == 1 and ("REFUSED %s" % rid) in out.getvalue())
    # the combined dirty working copy the item asks for
    g = FakeFlowWorksGame(faults=["rain", "prefilled", "stray_pawn", "cold"], saves_dir=P.saves, shots_dir=P.saves)
    g.dll_sha, g.map_id, g.tile = g0.dll_sha, g0.map_id, g0.tile
    plots = S.plots_from_json(json.load(open(P.sidecar))["plots"])
    g.finish_site(plots)
    g.dirty(plots)
    c, rows = live(P, g)
    failed = {r.name for r in rows if r.status == FAIL}
    check("combined dirt refused on P-E1, P-S1, P-E4, P-E2", {"P-E1", "P-S1", "P-E4", "P-E2"} <= failed, failed)
    # a different map is not the trial site
    g = FakeFlowWorksGame(saves_dir=P.saves, shots_dir=P.saves)
    g.finish_site(plots)
    g.dll_sha, g.map_id = g0.dll_sha, 99
    c, _ = live(P, g)
    check("wrong map refused by P-B2", c["P-B2"].status == FAIL, c["P-B2"].evidence)
    # today's tool set: the new-tool rows are UNMEASURED, and UNMEASURED refuses
    g = FakeFlowWorksGame(saves_dir=P.saves, shots_dir=P.saves, new_tools=False, identity=False)
    g.finish_site(plots)
    g.dll_sha, g.map_id, g.tile = g0.dll_sha, g0.map_id, g0.tile
    c, rows = live(P, g)
    check("no new tools: P-S2, P-E6, P-E7 UNMEASURED",
          all(c[r].status == UNMEASURED for r in ("P-S2", "P-E6", "P-E7")),
          [(r, c[r].status) for r in ("P-S2", "P-E6", "P-E7")])
    check("UNMEASURED refuses the run", PF.report(rows, stream=io.StringIO()) == 1)
    check("--allow-unmeasured still refuses nothing else", PF.report(rows, True, stream=io.StringIO()) == 0)
    # the other seat holds the bridge
    c, _ = live(P, FakeFlowWorksGame(saves_dir=P.saves, shots_dir=P.saves), seat="BENCH")
    check("bridge held by FOUNDRY refuses a BENCH run (P-B1)", c["P-B1"].status == FAIL)
    # log + list
    real_log, empty_log = P.player_log, os.path.join(TMP, "empty_Player.log")
    open(empty_log, "w").close()
    P.player_log = empty_log
    check("empty Player.log is UNMEASURED on P-L2, never PASS", PF.p_l2(None, P, None).status == UNMEASURED)
    P.player_log = real_log
    with open(P.player_log, "a") as f:
        f.write("Exception in RimMandrake.FlowWorks.RM_MapComponent_Excavation.MapComponentTick\n")
    check("FlowWorks exception in Player.log refused by P-L2", PF.p_l2(None, P, None).status == FAIL)
    P.expected_tier = P.expected_tier + ["mandrake.rm.pits"]
    check("list != tier refused by P-L1", PF.p_l1(None, P, None).status == FAIL)


# ---------------------------------------------------------------- offline rows with fixtures
def test_offline(P):
    full = os.path.join(TMP, "FULL.xml")
    ids = ["ludeon.rimworld", "a.b", "mandrake.rm.pits", "mandrake.rm.flowworks"]
    with open(full, "w") as f:
        f.write("<ModsConfigData><activeMods>%s</activeMods></ModsConfigData>" % "".join("<li>%s</li>" % i for i in ids))
    pre = os.path.join(TMP, "pre.xml")

    def write_pre(lst):
        with open(pre, "w") as f:
            f.write("<ModsConfigData><activeMods>%s</activeMods></ModsConfigData>"
                    % "".join("<li>%s</li>" % i for i in lst))
    roots = sub("o_modroot")
    Q = PF.Paths(full_latest=full, pre_swap=pre, backup_dir=sub("o_bk"), mod_roots=[roots])
    write_pre(ids)
    check("P-O4 equal lists PASS", PF.p_o4(Q).status == PASS)
    write_pre([i for i in ids if i != "mandrake.rm.pits"])
    check("P-O4 minus pits PASS", PF.p_o4(Q).status == PASS)
    # the real 2026-10-02 shape: FULL.LATEST dropped pits, the live list still carries it
    with open(full, "w") as f:
        f.write("<ModsConfigData><activeMods>%s</activeMods></ModsConfigData>"
                % "".join("<li>%s</li>" % i for i in ids if i != "mandrake.rm.pits"))
    write_pre(ids)
    check("P-O4 live has dangling pits, not installed -> PASS", PF.p_o4(Q).status == PASS, PF.p_o4(Q).evidence)
    os.makedirs(os.path.join(roots, "Pits", "About"))
    with open(os.path.join(roots, "Pits", "About", "About.xml"), "w") as f:
        f.write("<ModMetaData><packageId>mandrake.rm.pits</packageId></ModMetaData>")
    check("P-O4 pits diff while Pits IS installed -> FAIL", PF.p_o4(Q).status == FAIL, PF.p_o4(Q).evidence)
    Q.mod_roots = [os.path.join(roots, "nope")]
    check("P-O4 pits diff, unreadable roots -> UNMEASURED", PF.p_o4(Q).status == UNMEASURED, PF.p_o4(Q).evidence)
    with open(full, "w") as f:
        f.write("<ModsConfigData><activeMods>%s</activeMods></ModsConfigData>" % "".join("<li>%s</li>" % i for i in ids))
    write_pre(ids + ["x.y"])
    check("P-O4 unexpected extra FAIL", PF.p_o4(Q).status == FAIL)
    write_pre(["a.b", "ludeon.rimworld", "mandrake.rm.flowworks"])
    check("P-O4 reorder FAIL", PF.p_o4(Q).status == FAIL)

    # P-O5: git clean stubbed; contract on the prepped fake save
    P.run = lambda cmd, cwd=None: (0, "")
    check("P-O5 clean tree + matching contract PASS", PF.p_o5(P).status == PASS, PF.p_o5(P).evidence)
    golden = os.path.join(P.saves, S.GOLDEN_NAME + ".rws")
    os.chmod(golden, stat.S_IREAD | stat.S_IWRITE)
    check("P-O5 writable golden FAIL", PF.p_o5(P).status == FAIL)
    with open(golden, "a") as f:
        f.write(" ")
    check("P-O5 changed golden sha FAIL", "sha changed" in PF.p_o5(P).evidence)
    P.run = lambda cmd, cwd=None: (0, " M src/RimMandrake/FlowWorks/Defs/x.xml\n")
    check("P-O5 dirty FlowWorks tree FAIL", PF.p_o5(P).status == FAIL)

    # P-O3: stubbed deploy + stamp, real DLL bytes in the fixture deploy folder
    P.run = lambda cmd, cwd=None: (0, "FlowWorks\n    in sync (68 files)\n" if "deploy_custom_mods.py" in cmd[1]
                                   else "MATCH src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll\n")
    check("P-O3 in sync + identical DLL + MATCH PASS", PF.p_o3(P).status == PASS, PF.p_o3(P).evidence)
    with open(os.path.join(P.deployed_mod, S.DLL_REL), "ab") as f:
        f.write(b"\0")
    check("P-O3 deployed DLL drift FAIL", PF.p_o3(P).status == FAIL)

    # P-O6: duplicates + backups
    P.backup_manifest = None
    os.makedirs(os.path.join(P.deployed_mod, "About"), exist_ok=True)
    with open(os.path.join(P.deployed_mod, "About", "About.xml"), "w") as f:
        f.write("<ModMetaData><packageId>%s</packageId></ModMetaData>" % S.PACKAGE_ID)
    check("P-O6 no backup manifest FAIL", "no ModsConfig/ModSettings backup" in PF.p_o6(P).evidence)
    P.backup_manifest = S.backup_configs(P.config_dir, P.backup_dir, stamp="T2")
    check("P-O6 one copy + verified backup PASS", PF.p_o6(P).status == PASS, PF.p_o6(P).evidence)
    pits = os.path.join(os.path.dirname(P.deployed_mod), "Pits", "Assemblies")
    os.makedirs(pits)
    open(os.path.join(pits, "RimMandrakePits.dll"), "wb").close()
    check("P-O6 stale Pits DLL FAIL", "RimMandrakePits.dll" in PF.p_o6(P).evidence)

    # P-O1/P-O2 read the real walk + validation.py: they must answer, not raise
    for r in PF.run_offline(PF.Paths(), only=("P-O1", "P-O2")):
        check("%s answers from the real repo (%s)" % (r.name, r.status), r.status in (PASS, FAIL), r.evidence)


def test_fill_costs():
    """DEPTH_FILL_COST_MATRIX_1: the O1 fill-cost row reds on the named regression (Half 42 < Mid 45)."""
    import validation_v2 as V
    defs = V._xml_blocks()
    check("O1 fill costs: shipped flooded > dry at every depth 1-3", V.fill_cost_findings(defs) == [],
          V.fill_cost_findings(defs))
    k, a, b, fn = defs["RM_Fill_Water_Half"]
    mut = dict(defs)
    mut["RM_Fill_Water_Half"] = (k, a, re.sub(r"<pathCost>\d+</pathCost>", "<pathCost>42</pathCost>", b), fn)
    found = V.fill_cost_findings(mut)
    check("O1 fill costs: Half 42 regression reds at D2 F1", any("D2 F1" in x and "RM_Channel_Mid" in x for x in found), found)
    k, a, b, fn = defs["RM_Fill_SlimeRed_Trace"]
    mut = dict(defs)
    mut["RM_Fill_SlimeRed_Trace"] = (k, a, re.sub(r"\s*<pathCost>\d+</pathCost>", "", b), fn)
    found = V.fill_cost_findings(mut)
    check("O1 fill costs: trace inheriting WaterShallow 30 reds at D3 F1", any("SlimeRed D3 F1" in x for x in found), found)


def main():
    try:
        test_fill_costs()
        test_tier()
        test_settings_match_source()
        test_layout()
        test_backup_restore()
        P, g = test_prep()
        test_preflight_clean(P, g)
        test_preflight_dirt(P, g)
        test_offline(P)
    finally:
        for dp, dn, fn in os.walk(TMP):
            for f in fn:
                os.chmod(os.path.join(dp, f), stat.S_IREAD | stat.S_IWRITE)
        shutil.rmtree(TMP, ignore_errors=True)
    print("\n%s: %d failure(s)%s" % ("FAIL" if FAILS else "PASS", len(FAILS), (": %s" % FAILS) if FAILS else ""))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
