#!/usr/bin/env python3
"""Live proof of the Scald's steam clock and water immunity (SCALD_STEAM_WEATHER_DESIGN_1). Drives the bridge, so run
it with Windows python, on a throwaway quicktest colony on a list holding mandrake.rm.biomes:

    python.exe src/RimMandrake/TerminalBiomes/proof_scald_steam.py setup          stage the two sites, print the roster
    python.exe src/RimMandrake/TerminalBiomes/proof_scald_steam.py run <out.json> [ticks]   advance and judge

setup: a real surface RM_TheScald map on a warm tile (jawa/world_tile_map_generate, so the biome itself wires
RUT_ScaldSteamLock and RUT_ScaldSteamCarrier; a quicktest home map is a foreign biome with its own weather lock and
wildlife, which stopped the clock and killed the test pawns). A naked colonist, one in RM_Apparel_RindCoat and one in
the boil-suit stand on land; RM_Noohm, RM_Shulla and a control Muffalo stand in RUT_ScaldWaterShallow. run: the naked
one dies with RUT_ScaldExposure under 120000 ticks (two days, the owner's card), the rind wearer lives them out,
natives carry neither burns nor exposure, the control burns (proves the water bites). run resumes: call it again
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
    g = call(c, "jawa/world_tile_map_generate", tile=tile, sizeX=100, sizeZ=100, biome="RM_TheScald",
             suggestedMapParent="Ambush")
    call(c, "jawa/set_current_map", mapId=g["mapId"])
    print("tile", tile, "temp", temp, "map", g["mapId"], g.get("mapGenerator"))
    print(str(call(c, "jawa/settlement_remove", mode="map", tile=call(c, "jawa/set_current_map", mapId=g["mapId"])
               .get("previousTile", -1), force=True))[:120])
    call(c, "jawa/destroy_batch", rects="20,30,40,20;20,55,40,30", categories="Plant,Item,Building,Filth")
    call(c, "jawa/set_terrain", x=20, z=30, terrainDef="Soil", width=40, height=20)
    call(c, "jawa/set_terrain", x=20, z=55, terrainDef="RUT_ScaldWaterShallow", width=40, height=30)
    roster = {
        "naked": spawn(c, "Colonist", 30, 40, "player"),
        "rind": spawn(c, "Colonist", 36, 40, "player"),
        "boilsuit": spawn(c, "Colonist", 42, 40, "player"),
        "noohm": spawn(c, "RM_Noohm", 30, 70),
        "shulla": spawn(c, "RM_Shulla", 38, 70),
        "control": spawn(c, "Muffalo", 46, 70),
    }
    for k in ("naked", "rind", "boilsuit"):
        call(c, "jawa/pawn_gear", pawn=roster[k], action="clear")
    print(str(call(c, "jawa/pawn_gear", pawn=roster["rind"], action="wear", **{"def": "RM_Apparel_RindCoat"}))[:120])
    print(str(call(c, "jawa/pawn_gear", pawn=roster["boilsuit"], action="wear", **{"def": "RM_Apparel_BoilSuit"}))[:120])
    for k in ("naked", "rind", "boilsuit"):  # idle colonists otherwise wander into the boil and burn
        call(c, "jawa/set_draft", pawnId=roster[k], drafted=True)
    t0 = call(c, "rimworld/get_game_info")["ticksGame"]
    json.dump({"roster": roster, "t0": t0}, open(STATE, "w"))
    print(json.dumps(roster))
    w = call(c, "jawa/weather_get")
    print(w.get("weather"), [q["def"] for q in w.get("conditions", [])])


def read(c, pid):
    """A dead pawn is not 'spawned' and pawn_get refuses it: that refusal IS the death reading."""
    r = call(c, "jawa/pawn_get", pawn=pid)
    if r.get("success") is False:
        return None
    return (r.get("pawns") or [r])[0]


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
        log.append(row)
        json.dump({"log": log, "died": died}, open(out, "w"), indent=0)
        print(row["tick"], row["weather"], "died", died, "naked", row["naked"]["hediffs"][:4], "rind", row["rind"]["hediffs"][:4], flush=True)
        if now - t0 >= ticks:
            break
        if time.time() - start > wall:
            print("RESUME: call run again")
            return
        call(c, "rimworld/play_for", durationMs=8000, speed=4)
    judge(out, log, died, ticks)


def judge(out, log, died, ticks):
    last = log[-1]
    burn = lambda r: [h for h in r.get("hediffs", []) if "urn" in str(h[0]) or "Scald" in str(h[0])]  # noqa: E731
    exposure = [h[1] for r in log for h in r["naked"]["hediffs"] if h[0] == "RUT_ScaldExposure"]
    v = {
        "naked_dies_under_2d": "naked" in died and died["naked"] < 2 * DAY and bool(exposure) and max(exposure) > 0.8,
        "rind_survives": "rind" not in died and last["tick"] >= 2 * DAY,
        "natives_no_burn_no_exposure": not any(burn(r[k]) for r in log for k in ("noohm", "shulla")),
        "control_burns": any(burn(r["control"]) for r in log) or "control" in died,
    }
    json.dump({"verdict": v, "log": log, "died": died}, open(out, "w"), indent=0)
    print(json.dumps(v))
    sys.exit(0 if all(v.values()) else 1)


if __name__ == "__main__":
    if sys.argv[1] == "setup":
        setup()
    else:
        run(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 2 * DAY + 2000)
