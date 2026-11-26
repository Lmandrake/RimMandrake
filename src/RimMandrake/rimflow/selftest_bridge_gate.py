#!/usr/bin/env python3
"""model.bridge_gate: the check a game-touching tool (modset_builder --apply/--restore) runs first.
BRIDGE_LOCK_CROSS_CLONE_RACE_1 part 2: a tier swap from a window not holding the bridge rewrote the
other window's next load. Game a is judged by its driver lock, the one record (game_lock.py); a machine with no lock
(the Mac) by the ledger. Runs on a throwaway ledger and lock; touches nothing real."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "cli.py")
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    tmp = tempfile.mkdtemp(prefix="rf_gate_")
    try:
        os.makedirs(os.path.join(tmp, "items"))
        base = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")}
        base.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(tmp, "items"),
                    RIMFLOW_PROBE="no-reading")

        def gate(seat):
            e = dict(base)
            if seat:
                e["RIMFLOW_SEAT"] = seat
            code = ("import sys; sys.path.insert(0, %r); from rimflow import model as m; "
                    "r = m.bridge_gate(m.ambient_window_seat()); print('PASS' if r is None else 'REFUSE ' + r)"
                    % os.path.dirname(HERE))
            return subprocess.run([sys.executable, "-c", code], env=e, capture_output=True, text=True).stdout.strip()

        def rf(seat, *args):
            e = dict(base, RIMFLOW_SEAT=seat)
            return subprocess.run([sys.executable, CLI] + list(args), env=e, capture_output=True, text=True)

        check(gate(None) == "PASS", "the owner (no window seat) always passes")
        check(gate("FOUNDRY").startswith("REFUSE") and "does not hold" in gate("FOUNDRY"), "a window with a free bridge is refused")
        rf("FOUNDRY", "bridge", "take", "--for", "swap")
        check(gate("FOUNDRY") == "PASS", "the holder passes")
        check(gate("BENCH").startswith("REFUSE"), "the other window is refused while FOUNDRY holds it")
        # with game a's lock (Archmagi): the lock decides, never the ledger. This test's own process is the live holder
        lock = os.path.join(tmp, "DRIVER_LOCK.json")
        base.update(RIMFLOW_DRIVER_LOCK=lock, RM_HOST="archmagi", RM_DRIVER_PID=str(os.getpid()))
        base.pop("RM_GAME_INSTANCE", None)
        check(gate("FOUNDRY").startswith("REFUSE") and "nobody" in gate("FOUNDRY"),
              "lock: the ledger's FOUNDRY take is not a hold while game a's lock is free: " + gate("FOUNDRY"))
        r = rf("FOUNDRY", "bridge", "take", "--for", "swap")
        check(r.returncode == 0 and gate("FOUNDRY") == "PASS", "lock: the holder passes: " + gate("FOUNDRY"))
        g = gate("BENCH")
        check(g.startswith("REFUSE") and "FOUNDRY" in g, "lock: the other window is refused, naming the holder: " + g)
        with open(lock) as f:
            cur = json.load(f)
        with open(lock, "w") as f:           # another clone's live take (same process here, another seat)
            json.dump(dict(cur, seat="BENCH", clone="/b"), f)
        g = gate("FOUNDRY")
        check(g.startswith("REFUSE") and "BENCH" in g, "lock: a live hold from another clone refuses this ledger's holder: " + g)
        with open(lock, "w") as f:           # its process has ended: free at once, for every seat
            json.dump(dict(cur, seat="BENCH", identity=dict(cur["identity"], pid=999999, start=1.0)), f)
        g = gate("BENCH")
        check(g.startswith("REFUSE") and "nobody" in g, "lock: a holder whose process is gone holds nothing: " + g)
        with open(lock, "w") as f:
            f.write("{not json")
        g = gate("FOUNDRY")
        check(g.startswith("REFUSE") and "could not look" in g, "lock: an unreadable lock refuses (never free): " + g)
        archsmall_by_its_lock(tmp, base)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


def archsmall_by_its_lock(tmp, base):
    """RIMMANDRAKE_GATE_ARCHSMALL_TIER_SWAP_ON_DRIVER_LOCK_NOT_LEDGER: ArchSmall (archmagi.b) is judged by its own driver
    lock, the one record, as ArchBig is. Seen 2026-11-25: `game_lock.py run ArchSmall -- drive.sh` held the lock, the
    ledger's archmagi.b entry read nobody, and modset_builder's tier swap inside the hold was refused."""
    env = {k: v for k, v in base.items() if k not in ("RIMFLOW_DRIVER_LOCK",)}
    env.update(RM_INSTANCES_ROOT=os.path.join(tmp, "instances"), RM_HOST="archmagi", RM_DRIVER_PID=str(os.getpid()),
               RM_GAME_INSTANCE="b")
    os.makedirs(os.path.join(tmp, "instances", "b"), exist_ok=True)
    lock = os.path.join(tmp, "instances", "b", "DRIVER_LOCK.json")
    root = os.path.dirname(HERE)

    def gate(seat):
        code = ("import sys; sys.path.insert(0, %r); from rimflow import model as m; "
                "r = m.bridge_gate(%r, m.ambient_bridge_host()); print('PASS' if r is None else 'REFUSE ' + r)"
                % (root, seat))
        p = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
        return (p.stdout.strip() or p.stderr.strip()[-300:])

    g = gate("BENCH")
    check(g.startswith("REFUSE") and "nobody" in g, "ArchSmall: a free lock and an empty ledger entry refuse: " + g)
    code = ("import sys; sys.path.insert(0, %r); import game_lock as gl; r = gl.claim('b', 'tier swap', seat='BENCH'); "
            "print(r.get('ok'), r.get('line'))" % HERE)
    p = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    check(p.stdout.startswith("True") and os.path.exists(lock),
          "ArchSmall: the test claims game b's lock: " + (p.stdout + p.stderr).strip()[-300:])
    g = gate("BENCH")
    check(g == "PASS", "ArchSmall: the lock's live holder passes while the ledger's archmagi.b entry reads nobody: " + g)
    g = gate("FOUNDRY")
    check(g.startswith("REFUSE") and "BENCH" in g, "ArchSmall: another seat is refused, naming the lock's holder: " + g)
    with open(lock) as f:
        cur = json.load(f)
    with open(lock, "w") as f:           # its process has ended: free at once
        json.dump(dict(cur, identity=dict(cur["identity"], pid=999999, start=1.0)), f)
    g = gate("BENCH")
    check(g.startswith("REFUSE") and "nobody" in g, "ArchSmall: a holder whose process is gone holds nothing: " + g)
    with open(lock, "w") as f:
        f.write("{not json")
    g = gate("BENCH")
    check(g.startswith("REFUSE") and "could not look" in g, "ArchSmall: an unreadable lock refuses (never free): " + g)
    os.remove(lock)
    # another machine's game: still judged by its ledger entry
    code = ("import sys; sys.path.insert(0, %r); from rimflow import model as m; r = m.bridge_gate('BENCH', 'stevedesktop.b'); "
            "print('PASS' if r is None else 'REFUSE ' + r)" % root)
    g = subprocess.run([sys.executable, "-c", code], env=dict(base, RM_HOST="archmagi"), capture_output=True,
                       text=True).stdout.strip()
    check(g.startswith("REFUSE") and "stevedesktop.b" in g, "Steve2 is still judged by its ledger entry: " + g)


if __name__ == "__main__":
    sys.exit(main())
