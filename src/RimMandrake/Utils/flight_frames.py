#!/usr/bin/env python3
"""flight_frames - judge a recorded flight, tick by tick, from state only. No picture is made or read.

The flapping-bird test (design/specs/2026-11-23-bridge-v2/02_needs_design.md, worked example 3). The game records, at
the end of every tick, for each bird: the flight tracker's state and lerp tick (`pawn.flight.*`), and the flip-book
frame the game SELECTS (`pawn.anim.*`: the animation, its start tick, the body node's graphic state and its texPath,
and the facing). Those probes are JawaBenchCondProbes.cs; `scene_cond.flight(pawn)` records them in `s.run`. This
module turns such a series into a verdict per bird and one outcome per run. What reaches the screen is the owner's eye
(07_for_the_owner.md, choice 1); this judges what the game selects.

The model is the game's own code (RimWorld 1.6, read 2026-11-24):
- Pawn_FlightTracker.FlightTick: Grounded -> TakingOff (lerp 0..49) -> Flying -> Landing (lerp up to 49) -> Grounded.
  ForceLand enters Landing at lerp 25, from TakingOff or Flying. No other step is legal.
- CheckFlyAnimation runs at the START of FlightTick, so on the first Grounded tick after a landing the fly animation
  is still set; it is cleared on the next flight tick. The grounded graphic is due from the second Grounded tick.
- AnimationDefGenerator_Flying: n frames, keyframe i at tick i*tpf, durationTicks (n+1)*tpf, loop mode Loop, graphic
  state `<anim>_<i>`, texPath `<prefix><i+1>_<east|north|south>` (west uses east).
- AnimationWorker_Keyframes.GetKeyframeForTick: frame 0 at anim tick 0 only, frame i on ticks (i-1)*tpf+1 .. i*tpf,
  the last frame from (n-2)*tpf+1 to the end of the loop. So frame 0 shows 1 tick and the last frame 3*tpf-1 ticks.
  The judge expects exactly that hold pattern, not an even one.

    python3 flight_frames.py audit [<KindDefName> ...]     every frame texture of our flyers exists, per facing
    python3 flight_frames.py judge <trace.jsonl> <pawn>=<KindDefName> ...   judge a kept trace (scene_judge.Trace)

Promises: design/specs/2026-11-23-bridge-v2/boundary.md §flight_frames. Selftest: selftest_flight_frames.py.
"""
import json
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

GROUNDED, TAKING_OFF, FLYING, LANDING = "Grounded", "TakingOff", "Flying", "Landing"
STATES = (GROUNDED, TAKING_OFF, FLYING, LANDING)
LEGAL = {(GROUNDED, TAKING_OFF), (TAKING_OFF, FLYING), (TAKING_OFF, LANDING), (FLYING, LANDING), (LANDING, GROUNDED)}
LAST_LERP = 49                               # TakeoffDurationTicks = LandingDurationTicks = 50
LANDING_ENTRY = (0, 1, 25, 26)               # natural landing keeps lerp 0; ForceLand sets 25; +1 if its flight tick ran after
TAKEOFF_ENTRY = (0, 1)
FACING_DIR = {"east": "east", "west": "east", "north": "north", "south": "south"}
FIELDS = ("state", "lerp", "height", "anim", "start", "graphic", "texpath", "facing")
PROBE_OF = {"state": "pawn.flight.state", "lerp": "pawn.flight.lerp_tick", "height": "pawn.flight.height", "anim": "pawn.anim.name",
            "start": "pawn.anim.start_tick", "graphic": "pawn.anim.graphic", "texpath": "pawn.anim.texpath",
            "facing": "pawn.anim.facing"}

PASS, FAIL, NOT_JUDGED, NO_FLIGHT = "PASS", "FAIL", "NOT JUDGED", "NO FLIGHT"


def keyframe(anim_tick, n, tpf):
    """AnimationWorker_Keyframes.GetKeyframeForTick over keyframes at i*tpf (i = 0..n-1)."""
    if anim_tick <= 0:
        return 0
    if anim_tick >= (n - 1) * tpf:
        return n - 1
    return -(-anim_tick // tpf)


def expected_frame(tick, start, n, tpf):
    return keyframe((tick - start) % ((n + 1) * tpf), n, tpf)


def frame_texpath(prefix, index, facing):
    return "%s%d_%s" % (prefix, index + 1, FACING_DIR.get(facing, "?"))


# ---------------------------------------------------------------------------------------------- judging one bird
def _flights(rows):
    """-> [(first index, last index or None)] of each stretch that is not Grounded."""
    out, start = [], None
    for i, r in enumerate(rows):
        if r["state"] != GROUNDED and start is None:
            start = i
        elif r["state"] == GROUNDED and start is not None:
            out.append((start, i))
            start = None
    if start is not None:
        out.append((start, None))
    return out


def _judge_flight(rows, a, b, kind):
    """Faults of one whole flight rows[a-1 .. b+1]; b is the first Grounded row after it."""
    n, tpf, prefix = kind["frames"], kind["tpf"], kind["prefix"]
    faults = []

    def fault(code, i, text):
        faults.append({"code": code, "tick": rows[i]["tick"], "why": text})

    for i in range(a, b + 1):
        prev, cur = rows[i - 1], rows[i]
        if prev["state"] != cur["state"] and (prev["state"], cur["state"]) not in LEGAL:
            fault("STATE_SKIP", i, "%s -> %s is not a step of the flight tracker" % (prev["state"], cur["state"]))
        if cur["state"] in (TAKING_OFF, LANDING):
            if prev["state"] == cur["state"]:
                if cur["lerp"] != prev["lerp"] + 1:
                    fault("LERP", i, "%s lerp %s after %s" % (cur["state"], cur["lerp"], prev["lerp"]))
            elif cur["lerp"] not in (TAKEOFF_ENTRY if cur["state"] == TAKING_OFF else LANDING_ENTRY):
                fault("LERP", i, "%s entered at lerp %s" % (cur["state"], cur["lerp"]))
        if prev["state"] in (TAKING_OFF, LANDING) and cur["state"] != prev["state"] and prev["lerp"] != LAST_LERP \
                and not (prev["state"] == TAKING_OFF and cur["state"] == LANDING):
            fault("LERP", i, "%s ended at lerp %s, not %d" % (prev["state"], prev["lerp"], LAST_LERP))
    span_anim, span_from, seen = None, None, set()
    for i in range(a, b):
        r, prev = rows[i], rows[i - 1]
        if not r["anim"]:
            fault("NO_ANIM", i, "no fly animation while %s" % r["state"])
            continue
        if i > a and r["start"] != prev["start"] and r["anim"] == prev["anim"]:
            fault("RESTART", i, "animation %s restarted at %s without a change of animation" % (r["anim"], r["start"]))
        k = expected_frame(r["tick"], r["start"], n, tpf)
        want = "%s_%d" % (r["anim"], k)
        if r["graphic"] != want:
            fault("FRAME", i, "graphic %r, the clock selects %r" % (r["graphic"], want))
        dirs = {FACING_DIR.get(r["facing"]), FACING_DIR.get(prev["facing"])}
        if not any(r["texpath"] == frame_texpath(prefix, k, d) for d in dirs if d):
            fault("TEXPATH", i, "texPath %r, want %r" % (r["texpath"], frame_texpath(prefix, k, r["facing"])))
        if r["anim"] != span_anim or (i > a and r["start"] != prev["start"]):
            span_anim, span_from, seen = r["anim"], i, set()
        seen.add(r["graphic"])
        if i - span_from + 1 == (n + 1) * tpf and n > 1 and len(seen) == 1:
            fault("FROZEN", i, "one whole loop of %s showed one frame of %d: %s" % (r["anim"], n, sorted(seen)))
    # the first Grounded row may still carry the animation (CheckFlyAnimation runs before the state steps)
    for i in range(b + 1, len(rows)):
        if rows[i]["state"] != GROUNDED:
            break
        if rows[i]["anim"] or rows[i]["graphic"]:
            fault("LANDED_FLYING", i, "grounded %d ticks after landing and still shows %r" % (i - b, rows[i]["graphic"]))
        break
    return faults


def judge_bird(rows, kind):
    """rows: one dict per tick (tick, state, lerp, anim, start, graphic, texpath, facing). kind: prefix, frames, tpf.
    -> {"verdict": PASS|FAIL|NOT JUDGED|NO FLIGHT, "faults": [...], "flights": [...]}"""
    out = {"verdict": NO_FLIGHT, "faults": [], "flights": []}
    for x, y in zip(rows, rows[1:]):
        if y["tick"] != x["tick"] + 1:
            return dict(out, verdict=NOT_JUDGED, why="ticks %d to %d are not in the series" % (x["tick"] + 1, y["tick"] - 1))
    flights = _flights(rows)
    judged = 0
    for a, b in flights:
        f = {"from": rows[a]["tick"], "to": rows[b]["tick"] if b is not None else None}
        if a == 0:
            f["judged"] = "started before the window"
        elif b is None or b + 1 >= len(rows):
            f["judged"] = "in the air at the limit" if b is None else "the window ends on its first grounded tick"
        elif any(rows[i][k] is None for i in range(a - 1, b + 2) for k in FIELDS):
            f["judged"] = "a value was unreadable during the flight"
        else:
            f["faults"] = _judge_flight(rows, a, b, kind)
            f["judged"] = "yes"
            judged += 1
            out["faults"] += f["faults"]
        out["flights"].append(f)
    if out["faults"]:
        out["verdict"] = FAIL
    elif judged:
        out["verdict"] = PASS
    elif flights:
        out["verdict"] = NOT_JUDGED
    return out


def outcome(verdicts):
    """One run's outcome over its birds (live_kinds words). Contract: a bird still in the air at the limit is not judged
    and not a miss; 'no bird took off' is the allowed miss."""
    vs = [v["verdict"] for v in verdicts.values()]
    if FAIL in vs:
        return "MOD FAILURE"
    if PASS in vs:
        return "SUCCESS"
    if all(v == NO_FLIGHT for v in vs):
        return "RANDOM MISS"
    return "COULD NOT LOOK"


# ---------------------------------------------------------------------------------------------- reading a kept trace
def track_name(pawn, field):
    return "%s/%s" % (pawn, PROBE_OF[field])


def series_from_frames(frames, pawn):
    """frames: (tick, {track name: {"st", "v"}}) as scene_judge.Trace.frames() yields them (forward-filled)."""
    rows, last = [], None
    for tick, values, _ev in frames:
        r = {"tick": tick}
        for f in FIELDS:
            s = values.get(track_name(pawn, f))
            r[f] = s["v"] if s and s.get("st") == "ok" else None
        if last is not None and last["tick"] == tick:
            rows[-1] = r
        else:
            rows.append(r)
        last = r
    for r in rows:
        if isinstance(r["lerp"], float):
            r["lerp"] = int(r["lerp"])
        if isinstance(r["start"], float):
            r["start"] = int(r["start"])
    return rows


def judge_trace(rows, kinds):
    """rows: a kept scene_trace_v1; kinds: {pawn id: kind}. -> {"outcome", "birds"}"""
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
    import scene_judge
    tr = scene_judge.Trace(rows)
    frames = list(tr.frames())
    birds = {p: judge_bird(series_from_frames(frames, p), k) for p, k in kinds.items()}
    return {"outcome": outcome(birds), "birds": birds}


# ---------------------------------------------------------------------------------------------- the asset audit
def kind_of(def_name, src=None):
    """-> {"prefix", "female", "frames", "tpf", "mod"} of one PawnKindDef of ours, or None. Reads src/**/Defs XML; a value
    inherited through ParentName is not followed (none of ours inherits these fields on 2026-11-24)."""
    src = src or os.path.join(REPO, "src")
    for root, _d, files in os.walk(src):
        if "Defs" not in root.split(os.sep):
            continue
        for fn in files:
            if not fn.endswith(".xml"):
                continue
            p = os.path.join(root, fn)
            try:
                tree = ET.parse(p).getroot()
            except ET.ParseError:
                continue
            for el in tree.iter():
                if el.findtext("defName") == def_name and el.find("flyingAnimationFramePathPrefix") is not None:
                    fem = el.findtext("flyingAnimationFramePathPrefixFemale")
                    return {"prefix": el.findtext("flyingAnimationFramePathPrefix").strip(),
                            "female": fem.strip() if fem is not None and fem.strip() else None,
                            "frames": _game_int(el, "flyingAnimationFrameCount"),
                            "tpf": _game_int(el, "flyingAnimationTicksPerFrame"), "mod": _mod_root(p)}
    return None


# PawnKindDef's own field defaults (RimWorld 1.6): an unset field reads what the game reads, and the audit names it
GAME_DEFAULT = {"flyingAnimationFrameCount": 0, "flyingAnimationTicksPerFrame": -1}


def _game_int(el, tag):
    t = el.findtext(tag)
    return GAME_DEFAULT[tag] if t is None else int(t.strip())


def _mod_root(path):
    d = os.path.dirname(path)
    while os.path.basename(os.path.dirname(d)) not in ("RimMandrake", "RimStarWars", "RimUtinni"):
        if os.path.dirname(d) == d:
            return None
        d = os.path.dirname(d)
    return d


def audit(kind, textures_roots):
    """-> the frame textures the game will ask for and no root holds: '<prefix><i>_<facing>.png', every frame, every
    facing the generator makes (east, north, south; west mirrors east), and the female set when there is one."""
    missing = []
    for prefix in [kind["prefix"]] + ([kind["female"]] if kind.get("female") else []):
        for i in range(1, kind["frames"] + 1):
            for facing in ("east", "north", "south"):
                rel = "%s%d_%s.png" % (prefix, i, facing)
                if not any(os.path.isfile(os.path.join(r, rel)) for r in textures_roots):
                    missing.append(rel)
    if kind["frames"] < 1 or kind.get("tpf", 1) < 1:
        missing.append("%s: flyingAnimationFrameCount %s, ticksPerFrame %s" % (kind["prefix"], kind["frames"], kind.get("tpf")))
    return missing


def textures_roots(mod):
    out = []
    for root, dirs, _f in os.walk(mod):
        if "Textures" in dirs:
            out.append(os.path.join(root, "Textures"))
    return out


def main(argv):
    if not argv or argv[0] not in ("audit", "judge"):
        print(__doc__)
        return 2
    if argv[0] == "audit":
        names = argv[1:]
        if not names:
            sys.path.insert(0, os.path.join(HERE, "art"))
            import selftest_flier_frames_present as present
            return present.main()
        bad = 0
        for nm in names:
            k = kind_of(nm)
            if k is None:
                print("FAIL %s: no PawnKindDef of ours sets a flip-book" % nm)
                bad += 1
                continue
            miss = audit(k, textures_roots(k["mod"]))
            bad += bool(miss)
            print("%s %s: %d frames x 3 facings, %s" % ("FAIL" if miss else "PASS", nm, k["frames"],
                                                       ("missing " + ", ".join(miss)) if miss else "all present"))
        return 1 if bad else 0
    path, kinds = argv[1], {}
    for a in argv[2:]:
        pawn, _, kd = a.partition("=")
        k = kind_of(kd)
        if k is None:
            print("no PawnKindDef of ours named %s sets a flip-book" % kd)
            return 2
        kinds[pawn] = k
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    res = judge_trace(rows, kinds)
    print(json.dumps(res, indent=1, sort_keys=True))
    return {"SUCCESS": 0, "MOD FAILURE": 1}.get(res["outcome"], 3)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
