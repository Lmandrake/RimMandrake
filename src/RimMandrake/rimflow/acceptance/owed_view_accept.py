#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_LIST_CONDUCTOR_OWES_FIRST_AT_EVERY_WAKE (spec:
design/specs/2026-11-15-conductor-restart-loses-nothing.md §3 E1 and §5 ticket 1). Written by the filing seat; the
builder does not edit it (a wrong clause goes to the Conductor).

    python3 src/RimMandrake/rimflow/acceptance/owed_view_accept.py      # exit 0 and "PASS 17/17" when built

THE CONTRACT
  An owed act is an ordinary ledger item: `rimflow file <ID> --for BENCH --kind owed --title "<the act>"`, with
  `--caused-by <item>` when it acts on another item. No new verb or field.
  `rimflow queue CONDUCTOR --owed` prints ONLY open `kind: owed` items of the Conductor's seat (CONDUCTOR = BENCH):
    line 1   `OWED <n> (actionable <a>, waiting <w>), oldest <age> <ID>`  (`OWED 0` when there are none)
    then     one line per actionable item, oldest first, holding its ID, its title and, when set, `for <caused_by>`;
             an item older than 2 h carries the word LATE
    then     `WAITING (<w>):` and one line per item under an open `rimflow wait` (claimed first, as today), holding its ID and the wait reason
    at most 40 lines in all; past that a last line `… <k> more: rimflow queue CONDUCTOR --owed --all`
  A closed, dropped or superseded owed item is not listed; a non-owed item never is.
  `rimflow next --seat BENCH --peek` never offers a `kind: owed` item (owed acts are the Conductor's, not a builder's).
  Closing an owed item needs evidence: `close --sha <sha>` as today, or `close --no-code "<text>"` whose text holds a
  commit sha (7+ hex), a run id (`rm-detached-…`), a path (contains / or \\) or `told him at <time>`; a bare
  `--no-code "done"` is refused, naming the four shapes.
  Wakes print the view: src/RimMandrake/rimflow/seat_restart.py and src/RimMandrake/Utils/handoff.py both call it, and
  the role file's Start of turn reads `queue CONDUCTOR --owed` before anything else from the queue.
  Seeds: the real ledger holds a `kind: owed` item (open or closed) caused by each of the two debts measured open at
  filing: RIMMANDRAKE_REALIGN_FLOWWORKS_PROOFS_AFTER_UNDER_LIQUID_LAW and RIMMANDRAKE_HARDEN_PIPELINE_WHERE_HANDS_CLEANED_UP.
"""
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RIMFLOW, "..", "..", ".."))
sys.path.insert(0, RIMFLOW)
CLI = os.path.join(RIMFLOW, "cli.py")
TOTAL = 17
RESULTS = []


def check(ok, what):
    RESULTS.append((bool(ok), what))


def main():
    tmp = tempfile.mkdtemp(prefix="owed_view_")
    items = os.path.join(tmp, "items")
    os.makedirs(items)
    base = {k: v for k, v in os.environ.items() if not k.startswith("RIMFLOW_")}
    base.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=items, RIMFLOW_SEAT="BENCH",
                RIMFLOW_PROBE="no-reading", PYTHONDONTWRITEBYTECODE="1")

    def cli(*a):
        return subprocess.run([sys.executable, CLI] + list(a) + ["--why", "acceptance sandbox"], cwd=REPO, env=base,
                              capture_output=True, text=True, timeout=120)

    def view(*extra):
        r = subprocess.run([sys.executable, CLI, "queue", "CONDUCTOR", "--owed"] + list(extra), cwd=REPO, env=base,
                           capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout

    parent = "RIMMANDRAKE_PROVE_SANDBOX_PARENT_TASK_STANDS_ALONE"
    a = "RIMMANDRAKE_LAUNCH_SANDBOX_REALIGNMENT_WHEN_SLOT_FREES"
    b = "RIMMANDRAKE_ASK_SANDBOX_OWNER_TIMER_QUESTION_AGAIN"
    c = "RIMMANDRAKE_WRITE_SANDBOX_ONE_PAGE_SUMMARY_NEVER_WRITTEN"
    cli("file", parent, "--for", "BENCH", "--title", "an ordinary task", "--kind", "task")
    rc0, out0 = view()
    check(rc0 == 0 and out0.strip().splitlines()[:1] and out0.strip().splitlines()[0].startswith("OWED 0"),
          "with no owed items the view's first line is OWED 0")
    cli("file", a, "--for", "BENCH", "--title", "launch the realignment when a slot frees", "--kind", "owed",
        "--caused-by", parent)
    cli("file", b, "--for", "BENCH", "--title", "ask him about the usage timer", "--kind", "owed")
    cli("file", c, "--for", "BENCH", "--title", "write the one-page summary", "--kind", "owed")
    cli("claim", b)        # `wait` holds only started work (ready or doing)
    cli("wait", b, "--reason", "his answer to the timer question", "--until", "2099-01-01")
    rc, out = view()
    lines = out.strip().splitlines()
    check(rc == 0, "queue CONDUCTOR --owed exits 0")
    check(lines and re.match(r"OWED 3 \(actionable 2, waiting 1\), oldest ", lines[0] or ""),
          "first line counts 3 owed, 2 actionable, 1 waiting (got %r)" % (lines[:1],))
    check(a in out and c in out and b in out, "every open owed item is listed")
    pl = [l for l in lines if parent in l]
    check(len(pl) == 1 and a in pl[0] and ("for " + parent) in pl[0],
          "the plain task is not listed; it appears only as the caused_by on the owed launch's line")
    wi = next((i for i, l in enumerate(lines) if l.startswith("WAITING (1)")), None)
    check(wi is not None and any(b in l and "timer question" in l for l in lines[wi:]),
          "the waiting item is under WAITING with its wait reason")
    check(wi is not None and all(b not in l for l in lines[1:wi]), "the waiting item is not among the actionable")
    check(len(lines) <= 40, "the view is at most 40 lines")
    # many owed items: capped with a more-line
    for i in range(45):
        cli("file", "RIMMANDRAKE_PAD_SANDBOX_OWED_FILLER_%s" % ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[i % 26] * (1 + i // 26)),
            "--for", "BENCH", "--title", "filler %d" % i, "--kind", "owed")
    rc, out = view()
    lines = out.strip().splitlines()
    check(len(lines) <= 40 and re.search(r"more: rimflow queue CONDUCTOR --owed --all", lines[-1] if lines else ""),
          "past 40 lines the view ends with the --all line")
    # discharge needs evidence
    r = cli("close", c, "--no-code", "done")
    check(r.returncode != 0, "close of an owed item with --no-code \"done\" is refused")
    r = cli("close", c, "--no-code", "told him at 4:56 PM PST: the summary is at D:\\ClaudeWork\\x.md")
    check(r.returncode == 0, "close with evidence (told him at …, a path) succeeds")
    rc, out = view("--all")
    check(c not in out, "a closed owed item is no longer listed")
    # builders are never offered an owed act
    r = subprocess.run([sys.executable, CLI, "next", "--seat", "BENCH", "--peek"], cwd=REPO, env=base,
                       capture_output=True, text=True, timeout=120)
    check(r.returncode == 0 and parent in r.stdout and "FILLER" not in r.stdout and a not in r.stdout,
          "next --peek offers the plain task, never an owed item")
    # call sites and role file
    src = {p: open(os.path.join(REPO, p), encoding="utf-8").read() for p in (
        "src/RimMandrake/rimflow/seat_restart.py", "src/RimMandrake/Utils/handoff.py",
        "src/RimMandrake/rimflow/roles/conductor.md")}
    check("--owed" in src["src/RimMandrake/rimflow/seat_restart.py"]
          or re.search(r"owed\.(view|banner)", src["src/RimMandrake/rimflow/seat_restart.py"]),
          "seat_restart.py's wake prints the owed view")
    check("--owed" in src["src/RimMandrake/Utils/handoff.py"]
          or re.search(r"owed\.(view|banner)", src["src/RimMandrake/Utils/handoff.py"]),
          "handoff.py --wake prints the owed view")
    sot = src["src/RimMandrake/rimflow/roles/conductor.md"].split("## Start of turn", 1)[-1][:1500]
    check("queue CONDUCTOR --owed" in sot, "the role file's Start of turn reads queue CONDUCTOR --owed")
    # seeds, on the real ledger
    env_real = {k: v for k, v in os.environ.items() if not k.startswith("RIMFLOW_")}
    probe = ("import sys; sys.path.insert(0, %r); import model\n"
             "w = model.replay().items\n"
             "c = {getattr(i, 'caused_by', None) for i in w.values() if getattr(i, 'kind', None) == 'owed'}\n"
             "need = {'RIMMANDRAKE_REALIGN_FLOWWORKS_PROOFS_AFTER_UNDER_LIQUID_LAW', "
             "'RIMMANDRAKE_HARDEN_PIPELINE_WHERE_HANDS_CLEANED_UP'}\n"
             "print('SEEDS_OK' if need <= c else 'SEEDS_MISSING ' + ' '.join(sorted(need - c)))\n") % RIMFLOW
    r = subprocess.run([sys.executable, "-c", probe], cwd=REPO, env=env_real, capture_output=True, text=True,
                       timeout=300)
    check("SEEDS_OK" in r.stdout, "the two measured open debts are seeded as owed items (%s)"
          % (r.stdout.strip() or r.stderr.strip()[-200:]))
    passed = sum(ok for ok, _ in RESULTS)
    for ok, what in RESULTS:
        print("%s  %s" % ("ok  " if ok else "FAIL", what))
    print("%s %d/%d" % ("PASS" if passed == TOTAL == len(RESULTS) else "FAIL", passed, TOTAL))
    return 0 if passed == TOTAL == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
