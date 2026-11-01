#!/usr/bin/env python3
"""selftest_conductor_closeout.py — B2 step 1 by program (CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK).

Each case runs the real check on a small transcript and ledger in a temp dir, through the real CLI where it can.
Covered: an unrecorded ruling is a gap; his words at or after it clear it; words from BEFORE it do not; a typo fix and a
sentence of a longer message clear it; a one-word or stray overlap does not; a machine ring and a seat's message are
not his; a message typed mid-turn (queued_command) is; goodbye, slash command and plain question are exempt, a bare
"yes" and a two-sentence message are not; dismiss clears by key; every blind input is UNMEASURED, never ok; the request
stores the verdict and gaps, they reach the killed record, and the wake prints them until settled; the hook runs check.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import conductor_closeout as CC  # noqa: E402
import seat_restart as SR  # noqa: E402

TMP = tempfile.mkdtemp(prefix="closeout_")
DISMISSED = os.path.join(TMP, "dismissed.jsonl")
os.environ["CONDUCTOR_CLOSEOUT_DISMISSED"] = DISMISSED
fails = 0
T0 = "2026-10-31T10:00:00.000Z"
BEFORE = "2026-10-31T09:00:00Z"
AFTER = "2026-10-31T11:00:00Z"


def check(cond, what):
    global fails
    print(("ok    " if cond else "FAIL  ") + what)
    fails += 0 if cond else 1


def human(text, uuid, ts=T0):
    return {"type": "user", "timestamp": ts, "uuid": uuid, "origin": {"kind": "human"}, "promptSource": "typed",
            "message": {"role": "user", "content": text}}


def world(name, recs, quotes=()):
    """-> (transcript path, clone root) holding those records and ownerSaid events."""
    root = os.path.join(TMP, name)
    ev = os.path.join(root, "infrastructure", "state", "ledger", "events")
    os.makedirs(ev)
    with open(os.path.join(ev, "OWNER.jsonl"), "w") as f:
        f.write(json.dumps({"event": "note", "ownerSaid": "an ancient ruling of no bearing", "ts": "2020-01-01T00:00:00Z"}) + "\n")
        for said, at in quotes:
            f.write(json.dumps({"event": "note", "ownerSaid": said, "ts": at}) + "\n")
    tx = os.path.join(root, "t.jsonl")
    with open(tx, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    return tx, root


def run(tx, root, *extra):
    r = subprocess.run([sys.executable, os.path.join(HERE, "conductor_closeout.py"), "check", "--transcript", tx,
                        "--root", root, "--json"] + list(extra), capture_output=True, text=True, timeout=60)
    return r.returncode, json.loads(r.stdout)


def run_rc(tx, root):
    return subprocess.run([sys.executable, os.path.join(HERE, "conductor_closeout.py"), "check", "--transcript", tx,
                           "--root", root], capture_output=True, text=True, timeout=60).returncode


def t_diff():
    tx, root = world("gap", [human("drop the old pipe art entirely", "u1")])
    rc, res = run(tx, root)
    check(rc == 1 and res["closeout"] == "partial" and len(res["gaps"]) == 1, "an unrecorded ruling is a gap, exit 1")
    check(res["gaps"][0]["text"] == "drop the old pipe art entirely", "the gap keeps his text, not a count")
    tx, root = world("said", [human("drop the old pipe art entirely", "u1")],
                     [("drop the old pipe art entirely", AFTER)])
    rc, res = run(tx, root)
    check(rc == 0 and res["closeout"] == "ok" and res["recorded"] == 1, "his words on the ledger clear it, exit 0")
    tx, root = world("old", [human("drop the old pipe art entirely", "u1")],
                     [("drop the old pipe art entirely", BEFORE)])
    check(run(tx, root)[0] == 1, "the same words recorded BEFORE he said them do not clear it")
    tx, root = world("typo", [human("keep the rot beats small and quiet please", "u1")],
                     [("keep the rot beasts small and quiet please", AFTER)])
    check(run(tx, root)[0] == 0, "a fixed typo still matches")
    tx, root = world("part", [human("Is it done? Keep the rot beasts small.", "u1")],
                     [("Keep the rot beasts small", AFTER)])
    check(run(tx, root)[0] == 0, "a sentence of a longer message clears it")
    tx, root = world("two", [human("Use blue paint here. Preserve all the backups.", "u1")], [("Use blue paint here", AFTER)])
    res = run(tx, root)[1]
    check(len(res["gaps"]) == 1 and "partly" in res["gaps"][0]["hint"] and "preserve" in res["gaps"][0]["hint"],
          "one ruling quoted of two leaves a gap naming the other")
    tx, root = world("neg", [human("Do not deploy to production today", "u1")], [("Do deploy to production today", AFTER)])
    check(run(tx, root)[0] == 1, "a quote that drops his negation does not clear it")
    tx, root = world("neg2", [human("Do not deploy today.", "u1")], [("Deploy today", AFTER)])
    check(run(tx, root)[0] == 1, "a quote inside his sentence that loses the not does not clear it")
    tx, root = world("neg3", [human("I do not want you to not deploy this now", "u1")],
                     [("I do not want you to deploy this now", AFTER)])
    check(run(tx, root)[0] == 1, "one negation of two lost does not clear it")
    tx, root = world("short", [human("Keep the backups. Delete production.", "u1")], [("Keep the backups", AFTER)])
    check(run(tx, root)[0] == 1, "a two-word ruling beside a longer one still needs its quote")
    tx, root = world("half", [human("Please back up the staging database, then delete production.", "u1")],
                     [("Please back up the staging database", AFTER)])
    check(run(tx, root)[0] == 1, "a quote of two thirds of his sentence does not clear it")
    tx, root = world("mixyes", [human("Yes. Keep the weekly backup.", "u1")], [("Keep the weekly backup", AFTER)])
    check(run(tx, root)[0] == 1, "a Yes beside a ruling stays a gap: it may approve something else")
    tx, root = world("order", [human("the art goes before the code ships", "u1")],
                     [("the code goes before the art ships", AFTER)])
    check(run(tx, root)[0] == 1, "the same words in another order do not clear it")
    tx, root = world("sec", [human("drop the old pipe art entirely", "u1", "2026-10-31T11:00:00.900Z")],
                     [("drop the old pipe art entirely", AFTER)])
    check(run(tx, root)[0] == 1, "a quote stamped in the message's own second may predate it: no clear")
    tx, root = world("stray", [human("build the hose tonight then stop", "u1")], [("hose", AFTER), ("the art", AFTER)])
    check(run(tx, root)[0] == 1, "a stray word on the ledger does not clear it")


def t_whose():
    ring = {"type": "user", "timestamp": T0, "uuid": "m1", "origin": {"kind": "task-notification"},
            "message": {"role": "user", "content": "[RimFlow ring] do the thing now"}}
    tx, root = world("ring", [ring])
    res = run(tx, root)[1]
    check(res["closeout"] == "ok" and res["messages"] == 0, "a machine ring is not his message")
    typed = {"type": "attachment", "timestamp": T0, "uuid": "q1", "attachment": {
        "type": "queued_command", "commandMode": "prompt", "origin": {"kind": "human"}, "prompt": "stop the art run now"}}
    tx, root = world("queued", [typed])
    check(run(tx, root)[0] == 1, "a message typed mid-turn lands only as queued_command: it still counts")
    tx, root = world("twice", [typed, human("stop the art run now", "u2", "2026-10-31T10:00:05.000Z")])
    check(len(run(tx, root)[1]["gaps"]) == 1, "queued then echoed is one message")


def t_exempt():
    tx, root = world("ex", [human("goodbye", "a"), human("Good night!", "b"), human("/compact now", "c"),
                            human("what is left on the hose?", "d")])
    res = run(tx, root)[1]
    check(res["closeout"] == "ok" and res["exempt"] == 4, "goodbye, slash command and a plain question are exempt")
    tx, root = world("qq", [human("What is left? Who owns it?", "a")])
    check(run(tx, root)[1]["exempt"] == 1, "two questions are still only questions")
    tx, root = world("yes2", [human("yes", "a", "2026-10-31T10:00:00.000Z"), human("yes", "b", "2026-10-31T10:05:00.000Z")])
    check(len(run(tx, root)[1]["gaps"]) == 2, "two plain yeses are two answers")
    tx, root = world("yes", [human("yes", "a")])
    res = run(tx, root)[1]
    check(len(res["gaps"]) == 1 and "assent" in res["gaps"][0]["hint"], "a bare yes stays a gap and says why")
    tx, root = world("mixed", [human("Drop the hose run. What is next?", "a")])
    check(run(tx, root)[0] == 1, "a ruling followed by a question is not a question")
    tx, root = world("cmdplus", [human("/help\nDelete production.", "a")])
    check(run(tx, root)[0] == 1, "a slash command with a ruling under it is not exempt")
    bare = dict(human("drop the old pipe art entirely", "a"), timestamp=None)
    check(CC.unquoted([CC.words(bare["message"]["content"])], None, [(5, CC.words("drop the old pipe art entirely"))]) != [],
          "a message with no time is not cleared by an old quote")
    tx, root = world("path", [human("/rm/bench is the wrong clone, use foundry", "a")])
    check(run(tx, root)[0] == 1, "a path at the start of a message is not a slash command")


def t_dismiss():
    tx, root = world("dis", [human("nice weather for it", "u9")])
    key = run(tx, root)[1]["gaps"][0]["key"]
    r = subprocess.run([sys.executable, os.path.join(HERE, "conductor_closeout.py"), "dismiss", "--key", key,
                        "--why", "chat, ruled on nothing"], capture_output=True, text=True, timeout=60)
    check(r.returncode == 0, "dismiss runs")
    rc, res = run(tx, root)
    check(rc == 0 and res["dismissed"] == 1, "a dismissed key is no longer a gap")
    os.remove(DISMISSED)


def t_blind():
    tx, root = world("bad", [human("drop it all", "u1")])
    with open(tx, "a") as f:
        f.write("{not json\n")
    rc, res = run(tx, root)
    check(rc == 3 and res["closeout"] == "unmeasured", "a malformed transcript is UNMEASURED, exit 3")
    tx, root = world("none", [human("drop it all", "u1")])
    check(run(os.path.join(root, "absent.jsonl"), root)[0] == 3, "a missing transcript is UNMEASURED")
    os.remove(os.path.join(root, "infrastructure", "state", "ledger", "events", "OWNER.jsonl"))
    check(run(tx, root)[0] == 3, "no ledger is UNMEASURED, not a clean window")
    tx, root = world("empty", [human("drop it all", "u1")])
    with open(os.path.join(root, "infrastructure", "state", "ledger", "events", "OWNER.jsonl"), "w") as f:
        f.write('{"event": "close", "ts": "2020-01-01T00:00:00Z"}\n')
    check(run(tx, root)[0] == 3, "a ledger with no quote at all is a blind instrument, UNMEASURED")
    tx, root = world("utf", [human("drop it all", "u1")])
    with open(os.path.join(root, "infrastructure", "state", "ledger", "events", "OWNER.jsonl"), "ab") as f:
        f.write(b'{"ownerSaid": "\xff"}\n')
    check(run_rc(tx, root) == 3, "invalid UTF-8 in a shard is UNMEASURED, not a crash")
    tx, root = world("baddis", [human("drop it all", "u1")])
    with open(DISMISSED, "w") as f:
        f.write("{torn")
    check(run(tx, root)[0] == 3, "an unreadable dismissal file is UNMEASURED")
    os.remove(DISMISSED)


def t_real_ledger():
    """Sanity probe: the instrument sees the real ledger, and a real quote clears a message saying it."""
    q = CC.ledger_quotes(REPO)
    check(len(q) > 100, "the real ledger yields quotes (%d)" % len(q))
    at, w = max(q, key=lambda x: len(x[1]) if len(x[1]) < 30 else 0)
    check(CC.covered(w, w), "a real quote covers itself")


def t_carry():
    tx, root = world("carry", [human("rename the pump to sump", "u1"), human("goodbye", "u2")])
    old = SR.REPO
    SR.REPO = root
    try:
        out = SR.closeout_check(tx, {"seat_log": os.path.join(TMP, "log.md"), "goodbye_phrases": ["goodbye"]})
        check(out["closeout"] == "partial" and len(out["gaps"]) == 1, "the request's check stores verdict and gaps")
        check(SR.closeout_check(os.path.join(root, "no.jsonl"), {})["closeout"] == "unmeasured",
              "the request's check on an unreadable transcript is unmeasured")
        tx2, root2 = world("carry2", [human("goodbye", "u3")])
        SR.REPO = root2
        old_inh = SR.inherited_gaps
        SR.inherited_gaps = lambda: out["gaps"]
        inherited = SR.closeout_check(tx2, {"seat_log": os.path.join(TMP, "log.md"), "goodbye_phrases": ["goodbye"]})
        SR.inherited_gaps = old_inh
        SR.REPO = root
        check(inherited["closeout"] == "partial" and inherited["gaps"] == out["gaps"],
              "a clean window does not report ok over the last window's open gap")
        long_text = "keep the first part. " * 200 + "delete the second part."
        g = CC.evaluate([{"key": "k", "ts": 1.0, "text": long_text}], None, root, DISMISSED)["gaps"][0]
        _, root3 = world("cut", [], [("keep the first part", AFTER)])
        check(len(g["text"]) < len(long_text) and CC.still_open([g], root3, DISMISSED) == [g],
              "a gap cut for display stays open on the sentence past the cut")
        blind = SR.closeout_check(os.path.join(root, "gone.jsonl"), {})
        SR.inherited_gaps = lambda: blind["gaps"]
        tx4, root4 = world("after_blind", [human("goodbye", "u3")])
        SR.REPO = root4
        after = SR.closeout_check(tx4, {"seat_log": os.path.join(TMP, "log.md"), "goodbye_phrases": ["goodbye"]})
        SR.inherited_gaps = old_inh
        SR.REPO = root
        check(after["closeout"] == "partial" and "gone.jsonl" in after["gaps"][0]["text"],
              "a clean window does not report ok over a transcript nobody could read")
        kr = SR._kill_record("BENCH", {"pid": 1, "session_id": "s", "argv": []}, {"seat_restart": {"enabled": True}},
                             dict(out, tx_path=tx), 1, 2)
        check(kr.get("closeout") == "partial" and kr.get("gaps") == out["gaps"], "the killed record carries the gaps")
        import contextlib
        import io
        def wake(rec):
            b = io.StringIO()
            with contextlib.redirect_stdout(b):
                SR._wake_gaps(rec, {"seat_log": os.path.join(TMP, "log.md")})
            return b.getvalue()
        SR.inherited_gaps = lambda: out["gaps"]
        forced = SR._kill_record("BENCH", {"pid": 1, "session_id": "s", "argv": []},
                                 {"seat_restart": {"enabled": True, "seats": {"BENCH": {"kind": "conductor"}}}}, {}, 1, 2)
        SR.inherited_gaps = old_inh
        check(forced.get("closeout") == "partial" and forced.get("gaps") == out["gaps"],
              "a forced restart keeps the gaps of the record it overwrites")
        check("rename the pump to sump" in wake(kr), "the wake prints an open gap whole")
        ev = os.path.join(root, "infrastructure", "state", "ledger", "events", "OWNER.jsonl")
        with open(ev, "a") as f:
            f.write(json.dumps({"event": "note", "ownerSaid": "rename the pump to sump", "ts": AFTER}) + "\n")
        o = wake(kr)
        check("rename the pump" not in o and "since been recorded" in o, "once recorded the wake stops printing it")
        check("UNMEASURED" in wake({"closeout": "unmeasured", "tx_path": tx}), "the wake says an unmeasured close-out")
        check(wake({"closeout": "ok"}) == "", "an ok close-out adds nothing to the wake")
    finally:
        SR.REPO = old


def t_wired():
    with open(os.path.join(REPO, ".claude", "hooks", "conductor_goodbye.py"), encoding="utf-8") as f:
        hook = f.read()
    check("conductor_closeout.py check" in hook, "the goodbye hook's close-out runs the check")
    check("OWNER.jsonl" in hook, "the close-out publishes OWNER.jsonl, where --owner-said writes")
    with open(SR.__file__, encoding="utf-8") as f:
        src = f.read()
    check("req.update(closeout_check(path, cfg))" in src, "the goodbye request runs the check")


for t in (t_diff, t_whose, t_exempt, t_dismiss, t_blind, t_real_ledger, t_carry, t_wired):
    t()
print("\nPASS: 0 failure(s)" if not fails else "\nFAIL: %d failure(s)" % fails)
sys.exit(1 if fails else 0)
