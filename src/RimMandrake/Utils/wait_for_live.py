#!/usr/bin/env python3
"""wait_for_live.py - block until the game is actually LIVE, then say so once.

WHY THIS EXISTS
===============
`agents_def.md` rule 1b: **live means a map exists, measured by BRIDGE** — never
inferred from a splash screen and never from how long it has been. BRIDGE is the
only seat that can take that measurement, and other seats' work keys off the
call: OPS's savegame deletion only sticks inside the running-game window, and
that window opens on BRIDGE's signal.

So the cost of noticing late is real, and "check every few minutes" is exactly
how late happens. This blocks instead.

🔴 RUN IT WITH `python.exe`, NOT `python3`.
RimBridge binds Windows loopback and WSL2 is NAT-mode, so from WSL there is no
route at all — not a timeout, no route. The opposite rule applies to anything
that reads `/mnt/c` paths, which Windows Python cannot resolve. **The
interpreter is chosen by what the script TOUCHES, not by habit**; this one talks
to the bridge, so it is `python.exe`. See `skills/rimbridge/references/traps.md`.

    python.exe src/RimMandrake/Utils/wait_for_live.py
    python.exe src/RimMandrake/Utils/wait_for_live.py --timeout 3600

WHAT IT MEASURES, AND WHY THAT IS THE INTERESTING PART
======================================================
Three moments, not one:

  1. **bridge answering** — a token appears in `Player.log` and `ping` returns.
  2. **map exists**       — `currentMapReady` true and no long event pending.
  3. **reactive**         — the owner measured ~40 s AFTER (1) during which the
                            game is not really reactive, whatever the readiness
                            flags say.

Every flag we have describes (1). Announcing on (2) is the rule. Mutating before
(3) is the trap. This prints all three and the gaps between them, so the ~40 s
figure stops being folklore and starts being a measured number that can be
argued with — on this stack, on this day, at this mod count.
"""
import argparse
import os
import sys
import time

_UTILS = os.path.dirname(os.path.abspath(__file__))
if _UTILS not in sys.path:
    sys.path.insert(0, _UTILS)


def stamp():
    return time.strftime("%H:%M:%S")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--timeout", type=int, default=3000,
                    help="Give up after this many seconds. A cold load on this "
                         "stack is 23-30 min, so the default allows for one "
                         "plus slack.")
    ap.add_argument("--poll", type=int, default=5, help="Seconds between polls.")
    ap.add_argument("--settle", type=int, default=40,
                    help="Report when this many seconds have passed since the "
                         "bridge first answered — the owner's reactive window.")
    cfg = ap.parse_args(argv)

    from rimbridge_client import RimBridge, resolve_endpoint      # noqa: E402

    t0 = time.time()
    t_bridge = None
    t_map = None
    rb = None

    print("%s  waiting for the bridge (timeout %ds)" % (stamp(), cfg.timeout))
    while time.time() - t0 < cfg.timeout:
        # ---- phase 1: is there an endpoint to talk to at all?
        if rb is None:
            try:
                host, port, token = resolve_endpoint()
            except Exception:
                host = port = token = None
            # ⚠️ An EMPTY TOKEN is the tell that the game is still loading, not
            # that the transport is broken. resolve_endpoint scrapes host/port/
            # token out of Player.log, so before RimBridge's startup line there
            # is simply nothing to scrape — and the resulting failure is
            # character-for-character the WSL no-route failure. Two causes, one
            # symptom; do not go hunting a network problem here.
            if token:
                try:
                    rb = RimBridge(host, port, token)
                    rb.connect()
                    rb.call("rimbridge/ping", {})
                    t_bridge = time.time()
                    print("%s  BRIDGE ANSWERING  (%.0fs after start) %s:%s"
                          % (stamp(), t_bridge - t0, host, port))
                except Exception as e:
                    rb = None
                    print("%s  endpoint seen, not yet answering: %s"
                          % (stamp(), str(e)[:70]))

        # ---- phase 2: does a MAP exist? This is the announceable moment.
        if rb is not None:
            try:
                st = (rb.call("rimbridge/get_bridge_status", {})
                      or {}).get("state") or {}
                # mapCount > 0 is TRUE AND INSUFFICIENT: the map can exist while
                # Find.CurrentMap is still null, and every companion tool then
                # fails with "No current map", which reads like a broken tool.
                if st.get("currentMapReady") and not st.get("longEventPending"):
                    t_map = time.time()
                    since_bridge = t_map - (t_bridge or t_map)
                    print("\n%s  🔴 MAP EXISTS — THE GAME IS LIVE" % stamp())
                    print("     %.0fs after start, %.0fs after the bridge "
                          "answered" % (t_map - t0, since_bridge))
                    print("     paused=%s mapCount=%s playable=%s"
                          % (st.get("paused"), st.get("mapCount"),
                             st.get("playable")))
                    remaining = cfg.settle - since_bridge
                    if remaining > 0:
                        print("     ⚠️ %.0fs of the reactive window still to "
                              "run. ANNOUNCE NOW — read-only is fine — but do "
                              "not mutate yet." % remaining)
                    else:
                        print("     ✅ reactive window already elapsed "
                              "(%.0fs >= %ds); mutation is clear."
                              % (since_bridge, cfg.settle))
                    return 0
            except Exception as e:
                # A dead socket mid-load is ordinary. Rebuild rather than exit:
                # one timeout desyncs the client for every later call, so the
                # connection is not reusable after a failure.
                print("%s  bridge went away (%s) — reconnecting"
                      % (stamp(), str(e)[:60]))
                rb = None

        time.sleep(cfg.poll)

    print("%s  TIMED OUT after %ds. %s"
          % (stamp(), cfg.timeout,
             "Bridge never answered." if t_bridge is None
             else "Bridge answered but no map ever became current."))
    return 1


if __name__ == "__main__":
    sys.exit(main())
