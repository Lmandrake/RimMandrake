#!/usr/bin/env python3
"""A checker that cannot reach its evidence says UNMEASURED, and that is no FAIL (CHECKER_SANDBOX_FIX_BLIND_TO_STEVE).
STEVE_DISK_MEASURE_ONLY_FORTY_GIGS_LEFT was done at gen 1; the walled Marker could not ssh the machine nor see
/mnt/d/ClaudeWork, said FAIL, and the item looped to gen 9. Rows: the classifier on reasons Markers really wrote
(store attempts, 2026-11-01..04), the STEVE shape replayed through the real tick on selftest_relentless's rig (no gen,
no return, no approach change; a re-check; the same blindness twice holds for repair, routed to the seat, not to him;
unhold re-checks the same sha), and the off-box reading the supervisor hands in."""
import os
import stat
import sys
import tempfile

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


def t_classifier():
    for name, text in (("STEVE g1", STEVE_G1), ("STEVE g7", STEVE_G7), ("SELFTEST_ALARM g3", ALARM_G3)):
        word, blind = W.read_as("FAIL", text)
        ok(word == W.UNMEASURED and blind, "%s: a FAIL that only says it could not reach is read UNMEASURED" % name)
    for name, text in REAL.items():
        ok(W.read_as("FAIL", text) == ("FAIL", None), "%s: a red proof stays FAIL, blindness beside it or not" % name)
    ok(W.read_as("UNMEASURED", "CANNOT REACH: ssh stevedesktop exit 255")[0] == W.UNMEASURED, "the word itself stands")
    ok(W.read_as("WEAK", STEVE_G1) == ("WEAK", None), "only FAIL is re-read: a WEAK is the Marker's call on the proof")
    ok(W.read_as("PASS", STEVE_G1) == ("PASS", None), "a PASS is never re-read")
    ok(W.UNMEASURED in W.WORDS and "UNMEASURED" in W.VERDICT_SCRIPT, "the box's verdict script takes the word")
    ok(any("UNMEASURED" in line and "not a FAIL" in line for line in W.RULE), "the rule says inability is no FAIL")


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


def speak(x, i, word, reasons):
    st = x.st(i)
    R.verdict(x.s, i, st["check"]["nonce"], word, reasons)
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
    x.w.run_offbox = lambda cmd, cwd, timeout: {"cmd": cmd, "exit": 0, "out": "free_bytes=68354924544", "at": x.now}
    R.unhold(x.s, "I0", "Conductor: fix the class", now=x.now, offbox=["ssh stevedesktop 'df -B1 C:'"])
    st = x.st("I0")
    ok(st["status"] == "candidate" and st["blind"] is None, "unhold re-checks the candidate, no worker sent")
    ok(st["contract"]["offbox"] == ["ssh stevedesktop 'df -B1 C:'"], "unhold --offbox adds the reading to the contract")
    st = recheck(x, "I0")
    ok("free_bytes=68354924544" in x.w.launches[-1][2] and "df -B1 C:" in x.w.launches[-1][2],
       "the checker gets the supervisor's raw reading and its command")
    st = speak(x, "I0", "PASS", "the reading shows 68 GB free")
    ok(st["status"] in ("closing", "done") and "blind" not in st, "a PASS on the reading closes: %s" % st["status"])
    x.done()


def t_real_fail_after_blind():
    x = T.Rig(n=1, share=1.0, same_failure_limit=2, unmeasured_recheck_s=60)
    was = to_check(x, "I0")
    speak(x, "I0", "FAIL", STEVE_G1)
    recheck(x, "I0")
    st = speak(x, "I0", "FAIL", REAL["FOCUS_CAP g1"])
    ok(st["failures"].get("blind_fail") == 1 and st["gen"] > was["gen"],
       "a red proof after a blind one still fails: %s gen %s" % (st["failures"], st["gen"]))
    ok("blind" not in st and "recheck_at" not in st, "and ends the run of blind ones")
    x.done()


def t_contract_offbox():
    x = T.Rig(n=1, share=1.0)
    x.run_one("I0")
    g = x.st("I0")["gen"]
    R.contract(x.s, "I0", g, "proof", live="once: t")
    R.contract(x.s, "I0", g, "proof", why="read the disk from outside", offbox=["ssh h 'df'"])
    ok(x.st("I0")["contract"]["offbox"] == ["ssh h 'df'"] and x.st("I0")["contract"]["live"] == "once: t",
       "any worker may add offbox with the proof unchanged; the live line stays")
    try:
        R.contract(x.s, "I0", g, "proof", why="x", offbox=["a"] * (W.OFFBOX_MAX + 1))
        ok(False, "too many offbox commands are refused")
    except ValueError:
        ok(True, "too many offbox commands are refused")
    x.done()


def t_offbox_box_and_run():
    d = tempfile.mkdtemp(prefix="rl-offbox-")
    out = W.write_offbox(d, [{"cmd": "df -B1", "exit": 0, "out": "68354924544", "at": 0}])
    f = os.path.join(out, "1.txt")
    body = open(f, encoding="utf-8").read()
    ok(body.startswith("$ df -B1\n") and "exit=0" in body and "68354924544" in body, "the box gets command, exit, output")
    ok(not os.stat(f).st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH), "the reading is read only")
    st = {"item": "I0", "candidate": {"sha": "s", "evidence": "e"}, "contract": {"proof": "p", "offbox": ["df -B1"]}}
    p = W.marker_prompt(st, "T", d)
    ok("%s/offbox/" % d in p and "UNMEASURED, not FAIL" in p, "the Marker is told where the readings are")
    ok("Off-box readings" not in W.marker_prompt(dict(st, contract={"proof": "p"}), "T", d), "no offbox, no words about it")
    fx = R.Effects.__new__(R.Effects)
    got = fx.run_offbox("echo hi; exit 3", d, 30)
    ok(got["exit"] == 3 and "hi" in got["out"], "run_offbox keeps a red exit and its output: %s" % got)
    got = fx.run_offbox("sleep 5", d, 1)
    ok("timeout" in str(got["exit"]), "a hung reading is a timeout, not a hang of the tick")
    os.environ["RELENTLESS_ROOT"] = "/x"
    try:
        ok(fx.run_offbox("echo ${RELENTLESS_ROOT:-none}", d, 30)["out"].strip() == "none", "no store root in its env")
    finally:
        os.environ.pop("RELENTLESS_ROOT", None)


def main():
    for t in (t_classifier, t_steve_replay, t_real_fail_after_blind, t_contract_offbox, t_offbox_box_and_run):
        t()
    print("%d failed" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
