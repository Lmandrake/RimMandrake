#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_FILE_OWED_WHERE_RUNS_PARK_FOR_THE_CONDUCTOR (spec:
design/specs/2026-11-15-conductor-restart-loses-nothing.md §3 E3 as narrowed by §4, and §5 ticket 4). Written by the
filing seat; the builder does not edit it (a wrong clause goes to the Conductor).

    python3 src/RimMandrake/rimflow/acceptance/owed_sources_accept.py      # exit 0 and "PASS 10/10" when built

THE CONTRACT
  `python3 src/RimMandrake/rimflow/owed.py sync-sources [--maturation-json F] [--detached-dir D]` files one
  `kind: owed` item for the Conductor (`--for BENCH`) for each explicit Conductor hand step the programs already name,
  and nothing else:
    - a maturation status row (the dicts `maturation.py status --json` prints; F holds a JSON list of them) whose
      `next` says the Conductor decides ("PAUSED: three cycles, the Conductor decides") or that a card goes to him
      ("OWNER, a card in the Conductor log"); key `maturation:<mod>@<version>:<stage>:visit<blind.visit or 0>`
    - a detached run record (`D/*.json`, not `*.out.json`) carrying `owed_close` whose item is still open; key
      `detached:<unit>`; `--caused-by` the run's item
  The key is written into the owed item's title or why, and a key already filed (open or closed) is never filed again,
  also when two sync-sources run at once (serialized through the ledger writer). Each new filing prints `FILED <ID>`.
  Defaults read the live maturation status and /mnt/d/ClaudeWork/rimmandrake/dispatcher/detached; the Dispatcher tick
  runs it (src/RimMandrake/rimflow/dispatcher.py calls `sync-sources` or `owed.sync_sources`), so no window has to be
  alive when the result lands.
"""
import glob
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RIMFLOW, "..", "..", ".."))
sys.path.insert(0, RIMFLOW)
CLI = os.path.join(RIMFLOW, "cli.py")
OWED = os.path.join(RIMFLOW, "owed.py")
TOTAL = 10
RESULTS = []


def check(ok, what):
    RESULTS.append((bool(ok), what))


def main():
    tmp = tempfile.mkdtemp(prefix="owed_sources_")
    items = os.path.join(tmp, "items")
    os.makedirs(items)
    det = os.path.join(tmp, "detached")
    os.makedirs(det)
    base = {k: v for k, v in os.environ.items() if not k.startswith("RIMFLOW_")}
    base.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=items, RIMFLOW_SEAT="BENCH",
                RIMFLOW_PROBE="no-reading", PYTHONDONTWRITEBYTECODE="1")

    def cli(*a):
        return subprocess.run([sys.executable, CLI] + list(a) + ["--why", "acceptance sandbox"], cwd=REPO, env=base,
                              capture_output=True, text=True, timeout=120)

    x = "RIMMANDRAKE_FIX_SANDBOX_GAPS_ITEM_LEFT_OPEN"
    y = "RIMMANDRAKE_FIX_SANDBOX_GAPS_ITEM_CLOSED_BY_HAND"
    cli("file", x, "--for", "BENCH", "--title", "open after a success", "--kind", "task")
    cli("file", y, "--for", "BENCH", "--title", "closed by hand", "--kind", "task")
    cli("close", y, "--no-code", "closed by hand in the sandbox at 4:00 PM PST")
    rows = [
        {"mod": "GimmeSomeSlack", "version": "0.1.0", "stage": "blind_challenge", "hand_steps": [],
         "blind": {"visit": 3, "cycle": 3}, "next": "NEXT (PAUSED: three cycles, the Conductor decides): bring the "
         "Conductor the three cycles' findings; then maturation.py advance GimmeSomeSlack --to offline_build"},
        {"mod": "ExplosiveKnockback", "version": "0.1.0", "stage": "his_walk", "hand_steps": ["owner_said"],
         "blind": None, "next": "NEXT (OWNER, a card in the Conductor log): his walk ends with his words"},
        {"mod": "FlowWorks", "version": "0.1.0", "stage": "offline_build", "hand_steps": [], "blind": None,
         "next": "NEXT (automatic: the Dispatch tick launches a capped builder): build"},
    ]
    mj = os.path.join(tmp, "maturation.json")
    json.dump(rows, open(mj, "w"))
    recs = {"rm-detached-bench-fix-sandbox-a-1794790001": {"item": x, "owed_close": "%s is still open" % x},
            "rm-detached-bench-fix-sandbox-b-1794790002": {"item": y, "owed_close": "%s is still open" % y},
            "rm-detached-bench-fix-sandbox-c-1794790003": {"item": x}}
    for unit, r in recs.items():
        json.dump(dict(r, unit=unit), open(os.path.join(det, unit + ".json"), "w"))
    open(os.path.join(det, "rm-detached-bench-fix-sandbox-a-1794790001.out.json"), "w").write("{}")

    args = [sys.executable, OWED, "sync-sources", "--maturation-json", mj, "--detached-dir", det]
    p1 = subprocess.Popen(args, cwd=REPO, env=base, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p2 = subprocess.Popen(args, cwd=REPO, env=base, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    o1, _ = p1.communicate(timeout=300)
    o2, _ = p2.communicate(timeout=300)
    check(p1.returncode == 0 and p2.returncode == 0, "two concurrent sync-sources both exit 0")

    def owed_items():
        probe = ("import os, sys, json; sys.path.insert(0, %r); import model\n"
                 "model.EVENTS = os.environ['RIMFLOW_LEDGER']; model.ITEMS = os.environ['RIMFLOW_ITEMS']\n"
                 "w = model.replay().items\n"
                 "print(json.dumps([dict(id=i.id, title=i.title, caused_by=getattr(i, 'caused_by', None)) "
                 "for i in w.values() if getattr(i, 'kind', None) == 'owed']))\n") % RIMFLOW
        r = subprocess.run([sys.executable, "-c", probe], cwd=REPO, env=base, capture_output=True, text=True,
                           timeout=120)
        try:
            return json.loads(r.stdout.strip().splitlines()[-1])
        except Exception:
            return []

    got = owed_items()
    check(len(got) == 3, "exactly 3 owed items after the concurrent runs (got %d)" % len(got))
    txt = json.dumps(got)
    check("GimmeSomeSlack" in txt, "the three-cycle pause is owed (the T26 loss)")
    check("ExplosiveKnockback" in txt, "the card owed to him is owed")
    check(any(g.get("caused_by") == x for g in got), "the open item left by a successful run is owed, caused_by it")
    check(not any(g.get("caused_by") == y for g in got) and "sandbox-b" not in txt,
          "a run whose item is already closed files nothing")
    check("FlowWorks" not in txt, "an automatic stage files nothing")
    r = subprocess.run(args, cwd=REPO, env=base, capture_output=True, text=True, timeout=300)
    check(r.returncode == 0 and "FILED" not in r.stdout and len(owed_items()) == 3,
          "a third run files nothing new")
    allev = ""
    for f in glob.glob(os.path.join(tmp, "events", "*.jsonl")) + [base["RIMFLOW_LEDGER"]]:
        if os.path.isfile(f):
            allev += open(f).read()
    check("maturation:GimmeSomeSlack@0.1.0:blind_challenge:visit3" in allev
          and "detached:rm-detached-bench-fix-sandbox-a-1794790001" in allev,
          "each filing carries its source key")
    disp = open(os.path.join(RIMFLOW, "dispatcher.py"), encoding="utf-8").read()
    check("sync-sources" in disp or "owed.sync_sources" in disp, "the Dispatcher tick runs sync-sources")
    passed = sum(ok for ok, _ in RESULTS)
    for ok, what in RESULTS:
        print("%s  %s" % ("ok  " if ok else "FAIL", what))
    print("%s %d/%d" % ("PASS" if passed == TOTAL == len(RESULTS) else "FAIL", passed, TOTAL))
    return 0 if passed == TOTAL == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
