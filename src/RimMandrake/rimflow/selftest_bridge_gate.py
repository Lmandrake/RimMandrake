#!/usr/bin/env python3
"""model.bridge_gate: the check a game-touching tool (modset_builder --apply/--restore) runs first.
BRIDGE_LOCK_CROSS_CLONE_RACE_1 part 2: a tier swap from a window not holding the bridge rewrote the
other window's next load. Runs on a throwaway ledger and shared-lock file; touches nothing real."""
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
                    RIMFLOW_SHARED_BRIDGE=os.path.join(tmp, "shared.json"), RIMFLOW_PROBE="no-reading")

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
        # another clone holds it live: refused even though this ledger says FOUNDRY
        with open(os.path.join(tmp, "shared.json"), "w") as f:
            json.dump({"holder": "BENCH", "since": "x", "touched": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()), "clone": "/b"}, f)
        g = gate("FOUNDRY")
        check(g.startswith("REFUSE") and "another clone" in g, "a live hold in another clone refuses the local holder: " + g)
        with open(os.path.join(tmp, "shared.json"), "w") as f:
            json.dump({"holder": "BENCH", "since": "x", "touched": "2020-01-01T00:00:00Z", "clone": "/b"}, f)
        check(gate("FOUNDRY") == "PASS", "a stale hold in another clone does not")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
