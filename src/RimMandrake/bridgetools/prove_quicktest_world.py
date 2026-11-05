"""Prove rimworld/start_debug_game_ready reaches a real Playing map (DEBUG_GAME_READY_WORLDUI_CRASH_1).
Run under Windows python.exe from the repo root. Exit 0 = a FRESH quicktest is Playing (the start said success and one
map is loaded), 1 = not. A game already Playing is not fresh: the start answers success false ("A game is already
loaded.") and the old game, often with a foreign second map, must not pass (GRAFFITI_NORTHSTAR_GREEN_FULL_1 gen 17).
So a Playing TEST game (tick <= MAX_TICKS) is left for the main menu first; a colony past it is refused, never left."""
import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0); S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

MAX_TICKS = 120000   # two in-game days: past it the game is someone's colony, never left (live_site.py's bound)
t0 = time.time()
# A game already Playing makes the start refuse ("A game is already loaded.", live E2 2026-11-03), so a proof staged on
# a map could never be fresh: leave a TEST game for the main menu first, then start (GRAFFITI_NORTHSTAR_GREEN_FULL_1).
st0 = call("rimworld/get_ui_state")
if st0.get("programState") == "Playing":
    ticks = call("rimworld/get_game_info").get("ticksGame")
    if not isinstance(ticks, int) or ticks > MAX_TICKS:
        print("NOT READY: a game is Playing at tick %s (unread or > %d): a colony, not a test map; not leaving it"
              % (ticks, MAX_TICKS))
        sys.exit(1)
    call("rimworld/go_to_main_menu")
    for _ in range(120):
        if call("rimworld/get_ui_state").get("programState") == "Entry": break
        time.sleep(1)
    else:
        print("NOT READY: left a Playing test game (tick %s) but never reached the main menu in 120 s" % ticks)
        sys.exit(1)
    print("left a Playing test game (tick %s) for the main menu" % ticks)
r = call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
print("start_debug_game_ready:", json.dumps(r)[:400])
st = {}
for _ in range(90):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing": break
    time.sleep(1)
print("programState:", st.get("programState"), "after %.0fs" % (time.time() - t0))
gi = call("rimworld/get_game_info")
print("get_game_info:", json.dumps(gi)[:400])
# hasCurrentGame lives on get_ui_state (reload_check.py, w9_run.py read it there), not get_game_info: the old
# gi.get("hasCurrentGame") is not False was None-is-not-False, always true, so "with a world" was never checked.
started = isinstance(r, dict) and r.get("success") is True
ok = started and st.get("programState") == "Playing" and st.get("hasCurrentGame") is True and gi.get("mapCount") == 1
print("started:", started, "hasCurrentGame:", st.get("hasCurrentGame"), "mapCount:", gi.get("mapCount"), "->",
      "OK" if ok else "NOT READY" if started else "NOT FRESH (start refused: %s)" % str(
          ((r.get("entry") or {}).get("blockingReason") or r.get("message")) if isinstance(r, dict) else r)[:120])
sys.exit(0 if ok else 1)
