#!/usr/bin/env python3
"""selftest_list_drift_at_launch.py - the promises of design/specs/2026-11-27-list-drift-at-launch/boundary.md.

    python3 src/RimMandrake/Utils/selftest_list_drift_at_launch.py               every promise, then each planted fault
    python3 src/RimMandrake/Utils/selftest_list_drift_at_launch.py --live-record  the live repro on ArchSmall holds

Offline: one test per promise, run on the real code (must pass), then each test on its planted fault (must go red; a
test that cannot go red fails this file). Nothing here reads or writes a live list, game or journal: lists, swap books
and the journal are temp files (RM_LIST_JOURNAL_DIR), and game_instance's start, Steam and process reads are stubbed.

--live-record reads design/specs/2026-11-27-list-drift-at-launch/live_repro.json, written by the live repro of
RIMMANDRAKE_TRACE_ARCHSMALL_TIER_SWAP_UNDONE_BEFORE_LAUNCH: it holds (exit 0) when the record shows at least two launches
of ArchSmall after one `modset_builder --tier T --apply`, and each launch ran exactly the tier's packageIds
(`jawa/running_mods`) and its list line read `= tier T`. Exit 1 when the record is absent or shows less.
"""
import atexit
import contextlib
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time

TMP = tempfile.mkdtemp(prefix="st_list_drift_")
atexit.register(shutil.rmtree, TMP, True)
for _k in ("RM_GAME_INSTANCE", "RM_GAME_USERDATA", "RM_GAME_LOGDIR"):
    os.environ.pop(_k, None)
os.environ.update(RM_LIST_JOURNAL_DIR=os.path.join(TMP, "journal"), RM_HOST="archmagi",
                  RM_INSTANCES_ROOT=os.path.join(TMP, "instances"))
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for _p in (HERE, os.path.join(os.path.dirname(HERE), "rimflow")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
LIVE_RECORD = os.path.join(REPO, "design", "specs", "2026-11-27-list-drift-at-launch", "live_repro.json")

import list_journal as LJ       # noqa: E402

LIST = '<?xml version="1.0" encoding="utf-8"?>\n<ModsConfigData>\n  <version>1.6</version>\n  <activeMods>\n%s  </activeMods>\n</ModsConfigData>\n'


def write_list(path, ids, mtime=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(LIST % "".join("    <li>%s</li>\n" % i for i in ids))
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path


def md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def fresh(name):
    d = os.path.join(TMP, name + "_%d" % int(time.time() * 1e6))
    os.makedirs(d)
    os.environ["RM_LIST_JOURNAL_DIR"] = os.path.join(d, "journal")
    return d


TIER = ["ludeon.rimworld", "brrainz.harmony", "mandrake.rm.flowworks"]
OLD = ["ludeon.rimworld", "brrainz.harmony", "mandrake.rm.flowworks", "mandrake.rm.inhabited", "kutte.stairs"]
CORE = ["ludeon.rimworld", "ludeon.rimworld.royalty"]


# ---------------------------------------------------------------- the promises, one test each; each returns failures

def t_a_launch_on_modset_builders_last_write_names_its_tier_and_owner():
    """a-launch-on-modset-builders-last-write-names-its-tier-and-owner"""
    d = fresh("match")
    cfg = write_list(os.path.join(d, "Config", "ModsConfig.xml"), TIER)
    bad = []
    if LJ.record(cfg, "b", "apply", tier="flowworks_list", by="BENCH") is not None:
        bad.append("record refused a readable list")
    line = LJ.launch_line(cfg, "b", label="ArchSmall")
    if "= tier flowworks_list, written by BENCH at" not in line or "LIST CHANGED" in line:
        bad.append("match line wrong: %s" % line)
    LJ.record(cfg, "b", "restore-own", by="BENCH.b")
    line = LJ.launch_line(cfg, "b", label="ArchSmall")
    if "= the restore-own of modset_builder, written by BENCH.b" not in line:
        bad.append("restore match line wrong: %s" % line)
    return bad


def t_a_launch_after_another_writer_says_list_changed_with_md5_mtime_and_the_copy():
    """a-launch-after-another-writer-says-list-changed-with-md5-mtime-and-the-copy"""
    d = fresh("changed")
    jdir = os.environ["RM_LIST_JOURNAL_DIR"]
    old_mtime = time.time() - 4 * 3600
    before = write_list(os.path.join(jdir, "BENCH.b", "ModsConfig.before-tier-flowworks_list.xml"), OLD, old_mtime)
    decoy = write_list(os.path.join(jdir, "other.b", "ModsConfig.before-tier-x.xml"), OLD, old_mtime - 600)
    cfg = write_list(os.path.join(d, "Config", "ModsConfig.xml"), TIER)
    LJ.record(cfg, "b", "apply", tier="flowworks_list", by="BENCH")
    shutil.copy2(before, cfg)       # the 2026-11-26 shape: an older list back, its source's mtime kept
    line = LJ.launch_line(cfg, "b", label="ArchSmall")
    bad = []
    want = ["LIST CHANGED", "tier flowworks_list", md5(os.path.join(d, "Config", "ModsConfig.xml"))[:8],
            "(5 mods, mtime", "by BENCH", before]
    for w in want:
        if w not in line:
            bad.append("changed line lacks %r: %s" % (w, line))
    if decoy in line:
        bad.append("a copy with another mtime was named: %s" % line)
    rows = LJ.rows("b")
    if not rows or rows[-1].get("act") != "launch" or rows[-1].get("drift") is not True:
        bad.append("the launch row is not journaled as drift: %s" % rows[-1:])
    return bad


def t_no_write_on_record_is_its_own_answer():
    """no-write-on-record-is-its-own-answer"""
    d = fresh("nowrite")
    cfg = write_list(os.path.join(d, "Config", "ModsConfig.xml"), TIER)
    other = write_list(os.path.join(d, "Other", "ModsConfig.xml"), OLD)
    bad = []
    line = LJ.launch_line(cfg, "b", label="ArchSmall")
    if "no modset_builder write of it on record for ArchSmall" not in line:
        bad.append("empty journal line wrong: %s" % line)
    LJ.record(other, "b", "apply", tier="x", by="BENCH")     # a write of another file is no write of this one
    line = LJ.launch_line(cfg, "b", label="ArchSmall")
    if "no modset_builder write of it on record" not in line:
        bad.append("another file's write was read as this list's: %s" % line)
    return bad


def t_a_list_or_journal_that_cannot_be_read_says_could_not_look():
    """a-list-or-journal-that-cannot-be-read-says-could-not-look"""
    d = fresh("cnl")
    bad = []
    line = LJ.launch_line(os.path.join(d, "Config", "ModsConfig.xml"), "b", label="ArchSmall")
    if not line.startswith("list: COULD NOT LOOK"):
        bad.append("missing list: %s" % line)
    broken = os.path.join(d, "Config2", "ModsConfig.xml")
    os.makedirs(os.path.dirname(broken))
    with open(broken, "w") as f:
        f.write("<ModsConfigData><activeMods><li>torn")
    line = LJ.launch_line(broken, "b", label="ArchSmall")
    if not line.startswith("list: COULD NOT LOOK"):
        bad.append("unparsable list: %s" % line)
    cfg = write_list(os.path.join(d, "Config3", "ModsConfig.xml"), TIER)
    os.makedirs(LJ.journal_path("b"))      # a folder where the journal file should be: it cannot be read
    line = LJ.launch_line(cfg, "b", label="ArchSmall")
    if "COULD NOT LOOK at modset_builder's journal" not in line or "no modset_builder write" in line:
        bad.append("unreadable journal: %s" % line)
    return bad


def _modset():
    import modset_builder as MB
    return MB


def t_every_verified_live_write_of_modset_builder_is_journaled_and_a_temp_list_is_not():
    """every-verified-live-write-of-modset-builder-is-journaled-and-a-temp-list-is-not"""
    MB = _modset()
    d = fresh("modset")
    bad = []
    live = write_list(os.path.join(d, "Config", "ModsConfig.xml"), TIER)
    saved = MB.CONFIG
    MB.CONFIG = live
    try:
        def books(name, before_ids, live_ids):
            b = os.path.join(d, name)
            os.makedirs(b)
            bc = write_list(os.path.join(b, "ModsConfig.before-tier-t.xml"), before_ids)
            write_list(live, live_ids)
            with open(os.path.join(b, MB.SWAP_MARKER), "w") as f:
                json.dump({"tier": "t", "before": os.path.basename(bc), "md5": md5(bc), "tier_md5": md5(live)}, f)
            return b
        with contextlib.redirect_stdout(open(os.devnull, "w")):
            MB.restore_own(live, books("own.b", OLD, TIER))
            MB.restore_before(live, books("plain", OLD, TIER))
            b = books("reset.b", OLD, TIER)
            write_list(live, CORE)                          # the game's crash reset, after the marker was written
            MB.repair_game_reset(live, b)
            MB.journal(live, "apply", tier="t", by="BENCH")         # the --apply and --restore-full calls in main
            MB.journal(live, "restore-full", by="clone x")
        acts = [(r.get("act"), r.get("by")) for r in LJ.rows("a")]
        want = [("restore-own", "own.b"), ("restore", "plain"), ("repair-reset", "reset.b"), ("apply", "BENCH"),
                ("restore-full", "clone x")]
        if acts != want:
            bad.append("journal rows %s, want %s" % (acts, want))
        rows = LJ.rows("a")
        if rows and rows[0].get("md5") != hashlib.md5((LIST % "".join("    <li>%s</li>\n" % i for i in OLD)).encode()).hexdigest():
            bad.append("restore-own row's md5 is not the list it wrote: %s" % rows[0].get("md5"))
        src = open(MB.__file__, encoding="utf-8").read()
        for call in ('journal(CONFIG, "restore-full"', 'journal(CONFIG, "apply", tier=a.tier'):
            if call not in src:
                bad.append("main lost its %s call" % call)
        n = len(LJ.rows("a"))
        other = write_list(os.path.join(d, "Elsewhere", "ModsConfig.xml"), TIER)
        with contextlib.redirect_stdout(open(os.devnull, "w")):
            MB.journal(other, "apply", tier="t", by="BENCH")
        if len(LJ.rows("a")) != n:
            bad.append("a list at another path was journaled")
        appended, keep_env = [], os.environ.pop("RM_LIST_JOURNAL_DIR")
        try:      # no journal folder named: a list under the system temp folder is a test's, and writes no row anywhere
            with patched(LJ, "_append", lambda g, r: appended.append(r)):
                tmp_list = write_list(os.path.join(tempfile.mkdtemp(), "Config", "ModsConfig.xml"), TIER)
                LJ.record(tmp_list, "a", "apply", tier="t", by="BENCH")
                LJ.launch_line(tmp_list, "a")
        finally:
            os.environ["RM_LIST_JOURNAL_DIR"] = keep_env
        if appended:
            bad.append("a temp list with no journal folder named was journaled: %s" % appended)
    finally:
        MB.CONFIG = saved
    return bad


def _gi():
    import game_instance as GI
    return GI


@contextlib.contextmanager
def stub_launch(GI, calls):
    keep = {k: getattr(GI, k) for k in ("pid", "hold_refusal", "_steam_running", "_launch_a", "prepare", "_need_appid",
                                        "_launch_named", "mods_config")}
    d = fresh("gi")
    cfgs = {"a": write_list(os.path.join(d, "a", "ModsConfig.xml"), TIER),
            "b": write_list(os.path.join(d, "b", "Config", "ModsConfig.xml"), TIER)}
    GI.pid = lambda name=None: None
    GI.hold_refusal = lambda name, despite=None: None
    GI._steam_running = lambda: True
    GI._launch_a = lambda *a: calls.append("start a") or (0, "started game a by steam, pid 1")
    GI.prepare = lambda name=None: os.path.join(d, name)
    GI._need_appid = lambda *a, **k: None
    GI._launch_named = lambda name, *a: calls.append("start " + name) or (0, "started game %s, pid 2" % name)
    GI.mods_config = lambda name=None: calls.append("list " + GI.check_name(name)) or cfgs[GI.check_name(name)]
    try:
        yield cfgs
    finally:
        for k, v in keep.items():
            setattr(GI, k, v)


def t_game_instance_launch_carries_the_line_on_both_games():
    """game-instance-launch-carries-the-line-on-both-games"""
    GI = _gi()
    bad = []
    for game, letter in (("ArchBig", "a"), ("ArchSmall", "b")):
        calls = []
        with stub_launch(GI, calls) as cfgs:
            LJ.record(cfgs[letter], letter, "apply", tier="flowworks_list", by="BENCH")
            rc, text = GI.launch(game)
        if rc != 0 or "; list md5" not in text or "= tier flowworks_list" not in text:
            bad.append("%s launch text lacks the list line: %r" % (game, text))
        if calls != ["list " + letter, "start " + letter]:
            bad.append("%s: the line is not made before the start: %s" % (game, calls))
    return bad


def t_the_line_never_fails_a_launch():
    """the-line-never-fails-a-launch"""
    GI = _gi()
    bad = []
    keep = LJ.launch_line

    def boom(*a, **k):
        raise RuntimeError("planted reader fault")
    LJ.launch_line = boom
    try:
        for game in ("ArchBig", "ArchSmall"):
            calls = []
            with stub_launch(GI, calls):
                rc, text = GI.launch(game)
            if rc != 0 or "COULD NOT LOOK (RuntimeError: planted reader fault)" not in text or not any(
                    c.startswith("start") for c in calls):
                bad.append("%s: a raising reader changed the launch: rc %s %r %s" % (game, rc, text, calls))
    finally:
        LJ.launch_line = keep
    calls = []
    with stub_launch(GI, calls):
        os.environ["RM_LIST_JOURNAL_DIR"] = "/proc/no/such/journal"      # a folder nobody can make: absent, so empty
        rc, text = GI.launch("ArchSmall")
    if rc != 0 or "(launch not journaled:" not in text or "start b" not in calls:
        bad.append("an unmakeable journal folder changed the launch or went unsaid: rc %s %r" % (rc, text))
    return bad




# ---------------------------------------------------------------- planted faults: each must turn its test red

@contextlib.contextmanager
def patched(obj, name, value):
    keep = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, keep)


def _last_any(config, game):          # forgets which file a write was of
    rs = [r for r in LJ.rows(game) if r.get("act") != "launch"]
    return rs[-1] if rs else None


def _rows_blind(game):                # an unreadable journal read as empty
    try:
        return KEEP_ROWS(game)
    except LJ.CouldNotLook:
        return []


KEEP_ROWS = LJ.rows
PLANTS = [
    (t_a_launch_on_modset_builders_last_write_names_its_tier_and_owner, "last_write sees nothing", lambda: patched(LJ, "last_write", lambda c, g: None)),
    (t_a_launch_after_another_writer_says_list_changed_with_md5_mtime_and_the_copy, "the copy search finds nothing", lambda: patched(LJ, "same_copies", lambda *a: [])),
    (t_a_launch_after_another_writer_says_list_changed_with_md5_mtime_and_the_copy, "the copy search ignores mtime", lambda: patched(
        LJ, "same_copies", lambda cur, roots, config: sorted(
            p for r in roots for p in __import__("glob").glob(os.path.join(r, "**/ModsConfig*.xml"), recursive=True)
            if md5(p) == cur["md5"]))),
    (t_no_write_on_record_is_its_own_answer, "a write of another file counts", lambda: patched(LJ, "last_write", _last_any)),
    (t_a_list_or_journal_that_cannot_be_read_says_could_not_look, "an unreadable journal reads as empty", lambda: patched(LJ, "rows", _rows_blind)),
    (t_every_verified_live_write_of_modset_builder_is_journaled_and_a_temp_list_is_not, "modset_builder journals nothing", lambda: patched(_modset(), "journal", lambda *a, **k: None)),
    (t_every_verified_live_write_of_modset_builder_is_journaled_and_a_temp_list_is_not, "a temp list is journaled",
     lambda: patched(LJ, "_test_list", lambda c: False)),
    (t_game_instance_launch_carries_the_line_on_both_games, "launch drops the line", lambda: patched(_gi(), "list_line", lambda name: "")),
    (t_the_line_never_fails_a_launch, "the line's fault reaches the launch", lambda: patched(
        _gi(), "list_line", lambda name: LJ.launch_line(_gi().mods_config(name), name))),
]


def live_record():
    try:
        with open(LIVE_RECORD, encoding="utf-8") as f:
            rec = json.load(f)
    except (OSError, ValueError) as e:
        print("NOT YET: no readable live record at %s (%s)" % (LIVE_RECORD, e))
        return 1
    tier, ids = rec.get("tier"), set(rec.get("tier_ids") or [])
    launches = rec.get("launches") or []
    bad = [] if tier and ids and len(launches) >= 2 and rec.get("game") == "ArchSmall" else [
        "needs game ArchSmall, a tier, its ids and at least two launches"]
    for i, L in enumerate(launches, 1):
        run = set(L.get("running") or [])
        if run != ids:
            bad.append("launch %d ran %d mods, not the tier's %d: missing %s extra %s" % (
                i, len(run), len(ids), sorted(ids - run)[:5], sorted(run - ids)[:5]))
        if "= tier %s" % tier not in (L.get("line") or ""):
            bad.append("launch %d line does not read = tier %s: %s" % (i, tier, L.get("line")))
    for b in bad:
        print("FAIL " + b)
    print("%s live record %s: %d launch(es) of tier %s" % ("FAIL" if bad else "PASS", LIVE_RECORD, len(launches), tier))
    return 1 if bad else 0


def main(argv):
    if "--live-record" in argv:
        return live_record()
    fails = 0
    for t in (t_a_launch_on_modset_builders_last_write_names_its_tier_and_owner, t_a_launch_after_another_writer_says_list_changed_with_md5_mtime_and_the_copy, t_no_write_on_record_is_its_own_answer, t_a_list_or_journal_that_cannot_be_read_says_could_not_look, t_every_verified_live_write_of_modset_builder_is_journaled_and_a_temp_list_is_not, t_game_instance_launch_carries_the_line_on_both_games, t_the_line_never_fails_a_launch):
        bad = t()
        print(("ok   " if not bad else "FAIL ") + t.__doc__)
        for b in bad:
            print("       " + b[:500])
        fails += bool(bad)
    for t, what, plant in PLANTS:
        with plant():
            try:
                bad = t()
            except Exception as e:      # noqa: BLE001 - a crash under the plant is red too
                bad = ["raised %s: %s" % (type(e).__name__, e)]
        caught = bool(bad)
        print(("ok   " if caught else "FAIL ") + "planted '%s' turns %s red" % (what, t.__doc__))
        fails += not caught
    print("%s selftest_list_drift_at_launch: %d failed" % ("PASS" if not fails else "FAIL", fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
