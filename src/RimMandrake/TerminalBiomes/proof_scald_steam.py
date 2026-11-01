#!/usr/bin/env python3
"""Live proof of the Scald's steam clock and water immunity (SCALD_STEAM_WEATHER_DESIGN_1). Drives the bridge, so run
it with Windows python, on a throwaway quicktest colony on a list holding mandrake.rm.biomes:

    python.exe src/RimMandrake/TerminalBiomes/proof_scald_steam.py setup          stage the two sites, print the roster
    python.exe src/RimMandrake/TerminalBiomes/proof_scald_steam.py run <out.json> [ticks]   advance and judge
    python.exe src/RimMandrake/TerminalBiomes/proof_scald_steam.py rejudge <out.json>       judge a finished run again

setup: a real surface RM_TheScald map on a warm tile (jawa/world_tile_map_generate, so the biome itself wires
RUT_ScaldSteamLock and RUT_ScaldSteamCarrier; a quicktest home map is a foreign biome with its own weather lock and
wildlife, which stopped the clock and killed the test pawns). Two naked colonists, one in RM_Apparel_RindCoat and one in
the boil-suit stand on land, each ringed by an unroofed wall; RM_Noohm, RM_Shulla and a control Muffalo stand in RUT_ScaldWaterShallow. Deaths are judged
from the damage log's kill events, never from sampled severity (samples sit 6000+ ticks apart).
run: a naked pawn dies under 120000 ticks (two days, the owner's card). The open sky also gives it Direct Sun
Heatstroke, and the stacked capacity losses kill it before exposure reaches 1.0, so the kill log credits whichever
slow hediff tipped it (seen: RUT_ScaldExposure, Malnutrition): that row asks only for a death by no wound with the
clock already past 0.7. The row that isolates the steam is naked_nosun: its Heatstroke is removed at every sample and
its kill must name RUT_ScaldExposure. The rind wearer lives the two days, the boil-suit wearer comes through a full day at
stage 0 or 1, natives carry neither burns nor exposure while logged standing in boiling water, and the control carries
a real Burn (it then usually drowns: burns down it and a downed pawn drowns in shallows, the swim rule's design).
Other pawns are removed at setup and on every sample, so no stray predator decides a row. run resumes: call it again
with the same out file until it prints its verdict.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

STATE = os.path.join(os.environ.get("TEMP", "."), "proof_scald_steam_roster.json")
DAY = 60000
LAND = ("naked", "rind", "boilsuit", "naked_nosun")
NATIVES = ("noohm", "shulla")


def bridge():
    h, p, t = rb.resolve_endpoint()
    c = rb.RimBridge(host=h, port=p, token=t, timeout=120)
    c.connect()
    return c


def call(c, tool, **kw):
    r = c.call(tool, kw, check=False)
    if isinstance(r, dict) and r.get("success") is False:
        print("REFUSED", tool, kw, str(r)[:300])
    return r


def pawns(c):
    return call(c, "jawa/list_pawns", limit=500, includeHealth=True, includeCorpses=True).get("pawns", [])


def spawn(c, kind, x, z, faction=None):
    before = {p.get("id") or p.get("thingId") for p in pawns(c)}
    kw = dict(kindDef=kind, x=x, z=z)
    if faction:
        kw["faction"] = faction
    call(c, "jawa/spawn_pawn", **kw)
    new = [p for p in pawns(c) if (p.get("id") or p.get("thingId")) not in before]
    if not new:
        raise SystemExit("spawn of %s made nothing" % kind)
    return new[0].get("id") or new[0].get("thingId")


def warm_tile(c):
    """A tile with no world object at a temperature that cannot hypothermia a naked pawn inside two days."""
    for tile in range(3000, 40000, 137):
        r = call(c, "jawa/world_tile_get", tiles=str(tile))
        row = (r.get("tiles") or r.get("rows") or [{}])[0]
        temp = row.get("temperature")
        if temp is not None and 14 <= temp <= 28 and not row.get("worldObjects"):
            return tile, temp
    raise SystemExit("no warm tile found")


def setup():
    c = bridge()
    call(c, "rimworld/pause_game", pause=True)
    tile, temp = warm_tile(c)
    # A player settlement: an Ambush parent is removed as soon as the map holds no living colonist.
    call(c, "jawa/colony_found", tile=tile, name="Scald proof")
    g = call(c, "jawa/world_tile_map_generate", tile=tile, sizeX=100, sizeZ=100, biome="RM_TheScald")
    call(c, "jawa/set_current_map", mapId=g["mapId"])
    print("tile", tile, "temp", temp, "map", g["mapId"], g.get("mapGenerator"))
    # Roofs first: clearing rock under a mountain roof drops it on the first tick and Crush kills the whole roster
    # (which also made the game remove an Ambush map), and a roofed cell stops the clock anyway.
    call(c, "jawa/set_roof_batch", ops="None:0,0,100,100")
    call(c, "jawa/destroy_batch", rects="20,30,40,20;20,55,40,30", categories="Plant,Item,Building,Filth")
    call(c, "jawa/set_terrain", x=20, z=30, terrainDef="Soil", width=40, height=20)
    call(c, "jawa/set_terrain", x=20, z=55, terrainDef="RUT_ScaldWaterShallow", width=40, height=30)
    roster = {
        "naked": spawn(c, "Colonist", 30, 40, "player"),
        "rind": spawn(c, "Colonist", 36, 40, "player"),
        "boilsuit": spawn(c, "Colonist", 42, 40, "player"),
        "naked_nosun": spawn(c, "Colonist", 48, 40, "player"),
        "noohm": spawn(c, "RM_Noohm", 30, 70),
        "shulla": spawn(c, "RM_Shulla", 38, 70),
        "control": spawn(c, "Muffalo", 46, 70),
    }
    for k in LAND:
        call(c, "jawa/pawn_gear", pawn=roster[k], action="clear")
    print(str(call(c, "jawa/pawn_gear", pawn=roster["rind"], action="wear", **{"def": "RM_Apparel_RindCoat"}))[:120])
    print(str(call(c, "jawa/pawn_gear", pawn=roster["boilsuit"], action="wear", **{"def": "RM_Apparel_BoilSuit"}))[:120])
    # A draft alone did not hold them: a naked pawn walked into the boil at 39000 ticks and drowned, spoiling the row
    # (a mental break undrafts). An unroofed steel ring keeps each one on its cell and still under the open sky.
    ring = ";".join("Wall:%d,%d" % (x + dx, 40 + dz) for x in (30, 36, 42, 48)
                    for dx in (-1, 0, 1) for dz in (-1, 0, 1) if dx or dz)
    print(str(call(c, "jawa/build_batch", ops=ring, stuff="Steel").get("survived")))
    for k in LAND:
        call(c, "jawa/set_draft", pawnId=roster[k], drafted=True)
    t0 = call(c, "rimworld/get_game_info")["ticksGame"]
    clear_strays(c, roster)
    # The ruling is two days OF STEAM. A still day (RUT_ScaldSteamLock's Clear burst) stops the clock by design, and
    # one landing inside the window left the naked pawn alive at 0.87 and falling: hold the steam for the whole run.
    print(str(call(c, "jawa/weather_set", weather="RUT_ScaldSteam", lockWeather=True))[:120])
    call(c, "jawa/damage_log", action="clear")
    json.dump({"roster": roster, "t0": t0}, open(STATE, "w"))
    print(json.dumps(roster))
    w = call(c, "jawa/weather_get")
    print(w.get("weather"), [q["def"] for q in w.get("conditions", [])])


def clear_strays(c, roster):
    """Wild predators on the site killed test pawns (a rind wearer died of a Bruise): only the roster may stay."""
    keep = set(roster.values())
    for p in pawns(c):
        pid = p.get("id") or p.get("thingId")
        if pid and pid not in keep and not p.get("dead") and not p.get("downed"):
            c.call("jawa/pawn_force_incapacitate", {"pawn": pid, "action": "vanish"}, check=False)


def read(c, pid):
    """A dead pawn is not 'spawned' and pawn_get refuses it: that refusal IS the death reading."""
    r = call(c, "jawa/pawn_get", pawn=pid)
    if r.get("success") is False:
        return None
    return (r.get("pawns") or [r])[0]


def terrain_under(c, p):
    pos = p.get("position") or p
    return (call(c, "rimworld/get_cell_info", x=pos.get("x"), z=pos.get("z")).get("cell") or {}).get("terrainDefName")


def hediffs(p):
    return [(h.get("def") or h.get("defName") or h.get("label"), h.get("severity")) for h in p.get("hediffs", [])]


def run(out, ticks, wall=420):
    c = bridge()
    st = json.load(open(STATE))
    roster, t0 = st["roster"], st["t0"]
    prior = json.load(open(out)) if os.path.exists(out) else {"log": [], "died": {}}
    log, died = prior["log"], prior["died"]
    start = time.time()
    while True:
        now = call(c, "rimworld/get_game_info")["ticksGame"]
        row = {"tick": now - t0, "weather": call(c, "jawa/weather_get").get("weather", {}).get("current")}
        for k, pid in roster.items():
            p = read(c, pid)
            if p is None or p.get("dead"):
                died.setdefault(k, now - t0)
                row[k] = {"dead": True, "hediffs": []}
            else:
                row[k] = {"hediffs": hediffs(p)}
                if k == "naked_nosun" and any(h[0] == "Heatstroke" for h in row[k]["hediffs"]):
                    call(c, "jawa/pawn_health", pawn=pid, action="remove", hediff="Heatstroke")
                if k in NATIVES:
                    row[k]["terrain"] = terrain_under(c, p)
        if not log or log[-1]["tick"] != row["tick"]:
            log.append(row)
        clear_strays(c, roster)
        json.dump({"log": log, "died": died}, open(out, "w"), indent=0)
        print(row["tick"], row["weather"], "died", died, "naked", row["naked"]["hediffs"][:4], "rind", row["rind"]["hediffs"][:4], flush=True)
        if now - t0 >= ticks:
            break
        if time.time() - start > wall:
            print("RESUME: call run again")
            return
        # A new player settlement opens Dialog_NamePlayerFaction after a while; it force-pauses and play_for then
        # refuses forever without advancing a tick.
        c.call("jawa/window_list_close", {"action": "close", "typeName": "Dialog_Name"}, check=False)
        # The control can burn, down and drown inside 10000 ticks: sample tight early or its Burn is never seen.
        call(c, "rimworld/play_for", durationMs=1500 if now - t0 < 9000 else 8000, speed=4)
    kills = call(c, "jawa/damage_log", pawnsOnly=True, kind="kill", limit=4096).get("events", [])
    judge(out, log, died, kills, roster, t0)


def judge(out, log, died, kills, roster, t0):
    last = log[-1]
    has = lambda r, name: any(h[0] == name for h in r.get("hediffs", []))  # noqa: E731
    kill = {k: next((e for e in kills if str(e.get("victimId")).replace("Thing_", "") == str(pid).replace("Thing_", "")), None)
            for k, pid in roster.items()}
    exposure = [h[1] for r in log for h in r["naked"]["hediffs"] if h[0] == "RUT_ScaldExposure"]
    in_water = {k: [r[k].get("terrain") for r in log if not r[k].get("dead")] for k in NATIVES}
    wet = lambda k: sum(str(t).startswith("RUT_ScaldWater") for t in in_water[k])  # noqa: E731
    steam = sum(b["tick"] - a["tick"] for a, b in zip(log, log[1:]) if a["weather"] == "RUT_ScaldSteam")
    v = {
        "steam_held": steam >= 0.9 * last["tick"],
        "naked_dies_under_2d": bool(kill["naked"]) and kill["naked"]["tick"] - t0 < 2 * DAY
        and not kill["naked"].get("damageDef") and max(exposure, default=0) > 0.7,
        "steam_alone_kills_under_2d": bool(kill["naked_nosun"]) and kill["naked_nosun"]["tick"] - t0 < 2 * DAY
        and kill["naked_nosun"].get("culpritHediff") == "RUT_ScaldExposure",
        "rind_survives": died.get("rind", 2 * DAY + 1) > 2 * DAY and last["tick"] >= 2 * DAY,
        # The spec's own bar (section 8 step 5): a full day out, still at stage 0 or 1. Heatstroke is the sun's, not the
        # steam's, and runs on past a day in the open, so a suit wearer needs a roof at night like anyone.
        "boilsuit_full_day": died.get("boilsuit", 2 * DAY) > DAY and all(
            h[1] < 0.35 for r in log if r["tick"] <= DAY and not r["boilsuit"].get("dead")
            for h in r["boilsuit"]["hediffs"] if h[0] == "RUT_ScaldExposure"),
        "natives_no_burn_no_exposure": not any(has(r[k], "Burn") or has(r[k], "RUT_ScaldExposure")
                                               for r in log for k in NATIVES),
        # Half the samples in boiling water, or the row above could pass on a native that walked ashore.
        "natives_stood_in_boil": all(wet(k) >= max(5, len(in_water[k]) / 2) for k in NATIVES),
        "control_burns": any(has(r["control"], "Burn") for r in log),
    }
    credit = {k: (kill[k]["tick"] - t0, kill[k].get("culpritHediff")) if kill[k] else None for k in roster}
    json.dump({"verdict": v, "kills": kills, "credit": credit, "t0": t0, "log": log, "died": died}, open(out, "w"), indent=0)
    print(json.dumps(credit))
    print(json.dumps(v))
    sys.exit(0 if all(v.values()) else 1)


if __name__ == "__main__":
    if sys.argv[1] == "setup":
        setup()
    elif sys.argv[1] == "rejudge":   # re-read a finished run's json with this judge; no bridge
        d, st = json.load(open(sys.argv[2])), json.load(open(STATE))
        judge(sys.argv[2], d["log"], d["died"], d["kills"], st["roster"], st["t0"])
    else:
        run(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 2 * DAY + 500)
