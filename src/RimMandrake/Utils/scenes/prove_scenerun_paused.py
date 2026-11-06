"""Live proof of SCENERUN_MIGRATE_OFF_UNPAUSED_PLAY: scenelib.run advances paused and exactly, and a scene's verdict
reads do not change. Run from the repo root under python.exe (or python3 with the bridge reachable):

    python.exe src/RimMandrake/Utils/scenes/prove_scenerun_paused.py exact      # A1
    python.exe src/RimMandrake/Utils/scenes/prove_scenerun_paused.py verdicts   # A2 (needs mandrake.rm.luminouspigment)

A1: on the current map, S.run(600) moves ticksGame by exactly 600 and the game reads paused before and after.
A2: the tank_control scene (scenarios.py) is staged twice on the same rect, once advanced with the OLD unpaused
    play_for run (scenelib._run_play, the reference arm) and once with the new paused run. Its discrete verdict reads
    must match: the glow tank's Glows at every read, whether it has a power net, and GlowRadius within 0.5 cells.
Exit 0 PASS, 1 FAIL, 2 UNMEASURED (the reason on the same line). The verdict line is printed last."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "modcheck"))
from scenes import scenelib as S  # noqa: E402
import clockgate as cg  # noqa: E402

N = 600


def verdict(code, line):
    print(line)
    sys.stdout.flush()
    sys.exit(code)


def paused():
    return S.call("jawa/time_clock").get("paused")


def exact():
    t0, p0 = S.ticks(), paused()
    if not t0 or p0 is None:
        verdict(2, "UNMEASURED: no game clock (ticksGame %r, paused %r)" % (t0, p0))
    try:
        d = S.run(N)
    except (RuntimeError, cg.GovernorStop) as e:
        if isinstance(e, S.rb.RimBridgeError):
            verdict(2, "UNMEASURED: bridge error during the advance: %s" % str(e)[:200])
        verdict(1, "FAIL A1: S.run raised: %s" % str(e)[:200])
    t1, p1 = S.ticks(), paused()
    row = dict(id="A1", requested=N, delta=t1 - t0, returned=d, pausedBefore=p0, pausedAfter=p1)
    print("ROW " + json.dumps(row))
    if t1 - t0 == N and p1 is True:
        verdict(0, "PASS A1: ticksGame moved by exactly %d and the game reads paused" % N)
    verdict(1, "FAIL A1: delta %d of %d, pausedAfter %r" % (t1 - t0, N, p1))


def tank_scene(adv):
    """tank_control's staging and reads, advanced by `adv`; -> the discrete reads. Staging's own sc.fuel wait uses
    S.run in both arms: only the scene's measured advances differ."""
    with S.Scene("scenerun_tank", 40, 40, 12, 10) as sc:
        sc.room(); sc.grid(); sc.put("RM_GlowTank", 5, 5)
        pid = sc.colonist(8, 8); sc.fuel(pid, n=75, ticks=1500)
        sc.put("RM_CrowncarpetFresh", 2, 8); tk = sc.find("RM_GlowTank")
        if not tk:
            return None
        sc.order(pid, "Refuel", a=tk["id"], b=sc.find("RM_CrowncarpetFresh")["id"], count=1); adv(1200)
        reads = []
        for _ in range(4):
            reads.append(sc.comp("RM_GlowTank", "Glower", "GlowRadius,Glows")); adv(500)
        net = sc.netsize("RM_GlowTank")
        return dict(reads=reads, hasNet=bool(net))


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def verdicts():
    try:
        old = tank_scene(lambda n: S._run_play(n))
    except Exception as e:  # noqa: BLE001 - the reference arm could not run: nothing to compare against
        verdict(2, "UNMEASURED: reference play_for arm did not run: %s" % str(e)[:200])
    try:
        new = tank_scene(S.run)
    except (RuntimeError, cg.GovernorStop) as e:   # RimBridgeError is a RuntimeError: tell it from the run's own refusal
        if isinstance(e, S.rb.RimBridgeError):
            verdict(2, "UNMEASURED: bridge error in the paused arm: %s" % str(e)[:200])
        verdict(1, "FAIL A2: the paused run raised: %s" % str(e)[:200])
    except Exception as e:  # noqa: BLE001
        verdict(2, "UNMEASURED: paused arm did not stage: %s" % str(e)[:200])
    if old is None or new is None:
        verdict(2, "UNMEASURED: RM_GlowTank did not spawn (mandrake.rm.luminouspigment not loaded?)")
    print("ROW " + json.dumps(dict(id="A2", old=old, new=new), default=str))
    bad = []
    if old["hasNet"] != new["hasNet"]:
        bad.append("hasNet %s vs %s" % (old["hasNet"], new["hasNet"]))
    for i, (a, b) in enumerate(zip(old["reads"], new["reads"])):
        a, b = a or {}, b or {}
        if str(a.get("Glows")) != str(b.get("Glows")):
            bad.append("read %d Glows %s vs %s" % (i, a.get("Glows"), b.get("Glows")))
        ra, rb = _num(a.get("GlowRadius")), _num(b.get("GlowRadius"))
        if ra is None or rb is None:
            verdict(2, "UNMEASURED: GlowRadius unreadable (read %d: %r / %r)" % (i, a, b))
        if abs(ra - rb) > 0.5:
            bad.append("read %d GlowRadius %.2f vs %.2f" % (i, ra, rb))
    if bad:
        verdict(1, "FAIL A2: the paused arm diverged from play_for: " + "; ".join(bad))
    verdict(0, "PASS A2: tank_control reads match between play_for and the paused run (4 reads, net)")


if __name__ == "__main__":
    fn = {"exact": exact, "verdicts": verdicts}.get((sys.argv[1:] or [""])[0])
    if fn is None:
        verdict(2, "UNMEASURED: usage prove_scenerun_paused.py exact|verdicts")
    try:
        fn()
    except (OSError, ConnectionError, RuntimeError) as e:   # RimBridgeError included: an unreachable or failed bridge
        verdict(2, "UNMEASURED: bridge unreachable: %s" % str(e)[:200])
