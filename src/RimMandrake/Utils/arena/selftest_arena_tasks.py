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
    s["rework"] = commit(repo, {RWT: "from tool import f\nassert f() != 0  # the rework's own pin, hidden too\n"},
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
    check(set(got) == {"FIXTURE_GOOD_FIX_ONE", "FIXTURE_ESC_FIX_TWO", "FIXTURE_REMAP_FIX_FIVE"},
          "census keeps exactly good, escaped, remapped (got %s)" % sorted(got))
    check(rep["sanity"]["found"] and rep["pool"] == 3, "report: pool 3 with the sanity item found")
    check(rep["scanned_closed_in_window"] == 6, "the out-of-window close is not scanned (6 scanned)")
    check(rep["rejects"].get("no start before close") == 2, "the closes with no start (nostart, rework) are rejected (%s)" % rep["rejects"])
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
                     ("rejected item", dict(sanity="FIXTURE_NOSTART_FIX_FOUR"))):
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
    check(r["frozen_new"] == 3 and len(r["pool_sha256"]) == 64, "freeze hashes 3 tasks and a pool hash")
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
    check(w["unchanged_frozen"] == 3 and w["wrote"] == 0 and w["refused_frozen_changed"] == [],
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
    check(A.freeze(p, now="2026-10-28T00:00:00Z")["frozen_new"] == 3, "after every window ends the pool freezes")
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
    shutil.copytree(tmp / "repo", clones / "full")
    lk = A.find_leaks(p)
    check(any("git object" in x for x in lk) and any("marker" in x for x in lk),
          "a full-history copy is flagged (hidden objects present, no marker): %s" % lk[:1])
    gd = clones / "full" / ".git"
    (gd / A.MARKER).write_text(json.dumps({"task": tg["id"], "base_sha": tg["base_sha"],
                                           "source": str(tmp / "repo")}))
    git(clones / "full", "checkout", "-q", "--detach", tg["base_sha"])
    check(any("after base_sha" in x for x in A.find_leaks(p)), "a full clone checked out at base with a forged "
          "marker is still flagged for its later commits")
    shutil.rmtree(clones / "full")
    A.build_arm_clone(s["esc"], clones / "atfix", src=tmp / "repo", task=tg["id"])
    lk = A.find_leaks(p)
    check(any("marker base" in x for x in lk) and any(s["esc"][:12] in x for x in lk),
          "a clone at the fix sha is flagged (fix commit present, base mismatch): %s" % lk[:1])
    shutil.rmtree(clones / "atfix")
    subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", str(tmp / "repo"), str(clones / "shared")],
                   check=True, capture_output=True)
    check(any("alternates" in x for x in A.find_leaks(p)), "a --shared clone (alternates) is flagged")
    shutil.rmtree(clones / "shared")
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
        for k, v in saved.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        t_real_ledger()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
