#!/usr/bin/env python3
"""knockback_runner.py - in-game runner scenes for Explosive Knockback (design §8.2).

    python.exe src\\RimMandrake\\ExplosiveKnockback\\knockback_runner.py [--scenes a,b,...] [--ticks 300] [--real-seconds 0]

Needs python.exe (the bridge binds Windows loopback), a running game with a SCRATCH map (each scene clears a 15x15
patch), and the mod loaded (FlowWorks too, for the pit scenes). Per scene: jawa/static_call
RimMandrake.ExplosiveKnockback.RM_KnockbackProof.Stage("<scene>,x,z") builds it and sets the blast off,
advance_scene moves the clock --ticks without unpausing (jawa/safe_advance chunks via tickburst_step.advance, looped
past halts to the target tick; a short advance is INVALID, never a verdict read early), then .Verdict("<scene>") reads the knockback JOURNAL plus
map state and returns PASS/FAIL/INVALID/ERROR. The verdict is the game's; this script only records it, plus the
journal, to Transient/explosive_knockback/run_<stamp>.jsonl. Exit 0 only when every scene PASSed.
"""
import argparse
import datetime
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
sys.path.insert(0, HERE)

PROOF = "RimMandrake.ExplosiveKnockback.RM_KnockbackProof"
SETTINGS = "RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings"
ADVANCE_TRIES = 12          # tickburst_step.advance calls per scene, each resumed from the game clock, before giving up


def parse_verdict(text):
    """'PASS name detail...' -> (status, name, detail). Anything else is ERROR."""
    t = str(text or "").strip()
    head = t.split(" ", 2)
    if head and head[0] in ("PASS", "FAIL", "INVALID", "ERROR", "STAGED"):
        return head[0], head[1] if len(head) > 1 else "", head[2] if len(head) > 2 else ""
    return "ERROR", "", t


def overall(rows):
    if not rows:
        return "INCOMPLETE"
    st = [r["status"] for r in rows]
    if "FAIL" in st or "ERROR" in st:
        return "FAIL"
    if "INVALID" in st:
        return "INVALID"
    return "PASS"


def snapshot_settings(b):
    """Every RimMandrakeExplosiveKnockbackSettings field's current value, read before Settings("reset") wipes them."""
    from validation import settings_fields
    snap = {}
    for f in sorted(settings_fields()):
        r = b.call("jawa/mod_settings_field", {"typeName": SETTINGS, "action": "get", "field": f})
        if isinstance(r, dict) and r.get("success", True) is not False and "value" in r:
            snap[f] = r["value"]
    return snap


def settings_off(base, now):
    """{field: [baseline, now]} for every field whose value differs from the run's baseline, the fields one side could not
    read as [baseline or "UNREAD", now or "UNREAD"] (RIMMANDRAKE_HUNT_KNOCKBACK_GOOD_UNMOVED_LONG_BATCH_THREE_SIGHTINGS: a
    value a scene left off its default would spoil the next scene of the same process)."""
    out = {}
    for f in sorted(set(base) | set(now)):
        a, b = base.get(f, "UNREAD"), now.get(f, "UNREAD")
        if str(a) != str(b):
            out[f] = [a, b]
    return out


def restore_settings(b, snap):
    """Put the player's values back (the run's finally): a failed write is printed, never raised over the verdict."""
    for f, v in snap.items():
        try:
            r = b.call("jawa/mod_settings_field", {"typeName": SETTINGS, "action": "set", "field": f, "value": str(v)})
            ok = isinstance(r, dict) and bool(r.get("success"))
        except Exception as ex:                                  # noqa: BLE001 - restoring never masks the verdict
            r, ok = "%s: %s" % (type(ex).__name__, ex), False
        if not ok:
            print("SETTING RESTORE FAILED %s -> %r: %r" % (f, v, r), file=sys.stderr)


def _clock(sess):
    """ticksGame from jawa/safe_advance status, or None (an old companion, or a reply without it)."""
    try:
        r = sess.call("jawa/safe_advance", action="status")
        r = r.get("result", r) if isinstance(r, dict) and "ticksGame" not in r else r
        return int(r.get("ticksGame"))
    except Exception:                                            # noqa: BLE001 - unmeasured, the caller counts ticks
        return None


def advance_scene(b, ticks, tries=ADVANCE_TRIES):
    """Move the clock `ticks` paused and return {reached, target, ticksGame, halts, path, wallS}.

    RIMMANDRAKE_ADVANCE_PIT_FETCH_PAST_ONE_TICK_A_FRAME: every step goes through tickburst_step.advance (jawa/safe_advance,
    <=2500-tick chunks, stopOn=cancel; 60000 ticks measured 129 s in visit 1, where one tick a frame needs ~17 min). A
    chunk that stops (a mental break, a refusal) ends that call; the loop resumes from the game clock until the target
    tick, and stops early when a call moves nothing. Without a clock reading it counts the ticks each call reports."""
    import tickburst_step as TS
    t0 = time.time()
    sess = TS._GateSession(lambda tool, **kw: b.call(tool, kw, check=False))
    start = _clock(sess)
    target = start + ticks if start is not None else None
    done, halts, path, now = 0, [], None, start
    for _ in range(max(1, tries)):
        left = (target - now) if target is not None and now is not None else ticks - done
        if left <= 0:
            break
        r = TS.advance(sess.call, left, session=sess, force_fast=True)
        path = r.get("path") or path
        moved = int(r.get("completedTicks") or 0)
        before, now = now, _clock(sess)
        if now is not None and before is not None:
            moved = now - before
        done += moved
        if r.get("status") != "completed":
            halts.append(str(r.get("error") or r.get("status")))
        if moved <= 0:
            break
    left = (target - now) if target is not None and now is not None else ticks - done
    return {"reached": left <= 0, "target": target, "ticksGame": now, "advanced": done, "halts": halts, "path": path,
            "wallS": round(time.time() - t0, 1)}


def call(b, method, arg):
    r = b.call("jawa/static_call", {"type": PROOF, "method": method, "args": arg})
    if isinstance(r, dict):
        return str(r.get("result", r.get("value", r)))
    return str(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenes", default="")
    ap.add_argument("--ticks", type=int, default=300)
    ap.add_argument("--real-seconds", type=float, default=0.0,
                    help="wait this long in real time after staging (frame-time scenes run unpaused: use --ticks 0)")
    ap.add_argument("--out", default=os.path.join(REPO, "Transient", "explosive_knockback"))
    a = ap.parse_args()
    from rimbridge_client import RimBridge, resolve_endpoint
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from proof_build_gate import require_proof_build
    host, port, token = resolve_endpoint()
    os.makedirs(a.out, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    path = os.path.join(a.out, "run_%s.jsonl" % stamp)
    rows = []
    with RimBridge(host=host, port=port, token=token) as b:
        names = call(b, "Names", "x")
        require_proof_build(names)          # release DLL: exit 3 PROOF BUILD REQUIRED, never a table of FAILs
        print("scenes available:", names)
        scenes = [s for s in (a.scenes.split(",") if a.scenes else names.split(" ")[0].split(",")) if s]
        origins = call(b, "Origins", str(len(scenes))).split(";")
        if len(origins) < len(scenes):
            print("map too small for %d scenes (%d origins)" % (len(scenes), len(origins)))
            return 2
        # reset puts every field at its default for the scenes; the player's own values come back in the finally,
        # even when a scene throws or the bridge drops mid-run (PROOF_SCENE_RESTORE_LEAK sweep 2026-10-26)
        snap = snapshot_settings(b)
        try:
            call(b, "Settings", "reset")
            call(b, "Clear", "x")
            base = snapshot_settings(b)     # the defaults every scene starts from; each verdict is followed by a read against it
            for name, org in zip(scenes, origins):
                staged = call(b, "Stage", "%s,%s" % (name, org))
                st, _, detail = parse_verdict(staged)
                if st != "STAGED":
                    rows.append({"type": "scenario", "scene": name, "status": st, "detail": detail, "origin": org})
                    print("%-16s %s %s" % (name, st, detail))
                    continue
                adv = None
                if a.ticks > 0:
                    adv = advance_scene(b, a.ticks)
                    print("%-16s advanced %d/%d ticks in %.0f s via %s%s" % (
                        name, adv["advanced"], a.ticks, adv["wallS"], adv["path"],
                        (", %d halt(s)" % len(adv["halts"])) if adv["halts"] else ""))
                if a.real_seconds > 0:
                    time.sleep(a.real_seconds)
                st, _, detail = parse_verdict(call(b, "Verdict", name))
                if adv is not None and not adv["reached"] and st != "ERROR":
                    st, detail = "INVALID", "advance short (%d of %d ticks; %s); verdict was %s %s" % (
                        adv["advanced"], a.ticks, "; ".join(adv["halts"][-2:]) or "no halt reported", st, detail)
                off = settings_off(base, snapshot_settings(b))
                rows.append({"type": "scenario", "scene": name, "status": st, "detail": detail, "origin": org,
                             "advance": adv, "settings_off_after": off})
                print("%-16s %s %s" % (name, st, detail))
                print("%-16s SETTINGS after verdict: %s" % (name, json.dumps(off) if off else "all at the run's defaults"))
            journal = call(b, "Journal", "4000")
        finally:
            restore_settings(b, snap)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
        for line in journal.splitlines():
            if line.strip().startswith("{"):
                f.write(json.dumps({"type": "journal", "rec": line.strip()}) + "\n")
        v = overall(rows)
        f.write(json.dumps({"type": "run_end", "verdict": v, "scenes": len(rows)}) + "\n")
    print("VERDICT %s  (%d scenes) -> %s" % (v, len(rows), path))
    return 0 if v == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
