#!/usr/bin/env python3
"""Live proof of three tools: the loaded-build receipt (jawa/running_mods loadedOf), the calm map (jawa/quiet_site calm |
reassert | read | release) and the first-exception tap (jawa/first_exception).

Pages: design/specs/2026-11-23-loaded-receipt, -calm-map, -first-exception-tap (boundary.md). Item
RIMMANDRAKE_BUILD_BRIDGE_RECEIPT_CALM_AND_TAP_EITHER_WAY. Every tool is seen green on a clean state and red on a planted
fault. Run under Windows python.exe on a TEST-profile game on a small mod list (never a campaign save, no flyer), after
build.py --gm --apply and a restart:

    python.exe prove_three_tools.py [--out DIR] [--only receipt,calm,tap]

--out: the receipt reply is written there as receipt.json, for `build_match.py loaded --mod M --receipt receipt.json`.
The rows that need a new map make their own quicktest map. The save it makes and loads is rm_proof_three_tools.
Exit 0 = every row PASS, 1 = a FAIL, 2 = UNMEASURED (no bridge, or a row that could not look)."""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

ROWS = []
S = [None]
SAVE = "rm_proof_three_tools"


def row(name, ok, detail):
    """ok True PASS, False FAIL, None UNMEASURED."""
    v = "PASS" if ok is True else ("FAIL" if ok is False else "UNMEASURED")
    ROWS.append((name, v))
    print("%-44s %-10s %s" % (name, v, str(detail)[:400]), flush=True)
    return ok is True


def connect():
    host, port, token = rb.resolve_endpoint()
    if not token:
        raise SystemExit("UNMEASURED: no bridge token")
    S[0] = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
    S[0].connect()


def call(tool, **p):
    try:
        r = S[0].call(tool, p, check=False) or {}
    except Exception as e:  # noqa: BLE001 - a refusal may arrive as a transport error; it is the reading
        return {"success": False, "_error": "%s: %s" % (type(e).__name__, e)}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except (ValueError, KeyError, IndexError, TypeError):
            pass
    return r if isinstance(r, dict) else {"_raw": r}


def playing(limit=240):
    from await_lifecycle import await_lifecycle
    return bool(await_lifecycle(call, "map_ready", deadline_s=limit))


def quicktest():
    """A NEW debug game. From a Playing game, start_debug_game_ready times out on the entry scene and the old map stays
    (measured on ArchSmall 2026-11-24), so go to the main menu first, and a failed start is no map."""
    if (call("jawa/companion_handshake").get("game") or {}).get("programState") != "Entry":
        call("rimworld/go_to_main_menu")
    r = call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
    return r.get("success") is not False and playing()


def step(n):
    return call("rimworld/step_game_ticks", ticks=n, pauseFirst=True)


def tick():
    return call("jawa/map_info").get("ticksGame")


def unhook(hid):
    """Plant: take our hooks off. -> None when Harmony itself says they are gone, else what it said (the plant did not take)."""
    r = call("jawa/first_exception", action="plant", kind="unhook", label=hid)
    h = call("jawa/static_call", type="HarmonyLib.Harmony", method="HasAnyPatches", args=hid)
    return None if str(h.get("result")).lower() == "false" else "unpatch: %s | has patches: %s" % (str(r)[:300], str(h)[:120])


def status(r, name):
    return next((c.get("status") for c in r.get("controls") or [] if c.get("name") == name), None)


def things(r, name):
    return next((c.get("things") for c in r.get("controls") or [] if c.get("name") == name), None)


# ---------------------------------------------------------------------------------------------------------- receipt
def receipt(out):
    r = call("jawa/running_mods", details=False, assembly="", loadedOf="ours")
    ld = r.get("loaded") or {}
    with open(os.path.join(out, "receipt.json"), "w", encoding="utf-8") as f:
        json.dump(r, f, indent=1)
    mods = ld.get("mods") or []
    row("receipt.answers", bool(mods) and bool(ld.get("gameKey")) and str(ld.get("listFingerprint", "")).startswith("sha256:")
        if r.get("success") else None,
        "game %s, %s mods running, %d of ours, pid %s, %s, companion %s" % (ld.get("gameKey"), ld.get("listCount"), len(mods), ld.get("pid"),
                                                                             ld.get("gameVersion"), (ld.get("companion") or {}).get("srcHash")))
    states = {}
    for m in mods:
        states.setdefault(m.get("state"), []).append(m.get("packageId"))
    asm = [a for m in mods for a in m.get("assemblies") or []]
    row("receipt.every_assembly_has_its_id", bool(asm) and all(a.get("mvid") and a.get("fileHoldsLoadedCode") is not None for a in asm),
        "%d assemblies; states %s" % (len(asm), {k: len(v) for k, v in states.items()}))
    row("receipt.clean_load_is_loaded", bool(mods) and not any(k not in ("LOADED", "NO_ASSEMBLY") for k in states), states.get("LOADED"))
    return next((m for m in mods if m.get("state") == "LOADED" and m.get("assemblies")), None)


def receipt_planted(m):
    """The wrong build: the DLL file is replaced on disk while the game runs, then put back."""
    if not m:
        return row("receipt.planted_wrong_build", None, "no loaded mod of ours with a DLL on this list")
    path, moved = m["assemblies"][0]["location"], m["assemblies"][0]["location"] + ".rm_proof_moved"
    try:
        os.rename(path, moved)
    except OSError as e:
        return row("receipt.planted_wrong_build", None, "Windows refused to move the loaded file: %s" % e)
    try:
        with open(moved, "rb") as f:
            raw = bytearray(f.read())
        import uuid
        at = bytes(raw).index(uuid.UUID(m["assemblies"][0]["mvid"]).bytes_le)
        raw[at] ^= 0xFF                         # another build has another id
        with open(path, "wb") as f:
            f.write(bytes(raw))
        r = call("jawa/running_mods", details=False, assembly="", loadedOf=m["packageId"])
        got = ((r.get("loaded") or {}).get("mods") or [{}])[0]
        row("receipt.planted_wrong_build", got.get("state") == "FILE_CHANGED", "%s: %s" % (got.get("state"), got.get("why")))
    finally:
        if os.path.exists(path):
            os.remove(path)
        os.rename(moved, path)
    r = call("jawa/running_mods", details=False, assembly="", loadedOf=m["packageId"])
    got = ((r.get("loaded") or {}).get("mods") or [{}])[0]
    row("receipt.put_back_is_loaded", got.get("state") == "LOADED", got.get("state"))
    r = call("jawa/running_mods", details=False, assembly="", loadedOf="mandrake.no.such.mod")
    row("receipt.absent_mod_is_named", (r.get("loaded") or {}).get("notRunning") == ["mandrake.no.such.mod"], (r.get("loaded") or {}).get("notRunning"))


# ------------------------------------------------------------------------------------------------------------- calm
def qs(action, **p):
    return call("jawa/quiet_site", action=action, **p)


def calm():
    if not quicktest():
        return row("calm.map", None, "no quicktest map reached Playing")
    r = qs("read")
    row("calm.read_before_is_not_calm", r.get("verdict") == "NOT_CALM" and r.get("calm") is False and status(r, "incident_gate") == "NOT_CALM"
        and status(r, "arrivals") == "COULD_NOT_READ", "%s | %s" % (r.get("verdict"), r.get("notCalm")))
    r = qs("reassert")
    row("calm.reassert_before_calm_is_refused", r.get("success") is False and "calm first" in str(r), str(r)[:120])
    r = qs("calm", clear=True, minutes=60, **{"except": "wether"})
    row("calm.unknown_except_is_refused", r.get("success") is False and "wether" in str(r), str(r)[:160])
    r = qs("calm", clear=True, minutes=60)
    if not row("calm.clean_map_reads_calm", r.get("success") is True and r.get("verdict") == "CALM" and len(r.get("controls") or []) == 16,
               "%s; %s; errors %s" % (r.get("verdict"), r.get("message"), r.get("errors"))):
        print(json.dumps(r, indent=1)[:6000])
    row("calm.not_covered_is_listed", bool(r.get("notCovered")), len(r.get("notCovered") or []))
    t0 = tick()
    step(2600)                                   # past two wild-animal checks (1,213) and two storyteller checks (1,000)
    r = qs("read")
    row("calm.holds_over_2600_ticks", r.get("verdict") == "CALM" and (tick() or 0) - (t0 or 0) >= 2500,
        "%s after %s ticks; breaches %s; %s" % (r.get("verdict"), (tick() or 0) - (t0 or 0), (r.get("breaches") or {}).get("counts"), r.get("message")))

    # an injected incident
    f = call("jawa/fire_incident", incidentDef="RaidEnemy", forced=True, points=200)
    r = qs("read")
    held = ((r.get("breaches") or {}).get("counts") or {}).get("incident_held", 0)
    row("calm.injected_raid_is_held_and_logged", f.get("fired") is not True and held >= 1 and status(r, "hostiles") == "CALM",
        "fired=%s held=%s row=%s" % (f.get("fired"), held, ((r.get("breaches") or {}).get("rows") or [{}])[-1]))
    q = call("jawa/incident_schedule", incidentDef="RaidEnemy", delayTicks=30, points=200)
    step(200)
    r = qs("read")
    row("calm.queued_raid_stays_in_the_queue", q.get("success") is True and status(r, "incident_queue") == "HELD" and "RaidEnemy" in str(r.get("controls"))
        and status(r, "hostiles") == "CALM", next((c.get("detail") for c in r.get("controls") or [] if c["name"] == "incident_queue"), None))
    call("jawa/incident_queue_clear")

    # drift, one thing at a time: read names it, reassert repairs it
    call("jawa/site_state", storyteller="on")
    r = qs("read")
    row("calm.storyteller_on_is_named", r.get("verdict") == "NOT_CALM" and [x.split(":")[0] for x in r.get("notCalm") or []] == ["storyteller"], r.get("notCalm"))
    r = qs("reassert")
    row("calm.reassert_repairs_storyteller", r.get("verdict") == "CALM" and [x.split(":")[0] for x in r.get("repaired") or []] == ["storyteller"], r.get("repaired"))
    call("jawa/weather_set", weather="Rain", lockWeather=True)
    step(1)
    r = qs("read")
    row("calm.planted_rain_is_named", status(r, "weather") == "NOT_CALM", things(r, "weather"))
    r = qs("reassert", clear=True)
    row("calm.reassert_repairs_weather", r.get("verdict") == "CALM", "%s %s" % (r.get("verdict"), r.get("repaired")))
    call("jawa/wild_spawner_block", action="release")
    r = qs("read")
    row("calm.released_wild_spawner_is_named", status(r, "wild_spawner") == "NOT_CALM", things(r, "wild_spawner"))
    row("calm.reassert_blocks_wild_again", qs("reassert").get("verdict") == "CALM", "reassert")
    mi = call("jawa/map_info")
    x, z = int(mi.get("sizeX", 250)) // 2, int(mi.get("sizeZ", 250)) // 2
    sp = call("jawa/spawn_pawn", kindDef="Cougar", x=x, z=z, faction="none", count=1)
    r = qs("read")
    row("calm.planted_predator_is_named", sp.get("success") is True and status(r, "predators") == "NOT_CALM" and "Cougar" in str(things(r, "predators")), things(r, "predators"))
    r = qs("reassert")
    row("calm.reassert_without_clear_removes_nothing", r.get("verdict") == "NOT_CALM" and r.get("success") is False and r.get("couldNotRepair") == ["predators"], r.get("couldNotRepair"))
    r = qs("reassert", clear=True)
    row("calm.reassert_clear_removes_it", r.get("verdict") == "CALM" and any("Cougar" in x for x in r.get("repaired") or []), r.get("repaired"))
    miss = unhook("mandrake.jawabench.calm")
    r = qs("read")
    row("calm.removed_gate_is_never_calm", None if miss else r.get("calm") is False and status(r, "incident_gate") == "NOT_CALM" and status(r, "arrivals") == "COULD_NOT_READ",
        miss or "%s | %s | %s" % (r.get("verdict"), r.get("notCalm"), r.get("notRead")))
    r = qs("reassert")
    row("calm.reassert_puts_the_gate_back", None if miss else r.get("verdict") == "CALM", "%s %s" % (r.get("repaired"), r.get("message")))

    # an allowed incident runs, and the map then names its raiders
    r = qs("calm", allowIncidents="raidenemy", minutes=60)
    f = call("jawa/fire_incident", incidentDef="RaidEnemy", forced=True, points=200)
    call("jawa/fire_incident", incidentDef="ManhunterPack", forced=True, points=200)
    for _ in range(12):                          # the arrival mode is the raid's own: walkers read at +60, drop pods later
        step(60)
        r = qs("read")
        if status(r, "hostiles") == "NOT_CALM":
            break
    row("calm.allowed_raid_runs_and_is_named", f.get("fired") is True and (status(r, "hostiles") == "NOT_CALM" or f.get("blockedByDialog")) and
        ((r.get("breaches") or {}).get("counts") or {}).get("incident_held", 0) == 1, "fired=%s hostiles=%s held=%s" % (
            f.get("fired"), (things(r, "hostiles") or [])[:2], (r.get("breaches") or {}).get("counts")))
    r = qs("calm", clear=True, minutes=60)
    row("calm.clear_after_a_raid", r.get("verdict") == "CALM", "%s %s" % (r.get("verdict"), r.get("message")))

    # release puts every value back
    r = qs("release")
    st = call("jawa/site_state")
    w = qs("read")
    row("calm.release_puts_back", r.get("released") is True and (st.get("storyteller") or {}).get("enabledAfter") is True and "forced weather ended" in str(r.get("restored")) and
        status(w, "weather") == "NOT_CALM" and status(w, "incident_gate") == "NOT_CALM" and status(w, "wild_spawner") == "NOT_CALM", r.get("restored"))
    row("calm.release_twice_says_nothing_to_release", qs("release").get("released") is False, "ok")

    # the lease ends by itself and puts the values back
    qs("calm", minutes=0.05)
    time.sleep(5)
    step(2)
    st = call("jawa/site_state")
    r = qs("read")
    row("calm.lease_end_puts_back", (st.get("storyteller") or {}).get("enabledAfter") is True and r.get("lastRelease") and status(r, "weather") == "NOT_CALM"
        and status(r, "incident_gate") == "NOT_CALM", "%s %s" % (r.get("lastRelease"), r.get("lastRestore")))

    # a load ends the calm; reassert sets it again
    r = qs("calm", clear=True, minutes=60)
    call("rimworld/save_game", saveName=SAVE)
    call("rimworld/load_game", saveName=SAVE, ignoreModCompatibility=True)
    time.sleep(5)
    if not playing():
        return row("calm.after_a_load", None, "the load did not reach Playing")
    r = qs("read")
    row("calm.a_load_ends_it_and_read_says_so", r.get("calm") is False and status(r, "incident_gate") == "NOT_CALM" and "new-game" in str(r.get("lastRelease")),
        "%s lastRelease=%s" % (r.get("verdict"), r.get("lastRelease")))
    r = qs("reassert", clear=True)
    row("calm.reassert_after_a_load", r.get("verdict") == "CALM", "%s %s" % (r.get("verdict"), r.get("message")))
    r = qs("release")
    row("calm.release_names_the_saved_weather", "still forced to Clear" in str(r.get("restored")), r.get("restored"))
    call("jawa/weather_set", unlock=True)


# -------------------------------------------------------------------------------------------------------------- tap
def fe(action, **p):
    return call("jawa/first_exception", action=action, **p)


def tap():
    if call("rimworld/get_ui_state").get("programState") != "Playing" and not quicktest():
        return row("tap.map", None, "no map")
    call("jawa/static_call", type="Verse.Log", method="ResetMessageCount")
    r = fe("read")
    row("tap.armed_at_registration", r.get("armed") is True and r.get("armedBy") == "bridge-registration", "%s %s; before: %s" % (r.get("armedBy"), r.get("armedUtc"), r.get("beforeArm")))
    s0 = (r.get("session") or {}).get("firstException")
    r = fe("arm", label="clean window")
    step(300)
    r = fe("read")
    row("tap.clean_window_is_none_seen", r.get("state") == "NONE_SEEN", "%s blind=%s first=%s" % (
        r.get("state"), r.get("blind"), ((r.get("window") or {}).get("firstException") or {}).get("text")))
    fe("arm", label="plain error")               # its own window: another mod's plain error may be the first in the last one
    call("jawa/static_call", type="Verse.Log", method="Error", args="a plain error of the proof")
    r = fe("read")
    row("tap.plain_error_is_not_an_exception", r.get("state") == "NONE_SEEN" and "plain error" in str((r.get("window") or {}).get("firstError")), (r.get("window") or {}).get("errors"))
    t = tick()
    r = fe("plant", kind="caught", flood=12000)
    w = r.get("window") or {}
    first = w.get("firstException") or {}
    row("tap.thrown_exception_is_the_first", r.get("state") == "SEEN" and "planted exception" in str(first.get("text")) and first.get("tick") == t
        and "PlantedThrow" in str(first.get("text")) + str(first.get("stack")), "tick %s (game %s) source %s text %s" % (first.get("tick"), t, first.get("source"), str(first.get("text"))[:160]))
    row("tap.one_throw_counts_once", w.get("exceptions") == 1, w.get("exceptions"))
    row("tap.flood_reached_the_cap_and_is_said", bool(r.get("blind")) and bool(r.get("capHitUtc")), r.get("blind"))
    step(10)
    call("jawa/static_call", type="Verse.Log", method="Error", args="System.Exception: a later one, after the cap")
    r = fe("read")
    w = r.get("window") or {}
    row("tap.first_survives_the_flood", "planted exception" in str((w.get("firstException") or {}).get("text")) and w.get("exceptions") == 2
        and len(r.get("kept") or []) >= 2, "exceptions %s kept %s" % (w.get("exceptions"), [k.get("key") for k in r.get("kept") or []][-2:]))
    r = fe("arm", label="while capped")
    row("tap.capped_log_is_partial_never_none", r.get("state") == "NONE_SEEN_PARTIAL", "%s %s" % (r.get("state"), r.get("blind")))
    s = (r.get("session") or {}).get("firstException") or {}
    row("tap.arm_keeps_the_sessions_first", s.get("seq") is not None and s.get("seq") == (s0 or first).get("seq"), "seq %s" % s.get("seq"))
    call("jawa/static_call", type="Verse.Log", method="ResetMessageCount")
    r = fe("arm", label="unity")
    row("tap.revived_log_is_none_seen", r.get("state") == "NONE_SEEN", r.get("blind"))
    r = fe("plant", kind="unity")
    first = (r.get("window") or {}).get("firstException") or {}
    row("tap.unity_exception_is_seen_once", r.get("state") == "SEEN" and first.get("source") == "unity Exception" and (r.get("window") or {}).get("exceptions") == 1,
        "%s %s" % (first.get("source"), (r.get("window") or {}).get("exceptions")))
    miss = unhook("mandrake.jawabench.firstexception")
    r = fe("arm", label="unhooked")
    row("tap.removed_hook_is_not_armed", None if miss else r.get("state") == "NOT_ARMED" and r.get("armed") is False, miss or "%s: %s" % (r.get("state"), r.get("notArmedWhy")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".")
    ap.add_argument("--only", default="receipt,calm,tap")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    connect()
    only = a.only.split(",")
    if "receipt" in only:
        receipt_planted(receipt(a.out))
    if "calm" in only:
        calm()
    if "tap" in only:
        tap()
    n = dict((v, sum(1 for _r, x in ROWS if x == v)) for v in ("PASS", "FAIL", "UNMEASURED"))
    print("three tools live: %d PASS, %d FAIL, %d UNMEASURED" % (n["PASS"], n["FAIL"], n["UNMEASURED"]))
    return 1 if n["FAIL"] else (2 if n["UNMEASURED"] or not ROWS else 0)


if __name__ == "__main__":
    sys.exit(main())
