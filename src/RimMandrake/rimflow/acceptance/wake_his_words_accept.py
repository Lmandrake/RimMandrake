#!/usr/bin/env python3
"""wake_his_words_accept.py: the acceptance test of RIMMANDRAKE_SHOW_HIS_WORDS_AT_WAKE_FRESH_WINDOW_DENIED_A_MOD_PASS.

The failure (2026-11-23): the Conductor restarted at its 400k limit; his "GSS walk full pass. Looks great!" was on the
OWNER shard; the wake printed none of it, and the fresh window read a later stale note and told him the mod was not
passed. This test runs the whole `seat_restart.py wake` (cmd_wake) for a Conductor seat on a throwaway clone, ledger,
dispatcher state and ~/.claude, rebuilt as at that moment:
  - the OWNER shard holds his pass words on the GSS item (and one recorded message, must-stay-green);
  - a later BENCH note says "He did not say the walk passed" (the stale note);
  - GimmeSomeSlack's stage record is at Stage 8, his walk;
  - the old window's transcript holds one message he typed that no ledger event records.
It needs, in the wake's output: the pass words above the seat log; the GimmeSomeSlack line in EACH MOD NOW with the pass
words; the unrecorded message printed whole; the recorded one not printed as homeless. A second case makes the old
transcript unreadable and needs UNMEASURED, never "looked: none", for his typed messages.

  wake_his_words_accept.py                    the test on this tree's code. Exit 0 pass, 1 fail, 3 could not run
  wake_his_words_accept.py --code DIR         the same on another tree's rimflow folder (the parent commit's, to see red)
  wake_his_words_accept.py --mutants          the planted faults: an unmutated copy must pass, each mutant must fail
"""
import argparse
import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
PASS_WORDS = "GSS walk full pass. Looks great!"
UNRECORDED = "Run the FlowWorks look on Steve1 next, not on ArchBig, and tell me when it is staged."
RECORDED = "Thin outline please, the black one reads best on ember grass."
STALE = "He did not say the walk passed. The GSS walk stays open."
T_PASS = 1795413364.0      # 2026-11-22 9:56 PM PST


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def build(tmp):
    """-> (clone, old transcript path, schedule) for the 2026-11-23 failure."""
    clone = os.path.join(tmp, "clone")
    ev = os.path.join(clone, "infrastructure", "state", "ledger", "events")
    os.makedirs(ev)
    item = "RIMMANDRAKE_STAGE_SLACK_SHORT_LOOK_AT_FOUR_CHANGES_THEN_HIS_PASS"
    owner = [{"seat": "OWNER", "event": "file", "id": item, "ts": iso(T_PASS - 9000), "tsn": int((T_PASS - 9000) * 1e9),
              "title": "Stage Gimme Some Slack's short look, then his pass", "ownerSaid": "Stage the GSS look"},
             {"seat": "OWNER", "event": "note", "id": item, "ts": iso(T_PASS), "tsn": int(T_PASS * 1e9),
              "text": "His pass at his walk of Gimme Some Slack 0.1.1", "ownerSaid": PASS_WORDS},
             {"seat": "OWNER", "event": "note", "id": "RIMMANDRAKE_OUTLINE_ULLAI", "ts": iso(T_PASS + 300),
              "tsn": int((T_PASS + 300) * 1e9), "ownerSaid": "Thin outline please, the black one reads best on ember "
                                                             "grass."}]
    bench = [{"seat": "BENCH", "event": "note", "id": item, "ts": iso(T_PASS + 1020), "tsn": int((T_PASS + 1020) * 1e9),
              "text": STALE}]
    for name, rows in (("OWNER", owner), ("BENCH", bench)):
        with open(os.path.join(ev, name + ".jsonl"), "w") as f:
            f.write("".join(json.dumps(r) + "\n" for r in rows))
    vd = os.path.join(clone, "design", "concepts", "GimmeSomeSlack", "version")
    os.makedirs(vd)
    with open(os.path.join(vd, "stage_record.json"), "w") as f:
        json.dump({"mod": "GimmeSomeSlack", "version": "0.1.1", "stage": "his_walk",
                   "since": "2026-11-21T22:32:25-08:00", "moves": []}, f)
    import seat_restart as SR
    tx = SR.transcript_path(clone, "old-window")
    os.makedirs(os.path.dirname(tx))

    def u(t, text):
        return {"type": "user", "timestamp": iso(t), "uuid": "u%d" % int(t), "entrypoint": "cli",
                "message": {"role": "user", "content": text}, "origin": {"kind": "human"}, "promptSource": "typed"}

    def a(t, text):
        return {"type": "assistant", "timestamp": iso(t), "entrypoint": "cli",
                "message": {"role": "assistant", "stop_reason": "end_turn", "content": [{"type": "text", "text": text}]}}
    recs = [{"type": "custom-title", "customTitle": "CONDUCTOR", "sessionId": "old-window"},
            u(T_PASS - 10000, "Good evening."), a(T_PASS - 9990, "Evening."),
            u(T_PASS - 60, "GSS walk full pass. Looks great!"), a(T_PASS - 50, "Recorded."),
            u(T_PASS + 290, RECORDED), a(T_PASS + 295, "Thin outline it is."),
            u(T_PASS + 900, UNRECORDED), a(T_PASS + 910, "Yes.")]
    with open(tx, "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in recs))
    sch = {"seat_restart": {"enabled": True, "seats": {"BENCH": {"kind": "conductor"}}},
           "seats": {"BENCH": {"session_name": "CONDUCTOR", "clone": clone}}}
    holds = os.path.join(tmp, "holds.json")
    with open(holds, "w") as f:
        json.dump({"holds": []}, f)
    os.environ["RM_OWNER_HOLD_FILE"] = holds
    restart = os.path.join(tmp, "state", "restart")
    os.makedirs(restart)
    with open(os.path.join(restart, "BENCH.killed.json"), "w") as f:
        json.dump({"seat": "BENCH", "session_id": "old-window", "killed_at": T_PASS + 3700, "gen": "g-400k",
                   "source": "backstop_hard", "tx_path": tx, "tx_offset": os.path.getsize(tx)}, f)
    with open(os.path.join(restart, "BENCH.wake_words.json"), "w") as f:     # the wake that opened the old window
        json.dump({"seat": "BENCH", "at": T_PASS - 10000, "since": T_PASS - 20000, "session": "older-window"}, f)
    return clone, tx, sch


def run_wake(sch):
    import seat_restart as SR
    import doorbell
    SR._schedule = lambda: sch
    doorbell.claude_ancestor = lambda *a, **k: None
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        SR.cmd_wake(argparse.Namespace(seat="BENCH", lines=5, gen=None))
    return out.getvalue()


def section(text, head):
    i = text.find(head)
    if i < 0:
        return ""
    j = text.find("\n== ", i + 1)
    return text[i:] if j < 0 else text[i:j]


def child(code, mutant, case):
    """Run one case in this process; print PASS/FAIL lines; -> exit code."""
    tmp = tempfile.mkdtemp(prefix="wake_accept_")
    os.environ.update({"RM_DISPATCHER_STATE": os.path.join(tmp, "state"),
                       "CLAUDE_CONFIG_DIR": os.path.join(tmp, "claude"),
                       "RM_SEAT_LOG_DIR": os.path.join(tmp, "seat_log")})
    sys.path.insert(0, code)
    import seat_restart as SR
    if os.path.dirname(os.path.abspath(SR.__file__)) != os.path.abspath(code):
        print("COULD NOT RUN: seat_restart imported from %s, not %s" % (SR.__file__, code))
        return 3
    if mutant:
        spec = importlib.util.spec_from_file_location("wake_words", mutant)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["wake_words"] = mod
        spec.loader.exec_module(mod)
    clone, tx, sch = build(tmp)
    fails = []

    def check(ok, what):
        print(("PASS " if ok else "FAIL ") + what)
        if not ok:
            fails.append(what)
    if case == "unreadable":
        os.chmod(tx, 0)
        out = run_wake(sch)
        os.chmod(tx, 0o600)
        s = section(out, "== HIS TYPED MESSAGES")
        check(bool(s) and "UNMEASURED" in s and "looked: none" not in s,
              "an unreadable old transcript reads UNMEASURED for his typed messages, never none")
    else:
        out = run_wake(sch)
        seat_log = out.find("== seat log tail")
        check(PASS_WORDS in out, "the wake prints his pass words")
        top = out.find(PASS_WORDS)
        check(0 <= top < seat_log, "his pass words are above the seat log (the top of the wake)")
        mods = section(out, "== EACH MOD NOW")
        gss = [ln for ln in mods.splitlines() if ln.startswith("- GimmeSomeSlack")]
        check(bool(gss) and "Stage 8" in gss[0] and PASS_WORDS in mods,
              "EACH MOD NOW gives GimmeSomeSlack's stage with his pass words")
        home = section(out, "== HIS TYPED MESSAGES WITH NO HOME")
        check(UNRECORDED in home, "the unrecorded typed message is printed whole")
        check(bool(home) and RECORDED not in home, "a recorded typed message is not printed as homeless")
    if os.environ.get("WAKE_ACCEPT_SHOW"):
        print(out)
    shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failed" % ("FAIL" if fails else "ALL PASS", len(fails)))
    return 1 if fails else 0


def run_child(code, mutant=None, case="main"):
    argv = [sys.executable, os.path.abspath(__file__), "--child", "--code", code, "--case", case]
    if mutant:
        argv += ["--mutant", mutant]
    r = subprocess.run(argv, capture_output=True, text=True, timeout=600)   # hang guard: a whole case runs in ~3 s
    return r.returncode, r.stdout + r.stderr


# Each plant: (name, anchor in wake_words.py, replacement, the case that must go red).
MUTANTS = [
    ("drop the pass event from the output",
     "            out.append(e)\n        return out\n\n    def owner_bad",
     "            if 'pass' not in str(e.get('ownerSaid') or '').lower():\n                out.append(e)\n"
     "        return out\n\n    def owner_bad", "main"),
    ("mark an unrecorded message as matched",
     "    if not words:\n        return None, None\n", "    if not words or True:\n        return 'QUOTED', None\n", "main"),
    ("an unreadable transcript reported as none",
     '            blind.append("%s: unreadable" % p)\n            continue',
     "            continue", "unreadable"),
]


def mutants(code):
    src = os.path.join(code, "wake_words.py")
    with open(src) as f:
        orig = f.read()
    tmp = tempfile.mkdtemp(prefix="wake_mutants_")
    rows, bad = [], 0
    ctl = os.path.join(tmp, "control.py")
    with open(ctl, "w") as f:
        f.write(orig)
    for case in ("main", "unreadable"):
        rc, out = run_child(code, ctl, case)
        ok = rc == 0
        rows.append(("control (unmutated copy), case %s" % case, "green" if ok else "RED", ok))
        bad += not ok
    for i, (name, anchor, repl, case) in enumerate(MUTANTS):
        if orig.count(anchor) != 1:
            rows.append((name, "DID NOT APPLY (anchor found %d times)" % orig.count(anchor), False))
            bad += 1
            continue
        p = os.path.join(tmp, "m%d.py" % i)
        with open(p, "w") as f:
            f.write(orig.replace(anchor, repl))
        rc, out = run_child(code, p, case)
        caught = rc == 1 and "FAIL " in out
        rows.append((name, "caught" if caught else ("NOT CAUGHT" if rc == 0 else "harness broke rc=%d" % rc), caught))
        bad += not caught
    shutil.rmtree(tmp, ignore_errors=True)
    for name, verdict, _ in rows:
        print("%-55s %s" % (name, verdict))
    print("%s: %d of %d rows as required" % ("ALL PASS" if not bad else "FAIL", len(rows) - bad, len(rows)))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", default=RIMFLOW)
    ap.add_argument("--mutants", action="store_true")
    ap.add_argument("--child", action="store_true")
    ap.add_argument("--mutant")
    ap.add_argument("--case", default="main")
    a = ap.parse_args(argv)
    if a.child:
        return child(os.path.abspath(a.code), a.mutant, a.case)
    if a.mutants:
        return mutants(os.path.abspath(a.code))
    worst = 0
    for case in ("main", "unreadable"):
        rc, out = run_child(os.path.abspath(a.code), None, case)
        print(out.rstrip())
        worst = max(worst, rc if rc in (0, 1) else 3)
    return worst


if __name__ == "__main__":
    sys.exit(main())
