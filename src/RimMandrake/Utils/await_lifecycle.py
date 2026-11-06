#!/usr/bin/env python3
"""await_lifecycle: the ONE wait for the game to reach a lifecycle state (READYWAITS_UNIFY_ONE_HELPER).

Replaces the loop copy-pasted into ~50 proofs (design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md §2 T8):

    if call("rimworld/get_ui_state").get("programState") != "Playing":
        call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
        for _ in range(120):
            if call("rimworld/get_ui_state").get("programState") == "Playing": break
            time.sleep(1)

That loop fell through silently on a timeout and never asked whether a map exists. Use instead:

    from await_lifecycle import await_lifecycle
    lc = await_lifecycle(s.call, "map_ready", deadline_s=400, start=True)
    if not lc.ok:
        print("UNMEASURED: %s" % lc.reason); return 2

`call(tool, **params) -> dict` is any session's call (an MCP {"content": [{"text": json}]} envelope is opened).
States (wall clock and frames, never ticks: no tick runs while a map loads):
    menu       programState == "Entry"
    playing    programState == "Playing"
    map_ready  playing AND rimworld/get_game_info mapCount >= 1 (get_ui_state has no map key: hasCurrentGame is
               true for a game with no map, skills/rimbridge/references/traps.md)
settle=True (READYWAITS_MIGRATE_REMAINING_52_COPIES): map_ready also needs rimbridge/get_bridge_status state
               automationReady and no longEventPending (phase "settling" until then); the recipe the Regenerate Current
               Map waits used (that status has NO currentMapReady key, MEASURED 2026-10-07).
new_map_of=<mapId>: map_ready also needs jawa/map_info mapId to be a NEW id (phase "old_map" until then):
               programState stays Playing through a regen, so only a new mapId proves the map was rebuilt.
await_leaving(call, state, deadline_s): the other direction, e.g. after load_game the old map stays Playing for
               ~3-8 s before the load starts; ok once the game no longer reads `state`.
start=True: when the game sits at the menu and a playing state is wanted, start_debug_game_ready is called ONCE.
A call that raises (the bridge drops while a map builds) counts as "loading" and the wait goes on.
Never raises on a timeout: the result says ok=False with the phase it last saw (loading | menu | missing_map |
unreachable) in `reason`.
"""
import json
import time

STATES = ("menu", "playing", "map_ready")
START_PARAMS = {"timeoutMs": 280000, "readiness": "mapData", "pauseIfNeeded": True}


class Lifecycle(object):
    """The outcome of one wait. ok, state wanted, phase last seen, reason, waited_s, polls, started, last ui dict."""

    def __init__(self, ok, state, phase, reason, waited_s, polls, started, last):
        self.ok, self.state, self.phase, self.reason = ok, state, phase, reason
        self.waited_s, self.polls, self.started, self.last = waited_s, polls, started, last

    def __bool__(self):
        return self.ok

    __nonzero__ = __bool__

    def __repr__(self):
        return "Lifecycle(ok=%r, state=%r, phase=%r, reason=%r, waited_s=%.1f, polls=%d, started=%r)" % (
            self.ok, self.state, self.phase, self.reason, self.waited_s, self.polls, self.started)


def _open(r):
    if isinstance(r, dict) and isinstance(r.get("content"), list) and r["content"]:
        try:
            r = json.loads(r["content"][0].get("text") or "")
        except (ValueError, AttributeError, TypeError, KeyError):
            return {}
    return r if isinstance(r, dict) else {}


def phase_of(call, settle=False, new_map_of=None):
    """-> (phase, ui dict). phase is menu | loading | missing_map | settling | old_map | map_ready | unreachable."""
    try:
        ui = _open(call("rimworld/get_ui_state"))
    except Exception as ex:  # noqa: BLE001  the bridge can drop while a map builds: poll, never trust
        return "unreachable", {"error": str(ex)[:200]}
    ps = ui.get("programState")
    if ps == "Entry":
        return "menu", ui
    if ps != "Playing":
        return ("loading" if ps else "unreachable"), ui
    try:
        gi = _open(call("rimworld/get_game_info"))
    except Exception as ex:  # noqa: BLE001
        return "loading", dict(ui, gameInfoError=str(ex)[:200])
    n = gi.get("mapCount")
    if not (isinstance(n, int) and n >= 1):
        return "missing_map", dict(ui, mapCount=n)
    if settle:
        try:
            st = _open(call("rimbridge/get_bridge_status")).get("state") or {}
        except Exception as ex:  # noqa: BLE001
            return "settling", dict(ui, statusError=str(ex)[:200])
        if not st.get("automationReady") or st.get("longEventPending"):
            return "settling", dict(ui, bridgeState=st)
    if new_map_of is not None:
        try:
            mid = _open(call("jawa/map_info")).get("mapId")
        except Exception as ex:  # noqa: BLE001
            return "old_map", dict(ui, mapInfoError=str(ex)[:200])
        if mid is None or mid == new_map_of:
            return "old_map", dict(ui, mapId=mid)
    return "map_ready", ui


def _reached(state, phase):
    if state == "menu":
        return phase == "menu"
    if state == "playing":
        return phase in ("map_ready", "missing_map", "settling", "old_map")
    return phase == "map_ready"


def await_lifecycle(call, state="map_ready", deadline_s=120.0, start=False, poll_s=1.0,
                    clock=None, sleep=None, settle=False, new_map_of=None):
    """Wait until the game is in `state` or `deadline_s` of wall clock passes. -> Lifecycle (truthy when reached).
    clock/sleep default to time.monotonic/time.sleep looked up at CALL time, so a test that patches time.sleep
    (Stillsand's selftest does) reaches the helper too."""
    clock, sleep = clock or time.monotonic, sleep or time.sleep
    if state not in STATES:
        raise ValueError("state must be one of %s, not %r" % (", ".join(STATES), state))
    t0 = clock()
    polls, started, phase, ui = 0, False, None, {}
    while True:
        phase, ui = phase_of(call, settle and state == "map_ready", new_map_of if state == "map_ready" else None)
        polls += 1
        waited = clock() - t0
        if _reached(state, phase):
            return Lifecycle(True, state, phase, "reached %s after %.1fs" % (state, waited), waited, polls,
                             started, ui)
        if start and not started and phase == "menu" and state != "menu":
            started = True
            try:
                call("rimworld/start_debug_game_ready", **START_PARAMS)
            except Exception as ex:  # noqa: BLE001  a start that times out may still be loading: keep polling
                ui = dict(ui, startError=str(ex)[:200])
            continue
        if waited >= deadline_s:
            why = {"menu": "the game is at the main menu" + ("" if start else " (start=False)"),
                   "loading": "the game is still loading (programState %s)" % ui.get("programState"),
                   "missing_map": "a game is playing but has no map (mapCount %r)" % ui.get("mapCount"),
                   "unreachable": "the bridge did not answer: %s" % ui.get("error", ui),
                   "settling": "a map is up but the bridge is not settled: %s" % ui.get("bridgeState", ui),
                   "old_map": "the map is still the old one (mapId %r)" % ui.get("mapId", new_map_of),
                   "map_ready": "a map is up, but %s was wanted" % state}.get(phase, phase)
            return Lifecycle(False, state, phase, "timeout after %.0fs waiting for %s: %s" % (waited, state, why),
                             waited, polls, started, ui)
        sleep(poll_s)


def await_leaving(call, state="playing", deadline_s=30.0, poll_s=0.5, clock=None, sleep=None):
    """Wait until the game NO LONGER reads `state` (menu | playing | map_ready). -> Lifecycle, ok once it left;
    `state` in the result is "left <state>". A bridge that drops counts as having left (a load is under way)."""
    clock, sleep = clock or time.monotonic, sleep or time.sleep
    if state not in STATES:
        raise ValueError("state must be one of %s, not %r" % (", ".join(STATES), state))
    t0 = clock()
    polls = 0
    while True:
        phase, ui = phase_of(call)
        polls += 1
        waited = clock() - t0
        if not _reached(state, phase):
            return Lifecycle(True, "left " + state, phase, "left %s after %.1fs (now %s)" % (state, waited, phase),
                             waited, polls, False, ui)
        if waited >= deadline_s:
            return Lifecycle(False, "left " + state, phase, "timeout after %.0fs: still %s" % (waited, phase),
                             waited, polls, False, ui)
        sleep(poll_s)
