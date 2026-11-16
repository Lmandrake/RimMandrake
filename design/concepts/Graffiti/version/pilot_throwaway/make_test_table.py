#!/usr/bin/env python3
"""THROWAWAY (Maturation Pipeline Stage 2, Graffiti 0.1.0): build the test table.

Shape copied from design/concepts/Pyrelands/version/pilot_throwaway/make_test_table.py.
Every locked bar names the tests that DECIDE it and the tests that only SUPPORT
it. runs_today is MEASURED: every built offline test is run now (logs under
D:\\ClaudeWork\\rimmandrake\\graffiti_preflight\\runs); a live test's entry
function is looked up in its file. Nothing here is a model's judgement.

Writes design/concepts/Graffiti/version/test_table.json and test_table.md.
"""
import json, os, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
CON = ROOT / "design/concepts/Graffiti"
VER = CON / "version"
GRF = "src/RimMandrake/Graffiti"
RUNS = Path("/mnt/d/ClaudeWork/rimmandrake/graffiti_preflight/runs")
HELD_FILE = "design/RimMandrake/validation_holding/walk_defects_2026-11-14_graffiti.md"
KNOWN_RED = "RIMMANDRAKE_REFUSE_HIDDEN_FACE_PAINT_ORDER_OUTLIVED_ITS_WALL"

tree = json.loads((CON / "tree.json").read_text())
LEAVES = {l["id"]: l for l in (tree["leaves"] if isinstance(tree, dict) else tree)}
record = json.loads((CON / "record.json").read_text())
INV = {i["id"]: i for i in record["inventory"]}
scenes_doc = json.loads((CON / "scenes.json").read_text())
SCENES = {s["id"]: s for s in scenes_doc["scenes"]}
LOCKED = json.loads((VER / "locked_bars.json").read_text())["ids"]

T = {}


def off(tid, f, observes, reads, cmd=None, new=False, item=None, mod_rows=None,
        defs=(), symbols=(), mods=()):
    T[tid] = dict(id=tid, kind="offline", stage="4-5", file=f, observes=observes,
                  reads=list(reads), command=cmd or ("python3 " + f), new=new and not (ROOT / f).exists(), item=item,
                  mod_rows=mod_rows, defs=list(defs), symbols=list(symbols), mods=list(mods))


# ---- built offline tests (all exist today; each is run below) ----
off("T_FUZZ", "src/RimMandrake/Utils/selftest_graffiti_fuzz.py",
    "kernel rules by fuzz: weighted pick, meme/skill/hostility gates, reaction priority, "
    "scrub-protection predicates, wall-cell candidates, breach lure (NOT weather)",
    [GRF + "/Source/Kernel/RM_GraffitiKernel.cs", GRF + "/Source/SelfTest/RimMandrakeGraffiti.SelfTest.csproj"],
    symbols=["RM_GraffitiKernel"])
off("T_LINT", "src/RimMandrake/Utils/selftest_graffiti_lint.py",
    "14 static clauses over defs, textures, keys and settings",
    [GRF + "/Defs/ThingDefs_Graffiti.xml", GRF + "/Defs/ThingDefs_GraffitiMemeGlyphs.xml"],
    defs=["RM_Graffiti_ThrowUp_A", "RM_Graffiti_IdeoSigil"])
off("T_SIGIL_COVERAGE", GRF + "/sigil_coverage.py",
    "every vanilla meme the sigil set claims has a glyph def (reads installed Ideology data)",
    [GRF + "/Defs/ThingDefs_GraffitiMemeGlyphs.xml"], defs=["RM_Graffiti_IdeoSigil"],
    mods=["ludeon.rimworld.ideology"])
off("T_SETTINGS_SCREENS", "src/RimMandrake/Utils/selftest_settings_screens.py",
    "the Graffiti settings screen lays out every field (rows tagged 'Graffiti:')",
    [GRF + "/Source/RM_GraffitiMod.cs"], mod_rows="Graffiti",
    symbols=["RM_GraffitiMod"])
off("T_SHIP_CHECK", GRF + "/ship_check.py",
    "ship gate: art, settings, review, stamp, deploy clauses",
    [GRF + "/Source/RM_GraffitiMod.cs", GRF + "/About/About.xml"], mods=["mandrake.rm.graffiti"])
off("T_FULL_LIST_MODE", GRF + "/selftest_full_list_mode.py",
    "harness: northstar full-list mode switches", [GRF + "/northstar_full.py"])
off("T_FRESH_QT", GRF + "/selftest_graffiti_fresh_quicktest.py",
    "harness: fresh quicktest staging", [GRF + "/stage_colony.py"])
off("T_PLAY_ZOOM", GRF + "/selftest_graffiti_play_zoom.py",
    "harness: play-zoom camera framing", [GRF + "/validation.py"])
off("T_SPREE_SURPRISE", GRF + "/selftest_graffiti_spree_surprise.py",
    "harness: spree start is not pre-announced", [GRF + "/validation.py"])
off("T_V1_LIVE_VERDICTS", GRF + "/selftest_graffiti_v1_live.py",
    "offline check of graffiti_v1_live_proof.py's clause verdict logic", [GRF + "/graffiti_v1_live_proof.py"])

# ---- new offline tests (Stage 3 builds them; item names namechecked, NOT filed) ----
off("T_WEATHER_OFFLINE", "src/RimMandrake/Utils/selftest_graffiti_weather.py",
    "fade curve: WeatherDays roofed > unroofed for every form and craft; WeatherFade alpha 1 "
    "before 60% of life, 0 at its end, monotone; a permanent mark never fades; mutants go red",
    [GRF + "/Source/Kernel/RM_GraffitiKernel.cs", GRF + "/Source/Filth_Mark.cs"],
    new=True, item="RIMMANDRAKE_PIN_GRAFFITI_WEATHER_FADE_CURVE_OFFLINE",
    symbols=["RM_GraffitiKernel", "GraffitiForm"])
off("T_RAID_TAG_BUILT_WALL_ONLY", "src/RimMandrake/Utils/selftest_graffiti_raid_tag_wall.py",
    "the exit-tag wall predicate rejects natural rock (MineableGold, granite) and accepts a built wall "
    "(held walk defect #2; GraffitiJobUtility.IsPaintableWall accepts isNaturalRock today)",
    [GRF + "/Source/GraffitiJobUtility.cs", GRF + "/Source/RaidExitTagger.cs"],
    new=True, item="RIMMANDRAKE_KEEP_GRAFFITI_RAID_TAGS_OFF_NATURAL_ROCK",
    symbols=["GraffitiJobUtility", "RaidExitTaggerMod"])
off("T_MSG_COUNTERS_RESET", "src/RimMandrake/Utils/selftest_graffiti_message_counters.py",
    "GraffitiSocial.messagesSent and messagesKept read 0 at a new game's start (held walk defect #6)",
    [GRF + "/Source/GraffitiSocial.cs", GRF + "/Source/RM_GraffitiSocialProof.cs"],
    new=True, item="RIMMANDRAKE_RESET_GRAFFITI_MESSAGE_COUNTERS_EACH_GAME",
    symbols=["GraffitiSocial"])


# ---- live tests: one per scene (stage 6) ----
def why_game_for(sc):
    for r in (sc.get("requirement") or sc.get("features") or []):
        why = (LEAVES.get(r) or {}).get("tier_reason") or ""
        if why and (LEAVES[r].get("tier_proposed") or "").startswith("live"):
            return why, r
    return "", None


def entry_exists(path, entry):
    src = (ROOT / path).read_text(errors="replace") if (ROOT / path).exists() else ""
    if path.endswith("graffiti_v1_live_proof.py"):
        m = re.search(r"^CLAUSES\s*=\s*\(([^)]*)\)", src, re.M)
        return bool(m) and ('"%s"' % entry) in m.group(1)
    return bool(re.search(r"^def %s\(" % re.escape(entry), src, re.M))


for sid, sc in SCENES.items():
    f, entry = sc["entry_point"].split("::")
    full = any("full list" in s.lower() for s in sc.get("start", []))
    why, leaf = why_game_for(sc)
    wfl = ""
    if full:
        wfl = next(((LEAVES[r].get("tier_reason") or "") for r in (sc.get("requirement") or [])
                    if LEAVES.get(r, {}).get("tier_proposed") == "live_full"), "")
    T[sid] = dict(id=sid, kind="live_full" if full else "live_minimal", stage="6", file=f, entry=entry,
                  observes="; ".join(sc.get("expect", []))[:400] if isinstance(sc.get("expect"), list)
                  else str(sc.get("expect", ""))[:400],
                  reads=[f], command="bridge: %s %s" % (f, entry), why_game=why, why_game_from_leaf=leaf,
                  why_full_list=wfl, entry_exists=entry_exists(f, entry),
                  item=sc.get("entry_point_item") or None, hold=sc.get("hold"), new=False,
                  defs=[], symbols=[], mods=["mandrake.rm.graffiti"])

T["P_A9"] = dict(id="P_A9", kind="live_minimal", stage="6", file=GRF + "/graffiti_v1_live_proof.py", entry="A9",
                 observes="a mark's paint order dies with its wall (no hidden face keeps a paint order)",
                 reads=[GRF + "/graffiti_v1_live_proof.py", GRF + "/Source/WallLossPatch.cs"],
                 command="bridge: graffiti_v1_live_proof.py A9",
                 why_game=LEAVES["sits_on_wall"]["tier_reason"], why_game_from_leaf="sits_on_wall",
                 why_full_list="", entry_exists=entry_exists(GRF + "/graffiti_v1_live_proof.py", "A9"),
                 item=KNOWN_RED, known_red=KNOWN_RED, new=False, defs=[], symbols=["WallLossPatch"],
                 mods=["mandrake.rm.graffiti"])
T["H1_IDEO_RELOAD"] = dict(
    id="H1_IDEO_RELOAD", kind="live_minimal", stage="6", file=GRF + "/validation.py",
    entry="scene_ideo_removed_save_reload",
    observes="after the colony's ideoligion is removed, a save reloads with 0 Graffiti reference errors "
             "(held walk defect #1: rmMarkMakerIdeo, Filth_Mark.cs:297)",
    reads=[GRF + "/Source/Filth_Mark.cs"], command="bridge: validation.py scene_ideo_removed_save_reload",
    why_game="Scribe reference resolution on save and load is engine behaviour over a live world's ideoligion "
             "list; no offline model of Scribe_References exists to decide it",
    why_game_from_leaf=None, why_full_list="",
    entry_exists=entry_exists(GRF + "/validation.py", "scene_ideo_removed_save_reload"),
    item="RIMMANDRAKE_PROVE_GRAFFITI_MARKS_RELOAD_AFTER_IDEO_LOST", new=True, defs=[],
    symbols=["Filth_Mark"], mods=["mandrake.rm.graffiti"])
T["LOOK_STAGE8"] = dict(id="LOOK_STAGE8", kind="look", stage="8", file=None, observes="the owner walks the mod",
                        reads=[], command="owner walk", new=False, item=None, defs=[], symbols=[], mods=[],
                        runs_today={"ran": False, "why": "Stage 8: the owner's own walk"})

# ---- bars: (id, decides, supports) ----
B = [
    ("mark_appears", ["sc_spree_wall"], ["sc_spree_corridor", "T_FRESH_QT", "T_SPREE_SURPRISE", "T_FUZZ"]),
    ("reads_at_play_zoom", ["sc_gallery"], ["T_PLAY_ZOOM", "LOOK_STAGE8"]),
    ("sits_on_wall", ["sc_wall_closeup", "P_A9"], ["T_FUZZ"]),
    ("marks_various", ["sc_spree_variety"], ["sc_spree_corridor", "T_FUZZ"]),
    ("ideo_sigil", ["sc_sigil"], ["T_FUZZ", "T_SIGIL_COVERAGE"]),
    ("punk_register", ["sc_gallery"], ["LOOK_STAGE8"]),
    ("no_english", ["sc_gallery"], ["T_LINT", "LOOK_STAGE8"]),
    ("not_dirt", ["sc_gallery"], ["LOOK_STAGE8"]),
    ("ugliness_visible", ["sc_beauty_pair"], ["sc_spree_corridor", "sc_walk", "LOOK_STAGE8"]),
    ("art_skill", ["sc_art_skill"], ["sc_spree_corridor", "T_FUZZ"]),
    ("own_fun", ["sc_own_fun"], []),
    ("rereads_daily", ["sc_rereads"], ["sc_lived_in_soak"]),
    ("mockery", ["sc_mockery"], ["T_FUZZ", "sc_lived_in_soak"]),
    ("tribute_memorial", ["sc_tribute_memorial"], ["T_FUZZ"]),
    ("answer_wall", ["sc_answer_wall"], []),
    ("scrub_protection", ["sc_scrub_protection"], ["T_FUZZ"]),
    ("player_orders", ["sc_player_orders"], []),
    ("raid_mark_troubles", ["sc_raid_exit", "sc_hostile_thought", "sc_raid_retaken", "sc_weathered_raid_mark",
                            "T_RAID_TAG_BUILT_WALL_ONLY"], ["T_FUZZ"]),
    ("going_over", ["sc_going_over"], []),
    ("raider_pressure", ["sc_raider_pressure"], []),
    ("visitors", ["sc_visitors"], []),
    ("fights_reasons", ["sc_fights"], []),
    ("temperament", ["sc_temperament"], []),
    ("stands_alone_settings", ["sc_settings", "sc_breach_toggle", "sc_breach_bias_raid"],
     ["H1_IDEO_RELOAD", "T_SETTINGS_SCREENS"]),
    ("stories_not_tax", ["sc_lived_in_soak"], ["sc_rereads", "T_MSG_COUNTERS_RESET"]),
    ("paint_dies_with_wall", ["sc_wall_loss"], []),
    ("weathering_bounds_marks", ["T_WEATHER_OFFLINE", "sc_weathered_raid_mark"], []),
    ("walk_lived_in", ["sc_walk"], ["LOOK_STAGE8", "T_FULL_LIST_MODE"]),
    ("inv_mark_on_wall", ["sc_wall_closeup", "P_A9"], ["sc_spree_corridor", "T_FUZZ"]),
    ("inv_mark_art_set", ["sc_gallery", "sc_spree_variety"], ["T_LINT", "T_SHIP_CHECK", "sc_beauty_pair"]),
    ("inv_beauty_and_craft", ["sc_beauty_pair", "sc_art_skill"], ["sc_spree_corridor", "LOOK_STAGE8"]),
    ("inv_ideo_sigils", ["sc_sigil", "T_SIGIL_COVERAGE"], ["T_LINT", "T_FUZZ"]),
    ("inv_spree", ["sc_spree_wall"], ["sc_spree_corridor", "T_SPREE_SURPRISE"]),
    ("inv_joy_and_idle_tag", ["sc_own_fun"], []),
    ("inv_player_orders", ["sc_player_orders"], []),
    ("inv_viewer_mood", ["sc_rereads", "sc_hostile_thought"], ["sc_beauty_pair", "T_LINT"]),
    ("inv_social_layer", ["sc_mockery", "sc_answer_wall", "sc_tribute_memorial", "sc_fights"],
     ["T_FUZZ", "T_MSG_COUNTERS_RESET"]),
    ("inv_visitors", ["sc_visitors"], []),
    ("inv_raid_marks", ["sc_raid_exit", "sc_going_over", "sc_raid_retaken", "T_RAID_TAG_BUILT_WALL_ONLY"], []),
    ("inv_breach_bias", ["sc_breach_bias_raid", "sc_breach_toggle"], ["T_FUZZ"]),
    ("inv_scrub_protection", ["sc_scrub_protection"], ["T_FUZZ"]),
    ("inv_temperament", ["sc_temperament"], []),
    ("inv_wall_loss", ["sc_wall_loss"], []),
    ("inv_settings", ["sc_settings", "T_SETTINGS_SCREENS"], ["T_LINT", "T_SHIP_CHECK", "sc_breach_toggle"]),
    ("inv_standalone", ["sc_settings", "H1_IDEO_RELOAD"], ["T_SHIP_CHECK"]),
    ("inv_raider_future_marks", ["sc_raider_pressure"], []),
    ("inv_weathering", ["sc_weathered_raid_mark", "T_WEATHER_OFFLINE"], []),
]

# ---- held look statements (design/RimMandrake/validation_holding/): the placement IS the ingest ----
HELD_PLACE = {
    1: (["inv_standalone", "stands_alone_settings"], ["H1_IDEO_RELOAD"]),
    2: (["raid_mark_troubles", "inv_raid_marks"], ["T_RAID_TAG_BUILT_WALL_ONLY", "sc_raid_exit"]),
    3: (["stories_not_tax", "mockery"], ["sc_lived_in_soak", "sc_mockery"]),
    4: (["stories_not_tax"], ["sc_lived_in_soak"]),
    5: (["ugliness_visible", "inv_beauty_and_craft"], ["sc_beauty_pair", "sc_walk", "LOOK_STAGE8"]),
    6: (["stories_not_tax"], ["T_MSG_COUNTERS_RESET"]),
}
HELD_NOTE = {
    3: "may be by design: the owner's call at the Stage 8 walk; the soak measures it",
    4: "the owner's call; the soak measures the slope over weeks",
    5: "look only: text and picture agree is judged by eye; decided at sc_beauty_pair and the walk",
    6: "harness defect; its fix makes sc_lived_in_soak's message count an honest instrument",
}


def held_rows():
    rows = []
    for line in (ROOT / HELD_FILE).read_text().splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*(.*?)\s*\|", line)
        if m:
            n = int(m.group(1))
            bars, tests = HELD_PLACE.get(n, ([], []))
            rows.append(dict(source="%s row %d" % (HELD_FILE, n), row=n, text=m.group(2)[:300],
                             speaker="agent (walk finding, measured); not the owner's words",
                             bars=bars, tests=tests, note=HELD_NOTE.get(n, "")))
    return rows


# ---- measure runs_today ----
def run_offline(t):
    RUNS.mkdir(parents=True, exist_ok=True)
    log = RUNS / (Path(t["file"]).stem + ".txt")
    t0 = time.time()
    try:
        p = subprocess.run(["python3", t["file"]], cwd=ROOT, capture_output=True, text=True, timeout=500)
        out, rc = p.stdout + p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = (e.stdout or "") if isinstance(e.stdout, str) else "", "timeout"
    log.write_text(out)
    lines = [l for l in out.splitlines() if l.strip()]
    res = {"ran": True, "rc": rc, "seconds": round(time.time() - t0, 1), "last": lines[-1][:200] if lines else "",
           "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "log": str(log)}
    if t.get("mod_rows"):
        tag = re.compile(r"^(ok|FAIL)\s+%s:" % re.escape(t["mod_rows"]))
        mine = [l for l in out.splitlines() if tag.match(l.strip())]
        bad = [l for l in mine if l.strip().startswith("FAIL")]
        res["mod_rows"] = {"tag": t["mod_rows"] + ":", "ok": len(mine) - len(bad), "fail": len(bad)}
        res["result"] = "PASS" if mine and not bad else ("UNMEASURED: no rows tagged" if not mine else "FAIL")
    else:
        res["result"] = "PASS" if rc == 0 else "FAIL"
    return res


for t in T.values():
    if t["kind"] == "offline":
        if t["new"]:
            t["runs_today"] = {"ran": False, "why": "not written yet: Stage 3 work (%s)" % t["item"]}
        else:
            t["runs_today"] = run_offline(t)
            print("ran", t["id"], t["runs_today"]["result"], t["runs_today"]["seconds"], "s", flush=True)
    elif t["kind"] in ("live_minimal", "live_full"):
        t["runs_today"] = {"ran": False, "entry_exists": t["entry_exists"],
                           "why": "Stage 6 game test; Stage 2 checks only that its entry exists"}


sys.path.insert(0, str(ROOT / "src/RimMandrake/rimflow"))
import maturation as M  # noqa: E402


def red_is_live_only(item):
    """The pipeline's rule (maturation.live_known_red_owed): a known red that is closed, or implemented on main with a
    remainder that needs the live game, leaves a live check that runs, UNRUN and owed to Stage 6."""
    r = str(ROOT)
    return item in M.ledger_ended(r, [item]) or (
        item in M.ledger_implemented(r, [item]) and M.ledger_needs(r, [item]).get(item) in M.LIVE_NEEDS)


def runnable(tid):
    t = T[tid]
    if t["kind"] == "offline":
        return bool(t["runs_today"].get("ran")) and t["runs_today"].get("result") == "PASS"
    if t["kind"] in ("live_minimal", "live_full"):
        return bool(t["entry_exists"]) and (not t.get("known_red") or red_is_live_only(t["known_red"]))
    return False


ORDER = {"4-5": 1, "6": 2, "8": 3}
bars = []
for bid, dec, sup in B:
    src = "tree" if bid in LEAVES else "record"
    held = [r["row"] for r in held_rows() if bid in r["bars"]]
    offd = [d for d in dec if T[d]["kind"] == "offline"]
    bars.append(dict(
        id=bid, source=src,
        kind=(LEAVES[bid].get("tier_proposed") if src == "tree" else "inventory"),
        proves_at=max((T[d]["stage"] for d in dec), key=lambda s: ORDER[s]),
        decides=dec, supports=sup, held=held, offline_decides=offd,
        offline_green_today=bool(offd) and all(runnable(d) for d in offd),
        every_decider_runnable_today=all(runnable(d) for d in dec),
        any_test_runnable_today=any(runnable(x) for x in dec + sup)))

bars.sort(key=lambda b: LOCKED.index(b["id"]) if b["id"] in LOCKED else len(LOCKED))
out = dict(mod="Graffiti", version="0.1.0", made=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           made_by="design/concepts/Graffiti/version/pilot_throwaway/make_test_table.py (throwaway, no model)",
           stages={"4-5": "offline (blind)", "6": "in game", "8": "owner walk"},
           rule="a bar passes when every test in decides passes; supports adds evidence and decides nothing; "
                "proves_at is the highest stage among the deciders",
           known_red={"P_A9": KNOWN_RED},
           held_statements=held_rows(),
           held_note="validation_holding has one Graffiti file (walk_defects_2026-11-14_graffiti.md, 6 agent rows); "
                     "no owner_look_defects_* row names Graffiti",
           tests=T, bars=bars)

if __name__ == "__main__" and os.environ.get("GRAFFITI_TABLE_DRYRUN") != "1":
    (VER / "test_table.json").write_text(json.dumps(out, indent=1) + "\n")
    off_built = [t for t in T.values() if t["kind"] == "offline" and not t["new"]]
    md = ["# Graffiti 0.1.0 test table (read view of test_table.json)", "",
          "Made by `pilot_throwaway/make_test_table.py`, %s. A bar passes when every deciding test passes." % out["made"], "",
          "## Counts", "",
          "- bars: %d (locked: %d)" % (len(bars), len(LOCKED)),
          "- tests: %d (%d built offline, %d new offline, %d live, %d look)" % (
              len(T), len(off_built), sum(1 for t in T.values() if t["kind"] == "offline" and t["new"]),
              sum(1 for t in T.values() if t["kind"].startswith("live")), sum(1 for t in T.values() if t["kind"] == "look")),
          "- scene entries present: %d, absent: %d" % (
              sum(1 for s in SCENES if T[s]["entry_exists"]), sum(1 for s in SCENES if not T[s]["entry_exists"])),
          "- built offline green today: %d, red: %d" % (
              sum(1 for t in off_built if t["runs_today"]["result"] == "PASS"),
              sum(1 for t in off_built if t["runs_today"]["result"] != "PASS")),
          "- bars with every decider runnable today: %d" % sum(1 for b in bars if b["every_decider_runnable_today"]),
          "- known red: P_A9 = %s" % KNOWN_RED, "",
          "## Bars", "", "| bar | proves at | decides | supports | held | runnable today |", "|---|---|---|---|---|---|"]
    for b in bars:
        md.append("| %s | %s | %s | %s | %s | %s |" % (b["id"], b["proves_at"], ", ".join(b["decides"]),
                  ", ".join(b["supports"]) or "-", ", ".join(map(str, b["held"])) or "-",
                  "yes" if b["every_decider_runnable_today"] else "no"))
    md += ["", "## Tests", "", "| test | kind | stage | file::entry | today | new item |", "|---|---|---|---|---|---|"]
    for t in T.values():
        rt = t.get("runs_today", {})
        today = rt.get("result") or ("entry present" if t.get("entry_exists") else
                                      ("entry absent" if t["kind"].startswith("live") else rt.get("why", "")))
        if t.get("known_red"):
            today += " (known red)"
        md.append("| %s | %s | %s | %s | %s | %s |" % (t["id"], t["kind"], t["stage"],
                  (t["file"] or "-") + ("::" + t["entry"] if t.get("entry") else ""), today,
                  t["item"] if t.get("new") else "-"))
    md += ["", "## Held statements placed", "", "| row | bars | tests | note |", "|---|---|---|---|"]
    for r in out["held_statements"]:
        md.append("| %d | %s | %s | %s |" % (r["row"], ", ".join(r["bars"]), ", ".join(r["tests"]), r["note"] or "-"))
    (VER / "test_table.md").write_text("\n".join(md) + "\n")
    print("wrote", VER / "test_table.json", "and test_table.md")
