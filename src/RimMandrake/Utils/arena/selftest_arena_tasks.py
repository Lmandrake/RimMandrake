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
import json
import os
import shutil
import subprocess
import sys
import tempfile
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


def ledger(s, drop_good_close=False, rework_in_pool=False):
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
    check(s["esc"][:12] in toks and "FIXTURE_ESC_REWORK_THREE" in toks and NEWT in toks and RWT in toks,
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
    # a git clone: a tracked file is the checked-out base (skipped); an untracked one is a harness drop (caught)
    cl = Path(os.environ["ARENA_CLONES"]) / "ralph_b"
    shutil.copytree(Path(tmp) / "repo", cl)
    check(A.find_leaks(p) == [], "a clone's tracked files (history at its base) are not called leaks")
    (cl / "src" / "drop.txt").write_text("hint " + NEWT)
    check(any("drop.txt" in x for x in A.find_leaks(p)), "an untracked file in a git clone carrying a hidden check "
          "is caught")
    shutil.rmtree(cl)
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
