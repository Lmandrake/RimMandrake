#!/usr/bin/env python3
"""selftest: every Relentless jam is fixed as a class (JAM_CLASS_BUILD_OPS_DETECTOR_PER_CLASS). jam_classes.py's lint
and census, ops_watch's relentless.jam_unnamed / relentless.jam_repeat points and their targets, and the help_folder_left
remedy (relentless Effects.help_path).

    python3 src/RimMandrake/rimflow/selftest_jam_classes.py
"""
import copy
import json
import os
import shutil
import sys
import tempfile
import time
import types
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
sys.path[:0] = [HERE, UTILS]
TMP = tempfile.mkdtemp(prefix="selftest_jam_classes_")
os.environ["RM_OPS_WATCH_DIR"] = os.path.join(TMP, "ops")      # nothing here reads or writes the real alarm log
import jam_classes as JC  # noqa: E402
import ops_watch as OW  # noqa: E402

FAILS = []
REG = JC.load()
TARGETS = JC.target_names()

# Every jam reason the belt journaled 2026-11-01..04 (store/journal.jsonl, kinds jam/books_stale/breaker_emergency),
# one per distinct cause, with the class a human gave it. A class dropped or a regex narrowed shows here as a miss.
REAL = [
    ("day_spend_limit", "spend_cap"),
    ("breaker open until 2026-11-02T15:03:10Z: checkout 567b22fad99acbaaa9ef388b1699e474d3b420f4: fatal: unable to read "
     "tree (567b22fad99acbaaa9ef388b1699e474d3b420f4)", "clone_missing_commit"),
    ("pool full: 10 clones, cap 10 (1 kept for checks), nothing to release: BIOME_TIER_CLEANUP_1 (live)", "pool_full"),
    ("pool full: 16 clones, cap 16, nothing to release: CAULDRON_ROSTER_BOUNDARY_RECONCILE_PATCH (live)", "pool_full"),
    ("books 3 behind: dirty outside the ledger: infrastructure/state/art/events/BENCH.jsonl", "books_dirty"),
    ("books 2 behind: dirty outside the ledger: src/RimMandrake/Utils/modcheck/test_site_saves.json", "books_dirty"),
    ("books cannot fetch: git@github.com: Permission denied (publickey).\nfatal: Could not read from remote repository.",
     "origin_refused"),
    ("breaker open until 2026-11-04T10:26:23Z: clone failed: scratch_clone: FAILED: git fetch -q origin: git@github.com: "
     "Permission denied (publickey).", "origin_refused"),
    ("breaker open until 2026-11-04T11:59:10Z: help clone failed: scratch_clone: FAILED: /home/mandrake/rm/relentless/"
     "clones/help-ROLE_TOKENS_REPAIR_DESIGNER_ARTIST_CAPS-c1 already exists", "help_folder_left"),
    ("clone lacks src/RimMandrake/Utils/claude_bounded.sh and its bundle failed: [Errno 7] Argument list too long: 'git'",
     "bundle_too_long"),
    ("the run ended on the account's own error: rate_limit", "account_limit"),
    ("breaker open until 2026-11-04T20:06:50Z: rm-relentless-work-2f7d7ad7e9-g24 died at once with no usage",
     "launch_died_unpaid"),
    ("health degraded: content paused while system items wait", "content_paused_idle"),
]


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def mutant(fn):
    r = copy.deepcopy(REG)
    fn(r)
    return JC.lint(r, TARGETS, check_sha=False)


def cls(r, cid):
    return next(c for c in r["classes"] if c["id"] == cid)


def has_git():
    import subprocess
    try:
        return subprocess.run(["git", "-C", str(JC.REPO), "rev-parse", "--git-dir"], capture_output=True,
                              timeout=30).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def lint():
    git = has_git()
    bad = JC.lint(REG, TARGETS, check_sha=git)
    check(bad == [], "the shipped registry lints clean: %s" % bad)
    if not git:
        print("UNMEASURED fixed.sha: this tree has no git history; every other lint rule ran")
    for m in REG["meta_targets"]:
        check(m in TARGETS, "meta target %s is an ops_watch target" % m)
    rules = json.load(open(JC.OPS_RULES, encoding="utf-8"))
    keys = {t.get("name"): t for t in rules["targets"]}
    check(keys[REG["meta_targets"][0]]["key"] == "relentless.jam_unnamed" and keys[REG["meta_targets"][0]]["alarm"],
          "the unnamed-jam target alarms on relentless.jam_unnamed")
    check(keys[REG["meta_targets"][1]]["key"] == "relentless.jam_repeat" and keys[REG["meta_targets"][1]]["alarm"],
          "the repeat target alarms on relentless.jam_repeat")
    for c in REG["classes"]:
        rem = c["remedy"]
        check("auto" in rem or len(rem.get("none", "")) >= 40, "class %s has a remedy or says why none is safe" % c["id"])
    # mutants: each broken registry is refused, by name
    cases = [
        ("detector names no target", lambda r: cls(r, "pool_full")["detector"].update(target="OPS_NO_SUCH_TARGET"),
         "detector target"),
        ("remedy names a function that does not exist",
         lambda r: cls(r, "pool_full")["remedy"].update(auto="src/RimMandrake/rimflow/relentless.py::no_such_fn"),
         "defines no function"),
        ("remedy is both auto and none", lambda r: cls(r, "pool_full")["remedy"].update(none="x" * 50), "exactly one"),
        ("remedy is neither", lambda r: cls(r, "spend_cap").update(remedy={}), "exactly one"),
        ("a none remedy with no reason", lambda r: cls(r, "spend_cap")["remedy"].update(none="unsafe"), "reason"),
        ("an example two classes match", lambda r: cls(r, "spend_cap")["match"].append("pool full"), "not this class alone"),
        ("an example its own class misses", lambda r: cls(r, "pool_full").update(match=["^nothing like it"]),
         "matches nothing"),
        ("a regex that does not compile", lambda r: cls(r, "pool_full")["match"].append("(unclosed"), "does not compile"),
        ("a meta target that does not exist", lambda r: r.update(meta_targets=["OPS_NOPE", r["meta_targets"][1]]),
         "meta target OPS_NOPE"),
        ("a plain name of two sentences", lambda r: cls(r, "pool_full").update(plain="Pool full. Nothing ran."),
         "one short sentence"),
        ("a fix with no time", lambda r: cls(r, "pool_full")["fixed"].update(at="yesterday"), "fixed.at"),
        ("a class with no fixed key at all", lambda r: cls(r, "pool_full").pop("fixed"), "fixed is null"),
        ("a class with no examples", lambda r: cls(r, "pool_full").update(examples=[]), "examples"),
        ("an id used twice", lambda r: r["classes"].append(copy.deepcopy(cls(r, "spend_cap"))), "id used twice"),
    ]
    for name, fn, word in cases:
        bad = mutant(fn)
        check(any(word in b for b in bad), "lint refuses %s (%s)" % (name, bad[:2]))
    check(JC.lint(dict(REG, classes=[dict(cls(REG, "pool_full"), fixed={"sha": "0" * 40, "at": "2026-11-01T00:00:00Z"})]),
                  TARGETS) != [], "lint refuses a fixed.sha git does not know")


def classify():
    for text, want in REAL:
        got = JC.classify(REG, JC.reason({"why": text}))
        check(got == want, "real reason -> %s (got %s): %s" % (want, got, text[:70].replace("\n", " ")))
    check(JC.classify(REG, "the moon fell on the scheduler") is None, "a reason no class names classifies as None")
    check(JC.reason({"why": "breaker open until 2026-11-04T11:59:10Z: day_spend_limit"}) == "day_spend_limit",
          "the breaker's open-until prefix is removed before matching")


def journal(rows):
    p = Path(TMP) / ("journal_%d.jsonl" % len(os.listdir(TMP)))
    with open(p, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
        f.write('{"at": "2026-11-04T1')      # a torn last line from a killed tick
    return p


def census():
    fix = cls(REG, "pool_full")["fixed"]["at"]
    now = JC.epoch(fix) + 4 * 3600      # the times follow the shipped fix, which moves each time the class is fixed again
    before = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(JC.epoch(fix) - 3600))
    after = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(JC.epoch(fix) + 3600))
    assert JC.epoch(before) < JC.epoch(fix) < JC.epoch(after)
    rows = [
        {"at": before, "do": "alarm", "kind": "jam", "why": "pool full: 16 clones, cap 16, nothing to release: A (live)"},
        {"at": after, "do": "alarm", "kind": "jam", "why": "pool full: 16 clones, cap 16, nothing to release: B (live)"},
        {"at": after, "do": "alarm", "kind": "jam", "why": "the moon fell on the scheduler"},
        {"at": "2026-10-01T00:00:00Z", "do": "alarm", "kind": "jam", "why": "an old unnamed thing, out of window"},
        {"at": after, "do": "alarm", "kind": "understaffed", "why": "not a jam kind"},
        {"at": after, "do": "lease", "kind": "jam", "why": "not an alarm"},
    ] + [{"at": "2026-11-04T12:26:55Z", "do": "alarm", "kind": "breaker_emergency", "road": road,
          "why": "clone lacks x and its bundle failed: [Errno 7] Argument list too long: 'git'"}
         for road in ("told", "conductor", "item")]
    c = JC.census(REG, journal(rows), now)
    check(c.get("jams") == 4, "census counts 4 jams: in window, jam kinds, alarms only, one per road set (%s)" % c.get("jams"))
    check([r["why"] for r in c["unnamed"]] == ["the moon fell on the scheduler"], "the unnamed jam is reported: %s" % c["unnamed"])
    check([(r["cls"], r["at"]) for r in c["repeats"]] == [("pool_full", after)],
          "pool_full after its fixed.at is a repeat; before it is not: %s" % c["repeats"])
    check(c["by_class"] == {"pool_full": 2, "bundle_too_long": 1}, "by_class: %s" % c["by_class"])
    check("origin_refused" in c["open"], "a class with no fix yet is listed open")
    check("error" in JC.census(REG, Path(TMP) / "absent.jsonl", now), "an absent journal is an error, never zero jams")
    return rows, now


def books_dirty_refix():
    """OPS_JAM_CLASS_FIX_AGAIN_HJWN: the class fixed again moves fixed.at past the jam that reopened it (11:20Z on
    rail_walk_result_*), so that jam stops counting as a repeat; one after the new fix still counts."""
    fx = cls(REG, "books_dirty")["fixed"]
    check(JC.epoch(fx["at"]) > JC.epoch("2026-11-05T11:20:00Z"), "books_dirty.fixed.at is after the reopening jam: %s" % fx)
    why = ("books 3 behind: dirty outside the ledger: "
           "src/RimMandrake/FlowWorks/northstar/rail_walk_result_20261105T021421.json")
    rows = [{"at": "2026-11-05T11:20:00Z", "do": "alarm", "kind": "jam", "why": why}]
    c = JC.census(REG, journal(rows), JC.epoch("2026-11-05T12:00:00Z"))
    check(c.get("by_class") == {"books_dirty": 1} and c.get("repeats") == [],
          "the 11:20Z books_dirty jam is classed and is no repeat: %s" % c)
    rows.append({"at": "2026-11-05T13:00:00Z", "do": "alarm", "kind": "jam", "why": why})
    c = JC.census(REG, journal(rows), JC.epoch("2026-11-05T14:00:00Z"))
    check([r["at"] for r in c.get("repeats", [])] == ["2026-11-05T13:00:00Z"], "a jam after the new fix is a repeat: %s" % c)


def pool_full_refix():
    """OPS_JAM_CLASS_FIX_AGAIN_HJWN, 2026-11-06: pool_full fixed again (dead uncharged runs pinned clones live) moves
    fixed.at past the jam that reopened it (04:23:14Z), so that jam stops counting as a repeat; one after still counts."""
    fx = cls(REG, "pool_full")["fixed"]
    check(JC.epoch(fx["at"]) > JC.epoch("2026-11-06T04:49:53Z"), "pool_full.fixed.at is after the reopening jams: %s" % fx)
    why = "pool full: 15 clones, cap 16 (1 kept for checks), nothing to release: BAROQUE_LIST_PAGE_REDRAW_UMBRA_AS_BIOME (live)"
    rows = [{"at": "2026-11-06T04:23:14Z", "do": "alarm", "kind": "jam", "why": why}]
    c = JC.census(REG, journal(rows), JC.epoch("2026-11-06T06:00:00Z"))
    check(c.get("by_class") == {"pool_full": 1} and c.get("repeats") == [],
          "the 04:23Z pool_full jam is classed and is no repeat: %s" % c)
    rows.append({"at": "2026-11-06T07:00:00Z", "do": "alarm", "kind": "jam", "why": why})
    c = JC.census(REG, journal(rows), JC.epoch("2026-11-06T08:00:00Z"))
    check([r["at"] for r in c.get("repeats", [])] == ["2026-11-06T07:00:00Z"], "a pool_full jam after the new fix is a repeat: %s" % c)


def ops(rows, now):
    store = Path(TMP) / "store"
    store.mkdir()
    with open(store / "journal.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    p = OW.rl_jams(store, now)
    check(p["relentless.jam_unnamed"]["m"] == "MEASURED" and p["relentless.jam_unnamed"]["v"] == 1,
          "ops_watch: relentless.jam_unnamed MEASURED 1 (%s)" % p["relentless.jam_unnamed"])
    check(p["relentless.jam_repeat"]["v"] == 1 and p["relentless.jam_repeat"]["x"]["classes"] == ["pool_full"],
          "ops_watch: relentless.jam_repeat 1, class pool_full (%s)" % p["relentless.jam_repeat"])
    check("moon" in p["relentless.jam_unnamed"]["x"]["first"], "the unnamed alarm's title field carries the reason")
    clean = Path(TMP) / "clean"
    clean.mkdir()
    (clean / "journal.jsonl").write_text(json.dumps(rows[0]) + "\n")
    q = OW.rl_jams(clean, now)
    check(q["relentless.jam_unnamed"]["v"] == 0 and q["relentless.jam_repeat"]["v"] == 0,
          "ops_watch: a journal of named, pre-fix jams reads 0 and 0")
    q = OW.rl_jams(Path(TMP) / "nostore", now)
    check(q["relentless.jam_unnamed"]["m"] == "UNMEASURED" and q["relentless.jam_repeat"]["m"] == "UNMEASURED",
          "ops_watch: an unreadable journal is UNMEASURED, never a quiet 0")


def help_folder():
    import relentless as R
    base = Path(TMP) / "belt"
    (base / "clones").mkdir(parents=True)
    me = types.SimpleNamespace(base=str(base))
    st = {"item": "SOME_ITEM", "help_count": 0}
    check(R.Effects.help_path(me, st).endswith("help-SOME_ITEM-c1"), "help_path: c1 when free")
    (base / "clones" / "help-SOME_ITEM-c1").mkdir()
    check(R.Effects.help_path(me, st).endswith("help-SOME_ITEM-c2"),
          "help_path: a leftover c1 folder is skipped, not reused (jam class help_folder_left)")
    check((base / "clones" / "help-SOME_ITEM-c1").is_dir(), "help_path deletes nothing")
    st["help_count"] = 4
    check(R.Effects.help_path(me, st).endswith("help-SOME_ITEM-c5"), "help_path starts from help_count + 1")


if __name__ == "__main__":
    try:
        lint()
        classify()
        rows, now = census()
        ops(rows, now)
        books_dirty_refix()
        pool_full_refix()
        help_folder()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("selftest_jam_classes: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
