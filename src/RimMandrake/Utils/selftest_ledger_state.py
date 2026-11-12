#!/usr/bin/env python3
"""Selftest: ledger_state.py writes one screen of ledger state, and `handoff.py --wake` regenerates it and names it
(HANDOFF_SHRINK_HALF_THE_BYTES_WERE_GIT, half 2).

The test ledger is written by the real rimflow CLI as subprocesses (`RIMFLOW_LEDGER` in a temp dir), so every event is
one the schema accepted, not a hand-made dict the reader happens to like. Then each of the four sections is checked
for what must be there AND for what must not (a dropped item, a released lease, another seat's NEXT, an older NEXT),
because a section that lists everything passes every "is it there" check. A stress ledger of 400 more items checks the
one-screen bound where it can break, and the live ledger is read (never written) for the same bound.
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CLI = os.path.join(REPO, "src", "RimMandrake", "rimflow", "cli.py")
REAL_STATE = os.path.join(REPO, "infrastructure", "state")
TMP = tempfile.mkdtemp(prefix="selftest_ledger_state.")
LED = os.path.join(TMP, "events.jsonl")

fails = []


def check(ok, what):
    print(("  ok   " if ok else "  FAIL ") + what)
    if not ok:
        fails.append(what)


def env(seat):
    e = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT") and not k.startswith("GIT_")}
    e.update(RIMFLOW_LEDGER=LED, RIMFLOW_ITEMS=os.path.join(TMP, "items"), RIMFLOW_PROBE="no-reading",
             RIMFLOW_SCHEDULE=os.path.join(TMP, "no_schedule.json"), RIMFLOW_DRIVER_LOCK="", RIMFLOW_SHARED_BRIDGE="",
             RIMFLOW_BRIDGE_LOCK=os.path.join(TMP, "bridge.lock"), RM_HOST="archmagi", RIMFLOW_SEAT=seat)
    return e


def rf(seat, *args):
    p = subprocess.run([sys.executable, CLI] + list(args) + ["--why", "selftest_ledger_state"], env=env(seat),
                       cwd=REPO, capture_output=True, text=True, timeout=120)
    if p.returncode:
        raise SystemExit("rimflow %s exited %d: %s" % (" ".join(args), p.returncode, (p.stderr or p.stdout)[-400:]))
    return p.stdout


def token(out):
    return out.split("lease token ")[1].split()[0]


# --- the test ledger, written by the CLI -----------------------------------------------------------------------------
B, O = "BENCH", "CLAUDE_ARCHMAGI_OFFLINE1"
ids = ["STATENOW_TEST_ITEM_%s" % w for w in ("ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO", "FOXTROT", "GOLF",
                                             "HOTEL", "INDIA", "JULIET", "KILO", "LIMA")]
for i in ids:
    rf(B, "file", i, "--for", B, "--title", "title of " + i)
rf(O, "file", "STATENOW_TEST_OTHER_SEAT", "--for", O, "--title", "the other seat's item")
rf(O, "file", "STATENOW_TEST_OTHER_RELEASED", "--for", O, "--title", "a lease given back")

rf(B, "claim", ids[0])                                              # BENCH's live lease, in progress
rf(O, "claim", "STATENOW_TEST_OTHER_SEAT")                          # another seat's live lease
tok = token(rf(O, "claim", "STATENOW_TEST_OTHER_RELEASED"))
rf(O, "release", "STATENOW_TEST_OTHER_RELEASED", "--token", tok)    # a released lease is no live helper
rf(B, "needs", ids[1], "--to", "owner")
rf(B, "needs", ids[2], "--to", "owner")
rf(B, "block", ids[3], "--reason", "the pump eats its own hose", "--kind", "external")
rf(B, "note", ids[0], "--text", "first look; NEXT: the stale action")
time.sleep(1.1)                                                     # a later second, so "newest" means something
rf(B, "note", ids[0], "--text", "probe ran; NEXT: write the fix into the proof script")
rf(B, "note", ids[4], "--text", "NEXT: read the first exception in Player.log\nnot this second line")
rf(B, "note", ids[11], "--text", "NEXT: a dropped item's action")
rf(B, "drop", ids[11], "--reason", "selftest: dropped items leave every section")
rf(O, "note", "STATENOW_TEST_OTHER_SEAT", "--text", "NEXT: the other seat's action")
rf(B, "note", ids[6], "--text", "closed the loop. NEXT:\nno further step, this line is not an action")
# GPT broaden, 2026-11-11: a NEXT the ledger has since overtaken (blocked for him, then called off in a plain note)
rf(B, "note", ids[7], "--text", "NEXT: deploy the DLL")
rf(B, "block", ids[7], "--reason", "deploy waits on his approval", "--kind", "owner")
rf(B, "note", ids[7], "--text", "Deployment cancelled; wait for the owner.")
LONG = "RIMMANDRAKE_LENGTHEN_STATENOWTESTITEMNAME_UNTIL_THEY_HIT_CAPSXX"
rf(B, "file", LONG, "--for", B, "--title", "long id")
rf(O, "note", LONG, "--text", "NEXT: " + "z" * 200)
with open(os.path.join(TMP, "events", "BENCH.jsonl")) as fh:            # a hand-mangled line: text that is not a string
    bad = dict(json.loads([ln for ln in fh if '"note"' in ln][0]), text=["NEXT:", 3])
with open(os.path.join(TMP, "events", "BENCH.jsonl"), "a") as fh:
    fh.write(json.dumps(bad) + "\n")

os.environ.update(env(B))
sys.path.insert(0, HERE)
import ledger_state  # noqa: E402
import handoff  # noqa: E402

text = ledger_state.build(B)
lines = text.splitlines()
sec = {}
cur = None
for ln in lines:
    if ln.startswith("## "):
        cur = ln.split(" — ")[0][3:]
        sec[cur] = [ln]
    elif cur:
        sec[cur].append(ln)
body = lambda name: "\n".join(sec.get(name, []))   # noqa: E731

print("ledger_state: the four sections, from a CLI-written ledger")
check(list(sec) == ["Open items", "Owner-pending", "Live helpers", "NEXT"], "four sections, in order: %s" % list(sec))
check("## Open items — 12 (doing 1 · proposed 9 · blocked 2)" in body("Open items"),
      "open items: 12 of BENCH's, the dropped one gone, counts by state: %r" % sec["Open items"][0])
check("`%s` — doing, leased by BENCH:" % ids[0] in sec["Open items"][1], "open items: the leased one first: %r"
      % sec["Open items"][1])
check("BLOCKED: the pump eats its own hose" in body("Open items"), "open items: the blocked one with its reason")
check(len([x for x in sec["Open items"] if x]) == 10 and "… and 4 more: rimflow queue BENCH" in body("Open items"),
      "open items: 8 shown, the rest counted and named:\n        " + "\n        ".join(sec["Open items"]))
check("STATENOW_TEST_OTHER" not in body("Open items") and ids[11] not in body("Open items"),
      "open items: no other seat's item, no dropped item")
check(sec["Owner-pending"][0].startswith("## Owner-pending — 3 items in 1 topic")
      and "STATENOW_* (3 items, e.g. `%s`)" % ids[1] in body("Owner-pending"),
      "owner-pending: both needs=owner items and the one blocked on him, folded by leading word as the board does:\n        "
      + "\n        ".join(sec["Owner-pending"]))
check(ids[0] not in body("Owner-pending") and ids[3] not in body("Owner-pending"),
      "owner-pending: nothing that is not his")
check("2 unexpired leases" in sec["Live helpers"][0] and "BENCH holds `%s`" % ids[0] in body("Live helpers")
      and "%s holds `STATENOW_TEST_OTHER_SEAT`" % O in body("Live helpers"),
      "live helpers: both live leases, every seat: %r" % sec["Live helpers"][0])
check("STATENOW_TEST_OTHER_RELEASED" not in body("Live helpers"), "live helpers: a released lease is not one")
check("NEXT: write the fix into the proof script" in body("NEXT") and "the stale action" not in body("NEXT"),
      "NEXT: the newest NEXT on an item, not an older one")
check("NEXT: read the first exception in Player.log (" in body("NEXT") and "second line" not in body("NEXT"),
      "NEXT: one line of the note, with its date and writer")
check("dropped item's action" not in body("NEXT") and "other seat's action" not in body("NEXT"),
      "NEXT: nothing from a dropped item or another seat")
check("other seat's action" not in body("NEXT") and ("`%s`" % ids[6]) not in body("NEXT"),
      "NEXT: an empty NEXT: borrows nothing from the next line")
row7 = next((ln for ln in sec["NEXT"] if ("`%s`" % ids[7]) in ln), "")
check("BLOCKED: deploy waits on his approval" in row7 and "⚠ 2 later events" in row7,
      "NEXT: an overtaken NEXT carries the block and a later-events warning:\n        " + row7)
rowl = next((ln for ln in sec["NEXT"] if LONG in ln), "")
check(rowl.endswith(", %s)" % O) and len(rowl) <= ledger_state.WIDTH,
      "NEXT: a 64-char id keeps its stamp and writer, the action is what gets cut:\n        " + rowl)
check(ledger_state.build("CONDUCTOR").splitlines()[3:] == lines[3:] and
      ledger_state.out_path("BENCH") == ledger_state.out_path(ledger_state.model.canonical("CONDUCTOR")),
      "the CONDUCTOR alias reads BENCH's items, not an empty seat")
os.environ["TZ"] = "UTC"
time.tzset()
check(ledger_state.local("2026-11-12T05:33:39Z") == "2026-11-11 21:33 PST"
      and ledger_state.local("2026-07-01T19:00:00Z") == "2026-07-01 12:00 PDT", "times are Pacific on a UTC host, PDT in summer")
check(len(lines) <= ledger_state.MAX_LINES and max(map(len, lines)) <= ledger_state.WIDTH,
      "one screen: %d lines (<= %d), widest %d (<= %d)" % (len(lines), ledger_state.MAX_LINES,
                                                         max(map(len, lines)), ledger_state.WIDTH))

print("ledger_state: the file lands beside the ledger in use, never in the real repo")
path = ledger_state.out_path(B)
check(path == os.path.join(TMP, "derived", "state_now", "BENCH_STATE_NOW.md"), "path under the test root: %s" % path)

print("handoff --wake: regenerates the file and its pointer lines name it")
hdir = os.path.join(TMP, "handoffs")
os.makedirs(hdir)
with open(os.path.join(hdir, "BENCH_REBOOT_HANDOFF_209901010000.md"), "w") as fh:
    fh.write("# BENCH_REBOOT_HANDOFF_209901010000 — READ FIRST on wake\n\n## What is half-done, and where it stops\n\n"
             "- `%s` — probing; NEXT: something the ledger has since overtaken\n" % ids[0])
handoff.HANDOFFS = hdir
handoff.previous_handoff = lambda: ("BENCH_REBOOT_HANDOFF_209901010000.md", None)
handoff.show_last_reply = lambda: None
handoff.events = lambda: ledger_state.model.read()
if os.path.exists(path):
    os.remove(path)
rf(B, "note", ids[5], "--text", "NEXT: an action written after the last build")
out = io.StringIO()
with contextlib.redirect_stdout(out):
    handoff.wake()
w = out.getvalue()
tail = w[w.index("POINTER STATUS"):] if "POINTER STATUS" in w else ""
check(("LEDGER STATE NOW" in tail) and (path in tail), "the pointer block names the file:\n        "
      + "\n        ".join(tail.splitlines()[-3:]))
check(os.path.isfile(path), "the wake wrote it")
got = open(path).read() if os.path.isfile(path) else ""
check("NEXT: an action written after the last build" in got, "regenerated from the ledger as it is at the wake")
handoff.previous_handoff = lambda: (None, None)
out = io.StringIO()
with contextlib.redirect_stdout(out):
    handoff.wake()
check(path in out.getvalue(), "a seat with no handoff is still pointed at it")

print("ledger_state: a stress ledger of 400 more items stays one screen")
raw = [json.loads(ln) for ln in open(os.path.join(TMP, "events", "BENCH.jsonl")) if ln.strip()]
pick = lambda verb, iid: next(e for e in raw if e["event"] == verb and e["id"] == iid)   # noqa: E731
# on-disk events as the CLI wrote them, cloned under new ids: long titles, long NEXTs, needs=owner, live leases
tmpl = [(pick("file", ids[1]), {"title": "stress " + "x" * 300}), (pick("needs", ids[1]), {}),
        (pick("note", ids[4]), {"text": "NEXT: " + "y" * 300}), (pick("lease", ids[0]), {})]
with open(os.path.join(TMP, "events", "BENCH.jsonl"), "a") as fh:
    for n in range(400):
        for k, (ev, extra) in enumerate(tmpl):
            ev = dict(ev, id="STRESSED_ITEM_N%03d_%s" % (n, "ABCDEFGHIJ"[n % 10]), tsn=ev["tsn"] + n * 10 + k, **extra)
            fh.write(json.dumps(ev) + "\n")
text = ledger_state.build(B)
lines = text.splitlines()
check(len(lines) <= ledger_state.MAX_LINES and max(map(len, lines)) <= ledger_state.WIDTH,
      "stress: %d lines, widest %d" % (len(lines), max(map(len, lines))))
check(sum(1 for ln in lines if ln.startswith("- … and ")) >= 3, "stress: each long section says how many it left out")

print("ledger_state: the live ledger, read only")
os.environ.pop("RIMFLOW_LEDGER")
ledger_state.model.EVENTS = os.path.join(REAL_STATE, "ledger", "events.jsonl")
for s in ("BENCH",):
    lines = ledger_state.build(s).splitlines()
    check(len(lines) <= ledger_state.MAX_LINES, "live %s: %d lines" % (s, len(lines)))

if not os.environ.get("KEEP"): shutil.rmtree(TMP, ignore_errors=True)
else: print(TMP)
print("\n%s: %d failure(s)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
