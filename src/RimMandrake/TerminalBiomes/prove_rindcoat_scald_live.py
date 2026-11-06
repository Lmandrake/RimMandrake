#!/usr/bin/env python3
"""Live proof A1 of RINDCOAT_TUNE_NEAR_IMMUNE_AFTER_ALL: an Awful RM_Apparel_RindCoat wearer on a real RM_TheScald map
under held steam lives two days, and its RM_ScaldExposure reads near 0.08x the unprotected clock, never zero.

    python.exe src/RimMandrake/TerminalBiomes/prove_rindcoat_scald_live.py --max-seconds 2400

One literal command. --max-seconds is the live round's own budget flag (relentless_live.proof_budget gives such a proof
N + 120 s); the run stops advancing 60 s short of it. Resumable across rounds: the first call stages the
site with proof_scald_steam.setup(), every call advances up to that wall of real time with proof_scald_steam.run() and keeps its
samples in TEMP, and the call that sees the two days through judges. Exit 0 PASS, 1 FAIL, 2 UNMEASURED (bridge down, run
still in progress: the next round resumes). A staged run whose map is gone (the game restarted) is staged again.

The verdict is recomputed here from the raw samples, not taken from proof_scald_steam's rows, and checks the floor
itself: the clock def must carry minDriveFactor 0.08 (a moved floor would move the replay with it), and the coat's
measured exposure divided by the UNPROTECTED replay (same weather samples, drive factor 1) must sit in RATIO_BAND around
0.08 (the reversed 0.4x rung reads ~0.40; an unprotected coat ~1.0; a zeroed clock 0).
"""
import json
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
CLOCK_DEF = os.path.join(HERE, "Defs", "HediffDefs", "RM_ScaldExposure.xml")
DAY = 60000
FLOOR = 0.08                 # owner by card 2026-11-06: near-immune, the 8% floor, never zero (Ban 3)
RATIO_BAND = (0.05, 0.11)    # measured / unprotected replay; 0.08 sits mid-band, 0.4x and 1.0x far outside
STEAM_SHARE = 0.9            # the run must be steam for >= 90% of its ticks, or the clock was not driven


def clock():
    """-> (severityPerDayExposed, severityPerDayUnexposed, minDriveFactor) read from the clock def on disk."""
    comp = next(li for li in ET.parse(CLOCK_DEF).getroot().iter("li")
                if li.get("Class", "").endswith("HediffCompProperties_EnvironmentalExposure"))
    return (float(comp.findtext("severityPerDayExposed")), float(comp.findtext("severityPerDayUnexposed")),
            float(comp.findtext("minDriveFactor")))


def replay(log, key, up, down, factor):
    """RM_ScaldExposure on `key` replayed from the sampled weather at drive factor `factor` (each interval takes the
    weather read at its start, as proof_scald_steam.floor_model does)."""
    alive = [r for r in log if not r[key].get("dead")]
    sev = 0.0
    for a, b in zip(alive, alive[1:]):
        dt = (b["tick"] - a["tick"]) / DAY
        sev = max(0.0, sev + dt * (up * factor if a["weather"] == "RM_ScaldSteam" else down))
    return sev


def decide(d, up, down, floor):
    """A finished run's json (log, died) and the clock -> (exit code, one line). Pure: the selftest drives it."""
    if abs(floor - FLOOR) > 1e-9:
        return 1, "FAIL: the clock's minDriveFactor is %s, not the 8%% floor" % floor
    log, died = d.get("log") or [], d.get("died") or {}
    if len(log) < 3:
        return 2, "UNMEASURED: the run holds %d samples" % len(log)
    last = log[-1]["tick"]
    if last < 2 * DAY:
        return 2, "UNMEASURED: the run reached tick %d of %d" % (last, 2 * DAY)
    steam = sum(b["tick"] - a["tick"] for a, b in zip(log, log[1:]) if a["weather"] == "RM_ScaldSteam")
    if steam < STEAM_SHARE * last:
        return 1, "FAIL: steam held %d of %d ticks" % (steam, last)
    if died.get("rind") is not None and died["rind"] <= 2 * DAY:
        return 1, "FAIL: the rind wearer died at tick %s" % died["rind"]
    alive = [r for r in log if not r["rind"].get("dead")]
    if not alive or alive[-1]["tick"] < 2 * DAY:
        return 1, "FAIL: the rind wearer was not read alive at two days"
    measured = next((h[1] for h in alive[-1]["rind"]["hediffs"] if h[0] == "RM_ScaldExposure"), 0.0)
    if not measured > 0:
        return 1, "FAIL: the rind wearer's exposure reads %s: the clock must never zero (Ban 3)" % measured
    bare = replay(log, "rind", up, down, 1.0)
    if bare <= 0:
        return 2, "UNMEASURED: the unprotected replay reads %s" % bare
    ratio = measured / bare
    line = "rind exposure %.4f vs unprotected replay %.4f: %.3fx (band %s..%s)" % (measured, bare, ratio, *RATIO_BAND)
    return (0, "PASS: " + line) if RATIO_BAND[0] <= ratio <= RATIO_BAND[1] else (1, "FAIL: " + line)


def game_tick(info):
    """get_game_info reply -> ticksGame, or None with no game loaded: the main menu answers without the key
    (GAMEENV_FIX_PROOFSITE_528224CB_ITEMS_WAIT, where a bare KeyError read 'UNMEASURED: bridge: 'ticksGame''). Pure."""
    t = info.get("ticksGame") if isinstance(info, dict) else None
    return t if isinstance(t, int) and not isinstance(t, bool) else None


def main(argv):
    import argparse
    import proof_scald_steam as ps
    a = argparse.ArgumentParser()
    a.add_argument("--max-seconds", type=int, default=540)
    wall = max(60, a.parse_args(argv).max_seconds - 60)
    out = os.path.join(os.environ.get("TEMP", "."), "prove_rindcoat_scald_live.json")
    try:
        c = ps.bridge()
        info = ps.call(c, "rimworld/get_game_info")
        now = game_tick(info)
        if now is None:
            print("UNMEASURED: no game loaded (get_game_info has no ticksGame; status %s); the live-site step "
                  "`live_site.py --game` stages a quicktest" % (info.get("status") if isinstance(info, dict) else info))
            return 2
        st = json.load(open(ps.STATE)) if os.path.exists(ps.STATE) and os.path.exists(out) else None
        prior = json.load(open(out)) if st else {}
        stale = st is None or now < st["t0"] or (ps.read(c, st["roster"]["rind"]) is None
                                                  and "rind" not in prior.get("died", {}))
        if stale:
            if os.path.exists(out):
                os.remove(out)
            ps.setup()
            json.dump({"log": [], "died": {}}, open(out, "w"))
        try:
            ps.run(out, 2 * DAY + 500, wall=wall)
        except SystemExit:
            pass                       # judge() exits with its own rows; the verdict here is recomputed below
    except Exception as e:             # noqa: BLE001 -- any bridge failure is a reading not taken
        print("UNMEASURED: bridge: %s" % str(e).replace("\n", " ")[:200])
        return 2
    d = json.load(open(out))
    if "verdict" not in d:
        print("UNMEASURED: run in progress at tick %s of %d; the next round resumes"
              % ((d.get("log") or [{}])[-1].get("tick"), 2 * DAY))
        return 2
    code, line = decide(d, *clock())
    os.replace(out, out + ".done")     # a judged run is never judged again: the next call stages a fresh one
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
