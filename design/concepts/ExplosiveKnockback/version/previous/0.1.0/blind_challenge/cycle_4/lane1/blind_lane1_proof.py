#!/usr/bin/env python3
"""Blind lane 1, ExplosiveKnockback 0.1.0 cycle 4: the inv_proof_scenes half (no C# compile needed).
    python3 blind_lane1_proof.py [--gate <proof_build_gate.py>] [--src <ExplosiveKnockback dir>]
Prints one JSON row per line. Written from the bars (record.json inv_proof_scenes, scenes.json entry points) and the
shipped settings file alone, before any test, journal or earlier finding was read."""
import argparse, glob, importlib.util, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
SRC = os.path.join(REPO, "src/RimMandrake/ExplosiveKnockback")
CONCEPT = os.path.join(REPO, "design/concepts/ExplosiveKnockback")


def row(rid, bars, kind, verdict, cases, detail):
    print(json.dumps({"id": rid, "bars": bars, "kind": kind, "verdict": verdict, "cases": cases, "detail": detail}))
    return verdict


def gate_rows(path):
    spec = importlib.util.spec_from_file_location("pbg_blind", path)
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    bad, n = [], 0
    release = [
        "Type not found: RimMandrake.ExplosiveKnockback.RM_KnockbackProof",
        {"error": "Type not found: RimMandrake.ExplosiveKnockback.RM_KnockbackProof"},
        {"success": False, "result": "Type not found 'RimMandrake.ExplosiveKnockback.RM_KnockbackProof'"},
    ]
    not_release = [
        "calibration,wall_stop,door_stop flowworks=True hoses=False",            # a real Names answer
        "Type not found: RimMandrake.FlowWorks.RM_SomeOtherProof",                # another type missing
        "ERROR calibration NullReferenceException: Object reference not set",    # a proof-type error
        "STAGED calibration at 12,12 tick=100",
        {"result": "PASS calibration landed 3"},
        "",
        None,
    ]
    for r in release:
        n += 1
        if not g.is_release_answer(r):
            bad.append("release not seen: %r" % (r,))
        n += 1
        try:
            g.require_proof_build(r, out=io.StringIO())
            bad.append("require_proof_build returned on release %r" % (r,))
        except SystemExit as e:
            if e.code != 3:
                bad.append("exit %r (want 3) on %r" % (e.code, r))
    for r in not_release:
        n += 1
        if g.is_release_answer(r):
            bad.append("a non-release answer read as release: %r" % (r,))
        n += 1
        try:
            back = g.require_proof_build(r, out=io.StringIO())
            if back is not r and back != r:
                bad.append("did not return the answer unchanged: %r" % (r,))
        except SystemExit as e:
            bad.append("exited %r on a real answer %r" % (e.code, r))
    # the message names the proof build route
    n += 1
    buf = io.StringIO()
    try:
        g.require_proof_build(release[0], out=buf)
    except SystemExit:
        pass
    if "RmProofs=true" not in buf.getvalue() or "PROOF BUILD REQUIRED" not in buf.getvalue():
        bad.append("the refusal does not name the proof build")
    row("L1_PROOF_GATE_BEHAVIOUR", ["inv_proof_scenes"], "fixed", "FAIL" if bad else "PASS", n,
        "; ".join(bad[:6]) if bad else "release answers (string, dict, quoted name) exit 3 with the proof-build route; a real Names/Stage/Verdict answer, another type's 'Type not found', a proof error, empty and None return unchanged")


def scene_rows(src):
    files = sorted(glob.glob(os.path.join(src, "Source", "RM_KnockbackProof*.cs")))
    text = {os.path.basename(f): open(f, encoding="utf-8").read() for f in files}
    main = text.get("RM_KnockbackProof.cs", "")
    m = re.search(r"SceneNames\s*=\s*\{(.*?)\};", main, re.S)
    names = re.findall(r'"([a-z0-9_]+)"', re.sub(r"//[^\n]*", "", m.group(1))) if m else []
    allsrc = "\n".join(text.values())
    # each name has a builder: a case label, or a prefix dispatch (settings_sweep_<lane>)
    missing = [n for n in names if ('case "%s"' % n) not in allsrc and ('"%s"' % n) not in allsrc.replace(m.group(0) if m else "", "")]
    dup = sorted({n for n in names if names.count(n) > 1})
    sc = json.load(open(os.path.join(CONCEPT, "scenes.json")))
    eps = []

    def walk(n):
        if isinstance(n, dict):
            ep = n.get("entry_point")
            if isinstance(ep, str) and "RM_KnockbackProof" in ep and "::" in ep:
                eps.append((n.get("id"), ep.split("::", 1)[1].strip()))
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(sc)
    unnamed = [(i, e) for i, e in eps if e not in names]
    bad = []
    if not names:
        bad.append("SceneNames not found")
    if missing:
        bad.append("names with no builder: " + ",".join(missing))
    if dup:
        bad.append("duplicate names: " + ",".join(dup))
    if unnamed:
        bad.append("scenes.json entry points not in SceneNames: " + ",".join("%s->%s" % x for x in unnamed))
    row("L1_PROOF_SCENES_NAMED_AND_BUILT", ["inv_proof_scenes"], "fixed", "FAIL" if bad else "PASS", len(names) + len(eps),
        "; ".join(bad) if bad else "%d scene names, each with a builder, no duplicate; all %d scenes.json entry points into RM_KnockbackProof name a listed scene" % (len(names), len(eps)))
    # inv_proof_scenes' own list: mortar 3 cells, wall, door, sandbags, too big, EMP, items, shelf, corpse, pits, cover, caps,
    # master off, config, guards
    want = {"mortar 3 cells": ["calibration"], "wall": ["wall_stop"], "door": ["door_stop"], "sandbags": ["over_sandbags"],
            "too big": ["heavy_skip", "body_override", "mass_and_power"], "EMP": ["emp_no_throw"], "items": ["items"], "shelf": ["shelf", "open_storage"],
            "corpse": ["corpse_into_pit", "killed_by_blast"], "pits": ["pit_colonist", "pit_enemy"], "cover": ["cover_breaks"],
            "caps": ["all_fly_no_cap"], "master off": ["settings_off"], "config": ["lookup_projectile", "lookup_zero_wins"],
            "guards": ["immunity_window", "shield_counter", "in_pit_skip"]}
    gone = [k for k, v in want.items() if not any(x in names for x in v)]
    row("L1_PROOF_SCENES_INVENTORY_LIST", ["inv_proof_scenes"], "fixed", "FAIL" if gone else "PASS", len(want),
        ("inventory scenes with no listed scene: " + ",".join(gone)) if gone else "every scene kind inv_proof_scenes lists has a listed scene")
    return names


def settings_rows(src):
    t = open(os.path.join(src, "Source", "RM_KnockbackMod.cs"), encoding="utf-8").read()
    init = {k: v for k, v in re.findall(r"public static (?:bool|float|int) (\w+) = ([^;]+);", t)}
    scribe = {k: v for k, v in re.findall(r'Scribe_Values\.Look\(ref (\w+), "\w+", ([^)]+)\);', t)}
    reset = {k: v for k, v in re.findall(r"RimMandrakeExplosiveKnockbackSettings\.(\w+) = ([^;]+);", t)}

    def norm(v):
        v = v.strip()
        if v in ("true", "false"):
            return v
        try:
            return repr(float(v.rstrip("fF")))
        except ValueError:
            return v
    bad = []
    for k, v in scribe.items():
        if k not in init:
            bad.append("%s saved but no field initialiser" % k)
            continue
        if norm(init[k]) != norm(v):
            bad.append("%s initialiser %s != saved default %s" % (k, init[k], v))
        if k not in reset:
            bad.append("%s not in Reset()" % k)
        elif norm(reset[k]) != norm(v):
            bad.append("%s Reset() %s != saved default %s" % (k, reset[k], v))
    unsaved = [k for k in init if k not in scribe]
    row("L1_SETTINGS_DEFAULTS_AGREE", ["inv_proof_scenes", "settings_scale_and_switch", "inv_settings"], "fixed", "FAIL" if bad else "PASS", len(scribe) * 3,
        ("; ".join(bad[:8])) if bad else "%d saved settings: field initialiser = Scribe default = Reset() for every one (the scenes' 'Settings reset then read' is the shipped default)" % len(scribe))
    row("L1_SETTINGS_UNSAVED_FIELDS", ["settings_scale_and_switch"], "info", "INFO", len(unsaved),
        "public static settings fields not saved: " + (",".join(unsaved) or "none"))
    # no removed cap setting and no body-size setting remains on the page or in the saved settings
    caps = [k for k in scribe if re.search(r"(?i)(throwcap|capperexplosion|maxthrows|throwsperexplosion|itemspertick|droppertick|pertickdrop|bodysize|immunebody)", k)]
    row("L1_SETTINGS_NO_REMOVED_CAPS", ["settings_scale_and_switch", "every_good_moves", "the_spared"], "fixed", "FAIL" if caps else "PASS", len(scribe),
        ("removed cap or body-size settings still saved: " + ",".join(caps)) if caps else "no per-explosion, per-tick or body-size setting is saved")


GAME_SIDE = [
    ("pawn_flight_arc", "the PawnFlyer carrier, its target fixed at the blast and the stun end: Verse"),
    ("hose_drops_at_takeoff", "the hose carry and drop at takeoff: the game side and Hoses compat"),
    ("every_good_moves", "the candidate gathering per explosion and the removed caps live in the map component; the kernel's ledger is tested (L1_EXPLOSION_LEDGER)"),
    ("open_shelf_scatters", "which storage draws its contents (showContents, building classes) is def/Verse classification; GoodsHeld is tested (L1_MISC)"),
    ("only_explosions_throw", "the hook sits on the explosion damage worker only: Harmony"),
    ("gas_goes_clump_by_clump", "the burning gas grid, clump bursts and the 2 s cooldown: game side"),
    ("our_gases_burn", "the census of our gas sources: def and grid registration"),
    ("blast_breaks_pit_cover", "the cover break on a damaging blast: FlowWorks pits, game side"),
    ("pit_goods_fetched", "hauling off a pit floor: FlowWorks jobs"),
    ("no_teleport", "goods drawn in a carrier, not despawned and re-placed: RM_ThingFlyer_Knockback; the kernel's line is contiguous (L1_PATH_RANDOM_CONSERVATION)"),
    ("no_careless_fall", "pathing around pits: FlowWorks"),
    ("shield_belt_holds", "the shield absorbing and the gas-shove exception: Verse; the debit maths is tested (L1_IMMUNITY_SHIELD)"),
    ("barrage_frame_budget", "a live frame measurement; KbFrameStats is tested (L1_MISC)"),
    ("walk_storeroom_raid", "a walk on the full list"),
    ("inv_hook", "the Harmony hook on the explosion"),
    ("inv_pawn_flyer", "the pawn flyer def and carrier"),
    ("inv_which_blasts", "the DamageDef patch and lookup at runtime; KbLookup order is tested (L1_LOOKUP_ORDER)"),
    ("inv_items_teleport", "the item move path in the map component"),
    ("inv_shelf_skip", "storage classification at runtime"),
    ("inv_who_is_spared", "pit, carrying, airborne and bed states read from Verse"),
    ("inv_pits_receive", "FlowWorks pit landing"),
    ("inv_pit_floor_haul", "FlowWorks hauling"),
    ("inv_hose_drop", "Hoses compat"),
    ("inv_gas_chain", "the gas chain in the map component"),
    ("inv_closed_guard", "closed classification and guard at runtime"),
    ("inv_gas_tags", "gas opt-in registration"),
    ("inv_perf_all_fly", "live performance"),
    ("inv_killed_corpse", "a pawn killed by the blast thrown as a corpse: Verse ordering"),
    ("inv_pit_floor_goods_stay", "pit floor state from FlowWorks"),
    ("inv_too_weak_skip", "the journal skip line at runtime; the rounding to 0 is tested (L1_WILD_RIM_ZERO_KERNEL)"),
    ("inv_caps", "scope out: the caps are removed; the map component's absence of caps is runtime"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", default=os.path.join(SRC, "proof_build_gate.py"))
    ap.add_argument("--src", default=SRC)
    a = ap.parse_args()
    gate_rows(a.gate)
    scene_rows(a.src)
    settings_rows(a.src)
    row("L1_PROOF_RESTORE_GAME_SIDE", ["inv_proof_scenes"], "info", "INFO", 0,
        "the promise that RM_KnockbackProof.Verdict / Stage undo what a scene changed (settings, def extensions, spawned things) lives in Verse code; lane 1 does not stretch a kernel to it: its offline decider is T_RESTORE, rerun in lane 2")
    # bars whose logic is game-side (Verse, Harmony, the flyer carriers, FlowWorks pits, the live list): one not_kernel row each
    for bar, why in GAME_SIDE:
        row("L1_NOT_KERNEL_" + bar.upper(), [bar], "not_kernel", "UNSETTLED", 0, why)

main()
