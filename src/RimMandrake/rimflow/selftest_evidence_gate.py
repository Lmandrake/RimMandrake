#!/usr/bin/env python3
"""selftest_evidence_gate.py - the evidence-record close predicate, in shadow (RIMFLOW_BUILD_ONE_EVIDENCE_RECORD 09b,
redesign_final.md WP-09).

1. the corpus of REAL past Relentless closes (evidence_gate_corpus.json): every false close (WEAK closes, empty-diff
   --no-code closes) rejected, every valid PASS code close accepted, and both populations non-empty;
2. red under planted breaks: the module's own source with one rule cut out (marker word, empty diff) misses the corpus;
3. green() rule by rule: tampered, no record, red run, exam drift, a non-PASS marker, live owed, a clean record;
4. shadow() on real evidence.append records in a temp store: agree and disagree rows; a close at the work commit read
   from the candidate's record; an item the store does not hold writes nothing; a broken store never raises;
5. the report: one close per (item, sha), the last attempt stands, disagreement classes, the 30-close sample;
6. cli.py end to end on a throwaway ledger + temp store: a close the record rejects still closes (shadow logs the
   disagreement), a refused close is logged as refuse, an unwritable shadow log never stops a close, and a throwaway
   ledger without RELENTLESS_ROOT writes nothing.

    python3 src/RimMandrake/rimflow/selftest_evidence_gate.py
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "cli.py")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import evidence as E                # noqa: E402
import evidence_gate as G           # noqa: E402

FAILS = []
TMP = tempfile.mkdtemp(prefix="evidence_gate_")
CONTRACT = {"proof": "python3 x.py", "live": None}
EXAM = G.exam_of(CONTRACT)


def check(cond, what):
    print(("ok    " if cond else "FAIL  ") + what)
    if not cond:
        FAILS.append(what)


def git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, timeout=60).stdout.strip()


def store(name):
    sd = os.path.join(TMP, name, "store")
    os.makedirs(os.path.join(sd, "items"))
    return sd


def hold(sd, item, cand, contract=CONTRACT):
    os.makedirs(os.path.join(sd, "items", item), exist_ok=True)
    with open(os.path.join(sd, "items", item, "state.json"), "w") as f:
        json.dump({"item": item, "status": "done", "candidate": {"sha": cand}, "contract": contract}, f)


def record(sd, item, sha, word, exam=EXAM, exit_=0):
    E.append(sd, item, sha, "run", {"verdict": "green" if exit_ == 0 else "red", "exit": exit_, "exam_hash": exam["hash"]})
    if word:
        E.append_marker(sd, item, sha, word, nonce="n-%s-%s" % (item, word))


def quiet(fn, *a, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf), contextlib.redirect_stdout(buf):
        return fn(*a, **kw), buf.getvalue()


def corpus_and_breaks():
    with open(G.CORPUS, encoding="utf-8") as f:
        corpus = json.load(f)
    bad, n = G.check_corpus(corpus)
    check(not bad, "corpus: no misses (%d)" % len(bad))
    check(n["false"] >= 40 and n["false_rejected"] == n["false"],
          "corpus: %d real false closes, all %d rejected" % (n["false"], n["false_rejected"]))
    check(n["valid"] >= 500 and n["valid_accepted"] == n["valid"],
          "corpus: %d real valid closes, all %d accepted" % (n["valid"], n["valid_accepted"]))
    kinds = {r["kind"] for r in corpus["closes"] if r["class"] == "false"}
    check(any("WEAK" in k for k in kinds) and any("empty-diff" in k for k in kinds),
          "corpus: both false-close classes present (%s)" % sorted(kinds))
    with open(G.__file__, encoding="utf-8") as f:
        src = f.read()
    for name, old, new in (("marker word", 'marks[-1].get("verdict") != "PASS"', 'marks[-1].get("verdict") == "FAIL"'),
                           ("empty diff", "if no_code and not", "if False and not"),
                           ("live owed", 'if (exam or {}).get("live") and not live:', "if False:")):
        check(old in src, "planted break %s: the rule is where the test cuts" % name)
        mod = types.ModuleType("evidence_gate_broken")
        mod.__file__ = G.__file__
        exec(compile(src.replace(old, new, 1), "evidence_gate_broken", "exec"), mod.__dict__)
        b, _ = mod.check_corpus(corpus) if name != "live owed" else mod.check_corpus({"closes": [
            dict(corpus["closes"][0], live_declared=True, live=False, **{"class": "false", "kind": "planted live"})]})
        check(bool(b), "planted break %s: the corpus goes red (%d misses)" % (name, len(b)))


def rules():
    run = {"kind": "run", "verdict": "green", "exit": 0, "exam_hash": EXAM["hash"]}
    mark = {"kind": "marker", "verdict": "PASS"}
    ok, why = G.green([run, mark], EXAM)
    check(ok and not why, "green: a green run and a PASS on the frozen exam close")
    cases = (("tampered", [run, mark], {"tampered": ["line 1: hash"]}),
             ("no record", [], {}),
             ("run not green", [dict(run, verdict="red", exit=1), mark], {}),
             ("exam drift", [dict(run, exam_hash="f" * 64), mark], {}),
             ("no marker", [run], {}),
             ("marker WEAK", [run, dict(mark, verdict="WEAK")], {}),
             ("marker UNMEASURED", [run, dict(mark, verdict="UNMEASURED")], {}),
             ("empty diff", [run, mark], {"no_code": True}),
             ("live owed", [run, mark], {"exam": dict(EXAM, live=True)}))
    for cls, entries, kw in cases:
        exam = kw.pop("exam", EXAM)
        ok, why = G.green(entries, exam, **kw)
        check(not ok and any(G.reason_class(w) == cls for w in why), "green: %s rejects (%s)" % (cls, why[:2]))
    check(G.green([run, mark], dict(EXAM, live=True), live="unit=rm-x.timer max_age=6h")[0],
          "green: a declared live clause with an attestation closes")
    check(G.green([run, mark], dict(EXAM, no_code=True), no_code=True)[0], "green: a no_code exam closes with no code")
    check(G.green([run, dict(mark, verdict="FAIL"), dict(mark, verdict="PASS")], EXAM)[0],
          "green: the newest Marker verdict stands (a PASS after a FAIL)")


def shadow():
    sd = store("shadow")
    a, b = "a" * 40, "b" * 40
    hold(sd, "ITEM_PASS", a)
    record(sd, "ITEM_PASS", a, "PASS")
    row, _ = quiet(G.shadow, "ITEM_PASS", a, "", [], sd=sd)
    check(row and row["predicate"] == "accept" and not row["disagree"], "shadow: PASS record, gate accepts -> agree")
    hold(sd, "ITEM_WEAK", b)
    record(sd, "ITEM_WEAK", b, "WEAK")
    row, err = quiet(G.shadow, "ITEM_WEAK", b, "", [], sd=sd)
    check(row and row["disagree"] and "marker WEAK" in [G.reason_class(r) for r in row["reasons"]] and "DISAGREES" in err,
          "shadow: WEAK record, gate accepts -> disagree, said on stderr")
    row, _ = quiet(G.shadow, "ITEM_WEAK", b, "", [("run", "no level-tagged pass")], sd=sd)
    check(row and not row["disagree"] and row["gate"] == "refuse" and row["gate_reasons"] == ["run"],
          "shadow: WEAK record, gate refuses -> agree")
    row, _ = quiet(G.shadow, "ITEM_PASS", "", "bookkeeping", [], sd=sd)
    check(row and row["record"] == a and "empty diff" in [G.reason_class(r) for r in row["reasons"]],
          "shadow: a --no-code close reads the candidate's record and rejects (empty diff)")
    # a close at the work commit, an ancestor of the candidate where the Marker ran
    heads = git("log", "--format=%H", "-n", "2", "HEAD").split()
    hold(sd, "ITEM_WORK", heads[0])
    record(sd, "ITEM_WORK", heads[0], "PASS")
    row, _ = quiet(G.shadow, "ITEM_WORK", heads[1][:10], "", [], sd=sd, cwd=REPO)
    check(row and row["record"] == heads[0] and row["predicate"] == "accept",
          "shadow: a close at the work commit (short sha, an ancestor) reads the candidate's record")
    row, _ = quiet(G.shadow, "NOT_RELENTLESS", a, "", [], sd=sd)
    check(row is None, "shadow: an item the store does not hold is not judged")
    n = len(G.rows(sd))
    check(n == 5, "shadow: one row per judged close (%d)" % n)
    # broken store: the shadow log is a directory; a record that does not verify
    broken = store("broken")
    hold(broken, "ITEM_PASS", a)
    record(broken, "ITEM_PASS", a, "PASS")
    os.makedirs(os.path.join(broken, G.SHADOW))
    try:
        row, err = quiet(G.shadow, "ITEM_PASS", a, "", [], sd=broken)
        check(row is None and "the close is unaffected" in err, "shadow: an unwritable log never raises")
    except Exception as ex:      # noqa: BLE001
        check(False, "shadow: an unwritable log never raises (%r)" % ex)
    shutil.rmtree(os.path.join(broken, G.SHADOW))
    p = E.record_path(broken, "ITEM_PASS", a)
    os.chmod(p, 0o644)
    with open(p, "a") as f:
        f.write(json.dumps({"kind": "marker", "verdict": "PASS"}) + "\n")
    row, _ = quiet(G.shadow, "ITEM_PASS", a, "", [], sd=broken)
    check(row and "tampered" in [G.reason_class(r) for r in row["reasons"]], "shadow: a forged record line is tampered")


def report():
    rs = [{"item": "I%d" % i, "sha": "s", "gate": "accept", "predicate": "accept", "disagree": False, "reasons": []}
          for i in range(29)]
    rs.append({"item": "W", "sha": "s", "gate": "refuse", "predicate": "reject", "disagree": False, "reasons": ["x: y"]})
    rs.append({"item": "W", "sha": "s", "gate": "accept", "predicate": "reject", "disagree": True,
               "reasons": ["marker WEAK: a WEAK verdict cannot close"]})
    s = G.summary(rs)
    check(s["closes"] == 30 and s["attempts"] == 31 and s["disagree"] == 1 and s["sample_met"],
          "report: 31 attempts are 30 closes, the retried one's last attempt stands, sample met")
    check(s["by_class"] == {"gate accept / record reject: marker WEAK": 1} and s["gate_accept_record_reject"] == 1,
          "report: disagreements counted by class")
    s = G.summary(rs[:5])
    check(not s["sample_met"] and "UNDER SAMPLE: 5 of 30" in G.report_lines(s)[0], "report: under the sample says so")


def cli_end_to_end():
    import live_line
    good = []
    for sha in git("log", "origin/main", "--format=%H", "-n", "300", "--", "src/RimMandrake/Utils/").split():
        paths = git("diff-tree", "--no-commit-id", "--name-only", "-r", "--root", sha).split()
        if paths and not live_line.needs_line(paths):
            good.append(sha)
        if len(good) == 2:
            break
    if len(good) < 2:
        check(False, "cli: UNMEASURED - no code commit without a live path in the last 300")
        return
    root = os.path.join(TMP, "e2e")
    sd = store("e2e")
    ledger, items = os.path.join(root, "events.jsonl"), os.path.join(root, "items")
    os.makedirs(os.path.join(items, "closed"))

    def cli(*args, relentless=True):
        env = {k: v for k, v in os.environ.items()
               if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_GITINDEX", "RELENTLESS_ROOT")}
        env.update(RIMFLOW_LEDGER=ledger, RIMFLOW_ITEMS=items, RIMFLOW_SEAT="BENCH", AGENT_SEAT="BENCH")
        if relentless:
            env["RELENTLESS_ROOT"] = root
        r = subprocess.run([sys.executable, CLI, *args], cwd=REPO, env=env, capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout + r.stderr

    def item(iid, sha, word):
        for a in (("file", iid, "--for", "BENCH", "--title", "fixture %s" % iid), ("claim", iid)):
            rc, out = cli(*a)
            if rc:
                raise AssertionError(out[-300:])
        hold(sd, iid, sha)
        record(sd, iid, sha, word)

    def passed(iid, sha):
        return cli("verify", iid, "--sha", sha, "--level", "L0", "--result", "pass", "--config", "fixture",
                   "--evidence", "fixture")[0] == 0

    a, b = good
    item("WEAK_1_PROBE_FIXTURE", a, "WEAK")
    rc, out = cli("close", "WEAK_1_PROBE_FIXTURE", "--sha", a)
    check(rc != 0 and "has not earned" in out, "cli: a close with no pass is refused by today's gate")
    rows = G.rows(sd)
    check(len(rows) == 1 and rows[0]["gate"] == "refuse" and rows[0]["predicate"] == "reject",
          "cli: the refused close is in the shadow log as refuse/reject")
    check(passed("WEAK_1_PROBE_FIXTURE", a), "cli: a level-tagged pass recorded")
    rc, out = cli("close", "WEAK_1_PROBE_FIXTURE", "--sha", a)
    rows = G.rows(sd)
    check(rc == 0 and "closed at" in out, "cli: the gate's close goes through though the record says WEAK")
    check(len(rows) == 2 and rows[-1]["disagree"] and rows[-1]["gate"] == "accept" and "DISAGREES" in out,
          "cli: the shadow logs that close as a disagreement and says so")
    item("UNWRITABLE_2_PROBE_FIXTURE", b, "PASS")
    passed("UNWRITABLE_2_PROBE_FIXTURE", b)
    os.rename(os.path.join(sd, G.SHADOW), os.path.join(sd, "moved.jsonl"))
    os.makedirs(os.path.join(sd, G.SHADOW))
    rc, out = cli("close", "UNWRITABLE_2_PROBE_FIXTURE", "--sha", b)
    check(rc == 0 and "the close is unaffected" in out, "cli: an unwritable shadow log never stops a close")
    os.rmdir(os.path.join(sd, G.SHADOW))
    item("NOROOT_3_PROBE_FIXTURE", b, "PASS")
    passed("NOROOT_3_PROBE_FIXTURE", b)
    rc, out = cli("close", "NOROOT_3_PROBE_FIXTURE", "--sha", b, relentless=False)
    check(rc == 0 and not os.path.exists(os.path.join(sd, G.SHADOW)) and "evidence shadow" not in out,
          "cli: a throwaway ledger without RELENTLESS_ROOT writes no shadow row")


def main():
    try:
        corpus_and_breaks()
        rules()
        shadow()
        report()
        cli_end_to_end()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("\n%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
