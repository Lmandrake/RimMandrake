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
   ledger without RELENTLESS_ROOT writes nothing;
7. the wiring that made it reject every close (EVIDENCE_SHADOW_FIX_REJECTS_EVERY_CLOSE): relentless.verdict() writes the
   Marker's entry, an offbox `skipped` run is not red, a pre-evidence candidate is the pre_record cohort, a pre-seal
   writer's unsealed index tail no longer refuses every append after it;
8. the reading WP-09c cites (EVIDENCE_SHADOW_FIX_REPORT_NEVER_READS_ZERO): a declared window that says what it left out, a
   row that records who closed, an owner close that is neither agreement nor disagreement and never verdict_gone, the
   unrunnable ruling, and the no-run rows that are the wedge cohort only when the snapshot holds the receipts.

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


def toy_repo():
    rp = tempfile.mkdtemp(prefix="repo_", dir=TMP)
    for a in (("init", "-q", "-b", "main"), ("config", "user.email", "t@t"), ("config", "user.name", "t"),
              ("config", "commit.gpgsign", "false")):
        git_in(rp, *a)
    commit(rp, "root", {"README": "x"})
    return rp


def git_in(rp, *a):
    return subprocess.run(["git", *a], cwd=rp, capture_output=True, text=True, timeout=60).stdout.strip()


def commit(rp, subject, files):
    for path, text in files.items():
        os.makedirs(os.path.dirname(os.path.join(rp, path)) or rp, exist_ok=True)
        with open(os.path.join(rp, path), "w") as f:
            f.write(text)
        git_in(rp, "add", path)
    git_in(rp, "commit", "-q", "--no-verify", "-m", subject)
    return git_in(rp, "rev-parse", "HEAD")


def corpus_build():
    """findings 5 and 6: a no_code exam's --no-code PASS close is valid; a rebuild that dies keeps the old corpus."""
    sd = store("corpus")
    nc = {"proof": "true", "live": None, "no_code": True}
    hold(sd, "NC_OK", "c" * 40, contract=nc)
    hold(sd, "NC_BAD", "d" * 40)
    for iid in ("NC_OK", "NC_BAD"):
        p = os.path.join(sd, "items", iid, "state.json")
        with open(p) as f:
            st = json.load(f)
        st["check"] = {"verdict": "PASS"}
        with open(p, "w") as f:
            json.dump(st, f)
    ev = [{"event": "close", "id": iid, "sha": "e" * 10, "ts": "t", "why": "relentless: blind check passed",
           "noCode": "bookkeeping"} for iid in ("NC_OK", "NC_BAD")]
    c = G.build_corpus(ev, sd, [])
    cls = {r["item"]: r["class"] for r in c["closes"]}
    check(cls == {"NC_OK": "valid", "NC_BAD": "false"}, "corpus build: a no_code exam's --no-code close is valid, "
          "any other --no-code close false (%s)" % cls)
    bad, n = G.check_corpus(c)
    check(not bad and n["valid_accepted"] == 1 and n["false_rejected"] == 1,
          "corpus check: the predicate agrees with both labels (%s)" % bad[:1])
    path = os.path.join(TMP, "corpus.json")
    G.write_corpus(path, c)
    with open(path) as f:
        before = f.read()
    try:
        G.write_corpus(path, dict(c, closes=c["closes"] + [{"unserialisable": object()}]))
        check(False, "corpus write: a failing rebuild raises")
    except TypeError:
        pass
    with open(path) as f:
        after = f.read()
    check(before == after and json.loads(after)["closes"] and os.listdir(TMP).count("corpus.json") == 1
          and not [x for x in os.listdir(TMP) if x.startswith("corpus.json.tmp")],
          "corpus write: an interrupted rebuild leaves the old corpus whole and no temp file")


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
    # a close at the work commit, an ancestor of the candidate where the Marker ran (a throwaway repo: the work, then
    # bookkeeping and another item's landing on top)
    rp = toy_repo()
    work = commit(rp, "ITEM_WORK: the work", {"src/f.py": "1"})
    commit(rp, "ledger: ITEM_WORK note", {"infrastructure/state/ledger/events/X.jsonl": "{}"})
    cand = commit(rp, "OTHER_ITEM: its own work", {"src/other.py": "1"})
    hold(sd, "ITEM_WORK", cand)
    record(sd, "ITEM_WORK", cand, "PASS")
    row, _ = quiet(G.shadow, "ITEM_WORK", work[:10], "", [], sd=sd, cwd=rp)
    check(row and row["record"] == cand and row["predicate"] == "accept",
          "shadow: a close at the work commit (short sha, an ancestor; bookkeeping and another item between) reads "
          "the candidate's record")
    # finding 1: the work at `work` was broken, a later commit fixed it and the candidate passed on the fix
    fixed = commit(rp, "ITEM_WORK: fix the bug", {"src/f.py": "2"})
    hold(sd, "ITEM_WORK", fixed)
    record(sd, "ITEM_WORK", fixed, "PASS")
    row, _ = quiet(G.shadow, "ITEM_WORK", work, "", [], sd=sd, cwd=rp)
    check(row is not None and row["record"] is None and row["predicate"] == "reject",
          "shadow: an ancestor whose item files a later ITEM_WORK commit changed is not vouched for by the fix's pass "
          "(%s)" % (row and row["reasons"][:1]))
    edited = commit(rp, "UNRELATED: touches f.py", {"src/f.py": "3"})
    hold(sd, "ITEM_WORK2", edited)
    record(sd, "ITEM_WORK2", edited, "PASS")
    row, _ = quiet(G.shadow, "ITEM_WORK2", fixed, "", [], sd=sd, cwd=rp)
    check(row is not None and row["record"] is None,
          "shadow: no commit naming the item (ITEM_WORK2) leaves its work unknown: code between refuses the ancestor")
    row, _ = quiet(G.shadow, "NOT_RELENTLESS", a, "", [], sd=sd)
    check(row is None, "shadow: an item the store does not hold is not judged")
    n = len(G.rows(sd))
    check(n == 7, "shadow: one row per judged close (%d)" % n)
    # finding 4: a torn last row (crash mid-append) must not swallow the next whole observation
    with open(os.path.join(sd, G.SHADOW), "a") as f:
        f.write('{"item": "TORN", "sha": "x", "gate": "acc')
    row, _ = quiet(G.shadow, "ITEM_PASS", a, "", [], sd=sd)
    rs = G.rows(sd)
    check(row and len(rs) == n + 1 and rs[-1] == row, "shadow: after a torn row the next append is its own line (%d rows)"
          % len(rs))
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
    # finding 2: judge reads and verifies ONE snapshot - a separate verify() then read() is a race it must not run
    real = (E.verify, E.read)
    E.verify = E.read = lambda *a, **k: (_ for _ in ()).throw(AssertionError("verify/read called apart"))
    try:
        j = G.judge(broken, "ITEM_PASS", a, "")
        check(j and not j["accepted"] and "tampered" in [G.reason_class(r) for r in j["reasons"]],
              "judge: entries and verdict come from one snapshot (evidence.read_verified), not verify() then read()")
    except AssertionError as ex:
        check(False, "judge: entries and verdict come from one snapshot (%s)" % ex)
    finally:
        E.verify, E.read = real
    ents, bad = E.read_verified(broken, "ITEM_PASS", a)
    check(bad and ents and ents[-1].get("kind") == "marker", "read_verified: the forged line and its problem together")


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
    for sha in git("log", "HEAD", "--format=%H", "-n", "300", "--", "src/RimMandrake/Utils/").split():
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

    def item(iid, sha, word, contract=CONTRACT):
        for a in (("file", iid, "--for", "BENCH", "--title", "fixture %s" % iid), ("claim", iid)):
            rc, out = cli(*a)
            if rc:
                raise AssertionError(out[-300:])
        hold(sd, iid, sha, contract)
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
    # finding 3: the shadow logs the close's verdict AFTER _live_gate - a live line that does not hold refuses the close,
    # and the row says refuse, not an accept/accept agreement on the raw --live text
    live_c = dict(CONTRACT, live="unit=rm-nope.timer reading=/nonexistent max_age=6h")
    item("LIVE_4_PROBE_FIXTURE", b, "PASS", live_c)
    passed("LIVE_4_PROBE_FIXTURE", b)
    n0 = len(G.rows(sd))
    rc, out = cli("close", "LIVE_4_PROBE_FIXTURE", "--sha", b, "--live", "unit=rm-nope.timer reading=/nonexistent max_age=6h")
    rows = G.rows(sd)
    check(rc != 0 and "does not hold" in out and len(rows) == n0 + 1 and rows[-1]["gate"] == "refuse"
          and rows[-1]["gate_reasons"] == ["live"] and rows[-1]["item"] == "LIVE_4_PROBE_FIXTURE",
          "cli: a close the live gate refuses is logged refuse (%s)" % (rows[-1:] and rows[-1]["gate"]))
    # EVIDENCE_SHADOW_FIX_REPORT_NEVER_READS_ZERO: the row records who closed, through the real flags
    for iid, flags, want in (("BYSUP_5_PROBE_FIXTURE", ("--why", "relentless: blind check passed"), G.RELENTLESS_CLOSE),
                             ("BYHAND_6_PROBE_FIXTURE", ("--why", "closed on the relentless record"), G.SEAT_CLOSE),
                             ("BYOWNER_7_PROBE_FIXTURE", ("--owner-said", "close it"), G.OWNER_CLOSE)):
        item(iid, b, "WEAK")
        passed(iid, b)
        rc, out = cli("close", iid, "--sha", b, *flags)
        last = G.rows(sd)[-1]
        check(rc == 0 and last["item"] == iid and last["closed_by"] == want and last["disagree"],
              "cli: close %s records closed_by=%s, raw disagree kept (%s)" % (flags[0], want, last.get("closed_by")))
        check(("DISAGREES" in out) == (want != G.OWNER_CLOSE),
              "cli: %s close %s a disagreement on stderr" % (want, "is not called" if want == G.OWNER_CLOSE else "is called"))
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


def wiring():
    """EVIDENCE_SHADOW_FIX_REJECTS_EVERY_CLOSE: the predicate rejected all 70 shadow closes. Each cause, red-then-green."""
    import relentless as R
    sha = "c" * 40
    # W1. the Marker's verdict reaches the record: relentless.verdict() writes the `marker` entry (no harvest run)
    root = os.path.join(TMP, "wire_root")
    st_ = R.Store(root)
    st_.save({"item": "WIRE_A", "status": "checking", "gen": 1, "candidate": {"sha": sha, "at": 1.0},
              "check": {"nonce": "nW", "at": 1.0}, "contract": CONTRACT})
    E.append(st_.dir, "WIRE_A", sha, "run", {"verdict": "green", "exit": 0, "exam_hash": EXAM["hash"]})
    R.verdict(st_, "WIRE_A", "nW", "PASS", "ran it, green", defects=[], unreached=[])
    marks = [e for e in E.read(st_.dir, "WIRE_A", sha) if e["kind"] == "marker"]
    check(len(marks) == 1 and marks[0]["verdict"] == "PASS" and marks[0]["nonce"] == "nW",
          "W1. relentless.verdict() appends the Marker's PASS to the candidate's record (%r)" % [m["verdict"] for m in marks])
    j = G.judge(st_.dir, "WIRE_A", sha, False, None, REPO)
    check(j["accepted"], "W1. so the predicate accepts that close (%s)" % j["reasons"])
    got, _ = quiet(E.harvest, st_)
    check(got == [], "W1. a later harvest adds nothing: the same nonce is one entry (%r)" % got)
    # W1b. a receipt that cannot be written never costs the verdict
    st_.save({"item": "WIRE_B", "status": "checking", "gen": 1, "candidate": {"sha": "d" * 40},
              "check": {"nonce": "nB", "at": 1.0}, "contract": CONTRACT})
    real_append = E.append_marker
    E.append_marker = lambda *a, **k: (_ for _ in ()).throw(OSError("disk full"))
    try:
        (_, err) = quiet(R.verdict, st_, "WIRE_B", "nB", "PASS", "ok", defects=[], unreached=[])
    finally:
        E.append_marker = real_append
    check(st_.load("WIRE_B")["check"]["verdict"] == "PASS" and "NOT written" in err,
          "W1. an unwritable receipt is one stderr line and the verdict still stands")
    # W2. an offbox contract's box run is `skipped`: not red, the Marker decides
    sd = store("wire_skip")
    hold(sd, "SKIP", sha)
    E.append(sd, "SKIP", sha, "run", {"verdict": "skipped", "exit": None, "exam_hash": EXAM["hash"]})
    E.append_marker(sd, "SKIP", sha, "PASS", nonce="s1")
    check(G.judge(sd, "SKIP", sha, False, None, REPO)["accepted"], "W2. a skipped (offbox) box run + Marker PASS accepts")
    hold(sd, "UNRUN", sha)
    E.append(sd, "UNRUN", sha, "run", {"verdict": "unrunnable", "exit": None, "exam_hash": EXAM["hash"]})
    E.append_marker(sd, "UNRUN", sha, "PASS", nonce="u1")
    check(not G.judge(sd, "UNRUN", sha, False, None, REPO)["accepted"], "W2. an unrunnable box run still rejects")
    E.append_marker(sd, "SKIP", sha, "WEAK", nonce="s2")
    check(not G.judge(sd, "SKIP", sha, False, None, REPO)["accepted"], "W2. a skipped run + Marker WEAK rejects")
    # W3. a candidate finished before any evidence row is the pre_record cohort; the report does not count it
    sd = store("wire_pre")
    E.append(sd, "OTHER", sha, "run", {"verdict": "green", "exit": 0, "exam_hash": EXAM["hash"]},
             at="2026-11-06T13:39:24Z")
    for item, at in (("OLD", 1793750400.0), ("NEW", 1793990000.0)):     # 2026-11-04 / 2026-11-06T18:33Z
        os.makedirs(os.path.join(sd, "items", item))
        with open(os.path.join(sd, "items", item, "state.json"), "w") as f:
            json.dump({"item": item, "status": "done", "candidate": {"sha": sha, "at": at}, "contract": CONTRACT}, f)
    jo, jn = G.judge(sd, "OLD", sha, False, None, REPO), G.judge(sd, "NEW", sha, False, None, REPO)
    check(jo.get("cohort") == G.PRE_RECORD and not jo["accepted"] and "cohort" not in jn,
          "W3. a candidate older than every evidence row is pre_record (still rejected); a newer one is not (%r / %r)"
          % (jo.get("cohort"), jn.get("cohort")))
    s = G.summary([{"item": "OLD", "sha": sha, "gate": "accept", "predicate": "reject", "disagree": True,
                    "cohort": G.PRE_RECORD, "reasons": jo["reasons"]},
                   {"item": "NEW", "sha": sha, "gate": "accept", "predicate": "reject", "disagree": True,
                    "reasons": jn["reasons"]}])
    check(s["disagree"] == 1 and s["pre_record"] == 1 and s["agree"] == 0,
          "W3. the report counts pre_record apart from real disagreements (%r)" % {k: s[k] for k in ("disagree", "pre_record")})
    # W4. a pre-seal writer's unsealed row past HEAD no longer reads as tampering (selftest_evidence_recovery R8 has the
    # cuts); the record stays judgeable and the next append seals it
    sd = store("wire_seal")
    hold(sd, "SEAL", sha)
    record(sd, "SEAL", sha, "PASS")
    _old_writer_append(sd, "SEAL2", sha)
    hold(sd, "SEAL2", sha)
    check(G.judge(sd, "SEAL", sha, False, None, REPO)["accepted"],
          "W4. a pre-seal writer's tail past HEAD: the record still verifies and accepts")
    E.append_marker(sd, "SEAL2", sha, "PASS", nonce="z")
    check(E.verify_index(sd) == [] and E._head(sd)[0]["n"] == len(E.index_rows(sd)),
          "W4. and the next append is not refused: it seals the whole index")


def _old_writer_append(sd, item, sha):
    """evidence.append as it was before the seal (3e1d97efb4): record + chained index row, no `sealed`, no HEAD."""
    rows = [e for _, e in E._lines(E.record_path(sd, item, sha)) if e]
    last = [e for _, e in E._index(sd) if e]
    entry = {"verdict": "green", "exit": 0, "exam_hash": EXAM["hash"], "v": E.V, "kind": "run", "item": item, "sha": sha,
             "n": len(rows), "prev": rows[-1]["hash"] if rows else E.ZERO, "at": "2026-11-06T17:16:37Z"}
    entry["hash"] = E.entry_hash(entry)
    ix = {"v": E.V, "n": len(last), "prev": last[-1]["hash"] if last else E.ZERO, "item": item, "sha": sha,
          "entry_n": entry["n"], "entry": entry["hash"], "kind": "run", "at": entry["at"]}
    ix["hash"] = E.entry_hash(ix)
    path = E.record_path(sd, item, sha)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for pth, e in ((path, entry), (os.path.join(E.base(sd), E.INDEX), ix)):
        if os.path.exists(pth):
            os.chmod(pth, 0o644)
        with open(pth, "a") as f:
            f.write(json.dumps(e, sort_keys=True, separators=(",", ":")) + "\n")


def receipt_wedge():
    """RIMFLOW_BUILD_ONE_EVIDENCE_RECORD: a finish whose run receipt append was refused as tampering (the HEAD-lag
    wedge) is the wedge cohort from its own NEWEST finish receipt, after a seal has repaired the index tail."""
    sd = store("receipt_wedge")
    sha = "ab" * 20
    d = os.path.join(sd, "items", "WEDGED", "receipts")
    os.makedirs(d)
    refused = "TamperError: does not verify"
    def put(gen, boxrun, at_sha=sha, at="2026-11-06T17:30:00Z", raw=None):
        with open(os.path.join(d, "gen%d.json" % gen), "w") as f:
            f.write(raw if raw is not None else json.dumps({"item": "WEDGED", "sha": at_sha, "gen": gen, "at": at,
                                                             "boxrun": boxrun}))
    row_at = "2026-11-06T17:40:00Z"
    check(not G._receipt_wedged(sd, "WEDGED", sha, row_at), "no receipt: not wedged")
    put(1, {"verdict": "green", "evidence_error": None})
    check(not G._receipt_wedged(sd, "WEDGED", sha, row_at), "a clean green receipt is not the wedge")
    put(2, {"verdict": "green", "evidence_error": refused})
    check(G._receipt_wedged(sd, "WEDGED", sha, row_at), "a green run whose receipt was refused as tampering is the wedge")
    check(G._receipt_wedged(sd, "WEDGED", sha[:10], row_at), "a 10-digit sha matches its receipt")
    check(not G._receipt_wedged(sd, "WEDGED", sha[:4], row_at), "a sha under 7 digits matches nothing")
    check(not G._receipt_wedged(sd, "WEDGED", "", row_at), "an empty sha matches nothing")
    check(not G._receipt_wedged(sd, "WEDGED", sha, "2026-11-06T17:00:00Z"), "a receipt written after the close explains nothing")
    check(not G._receipt_wedged(sd, "OTHER", sha, row_at), "another item is not wedged")
    put(10, {"verdict": "red", "evidence_error": refused}, at="2026-11-06T17:35:00Z")
    check(not G._receipt_wedged(sd, "WEDGED", sha, row_at),
          "the newest receipt (gen10 after gen2, not name order) is red: a red run is never the wedge")
    os.remove(os.path.join(d, "gen10.json"))
    put(11, None, raw="[1, 2]")
    put(12, "green", at="2026-11-06T17:36:00Z")
    check(not G._receipt_wedged(sd, "WEDGED", sha, row_at), "a non-object receipt or a non-dict boxrun never crashes")
    put(13, {"verdict": "green", "evidence_error": refused}, at_sha="a")
    check(not G._receipt_wedged(sd, "WEDGED", "a" * 7, row_at), "a receipt sha that is not a full commit id matches nothing")


def _row(item, at, disagree=False, **kw):
    r = {"item": item, "sha": "ab" * 20, "at": at, "gate": "accept", "predicate": "reject" if disagree else "accept",
         "disagree": disagree, "reasons": ["no marker: none"] if disagree else [], "no_code": False}
    r.update(kw)
    return r


def window():
    """Clause 1: a declared window, and what it left out, said plainly."""
    old = [_row("OLD%d" % i, "2026-11-06T13:00:00Z", True) for i in range(70)]
    new = [_row("NEW%d" % i, "2026-11-06T18:00:00Z") for i in range(30)]
    rs = old + new
    whole = G.summary(rs)
    check(whole["disagree"] == 70 and whole["window"] is None and "none declared" in G.report_lines(whole)[1],
          "window: with none declared the whole log counts, and the report says so")
    w = {"since": "2026-11-06T17:52:16Z", "named": "a named fix"}
    s = G.summary(rs, w)
    check(s["disagree"] == 0 and s["closes"] == 30 and s["sample_met"], "window: old rows no longer hold the count above 0 (%d)"
          % s["disagree"])
    check(s["left_out"]["closes"] == 70 and s["left_out"]["disagree"] == 70
          and s["left_out"]["by_class"] == {"gate accept / record reject: no marker": 70},
          "window: what it left out is counted by class (%s)" % s["left_out"])
    text = "\n".join(G.report_lines(s))
    check("closes at or after 2026-11-06T17:52:16Z (a named fix)" in text and "left out: 70 closes before the window, 70 of "
          "them disagreeing: older than the fix" in text, "window: the report names the window, the rows left out and why")
    s = G.summary(old + [_row("NEW", "2026-11-06T18:00:00Z", True)], w)
    check(s["disagree"] == 1, "window: a disagreement inside the window still counts")
    s = G.summary([_row("R", "2026-11-06T13:00:00Z", True), _row("R", "2026-11-06T18:00:00Z")], w)
    check(s["closes"] == 1 and s["left_out"]["closes"] == 0 and s["disagree"] == 0,
          "window: a retried close is one close, where its last attempt stands")
    check(G.resolve_window("2026-11-06T18:00:00Z")["since"] == "2026-11-06T18:00:00Z", "window: an ISO time is itself")
    fix = G.resolve_window("marker_writer")
    check(fix["since"] == "2026-11-06T17:52:16Z" and "RELENTLESS_WIRE_MARKER_VERDICT_AND_REPAIR" in fix["named"],
          "window: the named writer fix is its commit's time, with its subject (%s)" % fix)
    rp = toy_repo()
    sha = git_in(rp, "rev-parse", "HEAD")
    check(G.resolve_window(sha[:10], rp)["named"].startswith(sha[:10] + ": root"), "window: a named sha reads the commit")
    for bad in ("nonsense", "", "f" * 40, "2026-11-06"):
        try:
            G.resolve_window(bad, rp)
            check(False, "window: %r names nothing and must refuse" % bad)
        except ValueError:
            check(True, "window: %r names nothing: refused" % bad)
    sd = store("window")
    with open(os.path.join(sd, G.SHADOW), "w") as f:
        f.write(json.dumps(_row("X", "2026-11-06T18:00:00Z", True, closed_by=G.RELENTLESS_CLOSE)) + "\n")
    rc, out = quiet(G.main, ["--store-dir", sd, "report", "--since", "nonsense"])
    check(rc == 2 and out.startswith("UNMEASURED") and "DISAGREE" not in out,
          "window: a --since that names nothing is UNMEASURED, never the whole log")


def scope():
    """Clause 2: who closed; an owner close is its own line."""
    check(G.closed_by(False, "relentless: blind check passed") == G.RELENTLESS_CLOSE, "scope: the supervisor's words are a Relentless close")
    check(G.closed_by(False, "closed as falsified on the relentless record") == G.SEAT_CLOSE,
          "scope: a hand close that mentions relentless is a seat close (the 2026-11-06 ARTEVAL words)")
    check(G.closed_by(True, "relentless: blind check passed") == G.OWNER_CLOSE, "scope: his authority wins")
    check(G.closed_by(False, "") == G.SEAT_CLOSE, "scope: no why is a seat close")
    closes = G.ledger_closes([
        {"event": "close", "id": "O", "sha": "ab" * 5, "seat": "OWNER", "ts": "2026-11-06T21:12:06Z", "why": "triage"},
        {"event": "close", "id": "C", "sha": "ab" * 5, "seat": "BENCH", "ts": "2026-11-06T21:12:06Z", "byCard": "q -> a"},
        {"event": "close", "id": "S", "sha": "ab" * 5, "seat": "BENCH", "ts": "2026-11-06T21:12:06Z", "why": "hand"},
        {"event": "close", "id": "R", "sha": "ab" * 5, "seat": "BENCH", "ts": "2026-11-06T21:12:06Z", "why": "relentless: blind check passed"},
        {"event": "note", "id": "N", "sha": "ab" * 5, "seat": "OWNER", "ts": "2026-11-06T21:12:06Z"}])
    at = "2026-11-06T21:12:05Z"
    check([G.closer(_row(i, at), closes) for i in "OCSRN"]
          == [G.OWNER_CLOSE, G.OWNER_CLOSE, G.SEAT_CLOSE, G.RELENTLESS_CLOSE, G.UNRECORDED],
          "scope: an older row reads its closer from the ledger, and no close event is unrecorded")
    check(G.closer(_row("O", "2026-11-06T21:13:00Z"), closes) == G.UNRECORDED, "scope: a close older than the row is not its closer")
    check(G.closer(_row("O", at, sha="cd" * 20), closes) == G.UNRECORDED, "scope: another sha's close is not its closer")
    check(G.closer(_row("O", at, closed_by=G.SEAT_CLOSE), closes) == G.SEAT_CLOSE, "scope: the row's own field wins")
    rs = [_row("A", at, closed_by=G.RELENTLESS_CLOSE), _row("O", at, True, closed_by=G.OWNER_CLOSE), _row("L", at, True),
          _row("H", at, True, closed_by=G.SEAT_CLOSE), _row("U", at, True)]
    closes = G.ledger_closes([{"event": "close", "id": "L", "sha": "ab" * 5, "seat": "OWNER", "ts": at}])
    s = G.summary(rs, None, closes)
    check((s["closes"], s["agree"], s["disagree"], s["owner"], s["judged"], s["unrecorded"]) == (5, 1, 2, 2, 3, 1),
          "scope: an owner close is neither agreement nor disagreement nor sample; seat and unrecorded stay judged (%s)"
          % {k: s[k] for k in ("closes", "agree", "disagree", "owner", "judged", "unrecorded")})
    text = "\n".join(G.report_lines(s))
    check("owner-authority: 2 closes out of the predicate's scope, neither agreement nor disagreement: L, O" in text
          and "closer unrecorded: 1 closes" in text, "scope: the owner closes are their own line, the unrecorded said")
    check(G._closes_for([_row("A", at, closed_by=G.SEAT_CLOSE)]) is None, "scope: rows that all carry the field read no ledger")
    check(isinstance(G._closes_for([_row("A", at)]), dict), "scope: an older row reads the ledger")


def unrunnable():
    """Clause 3: RULED, the predicate is right and the row stays a disagreement."""
    with open(G.__file__, encoding="utf-8") as f:
        src = f.read()
    check("`unrunnable` run is not green and rejects (RULED" in src, "unrunnable: the ruling and its reason are in the module doc")
    run = {"kind": "run", "verdict": "unrunnable", "exit": None, "exam_hash": EXAM["hash"]}
    mark = {"kind": "marker", "verdict": "PASS"}
    ok, why = G.green([run, mark], EXAM)
    check(not ok and [G.reason_class(w) for w in why] == ["run not green"],
          "unrunnable: a Marker PASS on an unrunnable box run rejects, on the run alone (%s)" % why)
    check(G.green([dict(run, verdict=G.SKIPPED), mark], EXAM)[0], "unrunnable: the declared route, `skipped`, still accepts")
    s = G.summary([_row("U", "2026-11-06T19:55:54Z", True, closed_by=G.RELENTLESS_CLOSE, reasons=[why[0]])])
    check(s["disagree"] == 1 and s["by_class"] == {"gate accept / record reject: run not green": 1},
          "unrunnable: the gate's accept stays a counted disagreement")


def rescore_cohorts():
    """Clauses 2 and 4: owner rows are not verdict_gone; each row classified or still said to be unexplained."""
    sd = store("rescore_fixture")
    snap = os.path.dirname(sd)
    sha, at = "ab" * 20, "2026-11-06T18:30:00Z"

    def state(item, **kw):
        os.makedirs(os.path.join(sd, "items", item), exist_ok=True)
        with open(os.path.join(sd, "items", item, "state.json"), "w") as f:
            json.dump(dict({"item": item, "status": "retired", "contract": CONTRACT}, **kw), f)
    passed = {"candidate": {"sha": sha}, "check": {"verdict": "PASS", "nonce": "x"}}
    for item in ("OWNER_ROW", "OWNER_OLD_ROW", "GONE_ROW"):
        state(item)
    state("WEDGED_ROW", status="done", **passed)
    state("NORUN_ROW", status="done", **passed)
    state("UNRUN_ROW", status="done", **passed)
    E.append(sd, "UNRUN_ROW", sha, "run", {"verdict": "unrunnable", "exit": None, "exam_hash": EXAM["hash"]})
    d = os.path.join(sd, "items", "WEDGED_ROW", "receipts")
    os.makedirs(d)
    with open(os.path.join(d, "gen1.json"), "w") as f:
        json.dump({"item": "WEDGED_ROW", "sha": sha, "gen": 1, "at": "2026-11-06T18:00:00Z",
                   "boxrun": {"verdict": "green", "evidence_error": "TamperError: does not verify"}}, f)
    why = ["no marker: none", "no record: none"]
    with open(os.path.join(sd, G.SHADOW), "w") as f:
        for r in (_row("OWNER_ROW", at, True, closed_by=G.OWNER_CLOSE, reasons=why),
                  _row("OWNER_OLD_ROW", at, True, reasons=why),
                  _row("GONE_ROW", at, True, closed_by=G.RELENTLESS_CLOSE, reasons=why),
                  _row("WEDGED_ROW", at, True, closed_by=G.RELENTLESS_CLOSE, reasons=["no run: none"]),
                  _row("NORUN_ROW", at, True, closed_by=G.RELENTLESS_CLOSE, reasons=["no run: none"]),
                  _row("UNRUN_ROW", at, True, closed_by=G.RELENTLESS_CLOSE, reasons=["run not green: x"])):
            f.write(json.dumps(r) + "\n")
    closes = G.ledger_closes([{"event": "close", "id": "OWNER_OLD_ROW", "sha": sha, "seat": "OWNER", "ts": at}])
    rep, bad = G.rescore(snap, REPO, closes)
    names = {k: [x.split("@")[0] for x in v] for k, v in rep["cohort_rows"].items()}
    check(names.get(G.OWNER_CLOSE) == ["OWNER_ROW", "OWNER_OLD_ROW"],
          "rescore: owner rows, by field and by ledger, are their own cohort (%s)" % names)
    check(names.get(G.VERDICT_GONE) == ["GONE_ROW"], "rescore: verdict_gone holds only the row that had a verdict to lose")
    check(names.get(G.WEDGE) == ["WEDGED_ROW"], "rescore: a no-run row whose receipt shows the refusal is the wedge cohort, by name")
    un = " | ".join(bad)
    check(len(bad) == 2 and "NORUN_ROW" in un and "UNRUN_ROW" in un and "run not green" in un,
          "rescore: a no-run row with no receipt and the unrunnable row stay unexplained (%s)" % un[:200])
    check(rep["receipts_held"] == 1, "rescore: the reading counts the receipts it could read")
    shutil.rmtree(d)
    rep, bad = G.rescore(snap, REPO, closes)
    check(rep["receipts_held"] == 0 and any("WEDGED_ROW" in b and "no run" in b for b in bad),
          "rescore: without receipts the wedge row is unexplained (the 2026-11-06 reading of 10 no-run rows)")
    rc, out = quiet(G.main, ["rescore", "--snapshot", snap, "--min-rows", "1"])
    check(rc == 1 and "the snapshot holds no items/*/receipts" in out and "UNEXPLAINED WEDGED_ROW" in out,
          "rescore: the CLI says the snapshot cannot read the wedge cohort, and exits 1")


def main():
    try:
        wiring()
        corpus_and_breaks()
        rules()
        shadow()
        report()
        corpus_build()
        cli_end_to_end()
        receipt_wedge()
        window()
        scope()
        unrunnable()
        rescore_cohorts()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("\n%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
