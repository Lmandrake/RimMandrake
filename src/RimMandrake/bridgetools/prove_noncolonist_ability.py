"""
prove_noncolonist_ability.py -- the FUNCTIONAL proof for BRIDGE_SELECT_NONCOLONIST_PAWN_1,
plus a live re-test of BRIDGE_MAP_DROP_SERIALIZATION_LOOP_1.

The three tools (jawa/select_things, jawa/pawn_use_ability, jawa/pawn_use_verb) were
deployed and confirmed present in the live tool list on 2026-09-21. Appearing in a tool
list is NOT the same as "neither refusing on faction", which is what the item's spec
actually claims. This exercises that claim against a real wild, faction-less pawn.

Run under python.exe (the bridge binds Windows loopback), on the beastmechanics tier:
    python.exe src/RimMandrake/bridgetools/prove_noncolonist_ability.py

Evidence bar, from the item:
  1. select_things on a wild RSW_Voltmaw -> selectedCount == 1, the row names the voltmaw.
  2. pawn_use_ability cast RSW_VoltmawPlasmaVolley at a colonist, waitTicks=600 ->
     readBack.lastCastTickAdvanced == true AND readBack.onCooldown == true.
     success:true is NOT evidence and is not accepted here.
  3. RSW_CindermiteFuelSpew at an x/z cell -> Filth_Fuel present afterwards.
  4. A deliberate out-of-range mode='verb' cast -> refusedBy names the real predicate.
  5. jawa/map_drop returns a parsed row naming the removed map instead of throwing.
"""
import sys, json, time

sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb  # noqa: E402

RESULTS = []


def record(step, ok, detail):
    RESULTS.append((step, ok, detail))
    print(("  PASS  " if ok else "  FAIL  ") + step + " :: " + detail, flush=True)


def main():
    host, port, token = rb.resolve_endpoint()
    S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
    S.connect()

    def call(tool, **params):
        r = S.call(tool, params) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:
                pass
        return r

    print("starting debug game...", flush=True)
    call("rimworld/start_debug_game_ready", timeoutMs=280000,
         readiness="mapData", pauseIfNeeded=True)
    state = None
    for _ in range(180):
        st = call("rimworld/get_ui_state")
        state = st.get("programState")
        if state == "Playing":
            break
        time.sleep(1)
    print("programState = %s" % state, flush=True)
    if state != "Playing":
        record("game reaches Playing", False, "programState=%r" % state)
        return summarize()

    # ---------------------------------------------------------------- spawns
    volt = call("jawa/spawn_pawn", kindDef="RSW_Voltmaw", x=100, z=100,
                faction="none", count=1)
    cind = call("jawa/spawn_pawn", kindDef="RSW_Cindermite", x=120, z=120,
                faction="none", count=1)
    colo = call("jawa/spawn_pawn", kindDef="Colonist", x=110, z=100,
                faction="player", count=1)
    print("spawn voltmaw    : %s" % json.dumps(volt)[:400], flush=True)
    print("spawn cindermite : %s" % json.dumps(cind)[:400], flush=True)
    print("spawn colonist   : %s" % json.dumps(colo)[:400], flush=True)

    def first_id(resp):
        for key in ("pawns", "spawned", "results"):
            rows = resp.get(key)
            if isinstance(rows, list) and rows:
                row = rows[0]
                if isinstance(row, dict):
                    for k in ("id", "thingId", "thingID"):
                        if row.get(k):
                            return row[k]
        for k in ("id", "thingId", "thingID"):
            if resp.get(k):
                return resp[k]
        return None

    volt_id, cind_id, colo_id = first_id(volt), first_id(cind), first_id(colo)
    print("ids: voltmaw=%s cindermite=%s colonist=%s" % (volt_id, cind_id, colo_id),
          flush=True)
    if not volt_id or not colo_id:
        record("spawn wild voltmaw + colonist", False,
               "could not read ids back out of jawa/spawn_pawn")
        return summarize()

    # ------------------------------------------------- 1. select a wild pawn
    sel = call("jawa/select_things", ids=volt_id, action="select")
    rows = sel.get("selected") or []
    names = json.dumps(rows)[:300]
    ok1 = (sel.get("selectedCount") == 1
           and any("Voltmaw" in json.dumps(r) for r in rows))
    record("1. select_things on a wild, faction-less RSW_Voltmaw",
           ok1, "selectedCount=%r selected=%s" % (sel.get("selectedCount"), names))

    # ----------------------------------- 1b. grant_ability on a tracker-less animal
    # Done BEFORE any tick, so CompInnateAbility has not run and the voltmaw genuinely
    # has no Pawn_AbilityTracker. jawa/grant_ability used to REFUSE that outright while
    # jawa/pawn_use_ability's refusal told the caller "jawa/grant_ability creates it" -
    # one of the two was false, and it was the tool. It now creates the tracker.
    pre = call("jawa/grant_ability", pawn=volt_id, ability="RSW_VoltmawPlasmaVolley")
    print("grant_ability (pre-tick): %s" % json.dumps(pre)[:300], flush=True)
    record("1b. grant_ability creates the Pawn_AbilityTracker an animal lacks",
           bool(pre.get("success")) and bool(pre.get("trackerCreated")),
           "success=%r trackerCreated=%r alreadyHad=%r abilityCountAfter=%r message=%r"
           % (pre.get("success"), pre.get("trackerCreated"), pre.get("alreadyHad"),
              pre.get("abilityCountAfter"), pre.get("message")))

    # The innate ability is granted by CompInnateAbility on CompTickRare (every 250
    # ticks), and that comp is ALSO what creates the Pawn_AbilityTracker an animal
    # does not otherwise have. A paused game never runs it, so step the clock first.
    step = call("rimworld/step_game_ticks", ticks=600, timeoutMs=120000)
    print("stepped ticks: %s" % json.dumps(step)[:200], flush=True)

    # ------------------------------------------- 2. cast a named ability
    listed = call("jawa/pawn_use_ability", pawn=volt_id, action="list")
    has_volley = "RSW_VoltmawPlasmaVolley" in json.dumps(listed)
    print("abilities: %s" % json.dumps(listed)[:600], flush=True)
    if not has_volley:
        g = call("jawa/grant_ability", pawn=volt_id,
                 ability="RSW_VoltmawPlasmaVolley")
        print("grant_ability: %s" % json.dumps(g)[:300], flush=True)

    # ⚠️ THREE THINGS MAKE A SINGLE CAST A BAD MEASUREMENT HERE, all MEASURED live
    # 2026-09-21 on this tier:
    #
    #   1. THE ANIMAL'S OWN AI. A wild, undrafted animal re-evaluates its think tree
    #      and can replace the ordered ability job with GotoWander before the warmup
    #      completes; readBack then shows currentJob=GotoWander, jobIsThisAbility=false
    #      and lastCastTick unmoved. That is the ANIMAL dropping the job, not the tool
    #      refusing, and it is intermittent.
    #   2. IT WANDERS OUT OF RANGE. A target placed at spawn time reads CanHitTarget
    #      false a few hundred ticks later. So a FRESH target is spawned 6 cells away
    #      immediately before each attempt (minRange is 2, range 20).
    #   3. THE WINDOW IS NARROW. At waitTicks<=240 the job was still 'CastAbilityOnThing'
    #      and nothing had fired; at waitTicks=300 the readBack already showed
    #      lastCastTickAdvanced=true with cooldownTicksRemaining=0 - the cooldown had
    #      come and gone. So binary-search the wait instead of guessing one number:
    #        not fired yet            -> wait LONGER
    #        fired but cooldown over  -> wait SHORTER
    #
    # The bar is unchanged and is NOT success:true - it is lastCastTickAdvanced AND
    # onCooldown together, read back off the live Ability after the wait.
    cast, rbk, ok2 = {}, {}, False
    lo, hi = 245, 700
    for _ in range(10):
        wait = (lo + hi) // 2
        where = call("jawa/pawn_use_ability", pawn=volt_id, action="list")
        vpos = (((where.get("result") or {}).get("pawn") or {}).get("position")
                or {"x": 100, "z": 100})
        tgt = call("jawa/spawn_pawn", kindDef="Colonist",
                   x=vpos["x"] + 6, z=vpos["z"], faction="player", count=1)
        tgt_id = first_id(tgt) or colo_id
        cast = call("jawa/pawn_use_ability", pawn=volt_id, action="cast",
                    ability="RSW_VoltmawPlasmaVolley", targetId=tgt_id,
                    mode="job", resetCooldown=True, waitTicks=wait,
                    timeoutSeconds=180, unpause=True)
        rbk = cast.get("readBack") or {}
        fired = bool(rbk.get("lastCastTickAdvanced"))
        ok2 = fired and bool(rbk.get("onCooldown"))
        print("cast volley waitTicks=%d -> lastCastTickAdvanced=%r onCooldown=%r "
              "cooldownTicksRemaining=%r currentJob=%r refusedBy=%r"
              % (wait, fired, rbk.get("onCooldown"),
                 rbk.get("cooldownTicksRemaining"), rbk.get("currentJob"),
                 cast.get("refusedBy")), flush=True)
        if ok2:
            break
        if fired:
            hi = max(lo, wait - 15)
        else:
            lo = min(hi, wait + 15)
        if lo >= hi:
            lo, hi = 245, 700   # AI dropped the job somewhere; re-widen and retry
    record("2. RSW_VoltmawPlasmaVolley fired by the wild voltmaw",
           ok2,
           "accepted=%r ticksElapsed=%r lastCastTickAdvanced=%r onCooldown=%r "
           "cooldownTicksRemaining=%r refusedBy=%r"
           % (cast.get("accepted"), cast.get("ticksElapsed"),
              rbk.get("lastCastTickAdvanced"), rbk.get("onCooldown"),
              rbk.get("cooldownTicksRemaining"), cast.get("refusedBy")))

    # ------------------------------ 3. cindermite fuel spew at a cell -> Filth_Fuel
    # ⚠️ AIM RELATIVE TO WHERE IT IS STANDING. A wild cindermite wanders, so a fixed
    # target cell chosen at spawn time can be out of range or behind a tree by the
    # time the cast is made - which is exactly what canHitTarget=false reported on
    # the first run. Read its position back, then aim 8 cells away (range is 12.9).
    ok3, detail3 = False, "cindermite did not spawn"
    if cind_id:
        def fuel_count():
            r = call("jawa/list_things", defName="Filth_Fuel", limit=400)
            n = r.get("countMatched")
            return len(r.get("things") or []) if n is None else n

        n_before = fuel_count()
        n_after = n_before
        spew = {}
        for mode, dx, dz in (("job", 8, 0), ("verb", 8, 0), ("verb", 0, 8),
                             ("verb", -8, 0)):
            where = call("jawa/pawn_use_ability", pawn=cind_id, action="list")
            pos = (((where.get("result") or {}).get("pawn") or {}).get("position")
                   or {"x": 120, "z": 120})
            tx, tz = pos["x"] + dx, pos["z"] + dz
            spew = call("jawa/pawn_use_ability", pawn=cind_id, action="cast",
                        ability="RSW_CindermiteFuelSpew", x=tx, z=tz,
                        mode=mode, resetCooldown=True, waitTicks=300,
                        timeoutSeconds=180, unpause=True)
            print("cast fuel spew mode=%s at (%d,%d) from (%d,%d): %s"
                  % (mode, tx, tz, pos["x"], pos["z"], json.dumps(spew)[:700]),
                  flush=True)
            n_after = fuel_count()
            if n_after > n_before:
                break
        ok3 = n_after > n_before
        detail3 = ("Filth_Fuel %r -> %r ; accepted=%r refusedBy=%r"
                   % (n_before, n_after, spew.get("accepted"), spew.get("refusedBy")))
    record("3. RSW_CindermiteFuelSpew lays Filth_Fuel in a cone", ok3, detail3)

    # ------------------------------------ 4. a deliberate out-of-range refusal
    far = call("jawa/pawn_use_ability", pawn=volt_id, action="cast",
               ability="RSW_VoltmawPlasmaVolley", x=100, z=180,
               mode="verb", resetCooldown=True, waitTicks=0)
    print("out-of-range verb cast: %s" % json.dumps(far)[:700], flush=True)
    refused = far.get("refusedBy") or ""
    ok4 = ("CanHitTarget" in refused) and not far.get("accepted")
    record("4. an out-of-range mode='verb' cast names the predicate that refused",
           ok4, "accepted=%r refusedBy=%r" % (far.get("accepted"), refused))

    # ------------------------ 5. the map_drop serialization fix, on this throwaway map
    # ⚠️ GATED. Dropping the map leaves the game Playing with zero maps, and
    # rimworld/start_debug_game_ready will NOT build a new one because a game already
    # exists - so the next run of this script spawns nothing until RimWorld is
    # relaunched. Pass --drop-map only on the run where you want that.
    if "--drop-map" not in sys.argv:
        print("  SKIP  5. jawa/map_drop - not run. Pass --drop-map to exercise it; "
              "it destroys the map and forces a relaunch before the next run.",
              flush=True)
        return summarize()

    before = call("rimbridge/get_bridge_status")
    drop = call("jawa/map_drop", notifyPlayer=False)
    print("map_drop: %s" % json.dumps(drop)[:700], flush=True)
    rm = drop.get("removedMap") or {}
    ok5 = (drop.get("success") is True
           and isinstance(rm.get("tile"), int)
           and drop.get("mapCountAfter") == (drop.get("mapCountBefore") or 0) - 1)
    record("5. jawa/map_drop returns a parsed row instead of throwing",
           ok5,
           "mapCountBefore=%r mapCountAfter=%r removedMap=%s (status before: mapCount=%r)"
           % (drop.get("mapCountBefore"), drop.get("mapCountAfter"),
              json.dumps(rm)[:260], before.get("mapCount")))

    return summarize()


def summarize():
    print("\n================ SUMMARY ================", flush=True)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for step, ok, detail in RESULTS:
        print(("PASS " if ok else "FAIL ") + step, flush=True)
    print("%d/%d" % (passed, len(RESULTS)), flush=True)
    return 0 if passed == len(RESULTS) and RESULTS else 1


if __name__ == "__main__":
    sys.exit(main())
