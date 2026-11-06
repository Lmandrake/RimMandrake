#!/usr/bin/env python3
"""The metronome's chores phase (OPS_METRONOME_MIGRATE_CLOCKS_FENCED; strategy §8 step 6): the beat owns the CLOCK of
each chore and starts its existing oneshot service, on the old cadence, without waiting for it.

Why it starts the service instead of running the command inside the beat: measured from the journal over 48 h
(2026-11-06), account_usage poll runs p50 19 s, p95 35 s, max 52 s and account-plan up to 29 s, against the phase's
10 s limit; a kill would land mid-poll or mid-switch. The units keep their own limits, environment and drop-ins
(account-plan's week.conf), systemd keeps one run at a time, and a failed run is a failed unit, as under the old timer.

    metronome_chores.py run --metronome-gen N --chore rm-scratch-pressure:600 --chore rm-account-usage:900 ...

Fenced like every owning phase: nothing starts unless metronome.may_act says generation N is live (exit 3). A chore
whose start was refused is not marked started, so the next beat tries again (exit 1 now). The last-start times live
in chores_state.json in the metronome's state directory; a torn file makes every chore due, which is harmless because
each is a cheap idempotent pass.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metronome  # noqa: E402

PHASE = "chores"
EXIT_FENCED = 3
START_TIMEOUT_S = 3
# The phase wakes on whole beats, so an interval compared exactly would slip a whole phase period whenever a beat ran
# a little early: a 300 s chore would run every other wake.
SLACK_S = 30


def parse_chore(text):
    name, sep, every = text.rpartition(":")
    if not sep or not name or name.endswith((".service", ".timer")) or not every.isdigit() or int(every) <= 0:
        raise argparse.ArgumentTypeError("--chore wants <unit without suffix>:<seconds>, got %r" % text)
    return name, int(every)


def read_state(path):
    try:
        got = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(got, dict):
        return {}
    return {k: v for k, v in got.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}


def due(chore_every, last, now, slack=SLACK_S):
    """A chore never started is due; so is one whose stamp is in the future (a wrong clock must not stop it for good)."""
    if last is None or last > now:
        return True
    return now - last >= chore_every - slack


def start_unit(name, runner=subprocess.run):
    """(ok, why). --no-block: queue the start and return, the unit's run is not the beat's."""
    try:
        r = runner(["systemctl", "--user", "start", "--no-block", name + ".service"],
                   capture_output=True, text=True, timeout=START_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    return r.returncode == 0, (r.stderr or "").strip()[:200] or "exit %d" % r.returncode


def write_state(path, state):
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(state, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def run_pass(mdir, gen, chores, now=None, runner=subprocess.run):
    """-> exit code. Checks the fence before every start: a beat that lost ownership starts nothing further."""
    now = time.time() if now is None else now
    path = Path(mdir) / "chores_state.json"
    state = read_state(path)
    code = 0
    for name, every in chores:
        if not due(every, state.get(name), now):
            continue
        live, why = metronome.may_act(Path(mdir), PHASE, gen)
        if not live:
            print("metronome_chores: fenced before %s: %s" % (name, why))
            return EXIT_FENCED
        ok, why = start_unit(name, runner)
        if ok:
            state[name] = now
            write_state(path, state)   # at once: a kill after this start must not start it again next beat
            print("metronome_chores: started %s" % name)
        else:
            print("metronome_chores: could not start %s: %s" % (name, why))
            code = 1
    return code


def main(argv=None, runner=subprocess.run):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["run"])
    ap.add_argument("--metronome-gen", type=int, required=True, help="the metronome's ownership generation")
    ap.add_argument("--chore", action="append", type=parse_chore, required=True, metavar="UNIT:SECONDS")
    a = ap.parse_args(argv)
    return run_pass(metronome.state_dir(os.environ.get("METRONOME_DIR")), a.metronome_gen, a.chore, runner=runner)


if __name__ == "__main__":
    sys.exit(main())
