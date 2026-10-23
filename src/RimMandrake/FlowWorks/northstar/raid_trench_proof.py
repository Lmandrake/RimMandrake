"""RAID vs SHEER TRENCH live proof (PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH; plan risks 1 and 2 of
design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md).

  python.exe src/RimMandrake/FlowWorks/northstar/raid_trench_proof.py [out.json] [--fresh-map] [--points 500]
                                                                       [--ticks 15000] [--direct]

Run from the repo root with python.exe; the bridge must be held. NO flyer anywhere (standing rule): the raid is the
storyteller's default hostile humanlike faction, and a flying raider is reported, never judged.

Scene (map centre c): a 9x9 ISLAND of untouched ground (Chebyshev distance <= 4 from c) holding every colonist, ringed
by a SHEER TRENCH 2 squares wide (distance 5 and 6), dug D 4 = 2 m everywhere (climb_proof: a person is trapped at D 3,
so 2 m is a wall for the person band both down and up). A CHURN cell 9 east of c is dug to D 4 and filled back every
other chunk, so the cliff masks rebuild over and over while the raiders' path requests are in flight (risk 2: the
per-request mask swap under 1.6's multithreaded pathfinding).

Rows:
  RAID_island_sealed        PASS/FAIL  state read before the raid: the person band's mask on the island's east lip
                                       has no east bit (the wall is a wall to the pathfinder).
  RAID_outcome              MEASURED   what the raiders did: BREACH (a raider ever on the island), FELL (a raider ever
                                       on a trench square), LEFT (raiders despawned alive), STALL (alive near the trench
                                       and barely moving), MILL (alive near the trench and moving), plus every sample.
                                       Not a pass/fail: whether that is a bug or a feature is DEPTH_QUESTIONS_ASK_RAIDERS_FIRST.
  MASKSWAP_no_wall_crossing PASS/FAIL  with the masks rebuilding every other chunk, no raider is ever sampled on the
                                       island or in the trench. Sampled every chunk (250 ticks): a crossing and a
                                       return inside one chunk would be missed, so a PASS is "never seen", not "proven
                                       impossible"; it is UNMEASURED when fewer than 2 raiders came within 15 squares,
                                       and when the crossing went over the raid's own ladder/plank (legal since
                                       RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP).
  RAID_LADDER_BREACH        PASS/FAIL  (--depth <= 6) RAIDERS_TRENCH A2: raider ladders on BOTH walls and a raider used them.
  RAID_FILL_CAUSEWAY        PASS/FAIL  (--depth 8, past the portable ladder reach) RAIDERS_TRENCH A3: a ring square filled
                                       shallower than dug and a raider used it. First live run 2026-10-22: FAIL, raiders
                                       Wait at the lip (CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP).
  LADDER_PARITY_* rows (LADDER_PARITY_BUILD_NO_KEYS_REQUIRED, owner by card 2026-10-23; design
  design/RimMandrake/ladder_parity_2026-10-23.md; reads/acts through RM_LadderParity.ProofLadderParity):
  LADDER_PARITY_BREACH_SCAR_REPAIR      (--depth 8) every square the raid filled carries a breach scar at its dug depth,
                                       and the real Orders > Repair breach designator puts a dig-to order back to it.
  LADDER_PARITY_RAIDERS_USE_COLONY_LADDERS (--direct --colony-ladders) the PLAYER's portable ladders stand on both walls of the
                                       east row; a raider reaches the island over them ("no keys") and the raid sets no
                                       ladder of its own (raider-faction ways stay 0).
  LADDER_PARITY_RAID_BRINGS_SOME_LADDERS (--carriers, a storyteller raid) with the raid-ladder chance forced to 100 % for the
                                       run (restored after), at least one raider and never every raider arrives carrying a
                                       minified portable ladder.
  LADDER_PARITY_RAIDER_FELLS_TREE (--direct --depth 4 --trees) TREES (default 6) mature Plant_TreeOak stand 10..15 squares
                                       east of the east bank (inside the 30 the criterion names); the direct raiders carry no
                                       ladder, so one should fell a tree to make one (RM_RaiderChopForLadder). EXPECT fewer
                                       oaks standing at the end than were planted (a stump, if the game leaves one, is
                                       recorded), or an RM_RaiderChopForLadder job seen in a raider's job trace. LIES: no oak
                                       planted (terrain refused) or no raider within 15 squares = UNMEASURED; a raider that
                                       crossed some other way first may never need a tree (recorded as `crossedOtherwise`).
                                       Written offline 2026-10-23 (area P); OWED to its first live run.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
for _p in (UTILS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

PROOF_TYPE = "RimMandrake.FlowWorks.RM_NorthstarProofs"
HPROBE = "RimMandrake.FlowWorks.Hose.HoseProbe"
OUT = os.path.join(REPO, "Transient", "fw_scenes", "live")
CHUNK = 250
NEAR = 15


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def classify(samples, c):
    """samples: [{tick, raiders:[{id,x,z,dead,downed,spawned}]}] -> (outcome words, detail). Pure."""
    seen, on_island, in_trench, near, gone_alive = set(), set(), set(), set(), set()
    last = {}
    moved_late = 0.0
    # a sample with no position (list_pawns gives x=None for an unspawned pawn) says nothing about where it stood
    samples = [dict(s, raiders=[r for r in s["raiders"] if r.get("x") is not None and r.get("z") is not None]) for s in samples]
    for s in samples:
        for r in s["raiders"]:
            seen.add(r["id"])
            p = (r["x"], r["z"])
            d = cheb(p, c)
            if r.get("spawned", True) and not r.get("dead"):
                if d <= 4:
                    on_island.add(r["id"])
                elif d <= 6:
                    in_trench.add(r["id"])
                if d <= NEAR:
                    near.add(r["id"])
    # movement over the last third of the samples, per alive raider near the trench
    tail = samples[len(samples) * 2 // 3:]
    for s in tail:
        for r in s["raiders"]:
            p = (r["x"], r["z"])
            if r["id"] in last and not r.get("dead") and not r.get("downed"):
                moved_late += cheb(p, last[r["id"]])
            last[r["id"]] = p
    end = {r["id"]: r for r in (samples[-1]["raiders"] if samples else [])}
    ever_dead = {r["id"] for s in samples for r in s["raiders"] if r.get("dead")}
    gone_alive = {i for i in seen if i not in end and i not in ever_dead}
    alive_near_end = [r for r in end.values() if not r.get("dead") and not r.get("downed") and cheb((r["x"], r["z"]), c) <= NEAR]
    words = []
    if on_island:
        words.append("BREACH")
    if in_trench:
        words.append("FELL")
    if gone_alive:
        words.append("LEFT")
    if alive_near_end:
        per = moved_late / max(1, len(alive_near_end)) / max(1, len(tail))
        words.append("MILL" if per >= 1.0 else "STALL")
    alive_end = [r for r in end.values() if not r.get("dead") and not r.get("downed")]
    if not near and alive_end:
        # LIVE 2026-10-17 first run: 10 raiders under LordJob_AssaultColony never came within 33 squares in 15,000 ticks
        # while moving ~20 squares per sample: they never reached the trench at all, which is neither STALL nor MILL at it
        per_far = moved_late / max(1, len(alive_end)) / max(1, len(tail))
        words.append("MILL_FAR" if per_far >= 1.0 else "STALL_FAR")
    # LIVE 2026-10-17 (--direct): the colonists went DOWN on the island while no hostile came within 18 squares: a gunner
    # stood 18 out and shot across the trench. Record when the first colonist went down and how close the nearest
    # hostile was then, so "shot across" is read from data, not inferred.
    first_down = next((s for s in samples if any(q.get("downed") or q.get("dead") for q in s.get("colonists") or []
                                                if q.get("x") is not None and cheb((q["x"], q["z"]), c) <= 4)), None)
    fd = None
    if first_down:
        ds = [cheb((r["x"], r["z"]), c) for r in first_down["raiders"] if r.get("x") is not None and not r.get("dead")]
        fd = dict(tick=first_down["tick"], nearestHostile=min(ds) if ds else None)
        if ds and min(ds) > 6:
            words.append("SHOT_ACROSS")
    det = dict(firstColonistDownOnIsland=fd, raidersSeen=len(seen), onIsland=sorted(on_island), inTrench=sorted(in_trench), cameNear=sorted(near),
               despawnedAlive=sorted(gone_alive), aliveNearAtEnd=len(alive_near_end),
               lateMovePerRaiderPerSample=round(moved_late / max(1, len(alive_near_end) or 1) / max(1, len(tail)), 2))
    return words or ["NONE_ARRIVED"], det


def storyteller_value(B):
    """The live DebugSettings.enableStoryteller, or None when the list reply cannot be read (never a guessed default)."""
    r = B.call("jawa/debug_settings", action="list") or {}
    for f in r.get("fields") or []:
        if f.get("name") == "enableStoryteller" and isinstance(f.get("value"), bool):
            return f["value"]
    return None


def restore_storyteller(B, prior):
    """Put enableStoryteller back to what the run found; -> (ok, note). Reads the reply back: a refused set is not a restore."""
    if prior is None:
        return False, "prior value was never read (UNMEASURED): storyteller left as the run set it"
    r = B.call("jawa/debug_settings", action="set", field="enableStoryteller", value=bool(prior)) or {}
    if r.get("success") is True and r.get("valueAfter") == bool(prior):
        return True, "enableStoryteller restored to %s" % prior
    return False, "restore of enableStoryteller to %s NOT confirmed: %s" % (prior, json.dumps(r, default=str)[:200])


def job_trace(B, pid):
    """RM_RaiderTrench.ProofJobTrace for one raider, as text; a refused or raising call is its own text, never a crash."""
    try:
        r = B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_RaiderTrench", method="ProofJobTrace", args=pid,
                   _answer=True) or {}
    except Exception as ex:  # noqa: BLE001 - diagnostics only (IndeterminateError after an unknown-outcome call)
        return ("unread: %s: %s" % (type(ex).__name__, ex))[:600]
    return str(r.get("result") or "no answer")[:600]


def parity(B, arg):
    """RM_LadderParity.ProofLadderParity, as text; a refused or raising call is its own text, never a crash."""
    try:
        r = B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_LadderParity", method="ProofLadderParity", args=arg) or {}
        return str(r.get("result") or r.get("message") or r)[:600]
    except Exception as ex:  # noqa: BLE001
        return "ERROR %s: %s" % (type(ex).__name__, ex)


TREE_DEF = "Plant_TreeOak"


def tree_spots(c, n=6):
    """n oak squares 10..15 east of the east bank (bank at c.x+7), 3 apart on z, clear of the --direct spawn (c.x+30). Pure."""
    return [(c[0] + 17 + 2 * (i % 3), c[1] - 6 + 4 * (i // 3) + (i % 3)) for i in range(n)]


def tree_verdict(planted, standing_after, chop_seen, came_near):
    """-> (status, why). planted / standing_after: oak counts on the tree squares. Pure."""
    if not planted:
        return "UNMEASURED", "no oak stood after planting (terrain refused)"
    if standing_after is None:
        return "UNMEASURED", "the oaks could not be counted at the end"
    if standing_after < planted or chop_seen:
        return "PASS", ""
    if came_near < 1:
        return "UNMEASURED", "no raider came within 15 squares"
    return "FAIL", "raiders came near, every oak still stands and no RM_RaiderChopForLadder job was seen"


def main(argv=None):
    """Runs the proof; the storyteller setting is restored in a finally whatever the body does (raise, Ctrl-C, early return)."""
    hold = {}
    try:
        return _run(argv, hold)
    finally:
        if hold.get("changed"):
            ok, note = restore_storyteller(hold["B"], hold.get("prior"))
            print("storyteller restore: %s" % note, flush=True)
            hold["restore"] = (ok, note)
            if hold.get("log") is not None:
                hold["log"].append("storyteller restore: " + note)
            if hold.get("save"):
                try:
                    hold["save"]()
                except Exception:  # noqa: BLE001
                    pass


def _run(argv, hold):
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=os.path.join(OUT, "raid_trench_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--points", type=float, default=500)
    ap.add_argument("--ticks", type=int, default=15000)
    ap.add_argument("--jump-packs", action="store_true", help="--direct only: every gunner wears Apparel_PackJump "
                    "(RAIDERS_TRENCH A4: a jump-pack raider jumps the trench and lands on its feet)")
    ap.add_argument("--preladder", action="store_true", help="--direct only: the raid's own scaling ladders already stand on "
                    "both walls on the east row (TRENCH_CROSSING A3: it walks straight across); colonists boxed")
    ap.add_argument("--colony-ladders", action="store_true", help="--direct only: the PLAYER's portable ladders stand on both "
                    "walls of the east row (LADDER_PARITY: raiders climb them, no keys); colonists boxed")
    ap.add_argument("--trees", type=int, default=0, help="--direct only: plant N mature oaks east of the bank "
                    "(LADDER_PARITY_RAIDER_FELLS_TREE; 6 is the written scene)")
    ap.add_argument("--carriers", action="store_true", help="storyteller raid with the raid-ladder chance forced to 100%% for "
                    "the run: LADDER_PARITY_RAID_BRINGS_SOME_LADDERS")
    ap.add_argument("--depth", type=int, default=4, help="ring depth in notches (4 = 2 m; 8 = 4 m, past the 3 m portable "
                    "ladder reach: RAIDERS_TRENCH A3 expects a fill causeway)")
    ap.add_argument("--direct", action="store_true", help="spawn 6 pirates 30 squares east into LordJob_AssaultColony "
                    "instead of a storyteller raid (which may stage or mill far off)")
    a = ap.parse_args(argv)
    import validation_core as V
    B = V.Bridge()
    rows, samples, log = [], [], []
    hold["B"], hold["log"] = B, log
    res = {"script": "raid_trench_proof.py", "mode": "live", "rows": rows, "samples": samples, "log": log}

    def save():
        with open(a.out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(a.out + ".tmp", a.out)

    def say(s):
        print(s, flush=True)
        log.append(s)

    def row(rid, st, det):
        rows.append({"id": rid, "status": st, "detail": det})
        say("%-26s %-10s %s" % (rid, st, json.dumps(det, default=str)[:600]))
        save()

    def feed():
        for p in B.probe_of(HPROBE, "colonists").get("pawns") or []:
            for need in ("Food", "Rest"):
                B.call("jawa/pawn_need", pawn=p["id"], action="need", need=need, level=1.0)

    def adv(n):
        r = B.call("jawa/safe_advance", ticks=n, stopOn="cancel", timeoutMs=max(60000, n * 100)) or {}
        if isinstance(r, dict) and r.get("content"):
            r = json.loads(r["content"][0]["text"])
        return r

    # ------------------------------------------------------------ map
    if a.fresh_map:
        if (B.call("rimworld/get_ui_state") or {}).get("programState") == "Playing":
            B.call("rimworld/go_to_main_menu")
            time.sleep(5)
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
        ok, waited = V._wait_playing(B, leave_s=0)
        say("quicktest map up: %s (%s s)" % (ok, waited))
    res_calm = V.clear_threat_structures(B)   # TESTENV_PREFLIGHT_HARDEN_TRISPIKE_AT_ARM (storyteller is handled below)
    say("threat structures: %s" % res_calm)
    B.call("rimworld/pause_game", pause=True)
    B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    B.call("jawa/incident_queue_clear")
    # LIVE 2026-10-17: with the storyteller on, a fleshbeast assault (Entities) landed on the island mid-run and downed
    # the colonists; the scene must hold only the attackers it names
    hold["prior"] = storyteller_value(B)
    hold["save"] = save
    off = B.call("jawa/debug_settings", action="set", field="enableStoryteller", value=False) or {}
    hold["changed"] = True          # even a refused set is restored: its effect is not known
    if not (off.get("success") is True and off.get("valueAfter") is False):
        say("WARNING: storyteller NOT confirmed off (%s): a stray incident may land on the island" % json.dumps(off, default=str)[:200])
        res["storytellerOff"] = "UNCONFIRMED"
    # PROOF_SWEEPS_FIX_OTHER_ZOOS_STILL_OPEN: on a map we did not make keep its own non-colonists (staged animals, prisoners)
    res["sweep_start"] = V.sweep_at_start(B, made_map=a.fresh_map)
    B.call("rimworld/set_god_mode", enabled=True)
    mi = B.call("jawa/map_info") or {}
    c = (int(mi.get("sizeX", 250)) // 2, int(mi.get("sizeZ", 250)) // 2)
    res["centre"] = c
    rect = (c[0] - 10, c[1] - 10, 21, 21)
    B.call("jawa/static_call", type=PROOF_TYPE, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    # HARNESS (live 20261023T044826): prepare_site's verdict was dropped -- set_terrain_batch refused part of the site
    # (fish map, TemperateForest river near the centre), the run dug its ring anyway and RAID_island_sealed read a
    # moat that was never a clean dry ring (bits 0xFF) as a MOD FAIL. A site that did not read back clear runs nothing.
    site_rows = []
    if not V.prepare_site(B, rect, site_rows, "raid_site"):
        why = (site_rows[-1].get("detail") if site_rows and isinstance(site_rows[-1], dict) else None) or "prepare_site refused"
        res["siteNotReady"] = why
        for rid in ("RAID_island_sealed", "RAID_outcome", "MASKSWAP_no_wall_crossing",
                    "RAID_LADDER_BREACH" if a.depth <= 6 else "RAID_FILL_CAUSEWAY"):
            row(rid, "UNMEASURED", {"class": "SITE", "why": "the raid site did not read back clear; nothing dug or fired",
                                    "site": why})
        return 2
    ring = [(x, z) for x in range(c[0] - 6, c[0] + 7) for z in range(c[1] - 6, c[1] + 7) if cheb((x, z), c) >= 5]
    dug = {}   # the depth each ring square actually reached: a dig stopped short (bedrock) is not the raid's fill
    for cell in ring:
        dr0 = B.call("jawa/flowworks_excavation_drive", x=cell[0], z=cell[1], deepenLevels=a.depth, setFill=-1) or {}
        dug[cell] = dr0.get("depth") if isinstance(dr0.get("depth"), int) else None
    res["ringShort"] = sorted((c_[0], c_[1], d_) for c_, d_ in dug.items() if d_ is None or d_ < a.depth)
    churn = (c[0] + 9, c[1])
    cols = B.probe_of(HPROBE, "colonists").get("pawns") or []
    for i, p in enumerate(cols):
        B.probe_of(HPROBE, "pawn:%d=tp:%d,%d" % (p["id"], c[0] - 2 + (i % 4), c[1] + (i // 4)))
    if a.jump_packs or a.preladder or a.colony_ladders:
        # SITE (belt live 2026-10-22, first --jump-packs run): the gunners shot every island colonist down across the moat by
        # t+4000, after which RM_RaiderTrench.TargetFor has no free colonist and nobody crosses. The colonists stand inside a
        # closed granite box (Chebyshev 3), out of sight, as drawbridge_proof's RAID_UP does.
        box = [(x, z) for x in range(c[0] - 3, c[0] + 4) for z in range(c[1] - 3, c[1] + 4) if cheb((x, z), c) == 3]
        B.call("jawa/spawn_batch", ops=";".join("Wall:%d,%d" % b_ for b_ in box), stuff="BlocksGranite")
    feed()
    adv(70)
    say("scene: centre %s, island 9x9, trench %d squares D 4 (2 m) width 2, colonists on the island: %s" % (
        c, len(ring), [p["id"] for p in cols]))

    # ------------------------------------------------------------ sealed?
    # the masks derive lazily (LIVE 2026-10-17: the first read after digging said bits=0xFF derived=False, a read of an
    # underived mask, and later read 0xCB derived=True): only a derived=True read counts
    bits, txt = None, ""
    for _ in range(6):
        r = B.call("jawa/static_call", type=PROOF_TYPE, method="ProofClimb", args="mask:%d,%d;2" % (c[0] + 4, c[1])) or {}
        txt = str(r.get("result") or r.get("message") or "")
        if "derived=True" in txt:
            bits = next((int(tok[5:], 16) for tok in txt.split() if tok.startswith("bits=")), None)
            break
        adv(60)
    sealed = "UNMEASURED" if bits is None else ("PASS" if not bits & 0x04 else "FAIL")
    row("RAID_island_sealed", sealed,
        {"read": txt[:200], "eastBit": None if bits is None else bool(bits & 0x04)})

    # ------------------------------------------------------------ raid
    if a.direct:
        # LIVE 2026-10-17: two storyteller raids never reached the trench (AssaultColony milled 33+ squares out for 15,000
        # ticks; a StageThenAttack tribe staged 54+ squares out for 30,000). --direct puts known pawns 30 squares east
        # straight into vanilla's LordJob_AssaultColony (the graph a raid's assault phase uses), defaults kept.
        ids = []
        probe = B.call("jawa/spawn_pawn", kindDef="Mercenary_Gunner", x=c[0] + 30, z=c[1], faction="?", count=1) or {}   # spawn_pawn has NO dryRun (an unknown arg is silently dropped);
        # the unknown faction "?" is what makes it refuse and list `available`, so nothing spawns
        avail = (probe.get("details") or {}).get("available") or []
        fac = next((f_["def"] for f_ in avail if f_.get("hostile") and str(f_.get("def")).startswith("Pirate")),
                   next((f_["def"] for f_ in avail if f_.get("hostile") and f_.get("def") not in ("Entities", "Mechanoid", "Insect")), None))
        if fac is None:
            say("no hostile humanlike faction readable from spawn_pawn's refusal: --direct cannot stage (UNMEASURED)")
            row("RAID_outcome", "UNMEASURED", dict(why="no assault faction available", reply=json.dumps(probe, default=str)[:300]))
            return 2
        say("assault faction: %s (hostile factions on this map: %s)" % (fac, [f_["def"] for f_ in avail if f_.get("hostile")]))
        for kind, n in (("Mercenary_Gunner", 4), ("Mercenary_Slasher", 2)):
            sp = B.call("jawa/spawn_pawn", kindDef=kind, x=c[0] + 30, z=c[1], faction=fac, count=n) or {}
            ids += [str(p_.get("id")) for p_ in sp.get("pawns") or []]
        if a.preladder or a.colony_ladders:
            pre = "RM_LadderPortable:%d,%d,1;RM_LadderPortable:%d,%d,3" % (c[0] + 6, c[1], c[0] + 5, c[1])   # outer wall faces the east bank, inner the island
            # LADDER_PARITY: --colony-ladders builds the same two ladders as the PLAYER's (build_batch's default faction)
            kw = {} if a.colony_ladders else {"faction": fac}
            res["preladder"] = str(B.call("jawa/build_batch", ops=pre, wipeExisting=False, **kw) or {})[:300]
            adv(70)
        if a.jump_packs:
            for i_ in ids:
                B.call("jawa/pawn_gear", pawn=i_, action="wear", **{"def": "Apparel_PackJump"})
        if a.trees:
            spots = tree_spots(c, a.trees)
            for x_, z_ in spots:
                B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (x_, z_), categories="All")
                B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,1,1" % (x_, z_))
                B.call("jawa/set_plants", ops="%s:%d,%d,1,1" % (TREE_DEF, x_, z_), growth=1.0)
            res["treeSpots"] = spots
            res["treesPlanted"] = sum(1 for x_, z_ in spots if (B.call("jawa/list_things", defName=TREE_DEF,
                                      rect="%d,%d,1,1" % (x_, z_), limit=2) or {}).get("things"))
        fr = B.call("jawa/lord_assault_spawn", pawns=",".join(ids)) or {}
        say("direct assault: %d pawns %s; lord %s" % (len(ids), ids, json.dumps(fr, default=str)[:300]))
    else:
        if a.carriers:
            res["ladderChance"] = parity(B, "chance:100")
        fr = B.call("jawa/fire_raid", dryRun=False, points=a.points) or {}
        say("raid fired: success=%s %s" % (fr.get("success"), json.dumps(fr, default=str)[:300]))
        if a.carriers:
            # PostProcessSpawnedPawns hands the ladders out as the raid spawns: read them now, then restore the chance
            txt_c = parity(B, "carriers")
            was = next((t_[4:] for t_ in str(res["ladderChance"]).split() if t_.startswith("was=")), None)
            res["ladderChanceRestore"] = parity(B, "chance:%s" % was) if was is not None else "NOT RESTORED (no prior read)"
            kv = dict(t_.split("=", 1) for t_ in txt_c.split() if "=" in t_)
            try:
                nr, nc = int(kv.get("raiders")), int(kv.get("carriers"))
                st_c = "PASS" if nr >= 2 and 1 <= nc < nr else "FAIL"
            except (TypeError, ValueError):
                st_c = "UNMEASURED"
            row("LADDER_PARITY_RAID_BRINGS_SOME_LADDERS", st_c, {"read": txt_c, "chance": res["ladderChance"],
                "restore": res["ladderChanceRestore"], "bar": "raiders >= 2; 1 <= carriers < raiders"})
    res["raid"] = fr
    t, k = 0, 0
    while t < a.ticks:
        k += 1
        if k % 2 == 0:
            B.call("jawa/flowworks_excavation_drive", x=churn[0], z=churn[1], deepenLevels=4, setFill=-1)
        else:
            B.call("jawa/flowworks_excavation_drive", x=churn[0], z=churn[1], deepenLevels=0, setFill=-1, fillInLevels=4)
        if k % 20 == 0:
            feed()
        ar = adv(CHUNK)
        t += int(ar.get("executed") or 0) or CHUNK
        lp = B.call("jawa/list_pawns", includeHealth=False, includeCorpses=True, limit=500) or {}
        raiders = [dict(id=p["id"], x=p.get("x"), z=p.get("z"), dead=p.get("dead"), downed=p.get("downed"),
                        spawned=p.get("spawned"), kind=p.get("kindDef"))
                   for p in lp.get("pawns") or [] if p.get("hostile")]       # every hostile, beasts too (kind kept)
        colon = [dict(id=p["id"], x=p.get("x"), z=p.get("z"), dead=p.get("dead"), downed=p.get("downed"))
                 for p in lp.get("pawns") or [] if p.get("isPlayer") and p.get("intelligence") == "Humanlike"]
        samples.append(dict(tick=t, advance=ar.get("state"), raiders=raiders, colonists=colon))
        if a.trees and k % 4 == 0:
            for r_ in raiders:
                if r_.get("spawned") and not r_.get("dead") and "RM_RaiderChopForLadder" in job_trace(B, r_["id"]):
                    res.setdefault("chopSeen", []).append((t, r_["id"]))
        if k % 8 == 0 or k == 1:
            near = [r_ for r_ in raiders if r_["x"] is not None and cheb((r_["x"], r_["z"]), c) <= NEAR]
            say("  t+%5d  raiders %d (near %d, dead %d, downed %d)  closest %s  colonists down/dead %d" % (
                t, len(raiders), len(near), sum(1 for r_ in raiders if r_["dead"]), sum(1 for r_ in raiders if r_["downed"]),
                min([cheb((r_["x"], r_["z"]), c) for r_ in raiders if r_["x"] is not None] or [None]),
                sum(1 for q in colon if q["dead"] or q["downed"])))
            save()
        if any(r_["x"] is not None and cheb((r_["x"], r_["z"]), c) <= 4 and not r_["dead"] for r_ in raiders):
            say("  BREACH: a raider stands on the island at t+%d" % t)
            break
        if k > 8 and raiders and all(r_["dead"] or not r_["spawned"] for r_ in raiders):
            break
    for r_ in samples[-1]["raiders"] if samples else []:
        if r_["x"] is not None:
            B.call("rimworld/frame_cell_rect", x=c[0] - 20, z=c[1] - 20, width=41, height=41, paddingCells=2)
            break
    sh = B.call("jawa/take_screenshot", fileName="raid_trench_%d" % int(time.time())) or {}
    res["screenshot"] = sh.get("filePath")
    words, det = classify(samples, c)
    det["ticksWatched"] = t
    lords = B.call("jawa/lord_pawn_move", action="list") or {}
    det["lords"] = [dict(job=l.get("job"), faction=l.get("faction"), pawns=l.get("pawnCount")) for l in lords.get("lords") or []]
    # CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP (live 2026-10-22: lip raiders in Wait 9,000 ticks, ProofDecision = RM_RaiderFillTrench):
    # per live raider at the end, its duty, lord toil, job and the giver that made it (none = vanilla's error-recover Wait),
    # how its trench-work jobs ended (sameTick = ended the tick they started: the 10-jobs-a-tick loop), and the reach checks
    # the next job's first toil meets. Read-only; an old DLL without the method reads its refusal, which is data.
    # HARNESS (live_session 20261022T235239 B8): an earlier tps_report timed out with an UNKNOWN outcome, so the client
    # refused this static_call (IndeterminateError) and the crash lost every row after it. The trace is diagnostics: a
    # refused read is recorded as text and the verdict rows below still run.
    if samples:
        det["jobTrace"] = {r_["id"]: job_trace(B, r_["id"])
                           for r_ in (samples[-1]["raiders"] if samples else []) if r_.get("spawned") and not r_.get("dead")}
    row("RAID_outcome", "MEASURED", dict(outcome=words, **det))
    cameNear = len(det["cameNear"])
    crossed = det["onIsland"] + det["inTrench"]
    # RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP (owner ruling: raiders set ladders, fill, jump) made a crossing LEGAL when the raid
    # put its own way across. HARNESS (BENCH belt 2026-10-22, --direct run): MASKSWAP read FAIL on two raiders who went down
    # and up by their own RM_LadderPortable at (131,125) -- the bar predated the ruling. Raider ways across are read back: a
    # crossing with one is the breach row's business and leaves the mask question UNMEASURED; a crossing without is a FAIL.
    ways = []
    for dn in ("RM_LadderPortable", "RM_RaidPlank", "RM_Ladder"):
        lt = B.call("jawa/list_things", defName=dn, rect="%d,%d,15,15" % (c[0] - 7, c[1] - 7), limit=50) or {}
        ways += [dict(def_=t.get("def"), x=t.get("x"), z=t.get("z"), faction=t.get("faction")) for t in lt.get("things") or []
                 if t.get("faction") and not str(t.get("faction")).startswith("Player") and cheb((t.get("x"), t.get("z")), c) in (4, 5, 6, 7)]
    if cameNear < 2 or sealed != "PASS":
        ms = "UNMEASURED"
    elif not crossed:
        ms = "PASS"
    else:
        # a jump-pack crossing is legal too (A4): with --jump-packs worn the mask question is masked as by a ladder
        ms = "UNMEASURED" if (ways or a.jump_packs or a.preladder) else "FAIL"
    row("MASKSWAP_no_wall_crossing", ms,
        {"raidersWithin15": cameNear, "islandSealed": sealed, "sampledOnIslandOrTrench": crossed, "churnRebuilds": k,
         "raiderWays": ways, "caveat": "sampled every %d ticks; never seen, not proven impossible; a crossing over the raid's "
                                       "own ladder/plank is legal (RAIDERS_TRENCH) and masks the question" % CHUNK})
    # RAIDERS_TRENCH A2: a raid against a base ringed by a sheer 2 m trench no longer stalls -- it sets a way across and walks in
    # HARNESS (belt 2026-10-22 raid_3): 'a raider on the island' was too strict -- the raiders laddered both walls, shot every
    # island colonist down from the trench and LEFT (the raid had won). The ruling's bar is "no longer stalls: set a ladder
    # down and up": a raider-faction way on BOTH walls (Chebyshev 6 outer, 5 inner) and a raider sampled in the trench or on
    # the island. A raid that came near and put no way across is the stall (FAIL).
    # RAIDERS_TRENCH A3 (--depth 8): a ring square the raid FILLED reads shallower than dug (a causeway); read back every ring
    # square's depth (the dig itself is the scene's only writer, so any shallower square is the raid's fill)
    filled = []
    try:
        for x in range(c[0] - 6, c[0] + 7):
            for z in range(c[1] - 6, c[1] + 7):
                if cheb((x, z), c) in (5, 6):
                    dr = B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=0, setFill=-1) or {}
                    if isinstance(dr.get("depth"), int) and dug.get((x, z)) is not None and dr["depth"] < dug[(x, z)]:
                        filled.append((x, z, dr["depth"]))
    except Exception as ex:  # noqa: BLE001 - the client refuses a mutating tool after an unknown-outcome call (see jobTrace)
        filled, det["ringReadError"] = None, ("%s: %s" % (type(ex).__name__, ex))[:300]
    det["ringDepth"], det["filledSquares"], det["ringDugShort"] = a.depth, filled, res["ringShort"]
    walls = sorted({cheb((w["x"], w["z"]), c) for w in ways})
    both = 5 in walls and 6 in walls
    used = bool(det["onIsland"] or det["inTrench"])
    a2 = ("UNMEASURED" if cameNear < 2 or sealed != "PASS" else
          "PASS" if (both and used) else "FAIL")
    if a.depth > 6:
        # 4 m: past the portable ladder's reach -> the fill causeway is the legal way (A3); a ladder there is a FAIL of its own
        a2 = ("UNMEASURED" if cameNear < 2 or sealed != "PASS" or filled is None else
              "PASS" if (filled and used) else "FAIL")
    if a.jump_packs:
        # A4: a raider who reached the island over a trench nobody laddered or filled jumped; no descent recorded for him
        pr_ = B.call("jawa/flowworks_pit_report", x=c[0] + 6, z=c[1]) or {}
        desc = [str(x) for x in pr_.get("recentDescents") or []]
        fell = [i_ for i_ in det["onIsland"] if any(d_.startswith(str(i_) + "@") for d_ in desc)]
        st_j = ("UNMEASURED" if cameNear < 2 or sealed != "PASS" or filled is None else
                "PASS" if det["onIsland"] and not fell and not ways and not filled else "FAIL")
        row("RAID_JUMP_LANDS_UNHURT", st_j, {"onIsland": det["onIsland"], "fellOnTheWay": fell, "raiderWays": ways,
                                             "filledSquares": filled, "recentDescents": desc[-8:],
                                             "bar": "a raider on the island with no ladder/fill and no descent of his recorded"})
    if a.preladder:
        # TRENCH_CROSSING A3: with both walls laddered beforehand the raid crosses on them -- a raider on the island and no
        # extra ladder set (the two pre-placed ones are the only raider ways)
        st_p = ("UNMEASURED" if cameNear < 2 or sealed != "PASS" else
                "PASS" if det["onIsland"] and len(ways) <= 2 else "FAIL")
        row("RAID_PRELADDERED_CROSSES", st_p, {"onIsland": det["onIsland"], "inTrench": det["inTrench"], "raiderWays": ways,
                                               "preladder": res.get("preladder"), "ticksWatched": det.get("ticksWatched")})
    if a.colony_ladders:
        # LADDER_PARITY: the player's ladders carry the raid across; the raid needs none of its own
        st_k = ("UNMEASURED" if cameNear < 2 or sealed != "PASS" else
                "PASS" if det["onIsland"] and not ways else "FAIL")
        row("LADDER_PARITY_RAIDERS_USE_COLONY_LADDERS", st_k, {"onIsland": det["onIsland"], "inTrench": det["inTrench"],
            "raiderWays": ways, "preladder": res.get("preladder"),
            "bar": "a raider on the island over the PLAYER's two ladders; no raider-faction way set"})
    if a.depth > 6 and filled:
        # LADDER_PARITY: each filled square carries its scar at the dug depth; the real designator orders it dug back
        reps = {"%d,%d" % (x, z): parity(B, "repair:%d,%d" % (x, z)) for x, z, _d in filled}
        good = [k_ for k_, v_ in reps.items()
                if "accepted=True" in v_ and "digTarget=%s" % dug.get(tuple(int(q) for q in k_.split(","))) in v_]
        row("LADDER_PARITY_BREACH_SCAR_REPAIR", "PASS" if len(good) == len(reps) else "FAIL",
            {"repairs": reps, "dug": {"%d,%d" % k_: v_ for k_, v_ in dug.items() if "%d,%d" % k_ in reps},
             "bar": "every filled square: Repair breach accepted, dig-to target = the depth it was dug to"})
    elif a.depth > 6:
        row("LADDER_PARITY_BREACH_SCAR_REPAIR", "UNMEASURED", {"why": "the raid filled no square", "filled": filled})
    if a.trees:
        spots = res.get("treeSpots") or []
        try:
            left = sum(1 for x_, z_ in spots if (B.call("jawa/list_things", defName=TREE_DEF, rect="%d,%d,1,1" % (x_, z_),
                                                       limit=2) or {}).get("things"))
            stumps = [t_.get("def") for x_, z_ in spots for t_ in (B.call("jawa/list_things", rect="%d,%d,1,1" % (x_, z_),
                      limit=5) or {}).get("things") or [] if "stump" in str(t_.get("def") or t_.get("defName")).lower()]
        except Exception as ex:  # noqa: BLE001 - an unknown-outcome client refuses later calls (see jobTrace)
            left, stumps = None, ["unread: %s" % ex]
        st_t, why_t = tree_verdict(res.get("treesPlanted") or 0, left, bool(res.get("chopSeen")), cameNear)
        row("LADDER_PARITY_RAIDER_FELLS_TREE", st_t, {"why": why_t, "planted": res.get("treesPlanted"), "standingAfter": left,
            "stumps": stumps, "chopSeen": res.get("chopSeen"), "raidersWithin15": cameNear, "crossedOtherwise": ways,
            "bar": "a ladderless raider fells an oak within 30 squares of the east bank"})
    if a.jump_packs or a.preladder or a.colony_ladders:
        a2 = "UNMEASURED"       # jump packs come first in the owner's order: ladders/fill are not asked of this run
    row("RAID_LADDER_BREACH" if a.depth <= 6 else "RAID_FILL_CAUSEWAY", a2,
        {"onIsland": det["onIsland"], "inTrench": det["inTrench"], "raiderWays": ways, "filledSquares": filled,
                                   "wallsLaddered": walls, "outcome": words,
                                   "bar": "raiders within 15 squares; raider-faction ladders/planks on both trench walls and a "
                                          "raider used them (in the trench or on the island) -- no stall"})
    save()
    say("result: %s" % os.path.relpath(a.out, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
