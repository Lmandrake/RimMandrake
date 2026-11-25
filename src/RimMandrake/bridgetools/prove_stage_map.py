"""Live proof of RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS: the stage map holds the cast only, the green room keeps
the colony, and the scene library takes its stations from the stage's allocator. Pages:
design/specs/2026-11-23-bridge-v2/boundary.md §THE STATION ALLOCATOR and §THE STAGE MAP;
design/specs/2026-11-23-scene-library/boundary.md §STATIONS.

    python.exe src/RimMandrake/bridgetools/prove_stage_map.py [--game ArchSmall] [--log PATH] < /dev/null

It makes both stages itself (`stage_map.py make`, through wsl.exe: the maker takes the driver lock), then opens one scene
session at a time on a fresh load of a stage save. Six rows:
  R1 the stage holds zero pawns after make (both kinds), and stays empty over an idle day;
  R2 the green room's colonists are alive and fed after 60,000 ticks of an idle stage;
  R3 a raid fired at a settlement stage with cast defenders spawns raiders at an edge with an assault duty;
  R4 the same raid at a stage with no free colonist is reported "called, not fired";
  R5 the make time of each map kind is printed (settlement, pocket; colony is registered, not made);
  R6 a wild animal that appears on the stage is a breach on the receipt of s.stage and of the close.
Exit 0 = every row held, 1 = a row failed, 2 = no verdict (no bridge, the maker failed), 3 = no row failed and a raid row was\nrefused by the raid pause (raid_pause.py; the row reads PAUSED, never PASS).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

UTILS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils")
sys.path.insert(0, UTILS)
import scene  # noqa: E402

RAID_POINTS = 300
IDLE_TICKS = 60000
EDGE_CELLS = 6           # an edge walk-in spawns within a few cells of the edge (IncidentWorker_RaidEnemy, EdgeWalkIn)


def reply(r):
    """-> the bridge's reply dict inside an s.raw result."""
    for k in ("reply", "value", "result"):
        v = getattr(r, k, None)
        if isinstance(v, dict):
            return v
    return r if isinstance(r, dict) else {"raw": str(r)[:300]}


def raw(s, tool, **args):
    return reply(s.raw(tool, **args))


def wsl_make(game, verb, *extra):
    """Run stage_map.py in WSL (it takes the driver lock). -> (rc, output)."""
    here = os.path.abspath(os.path.join(UTILS, "stage_map.py"))
    m = re.match(r"^\\\\wsl(?:\.localhost|\$)\\[^\\]+(\\.*)$", here)      # \\wsl.localhost\<distro>\home\... -> /home/...
    unix = m.group(1).replace("\\", "/") if m else here
    t0 = time.time()
    # budget: danger=a hung wsl.exe (interop) holds the proof; evidence=wsl.exe interop failed twice on 2026-11-24; longest=53s (make pocket, 2026-11-24)
    p = subprocess.run(["wsl.exe", "python3", unix, verb, game] + list(extra), capture_output=True, text=True, encoding="utf-8",
                       errors="replace", stdin=subprocess.DEVNULL, timeout=1800)
    return p.returncode, p.stdout + p.stderr, time.time() - t0


PAUSE_WORD = "PAUSED: raid tests wait for the tools"


class Paused(Exception):
    pass


def fire_raid(s):
    """RaidEnemy at the current map. A refusal by the raid pause (raid_pause.py, the owner's of 2026-11-23) is Paused."""
    try:
        return raw(s, "jawa/fire_incident", incidentDef="RaidEnemy", points=RAID_POINTS, forced=True)
    except (scene.Fault, scene.Refused) as e:
        if PAUSE_WORD in str(e):
            raise Paused(str(e).split(". The work")[0][:240])
        raise


def open_session(game, save, calm=None):
    """scene.open on a fresh load of `save`. Retried once when the driver lock's WSL child died before it spoke: measured
    2026-11-24 (exit 4294967295, a wsl.exe interop failure), it is outside the stage and is not a reading of a row."""
    needs = {"map": save}
    if calm:
        needs["calm"] = calm
    try:
        return scene.open(game, needs=needs)
    except scene.Fault as e:
        if "the lock holder ended" not in str(e):
            raise
        print("  the lock holder died before it spoke (%s): opening again, once" % str(e).split("\n")[0][:160], flush=True)
        time.sleep(5)
        return scene.open(game, needs=needs)


def switch(s, mid):
    """Make map `mid` current and read it back. Measured 2026-11-24: right after rimworld/step_game_ticks a set_current_map
    replied success and the game stayed on the other map; the next call took. 20 tries guard a switch that never takes."""
    for _ in range(20):
        raw(s, "jawa/set_current_map", mapId=mid)
        if raw(s, "jawa/map_info").get("mapId") == mid:
            return
        time.sleep(0.5)
    raise scene.Fault("COULD_NOT_LOOK", detail="map %s did not become current in 20 tries" % mid)


def maps(s):
    r = raw(s, "jawa/set_current_map", mapId=-987654)
    return r.get("loadedMaps") or (r.get("details") or {}).get("loadedMaps") or []


def idle(s, ticks):
    """Let the game run `ticks` ticks at the top speed and pause again. -> the ticks that passed (read from the game)."""
    t0 = scene_tick(s)
    r = raw(s, "rimworld/step_game_ticks", ticks=ticks)
    return scene_tick(s) - t0, r


def scene_tick(s):
    st = raw(s, "rimworld/get_game_info")
    return int(st.get("ticksGame") or (st.get("state") or {}).get("tick") or 0)


def colonists(s):
    r = raw(s, "jawa/pawn_census", faction="player")
    return [p for p in (r.get("pawns") or r.get("rows") or []) if isinstance(p, dict)]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default="ArchSmall")
    ap.add_argument("--log")
    ap.add_argument("--idle-ticks", type=int, default=IDLE_TICKS, help="R2's idle span; below 60000 R2 is not decided (a debugging run)")
    a = ap.parse_args(argv)
    out, rows = [], []

    def say(x):
        print(x, flush=True)
        out.append(x)

    saves = {k: "RM_Stage_%s_%s" % (a.game, k) for k in ("settlement", "pocket")}
    made = {}
    for kind in ("pocket", "settlement"):          # the settlement stage is made last: the game is left on it
        rc, text, wall = wsl_make(a.game, "make", "--kind", kind, "--save", saves[kind])
        say("make %s: exit %s, %.1f s wall\n  %s" % (kind, rc, wall, "\n  ".join(ln for ln in text.splitlines() if not ln.startswith("ArchSmall: held"))))
        m = re.search(r"MADE %s stage .* make ([\d.]+) s, total ([\d.]+) s" % kind, text)
        made[kind] = (rc, m, re.search(r"emptied: .* (\d+) pawn\(s\) left", text))
        if rc != 0 or not m:
            say("NO VERDICT: the %s stage was not made" % kind)
            return 2

    # R1 + R5 (make side)
    bad = None
    for kind, (_rc, _m, left) in made.items():
        if not left or left.group(1) != "0":
            bad = "%s: the make did not read zero pawns after the empty" % kind
    r1_detail = []

    # R2: an idle day on the settlement stage; the green room keeps its colony; the stage stays empty
    r2 = None
    with open_session(a.game, saves["settlement"], calm="standard") as s:
        ms = maps(s)
        stage_id = next((m["mapId"] for m in ms if raw(s, "jawa/map_info").get("mapId") == m["mapId"]), None)
        green_id = next((m["mapId"] for m in ms if m["mapId"] != stage_id), None)
        r1_detail.append("after load: stage map %s holds %d pawn(s)" % (stage_id, len(raw(s, "jawa/list_pawns").get("pawns") or [])))
        if raw(s, "jawa/list_pawns").get("pawns"):
            bad = bad or "the loaded stage holds pawns: %s" % raw(s, "jawa/list_pawns").get("pawns")[:3]
        passed, step = idle(s, a.idle_ticks)
        after = raw(s, "jawa/list_pawns").get("pawns") or []
        r1_detail.append("after %d idle ticks: %d pawn(s) on the stage%s" % (passed, len(after), (": %s" % [p.get("kind") for p in after[:5]]) if after else ""))
        if after:
            bad = bad or "the idle stage gained %d pawn(s): %s" % (len(after), [(p.get("id"), p.get("kind")) for p in after[:5]])
        switch(s, green_id)
        col = [p for p in colonists(s) if p.get("isColonist")]
        hl = [p for p in raw(s, "jawa/list_pawns", faction="player", includeHealth=True).get("pawns") or [] if p.get("intelligence") == "Humanlike"]
        starving = [p.get("id") for p in hl if '"Malnutrition"' in json.dumps(p) or "'Malnutrition'" in str(p)]
        dead = [p.get("id") for p in hl if p.get("dead") is True]
        food = [(p.get("id"), (p.get("needs") or {}).get("food")) for p in col]
        switch(s, stage_id)
        if a.idle_ticks < IDLE_TICKS:
            r2 = "NOT DECIDED: a debugging run idled %d ticks, not %d" % (passed, IDLE_TICKS)
        elif passed < IDLE_TICKS:
            r2 = "only %d of %d ticks passed: %s" % (passed, IDLE_TICKS, str(step)[:200])
        elif not col or len(hl) < len(col):
            r2 = "the green room's colonists could not be read: census %d, list %d" % (len(col), len(hl))
        elif starving or dead or any(f is None or float(f) <= 0.0 for _i, f in food):
            r2 = "after %d ticks: dead %s, malnourished %s, food %s" % (passed, dead, starving, food)
        r2_detail = "%d ticks passed; %d colonist(s) on green room map %s, food %s, none malnourished" % (passed, len(col), green_id, food)
    rows.append(("R1 the stage holds zero pawns after make, and an idle day", bad, "; ".join(r1_detail)))
    rows.append(("R2 the green room's colonists are alive and fed after 60,000 ticks", r2, r2_detail))

    # R6: a wild animal on the stage is a breach, on the receipt of s.stage and of the close
    with open_session(a.game, saves["settlement"]) as s:
        mi = raw(s, "jawa/map_info")
        sx, sz = int(mi["sizeX"]), int(mi["sizeZ"])
        raw(s, "jawa/spawn_pawn", kindDef="Muffalo", x=sx - 8, z=sz - 8, faction="none", count=1)
        cast = s.stage(cast={"stander": dict(kind="Colonist", at=(4, 4))}, station=dict(size=(12, 12), margin=4))
        breach = [d for d in cast.receipt.did if d.startswith("BREACH")]
    closing = s.closed_report.did
    r6 = None
    if not breach or "Muffalo" not in breach[0]:
        r6 = "s.stage named no breach for the Muffalo: %s" % cast.receipt.did
    elif not any("BREACH" in x and "Muffalo" in x for x in closing):
        r6 = "the close did not name the breach: %s" % closing
    rows.append(("R6 a wild animal on the stage is a breach", r6, "%s; close: %s" % (breach[0] if breach else "", [x for x in closing if "station" in x or "BREACH" in x])))

    # R3: a raid at a settlement stage with cast defenders
    name3 = "R3 a raid at a settlement stage with cast defenders spawns raiders at an edge with an assault duty"
    with open_session(a.game, saves["settlement"]) as s:
        cast = s.stage(cast={"defenders": dict(kind="Colonist", at=[(4, 4), (6, 4), (8, 4)])},
                       station=dict(size=(12, 12), margin=4, edge=30, incident=True))
        try:
            fire = fire_raid(s)
        except Paused as e:
            fire = {"paused": str(e)}
        if "paused" in fire:
            rows.append((name3, "PAUSED", fire["paused"]))
        else:
            idle(s, 60)
            hostile = raw(s, "jawa/pawn_census", faction="hostile")
            hp = [p for p in (hostile.get("pawns") or hostile.get("rows") or []) if isinstance(p, dict)]
            lp = {p.get("id"): p for p in (raw(s, "jawa/list_pawns", faction="hostile").get("pawns") or [])}

            def at_edge(p):
                q = lp.get(p.get("id") or p.get("pawn"), {})
                c = scene.names._cell(q.get("position") or q.get("cell"))
                return c is not None and min(c[0], c[1], sx - 1 - c[0], sz - 1 - c[1]) <= EDGE_CELLS
            edge = [p for p in hp if at_edge(p)]
            assault = [p for p in hp if "assault" in str(p.get("lord") or p.get("duty") or "").lower()]
            r3 = None
            if fire.get("fired") is not True:
                r3 = "the raid did not fire: %s" % str(fire)[:300]
            elif not hp:
                r3 = "fired, and no hostile pawn is on the stage: %s" % str(fire)[:200]
            elif len(edge) != len(hp) or len(assault) != len(hp):
                r3 = "%d raider(s): %d at an edge, %d with an assault duty: %s" % (len(hp), len(edge), len(assault),
                                                                                   [(p.get("id"), p.get("lord"), p.get("duty")) for p in hp[:4]])
            rows.append((name3, r3, "%d raider(s), all within %d cells of an edge, lords %s; defenders %s" % (
                len(hp), EDGE_CELLS, sorted({str(p.get("lord"))[:40] for p in hp}), [m.id for m in cast.defenders])))

    # R4: the same raid at a stage with no free colonist
    name4 = "R4 a raid at a stage with no free colonist is reported called, not fired"
    with open_session(a.game, saves["settlement"]) as s:
        j0 = raw(s, "jawa/incident_journal", limit=1)
        seq0 = max([int(r.get("aseq") or 0) for r in j0.get("rows") or []] or [-1])
        try:
            fire = fire_raid(s)
        except Paused as e:
            fire = {"paused": str(e)}
        if "paused" in fire:
            rows.append((name4, "PAUSED", fire["paused"]))
        else:
            idle(s, 60)
            hostile = raw(s, "jawa/list_pawns", faction="hostile").get("pawns") or []
            jr = [r for r in raw(s, "jawa/incident_journal", sinceSeq=seq0).get("rows") or [] if "Raid" in str(r.get("def"))]
            r4 = None
            if not jr:
                r4 = "the journal has no row of the raid call: fire %s" % str(fire)[:200]
            elif hostile:
                r4 = "the raid spawned %d hostile(s) on a stage with no colonist" % len(hostile)
            rows.append((name4, r4, "fire_incident fired=%s; journal row %s; %d hostile(s) on the stage" % (
                fire.get("fired"), {k: jr[-1].get(k) for k in ("def", "returned", "outerBodyRan", "workerEntered", "outcome")} if jr else None,
                len(hostile))))


    # R5: the make time of each kind
    rc, text, wall = wsl_make(a.game, "register", "--save", "RM_Stage_%s_colony_probe" % a.game)
    times = {k: float(m.group(1)) for k, (_rc, m, _l) in made.items()}
    r5 = None if rc == 0 and "REGISTERED colony" in text else "register failed: exit %s %s" % (rc, text[-300:])
    rows.append(("R5 the make time of each map kind is printed", r5,
                 "settlement %.1f s, pocket %.1f s (the map's generation; the whole make with the empty: %s); colony: no map is made, "
                 "the walk save is registered (%.1f s wall, with the lock)" % (
                     times["settlement"], times["pocket"], {k: m.group(2) + " s" for k, (_rc, m, _l) in made.items()}, wall)))

    fails = paused = 0
    for name, bad, info in rows:
        paused += bad == "PAUSED"
        fails += bad is not None and bad != "PAUSED"
        say("%s %s: %s" % ("PASS" if bad is None else ("PAUSED" if bad == "PAUSED" else "FAIL"), name, info if bad in (None, "PAUSED") else bad))
    say("prove_stage_map: %d of %d rows held, %d failed, %d paused (raid_pause.py)" % (len(rows) - fails - paused, len(rows), fails, paused))
    if a.log:
        with open(a.log, "w", encoding="utf-8") as f:
            f.write("\n".join(out) + "\n")
    return 1 if fails else (3 if paused else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
