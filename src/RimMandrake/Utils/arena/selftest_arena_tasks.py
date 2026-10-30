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
    # the old side's parent holds the same tool/test as the new side's (a rewrite keeps every non-excised file), so
    # the remap's own change is the same and its patch-id check (ARENA_RESOLVER_VERIFY_REMAP_BY_PATCH_ID) passes
    commit(old, {TOOL: "def f():\n    return 4\n",
                 TEST: "assert True  # nostart change to the test, long enough to count\n"},
           "old side catch-up", "2026-10-19T11:03:00+00:00")
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
    pool, rep = A.census(ledger(s), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old, vet=stub_vet)
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
    pc, rc = A.census(ledger(s, rework_in_pool=True), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old, vet=stub_vet)
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



def t_live_plan(tmp, pool):
    """TRIO_FROZEN_TASKS_WIRE_LIVE_PLAN: live_plan is a frozen, hashed task field. The census writes null for every
    (offline) replay task; a live task needs a plan testpilot.check_live_plan accepts; an offline task may not carry
    one; a task frozen before the field existed loads only if it is live: none (no silent proof fallback)."""
    check(all("live_plan" in t and t["live_plan"] is None and t["live"] == "none" for t, _ in pool),
          "census: every replay task carries live_plan null explicitly")
    plan = {"scenarios": [{"id": "s1", "argv": ["python3", "proof.py"], "footprint": {"files": ["a/*.xml"]},
                           "taints": ["s1"], "fail_rc": 1}], "fixture_save": "fx"}
    p = fresh_arena(tmp, "arena_live_plan")
    A.write_pool(pool, p)
    tf = p["tasks"] / "RP_FIXTURE_ESC_FIX_TWO.json"
    hp = p["judge"] / tf.name
    t0 = json.loads(tf.read_text())
    for why, t in (("no live_plan field", {k: v for k, v in dict(t0, live="minimal").items() if k != "live_plan"}),
                   ("live_plan null", dict(t0, live="minimal")),
                   ("does not read", dict(t0, live="minimal", live_plan=dict(plan, timeout=3))),
                   ("does not read", dict(t0, live="minimal",
                                          live_plan={"scenarios": [dict(plan["scenarios"][0], timeout_s=9)]})),
                   ("no scenarios", dict(t0, live="minimal", live_plan={"scenarios": []})),
                   ("argv", dict(t0, live="minimal", live_plan={"scenarios": [{"id": "s1", "argv": ["x", 3]}]})),
                   ("taints", dict(t0, live="minimal", live_plan={"scenarios": [{"id": "s1", "argv": ["x"],
                                                                                  "taints": ["s9"]}]})),
                   ("fail_rc", dict(t0, live="minimal", live_plan={"scenarios": [{"id": "s1", "argv": ["x"],
                                                                                   "fail_rc": 0}]})),
                   ("live: none task", dict(t0, live_plan=plan))):
        e = raises(A.TaskRefused, A.validate_task, t, hp, p)
        check(bool(e) and why in e, "validate_task refuses (%s): %s" % (why, (e or "NOT REFUSED")[:110]))
    check(raises(A.TaskRefused, A.validate_task, dict(t0, live="minimal", live_plan=plan), hp, p) is None,
          "validate_task accepts a live task with a valid plan")
    check(raises(A.TaskRefused, A.validate_task, dict(t0, live="minimal+deps", live_plan=plan), hp, p) is None,
          "validate_task accepts a minimal+deps task with a valid plan")
    tf.write_bytes(A._dump(dict(t0, live="minimal")))
    e = raises(A.TaskRefused, A.freeze, p)
    check(bool(e) and "live_plan" in e and A.frozen_hashes(p) == {}, "freeze refuses a live task with live_plan "
          "null and freezes nothing")
    tf.write_bytes(A._dump(dict(t0, live="minimal", live_plan=plan)))
    old = p["tasks"] / "RP_FIXTURE_GOOD_FIX_ONE.json"          # an offline task frozen before the field existed
    old.write_bytes(A._dump({k: v for k, v in json.loads(old.read_text()).items() if k != "live_plan"}))
    A.freeze(p)
    check(A.check(p) == [], "a live task with a valid plan and an old offline task without the key both freeze")
    got = A.load_frozen("RP_FIXTURE_ESC_FIX_TWO", p)
    check(got["live_plan"] == plan, "load_frozen returns the frozen plan verbatim")
    check("live_plan" not in A.load_frozen("RP_FIXTURE_GOOD_FIX_ONE", p),
          "an old live: none task without live_plan still loads (it is never published)")
    tf.write_bytes(A._dump(dict(t0, live="minimal", live_plan=dict(plan, fixture_save="other"))))
    probs = A.check(p)
    check(any("RP_FIXTURE_ESC_FIX_TWO" in x and "hash" in x for x in probs),
          "editing a frozen live_plan changes the hash and is refused")
    check(bool(raises(A.TaskRefused, A.load_frozen, "RP_FIXTURE_ESC_FIX_TWO", p)), "load_frozen refuses it too")

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
    pool, rep = A.census(ledger(s, children=True), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old, vet=stub_vet)
    h = {t["source_item"]: hh for t, hh in pool}["FIXTURE_GOOD_FIX_ONE"]
    v = {c["item"]: c["verdict"] for c in h.get("rework_candidates", [])}
    check(h["label"] == "Clean" and v.get("FIXTURE_GOOD_DESIGN_KID", "").startswith("not a fix")
          and "review" in v.get("FIXTURE_GOOD_REVIEW_KID", ""),
          "a design child and a closed 'Review ...' child do not make the fix Escaped (%s, %s)" % (h["label"], v))
    pool, rep = A.census(ledger(s, open_bug=True), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old, vet=stub_vet)
    h = {t["source_item"]: hh for t, hh in pool}["FIXTURE_GOOD_FIX_ONE"]
    check(h["label"] == "Clean" and h.get("label_pending") == ["FIXTURE_GOOD_BUG_KID"],
          "an open bug child leaves Clean provisional (label_pending %s)" % h.get("label_pending"))
    p = fresh_arena(tmp, "arena_prov")
    A.write_pool(pool, p)
    e = raises(A.TaskRefused, A.freeze, p, now="2026-11-10T00:00:00Z")
    check(bool(e) and "provisional" in e and A.frozen_hashes(p) == {},
          "freeze refuses a Clean label with an open fix-type rework: %s" % (e or "NOT REFUSED")[:70])
    pool, _ = A.census(ledger(s), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old, vet=stub_vet)
    p = fresh_arena(tmp, "arena_early")
    A.write_pool(pool, p)
    e = raises(A.TaskRefused, A.freeze, p, now="2026-10-20T00:00:00Z")
    check(bool(e) and "window ends 2026-10-21" in e, "freeze refuses a Clean label before its 7-day rework window "
          "ends: %s" % (e or "NOT REFUSED")[:70])
    check(A.freeze(p, now="2026-10-28T00:00:00Z")["frozen_new"] == 4, "after every window ends the pool freezes")
    _, rep = A.census(ledger(s, late_close=True), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old, vet=stub_vet)
    check(rep["scanned_closed_in_window"] == 6 and rep["rejects"].get("last close falls outside the window") == 1,
          "an item whose last close is outside the window is scanned and rejected with a reason (%s)" % rep["rejects"])


def t_census3(tmp, repo, old, s):
    """(h) a deleted test; (6) a self-leaking task."""
    real = A._prose_at

    def leaky(repo_, sha, iid):
        return ("## spec\nsee " + NEWT + "\n") if iid == "FIXTURE_ESC_FIX_TWO" else real(repo_, sha, iid)
    A._prose_at = leaky
    try:
        pool2, rep2 = A.census(ledger(s), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old, vet=stub_vet)
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
    pool2, _ = A.census(E, repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old, vet=stub_vet)
    lab = {t["source_item"]: h["label"] for t, h in pool2}
    check(lab.get("FIXTURE_ESC_FIX_TWO") == "Escaped", "a grandchild rework (via a review child) counts: %s" % lab)
    # a child filed 10 s BEFORE the parent's close (the close and the finding raced) still counts
    E = ledger(s)
    _ev_of(E, "FIXTURE_ESC_REWORK_THREE")["ts"] = "2026-10-16T10:03:50Z"
    pool3, _ = A.census(E, repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old, vet=stub_vet)
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


def t_round3(tmp, repo, old, s, pool):
    """Round 3: archive decodings after assignment; prompt provenance + hints flag."""
    import bz2, gzip, io, lzma, zipfile, zlib
    body = git(tmp / "repo", "show", "%s:%s" % (s["esc"], NEWT)) + "\n"
    b = body.encode()
    b64 = base64.b64encode(b)
    zb = io.BytesIO()
    with zipfile.ZipFile(zb, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("inner/notes.txt", body)
    plants = [("notes.gz", gzip.compress(b)), ("notes.bz2", bz2.compress(b)), ("notes.xz", lzma.compress(b)),
              ("notes.zip", zb.getvalue()), ("notes.z", zlib.compress(b)),
              ("notes.b64.gz", gzip.compress(b64)), ("notes.gz.b64", base64.b64encode(gzip.compress(b)))]
    m = A.Matcher([{"task": "RP_X", "fix_sha": "0" * 40, "reworks": [],
                    "checks": [{"path": "src/a/selftest_x.py", "added": True, "body": body, "novel": [body]}]}])
    for name, raw in plants:
        check(bool(m.hits(raw)), "matcher reads the %s container" % name)
    check(not m.hits(gzip.compress(b"def other():\n    return 1\n" * 50)), "a gzip of unrelated text stays quiet")
    bomb = gzip.compress(b"\0" * (64 * 1024 * 1024))
    mx = max(len(t) for t in A._decodings(bomb))
    check(mx <= A._UNPACK_CAP + 16, "a decompression bomb is capped (%d chars)" % mx)
    for i, (name, raw) in enumerate(plants):
        p, c, good = _registered(tmp, "r3%d" % i, pool, True)
        before = A.find_leaks(p)
        (c / name).write_bytes(raw)
        got = A.find_leaks(p)
        check(before == [] and bool(got), "after hand-over a hidden body in %s is caught: %s"
              % (name, (got or ["NOT CAUGHT"])[0][:90]))
    pool2, _ = A.census(ledger(s), repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old, vet=stub_vet)
    check(all(t["prompt_source"] == "base_parent" and isinstance(t["prompt_may_hold_hints"], bool) for t, _ in pool2),
          "every census task records prompt_source base_parent and a boolean hints flag")
    # hints: prose gains a line after the claim
    r = tmp / "hintrepo"
    r.mkdir()
    rel = "infrastructure/state/items/HINT_ITEM.md"
    git(r, "init", "-q")
    for d, text, ts in (("a", "# item\nplain ask\n", "2026-10-01T10:00:00"),
                        ("b", "# item\nplain ask\nHINT: use approach X\n", "2026-10-03T10:00:00")):
        (r / rel).parent.mkdir(parents=True, exist_ok=True)
        (r / rel).write_text(text)
        git(r, "add", rel)
        env = dict(os.environ, GIT_AUTHOR_DATE=ts + "Z", GIT_COMMITTER_DATE=ts + "Z")
        subprocess.run(["git", "-C", str(r), "-c", "user.name=a", "-c", "user.email=a@a", "commit", "-q", "-m", d],
                       check=True, env=env, capture_output=True, timeout=60)
    head = git(r, "rev-parse", "HEAD").strip()
    prose = A._prose_at(r, head, "HINT_ITEM")
    check(A._prompt_hints(r, head, "HINT_ITEM", "2026-10-02T00:00:00Z", prose) is True,
          "prose that gained a line after the claim is flagged prompt_may_hold_hints")
    check(A._prompt_hints(r, head, "HINT_ITEM", "2026-10-04T00:00:00Z", prose) is False,
          "unchanged since the claim: not flagged")
    check(A._prompt_hints(r, head, "HINT_ITEM", None, prose) is False, "no start event: not flagged")


def t_multi_old(tmp, repo, old, s):
    """POOL DIAG 2026-10-30: 107 of 123 'resolves nowhere' close shas live in a SECOND pre-rewrite git dir (the
    retired local clones under retired-trees/), not in the mirror. The old history is a LIST of repos: a sha found
    only in the second one remaps, and is pinned there, not in the first."""
    old2 = tmp / "old2"
    subprocess.run(["git", "clone", "-q", str(old), str(old2)], check=True, capture_output=True, timeout=60)
    s2 = {"new": commit(repo, {TOOL: "def f():\n    return 8\n",
                               TEST: "assert True  # second-old fix, rewritten side, long enough\n"},
                        "fix second old", "2026-10-22T10:03:00+00:00"),
          "old": commit(old2, {TOOL: "def f():\n    return 8\n", "work/only_in_old2.bin": "z" * 50,
                               TEST: "assert True  # second-old fix, rewritten side, long enough\n"},
                        "fix second old", "2026-10-22T10:03:00+00:00")}
    E = ledger(s)
    for k in (dict(event="file", id="FIXTURE_OLD2_FIX_EIGHT", title="t", kind="task", needs="offline",
                   ts="2026-10-22T10:00:00Z", **{"for": "FOUNDRY"}),
              dict(event="close", id="FIXTURE_OLD2_FIX_EIGHT", sha=s2["old"][:10], reason="r",
                   ts="2026-10-22T10:04:00Z")):
        E.append(dict(k, seat="FOUNDRY", tsn="o2" + k["event"]))
    _, r1 = A.census(E, repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=old, vet=stub_vet)
    check(r1["rejects"].get("close sha resolves nowhere") == 1,
          "forced: with only the first old-history repo the second-old sha resolves nowhere (%s)" % r1["rejects"])
    for form in ([old, old2], os.pathsep.join([str(old), str(old2)])):
        p2, r2 = A.census(E, repo=repo, sanity="FIXTURE_GOOD_FIX_ONE", old_history=form, vet=stub_vet)
        h = {t["source_item"]: hh for t, hh in p2}.get("FIXTURE_OLD2_FIX_EIGHT")
        check(bool(h) and h["fix_sha"] == s2["new"] and h["sha_resolution"] == "remapped"
              and r2["old_history_pins"].get(str(old2)) == [s2["old"]],
              "old history as %s: a sha only in the second repo remaps and is attributed to it"
              % type(form).__name__)
    pins = A.pin_old(r2["old_history_pins"])
    check(pins["pinned"] == sum(len(v) for v in r2["old_history_pins"].values()) and not pins["missing"]
          and git(old2, "for-each-ref", "--format=%(objectname)", A.PIN_PREFIX).split() == [s2["old"]]
          and s["remap_old"] in git(old, "for-each-ref", "--format=%(objectname)", A.PIN_PREFIX).split(),
          "pin_old pins each sha in the repo that resolved it: %s" % pins)
    ret = tmp / "retired"
    for n in ("bench-git-1", "foundry-git-2", "notes"):
        (ret / n).mkdir(parents=True)
    got = A.old_history_repos(os.pathsep.join([str(old), str(ret / "*-git-*"), str(tmp / "absent.git")]))
    check(got == [old, ret / "bench-git-1", ret / "foundry-git-2"],
          "old_history_repos expands globs, keeps order, drops absent paths: %s" % got)
    check(any("retired-trees" in g for g in A.OLD_HISTORY_DEFAULT),
          "the default old history includes the retired pre-rewrite clones: %s" % (A.OLD_HISTORY_DEFAULT,))


CS = "src/RimMandrake/ModX/Source/X.cs"
DX = "src/RimMandrake/ModX/Defs/X.xml"


def t_review_2026_10_30(tmp):
    """REVIEW 2026-10-30 (BENCH, of 67094dc0f6). Its own repo, so the main fixture's counts do not move.
    - CONDUCTOR DECISION (owner authority, CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM): a replay task must carry at
      least one objective check beyond "the build succeeds"; build-only tasks are excluded. A C#-only or XML-only
      fix (proof = winbuild / validate_patch alone, no fix selftest) is rejected; C# WITH a fix selftest stays.
    - a "current" sha HEAD cannot reach (a dangling object in the store) is not current history;
    - a verify pass from an EARLIER close cycle does not make the final close Clean;
    - a rework on a divergent branch (not a descendant of the parent's fix) is not an escape;
    - pin_old does not count a pin that points at a different commit as already pinned."""
    repo, empty = tmp / "rv_repo", tmp / "rv_empty_old"
    for r in (repo, empty):
        r.mkdir()
        git(r, "init", "-q", "-b", "main")
    base = commit(repo, {TOOL: "def f():\n    return 1\n", TEST: "assert True  # rv base body of the selftest\n",
                         CS: "class X { int v = 1; }\n",
                         DX: "<Defs><ThingDef><defName>RM_X</defName></ThingDef></Defs>\n"},
                  "rv base", "2026-10-13T09:00:00+00:00")
    s = {"sane": commit(repo, {TOOL: "def f():\n    return 2\n",
                               TEST: "from tool import f\nassert f() == 2  # rv sanity fix pins f, long line\n"},
                        "rv fix sane", "2026-10-14T10:03:00+00:00"),
         "cs": commit(repo, {CS: "class X { int v = 2; }\n"}, "rv fix cs only", "2026-10-15T10:03:00+00:00"),
         "xml": commit(repo, {DX: "<Defs><ThingDef><defName>RM_X</defName><label>x</label></ThingDef></Defs>\n"},
                       "rv fix xml only", "2026-10-15T11:03:00+00:00"),
         "cs_t": commit(repo, {CS: "class X { int v = 3; }\n",
                               TEST: "from tool import f\nassert f() == 2  # rv csharp fix with a selftest too\n"},
                        "rv fix cs with test", "2026-10-16T10:03:00+00:00")}
    stale1 = commit(repo, {TOOL: "def f():\n    return 6\n",
                           TEST: "from tool import f\nassert f() == 6  # rv stale first cycle, long line\n"},
                    "rv stale first", "2026-10-17T10:03:00+00:00")
    stale2 = commit(repo, {TOOL: "def f():\n    return 7\n",
                           TEST: "from tool import f\nassert f() == 7  # rv stale second cycle, long line\n"},
                    "rv stale second", "2026-10-18T10:03:00+00:00")
    # a divergent rework: on a side branch off cs_t's parent, then joined with `merge -s ours` (reachable from
    # HEAD, never a descendant of cs_t); it changes cs_t's file X.cs
    git(repo, "checkout", "-q", "-b", "side", s["cs"])
    side = commit(repo, {CS: "class X { int v = 9; }\n", RWT: "assert 1  # rv side rework pin, long enough line\n"},
                  "rv side rework", "2026-10-19T10:03:00+00:00")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "-s", "ours", "-m", "rv join side", "side", date="2026-10-19T12:00:00+00:00")
    # a dangling commit: in the object store, on no ref, unreachable from HEAD
    dangling = git(repo, "commit-tree", git(repo, "rev-parse", "HEAD^{tree}"), "-p", base, "-m", "rv dangling",
                   date="2026-10-20T10:03:00+00:00")
    E, n = [], [0]

    def ev(**k):
        n[0] += 1
        k.setdefault("seat", "FOUNDRY")
        if k["event"] == "file":
            k.setdefault("for", "FOUNDRY")
        k["tsn"] = "rv%d" % n[0]
        E.append(k)

    def item(iid, day, sha, verify=True, **kw):
        ev(event="file", id=iid, title="title of " + iid, kind=kw.get("kind", "task"), needs="offline",
           ts=day + "T10:00:00Z", **({"caused_by": kw["caused_by"]} if kw.get("caused_by") else {}))
        if verify:
            ev(event="verify", id=iid, result="pass", config="c", evidence="e", sha=sha[:10], ts=day + "T10:03:30Z")
        ev(event="close", id=iid, sha=sha[:10], reason="r", ts=day + "T10:04:00Z")

    item("RV_SANE_FIX_ONE", "2026-10-14", s["sane"])
    item("RV_CSONLY_FIX_TWO", "2026-10-15", s["cs"])
    item("RV_XMLONLY_FIX_THREE", "2026-10-15", s["xml"])
    item("RV_CSTEST_FIX_FOUR", "2026-10-16", s["cs_t"])
    item("RV_STALE_FIX_FIVE", "2026-10-17", stale1)                     # verified + closed on the first cycle ...
    ev(event="close", id="RV_STALE_FIX_FIVE", sha=stale2[:10], reason="again", ts="2026-10-18T10:04:00Z")
    item("RV_SIDE_REWORK_SIX", "2026-10-19", side, verify=False, kind="bug", caused_by="RV_CSTEST_FIX_FOUR")
    item("RV_DANGLING_FIX_SEVEN", "2026-10-20", dangling)
    pool, rep = A.census(E, repo=repo, sanity="RV_SANE_FIX_ONE", old_history=[empty], vet=stub_vet)
    got = {t["source_item"]: (t, h) for t, h in pool}
    bo = [k for k in rep["rejects"] if k.startswith("build-only")]
    check("RV_CSONLY_FIX_TWO" not in got and "RV_XMLONLY_FIX_THREE" not in got and bo
          and rep["rejects"][bo[0]] >= 2,
          "decision: a C#-only and an XML-only fix (build/validate proof alone) are rejected as build-only (%s)"
          % rep["rejects"])
    check("RV_CSTEST_FIX_FOUR" in got and got["RV_CSTEST_FIX_FOUR"][0]["kind"] == "csharp"
          and any(c["type"] == "fix_test" for c in got["RV_CSTEST_FIX_FOUR"][1]["checks"]),
          "decision: a C# fix that also changes a selftest stays in the pool (%s)" % sorted(got))
    check("RV_DANGLING_FIX_SEVEN" not in got,
          "a close sha that is only a dangling object (unreachable from HEAD) is not current history (%s)"
          % (got.get("RV_DANGLING_FIX_SEVEN", (None, {}))[1].get("sha_resolution"),))
    st = got.get("RV_STALE_FIX_FIVE")
    check(st is not None and st[1]["fix_sha"] == stale2 and st[1]["label"] is None,
          "a verify pass from an earlier close cycle does not label the final close Clean (%s)"
          % (st and st[1]["label"],))
    c4 = got.get("RV_CSTEST_FIX_FOUR", (None, {}))[1]
    check(c4.get("label") == "Clean" and not c4.get("reworks"),
          "a rework on a divergent branch (not a descendant of the parent's fix) is not an escape (%s)"
          % [r.get("verdict") for r in c4.get("rework_candidates", [])])
    # pin_old: a pin ref that already exists but points elsewhere is a conflict, not "already"
    git(repo, "update-ref", A.PIN_PREFIX + s["xml"], s["cs"])
    out = A.pin_old([s["xml"], s["sane"]], old=[repo])
    check(out.get("already") == 0 and out.get("pinned") == 1 and out.get("conflict") == [s["xml"]]
          and git(repo, "rev-parse", A.PIN_PREFIX + s["xml"]) == s["cs"],
          "pin_old reports a pin pointing at another commit as a conflict and leaves it (%s)" % out)


OTHER = "src/RimMandrake/Utils/other.py"
NEW2 = "src/RimMandrake/Utils/selftest_vt_added.py"
SLOW = "src/RimMandrake/Utils/selftest_vt_slow.py"


def stub_vet(base, fix, path, body):
    """Fixture pools: every hidden check discriminates (the vet itself is proven in t_vet_siblings)."""
    return {"base_rc": 1, "fix_rc": 0, "fix_result": "pass", "base_result": "fail"}


def t_vet_siblings(tmp):
    """FOUNDRY 2026-10-30, four BENCH review findings of 67094dc0f6. Its own repos, so the main fixture's counts
    do not move.
    - ARENA_TASKS_VET_CHECK_FAILS_AT_BASE: a fix_test must FAIL at base (its hidden body overlaid, alone, like the
      judge's run_hidden) and PASS at the fix, measured by the judge's own materialise + run_hidden. A check that passes
      at base, fails at the fix or times out is unscored; a task left with none is rejected; a never-vetted check
      rejects its task (fail closed) and freeze refuses any scored fix_test without a passing vet record.
    - ARENA_POOL_HARDEN_SIBLING_FIX_IN_BASE: the report lists, per task, the pool tasks whose fix is in its base;
      schedule_conflicts refuses an order that judges such a task before (or with) the one its base contains.
    - ARENA_TASKS_FIX_CRITERIA_FROM_LATER_LEDGER: criteria never come from the ledger manifest (written by the
      `implemented` event, i.e. after the fix): prose at base, else the title.
    - ARENA_RESOLVER_VERIFY_REMAP_BY_PATCH_ID: a triple remap whose content differs is rejected."""
    repo, old = tmp / "vt_repo", tmp / "vt_old"
    for r in (repo, old):
        r.mkdir()
        git(r, "init", "-q", "-b", "main")
    base_files = {TOOL: "def f():\n    return 1\n", TEST: "assert True  # vt base body of the selftest\n",
                  OTHER: "X = 1\n",
                  "infrastructure/state/items/VT_DISC_FIX_ONE.md": "# VT_DISC_FIX_ONE\n\n## spec\nmake f 2\n",
                  "infrastructure/state/items/VT_MIXED_FIX_THREE.md":
                      "# VT_MIXED_FIX_THREE\n\n## spec\npin f\n\n## criteria\nBASE CRITERIA: f is pinned by a test\n"}
    b0 = commit(repo, base_files, "vt base", "2026-10-13T09:00:00+00:00")
    commit(old, base_files, "vt base", "2026-10-13T09:00:00+00:00")
    disc_files = {TOOL: "def f():\n    return 2\n",
                  TEST: "from tool import f\nassert f() == 2  # vt discriminating fix pins f, long line\n"}
    s = {"disc": commit(repo, disc_files, "vt fix disc", "2026-10-14T10:03:00+00:00"),
         "nondisc": commit(repo, {TOOL: "def f():\n    return 3\n",
                                  TEST: "assert True  # vt comment-only change to the selftest, long line\n"},
                           "vt fix nondisc", "2026-10-15T10:03:00+00:00"),
         "mixed": commit(repo, {TOOL: "def f():\n    return 4\n",
                                TEST: "from tool import f\nassert f() == 4  # vt mixed fix pins f, long line\n",
                                NEW2: "assert True  # vt added test that passes anywhere, long line\n"},
                         "vt fix mixed", "2026-10-16T10:03:00+00:00"),
         "fixfail": commit(repo, {TOOL: "def f():\n    return 5\n",
                                  TEST: "from tool import f\nassert f() == 99  # vt fails even at its own fix\n"},
                           "vt fix fixfail", "2026-10-17T10:03:00+00:00"),
         "slow": commit(repo, {TOOL: "def f():\n    return 6\n",
                               SLOW: "import time\ntime.sleep(30)  # vt never finishes inside the vet timeout\n"},
                        "vt fix slow", "2026-10-18T10:03:00+00:00")}
    # one discriminating test and one the judge cannot finish: the whole task is out (fail closed)
    s["mixslow"] = commit(repo, {TOOL: "def f():\n    return 7\n",
                                 TEST: "from tool import f\nassert f() == 7  # vt mixslow fix pins f, long line\n",
                                 "src/RimMandrake/Utils/selftest_vt_hang.py":
                                     "import time\ntime.sleep(31)  # vt mixslow adds a test that hangs, long line\n"},
                          "vt fix mixslow", "2026-10-19T08:03:00+00:00")
    # old history: two pre-rewrite commits with the SAME triple as vt fix disc (date, author, subject) but other
    # content: one changes f differently, one also changes a path the rewritten commit leaves alone (not excised:
    # it exists in the rewritten trees). A third, with only an excised path extra, is the positive control.
    collide = commit(old, {TOOL: "def f():\n    return 22\n", TEST: disc_files[TEST]},
                     "vt fix disc", "2026-10-14T10:03:00+00:00")
    git(old, "checkout", "-q", "-b", "b2", git(old, "rev-parse", "HEAD^"))
    extra = commit(old, dict(disc_files, **{OTHER: "X = 2\n"}), "vt fix disc", "2026-10-14T10:03:00+00:00")
    git(old, "checkout", "-q", "-b", "b3", git(old, "rev-parse", "HEAD^"))
    excised = commit(old, dict(disc_files, **{"work/excised.bin": "z" * 40}), "vt fix disc",
                     "2026-10-14T10:03:00+00:00")
    R = A.Resolver(repo, [old])
    rc, why = R(collide)
    check(rc is None and "content differs" in why,
          "remap: same triple, different content -> rejected (%s, %s)" % (rc, why))
    rx, whyx = R(extra)
    check(rx is None and "content differs" in whyx,
          "remap: same triple, an extra non-excised path changed -> rejected (%s, %s)" % (rx, whyx))
    ro, whyo = R(excised)
    check(ro == s["disc"] and whyo == "remapped",
          "remap: same triple, only an excised path extra -> remapped (%s, %s)" % (ro, whyo))
    # binary content: patch-id does not see it, so the resulting blobs are compared
    brepo, bold = tmp / "vt_bin", tmp / "vt_bin_old"
    for r in (brepo, bold):
        r.mkdir()
        git(r, "init", "-q", "-b", "main")
        commit(r, {OTHER: "X = 1\n", **({"work/gone.txt": "excised\n"} if r == bold else {})}, "vt bin base",
               "2026-10-13T09:00:00+00:00")                  # trees differ (an excised file), so shas differ
    BIN = "src/RimMandrake/Utils/blob.dat"
    bnew = commit(brepo, {BIN: "\0bin\0same" * 8}, "vt bin fix", "2026-10-14T10:03:00+00:00")
    bsame = commit(bold, {BIN: "\0bin\0same" * 8}, "vt bin fix", "2026-10-14T10:03:00+00:00")
    git(bold, "checkout", "-q", "-b", "b2", git(bold, "rev-parse", "HEAD^"))
    bdiff = commit(bold, {BIN: "\0bin\0diff" * 8}, "vt bin fix", "2026-10-14T10:03:00+00:00")
    RB = A.Resolver(brepo, [bold])
    check(RB(bsame) == (bnew, "remapped"), "remap: same triple, same binary -> remapped (%s)" % (RB(bsame),))
    rb, whyb = RB(bdiff)
    check(rb is None and "binary" in whyb, "remap: same triple, a different binary -> rejected (%s, %s)" % (rb, whyb))

    # the change, not just its result: A->C vs B->C, deleting A vs deleting B, and a mode flip patch-id cannot see
    def pair(tag, new_base, old_base, new_fix, old_fix, chmod_old=False, chmod_new=False):
        nr, orr = tmp / ("vt_%s" % tag), tmp / ("vt_%s_old" % tag)
        out = []
        for r, b, f, x in ((nr, new_base, new_fix, chmod_new), (orr, old_base, old_fix, chmod_old)):
            r.mkdir()
            git(r, "init", "-q", "-b", "main")
            commit(r, dict(b, **({"work/gone.txt": "excised\n"} if r == orr else {})), "vt %s base" % tag,
                   "2026-10-13T09:00:00+00:00")
            for rel, body in f.items():
                if body is not None:
                    (r / rel).parent.mkdir(parents=True, exist_ok=True)
                    (r / rel).write_text(body)
                if x:
                    (r / rel).chmod(0o755)
            out.append(commit(r, f, "vt %s fix" % tag, "2026-10-14T10:03:00+00:00"))
        return A.Resolver(nr, [orr])(out[1]), out[0]

    BA, BB, BC = "\0bin\0A" * 8, "\0bin\0B" * 8, "\0bin\0C" * 8
    (rp, why), _ = pair("b2c", {BIN: BA}, {BIN: BB}, {BIN: BC}, {BIN: BC})
    check(rp is None and "binary" in why, "remap: A->C vs B->C (same result blob) -> rejected (%s, %s)" % (rp, why))
    (rp, why), _ = pair("bdel", {BIN: BA}, {BIN: BB}, {BIN: None}, {BIN: None})
    check(rp is None and "binary" in why, "remap: deleting different binaries -> rejected (%s, %s)" % (rp, why))
    (rp, why), want = pair("bdel_ok", {BIN: BA}, {BIN: BA}, {BIN: None}, {BIN: None})
    check(rp == want, "remap: deleting the same binary -> remapped (%s, %s)" % (rp, why))
    TX = "src/RimMandrake/Utils/run_me.py"
    (rp, why), _ = pair("mode", {TX: "a = 1\n"}, {TX: "a = 1\n"}, {TX: "a = 2\n"}, {TX: "a = 2\n"}, chmod_old=True)
    check(rp is None and "differs" in why, "remap: same text change, only the old side made it executable -> rejected "
          "(%s, %s)" % (rp, why))
    (rp, why), want = pair("mode_ok", {TX: "a = 1\n"}, {TX: "a = 1\n"}, {TX: "a = 2\n"}, {TX: "a = 2\n"},
                           chmod_old=True, chmod_new=True)
    check(rp == want, "remap: same text change and the same mode flip -> remapped (%s, %s)" % (rp, why))

    E, n = [], [0]

    def ev(**k):
        n[0] += 1
        k.setdefault("seat", "FOUNDRY")
        if k["event"] == "file":
            k.setdefault("for", "FOUNDRY")
        k["tsn"] = "vt%d" % n[0]
        E.append(k)

    def item(iid, day, sha, crit=None):
        ev(event="file", id=iid, title="title of " + iid, kind="task", needs="offline", ts=day + "T10:00:00Z")
        ev(event="verify", id=iid, result="pass", config="c", evidence="e", sha=sha[:10], ts=day + "T10:03:30Z")
        if crit:            # the implementer's manifest: written WITH the fix, so it can describe the answer
            ev(event="implemented", id=iid, sha=sha[:10], criteria=[{"id": "C1", "level": "L0", "text": crit}],
               ts=day + "T10:03:40Z")
        ev(event="close", id=iid, sha=sha[:10], reason="r", ts=day + "T10:04:00Z")

    item("VT_DISC_FIX_ONE", "2026-10-14", s["disc"], crit="LEAKED ANSWER: make f return 2")
    item("VT_NONDISC_FIX_TWO", "2026-10-15", s["nondisc"])
    item("VT_MIXED_FIX_THREE", "2026-10-16", s["mixed"], crit="LEAKED MIXED ANSWER: f returns 4")
    item("VT_FIXFAIL_FIX_FOUR", "2026-10-17", s["fixfail"])
    item("VT_SLOW_FIX_FIVE", "2026-10-18", s["slow"])
    item("VT_COLLIDE_FIX_SIX", "2026-10-19", collide)
    item("VT_MIXSLOW_FIX_SEVEN", "2026-10-19", s["mixslow"])
    w = A.model.replay(E).items["VT_DISC_FIX_ONE"]
    check(bool(w.criteria) and "LEAKED" in w.criteria[0]["text"],
          "instrument: the fixture's ledger manifest really holds the later criteria (%s)" % (w.criteria,))

    # census without a vet: candidates only, nothing scored is claimed
    p0, r0 = A.census(E, repo=repo, sanity="VT_DISC_FIX_ONE", old_history=[old])
    g0 = {t["source_item"]: (t, h) for t, h in p0}
    t1 = g0["VT_DISC_FIX_ONE"][0]
    check(t1["criteria"] == "title of VT_DISC_FIX_ONE" and "LEAKED" not in A._dump(t1).decode()
          and t1["criteria_source"].startswith("title"),
          "criteria: the ledger manifest (implemented, after the fix) never reaches the task (%s / %s)"
          % (t1["criteria"], t1["criteria_source"]))
    t3 = g0["VT_MIXED_FIX_THREE"][0]
    check("BASE CRITERIA" in t3["criteria"] and "LEAKED" not in A._dump(t3).decode()
          and t3["criteria_source"].startswith("prose"),
          "criteria: prose ## criteria at base wins over a later manifest (%s / %s)"
          % (t3["criteria"], t3["criteria_source"]))
    check("VT_COLLIDE_FIX_SIX" not in g0 and any("content differs" in k for k in r0["rejects"]),
          "census: a content-differing remap is rejected with its reason (%s)" % r0["rejects"])
    check(r0["vet"]["run"] is False and r0["vet"]["not_vetted"] == 0,
          "census without a vet says so in the report (%s)" % r0.get("vet"))

    # the vet itself: the judge's own route (materialise + run_hidden), fix side and base side (body overlaid alone)
    cache = tmp / "vt_vet_cache.jsonl"
    jobs = A.vet_jobs(p0)
    check(sum(len(j["checks"]) for j in jobs) == 8, "vet jobs: 8 fix_tests across the 6 candidate tasks (%s)"
          % [(j["task"], len(j["checks"])) for j in jobs])
    out = A.run_vet(jobs, repo, tmp / "vt_vetdir", cache, workers=2, timeout=3)
    check(out["ran"] == 8 and out["left"] == 0 and not out["errors"], "run_vet ran all 8 checks (%s)" % out)
    check(not (tmp / "vt_vetdir").exists() or not any((tmp / "vt_vetdir").iterdir()),
          "run_vet leaves no tree behind")
    recs = A.read_vet_cache(cache)
    by_path = {}
    for r in recs.values():
        by_path.setdefault((r["task"], r["path"]), r)
    d = by_path.get(("RP_VT_DISC_FIX_ONE", TEST), {})
    check(d.get("fix_result") == "pass" and d.get("base_result") == "fail" and d.get("fix_rc") == 0
          and d.get("base_rc") not in (0, None),
          "vet: the discriminating test passes at the fix and fails at base (%s)" % d)
    nd = by_path.get(("RP_VT_NONDISC_FIX_TWO", TEST), {})
    check(nd.get("fix_result") == "pass" and nd.get("base_result") == "pass",
          "vet: the comment-only test passes at base too (%s)" % nd)
    sl = by_path.get(("RP_VT_SLOW_FIX_FIVE", SLOW), {})
    check(sl.get("fix_result") == "error" and A.vet_verdict(sl) == (False, "timeout"),
          "vet: a hung test is recorded as a timeout, never a pass (%s)" % sl)
    # judge fidelity: rc 0 without the runner's nonce marker is no pass (plain python would call it one)
    fj = {"task": "RP_VT_FIDELITY", "base": b0, "fix": s["disc"], "area": A.area_for([TEST]),
          "checks": [{"path": TEST, "body": "import os\nos._exit(0)\n", "key": "vt-fid"}]}
    fr = A._vet_task(fj, repo, tmp / "vt_fid", 10)[0]
    check(fr["fix_result"] == "no_marker" and fr["fix_rc"] == 0 and A.vet_verdict(fr) == (False, "fails_at_fix"),
          "vet runs the judge's runner: rc 0 without its marker is not a pass (%s)" % {k: fr[k] for k in
                                                                                     ("fix_result", "fix_rc")})
    for b, want in (("no_marker", "base_invalid"), ("denied", "base_invalid"), ("error", "timeout"),
                    ("fail", "discriminating"), ("pass", "passes_at_base")):
        check(A.vet_verdict({"fix_result": "pass", "base_result": b})[1] == want,
              "vet verdict: base %s -> %s" % (b, want))
    check(A.vet_verdict({"fix_rc": 0, "base_rc": 1}) == (False, "fails_at_fix"),
          "vet verdict: a record without judge results (another runner) never discriminates")
    k_now = A.vet_key(b0, s["disc"], TEST, "x")
    saved = list(A._RUNNER_ID)
    A._RUNNER_ID[:] = ["judge runner changed"]
    k_other = A.vet_key(b0, s["disc"], TEST, "x")
    A._RUNNER_ID[:] = saved
    check(k_now != k_other and A._runner_id().startswith(A.VET_RUNNER + "@"),
          "vet cache key carries the judge runner's hash: a runner change invalidates every record")
    import arena_judge as J
    jsrc = Path(J.__file__).read_bytes()
    check(A.vet_runner_id(jsrc) == A._runner_id() and b"class SafeRepo" in jsrc
          and A.vet_runner_id(jsrc.replace(b"class SafeRepo", b"class SafeRepo ", 1)) != A._runner_id(),
          "runner hash covers the whole judge module (a helper such as SafeRepo, not only named functions)")
    # a second run finds everything cached
    out2 = A.run_vet(A.vet_jobs(p0), repo, tmp / "vt_vetdir", cache, workers=2, timeout=3)
    check(out2["ran"] == 0 and out2["cached"] == 8, "run_vet is resumable: a rerun runs nothing (%s)" % out2)
    bj = [{"task": "RP_VT_BUDGET", "base": b0, "fix": s["disc"],
           "checks": [{"path": TEST, "body": "assert 0\n", "key": "vt-budget-key"}]}]
    ob = A.run_vet(bj, repo, tmp / "vt_vetdir", cache, workers=1, timeout=3, budget=-1)
    check(ob["ran"] == 0 and ob["left"] == 1 and not ob["errors"] and "vt-budget-key" not in A.read_vet_cache(cache),
          "run_vet: past its budget it starts nothing and caches nothing (%s)" % ob)
    ej = [{"task": "RP_VT_INFRA", "base": b0, "fix": "0" * 40,
           "checks": [{"path": TEST, "body": "assert 0\n", "key": "vt-infra-key"}]}]
    oe = A.run_vet(ej, repo, tmp / "vt_vetdir", cache, workers=1, timeout=3)
    check(oe["ran"] == 0 and len(oe["errors"]) == 1 and "vt-infra-key" not in A.read_vet_cache(cache),
          "run_vet: an infrastructure error is reported and NOT cached (stays unvetted) (%s)" % oe)

    pool, rep = A.census(E, repo=repo, sanity="VT_DISC_FIX_ONE", old_history=[old], vet=A.vet_lookup(recs))
    got = {t["source_item"]: (t, h) for t, h in pool}
    check(set(got) == {"VT_DISC_FIX_ONE", "VT_MIXED_FIX_THREE"},
          "vet: only tasks with a discriminating check stay (%s; rejects %s)" % (sorted(got), rep["rejects"]))
    rj = A.json.dumps(rep["rejects"])
    check("discriminat" in rj and rep["vet"]["passes_at_base"] >= 2 and rep["vet"]["fails_at_fix"] == 1
          and rep["vet"]["timeout"] == 2 and rep["vet"]["discriminating"] == 3 and rep["vet"]["tasks_rejected"] == 4,
          "vet report counts: 3 discriminating, >=2 pass at base, 1 fails at fix, 2 timeouts, 4 tasks out (%s)"
          % rep["vet"])
    check(rep["rejects"].get("a hidden check cannot run under the judge (timeout, denied or no marker)") == 2,
          "fail closed: a timed-out check rejects its task even beside a discriminating one (%s)" % rep["rejects"])
    tm, hm = got["VT_MIXED_FIX_THREE"]
    types = {c["path"]: c["type"] for c in hm["checks"]}
    check(types.get(TEST) == "fix_test" and types.get(NEW2) == "fix_test_unscored",
          "mixed task: the discriminating test is scored, the base-passing one kept unscored (%s)" % types)
    check(all(isinstance(c.get("vet"), dict) and "base_rc" in c["vet"] and "fix_rc" in c["vet"]
              for _, h in pool for c in h["checks"] if c["type"].startswith("fix_test")),
          "every hidden fix_test records its base and fix exit codes")
    check("held-back" not in tm["proof"] and TEST in tm["proof"],
          "proof counts no held-back test for an unscored added one (%s)" % tm["proof"])
    # fail closed: a check the vet never ran rejects its task
    miss: list = []
    pn, rn = A.census(E, repo=repo, sanity=None, old_history=[old], vet=lambda *a: None, vet_missing=miss)
    check(not pn and rn["vet"]["not_vetted"] == 8 and any("not vetted" in k for k in rn["rejects"]),
          "fail closed: never-vetted checks reject every task (%s)" % rn["rejects"])
    mk = sorted(A.vet_key(j["base"], j["fix"], c["path"], c["body"]) for j in miss for c in j["checks"])
    check(len(mk) == 8 and all(c["key"] == A.vet_key(j["base"], j["fix"], c["path"], c["body"])
                               for j in miss for c in j["checks"]) and len(set(mk)) == 8,
          "census collects every unvetted check as a vet job (%d)" % len(mk))
    # freeze refuses a scored fix_test without a passing vet record (a pool from census(vet=None))
    pa = fresh_arena(tmp, "vt_arena")
    A.write_pool(p0, pa)
    e = raises(A.TaskRefused, A.freeze, pa)
    check(bool(e) and "vet" in e, "freeze refuses tasks whose checks were never vetted: %s" % (e or "NOT RAISED")[:120])
    # freeze binds the evidence to the check: a judge change since the census, or an edited body, refuses
    pr = fresh_arena(tmp, "vt_arena_runner")
    A.write_pool(pool, pr)
    saved = list(A._RUNNER_ID)
    A._RUNNER_ID[:] = ["judge runner changed after the census"]
    e = raises(A.TaskRefused, A.freeze, pr)
    A._RUNNER_ID[:] = saved
    check(bool(e) and "vet" in e, "freeze refuses vet evidence from another judge runner: %s" % (e or "NOT RAISED")[:120])
    import copy
    pe = fresh_arena(tmp, "vt_arena_body")
    edited = copy.deepcopy(pool)
    for c in edited[0][1]["checks"]:
        if c["type"] == "fix_test":
            c["body"] += "# edited after the vet\n"
    A.write_pool(edited, pe)
    e = raises(A.TaskRefused, A.freeze, pe)
    check(bool(e) and "vet" in e, "freeze refuses a check body edited after its vet: %s" % (e or "NOT RAISED")[:120])
    pv = fresh_arena(tmp, "vt_arena_ok")
    A.write_pool(pool, pv)
    check(A.freeze(pv)["pool"] == 2, "freeze accepts the vetted pool")

    # siblings: the report lists, per task, the pool tasks whose fix commit is in its base
    bc = rep["base_contains"]
    check(bc.get("RP_VT_MIXED_FIX_THREE") == ["RP_VT_DISC_FIX_ONE"] and bc.get("RP_VT_DISC_FIX_ONE") == []
          and rep["base_contains_pairs"] == 1,
          "base_contains: the mixed task's base holds the disc task's fix (%s)" % bc)
    later, earlier = "RP_VT_MIXED_FIX_THREE", "RP_VT_DISC_FIX_ONE"
    check(A.schedule_conflicts([later, earlier], bc) == [(later, earlier)],
          "planner: judging a task before the one its base contains is a conflict")
    check(A.schedule_conflicts([[later, earlier]], bc) == [(later, earlier)],
          "planner: the two in one round is a conflict")
    check(A.schedule_conflicts([earlier, later], bc) == [], "planner: the contained task judged first is fine")
    check(bool(raises(A.TaskRefused, A.check_schedule, [later, earlier], bc)),
          "planner: check_schedule refuses a conflicting order")
    check(A.check_schedule([earlier, later], bc) is None, "planner: check_schedule accepts the safe order")


def t_real_ledger():
    check(A.arena_root().name == "arena" and A.paths()["judge"].parent.name == "judge",
          "with ARENA_ROOT unset the root comes from rmpaths/agent_storage: %s" % A.arena_root())
    pool, rep = A.census(sanity=A.SANITY_ITEM)        # raises SanityFail if blind
    check(rep["sanity"]["found"], "real ledger: sanity item %s found (pool %d: %s)"
          % (A.SANITY_ITEM, rep["pool"], rep["labels"]))
    check(rep["pool"] > 0 and all(t["live"] in A.LIVE_OK for t, _ in pool), "real ledger: no task has live: full")
    h = {t["source_item"]: hh for t, hh in pool}[A.SANITY_ITEM]
    check(h["fix_sha"].startswith("7a68931d8a") and h["label"] == "Clean"
          and any(c.get("path") == "src/RimMandrake/FlowWorks/northstar/selftest_walk_gaps_proof.py"
                  for c in h["checks"]),
          "real ledger: the sanity item remaps to 7a68931d8a, is Clean and holds its discriminating walk-gaps check")


def main():
    tmp = Path(tempfile.mkdtemp(prefix="arena_tasks_st_"))
    saved = {k: os.environ.get(k) for k in ("ARENA_ROOT", "ARENA_CLONES")}
    try:
        repo, old, s = build_repos(tmp)
        pool = t_census(tmp, repo, old, s)
        t_hash(tmp, pool)
        t_live(tmp, pool)
        t_live_plan(tmp, pool)
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
        t_round3(tmp, repo, old, s, pool)
        t_review_2026_10_30(tmp)                # its own repo
        t_vet_siblings(tmp)                     # its own repo
        t_multi_old(tmp, repo, old, s)          # last: it adds a commit to the fixture repo
        for k, v in saved.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        t_real_ledger()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
