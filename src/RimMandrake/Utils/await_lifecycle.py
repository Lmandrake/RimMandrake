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


def phase_of(call):
    """-> (phase, ui dict). phase is menu | loading | missing_map | map_ready | unreachable. One or two calls."""
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
    if isinstance(n, int) and n >= 1:
        return "map_ready", ui
    return "missing_map", dict(ui, mapCount=n)


def _reached(state, phase):
    if state == "menu":
        return phase == "menu"
    if state == "playing":
        return phase in ("map_ready", "missing_map")
    return phase == "map_ready"


def await_lifecycle(call, state="map_ready", deadline_s=120.0, start=False, poll_s=1.0,
                    clock=time.monotonic, sleep=time.sleep):
    """Wait until the game is in `state` or `deadline_s` of wall clock passes. -> Lifecycle (truthy when reached)."""
    if state not in STATES:
        raise ValueError("state must be one of %s, not %r" % (", ".join(STATES), state))
    t0 = clock()
    polls, started, phase, ui = 0, False, None, {}
    while True:
        phase, ui = phase_of(call)
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
                   "map_ready": "a map is up, but %s was wanted" % state}.get(phase, phase)
            return Lifecycle(False, state, phase, "timeout after %.0fs waiting for %s: %s" % (waited, state, why),
                             waited, polls, started, ui)
        sleep(poll_s)
