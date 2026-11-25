#!/usr/bin/env python3
"""Live proof of the calm profile of BRIDGE v2.0 (jawa/calm_profile). Page: design/specs/2026-11-23-bridge-v2/boundary.md
§CALM PROFILE. Item RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE. The offline rules are selftest_calm_profile.py.

Run under Windows python.exe on a TEST-profile game on a small mod list (never a campaign save, no flyer), after
build.py --gm --apply and a restart:

    python.exe prove_calm_profile.py [--game ArchSmall] [--out DIR]

The five rows of the ticket, each on a fresh quicktest map with the profile armed (certified lines from the committed tap
certificate when it is valid for the loaded identity, else none: the controls then read ARMED UNPROVEN, which the rows accept):
  planted_incident_is_one_breach             a forced RaidEnemy by a call: held, and ONE breach that names it
  planted_wild_animal_at_the_edge_is_one_breach  a Muffalo spawned at the map edge by an act inside a run (a game tick): ONE
                                             arrival breach that names it
  planted_weather_change_is_one_breach      a locked Rain: ONE weather breach that names it
  a_load_in_the_middle_changes_no_status    save, load: the profile re-arms itself, every control's status as before
  a_killed_driver_leaves_no_control_on      a child process arms with a 0.1-minute lease and is killed: after the lease the
                                             profile is off and the storyteller switch, the gates and the wild spawner are back
The save it makes and loads is rm_proof_calm_profile. Exit 0 = every row PASS, 1 = a FAIL, 2 = UNMEASURED."""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
sys.path.insert(0, HERE)
import prove_scene_tick_wiring as W  # noqa: E402  the connection, call() and row()

SAVE = "rm_proof_calm_profile"
DRIVER = "prove_calm:%d" % os.getpid()
OK_STATUS = ("HELD", "ARMED UNPROVEN", "OFF")


def connect(game):
    if game:
        import prove_tap_certificate as TC
        return TC.connect(game)
    W.connect()
    return W


def cp(action, driver=DRIVER, **p):
    return W.call("jawa/calm_profile", action=action, driver=driver, **p)


def statuses(r):
    return {c.get("name"): c.get("status") for c in r.get("controls") or []}


def new_breaches(r, seq):
    return [b for b in ((r.get("breaches") or {}).get("rows") or []) if (b.get("seq") or 0) > seq]


def certified():
    """The certified lines for the loaded identity: calm_profile.certificate_lines on the committed tap certificate."""
    import calm_profile
    import tap_certificate as T
    try:
        with open(T.RESULT, encoding="utf-8") as f:
            cert = (json.load(f) or {}).get("certificate")
    except (OSError, ValueError):
        cert = None
    ident = T.read_identity(lambda tool, args: W.call(tool, **args))
    if ident is None:
        return [], "the loaded identity could not be read"
    return calm_profile.certificate_lines(cert, ident)


def fresh_map():
    import prove_run_until as R
    R.W = W
    if (W.call("jawa/companion_handshake").get("game") or {}).get("programState") != "Entry":
        W.call("rimworld/go_to_main_menu")
    return R.start_map()


def arm(lines, **spec):
    spec = dict({"profile": "standard", "version": 1, "minutes": 30, "certified": ",".join(lines)}, **spec)
    return cp("arm", spec=json.dumps(spec))


def wait_frames(s=1.5):
    time.sleep(s)                  # Root_Play.Update runs each frame, paused or not: the gate poll and the weather watch


def child(lease_min, game):
    """--child: arm as another driver with a short lease, say so, then wait to be killed."""
    connect(game)
    r = cp("arm", driver="child:%d" % os.getpid(), spec=json.dumps({"profile": "standard", "minutes": lease_min}))
    print("ARMED" if r.get("success") else "REFUSED %s" % r.get("message"), flush=True)
    time.sleep(3600)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--child", type=float, default=None)
    a = ap.parse_args()
    if a.child is not None:
        return child(a.child, a.game)
    connect(a.game)
    hs = W.call("jawa/companion_handshake")
    if str(hs.get("effectiveProfile") or "").lower() != "test":
        print("UNMEASURED: the companion's effective profile is %r, not test" % hs.get("effectiveProfile"))
        return 2
    if not fresh_map():
        print("UNMEASURED: no quicktest map")
        return 2
    lines, why = certified()
    print("certified lines: %s (%s)" % (lines, why), flush=True)
    cp("leave")
    r = arm(lines)
    st0 = statuses(r)
    if not W.row("arm", r.get("success") is True and st0 and all(v in OK_STATUS for v in st0.values()), "%s; %s" % (st0, r.get("message"))):
        print(json.dumps(r, indent=1)[:4000])
        return 1

    # 1. a planted incident
    seq = (r.get("breaches") or {}).get("lastSeq") or 0
    f = W.call("jawa/fire_incident", incidentDef="RaidEnemy", forced=True, points=200)
    wait_frames()
    r = cp("read", sinceSeq=seq)
    nb = new_breaches(r, seq)
    W.row("planted_incident_is_one_breach", f.get("fired") is not True and len(nb) == 1 and nb[0].get("kind") == "incident_held" and "RaidEnemy" in str(nb[0].get("what")),
          "fired=%s breaches=%s; reply %s" % (f.get("fired"), nb, json.dumps(f)[:300]))

    # 2. a planted wild animal at the map edge, in a game tick (an act of a run)
    import prove_run_until as R
    R.W = W
    seq = (r.get("breaches") or {}).get("lastSeq") or 0
    mi = W.call("jawa/map_info")
    z = int(mi.get("sizeZ", 250)) // 2
    R.DRIVER = DRIVER
    R.open_session(lease=120)
    t0 = R.tick() or 0
    rep = R.run(R.at_tick(t0 + 6), 60, acts=[{"tool": "jawa/spawn_pawn", "at": 2, "id": R.req("edge_animal"),
                                               "args": {"kindDef": "Muffalo", "x": 2, "z": z, "faction": "none"}}])
    R.end_session()
    wait_frames()
    r = cp("read", sinceSeq=seq)
    nb = new_breaches(r, seq)
    W.row("planted_wild_animal_at_the_edge_is_one_breach", len(nb) == 1 and nb[0].get("kind") == "arrival" and "Muffalo" in str(nb[0].get("what")),
          "run %s %s; acts %s; breaches=%s; placed=%s" % (rep.get("run"), rep.get("why"), [x.get("state") for x in rep.get("acts") or []], nb, r.get("placed")))

    # 3. a planted weather change
    seq = (r.get("breaches") or {}).get("lastSeq") or 0
    W.call("jawa/weather_set", weather="Rain", lockWeather=True)
    W.call("rimworld/step_game_ticks", ticks=1, pauseFirst=True)
    wait_frames()
    r = cp("read", sinceSeq=seq)
    nb = new_breaches(r, seq)
    W.row("planted_weather_change_is_one_breach", len(nb) == 1 and nb[0].get("kind") == "weather" and "Rain" in str(nb[0].get("what")), "breaches=%s" % nb)
    W.call("jawa/weather_set", unlock=True)

    # 4. a load in the middle changes no status
    cp("leave")
    st0 = statuses(arm(lines))
    W.call("rimworld/save_game", saveName=SAVE)
    W.call("rimworld/load_game", saveName=SAVE, ignoreModCompatibility=True)
    from await_lifecycle import await_lifecycle
    time.sleep(5)
    if not await_lifecycle(W.call, "map_ready", deadline_s=400):
        W.row("a_load_in_the_middle_changes_no_status", None, "the load did not reach Playing")
    else:
        wait_frames(3)
        r = cp("read")
        st1 = statuses(r)
        W.row("a_load_in_the_middle_changes_no_status", r.get("armed") is True and (r.get("rearms") or 0) >= 1 and st1 == st0,
              "rearms=%s policy=%s; before %s; after %s; notPutBack %s" % (r.get("rearms"), r.get("rearmPolicy"), st0, st1, r.get("notPutBack")))
    cp("leave")

    # 5. a killed driver leaves no control on after its lease
    p = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--child", "0.1"] + (["--game", a.game] if a.game else []),
                         stdout=subprocess.PIPE, text=True)
    first = p.stdout.readline().strip()
    p.kill()
    p.wait()
    armed = cp("read")
    time.sleep(10)                 # the lease is 6 s; the put-back runs on the next frame
    r = cp("read")
    site = W.call("jawa/site_state")
    gates = str(r.get("gates"))
    W.row("a_killed_driver_leaves_no_control_on", first == "ARMED" and armed.get("armed") is True and r.get("armed") is False and r.get("leaseEnd") == "lease ended"
          and (site.get("storyteller") or {}).get("enabledAfter") is True and not r.get("notPutBack"),
          "child %s; armed then %s; now armed=%s leaseEnd=%s notPutBack=%s storyteller=%s gates=%s" % (
              first, armed.get("armed"), r.get("armed"), r.get("leaseEnd"), r.get("notPutBack"), site.get("storyteller"), gates[:200]))

    if a.out:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "prove_calm_profile_rows.json"), "w", encoding="utf-8") as f:
            json.dump(W.ROWS, f, indent=1)
    n = dict((v, sum(1 for _r, x in W.ROWS if x == v)) for v in ("PASS", "FAIL", "UNMEASURED"))
    print("calm profile live: %d PASS, %d FAIL, %d UNMEASURED" % (n["PASS"], n["FAIL"], n["UNMEASURED"]))
    return 1 if n["FAIL"] else (2 if n["UNMEASURED"] or not W.ROWS else 0)


if __name__ == "__main__":
    sys.exit(main())
