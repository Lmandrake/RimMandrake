#!/usr/bin/env python3
"""Selftest: the station note box (STATION_NOTEBOX_BUILD_WHISPER_AT_NEXT_TURN, src/RimMandrake/rimflow/notebox.py).

A note sent to item X is bound to the gen running then, stored durably, and handed by the PostToolUse/Stop hook
(.claude/hooks/notebox_deliver.py, run through its REGISTERED command string as Claude Code runs it) exactly once,
only to a session whose clone marker + RELENTLESS_GEN is X at that gen; never to another item, a later gen, or a
subagent's tool call. Send and delivery both stay in the record (notes.jsonl, store journal, learned.md).
All in a throwaway RELENTLESS_ROOT and throwaway git clones; the real store is never touched.

    python3 src/RimMandrake/Utils/selftest_notebox.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
import notebox  # noqa: E402

FAILS = []


def check(cond, what):
    if not cond:
        FAILS.append(what)
        print("FAIL " + what)


def state(base, item, gen, status):
    d = os.path.join(base, "store", "items", item)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "state.json"), "w") as f:
        json.dump({"item": item, "gen": gen, "status": status}, f)


def clone(tmp, name, item, gen):
    d = os.path.join(tmp, name)
    os.makedirs(d)
    subprocess.run(["git", "init", "-q", d], check=True)
    if item:
        with open(os.path.join(d, ".git", "relentless.json"), "w") as f:
            json.dump({"item": item, "gen": gen}, f)
    os.makedirs(os.path.join(d, "src", "RimMandrake"))
    os.symlink(os.path.join(REPO, "src", "RimMandrake", "rimflow"), os.path.join(d, "src", "RimMandrake", "rimflow"))
    os.makedirs(os.path.join(d, ".claude"))
    os.symlink(os.path.join(REPO, ".claude", "hooks"), os.path.join(d, ".claude", "hooks"))
    return d


def registered(event):
    with open(os.path.join(REPO, ".claude", "settings.json")) as f:
        hooks = json.load(f)["hooks"]
    return [h["command"] for g in hooks.get(event, []) for h in g["hooks"] if "notebox_deliver.py" in h["command"]]


def run_hook(cmd, proj, ev, base, gen_env=None):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=proj, RELENTLESS_ROOT=base)
    env.pop("RELENTLESS_GEN", None)
    if gen_env is not None:
        env["RELENTLESS_GEN"] = str(gen_env)
    p = subprocess.run(["sh", "-c", cmd], input=json.dumps(ev), capture_output=True, text=True, env=env, cwd=proj,
                       timeout=30)
    check(p.returncode == 0, "hook exits 0 (got %d: %s)" % (p.returncode, p.stderr[-200:]))
    return json.loads(p.stdout) if p.stdout.strip() else None


def main():
    post, stop = registered("PostToolUse"), registered("Stop")
    check(len(post) == 1 and "PostToolUse" in post[0], "one PostToolUse registration of notebox_deliver.py")
    check(len(stop) == 1 and stop[0].rstrip().split("notebox_deliver.py\"")[1].split()[0] == "Stop",
          "one Stop registration of notebox_deliver.py passing Stop")
    if FAILS:
        return 1
    post, stop = post[0], stop[0]
    tmp = tempfile.mkdtemp(prefix="selftest_notebox_")
    try:
        base = os.path.join(tmp, "root")
        X, Y = "ITEM_X_TEST", "ITEM_Y_TEST"
        state(base, X, 3, "running")
        state(base, Y, 1, "queued")
        # sending
        nid, why = notebox.send(X, "use the earlier texture", by="owner", base=base)
        check(nid and why is None, "send to a running item gives an id (%s)" % why)
        check(notebox.send(Y, "hello", base=base)[0] is None, "send to a queued item without --gen is refused")
        check(notebox.send(X, "   ", base=base)[0] is None, "an empty note is refused")
        check(notebox.send("NO_SUCH_ITEM", "x", base=base)[0] is None, "send to an unknown item is refused")
        n = notebox.notes(X, base)
        check(len(n) == 1 and n[0]["gen"] == 3 and n[0]["state"] == "pending", "the note is bound to gen 3, pending")
        cx = clone(tmp, "cx", X, 3)
        cy = clone(tmp, "cy", Y, 3)
        cnone = clone(tmp, "plain", None, 0)
        ev = {"hook_event_name": "PostToolUse", "tool_name": "Bash", "session_id": "s1"}
        # never to the wrong place
        check(run_hook(post, cy, dict(ev, cwd=cy), base) is None, "another item's clone receives nothing")
        check(run_hook(post, cnone, dict(ev, cwd=cnone), base, gen_env=3) is None, "a non-Relentless clone receives nothing")
        check(run_hook(post, cx, dict(ev, cwd=cx), base) is None,
              "a session in X's clone without RELENTLESS_GEN (not the worker) receives nothing")
        check(run_hook(post, cy, dict(ev, cwd=cx), base, gen_env=3) is None,
              "a Y worker whose tool cwd wandered into X's clone receives nothing (the item is the project's)")
        check(run_hook(post, cx, dict(ev, cwd=cx), base, gen_env=2) is None, "an older gen of X receives nothing")
        check(run_hook(post, cx, dict(ev, cwd=cx), base, gen_env=4) is None, "a later gen of X receives nothing")
        check(run_hook(post, cx, dict(ev, cwd=cx, agent_id="sub1"), base, gen_env=3) is None,
              "a subagent's tool call receives nothing")
        check(notebox.notes(X, base)[0]["state"] == "pending", "after the misses the note is still pending")
        # delivered once, to X gen 3
        out = run_hook(post, cx, dict(ev, cwd=cx), base, gen_env=3)
        ctx = ((out or {}).get("hookSpecificOutput") or {})
        check(ctx.get("hookEventName") == "PostToolUse" and "use the earlier texture" in (ctx.get("additionalContext") or "")
              and nid in ctx.get("additionalContext", ""), "X gen 3 gets the note as additionalContext")
        check(run_hook(post, cx, dict(ev, cwd=cx), base, gen_env=3) is None, "a second tool call gets nothing (once)")
        n = notebox.notes(X, base)[0]
        check(n["state"] == "delivered" and n["event"] == "PostToolUse" and n["session"] == "s1",
              "the record shows it delivered, by PostToolUse, to session s1")
        # Stop blocks with a pending note, also during a forced continuation (a note that came meanwhile), and only
        # while one is pending: the continuation then ends
        nid2, _ = notebox.send(X, "also check the north facing\nand the west", base=base)
        out = run_hook(stop, cx, {"hook_event_name": "Stop", "cwd": cx, "session_id": "s1", "stop_hook_active": False},
                       base, gen_env=3)
        check((out or {}).get("decision") == "block" and "north facing" in (out or {}).get("reason", ""),
              "a note pending at Stop blocks the stop with the note as the reason")
        check(run_hook(stop, cx, {"hook_event_name": "Stop", "cwd": cx, "stop_hook_active": True}, base, gen_env=3)
              is None, "the forced continuation's Stop, nothing pending, does not block again")
        nid2b, _ = notebox.send(X, "one more", base=base)
        out = run_hook(stop, cx, {"hook_event_name": "Stop", "cwd": cx, "stop_hook_active": True}, base, gen_env=3)
        check((out or {}).get("decision") == "block" and "one more" in (out or {}).get("reason", ""),
              "a note that arrived during the forced continuation is still delivered at its Stop")
        # a held lock never stalls the session: the hook gives up, the note stays pending
        import fcntl
        nid2c, _ = notebox.send(X, "while locked", base=base)
        fd = os.open(os.path.join(base, "store", "items", X, "notes.lock"), os.O_RDWR)
        fcntl.flock(fd, fcntl.LOCK_EX)
        import time
        t0 = time.monotonic()
        out = run_hook(post, cx, dict(ev, cwd=cx), base, gen_env=3)
        took = time.monotonic() - t0
        os.close(fd)
        check(out is None and took < 8, "a held note lock: nothing delivered, back in %.1f s" % took)
        check([n["state"] for n in notebox.notes(X, base) if n["id"] == nid2c] == ["pending"],
              "the note sent while locked is still pending")
        check(run_hook(post, cx, dict(ev, cwd=cx), base, gen_env=3) is not None, "and is delivered once the lock frees")
        # a note left for an ended gen stays pending; --gen binds a later one on purpose
        nid3, _ = notebox.send(X, "for the next worker", gen=4, base=base)
        check(run_hook(post, cx, dict(ev, cwd=cx), base, gen_env=3) is None, "gen 3 does not get a gen 4 note")
        check(run_hook(post, cx, dict(ev, cwd=cx), base, gen_env=4) is not None, "gen 4 gets its note")
        # the record
        recs = notebox.records(X, base)
        check([r["kind"] for r in recs].count("sent") == 5 and [r["kind"] for r in recs].count("delivered") == 5,
              "notes.jsonl holds 5 sent + 5 delivered")
        with open(os.path.join(base, "store", "journal.jsonl")) as f:
            j = [json.loads(x) for x in f]
        check(sum(r["do"] == "note_sent" for r in j) == 5 and sum(r["do"] == "note_delivered" for r in j) == 5,
              "the store journal has every send and delivery")
        with open(os.path.join(base, "store", "items", X, "learned.md")) as f:
            learned = f.read()
        check(all(t in learned for t in (nid, nid2, nid2b, nid2c, nid3)),
              "learned.md carries each delivered note to the next brief")
        check("also check the north facing and the west" in learned and '"' not in learned
              and len(learned.splitlines()) == 5, "learned.md lines are plain text, one per note, not JSON-quoted")
        # the CLI
        p = subprocess.run([sys.executable, os.path.join(REPO, "src", "RimMandrake", "rimflow", "notebox.py"), "show", X],
                           capture_output=True, text=True, env=dict(os.environ, RELENTLESS_ROOT=base), timeout=30)
        check(p.returncode == 0 and p.stdout.count("delivered") >= 3, "notebox.py show lists the notes")
        p = subprocess.run([sys.executable, os.path.join(REPO, "src", "RimMandrake", "rimflow", "notebox.py"), "send", Y,
                            "x"], capture_output=True, text=True, env=dict(os.environ, RELENTLESS_ROOT=base), timeout=30)
        check(p.returncode == 2 and "REFUSED" in p.stderr, "notebox.py send to a non-running item exits 2")
        # a broken event never breaks the session
        p = subprocess.run(["sh", "-c", post], input="not json", capture_output=True, text=True, cwd=cx, timeout=30,
                           env=dict(os.environ, CLAUDE_PROJECT_DIR=cx, RELENTLESS_ROOT=base, RELENTLESS_GEN="3"))
        check(p.returncode == 0 and not p.stdout.strip(), "a malformed event: exit 0, nothing printed")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if FAILS:
        print("FAIL selftest_notebox: %d" % len(FAILS))
        return 1
    print("PASS selftest_notebox")
    return 0


if __name__ == "__main__":
    sys.exit(main())
