r"""prove_venomvine_flyer.py - VENOMVINE_PATHCOST_AND_FLYER_1, the flyer half.

THE QUESTION. MapComponent_ContactVenom.Sample skips a pawn when pawn.Flying,
copied from vanilla Building_Trap.Tick. That line had never been observed doing
anything, because nothing on the bridge could READ Pawn.Flying, let alone set
it. jawa/pawn_flight now does both.

THE DESIGN, and why it is not the observational run that already failed.
The earlier attempt put 20 geese and 40 ground birds in a 100%-vine pen for
7,220 ticks and got identical scratch counts. That null could not be attributed:
with Flying unreadable there was no way to tell "the skip never fires" from "the
geese never left the ground". This is a WITHIN-SUBJECT design instead, and it
turns on one fact read from the component's source: FIRST contact scratches
IMMEDIATELY (index < 0 -> Scratch(pawn, vine) on that same sample pass), and
Sample runs every 15 ticks. So the whole measurement fits in a window of a
couple of hundred ticks, and the outcome per pawn is BINARY - scratched on first
contact, or not sampled at all.

    window 1   geese held FLYING, maintained   ->  expect 0 scratched
               turkeys untouched on the same vines, same window
                                               ->  expect all scratched
    window 2   the SAME geese written GROUNDED ->  expect all scratched

Window 2 is the control that the failed run could not have: the identical pawns,
on the identical cells, differing only in Pawn.Flying.

    window 3   hares (MaxFlightTime 0, so they CANNOT fly) held FLYING
                                               ->  expect 0 scratched
    window 4   the same hares written GROUNDED ->  expect all scratched

Windows 3-4 are what rule out species. A hare cannot be launched by the engine
at all, so if forcing its flightState alone exempts it, the skip is keyed on
Pawn.Flying and on nothing else.

⚠️ SIZE THE WINDOW SMALL. victimSeverityScalingByInvBodySize makes a solid stand
lethal to small animals within a few in-game hours; a 57,000-tick attempt killed
all 60 test animals and returned nothing. These windows are ~200 ticks.
"""
import json
import sys
import time

sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb  # noqa: E402

# The arena. 30x30 of solid vine, so nobody in it can stand off a vine and
# nobody can wander out of it inside a 200-tick window.
AX, AZ, AW, AH = 30, 110, 30, 30
CENTRE_GOOSE = (38, 122)
CENTRE_TURKEY = (46, 122)
CENTRE_HARE = (42, 130)
N = 15
WINDOW = 200            # game ticks per arm. Sample runs every 15.
VENOM_HEDIFF = "RM_VenomvineVenom"

LOG = []


def say(msg):
    print(msg, flush=True)
    LOG.append(msg)


S = None


def call(tool, **params):
    r = S.call(tool, params) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r


def health_snapshot():
    """Per-pawn hediff picture over the arena: scratch-type injuries and the
    venom hediff's severity. Read from jawa/list_pawns includeHealth, which is
    the only route to a live hediff list without saving the game.

    🔴 THE HEDIFF LIST IS AT row['health']['hediffs'], NOT row['hediffs'].
    Reading the wrong key returns [] for every pawn and so reports a clean,
    confident ZERO for every arm - which is exactly what the first run of this
    script did, making a WORKING venom stand look inert and nearly producing a
    false 'the mechanism is broken' finding. Never read a per-pawn health field
    without first confirming a pawn that IS damaged reads as damaged."""
    r = call("jawa/list_pawns",
             rect="%d,%d,%d,%d" % (AX, AZ, AW, AH),
             includeHealth=True, limit=500)
    out = {}
    for p in (r.get("pawns") or []):
        hediffs = ((p.get("health") or {}).get("hediffs")) or []
        injuries = 0
        venom = 0.0
        for h in hediffs:
            d = (h.get("def") or h.get("defName") or "")
            if d == VENOM_HEDIFF:
                venom += float(h.get("severity") or 0.0)
            elif d in ("Scratch", "Cut", "Bite"):
                injuries += 1
        out[p.get("id") or p.get("thingId")] = {
            "kind": p.get("kind") or p.get("kindDef"),
            "injuries": injuries,
            "venom": round(venom, 4),
            "dead": bool(p.get("dead")),
            "x": p.get("x"), "z": p.get("z"),
            "hediffDefs": sorted({(h.get("def") or h.get("defName") or "?") for h in hediffs}),
        }
    return out


def arm(label, kinds, before, after):
    """Report one arm: how many pawns of these kinds gained any venom/injury."""
    rows = []
    for pid, a in after.items():
        if a["kind"] not in kinds:
            continue
        b = before.get(pid, {"injuries": 0, "venom": 0.0})
        gained = (a["venom"] - b["venom"]) > 1e-6 or (a["injuries"] - b["injuries"]) > 0
        rows.append((pid, gained, a))
    n = len(rows)
    hit = sum(1 for _, g, _ in rows if g)
    inside = sum(1 for _, _, a in rows
                 if AX <= (a["x"] or -1) < AX + AW and AZ <= (a["z"] or -1) < AZ + AH)
    dead = sum(1 for _, _, a in rows if a["dead"])
    say("  %-34s %2d/%2d pawns newly envenomed   (in arena %d/%d, dead %d)"
        % (label, hit, n, inside, n, dead))
    return hit, n, inside


def main():
    global S
    host, port, token = rb.resolve_endpoint()
    S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
    S.connect()

    say("=== VENOMVINE_PATHCOST_AND_FLYER_1 :: flyer exemption ===")

    call("rimworld/start_debug_game_ready", timeoutMs=280000,
         readiness="mapData", pauseIfNeeded=True)
    for _ in range(120):
        st = call("rimworld/get_ui_state")
        if st.get("programState") == "Playing":
            break
        time.sleep(1)
    say("programState: %s" % call("rimworld/get_ui_state").get("programState"))
    call("rimworld/set_time_speed", speed="Paused")

    # ---------------------------------------------------------------- arena
    rect = "%d,%d,%d,%d" % (AX, AZ, AW, AH)
    # 🔴 CLEAR THE WHOLE MAP OF THE TEST SPECIES FIRST. pawn_flight selects by
    # KIND across the map, so a goose left over from an earlier attempt - out
    # of the arena, already scratched, wandering - would be held airborne and
    # counted as if it were part of this run.
    d = call("jawa/destroy_bulk", filter="factionlessAnimals", dryRun=False)
    say("destroy_bulk factionlessAnimals -> %s" % (d.get("destroyed", d.get("count", d.get("success")))))

    c = call("jawa/clear_area", rect=rect, dryRun=False)
    say("clear_area %s -> destroyed %d things"
        % (rect, len(c.get("destroyed") or []) if isinstance(c.get("destroyed"), list)
           else c.get("destroyed", -1)))

    ops = ";".join("RM_Venomvine:%d,%d" % (x, z)
                   for x in range(AX, AX + AW) for z in range(AZ, AZ + AH))
    sp = call("jawa/spawn_batch", ops=ops)
    say("spawn_batch RM_Venomvine -> spawned=%s failed=%s"
        % (sp.get("spawned", sp.get("spawnedCount")), sp.get("failed", sp.get("failedCount"))))

    for kind, (x, z) in (("Goose", CENTRE_GOOSE), ("Turkey", CENTRE_TURKEY)):
        r = call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction="none", count=N)
        say("spawn_pawn %-7s x%d -> success=%s" % (kind, N, r.get("success")))

    # Baseline BEFORE anything ticks. The game is paused, so nothing has been
    # sampled yet and this is a true zero point.
    base = health_snapshot()
    say("baseline pawns in arena: %d" % len(base))

    # --------------------------------------------------- window 1: geese fly
    pre = call("jawa/pawn_flight", action="hold", kind="Goose", maintainTicks=0)
    say("\nwindow 1 setup: hold Goose -> count=%s flyingAtEnd=%s"
        % (pre.get("count"), pre.get("flyingAtEnd")))
    for row in (pre.get("results") or [])[:3]:
        say("   %s changed=%s %s->%s refused=%s"
            % (row["label"], row["changed"], row["stateBefore"], row["stateAfter"],
               row["refusedReason"]))
    tk = call("jawa/pawn_flight", action="hold", kind="Turkey", maintainTicks=0)
    say("   (turkey canEverFly readings: %s)"
        % sorted({p["canEverFly"] for p in (tk.get("pawns") or [])}))
    # Put the turkeys straight back on the ground - they are the GROUND arm.
    call("jawa/pawn_flight", action="land", kind="Turkey")

    w1 = call("jawa/pawn_flight", action="hold", kind="Goose",
              maintainTicks=WINDOW, unpause=True, timeoutSeconds=120)
    say("window 1 ran: ticksElapsed=%s polls=%s reasserts=%s flyingLowWater=%s/%s "
        "flyingAtEnd=%s timedOut=%s speedRestored=%s"
        % (w1.get("ticksElapsed"), w1.get("polls"), w1.get("reasserts"),
           w1.get("flyingLowWater"), w1.get("count"), w1.get("flyingAtEnd"),
           w1.get("timedOut"), w1.get("speedRestored")))
    call("rimworld/set_time_speed", speed="Paused")
    after1 = health_snapshot()
    say("window 1 result (geese FLYING, turkeys GROUNDED, same vines, same ticks):")
    g1 = arm("Goose  [FLYING]", {"Goose"}, base, after1)
    t1 = arm("Turkey [grounded control]", {"Turkey"}, base, after1)

    # ------------------------------------------- window 2: the same geese land
    ld = call("jawa/pawn_flight", action="land", kind="Goose")
    say("\nwindow 2 setup: land Goose -> flyingAtEnd=%s" % ld.get("flyingAtEnd"))
    call("rimworld/step_game_ticks", ticks=WINDOW, timeoutMs=120000, pauseFirst=True)
    after2 = health_snapshot()
    say("window 2 result (the SAME geese, now GROUNDED, same cells):")
    g2 = arm("Goose  [grounded]", {"Goose"}, after1, after2)

    # ------------------------------ windows 3-4: a species that CANNOT ever fly
    call("rimworld/set_time_speed", speed="Paused")
    r = call("jawa/spawn_pawn", kindDef="Hare", x=CENTRE_HARE[0], z=CENTRE_HARE[1],
             faction="none", count=N)
    say("\nspawn_pawn Hare x%d -> success=%s" % (N, r.get("success")))
    base3 = health_snapshot()
    h0 = call("jawa/pawn_flight", action="report", kind="Hare")
    say("hare flight capability: canEverFly=%s maxFlightTimeStat=%s"
        % (sorted({p["canEverFly"] for p in (h0.get("pawns") or [])}),
           sorted({p["maxFlightTimeStat"] for p in (h0.get("pawns") or [])})))
    hs = call("jawa/pawn_flight", action="start", kind="Hare")
    say("hare via the ENGINE API (StartFlying): %s"
        % ((hs.get("results") or [{}])[0].get("refusedReason") or "accepted"))

    w3 = call("jawa/pawn_flight", action="hold", kind="Hare",
              maintainTicks=WINDOW, unpause=True, timeoutSeconds=120)
    say("window 3 ran: ticksElapsed=%s flyingLowWater=%s/%s flyingAtEnd=%s"
        % (w3.get("ticksElapsed"), w3.get("flyingLowWater"), w3.get("count"),
           w3.get("flyingAtEnd")))
    call("rimworld/set_time_speed", speed="Paused")
    after3 = health_snapshot()
    say("window 3 result (hares FORCED airborne despite MaxFlightTime 0):")
    h3 = arm("Hare   [FLYING, forced]", {"Hare"}, base3, after3)

    call("jawa/pawn_flight", action="land", kind="Hare")
    call("rimworld/step_game_ticks", ticks=WINDOW, timeoutMs=120000, pauseFirst=True)
    after4 = health_snapshot()
    say("window 4 result (the SAME hares, now GROUNDED):")
    h4 = arm("Hare   [grounded]", {"Hare"}, after3, after4)

    # -------------------------------------------------------------- verdict
    say("\n=== VERDICT ===")
    say("  flyers envenomed   : Goose %d/%d, Hare %d/%d" % (g1[0], g1[1], h3[0], h3[1]))
    say("  grounded envenomed : Goose %d/%d, Turkey %d/%d, Hare %d/%d"
        % (g2[0], g2[1], t1[0], t1[1], h4[0], h4[1]))
    clean = (w1.get("flyingLowWater") == w1.get("count")
             and w3.get("flyingLowWater") == w3.get("count"))
    say("  windows clean (every flyer airborne at every poll): %s" % clean)
    proven = (g1[0] == 0 and h3[0] == 0 and g2[0] == g2[1] and t1[0] == t1[1]
              and h4[0] == h4[1] and clean)
    say("  EXEMPTION OBSERVED: %s" % proven)

    with open(r"D:\Luke\dev\Rimworld\Transient\venomvine_flyer_run.txt", "w",
              encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
        f.write("\nraw after1=%s\n" % json.dumps(after1)[:4000])
    return 0 if proven else 1


if __name__ == "__main__":
    sys.exit(main())
