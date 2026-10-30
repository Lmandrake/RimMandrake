#!/usr/bin/env python3
"""selftest_arena_tasks.py — arena_tasks.py census / freeze / check, each requirement proven by FORCED FAILURE.

ARENA_TASKS_BUILD_FROZEN_BEFORE_ASSIGNED criteria, and the failure planted for each:
  sanity      the census finds its hand-picked item (fixture AND real ledger); a missing sanity item, one the
              census rejects, and a ledger with the item's close removed each raise SanityFail
  hash        a frozen task file edited by one byte is refused by check, load_frozen and a re-freeze; restored, it
              is accepted again (the check is not refusing everything)
  live        a `live: full` task is refused by validate_task and by freeze; a frozen task edited to `full` is
              refused; every census task is live none/minimal/minimal+deps
  hidden      the leak scan first sees its tokens (instrument), then catches a hidden check planted in a task
              prompt, a stray file in the tasks dir, an arm clone and the event log; a judge dir inside the tasks
              dir; an inline hidden_checks body; a judge-only key in a task file
  remap       a close sha that exists only in the old-history repo maps to the rewritten commit with the same
              author date, author and subject; an excised one is rejected
  order       a freeze with an `assign` already in the log is refused
Writes only under a temp dir (ARENA_ROOT / ARENA_CLONES point there). The real-ledger probe is read-only.
"""
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_tasks as A  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def raises(exc, fn, *a, **k):
    try:
        fn(*a, **k)
    except exc as e:
        return str(e)
    return None


# ---------------------------------------------------------------- fixture git repos

def git(repo, *args, date=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="Fixture", GIT_AUTHOR_EMAIL="f@x", GIT_COMMITTER_NAME="Fixture",
               GIT_COMMITTER_EMAIL="f@x")
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env, timeout=60)
    assert r.returncode == 0, (args, r.stderr)
    return r.stdout.strip()


def commit(repo, files, msg, date):
    for rel, body in files.items():
        p = Path(repo) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if body is None:
            p.unlink()
        else:
            p.write_text(body)
    git(repo, "add", "-A", ".")          # fixture repo only, in a temp dir
    git(repo, "commit", "-q", "-m", msg, date=date)
    return git(repo, "rev-parse", "HEAD")


TOOL = "src/RimMandrake/Utils/tool.py"
TEST = "src/RimMandrake/Utils/selftest_tool.py"
NEWT = "src/RimMandrake/Utils/selftest_escape_guard.py"
RWT = "src/RimMandrake/Utils/selftest_rework_pin.py"


def build_repos(tmp):
    repo, old = tmp / "repo", tmp / "old"
    for r in (repo, old):
        r.mkdir()
        git(r, "init", "-q", "-b", "main")
    base_files = {TOOL: "def f():\n    return 1\n", TEST: "assert True  # selftest of tool.py, original body\n",
                  "infrastructure/state/items/FIXTURE_GOOD_FIX_ONE.md":
                      "# FIXTURE_GOOD_FIX_ONE\n\n## spec\nmake f return 2\n\n## criteria\nDone when: f() == 2\n"}
    commit(repo, base_files, "base", "2026-10-13T09:00:00+00:00")
    commit(old, base_files, "base", "2026-10-13T09:00:00+00:00")
    s = {}
    s["good"] = commit(repo, {TOOL: "def f():\n    return 2\n",
                              TEST: "from tool import f\nassert f() == 2  # pinned by the good fix, a long line\n"},
                       "fix good", "2026-10-14T10:03:00+00:00")
    s["esc"] = commit(repo, {TOOL: "def f():\n    return 3\n",
                             NEWT: "from tool import f\nassert f() == 3  # added by the escaped fix, hidden body\n"},
                      "fix esc", "2026-10-16T10:03:00+00:00")
    # the rework changes the parent's file (tool.py): only such a fix makes its parent Escaped (pool ruling)
    s["rework"] = commit(repo, {TOOL: "def f():\n    return 3  # reworked\n",
                                RWT: "from tool import f\nassert f() != 0  # the rework's own pin, hidden too\n"},
                         "fix rework", "2026-10-18T10:03:00+00:00")
    s["nostart"] = commit(repo, {TOOL: "def f():\n    return 4\n",
                                 TEST: "assert True  # nostart change to the test, long enough to count\n"},
                          "fix nostart", "2026-10-19T10:03:00+00:00")
    # the "rewritten" pair: same author date + author + subject in both repos, different trees -> different shas
    s["remap_new"] = commit(repo, {TOOL: "def f():\n    return 5\n",
                                   TEST: "assert True  # remapped fix, rewritten side, long enough\n"},
                            "fix remap", "2026-10-20T10:03:00+00:00")
    s["remap_old"] = commit(old, {TOOL: "def f():\n    return 5\n", "work/excised.bin": "x" * 50,
                                  TEST: "assert True  # remapped fix, rewritten side, long enough\n"},
                            "fix remap", "2026-10-20T10:03:00+00:00")
    s["excised_old"] = commit(old, {"work/excised.bin": "y" * 50}, "excised only", "2026-10-21T10:03:00+00:00")
    return repo, old, s


def ledger(s, drop_good_close=False, rework_in_pool=False, children=False, open_bug=False, late_close=False):
    E, n = [], [0]

    def ev(**k):
        n[0] += 1
        k.setdefault("seat", "FOUNDRY")
        if k["event"] == "file":
            k.setdefault("for", "FOUNDRY")
        k["tsn"] = str(n[0])
        E.append(k)

    def item(iid, day, sha, start=True, verify=True, kind="task"):
        ev(event="file", id=iid, title="title of " + iid, kind=kind, needs="offline", ts=day + "T10:00:00Z")
        if start:
            ev(event="claim", id=iid, ts=day + "T10:01:00Z")
            ev(event="start", id=iid, ts=day + "T10:01:30Z")
        if verify:
            ev(event="verify", id=iid, result="pass", config="c", evidence="e", sha=sha[:10], ts=day + "T10:03:30Z")
        if not (drop_good_close and iid == "FIXTURE_GOOD_FIX_ONE"):
            ev(event="close", id=iid, sha=sha[:10], reason="r", ts=day + "T10:04:00Z")

    item("FIXTURE_GOOD_FIX_ONE", "2026-10-14", s["good"])
    item("FIXTURE_ESC_FIX_TWO", "2026-10-16", s["esc"], verify=False)
    ev(event="file", id="FIXTURE_ESC_REWORK_THREE", title="rework of esc", kind="bug", needs="offline",
       caused_by="FIXTURE_ESC_FIX_TWO", ts="2026-10-18T10:00:00Z")
    if rework_in_pool:                    # the rework is itself a started, verified item: a pool candidate
        ev(event="claim", id="FIXTURE_ESC_REWORK_THREE", ts="2026-10-18T10:01:00Z")
        ev(event="start", id="FIXTURE_ESC_REWORK_THREE", ts="2026-10-18T10:01:30Z")
        ev(event="verify", id="FIXTURE_ESC_REWORK_THREE", result="pass", config="c", evidence="e",
           sha=s["rework"][:10], ts="2026-10-18T10:03:30Z")
    ev(event="close", id="FIXTURE_ESC_REWORK_THREE", sha=s["rework"][:10], reason="r", ts="2026-10-18T10:04:00Z")
    item("FIXTURE_NOSTART_FIX_FOUR", "2026-10-19", s["nostart"], start=False)
    item("FIXTURE_REMAP_FIX_FIVE", "2026-10-20", s["remap_old"])
    item("FIXTURE_EXCISED_FIX_SIX", "2026-10-21", s["excised_old"])
    item("FIXTURE_LATE_FIX_SEVEN", "2026-10-28", s["good"])            # out of window: not scanned
    if children:        # caused_by children of the good fix that are NOT closed code fixes: no escape
        ev(event="file", id="FIXTURE_GOOD_DESIGN_KID", title="design a follow-up", kind="design", needs="offline",
           caused_by="FIXTURE_GOOD_FIX_ONE", ts="2026-10-15T10:00:00Z")
        ev(event="file", id="FIXTURE_GOOD_REVIEW_KID", title="Review the good fix and mark it", kind="task",
           needs="offline", caused_by="FIXTURE_GOOD_FIX_ONE", ts="2026-10-15T11:00:00Z")
        ev(event="close", id="FIXTURE_GOOD_REVIEW_KID", sha=s["good"][:10], reason="r", ts="2026-10-15T11:30:00Z")
    if open_bug:        # an open fix-type child: the good fix's Clean is provisional
        ev(event="file", id="FIXTURE_GOOD_BUG_KID", title="f still wrong", kind="bug", needs="offline",
           caused_by="FIXTURE_GOOD_FIX_ONE", ts="2026-10-15T12:00:00Z")
    if late_close:      # a second close after the window: the item is scanned and rejected with a reason
        ev(event="close", id="FIXTURE_REMAP_FIX_FIVE", sha=s["remap_old"][:10], reason="r", ts="2026-10-29T00:00:00Z")
    return E


# ---------------------------------------------------------------- tests

def t_census(tmp, repo, old, s):
    pool, rep = A.census(ledger(s), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old)
    got = {t["source_item"]: (t, h) for t, h in pool}
    # BENCH pool ruling: no start event needed, unlabelled items stay (label null); the rework is a candidate too,
    # rejected only because its public file names the escaped task's hidden check (the chain rule)
    check(set(got) == {"FIXTURE_GOOD_FIX_ONE", "FIXTURE_ESC_FIX_TWO", "FIXTURE_NOSTART_FIX_FOUR",
                       "FIXTURE_REMAP_FIX_FIVE"},
          "census keeps good, escaped, nostart, remapped (got %s)" % sorted(got))
    check(rep["sanity"]["found"] and rep["pool"] == 4, "report: pool 4 with the sanity item found")
    check(rep["scanned_closed_in_window"] == 6, "the out-of-window close is not scanned (6 scanned)")
    check("no start before close" not in rep["rejects"] and "FIXTURE_NOSTART_FIX_FOUR" in got,
          "forced (ruling): a close with no start event is NOT rejected (%s)" % rep["rejects"])
    check(any(k.startswith("would expose") for k in rep["rejects"]) and "FIXTURE_ESC_REWORK_THREE" not in got,
          "the rework, now a candidate, is chain-rejected (%s)" % rep["rejects"])
    check(rep["rejects"].get("close sha excised by the history rewrite") == 1, "an excised-only sha is rejected")
    check(got["FIXTURE_GOOD_FIX_ONE"][1]["label"] == "Clean" and got["FIXTURE_ESC_FIX_TWO"][1]["label"] == "Escaped",
          "labels: verified + no rework = Clean; a caused_by rework in 7 days = Escaped")
    t, h = got["FIXTURE_REMAP_FIX_FIVE"]
    check(h["fix_sha"] == s["remap_new"] and h["sha_resolution"] == "remapped",
          "an old-history sha maps to the rewritten commit")
    check(t["base_sha"] == s["nostart"], "the remapped task's base is the rewritten parent")
    tg = got["FIXTURE_GOOD_FIX_ONE"][0]
    check(tg["criteria"] == "Done when: f() == 2" and "make f return 2" in tg["prompt"],
          "prompt and criteria come from the prose at base_sha")
    check(tg["size"] == 1 and tg["kind"] == "python-util" and "selftest_tool.py" in tg["proof"], "size, kind, proof")
    te = got["FIXTURE_ESC_FIX_TWO"][0]
    check(NEWT not in te["proof"] and "1 held-back" in te["proof"],
          "a selftest the fix ADDED is not named in the proof, only counted: %s" % te["proof"][:80])
    he = got["FIXTURE_ESC_FIX_TWO"][1]
    check(any(r["item"] == "FIXTURE_ESC_REWORK_THREE" and r["tests"] and not r["needs_authoring"]
              for r in he["reworks"]), "the rework's added test becomes the Escaped item's hidden check")
    check(all(t["live"] in A.LIVE_OK for t, _ in pool), "every census task has an allowed live tier")
    # forced: a pool candidate that is an earlier pool task's rework would expose that task's hidden check
    pc, rc = A.census(ledger(s, rework_in_pool=True), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old)
    ids = {t["source_item"] for t, _ in pc}
    check("FIXTURE_ESC_FIX_TWO" in ids and "FIXTURE_ESC_REWORK_THREE" not in ids and any(
          k.startswith("would expose") for k in rc["rejects"]),
          "a chained later task naming an earlier task's hidden check is rejected, the earlier kept (%s)" % rc["rejects"])
    # forced failures of the sanity probe
    for name, kw in (("absent item", dict(sanity="FIXTURE_NEVER_FILED")),
                     ("rejected item", dict(sanity="FIXTURE_EXCISED_FIX_SIX"))):
        e = raises(A.SanityFail, A.census, ledger(s), repo=repo, old_history=old, **kw)
        check(bool(e), "SanityFail on a %s: %s" % (name, (e or "NOT RAISED")[:90]))
    e = raises(A.SanityFail, A.census, ledger(s, drop_good_close=True), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE",
               old_history=old)
    check(bool(e), "SanityFail when the sanity item's close is missing from the ledger")
    return pool


def fresh_arena(tmp, name):
    root = tmp / name
    os.environ["ARENA_ROOT"] = str(root)
    os.environ["ARENA_CLONES"] = str(tmp / (name + "_clones"))
    (tmp / (name + "_clones")).mkdir()
    return A.paths(root)


def t_hash(tmp, pool):
    p = fresh_arena(tmp, "arena_hash")
    A.write_pool(pool, p)
    check(A.check(p) != [] and any("not frozen" in x for x in A.check(p)), "before freeze, check refuses (not frozen)")
    r = A.freeze(p, now="2026-10-30T00:00:00Z")
    check(r["frozen_new"] == 4 and len(r["pool_sha256"]) == 64, "freeze hashes 4 tasks and a pool hash")
    check(A.check(p) == [], "frozen and unchanged: check passes")
    again = A.freeze(p, now="2026-10-30T00:00:01Z")
    check(again["frozen_new"] == 0, "re-freezing an unchanged pool writes nothing")
    tf = p["tasks"] / "RP_FIXTURE_GOOD_FIX_ONE.json"
    orig = tf.read_bytes()
    task = json.loads(orig)
    task["criteria"] += " (or close enough)"
    tf.write_bytes(A._dump(task))
    probs = A.check(p)
    check(any("RP_FIXTURE_GOOD_FIX_ONE" in x and "hash" in x for x in probs), "a changed task file is refused by "
          "its hash: %s" % (probs[:1] or ["NOT REFUSED"])[0][:90])
    check(bool(raises(A.TaskRefused, A.load_frozen, "RP_FIXTURE_GOOD_FIX_ONE", p)), "load_frozen refuses it too")
    check(bool(raises(A.TaskRefused, A.freeze, p)), "a re-freeze cannot launder the change")
    w = A.write_pool(pool, p)
    check(w["unchanged_frozen"] == 4 and w["wrote"] == 0 and w["refused_frozen_changed"] == [],
          "a re-census reproduces every frozen task byte-for-byte and rewrites none")
    check(tf.read_bytes() != orig and any("RP_FIXTURE_GOOD_FIX_ONE" in x for x in A.check(p)),
          "the re-census did not launder the edited file: it is still refused")
    tf.write_bytes(orig)
    check(A.check(p) == [], "restored byte-for-byte: accepted again")
    hf = p["judge"] / "RP_FIXTURE_GOOD_FIX_ONE.json"
    hb = hf.read_bytes()
    hf.write_bytes(hb.replace(b'"Clean"', b'"Escaped"'))
    check(any("judge file" in x for x in A.check(p)), "a changed judge file (label flipped) is refused")
    hf.write_bytes(hb)
    return p


def t_live(tmp, pool):
    p = fresh_arena(tmp, "arena_live")
    A.write_pool(pool, p)
    tf = p["tasks"] / "RP_FIXTURE_ESC_FIX_TWO.json"
    t = json.loads(tf.read_text())
    t["live"] = "full"
    tf.write_bytes(A._dump(t))
    e = raises(A.TaskRefused, A.validate_task, t, p["judge"] / tf.name, p)
    check(bool(e) and "full" in e, "validate_task refuses live: full")
    e = raises(A.TaskRefused, A.freeze, p)
    check(bool(e) and "full" in e and A.frozen_hashes(p) == {}, "freeze refuses a pool with live: full and freezes "
          "nothing")
    t["live"] = "none"
    tf.write_bytes(A._dump(t))
    A.freeze(p)
    t["live"] = "full"
    tf.write_bytes(A._dump(t))
    check(any("RP_FIXTURE_ESC_FIX_TWO" in x for x in A.check(p)), "a frozen task edited to live: full is refused")


def t_hidden(tmp, pool, s):
    p = fresh_arena(tmp, "arena_hidden")
    A.write_pool(pool, p)
    A.freeze(p)
    # a REGISTERED arm clone (the whitelist): a plant inside it is a deviation from its build manifest
    good = {t["source_item"]: t for t, _ in pool}["FIXTURE_GOOD_FIX_ONE"]   # ESC's base holds GOOD's fix: not clean
    A.build_arm_clone(good["base_sha"], Path(os.environ["ARENA_CLONES"]) / "ralph_a", src=Path(tmp) / "repo",
                      p=p)
    toks = set()
    for hf in p["judge"].glob("*.json"):
        toks.update(A.leak_tokens(json.loads(hf.read_text())))
    check(s["esc"] in toks and "fixture_esc_rework_three" in toks and NEWT.lower() in toks and RWT.lower() in toks,
          "instrument: the leak tokens include fix sha, rework id and added test paths")
    check(A.find_leaks(p) == [], "clean arena: no leak")
    for t, _ in pool:
        raw = (p["tasks"] / (t["id"] + ".json")).read_text()
        check(s["esc"][:12] not in raw and NEWT not in raw and '"label"' not in raw,
              "%s carries no fix sha, hidden test path or label" % t["id"])
    body = (Path(tmp) / "repo" / RWT).read_text()
    plants = [("tasks/RP_FIXTURE_ESC_FIX_TWO.json", None), ("tasks/notes.txt", "see FIXTURE_ESC_REWORK_THREE"),
              ("clones/ralph_a/src/x.py", body), ("events/harness.jsonl", None)]
    for rel, text in plants:
        root = Path(os.environ["ARENA_CLONES"]) if rel.startswith("clones/") else p["root"]
        fp = root / rel.split("/", 1)[1] if rel.startswith("clones/") else root / rel
        fp.parent.mkdir(parents=True, exist_ok=True)
        before = fp.read_bytes() if fp.exists() else None
        if rel.endswith("RP_FIXTURE_ESC_FIX_TWO.json"):
            t = json.loads(before)
            t["prompt"] += "\nhint: " + NEWT
            fp.write_bytes(A._dump(t))
        elif rel.endswith("harness.jsonl"):
            fp.write_bytes(before + (json.dumps({"event": "note", "detail": s["esc"]}) + "\n").encode())
        else:
            fp.write_text(text)
        leaks = A.find_leaks(p)
        check(any(str(fp) in x for x in leaks), "a hidden check planted at %s is caught" % rel)
        if before is None:
            fp.unlink()
        else:
            fp.write_bytes(before)
    check(A.find_leaks(p) == [], "plants removed: no leak again")
    # judge dir inside an arm-readable root
    q = dict(p, judge=p["tasks"] / "judge")
    check(any("inside arm-readable" in x for x in A.find_leaks(q)), "a judge dir inside the tasks dir is refused")
    # inline hidden content and judge-only keys in a task file
    tf = p["tasks"] / "RP_FIXTURE_GOOD_FIX_ONE.json"
    t = json.loads(tf.read_text())
    for bad in (dict(t, hidden_checks={"held_by": "judge", "sha256": t["hidden_checks"]["sha256"], "checks": [1]}),
                dict(t, label="Clean"), dict(t, fix_sha=s["good"])):
        e = raises(A.TaskRefused, A.validate_task, bad, p["judge"] / tf.name, p)
        check(bool(e), "refused in a task file: %s" % (e or "NOT REFUSED")[:80])



def t_census2(tmp, repo, old, s):
    """(4) labels need a closed code-fix rework; (e) provisional Clean; (g) reasons; (h) deleted test; (6) own leak."""
    pool, rep = A.census(ledger(s, children=True), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old)
    h = {t["source_item"]: hh for t, hh in pool}["FIXTURE_GOOD_FIX_ONE"]
    v = {c["item"]: c["verdict"] for c in h.get("rework_candidates", [])}
    check(h["label"] == "Clean" and v.get("FIXTURE_GOOD_DESIGN_KID", "").startswith("not a fix")
          and "review" in v.get("FIXTURE_GOOD_REVIEW_KID", ""),
          "a design child and a closed 'Review ...' child do not make the fix Escaped (%s, %s)" % (h["label"], v))
    pool, rep = A.census(ledger(s, open_bug=True), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old)
    h = {t["source_item"]: hh for t, hh in pool}["FIXTURE_GOOD_FIX_ONE"]
    check(h["label"] == "Clean" and h.get("label_pending") == ["FIXTURE_GOOD_BUG_KID"],
          "an open bug child leaves Clean provisional (label_pending %s)" % h.get("label_pending"))
    p = fresh_arena(tmp, "arena_prov")
    A.write_pool(pool, p)
    e = raises(A.TaskRefused, A.freeze, p, now="2026-11-10T00:00:00Z")
    check(bool(e) and "provisional" in e and A.frozen_hashes(p) == {},
          "freeze refuses a Clean label with an open fix-type rework: %s" % (e or "NOT REFUSED")[:70])
    pool, _ = A.census(ledger(s), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old)
    p = fresh_arena(tmp, "arena_early")
    A.write_pool(pool, p)
    e = raises(A.TaskRefused, A.freeze, p, now="2026-10-20T00:00:00Z")
    check(bool(e) and "window ends 2026-10-21" in e, "freeze refuses a Clean label before its 7-day rework window "
          "ends: %s" % (e or "NOT REFUSED")[:70])
    check(A.freeze(p, now="2026-10-28T00:00:00Z")["frozen_new"] == 4, "after every window ends the pool freezes")
    _, rep = A.census(ledger(s, late_close=True), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old)
    check(rep["scanned_closed_in_window"] == 6 and rep["rejects"].get("last close falls outside the window") == 1,
          "an item whose last close is outside the window is scanned and rejected with a reason (%s)" % rep["rejects"])


def t_census3(tmp, repo, old, s):
    """(h) a deleted test; (6) a self-leaking task."""
    real = A._prose_at

    def leaky(repo_, sha, iid):
        return ("## spec\nsee " + NEWT + "\n") if iid == "FIXTURE_ESC_FIX_TWO" else real(repo_, sha, iid)
    A._prose_at = leaky
    try:
        pool2, rep2 = A.census(ledger(s), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old)
        ids = {t["source_item"] for t, _ in pool2}
        check("FIXTURE_ESC_FIX_TWO" not in ids and "FIXTURE_GOOD_FIX_ONE" in ids and any(
              "its own hidden check" in k for k in rep2["rejects"]),
              "a self-leaking task is rejected alone; the census goes on (%s)" % rep2["rejects"])
    except A.ArenaError as e:
        check(False, "a self-leaking task aborted the census: %s" % e)
    finally:
        A._prose_at = real
    check(not A.proof_for([TOOL, TEST], set(), {TEST}) and A.proof_for([TOOL, TEST], set(), set()),
          "a deleted test is not objective proof (a changed one is)")


def t_match():
    """(5)/(f) the matcher: case, sha prefixes, slashes, any 120-char window, encodings, escaping, short bodies."""
    long_ = "\n".join("def test_case_%d():\n    assert compute_value(%d) == expected_table[%d], 'row %d'"
                      % (i, i, i, i) for i in range(20))
    sha = "0123456789abcdef0123456789abcdef01234567"
    h = {"task": "RP_X", "fix_sha": sha, "reworks": [],
         "checks": [{"path": "src/a/selftest_x.py", "added": True, "body": long_, "novel": [long_]}]}
    m = A.Matcher([h])
    win = long_[700:900]
    cases = [("uppercase sha", ("see " + sha[:20].upper()).encode()), ("10-char sha", b"commit 0123456789 x"),
             ("backslash path", b"look at SRC\\a\\selftest_x.py"),
             ("a window 700 chars in, re-indented", "\n\t ".join(win.split()).encode()),
             ("base64", base64.b64encode(win.encode())), ("base64 wrapped", b"\n".join(
                 base64.b64encode(win.encode())[i:i + 20] for i in range(0, 300, 20))),
             ("utf-16", win.encode("utf-16")), ("utf-16-be", win.encode("utf-16-be")),
             ("json-escaped", json.dumps({"a": win}).encode()),
             ("json twice", json.dumps(json.dumps({"a": win})).encode())]
    for name, raw in cases:
        check(bool(m.hits(raw)), "matcher catches the %s form" % name)
    for name, raw in (("unrelated text", b"def other():\n    return compute(1)\n" * 40),
                      ("a shorter sha prefix", b"0123456 is only 7 and 012345 is 6"),
                      ("boilerplate imports", b"import os\nimport sys\nimport json\n")):
        hit = m.hits(raw)
        check(not hit or name == "a shorter sha prefix", "matcher stays quiet on %s (%s)" % (name, hit))
    check(not m.hits(b"012345 abcdef"), "a 6-hex run is not a sha hit")
    ms = A.Matcher([{"task": "RP_S", "checks": [{"path": "t/selftest_s.py", "added": False,
                                                 "body": "assert f() == 2\n", "novel": ["assert f() == 2\n"]}]}])
    check(bool(ms.hits(b"x = 1\nASSERT  f() == 2\n")) and not ms.hits(b"assert f() == 3"),
          "a short body is matched exactly (and only exactly)")


def t_clone(tmp, pool, s):
    """(1)/(a)/(b) arm clones: only a depth-1 clone at base_sha is clean."""
    p = fresh_arena(tmp, "arena_clone")
    A.write_pool(pool, p)
    clones = Path(os.environ["ARENA_CLONES"])
    tg = {t["source_item"]: t for t, _ in pool}["FIXTURE_GOOD_FIX_ONE"]
    cl = A.build_arm_clone(tg["base_sha"], clones / "ralph_b", src=tmp / "repo", task=tg["id"])
    r = subprocess.run(["git", "-C", str(cl), "cat-file", "-e", s["good"]], capture_output=True)
    check(r.returncode != 0, "instrument: the built clone holds no commit after base_sha")
    check(A.find_leaks(p) == [], "a depth-1 clone at base_sha is clean: %s" % A.find_leaks(p)[:1])
    (cl / "src" / "drop.txt").write_text("hint " + NEWT)
    check(any("drop.txt" in x for x in A.find_leaks(p)), "an untracked file carrying a hidden check is caught")
    (cl / "src" / "drop.txt").unlink()
    rw_body = (tmp / "repo" / RWT).read_text()
    (cl / TOOL).write_text((cl / TOOL).read_text() + "\n" + rw_body)
    check(any(TOOL in x for x in A.find_leaks(p)), "a TRACKED file whose content differs from base is scanned")
    git(cl, "add", TOOL)
    git(cl, "commit", "-q", "-m", "arm commit")
    check(any(TOOL in x for x in A.find_leaks(p)), "... also once committed in the clone")
    shutil.rmtree(cl)
    cl = A.build_arm_clone(tg["base_sha"], clones / "ralph_b", src=tmp / "repo", task=tg["id"])
    (cl / "stash.txt").write_text(rw_body)
    git(cl, "add", "stash.txt")
    (cl / "stash.txt").unlink()
    check(any("git blob" in x for x in A.find_leaks(p)), "a hidden check only in the clone's object store is caught")
    shutil.rmtree(cl)
    # WHITELIST: a tree the harness did not build is unverified, whatever it says about itself
    shutil.copytree(tmp / "repo", clones / "full")
    lk = A.find_leaks(p)
    check(any("[*]" in x and "unregistered directory" in x for x in lk),
          "a full-history copy (not built by build_arm_clone) refuses every task: %s" % lk[:1])
    gd = clones / "full" / ".git"
    (gd / "arena_clone.json").write_text(json.dumps({"task": tg["id"], "base_sha": tg["base_sha"],
                                                     "source": str(tmp / "repo")}))
    git(clones / "full", "checkout", "-q", "--detach", tg["base_sha"])
    check(any("unregistered" in x for x in A.find_leaks(p)), "a marker forged inside .git buys nothing (the "
          "registry is harness-owned, keyed by path + nonce)")
    shutil.rmtree(clones / "full")
    A.build_arm_clone(s["esc"], clones / "atfix", src=tmp / "repo", task=tg["id"])
    lk = A.find_leaks(p)
    check(any("starts at base_sha" in x for x in lk) and any(s["esc"][:12] in x for x in lk),
          "a clone built at the fix sha is flagged (fix commit in its build, base mismatch): %s" % lk[:1])
    shutil.rmtree(clones / "atfix")
    cl = A.build_arm_clone(tg["base_sha"], clones / "ralph_b", src=tmp / "repo", task=tg["id"])
    (cl / ".git" / "objects" / "info").mkdir(parents=True, exist_ok=True)
    (cl / ".git" / "objects" / "info" / "alternates").write_text(str(tmp / "repo" / ".git" / "objects") + "\n")
    check(any("alternates" in x and "[*]" in x for x in A.find_leaks(p)), "alternates in a registered clone are "
          "flagged for every task")
    shutil.rmtree(cl)
    cl = A.build_arm_clone(tg["base_sha"], clones / "ralph_b", src=tmp / "repo", task=tg["id"])
    git(cl, "fetch", "-q", "--no-tags", "file://" + str(tmp / "repo"), "main")
    check(any("commit/tag object" in x and "[*]" in x for x in A.find_leaks(p)),
          "a registered clone that fetched later history is flagged for every task")
    shutil.rmtree(cl)
    te = {t["source_item"]: t for t, _ in pool}["FIXTURE_ESC_FIX_TWO"]
    A.build_arm_clone(te["base_sha"], clones / "chain", src=tmp / "repo", task=te["id"])
    check(any("RP_FIXTURE_GOOD_FIX_ONE" in x for x in A.find_leaks(p)), "a clone whose base holds ANOTHER pool "
          "task's fixed test is flagged (chained tasks need per-arm isolation)")
    shutil.rmtree(clones / "chain")
    check(A.find_leaks(p) == [], "clones removed: clean again")


def t_links(tmp, pool):
    """(2) a symlink into the judge dir or outside every arm-readable root is flagged, never skipped."""
    p = fresh_arena(tmp, "arena_links")
    A.write_pool(pool, p)
    clones = Path(os.environ["ARENA_CLONES"])
    # a registered clone already handed to its arm (assign logged): the arm's own files are its work
    good = {t["source_item"]: t for t, _ in pool}["FIXTURE_GOOD_FIX_ONE"]
    A.build_arm_clone(good["base_sha"], clones / "ralph_l", src=tmp / "repo", task=good["id"], p=p)
    p["events"].mkdir(parents=True, exist_ok=True)
    (p["events"] / "harness.jsonl").write_text(json.dumps({"event": "assign", "task": good["id"]}) + "\n")
    (clones / "ralph_l" / "sub").mkdir(parents=True)
    links = [(clones / "ralph_l" / "h", str(p["judge"])), (p["tasks"] / "h", "../judge/hidden"),
             (clones / "ralph_l" / "etc", "/etc"), (clones / "ralph_l" / "jf", str(p["judge"] / os.listdir(p["judge"])[0]))]
    os.symlink("sub", clones / "ralph_l" / "ok")
    check(A.find_leaks(p) == [], "a symlink inside its own root is not a leak")
    for lp, tgt in links:
        os.symlink(tgt, lp)
        check(any(str(lp) in x for x in A.find_leaks(p)), "symlink %s -> %s is flagged" % (lp.name, tgt))
        lp.unlink()
    os.link(p["judge"] / os.listdir(p["judge"])[0], clones / "ralph_l" / "hard")
    check(any("hard link" in x for x in A.find_leaks(p)), "a hard link to a judge file is flagged")
    (clones / "ralph_l" / "hard").unlink()
    # a link base_sha itself tracks (the real repo has .claude/skills/* -> /mnt/d/...) is task content, not a leak;
    # the same link retargeted by the arm, or a tracked link into the judge dir, is still flagged
    src = tmp / "linkrepo"
    src.mkdir()
    sh = lambda *a: subprocess.run(["git", "-C", str(src), *a], capture_output=True, text=True, check=True)
    sh("init", "-q")
    os.symlink("/etc", src / "abs")
    os.symlink(str(p["judge"]), src / "peek")
    sh("add", "abs")
    sh("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
    lbase = sh("rev-parse", "HEAD").stdout.strip()
    sh("add", "peek")
    sh("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "peek")
    lpeek = sh("rev-parse", "HEAD").stdout.strip()
    c1 = A.build_arm_clone(lbase, clones / "ralph_lk", src=src)
    check(not any("ralph_lk" in x for x in A.find_leaks(p)), "an unchanged symlink tracked at base is not flagged")
    os.unlink(c1 / "abs")
    os.symlink("/usr", c1 / "abs")
    check(any(str(c1 / "abs") in x for x in A.find_leaks(p)), "a tracked symlink the arm retargeted is flagged")
    shutil.rmtree(c1)
    c2 = A.build_arm_clone(lpeek, clones / "ralph_lk", src=src)
    check(any(str(c2 / "peek") in x and "judge" in x for x in A.find_leaks(p)),
          "a symlink into the judge dir is flagged even when base_sha tracks it")
    shutil.rmtree(c2)


def t_auth(tmp, pool):
    """(3)/(c)/(i)/(6) the freeze authority, the read-once loader, pool agreement, strict JSON."""
    p = fresh_arena(tmp, "arena_auth")
    A.write_pool(pool, p)
    A.freeze(p, now="2026-11-10T00:00:00Z")
    check(A.check(p) == [] and p["freeze"].is_file(), "frozen into judge/freeze.jsonl: check passes")
    tid = "RP_FIXTURE_GOOD_FIX_ONE"
    tf, hf = p["tasks"] / (tid + ".json"), p["judge"] / (tid + ".json")
    orig = tf.read_bytes()
    t = json.loads(orig)
    t["criteria"] += " (or close enough)"
    tf.write_bytes(A._dump(t))
    forged = p["events"] / "aaa.jsonl"
    forged.write_text(json.dumps({"event": "freeze", "task": tid, "detail": {
        "sha256": A.hashlib.sha256(tf.read_bytes()).hexdigest(),
        "hidden_sha256": A.hashlib.sha256(hf.read_bytes()).hexdigest()}}) + "\n")
    probs = A.check(p)
    check(any("forged" in x for x in probs) and any(tid in x and "hash" in x for x in probs),
          "a forged freeze record in events/aaa.jsonl is flagged and does not launder the edit")
    forged.unlink()
    tf.write_bytes(orig)
    log = p["log"].read_bytes()
    p["log"].write_bytes(b"\n".join(ln for ln in log.split(b"\n") if tid.encode() not in ln))
    p["log"].write_bytes(p["log"].read_bytes() + b"\n")
    check(any("lost its freeze record" in x for x in A.check(p)), "a lost event-log freeze line is flagged")
    p["log"].write_bytes(log)
    auth = p["freeze"].read_bytes()
    p["freeze"].write_bytes(b"\n".join(auth.split(b"\n")[1:]))
    probs = A.check(p)
    check(any("chain" in x for x in probs), "a dropped authority line breaks the chain: %s" % probs[:1])
    check(bool(raises(A.ArenaError, A.freeze, p, now="2026-11-10T00:00:01Z")), "... and freeze refuses")
    p["freeze"].write_bytes(auth)
    first = json.loads(auth.split(b"\n")[0])
    A._append_authority(p, [{k: v for k, v in first.items() if k not in ("seq", "prev")}])
    e = raises(A.ArenaError, A.frozen_hashes, p)
    check(bool(e) and "duplicate" in e, "a duplicate (validly chained) freeze record is an error: %s" % (e or "")[:60])
    p["freeze"].write_bytes(auth[:-7])
    probs = A.check(p)
    check(any("truncated" in x or "unreadable" in x for x in probs), "a truncated authority fails closed: %s"
          % probs[:1])
    try:
        rc = A.main(["check"])
        check(rc == 1, "the CLI reports it cleanly (exit %s, no traceback)" % rc)
    except Exception as ex:      # noqa: BLE001 - the defect is exactly an uncaught exception
        check(False, "the CLI raised on a truncated log: %r" % ex)
    p["freeze"].write_bytes(auth)
    p["log"].write_bytes(log[:-3])
    check(any("truncated" in x or "unreadable" in x for x in A.check(p)), "a truncated event log fails closed")
    p["log"].write_bytes(log)
    check(A.check(p) == [], "restored: clean")


def t_auth2(tmp, pool):
    """(c) the read-once leak-checking loader; (i) pool agreement; (6) strict JSON and integer size."""
    p = fresh_arena(tmp, "arena_auth2")
    A.write_pool(pool, p)
    A.freeze(p, now="2026-11-10T00:00:00Z")
    tid = "RP_FIXTURE_GOOD_FIX_ONE"
    tf = p["tasks"] / (tid + ".json")
    orig = tf.read_bytes()
    # (i) the stored pool and the census must agree
    w = A.write_pool([x for x in pool if x[0]["id"] != tid], p)
    check(w.get("frozen_not_in_pool") == [tid], "a frozen task the census no longer picks is reported: %s"
          % w.get("frozen_not_in_pool"))
    tf.unlink()
    e = raises(A.TaskRefused, A.freeze, p, now="2026-11-10T00:00:02Z")
    check(bool(e) and "missing" in e, "freeze refuses when a frozen task file is gone: %s" % (e or "NOT REFUSED")[:60])
    tf.write_bytes(orig)
    # (6) strict JSON and an integer size
    p2 = fresh_arena(tmp, "arena_json")
    A.write_pool(pool, p2)
    tf2 = p2["tasks"] / (tid + ".json")
    raw = tf2.read_bytes()
    tf2.write_bytes(raw.replace(b'"live": "none"', b'"live": "full", "live": "none"', 1))
    e = raises(A.TaskRefused, A.freeze, p2, now="2026-11-10T00:00:00Z")
    check(bool(e) and "duplicate key" in e, "a duplicate JSON key is refused: %s" % (e or "NOT REFUSED")[:60])
    tf2.write_bytes(raw)
    t = json.loads(raw)
    for bad in (True, 3, "1", 1.0):
        e = raises(A.TaskRefused, A.validate_task, dict(t, size=bad), p2["judge"] / tf2.name, p2)
        check(bool(e), "size %r is refused" % (bad,))
    # (c) the loader refuses on a leak and reads the task file once
    (p["tasks"] / "notes.txt").write_text("hint " + NEWT)
    check(bool(raises(A.TaskRefused, A.load_frozen, tid, p)), "load_frozen refuses while a hidden check is readable")
    check(A.load_frozen(tid, p, leaks=False)["id"] == tid, "... (its hash/schema half alone accepts)")
    (p["tasks"] / "notes.txt").unlink()
    reads, real = [], Path.read_bytes

    def counting(self):
        if self == tf:
            reads.append(1)
        return real(self)
    Path.read_bytes = counting
    try:
        A.load_frozen(tid, p, leaks=False)
    finally:
        Path.read_bytes = real
    check(len(reads) == 1, "load_frozen reads the task file once and parses those bytes (%d reads)" % len(reads))

LOCK_HOLDER = r"""
import fcntl, json, sys, time
lock, log, sig = sys.argv[1:4]
with open(lock, "a") as fh:
    fcntl.flock(fh, fcntl.LOCK_EX)
    open(sig, "w").write("held")
    time.sleep(1.5)
    with open(log, "a") as lf:
        lf.write(json.dumps({"event": "assign", "arm": "ralph_a", "task": "RP_FIXTURE_GOOD_FIX_ONE"}) + "\n")
"""


def t_lock(tmp, pool):
    """(d) an assign landing while freeze runs: the lock makes freeze see it (refuse) rather than miss it."""
    p = fresh_arena(tmp, "arena_lock")
    A.write_pool(pool, p)
    p["events"].mkdir(parents=True, exist_ok=True)
    sig = tmp / "lock.sig"
    pr = subprocess.Popen([sys.executable, "-c", LOCK_HOLDER, str(p["lock"]), str(p["log"]), str(sig)])
    for _ in range(100):
        if sig.exists():
            break
        time.sleep(0.05)
    e = raises(A.TaskRefused, A.freeze, p, now="2026-11-10T00:00:00Z")
    pr.wait(timeout=30)
    check(bool(e) and "assign" in e and A.frozen_hashes(p) == {},
          "freeze waits on the arena lock and refuses the assign that landed meanwhile: %s" % (e or "NOT REFUSED")[:60])

def t_order(tmp, pool):
    p = fresh_arena(tmp, "arena_order")
    A.write_pool(pool, p)
    A._append(p, [{"ts": "2026-10-30T00:00:00Z", "arm": "ralph_a", "task": "RP_FIXTURE_GOOD_FIX_ONE",
                   "event": "assign"}])
    e = raises(A.TaskRefused, A.freeze, p)
    check(bool(e) and "assign" in e, "freeze after an assign event is refused")


# ---------------------------------------------------------------- fix round 2 (pool ruling, whitelist clone check)

def _ev_of(E, iid, event="file"):
    return next(e for e in E if e.get("id") == iid and e.get("event") == event)


def t_pool_ruling(tmp, repo, old, s):
    """Pool ruling: descendants are followed transitively; a child filed seconds BEFORE the close counts; a rework
    counts only if its fix changes one of the parent's files; pre-rewrite shas are pinned (never pushed)."""
    from types import SimpleNamespace as NS
    kids = {"P": [NS(id="C")], "C": [NS(id="G")], "G": [NS(id="GG"), NS(id="P")], "GG": [NS(id="GGG")]}
    got = [(c.id, g) for c, g in A._descendants("P", kids)]
    check(got == [("C", 1), ("G", 2), ("GG", 3)], "descendants: grandchildren followed, a cycle stops, depth 3: %s"
          % got)
    # a grandchild rework (ESC -> design MID -> REWORK) still makes ESC Escaped
    E = ledger(s)
    E.insert(E.index(_ev_of(E, "FIXTURE_ESC_REWORK_THREE")), {
        "event": "file", "id": "FIXTURE_ESC_MID_REVIEW", "title": "review of esc", "kind": "review",
        "needs": "offline", "caused_by": "FIXTURE_ESC_FIX_TWO", "seat": "FOUNDRY", "for": "FOUNDRY",
        "ts": "2026-10-17T10:00:00Z", "tsn": "m1"})
    _ev_of(E, "FIXTURE_ESC_REWORK_THREE")["caused_by"] = "FIXTURE_ESC_MID_REVIEW"
    pool2, _ = A.census(E, repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old)
    lab = {t["source_item"]: h["label"] for t, h in pool2}
    check(lab.get("FIXTURE_ESC_FIX_TWO") == "Escaped", "a grandchild rework (via a review child) counts: %s" % lab)
    # a child filed 10 s BEFORE the parent's close (the close and the finding raced) still counts
    E = ledger(s)
    _ev_of(E, "FIXTURE_ESC_REWORK_THREE")["ts"] = "2026-10-16T10:03:50Z"
    pool3, _ = A.census(E, repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old)
    lab = {t["source_item"]: h["label"] for t, h in pool3}
    check(lab.get("FIXTURE_ESC_FIX_TWO") == "Escaped", "a child filed seconds before the close counts: %s" % lab)
    # the file-intersection rule: a 'remaining half' whose fix touches none of the parent's files is no escape
    r = NS(id="R", kind="bug", title="remaining half of esc", state="done")
    by_id = {"R": [{"event": "close", "sha": s["rework"][:10]}]}
    res = lambda sha: (s["rework"],)
    v1 = A._rework_verdict(r, by_id, res, repo, parent_fix=s["esc"], parent_files=frozenset({"other/elsewhere.py"}))
    v2 = A._rework_verdict(r, by_id, res, repo, parent_fix=s["esc"], parent_files=frozenset({TOOL}))
    v3 = A._rework_verdict(r, by_id, res, repo, parent_fix=s["rework"], parent_files=frozenset({TOOL}))
    check(v1[0].startswith("its fix changes none of the parent's files") and v2 == ("counts", s["rework"])
          and v3[0].startswith("its fix landed at or before"),
          "a rework counts only if its fix is later and changes a parent file: %s / %s / %s" % (v1[0], v2[0], v3[0]))
    # pins: refs/arena/old/<sha> in a scratch copy of the old-history repo; idempotent; a missing sha reported
    pin = tmp / "pin.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(old), str(pin)], check=True, capture_output=True, timeout=60)
    a = A.pin_old([s["remap_old"], "f" * 40], old=pin)
    b = A.pin_old([s["remap_old"]], old=pin)
    refs = git(pin, "for-each-ref", "--format=%(refname) %(objectname)", A.PIN_PREFIX)
    check(a["pinned"] == 1 and a["missing"] == ["f" * 40] and b == dict(b, pinned=0, already=1)
          and refs == A.PIN_PREFIX + s["remap_old"] + " " + s["remap_old"],
          "pin_old pins once, reports a missing sha, never repins: %s %s" % (a, b))


def _registered(tmp, name, pool, post=False, item="FIXTURE_GOOD_FIX_ONE"):
    p = fresh_arena(tmp, name)
    A.write_pool(pool, p)
    good = {t["source_item"]: t for t, _ in pool}[item]
    c = A.build_arm_clone(good["base_sha"], Path(os.environ["ARENA_CLONES"]) / "arm", src=tmp / "repo",
                          task=good["id"], p=p)
    if post:
        p["events"].mkdir(parents=True, exist_ok=True)
        (p["events"] / "harness.jsonl").write_text(json.dumps({"event": "assign", "task": good["id"]}) + "\n")
    return p, Path(c), good


def t_whitelist(tmp, pool, s):
    """Each leak route tester 2 found, planted in a REGISTERED clone; the check must see every one."""
    body = git(tmp / "repo", "show", "%s:%s" % (s["esc"], NEWT)) + "\n"
    import gzip
    tag_env = ["-c", "user.name=a", "-c", "user.email=a@a"]

    def bare_in(c, cl):
        subprocess.run(["git", "clone", "-q", "--bare", str(tmp / "repo"), str(c / "stuff.git")], check=True,
                       capture_output=True, timeout=60)

    def bare_root(c, cl):
        subprocess.run(["git", "clone", "-q", "--bare", str(tmp / "repo"), str(cl / "cache.git")], check=True,
                       capture_output=True, timeout=60)

    def commit_msg(c, cl):
        tree = git(c, "rev-parse", "HEAD^{tree}")
        cm = git(c, *tag_env, "commit-tree", tree, "-p", "HEAD", "-m", body)
        git(c, "update-ref", "refs/heads/notes", cm)

    def tag_msg(c, cl):
        git(c, *tag_env, "tag", "-a", "t1", "-m", body)

    def pack_txt(c, cl):
        (c / ".git/objects/pack" / ("pack-" + "ab" * 20 + ".txt")).write_text(body)

    def fake_loose(c, cl):
        (c / ".git/objects/ab").mkdir(parents=True, exist_ok=True)
        (c / ".git/objects/ab" / ("cd" * 19)).write_text(body)

    def gz(c, cl):
        (c / "n.gz").write_bytes(gzip.compress(body.encode()))

    def name(c, cl):
        (c / NEWT.replace("/", "_")).write_text("x")

    def tasks_json(c, cl):
        (c / "tasks").mkdir()
        (c / "tasks" / "x.json").write_text('{"base_sha": "%s"}\n' % s["esc"])

    def forged_fetch(c, cl):
        git(c, "fetch", "-q", "--depth", "1", "--no-tags", "file://" + str(tmp / "repo"), s["esc"])
        git(c, "checkout", "-q", "--detach", s["esc"])
        (c / ".git" / "FETCH_HEAD").unlink()
        (c / ".git" / "arena_clone.json").write_text(json.dumps({"task": None, "base_sha": s["esc"]}))

    routes = [("bare repo in the clone", bare_in, True), ("bare repo at the clone root", bare_root, True),
              ("commit message", commit_msg, True), ("annotated tag message", tag_msg, True),
              ("text file named like a pack", pack_txt, True), ("fake loose object", fake_loose, True),
              ("gzip copy", gz, False), ("path in a file name", name, False),
              ("tasks/x.json inside a clone", tasks_json, True), ("forged fetch of a later commit", forged_fetch, True)]
    for i, (what, plant, after) in enumerate(routes):
        for post in ((False, True) if after else (False,)):
            p, c, good = _registered(tmp, "wl%d%s" % (i, "post" if post else "pre"), pool, post)
            before = A.find_leaks(p)
            plant(c, Path(os.environ["ARENA_CLONES"]))
            got = A.find_leaks(p)
            check(before == [] and bool(got), "whitelist (%s): %s caught: %s"
                  % ("handed over" if post else "before hand-over", what, (got or ["NOT CAUGHT"])[0][:110]))
    # scoping (FP2): the arm's own notes naming its own test path, after hand-over, are its work
    # ESC's hidden check ADDS a test file (a path literal); alone in its pool (its base holds GOOD's fix objects)
    esc_only = [x for x in pool if x[0]["source_item"] == "FIXTURE_ESC_FIX_TWO"]
    p, c, good = _registered(tmp, "fp2post", esc_only, post=True, item="FIXTURE_ESC_FIX_TWO")
    gh = json.loads((p["judge"] / (good["id"] + ".json")).read_text())
    paths_ = sorted(A._path_lits(gh))
    (c / "SUMMARY.md").write_text("I changed " + " and ".join(paths_) + "\n")
    check(bool(paths_) and A.find_leaks(p) == [], "after hand-over an arm naming its own test paths is not a leak "
          "(%s)" % paths_)
    p, c, good = _registered(tmp, "fp2pre", pool, post=False)
    paths_ = sorted(A._path_lits(json.loads((p["judge"] / (good["id"] + ".json")).read_text()))) or [TEST]
    (c / "SUMMARY.md").write_text("I changed " + " and ".join(paths_) + "\n")
    other = [t["id"] for t, _ in pool if t["id"] != good["id"]]
    mine = A.find_leaks(p, good["id"])
    check(bool(mine) and mine[0].startswith("[%s]" % good["id"]) and all(A.find_leaks(p, o) == [] for o in other),
          "before hand-over a stray file is scoped to its clone's task only: %s" % (mine or ["NONE"])[0][:80])
    r = A.freeze(p, now="2026-11-10T00:00:00Z")
    fz = A.frozen_hashes(p)
    check(good["id"] in r["withheld"] and good["id"] not in fz and set(other) <= set(fz),
          "freeze withholds the task with a scoped leak and freezes the rest: %s" % sorted(r["withheld"]))


def t_freeze_round2(tmp, pool):
    """Symlinked task file refused; assign records under other names seen; TOCTOU re-read; refreeze procedure."""
    p = fresh_arena(tmp, "fz_link")
    A.write_pool(pool, p)
    tid = "RP_FIXTURE_GOOD_FIX_ONE"
    tf = p["tasks"] / (tid + ".json")
    elsewhere = Path(os.environ["ARENA_CLONES"]).parent / "fz_link_copy.json"
    elsewhere.write_bytes(tf.read_bytes())
    tf.unlink()
    os.symlink(elsewhere, tf)
    e = raises(A.TaskRefused, A.freeze, p, now="2026-11-10T00:00:00Z")
    check(bool(e) and A.frozen_hashes(p) == {}, "a symlinked task file is refused: %s" % (e or "NOT REFUSED")[:70])
    variants = [("assign.json", {"event": "assign", "task": tid}), ("sub/x.jsonl", {"event": "assign", "task": tid}),
                ("harness.jsonl", {"event": "Assign", "task": tid}), ("harness.jsonl", {"type": "assign", "task": tid}),
                ("harness.jsonl", {"action": "ASSIGN ", "task": tid})]
    for i, (rel, rec) in enumerate(variants):
        p = fresh_arena(tmp, "fz_as%d" % i)
        A.write_pool(pool, p)
        (p["events"] / rel).parent.mkdir(parents=True, exist_ok=True)
        (p["events"] / rel).write_text(json.dumps(rec) + "\n")
        e = raises(A.TaskRefused, A.freeze, p, now="2026-11-10T00:00:00Z")
        check(bool(e) and A.frozen_hashes(p) == {}, "an assign as events/%s %s refuses the freeze: %s"
              % (rel, rec, (e or "NOT REFUSED")[:50]))
    # TOCTOU: a task swapped while the leak scan runs
    p = fresh_arena(tmp, "fz_toctou")
    A.write_pool(pool, p)
    tf = p["tasks"] / (tid + ".json")
    real = A.scoped_leaks

    def swapping(p_):
        out = real(p_)
        t = json.loads(tf.read_text())
        tf.write_bytes(A._dump(dict(t, prompt=t["prompt"] + " (swapped)")))
        return out
    A.scoped_leaks = swapping
    try:
        e = raises(A.TaskRefused, A.freeze, p, now="2026-11-10T00:00:00Z")
    finally:
        A.scoped_leaks = real
    check(bool(e) and "while the leak scan ran" in e and A.frozen_hashes(p) == {},
          "a task file swapped during the scan refuses the whole freeze: %s" % (e or "NOT REFUSED")[:60])
    # refreeze: the appended, reasoned recovery
    p = fresh_arena(tmp, "fz_refreeze")
    A.write_pool(pool, p)
    A.freeze(p, now="2026-11-10T00:00:00Z")
    tf = p["tasks"] / (tid + ".json")
    old_h = A.frozen_hashes(p)[tid]["sha256"]
    t = json.loads(tf.read_text())
    tf.write_bytes(A._dump(dict(t, prompt=t["prompt"] + " (re-census)")))
    e = raises(A.TaskRefused, A.freeze, p, now="2026-11-10T00:00:01Z")
    check(bool(e) and "refreeze" in e, "a changed frozen task is refused and the refusal names the recovery")
    check(bool(raises(A.TaskRefused, A.refreeze, p, tid, "  ", now="2026-11-10T00:00:02Z")),
          "refreeze without a reason is refused")
    check(bool(raises(A.TaskRefused, A.load_frozen, tid, p)), "before the refreeze, load_frozen refuses the edit")
    before = p["freeze"].read_bytes()
    r = A.refreeze(p, tid, "re-census after the pool ruling", now="2026-11-10T00:00:03Z")
    after = p["freeze"].read_bytes()
    check(r["replaces"] == old_h and after.startswith(before) and b'"refreeze"' in after[len(before):],
          "refreeze appends (old freeze kept) a record naming the replaced hash and the reason")
    check(A.load_frozen(tid, p)["id"] == tid and A.check(p) == [], "after the refreeze the task loads and check is "
          "clean")
    check(bool(raises(A.TaskRefused, A.refreeze, p, tid, "again", now="2026-11-10T00:00:04Z")),
          "refreezing an unchanged task is refused")
    tf.write_bytes(A._dump(dict(t, prompt=t["prompt"] + " (third)")))
    A._append(p, [{"ts": "2026-11-10T00:00:05Z", "arm": "ralph_a", "task": tid, "event": "assign"}])
    e = raises(A.TaskRefused, A.refreeze, p, tid, "late", now="2026-11-10T00:00:06Z")
    check(bool(e) and "assign" in e, "no refreeze after an assignment")


def t_real_ledger():
    check(A.arena_root().name == "arena" and A.paths()["judge"].parent.name == "judge",
          "with ARENA_ROOT unset the root comes from rmpaths/agent_storage: %s" % A.arena_root())
    pool, rep = A.census(sanity=A.SANITY_ITEM)        # raises SanityFail if blind
    check(rep["sanity"]["found"], "real ledger: sanity item %s found (pool %d: %s)"
          % (A.SANITY_ITEM, rep["pool"], rep["labels"]))
    check(rep["pool"] > 0 and all(t["live"] in A.LIVE_OK for t, _ in pool), "real ledger: no task has live: full")
    h = {t["source_item"]: hh for t, hh in pool}[A.SANITY_ITEM]
    check(h["fix_sha"].startswith("310ad7f953") and h["label"] == "Clean",
          "real ledger: the sanity item remaps to 310ad7f953 and is Clean (hand-checked)")


def main():
    tmp = Path(tempfile.mkdtemp(prefix="arena_tasks_st_"))
    saved = {k: os.environ.get(k) for k in ("ARENA_ROOT", "ARENA_CLONES")}
    try:
        repo, old, s = build_repos(tmp)
        pool = t_census(tmp, repo, old, s)
        t_hash(tmp, pool)
        t_live(tmp, pool)
        t_hidden(tmp, pool, s)
        t_census2(tmp, repo, old, s)
        t_census3(tmp, repo, old, s)
        t_match()
        t_clone(tmp, pool, s)
        t_links(tmp, pool)
        t_auth(tmp, pool)
        t_auth2(tmp, pool)
        t_lock(tmp, pool)
        t_order(tmp, pool)
        t_pool_ruling(tmp, repo, old, s)
        t_whitelist(tmp, pool, s)
        t_freeze_round2(tmp, pool)
        for k, v in saved.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        t_real_ledger()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
