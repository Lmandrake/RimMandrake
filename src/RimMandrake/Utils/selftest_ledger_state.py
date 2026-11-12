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
import re
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
rf(B, "note", ids[9], "--text", "fixed the reader (NEXT then: is read now); NEXT: re-run the judge")    # a NEXT quoted, then the real one
rf(B, "note", ids[11], "--text", "NEXT: a dropped item's action")
rf(B, "drop", ids[11], "--reason", "selftest: dropped items leave every section")
rf(O, "note", "STATENOW_TEST_OTHER_SEAT", "--text", "NEXT: the other seat's action")
rf(B, "note", ids[6], "--text", "closed the loop. NEXT:\nno further step, this line is not an action")
rf(B, "note", ids[8], "--text", "Looked at it. NOT BEFORE Wed 3 PM. NEXT then: deploy it with him")       # the spoken form an owner note used
# GPT broaden, 2026-11-11: a NEXT the ledger has since overtaken (blocked for him, then called off in a plain note)
rf(B, "note", ids[7], "--text", "NEXT: deploy the DLL")
rf(B, "block", ids[7], "--reason", "deploy waits on his approval", "--kind", "owner")
rf(B, "note", ids[7], "--text", "Deployment cancelled; wait for the owner.")
LONG = "RIMMANDRAKE_LENGTHEN_STATENOWTESTITEMNAME_UNTIL_THEY_HIT_CAPSXX"
rf(B, "file", LONG, "--for", B, "--title", "long id")
rf(O, "note", LONG, "--text", "NEXT: " + "z" * 200)
# full-file review, 2026-11-11: a dated wait written after the NEXT (a trailing empty NEXT and a wide-character action
# come later, on a rebuild: the NEXT section shows six rows, and two more would push the rows above out of it)
WAIT_UNTIL = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 3 * 86400))
rf(B, "wait", ids[0], "--until", WAIT_UNTIL, "--reason", "not before he is back")
# pointer states a last-verb reader got wrong: reopened by a failed verify after its close, and blocked then unblocked
SHA = subprocess.check_output(["git", "-C", REPO, "rev-parse", "HEAD"], text=True).strip()
REOPENED, UNBLOCKED = "STATENOW_TEST_PTR_REOPENED", "STATENOW_TEST_PTR_UNBLOCKED"
rf(O, "file", REOPENED, "--for", O, "--title", "closed, then a fail reopened it")
rf(O, "verify", REOPENED, "--result", "pass", "--config", "selftest", "--level", "L0", "--sha", SHA)
rf(O, "close", REOPENED, "--sha", SHA, "--live", "once: selftest")
rf(O, "verify", REOPENED, "--result", "fail", "--config", "selftest", "--level", "L0", "--sha", SHA)
rf(O, "file", UNBLOCKED, "--for", O, "--title", "blocked, then unblocked")
rf(O, "block", UNBLOCKED, "--reason", "a block that is lifted", "--kind", "external")
rf(O, "unblock", UNBLOCKED)
SUPERSEDED = "STATENOW_TEST_PTR_SUPERSEDED"
rf(O, "file", SUPERSEDED, "--for", O, "--title", "replaced by another item")
rf(O, "supersede", SUPERSEDED, "--by", ids[5])
CHAINED = "STATENOW_TEST_PTR_CHAINED"                   # CHAINED -> SUPERSEDED -> ids[5], which is open
rf(O, "file", CHAINED, "--for", O, "--title", "replaced by an item that was itself replaced")
rf(O, "supersede", CHAINED, "--by", SUPERSEDED)
with open(os.path.join(TMP, "events", "BENCH.jsonl")) as fh:            # a hand-mangled line: text that is not a string
    bad = dict(json.loads([ln for ln in fh if '"note"' in ln][0]), text=["NEXT:", 3])
with open(os.path.join(TMP, "events", "BENCH.jsonl"), "a") as fh:
    fh.write(json.dumps(bad) + "\n")

os.environ.update(env(B))
sys.path.insert(0, HERE)
import ledger_state  # noqa: E402
import handoff  # noqa: E402

MON = ledger_state.local(time.time())[5:8]        # "11-": the notes are stamped today, so no month is wired in
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
check("## Open items — this seat's 12 (doing 1 · proposed 9 · blocked 2)" in body("Open items"),
      "open items: 12 of BENCH's, the dropped one gone, counts by state: %r" % sec["Open items"][0])
check(sec["Open items"][1].startswith("- `%s` — doing, WAITS until " % ids[0])
      and ": not before he is back, leased by BENCH:" in sec["Open items"][1],
      "open items: the leased one first, with the owner's dated wait on it: %r" % sec["Open items"][1])
check("BLOCKED: the pump eats its own hose" in body("Open items"), "open items: the blocked one with its reason")
check(len([x for x in sec["Open items"] if x]) == 9 and "… and 5 more: rimflow queue BENCH" in body("Open items"),
      "open items: 7 shown, the rest counted and named:\n        " + "\n        ".join(sec["Open items"]))
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
check(all(re.search(r"lease to \d{2}-\d{2} \d{2}:\d{2} P[SD]T$", ln) for ln in sec["Live helpers"][1:3]),
      "live helpers: a lease's end carries its date, so tomorrow never reads as today: %r" % sec["Live helpers"][1:3])
check("NEXT: write the fix into the proof script" in body("NEXT") and "the stale action" not in body("NEXT"),
      "NEXT: the newest NEXT on an item, not an older one")
i4 = next((k for k, ln in enumerate(sec["NEXT"]) if ("`%s`" % ids[4]) in ln), -1)
check(i4 > 0 and "(NEXT " + MON in sec["NEXT"][i4] and "by BENCH)" in sec["NEXT"][i4]
      and sec["NEXT"][i4 + 1] == "    NEXT: read the first exception in Player.log" and "second line" not in body("NEXT"),
      "NEXT: two lines, the stamp and writer on the first, one line of the note on the second")
check("dropped item's action" not in body("NEXT") and "other seat's action" not in body("NEXT"),
      "NEXT: nothing from a dropped item or another seat")
check("    NEXT: re-run the judge" in sec["NEXT"] and "is read now" not in body("NEXT"),
      "NEXT: a quoted NEXT earlier on the line does not swallow the real one after it")
check("    NOT BEFORE Wed 3 PM. NEXT then: deploy it with him" in sec["NEXT"] and "Looked at it" not in body("NEXT"),
      "NEXT: the spoken form \"NEXT then:\" is a NEXT too, and keeps the sentence it leans on (its date gate)")
check("other seat's action" not in body("NEXT") and ("`%s`" % ids[6]) not in body("NEXT"),
      "NEXT: an empty NEXT: borrows nothing from the next line")
row7 = next((ln for ln in sec["NEXT"] if ("`%s`" % ids[7]) in ln), "")
check("BLOCKED: deploy waits on his app" in row7 and "⚠ 2 later events" in row7 and ledger_state.cols(row7) <= ledger_state.WIDTH,
      "NEXT: an overtaken NEXT carries the block and a later-events warning:\n        " + row7)
il = next((k for k, ln in enumerate(sec["NEXT"]) if LONG in ln), -1)
rowl = "\n        ".join(sec["NEXT"][il:il + 2]) if il > 0 else ""
check(il > 0 and sec["NEXT"][il + 1].startswith("    (NEXT " + MON) and (" by %s) NEXT: zzz" % O) in sec["NEXT"][il + 1]
      and sec["NEXT"][il + 1].endswith("…") and max(ledger_state.cols(x) for x in sec["NEXT"][il:il + 2]) <= ledger_state.WIDTH,
      "NEXT: a 63-char id keeps its stamp and writer, the action is what gets cut:\n        " + rowl)
r0 = next((ln for ln in sec["NEXT"] if ("`%s`" % ids[0]) in ln), "")
check("WAITS" in r0 and "⚠ 1 later event" in r0, "NEXT: a dated wait written after the NEXT shows on its row:\n        " + r0)
rf(B, "note", ids[10], "--text", "NEXT: the real action. Then a NEXT time: ")
rf(B, "note", ids[2], "--text", "NEXT: " + "日本語の手順" * 40)
check(ledger_state.cols(ledger_state.clip("日" * 100)) <= ledger_state.WIDTH and ledger_state.clip("日" * 59) == "日" * 59,
      "clip: 100 wide characters (fewer characters than the width, twice the columns) are cut; 59 are not")
nx2 = ledger_state.build(B).split("## NEXT")[1].splitlines()
check(any(ln.startswith("    NEXT: the real action") for ln in nx2),
      "NEXT: a trailing empty NEXT does not throw away the real one before it")
i2 = next((k for k, ln in enumerate(nx2) if ("`%s`" % ids[2]) in ln), -1)
check(i2 > 0 and "日本語" in nx2[i2 + 1] and nx2[i2 + 1].endswith("…")
      and ledger_state.cols(nx2[i2 + 1]) <= ledger_state.WIDTH < 2 * len(nx2[i2 + 1]),
      "NEXT: a wide-character action is cut by terminal columns, not characters (%d columns)"
      % (ledger_state.cols(nx2[i2 + 1]) if i2 > 0 else -1))
check(ledger_state.build("CONDUCTOR").splitlines()[3:] == ledger_state.build(B).splitlines()[3:] and
      ledger_state.out_path("BENCH") == ledger_state.out_path(ledger_state.model.canonical("CONDUCTOR")),
      "the CONDUCTOR alias reads BENCH's items, not an empty seat")
os.environ["TZ"] = "UTC"
time.tzset()
check(ledger_state.local("2026-11-12T05:33:39Z") == "2026-11-11 21:33 PST"
      and ledger_state.local("2026-07-01T19:00:00Z") == "2026-07-01 12:00 PDT", "times are Pacific on a UTC host, PDT in summer")
check(len(lines) <= ledger_state.MAX_LINES and max(map(ledger_state.cols, lines)) <= ledger_state.WIDTH,
      "one screen: %d lines (<= %d), widest %d (<= %d)" % (len(lines), ledger_state.MAX_LINES,
                                                         max(map(ledger_state.cols, lines)), ledger_state.WIDTH))

print("ledger_state: the file lands beside the ledger in use, never in the real repo")
path = ledger_state.out_path(B)
check(path == os.path.join(TMP, "derived", "state_now", "BENCH_STATE_NOW.md"), "path under the test root: %s" % path)

print("handoff --wake: regenerates the file and its pointer lines name it")
hdir = os.path.join(TMP, "handoffs")
os.makedirs(hdir)
with open(os.path.join(hdir, "BENCH_REBOOT_HANDOFF_209901010000.md"), "w") as fh:
    fh.write("# BENCH_REBOOT_HANDOFF_209901010000 — READ FIRST on wake\n\n## What is half-done, and where it stops\n\n"
             "<!-- TEMPLATE GUIDANCE for the writer -->\n"
             "- `%s` — probing; NEXT: something the ledger has since overtaken\n" % ids[0]
             + "".join("- `%s` — x; NEXT: y\n" % i for i in (ids[11], REOPENED, UNBLOCKED, ids[3], SUPERSEDED, CHAINED))
             + "\n## Filed and still open (1)\n- `%s` — filed, hidden from the view, so no pointer\n" % ids[9])
handoff.HANDOFFS = hdir
handoff.previous_handoff = lambda: ("BENCH_REBOOT_HANDOFF_209901010000.md", "2000-01-01T00:00:00Z")
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
check("TEMPLATE GUIDANCE" not in w and "<!--" not in w, "the template's <!-- --> guidance is not printed")
check("written 1999-12-31 16:00 PST" in w, "the pointer block says when the handoff was written, in Pacific time")
check("open (doing)" in tail and 'newest note' in tail and "write the fix into the proof script" in tail
      and "the stale action" not in tail, "an open pointer shows what the ledger recorded after the handoff, newest note")
prow = lambda iid: next((ln for ln in tail.splitlines() if ln.strip().startswith(iid + " ")), "")    # noqa: E731
check("DROPPED" in prow(ids[11]) and "do NOT act" in prow(ids[11]), "a dropped pointer is CLOSED: %r" % prow(ids[11]))
check(prow(REOPENED).endswith("open (ready, %s's)" % O) and prow(UNBLOCKED).endswith("open (proposed, %s's)" % O)
      and prow(ids[3]).endswith("open (proposed, BLOCKED)"),
      "pointer states are the ledger's own: reopened after a close is open, an unblocked one is not BLOCKED:\n        "
      + "\n        ".join(prow(i) for i in (REOPENED, UNBLOCKED, ids[3])))
check("open pointers: 4 " in tail, "the dropped and superseded pointers are not counted open")
check(prow(ids[9]) == "", "an id in the hidden filed list is no pointer: the reader cannot see it")
check(prow(SUPERSEDED).endswith("SUPERSEDED  *** CLOSED -- do NOT act on this pointer; work its successor %s ***" % ids[5]),
      "a superseded pointer names its successor: %r" % prow(SUPERSEDED))
check(prow(CHAINED).endswith("work its successor %s (via %s) ***" % (ids[5], SUPERSEDED)),
      "a chain of supersessions is followed to its open end: %r" % prow(CHAINED))
check("  now: ledger as of " in tail, "the line under it says the game and bridge as the ledger has them now")
got = open(path).read() if os.path.isfile(path) else ""
check("NEXT: an action written after the last build" in got, "regenerated from the ledger as it is at the wake")
handoff.previous_handoff = lambda: (None, None)
out = io.StringIO()
with contextlib.redirect_stdout(out):
    handoff.wake()
check(path in out.getvalue(), "a seat with no handoff is still pointed at it")
handoff.previous_handoff = lambda: ("BENCH_REBOOT_HANDOFF_209901010000.md", "2000-01-01T00:00:00Z")
sys.modules["ledger_state"] = None          # the generator cannot load: the wake must still print, and say so
out = io.StringIO()
try:
    with contextlib.redirect_stdout(out):
        rc = handoff.wake()
except Exception as e:      # noqa: BLE001
    rc = "raised %r" % e
sys.modules["ledger_state"] = ledger_state
w = out.getvalue()
unm = next((ln for ln in w.splitlines() if ln.startswith("POINTER STATUS: UNMEASURED")), "")
check(rc == 0 and ids[0] in unm and REOPENED in unm and "LEDGER STATE NOW: UNMEASURED" in w,
      "a ledger_state that cannot load: the wake still prints the handoff and names every pointer UNMEASURED (rc %r)" % rc)

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
check(len(lines) <= ledger_state.MAX_LINES and max(map(ledger_state.cols, lines)) <= ledger_state.WIDTH,
      "stress: %d lines, widest %d" % (len(lines), max(map(ledger_state.cols, lines))))
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
