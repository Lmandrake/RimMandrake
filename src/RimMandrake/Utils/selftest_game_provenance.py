#!/usr/bin/env python3
"""selftest_game_provenance.py — `./game`'s provenance flags reach their own event fields.

    python3 src/RimMandrake/Utils/selftest_game_provenance.py

Owner, by card 2026-10-11: his words, his card clicks, a standing ruling cited by
reference and the agent's own reason each get their own field. `./game` exports them as
RIMFLOW_OWNER_SAID / RIMFLOW_WHY / RIMFLOW_BY_CARD / RIMFLOW_PER_RULING and
`broadcast.record_game` forwards them to `rimflow game`. This drives that forwarding
against a throwaway ledger (RIMFLOW_LEDGER redirected), and drives `./game`'s own flag
parser up to the point it would announce. Sends nothing.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import broadcast  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("ok    " if cond else "FAIL  ") + name + ("" if cond else "\n        " + str(detail)))
    if not cond:
        FAIL.append(name)


def events(tmp):
    out = []
    for root, _, files in os.walk(tmp):
        for f in files:
            if f.endswith(".jsonl"):
                with open(os.path.join(root, f), encoding="utf-8") as fh:
                    out += [json.loads(l) for l in fh if l.strip()]
    return [e for e in out if e.get("event") == "game"]


def main():
    tmp = tempfile.mkdtemp(prefix="game_prov_")
    keep = {k: os.environ.get(k) for k in ("RIMFLOW_LEDGER", "RIMFLOW_ITEMS", "RIMFLOW_PROBE",
                                           "RIMFLOW_OWNER_SAID", "RIMFLOW_WHY",
                                           "RIMFLOW_BY_CARD", "RIMFLOW_PER_RULING",
                                           "RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")}
    try:
        os.makedirs(os.path.join(tmp, "items"))
        for k in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID"):
            os.environ.pop(k, None)
        os.environ.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"),
                          RIMFLOW_ITEMS=os.path.join(tmp, "items"), RIMFLOW_PROBE="no-reading",
                          RIMFLOW_OWNER_SAID="", RIMFLOW_BY_CARD="",
                          RIMFLOW_WHY="FOUNDRY restart to load the new DLL",
                          RIMFLOW_PER_RULING="REBOOT_IS_OURS_RULING")
        err = broadcast.record_game("DOWN", "Game is down")
        evs = events(tmp)
        check("record_game stamps the event", err is None and len(evs) == 1, (err, evs))
        ev = evs[-1] if evs else {}
        check("--why lands in `why`, never in `ownerSaid`",
              ev.get("why") == "FOUNDRY restart to load the new DLL" and "ownerSaid" not in ev, ev)
        check("--per-ruling lands in `perRuling`", ev.get("perRuling") == "REBOOT_IS_OURS_RULING", ev)

        os.environ.update(RIMFLOW_WHY="", RIMFLOW_PER_RULING="", RIMFLOW_BY_CARD="Restart now")
        broadcast.record_game("UP", "Game is up")
        ev = events(tmp)[-1]
        check("--by-card lands in `byCard`", ev.get("byCard") == "Restart now"
              and "ownerSaid" not in ev, ev)

        # ./game's parser: a flag with no state after it is refused before anything runs.
        p = subprocess.run(["bash", os.path.join(REPO, "game"), "--why", "x"],
                           capture_output=True, text=True, cwd=REPO, timeout=30)
        check("./game --why with no state is refused", p.returncode == 2
              and "then the state" in p.stderr, (p.returncode, p.stderr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    print("\n%d failed" % len(FAIL) if FAIL else "\nall passed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
