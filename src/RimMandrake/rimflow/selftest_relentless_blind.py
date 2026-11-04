#!/usr/bin/env python3
"""A checker that cannot reach its evidence says UNMEASURED, and that is no FAIL (CHECKER_SANDBOX_FIX_BLIND_TO_STEVE).
STEVE_DISK_MEASURE_ONLY_FORTY_GIGS_LEFT was done at gen 1; the walled Marker could not ssh the machine nor see
/mnt/d/ClaudeWork, said FAIL, and the item looped to gen 9. Rows: the classifier on reasons Markers really wrote
(store attempts, 2026-11-01..04), the STEVE shape replayed through the real tick on selftest_relentless's rig (no gen,
no return, no approach change; a re-check; the same blindness twice holds for repair, routed to the seat, not to him;
unhold re-checks the same sha), and the off-box reading the supervisor hands in.
GPT review of 0135b04912, one row group each: F1 no worker-authored command crosses the wall (adapter names only, run
from an empty folder); F2 a named defect is never hidden by blindness; F3 a structured unreached-only verdict is
UNMEASURED even when its prose says "red"; F4 offbox output is bounded while it is read; F5 the check's identity is on
disk before any offbox reading runs."""
import base64
import json
import os
import stat
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                  # noqa: E402
import relentless_wall as W             # noqa: E402
import selftest_relentless as T         # noqa: E402

FAILS = []

# what Markers wrote, cut from the store's attempts (corpus: D:\ClaudeWork\rimmandrake\checker_blind\corpus.jsonl)
STEVE_G1 = ("Doc clauses hold: infrastructure/state/facts/steve_c_drive_fill_2026-11-03.md is non-empty and has '## What "
            "fills C:'. The live clause (C: free >=55GB) could not be run from this checker: the proof's ssh stevedesktop "
            "exits 255 ('Bad owner or permissions on /etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf').")
STEVE_G7 = ("Ran the contract proof: exit 0 (the report has both sections and free_bytes=68354924544). The item's second "
            "clause, 'clear what is ours', is an act on SteveDesktop's C:, and I could not show it either way: ssh "
            "stevedesktop fails in this sandbox (ssh_config.d perms; with -F /dev/null, known_hosts permission denied).")
ALARM_G3 = ("One clause cannot be shown either way from here: 'remove the lines'. The other clauses hold. This is not "
            "evidence that the lines are still in the log; the log could not be read at all. UNSHOWN: "
            "/mnt/d/ClaudeWork/rimmandrake/conductor/log.md is behind an empty mask. conductor_log_receipt.py check "
            "printed NOT VISIBLE.")
REAL = {
    "LEVELLING_TICK g1": "The contract's proof is red. run_selftests.py could not run here (sandbox D: is not visible to "
                         "dotnet.exe), so I ran dotnet run on this export: exit 1, 1148 ok, 2 FAIL.",
    "FOCUS_CAP g1": "selftest_focus_cap.py passes 25/25, but the cap leaks on the real path, so 'next holds the WIP cap' is "
                    "false.",
    "HMGHDI g1": "ssh to the box fails in this sandbox, but the cause is in this commit: the parser drops the last row.",
    "plain": "Clause 2 is missing: the selftest never runs the new branch.",
}


def ok(cond, name):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


GPT_HIDDEN = "ssh host timed out; the parser drops the last row (expected 8, got 7)"
GPT_RED_UNMEASURED = "proof is red; 2 FAIL in selftest_x"
GPT_RED_BLIND = "proof is red: ssh exits 255, so the reading never ran; no measurement"
ADAPTER = "steve_c_free"


def t_classifier():
    for name, text in (("STEVE g1", STEVE_G1), ("STEVE g7", STEVE_G7), ("SELFTEST_ALARM g3", ALARM_G3)):
        word, blind = W.read_as("FAIL", text)
        ok(word == W.UNMEASURED and blind, "%s: a FAIL that only says it could not reach is read UNMEASURED" % name)
    for name, text in REAL.items():
        ok(W.read_as("FAIL", text) == ("FAIL", None), "%s: a red proof stays FAIL, blindness beside it or not" % name)
    ok(W.read_as("UNMEASURED", "CANNOT REACH: ssh stevedesktop exit 255")[0] == W.UNMEASURED, "the word itself stands")
    ok(W.read_as("WEAK", STEVE_G1) == ("WEAK", None), "only FAIL is re-read: a WEAK is the Marker's call on the proof")
    ok(W.read_as("PASS", STEVE_G1) == ("PASS", None), "a PASS is never re-read")
    # the narrower WEAK is live (owner by card 2026-11-03, "Narrow it now")
    ok(W.read_as("WEAK", "GAP:OTHER. my own mutant of the parser stays green") == ("PASS", None), "GAP:OTHER is a PASS")
    ok(W.read_as("WEAK", "GAP:DIFF. reverting the commit's guard stays green") == ("WEAK", None), "GAP:DIFF holds")
    ok(W.read_as("WEAK", "GAP:OTHER", [], []) == ("PASS", None), "GAP:OTHER is a PASS, structured too")
    ok(W.read_as("WEAK", "GAP:OTHER", ["row 7 is dropped"], []) == ("FAIL", None), "a defect still beats a GAP:OTHER")
    ok(W.UNMEASURED in W.WORDS and "UNMEASURED" in W.VERDICT_SCRIPT, "the box's verdict script takes the word")
    ok(any("UNMEASURED" in line and "not a FAIL" in line for line in W.RULE), "the rule says inability is no FAIL")
    # F2: old-format prose is biased to FAIL when a defect is named
    ok(W.read_as("FAIL", GPT_HIDDEN) == ("FAIL", None), "F2: an ssh timeout beside 'expected 8, got 7' stays FAIL")
    ok(W.read_as("UNMEASURED", GPT_RED_UNMEASURED) == ("FAIL", None), "F2: an UNMEASURED naming a red proof is FAIL")
    # structured: the defect list decides, the prose does not
    ok(W.read_as("FAIL", GPT_HIDDEN, ["expected 8 rows, got 7"], ["ssh host timed out"]) == ("FAIL", None),
       "F2: structured, any --defect is FAIL whatever it could not reach")
    ok(W.read_as("UNMEASURED", "x", ["a red test"], ["ssh"])[0] == "FAIL", "F2: structured UNMEASURED with a defect is FAIL")
    ok(W.read_as("PASS", "x", ["a wrong number"], [])[0] == "FAIL", "F2: an observed defect under PASS is FAIL")
    got = W.read_as("FAIL", GPT_RED_BLIND, [], ["ssh stevedesktop exits 255"])
    ok(got[0] == W.UNMEASURED and "255" in got[1], "F3: structured unreached-only is UNMEASURED though its prose says red")
    ok(W.read_as("FAIL", GPT_RED_BLIND) == ("FAIL", None), "F3: the same prose, old format, stays FAIL (biased)")
    ok(W.read_as("FAIL", "a clause is not done", [], []) == ("FAIL", None), "structured FAIL with neither list is FAIL")
    ok(W.read_as("PASS", "ran it", [], ["the live clause"])[0] == W.UNMEASURED,
       "R2-1: a PASS naming evidence it could not reach is UNMEASURED, never a close")
    ok(W.read_as("PASS", "ran it", ["8 != 7"], ["the live clause"])[0] == "FAIL", "R2-1: and with a defect beside it, FAIL")
    ok(W.read_as("PASS", "ran it", [], []) == ("PASS", None), "a structured PASS with neither list is PASS")
    ok(W.read_as("PASS", "ran it", None, [" ", "\t"]) == ("PASS", None), "R2-2: blank unreached entries are no entries")


def t_verdict_script():
    """F2/F3: the box's own script records the two lists apart and refuses an UNMEASURED that cannot say what."""
    d = tempfile.mkdtemp(prefix="rl-verdict-")
    v = os.path.join(d, "verdict")
    with open(v, "w", encoding="utf-8") as f:
        f.write(W.VERDICT_SCRIPT)
    run = lambda *a: subprocess.run([sys.executable, v, *a], capture_output=True, text=True, timeout=30)
    ok(run("UNMEASURED", "CANNOT REACH: ssh").returncode != 0, "F3: UNMEASURED with no --unreached is refused")
    ok(run("UNMEASURED", "x", "--unreached", "ssh", "--defect", "8 != 7").returncode != 0,
       "F2: UNMEASURED with a --defect is refused: say FAIL")
    ok(not os.path.exists(os.path.join(d, "verdict.json")), "a refused verdict writes nothing")
    ok(run("FAIL", GPT_HIDDEN, "--defect", "expected 8, got 7", "--unreached", "ssh host timed out").returncode == 0,
       "a FAIL with both lists is recorded")
    got = W.read_verdict(d)
    ok(got["defects"] == ["expected 8, got 7"] and got["unreached"] == ["ssh host timed out"], "read_verdict returns both lists")
    ok(W.read_as(got["word"], got["reasons"], got["defects"], got["unreached"])[0] == "FAIL", "F2: and it acts as FAIL")
    with open(os.path.join(d, "verdict.json"), "w", encoding="utf-8") as f:
        json.dump({"word": "FAIL", "reasons": "old"}, f)
    got = W.read_verdict(d)
    ok(got["defects"] is None and got["unreached"] is None, "an old-format file reads as old format (None), not as empty lists")


def t_round2_script_and_cli():
    """GPT round 2 on e3c2fb9550: the script, the CLI and the reader agree on one normalisation (R2-2); PASS cannot carry
    unreached evidence (R2-1); a CLI verdict with neither flag is old format, read from its prose (R2-3)."""
    d = tempfile.mkdtemp(prefix="rl-verdict2-")
    v = os.path.join(d, "verdict")
    with open(v, "w", encoding="utf-8") as f:
        f.write(W.VERDICT_SCRIPT)
    run = lambda *a: subprocess.run([sys.executable, v, *a], capture_output=True, text=True, timeout=30)
    ok(run("UNMEASURED", "CANNOT REACH: ssh", "--unreached", " ").returncode != 0 and not os.path.exists(
        os.path.join(d, "verdict.json")), "R2-2: the script drops a blank --unreached as the reader does, then refuses")
    ok(run("PASS", "offline checks passed", "--unreached", "Steve free space: ssh failed").returncode != 0,
       "R2-1: the script refuses a PASS carrying --unreached")
    ok(W.refusal("PASS", [], ["x"]) and W.refusal("UNMEASURED", [], []) and W.refusal("UNMEASURED", ["d"], ["u"])
       and W.refusal("FAIL", ["d"], ["u"]) is None and W.refusal("PASS", None, None) is None, "the CLI refuses the same set")
    for args in (("UNMEASURED", "x", "--unreached", "  a\n b  "), ("FAIL", "x", "--defect", "d", "--unreached", "u")):
        ok(run(*args).returncode == 0, "accepted: %s" % (args,))
        got = W.read_verdict(d)
        clean = {k: W.clean_list(got[k]) for k in ("defects", "unreached")}
        ok(clean == {k: got[k] for k in clean} and W.refusal(got["word"], got["defects"], got["unreached"]) is None,
           "R2-2: what the script accepts, the reader reads unchanged and the CLI would accept: %s" % got)
    x = T.Rig(n=1, share=1.0, same_failure_limit=2, unmeasured_limit=3, unmeasured_recheck_s=1800)
    was = to_check(x, "I0")
    st = x.st("I0")
    os.environ["RELENTLESS_ROOT"] = x.d
    try:
        ok(R.main(["verdict", "--item", "I0", "--nonce", st["check"]["nonce"], "FAIL",
                   "ssh host timed out; no measurement"]) in (0, None), "the CLI takes an old-format FAIL")
    finally:
        os.environ.pop("RELENTLESS_ROOT", None)
    chk = x.st("I0")["check"]
    ok("defects" not in chk and "unreached" not in chk, "R2-3: no flag given stores no lists: old format, not structured empty")
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick()
    x.tick()
    st = x.st("I0")
    ok(st["gen"] == was["gen"] and (st.get("blind") or {}).get("n") == 1,
       "R2-3: so its blindness prose is read and nothing goes back: %s" % st["status"])
    x.done()


def box_says(x, i, body):
    """The walled path: a verdict.json in the check's box, read by the tick (hand-written, so the script's door is skipped)."""
    box = tempfile.mkdtemp(prefix="rl-box-")
    with open(os.path.join(box, "verdict.json"), "w", encoding="utf-8") as f:
        json.dump(dict(body, at=x.now), f)
    with x.s.lock():
        cur = x.s.load(i)
        cur["check"]["box"] = box
        x.s.save(cur)
    unit = cur["check"]["run"]["unit"]
    x.w.up[unit] = False
    acts = x.tick() + x.tick()
    return x.st(i), acts


def t_round2_box_never_wedges():
    """R2-1 through the tick: a box PASS with unreached evidence does not close. R2-2: a file the reader accepts never
    raises in the tick - UNMEASURED beside a defect is FAIL, a whitespace-only list is read from its prose, and anything
    still malformed is a lost check, once."""
    x = T.Rig(n=1, share=1.0, same_failure_limit=3, unmeasured_limit=3, unmeasured_recheck_s=1800)
    was = to_check(x, "I0")
    st, _ = box_says(x, "I0", {"word": "PASS", "reasons": "offline checks passed",
                               "defects": [], "unreached": ["required Steve free-space measurement: ssh failed"]})
    ok(st["status"] == "candidate" and (st.get("blind") or {}).get("n") == 1 and st["gen"] == was["gen"],
       "R2-1: a box PASS with unreached evidence is UNMEASURED, not a close: %s" % st["status"])
    st = recheck(x, "I0")
    try:
        st, _ = box_says(x, "I0", {"word": "UNMEASURED", "reasons": "CANNOT REACH: ssh", "defects": [], "unreached": [" "]})
        ok(True, "R2-2: a whitespace-only --unreached in the box raises nothing in the tick")
    except ValueError as e:
        ok(False, "R2-2: a whitespace-only --unreached in the box raises nothing in the tick: %s" % e)
    ok(st["gen"] == was["gen"] and st["blind"]["n"] == 2, "R2-2: and it is read from its prose: still blind, nothing back")
    x.done()
    x = T.Rig(n=1, share=1.0, same_failure_limit=3, unmeasured_limit=3, unmeasured_recheck_s=1800)
    was = to_check(x, "I0")
    try:
        st, _ = box_says(x, "I0", {"word": "UNMEASURED", "reasons": "x", "defects": ["8 != 7"], "unreached": ["ssh"]})
        ok(True, "R2-2: a hand-written UNMEASURED beside a defect raises nothing")
    except ValueError as e:
        ok(False, "R2-2: a hand-written UNMEASURED beside a defect raises nothing: %s" % e)
    ok(st["failures"].get("blind_fail") == 1 and st["gen"] > was["gen"], "R2-2: and it acts as the FAIL read_as promises")
    x.done()
    x = T.Rig(n=1, share=1.0, same_failure_limit=3, unmeasured_limit=3, unmeasured_recheck_s=1800)
    was = to_check(x, "I0")
    real = R.verdict

    def broken(*a, **k):
        raise ValueError("a verdict nobody foresaw")
    R.verdict = broken
    try:
        st, acts = box_says(x, "I0", {"word": "PASS", "reasons": "x"})
        more = x.tick() + x.tick()
        ok(True, "R2-2: a verdict that still raises does not escape the tick")
    except ValueError as e:
        ok(False, "R2-2: a verdict that still raises does not escape the tick: %s" % e)
        more = []
    finally:
        R.verdict = real
    st = x.st("I0")
    malformed = [a for a in acts + more if a.get("do") == "verdict_malformed"]
    ok(len(malformed) == 1, "R2-2: it is said once, not every tick: %d" % len(malformed))
    ok(st["status"] in ("candidate", "checking") and st.get("check_lost", 0) <= 1 and st["gen"] == was["gen"],
       "R2-2: routed as one lost check, the candidate kept: %s lost=%s" % (st["status"], st.get("check_lost")))
    x.done()


def t_round2_race():
    """R2-5: should two preparations of one candidate ever overlap (ticks are serialised by tick.lock), the second does
    not install its check over the first: compare-and-set on status, gen and sha under store.lock."""
    x = T.Rig(n=1, share=1.0, same_failure_limit=2)
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "grep -q x y", live="once: test")
    R.finish(x.s, "I0", st["gen"], "sha1", "evidence")
    x.w.up[st["run"]["unit"]] = False
    real = x.w.clean_checkout

    def other_tick_won(st0, sha):
        got = real(st0, sha)
        with x.s.lock():
            cur = x.s.load("I0")
            if cur["status"] == "candidate":
                cur["status"] = "checking"
                cur["check"] = {"nonce": "first", "unit": "u-first", "at": x.now, "clone": "/c/first", "run": {"unit": "u-first"}}
                x.s.save(cur)
        return got
    x.w.clean_checkout = other_tick_won
    launches = len(x.w.launches)
    acts = []
    for _ in range(4):
        acts += x.tick()
        if any(a.get("do") == "check_race" for a in acts):
            break
    st = x.st("I0")
    ok(any(a.get("do") == "check_race" for a in acts), "R2-5: the second preparation sees it lost the race")
    ok(st["check"]["nonce"] == "first" and len(x.w.launches) == launches,
       "R2-5: the first check stands and the second launched nothing: %s" % st["check"].get("nonce"))
    x.done()


def to_check(x, i, sha="sha1"):
    """Worker I0 sets the STEVE contract and finishes at `sha`; tick until its check is running."""
    x.run_one(i)
    st = x.st(i)
    R.contract(x.s, i, st["gen"], "grep -q free_bytes infrastructure/state/facts/steve_c_drive_fill_2026-11-03.md",
               live="once: test")
    R.finish(x.s, i, st["gen"], sha, "evidence")
    x.w.up[st["run"]["unit"]] = False
    for _ in range(4):
        if x.st(i)["status"] == "checking":
            return x.st(i)
        x.tick()
    raise AssertionError("never checked: %s" % x.st(i)["status"])


def speak(x, i, word, reasons, defects=None):
    st = x.st(i)
    R.verdict(x.s, i, st["check"]["nonce"], word, reasons, defects=defects)
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick()
    x.tick()
    return x.st(i)


def recheck(x, i):
    for _ in range(30):
        if x.st(i)["status"] == "checking":
            return x.st(i)
        x.tick(120)
    raise AssertionError("never re-checked: %s" % x.st(i)["status"])


def t_steve_replay():
    x = T.Rig(n=1, share=1.0, same_failure_limit=2, unmeasured_limit=2, unmeasured_recheck_s=1800)
    was = to_check(x, "I0")
    launches = len(x.w.launches)
    st = speak(x, "I0", "FAIL", STEVE_G1)        # what the Marker said at gen 1
    ok(st["status"] == "candidate", "a blind FAIL keeps the candidate: %s" % st["status"])
    ok(st["gen"] == was["gen"] and st["returns"] == was["returns"], "no gen, no return: nothing goes back to a worker")
    ok(st["failures"].get("blind_fail") is None and st["total_failures"] == was["total_failures"], "no strike")
    ok(st["approach"] == "build" and st["approach_changes"] == 0, "no approach change")
    ok(st["blind"]["n"] == 1 and st["blind"]["sha"] == "sha1" and st["blind"]["said"] == "FAIL", "the blindness is counted")
    ok(x.s.attempts("I0")[-1]["end"] == "unmeasured", "recorded as unmeasured, not blind_fail")
    ok(any("UNMEASURED" in n and "no work goes back" in n for n in x.w.notes), "the ledger hears it")
    x.tick(600)
    ok(x.st("I0")["status"] == "candidate" and len(x.w.launches) == launches,
       "no checker before the re-check wait: the box is not repaired by asking again at once")
    st = recheck(x, "I0")
    ok(st["candidate"]["sha"] == "sha1" and st["gen"] == was["gen"], "the same sha is checked again, no worker between")
    st = speak(x, "I0", "UNMEASURED", "CANNOT REACH: ssh stevedesktop exits 255 (ssh_config.d perms)")
    ok(st["status"] == "held" and (st["hold"] or {}).get("kind") == "unmeasured", "twice blind holds for repair")
    ok(not R.hold_is_his(st["hold"]), "the hold is not his: tooling, the seat's to repair")
    ok(st["gen"] == was["gen"] and st["approach"] == "build", "still no gen and no approach change")
    x.tick()
    ok("I0" in x.w.seat_holds, "the held branch reports it up to the seat queue and the Conductor")
    seen = []

    def fake(name, adapter, timeout):     # F5: the check's identity is on disk before any reading runs
        cur = x.st("I0")
        seen.append((cur["status"], bool((cur.get("check") or {}).get("nonce"))))
        return {"cmd": "%s: %s" % (name, adapter["what"]), "exit": 0, "out": "free_bytes=68354924544", "at": x.now}
    x.w.run_offbox = fake
    try:
        R.unhold(x.s, "I0", "Conductor: fix the class", now=x.now, offbox=["ssh stevedesktop 'df -B1 C:'"])
        ok(False, "F1: unhold refuses a command in --offbox")
    except ValueError as e:
        ok("adapter name" in str(e), "F1: unhold refuses a command in --offbox: %s" % str(e)[:80])
    R.unhold(x.s, "I0", "Conductor: fix the class", now=x.now, offbox=[ADAPTER])
    st = x.st("I0")
    ok(st["status"] == "candidate" and st["blind"] is None, "unhold re-checks the candidate, no worker sent")
    ok(st["contract"]["offbox"] == [ADAPTER], "unhold --offbox adds the adapter name to the contract")
    st = recheck(x, "I0")
    ok(seen == [("checking", True)], "F5: the reading ran after the check was saved as checking: %s" % seen)
    ok("free_bytes=68354924544" in x.w.launches[-1][2] and ADAPTER in x.w.launches[-1][2],
       "the checker gets the supervisor's raw reading and the adapter's name")
    st = speak(x, "I0", "PASS", "the reading shows 68 GB free")
    ok(st["status"] in ("closing", "done") and "blind" not in st, "a PASS on the reading closes: %s" % st["status"])
    x.done()


def t_real_fail_after_blind():
    x = T.Rig(n=1, share=1.0, same_failure_limit=2, unmeasured_recheck_s=60)
    was = to_check(x, "I0")
    speak(x, "I0", "FAIL", STEVE_G1)
    recheck(x, "I0")
    # the Marker names the defect its run showed (--defect): an observed violation, PRODUCT, so the strike stands
    st = speak(x, "I0", "FAIL", REAL["FOCUS_CAP g1"], defects=["the cap leaks on the real path"])
    ok(st["failures"].get("blind_fail") == 1 and st["gen"] > was["gen"],
       "a red proof after a blind one still fails: %s gen %s" % (st["failures"], st["gen"]))
    ok("blind" not in st and "recheck_at" not in st, "and ends the run of blind ones")
    x.done()


def t_structured_replay():
    """F2/F3 through the real tick: the lists decide, not the prose."""
    x = T.Rig(n=1, share=1.0, same_failure_limit=2, unmeasured_limit=3, unmeasured_recheck_s=1800)
    was = to_check(x, "I0")
    st = x.st("I0")
    R.verdict(x.s, "I0", st["check"]["nonce"], "FAIL", GPT_RED_BLIND, defects=[], unreached=["ssh stevedesktop exits 255"])
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick()
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "candidate" and st["gen"] == was["gen"] and st["blind"]["n"] == 1,
       "F3: a structured unreached-only FAIL sends nothing back: %s" % st["status"])
    st = recheck(x, "I0")
    try:
        R.verdict(x.s, "I0", st["check"]["nonce"], "UNMEASURED", "x", defects=["8 != 7"], unreached=["ssh"])
        ok(False, "F2: the verdict verb refuses UNMEASURED with a defect")
    except ValueError:
        ok(True, "F2: the verdict verb refuses UNMEASURED with a defect")
    R.verdict(x.s, "I0", st["check"]["nonce"], "FAIL", GPT_HIDDEN, defects=["expected 8, got 7"], unreached=["ssh host timed out"])
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick()
    x.tick()
    st = x.st("I0")
    ok(st["failures"].get("blind_fail") == 1 and st["gen"] > was["gen"], "F2: a defect beside blindness goes back as FAIL")
    x.done()


def t_contract_offbox():
    x = T.Rig(n=1, share=1.0)
    x.run_one("I0")
    g = x.st("I0")["gen"]
    R.contract(x.s, "I0", g, "proof", live="once: t")
    for bad in (["ssh h 'df'"], ["cat ~/.claude/projects/x.jsonl"], ["steve_c_free; cat /etc/passwd"], ["no_such_adapter"]):
        try:
            R.contract(x.s, "I0", g, "proof", why="read the disk from outside", offbox=bad)
            ok(False, "F1: a worker cannot author an offbox command: %s" % bad)
        except ValueError:
            ok(True, "F1: a worker cannot author an offbox command: %s" % bad)
    ok(not x.st("I0")["contract"].get("offbox"), "F1: and nothing was stored")
    R.contract(x.s, "I0", g, "proof", why="read the disk from outside", offbox=[ADAPTER])
    ok(x.st("I0")["contract"]["offbox"] == [ADAPTER] and x.st("I0")["contract"]["live"] == "once: t",
       "any worker may name an adapter with the proof unchanged; the live line stays")
    try:
        R.contract(x.s, "I0", g, "proof", why="x", offbox=[ADAPTER] * (W.OFFBOX_MAX + 1))
        ok(False, "too many offbox adapters are refused")
    except ValueError:
        ok(True, "too many offbox adapters are refused")
    x.done()


def t_old_contract_text_never_runs():
    """F1: a free-text entry from a contract written before adapters is refused at run time, not run."""
    calls = []

    class Fx:
        def run_offbox(self, name, adapter, timeout):
            calls.append(name)
            return {"cmd": name, "exit": 0, "out": "x", "at": 0}
    r = R.rules(os.path.join(R.HERE, "relentless_rules.json"))
    got = R.offbox_readings(Fx(), {"offbox": ["cat ~/.claude/x", ADAPTER]}, r)
    ok(calls == [ADAPTER] and "refused" in str(got[0]["exit"]), "F1: only the adapter ran; the text was refused: %s" % calls)
    got = R.offbox_readings(Fx(), {"offbox": [ADAPTER, ADAPTER]}, dict(r, offbox_max_s=0))
    ok(all("spent" in str(g["exit"]) for g in got), "F5: all of a check's readings share one deadline")
    a = W.adapters(r)[ADAPTER]
    ok(base64.b64decode(a["argv"][-1]).decode("utf-16-le") == a["script"], "the adapter's encoded command is its script")
    ok("ssh" == a["argv"][0] and not any(";" in x or "|" in x for x in a["argv"][:-1]), "argv, no shell")


def t_offbox_box_and_run():
    d = tempfile.mkdtemp(prefix="rl-offbox-")
    out = W.write_offbox(d, [{"cmd": "df -B1", "exit": 0, "out": "68354924544", "at": 0}])
    f = os.path.join(out, "1.txt")
    body = open(f, encoding="utf-8").read()
    ok(body.startswith("$ df -B1\n") and "exit=0" in body and "68354924544" in body, "the box gets command, exit, output")
    ok(not os.stat(f).st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH), "the reading is read only")
    st = {"item": "I0", "candidate": {"sha": "s", "evidence": "e"}, "contract": {"proof": "p", "offbox": [ADAPTER]}}
    p = W.marker_prompt(st, "T", d)
    ok("%s/offbox/" % d in p and "--unreached, not a --defect" in p, "the Marker is told where the readings are")
    ok("--defect" in p and "--unreached" in p, "F2/F3: the walled Marker is told to keep defects and unreached apart")
    ok("--defect" in R.checker_prompt(st, "T", "n0"), "F2/F3: and so is the unwalled one")
    ok("Off-box readings" not in W.marker_prompt(dict(st, contract={"proof": "p"}), "T", d), "no offbox, no words about it")
    fx = R.Effects.__new__(R.Effects)
    sh = lambda code: {"what": "t", "argv": ["sh", "-c", code]}
    got = fx.run_offbox("t", sh("echo hi; exit 3"), 30)
    ok(got["exit"] == 3 and "hi" in got["out"], "run_offbox keeps a red exit and its output: %s" % got)
    got = fx.run_offbox("t", sh("sleep 5"), 1)
    ok("timeout" in str(got["exit"]), "a hung reading is a timeout, not a hang of the tick")
    got = fx.run_offbox("t", sh("pwd; ls -A | wc -l"), 30)
    lines = got["out"].split()
    ok("offbox-" in lines[0] and lines[1] == "0", "F1: it runs from an empty folder, not the candidate tree: %s" % lines)
    got = fx.run_offbox("t", {"what": "t", "argv": ["yes"]}, 30)
    ok(len(got["out"]) <= W.OFFBOX_OUT_MAX and "killed" in str(got["exit"]),
       "F4: an endless output is cut at the cap while read: %d bytes, %s" % (len(got["out"]), got["exit"]))
    t0 = time.time()
    got = fx.run_offbox("t", sh("exec >/dev/null 2>&1; sleep 20"), 1)
    ok(time.time() - t0 < 5 and "timeout" in str(got["exit"]),
       "R2-4: after EOF the wait keeps the shared deadline: %.1f s, %s" % (time.time() - t0, got["exit"]))
    mark = os.path.join(tempfile.mkdtemp(prefix="rl-orphan-"), "alive")
    got = fx.run_offbox("t", sh("(sleep 2; touch %s) >/dev/null 2>&1 & echo started" % mark), 30)
    time.sleep(3)
    ok(got["exit"] == 0 and not os.path.exists(mark), "R2-4: a helper the adapter left behind dies with its group")
    os.environ["RELENTLESS_ROOT"] = "/x"
    try:
        ok(fx.run_offbox("t", sh("echo ${RELENTLESS_ROOT:-none}"), 30)["out"].strip() == "none", "no store root in its env")
    finally:
        os.environ.pop("RELENTLESS_ROOT", None)


def main():
    for t in (t_classifier, t_verdict_script, t_steve_replay, t_real_fail_after_blind, t_structured_replay, t_contract_offbox,
              t_old_contract_text_never_runs, t_offbox_box_and_run, t_round2_script_and_cli, t_round2_box_never_wedges,
              t_round2_race):
        t()
    print("%d failed" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
