import sys, io, time, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
results = {}

def kill_pawn(rb, pid, tries=6, amount=1500):
    for attempt in range(tries):
        g = rb.call("jawa/pawn_get", {"pawn": pid})
        pawns = g.get("pawns", [])
        if not pawns:
            return {"dead": True, "why": "no longer resolvable (likely dead+decayed to corpse)", "attempts": attempt}
        dead = pawns[0].get("dead")
        if dead:
            return {"dead": True, "attempts": attempt}
        r = rb.call("jawa/damage", {"damageDef": "Bomb", "amount": amount, "thingId": pid, "allowColonists": True})
        print("  damage attempt", attempt, pid, r.get("success"), r.get("message"))
        if not r.get("success"):
            return {"dead": False, "attempts": attempt, "lastError": r.get("message")}
        time.sleep(0.3)
    g = rb.call("jawa/pawn_get", {"pawn": pid})
    pawns = g.get("pawns", [])
    dead = pawns[0].get("dead") if pawns else True
    return {"dead": dead, "attempts": tries}

with RimBridge(host, port, token) as rb:
    rb.call("jawa/clear_ui", {})

    # --- spawn subjects ---
    for i in range(3):
        r = rb.call("rimworld/execute_debug_action", {
            "path": "Actions\\Spawn Pawn...\\RSW_DW_KotORDroidColonist_ADMkI",
            "x": 120 + i, "z": 100})
        print("spawn kotorGood", i, r.get("success"), r.get("message"))
    time.sleep(1)

    for i in range(3):
        r = rb.call("rimworld/execute_debug_action", {
            "path": "Actions\\Spawn Pawn...\\RSW_DW_KotORDroidBad_ADMkI",
            "x": 130 + i, "z": 100})
        print("spawn kotorBad", i, r.get("success"), r.get("message"))
    time.sleep(1)

    for i in range(4):
        r = rb.call("rimworld/execute_debug_action", {
            "path": "Actions\\Spawn Pawn...\\RSW_DW_OuterRim_GNKDroid",
            "x": 140 + i, "z": 100})
        print("spawn gnk", i, r.get("success"), r.get("message"))
    time.sleep(1)

    lp = rb.call("jawa/list_pawns", {})
    all_pawns = lp.get("pawns", [])
    kg_ids = sorted([p["id"] for p in all_pawns if p.get("kind") == "RSW_DW_KotORDroidColonist_ADMkI"])
    kb_ids = sorted([p["id"] for p in all_pawns if p.get("kind") == "RSW_DW_KotORDroidBad_ADMkI"])
    gnk_ids = sorted([p["id"] for p in all_pawns if p.get("kind") == "RSW_DW_OuterRim_GNKDroid"])
    print("kg_ids", kg_ids)
    print("kb_ids", kb_ids)
    print("gnk_ids", gnk_ids)
    results["spawned"] = {"kg": kg_ids, "kb": kb_ids, "gnk": gnk_ids,
                           "expected": {"kg": 3, "kb": 3, "gnk": 4}}

    # set kg (colonist-typed KotOR droids) to player faction
    for pid in kg_ids:
        r = rb.call("jawa/set_pawn_faction", {"pawn": pid, "faction": "player"})
        print("set kg player", pid, r.get("success"), r.get("notes"))

    # --- check #1: PoweredDown lands and does not self-clear ---
    print("=== CHECK 1: PoweredDown persistence ===")
    before = {}
    for pid in kg_ids:
        r = rb.call("jawa/pawn_health", {"pawn": pid, "action": "add", "hediff": "RSW_DW_PoweredDown", "severity": 1.0})
        hs = [h for h in r.get("hediffs", []) if h["def"] == "RSW_DW_PoweredDown"]
        before[pid] = hs
        print("add PoweredDown", pid, r.get("success"), hs)
    r = rb.call("rimworld/step_game_ticks", {"ticks": 2500})
    print("step_game_ticks:", r.get("success"), r.get("completedTicks") if isinstance(r, dict) else None, r.get("status"))
    after = {}
    for pid in kg_ids:
        g = rb.call("jawa/pawn_get", {"pawn": pid})
        pawns = g.get("pawns", [])
        after[pid] = pawns[0] if pawns else None
    results["check1_poweredDown_persist"] = {"before": before, "after_raw": str(after)[:2500]}

    # --- check #2: reboot recipe state transition ---
    print("=== CHECK 2: reboot (state transition) ===")
    reboot_results = {}
    for pid in kg_ids:
        r1 = rb.call("jawa/pawn_health", {"pawn": pid, "action": "remove", "hediff": "RSW_DW_PoweredDown"})
        r2 = rb.call("jawa/pawn_need", {"pawn": pid, "need": "RSW_DW_Power", "action": "need", "level": 0.15})
        print("reboot", pid, "remove:", r1.get("success"), r1.get("didWhat"), "| power:", r2.get("success"))
        reboot_results[pid] = {"remove": r1.get("didWhat"), "power_set": r2.get("notes")}
    results["check2_reboot"] = reboot_results

    # --- bolt: install then remove ---
    print("=== CHECK: bolt install/remove ===")
    boltPawn = kg_ids[0]
    r = rb.call("jawa/pawn_health", {"pawn": boltPawn, "action": "add", "hediff": "RSW_DW_RestrainingBolt"})
    print("add bolt", r.get("success"), r.get("didWhat"))
    r = rb.call("jawa/pawn_health", {"pawn": boltPawn, "action": "add", "hediff": "RSW_DW_BoltResentment"})
    print("add resentment", r.get("success"), r.get("didWhat"), "hediffs now:", r.get("hediffs"))
    results["check_bolt_installed"] = r.get("hediffs")
    r = rb.call("jawa/pawn_health", {"pawn": boltPawn, "action": "remove", "hediff": "RSW_DW_RestrainingBolt"})
    print("remove bolt", r.get("success"), r.get("didWhat"), "hediffs now:", r.get("hediffs"))
    results["check_bolt_removed"] = r.get("hediffs")

    # --- wipe: on a hostile kotorBad pawn (traits + relations state, then faction flip) ---
    print("=== CHECK: wipe (faction flip, the recipe's own end effect) ===")
    wipePawn = kb_ids[1]
    g_before = rb.call("jawa/pawn_get", {"pawn": wipePawn})
    before_faction = g_before.get("pawns", [{}])[0].get("faction") if g_before.get("pawns") else None
    print("wipe target faction before:", before_faction)
    r = rb.call("jawa/set_pawn_faction", {"pawn": wipePawn, "faction": "player"})
    print("wipe faction flip", r.get("success"), r.get("before"), "->", r.get("after"))
    results["check_wipe_faction_flip"] = {"before": r.get("before"), "after": r.get("after")}

    # --- spike: down a hostile kotorBad pawn via Anesthetic, then faction flip
    #     (replicating JobDriver_DWDataSpike's job-level finish action, which fires
    #     only when Target.Downed||IsPrisoner AND the spike's faction key matches) ---
    print("=== CHECK: spike (downed precondition + faction flip) ===")
    spikePawn = kb_ids[2]
    r = rb.call("jawa/pawn_health", {"pawn": spikePawn, "action": "add", "hediff": "Anesthetic", "severity": 0.6})
    print("anesthetic (down)", r.get("success"), r.get("didWhat"))
    time.sleep(1)
    g_downed = rb.call("jawa/pawn_get", {"pawn": spikePawn})
    downed_flag = g_downed.get("pawns", [{}])[0].get("downed") if g_downed.get("pawns") else None
    print("spike target downed flag:", downed_flag)
    results["check_spike_downed_flag"] = downed_flag
    r = rb.call("jawa/set_pawn_faction", {"pawn": spikePawn, "faction": "player"})
    print("spike faction flip", r.get("success"), r.get("before"), "->", r.get("after"))
    results["check_spike_flip"] = {"before": r.get("before"), "after": r.get("after")}

    # --- kill -> corpse ---
    print("=== CHECK: kill -> corpse ===")
    killPawn = kb_ids[0]
    kr = kill_pawn(rb, killPawn)
    print("kill result:", kr)
    time.sleep(1)
    things = rb.call("jawa/list_things", {"group": "Corpse"})
    results["check_kill_corpse"] = {"kill": kr, "corpses": things.get("things") if isinstance(things, dict) else things}

    # --- GNK detonation: 100% vs 5% ---
    print("=== CHECK: GNK detonation 100% vs 5% ===")
    hot = gnk_ids[0:2]
    cold = gnk_ids[2:4]
    for pid in hot:
        r = rb.call("jawa/pawn_need", {"pawn": pid, "need": "RSW_DW_Power", "action": "need", "level": 1.0})
        print("set gnk power 1.0", pid, r.get("success"))
    for pid in cold:
        r = rb.call("jawa/pawn_need", {"pawn": pid, "need": "RSW_DW_Power", "action": "need", "level": 0.05})
        print("set gnk power 0.05", pid, r.get("success"))

    before_cells = rb.call("jawa/get_terrain_batch", {"rects": "128,90,20,20"})
    kill_log = {}
    for pid in hot + cold:
        kill_log[pid] = kill_pawn(rb, pid)
        print("gnk kill", pid, kill_log[pid])
    time.sleep(1)
    after_cells = rb.call("jawa/get_terrain_batch", {"rects": "128,90,20,20"})

    def scorched_count(batch):
        cells = batch.get("cells") or batch.get("terrain") or []
        n = 0
        for c in (cells if isinstance(cells, list) else []):
            td = str(c.get("terrain") or c.get("defName") or "").lower()
            if "burn" in td or "scorch" in td or "char" in td:
                n += 1
        return n, len(cells) if isinstance(cells, list) else 0

    b_n, b_tot = scorched_count(before_cells)
    a_n, a_tot = scorched_count(after_cells)
    results["gnk_kill_log"] = kill_log
    results["gnk_scorch_before"] = {"scorched": b_n, "total": b_tot}
    results["gnk_scorch_after"] = {"scorched": a_n, "total": a_tot}
    results["gnk_terrain_before_raw"] = str(before_cells)[:1500]
    results["gnk_terrain_after_raw"] = str(after_cells)[:1500]

    rb.call("rimworld/jump_camera_to_cell", {"x": 138, "z": 100})
    rb.call("jawa/clear_ui", {})
    ss = rb.call("rimworld/take_screenshot", {"name": "droidworks_a1_gnk_detonation_result"})
    print("screenshot:", ss)
    results["gnk_screenshot"] = ss

with open(r"D:\Luke\dev\Rimworld\Transient\droidworks_live_loop\results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)
print("DONE")
