#!/usr/bin/env python3
"""selftest_live_checks_in_builder_run.py: the promises of design/specs/2026-11-24-live-checks-in-builder-run/boundary.md,
one test of each name (item RIMMANDRAKE_RUN_LIVE_CHECKS_IN_BUILDER_RUN_WHEN_GAME_FREE). Each test builds a throwaway git
repository with one mod and READS what the real code answers or writes: the briefs a builder and a fixer get, the early
rows `maturation.py live-row` writes, and what Stage 6 then owes. Offline: no game, bridge, claude, unit or landing."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="live_in_run_")
for _k, _v in (("RM_MATURATION_DISPATCH_DIR", "_dispatch"), ("RM_DISPATCHER_STATE", "_dispatcher"),
               ("RM_REFUSAL_DIR", "_refusals"), ("RM_OPS_WATCH_DIR", "_ops")):
    os.environ[_k] = os.path.join(TMP, _v)      # never a live store
os.environ["RM_STAGE_LAND"] = "0"
for _k in ("RM_MODLEDGER_WRITER", "RM_MODLEDGER_TOKEN", "RM_ROLE_UNIT"):
    os.environ.pop(_k, None)
import maturation as M              # noqa: E402
import maturation_autonomy as A     # noqa: E402
import build_match as BM            # noqa: E402
import live_kinds as LK             # noqa: E402

MOD, VER = "LiveInRun", "0.1.0"
CHECKS = ("sc_a", "sc_b", "sc_c")
IDENT = {"mod_hash": "h1", "game_build": "1.6.4871 rev590", "active_mods": ["ludeon.rimworld"], "tier": "liveinrun"}
EARLY = "version/in_game/early_rows.jsonl"
ITEM = "RIMMANDRAKE_FIX_SELFTEST_LINE_ONE_OF_ONE"
IN_GAME_MOVE = {"from": "blind_challenge", "to": "in_game", "at": "2026-11-23T10:00:00-08:00", "by": "BENCH"}
BACK_MOVE = {"from": "in_game", "to": "offline_build", "at": "2026-11-23T12:00:00-08:00", "by": "BENCH"}


class Tree(object):
    def __init__(self, stage="offline_build", moves=(), cs=False):     # cs: the change is C# that every check reads
        self.root = tempfile.mkdtemp(prefix="r_", dir=TMP)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "selftest@example.invalid")
        self.git("config", "user.name", "selftest")
        self.tests = {t: {"id": t, "kind": "live_minimal", "stage": "6", "tier": "liveinrun",
                          "file": "src/RimMandrake/%s/validation.py" % MOD, "entry": t,
                          "reads": ["src/RimMandrake/%s/Source/A.cs" % MOD]} for t in CHECKS}
        self.put("src/RimMandrake/%s/validation.py" % MOD, "".join("def %s():\n    return 1\n" % t for t in CHECKS))
        self.put("src/RimMandrake/%s/Source/A.cs" % MOD, "class A { int v = 0; }\n")
        self.put(self.c("version/test_table.json"), json.dumps({"version": VER, "tests": self.tests}))
        self.put(self.c("version/VERSION.json"), json.dumps({"version": VER}))
        self.put(self.c("journal.md"), "# j\n\n- **Stage now:** x.\n- **Waiting on:** x.\n- **Next:** x.\n")
        self.stage(stage, moves)
        self.put("infrastructure/state/ledger/events/OWNER.jsonl", "")
        self.c0 = self.commit("base")
        self.put("src/RimMandrake/%s/Docs.txt" % MOD, "x\n")
        if cs:
            self.put("src/RimMandrake/%s/Source/A.cs" % MOD, "class A { int v = 1; }\n")
        self.c1 = self.commit("the change")
        self.put("src/RimMandrake/%s/Docs.txt" % MOD, "y\n")
        self.c2 = self.commit("later")

    def c(self, p):
        return "design/concepts/%s/%s" % (MOD, p)

    def git(self, *a):
        return subprocess.run(["git", "-C", self.root] + list(a), capture_output=True, text=True, timeout=60,
                              check=True).stdout.strip()

    def put(self, rel, text):
        p = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(text)

    def commit(self, msg):
        self.git("add", "-A", ".")
        self.git("commit", "-q", "--allow-empty", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def stage(self, stage, moves=()):
        self.put(self.c("version/stage_record.json"), json.dumps({
            "mod": MOD, "version": VER, "stage": stage, "cycles": {"visit": 0, "total": 1}, "moves": list(moves)}))

    def visit_rows(self, shas, visit=1, **kw):
        self.put(self.c("version/in_game/visit_%d/rows.jsonl" % visit), "".join(json.dumps(dict(
            {"test": t, "verdict": "PASS", "outcome": "SUCCESS", "site_checked": True, "mod_sha": s}, **kw)) + "\n"
            for t, s in shas.items()))

    def early(self, check, sha, **kw):
        """A live run a builder or fixer made, recorded through the real tool."""
        return M.record_early_row(self.root, MOD, ITEM, good_row(check, sha, **kw), by="BENCH")

    def unrun(self, check, sha):
        return M.record_unrun(self.root, MOD, ITEM, check, "run %s" % check, "o", sha, games=["ArchBig: FREE"])


def good_row(check, sha, **kw):
    r = dict({"test": check, "verdict": "PASS", "outcome": "SUCCESS", "game": "ArchSmall", "mod_sha": sha,
              "command": "python3 src/RimMandrake/%s/validation.py %s" % (MOD, check), "evidence": "Transient/x.log",
              "site_checked": True, "site": "the site read clean", "held": []}, **IDENT)
    r.update(kw)
    return r


def flat(text):
    return " ".join(str(text).split())


# the words that make the rule, read by every builder and fixer brief below
RULE_PINS = ("game_lock.py query all", "maturation.py live-row", "small_list.py", "touches",
             "same sitting", "UNRUN", "no game could take", "held each game")
BIND_PINS = ("OWNER hold", "./pipe off game:", "fullscreen", "raid pause")
OLD_WORDS = ("you never run one", "Offline only: no bridge, no game", "Never take the bridge or a game",
             "UNRUN until Stage 6", "records UNRUN for Stage 6", "Its in-game check is Stage 6's")


def builder_brief():
    tr = Tree()
    return flat(M.brief_text(tr.root, MOD)[0])


def fixer_briefs():
    return {"road-back": flat(A.fixer_brief(ITEM, MOD, 15)),
            "version": flat(A.fixer_brief(ITEM, MOD, 15, fix_for="version")),
            "walk": flat(A.fixer_brief(ITEM, MOD, 15, fix_for="walk"))}


def t_the_builder_brief_runs_touched_checks_on_a_free_game():
    b = builder_brief()
    lacks = [p for p in RULE_PINS if p not in b]
    stale = [s for s in OLD_WORDS if s in b]
    return not lacks and not stale, {"lacks": lacks, "stale": stale}


def t_every_fixer_brief_runs_touched_checks_on_a_free_game():
    out = {}
    for k, b in fixer_briefs().items():
        lacks = [p for p in RULE_PINS if p not in b]
        stale = [s for s in OLD_WORDS if s in b]
        if lacks or stale:
            out[k] = {"lacks": lacks, "stale": stale}
    road = flat(A.STAGE6_ROAD)
    if "records UNRUN for Stage 6" in road or "live-row" not in road:
        out["stage6 road"] = road[:400]
    blocked = flat(A.fixer_brief(ITEM, MOD, 15, fix_for="blocked"))
    if "Never take the bridge or a game" in blocked or "free game" not in blocked:   # the Conductor's ruling, 2026-11-25
        out["blocked"] = "keeps the old game ban, or lost the free-game line"
    return not out, out


def t_each_brief_keeps_the_bindings():
    briefs = dict(fixer_briefs(), builder=builder_brief())
    lacks = {k: [p for p in BIND_PINS if p not in b] for k, b in briefs.items()}
    lacks = {k: v for k, v in lacks.items() if v}
    return not lacks, lacks


def t_a_live_row_carries_what_a_visit_row_carries():
    tr = Tree()
    p = os.path.join(tr.root, tr.c(EARLY))
    refused = {}
    for drop in ("test", "verdict", "outcome", "game", "mod_sha", "command", "evidence", "site_checked", "held",
                 "mod_hash", "game_build", "active_mods", "tier"):
        r = good_row("sc_a", tr.c0)
        r.pop(drop)
        try:
            M.record_early_row(tr.root, MOD, ITEM, r)
            refused[drop] = "accepted"
        except ValueError as e:
            refused[drop] = drop in str(e) and "build_match.py identity" in str(e)
    bad = {}
    for k, v in (("test", "sc_not_in_table"), ("verdict", "GREEN"), ("outcome", "FINE"), ("held", "fire"),
                 ("site_checked", "yes")):
        try:
            M.record_early_row(tr.root, MOD, ITEM, good_row("sc_a", tr.c0, **{k: v}))
            bad[k] = "accepted"
        except ValueError as e:
            bad[k] = k in str(e)
    nothing = not os.path.exists(p)
    full = good_row("sc_a", tr.c0)
    full.pop("tier")
    full["full_list"] = True
    ok_full = M.record_early_row(tr.root, MOD, ITEM, full).get("full_list") is True
    return all(v is True for v in refused.values()) and all(v is True for v in bad.values()) and nothing and ok_full, \
        (refused, bad, nothing, ok_full)


def t_a_live_row_belongs_to_the_next_visit():
    got = {}
    tr = Tree()                                                     # never in a visit: visit 1 is next
    got["none yet"] = tr.early("sc_a", tr.c0)
    tr = Tree(moves=[IN_GAME_MOVE, BACK_MOVE])                       # back from visit 1: visit 2 is next
    got["road back"] = tr.early("sc_a", tr.c0)
    tr = Tree(stage="in_game", moves=[IN_GAME_MOVE])                 # visit 1 open, its driver wrote nothing
    got["open, no driver"] = tr.early("sc_a", tr.c0)
    tr.put(tr.c("version/in_game/visit_1/rows.jsonl"), json.dumps({"test": "sc_b", "by": M.LANE_ROWS_BY}) + "\n")
    got["open, lane rows only"] = tr.early("sc_a", tr.c0)
    tr.visit_rows({"sc_b": tr.c0})                                  # its driver has written: the next visit counts it
    got["open, driver wrote"] = tr.early("sc_a", tr.c0)
    want = {"none yet": 1, "road back": 2, "open, no driver": 1, "open, lane rows only": 1, "open, driver wrote": 2}
    seen = {k: r.get("before_visit") for k, r in got.items()}
    stamped = all(r.get("item") == ITEM and r.get("by") == "BENCH" and r.get("at") for r in got.values())
    on_disk = len(M._jsonl(os.path.join(tr.root, tr.c(EARLY)))) == 3
    return seen == want and stamped and on_disk, (seen, stamped, on_disk)


def t_an_early_row_counts_as_a_row_of_its_visit():
    out = {}
    tr = Tree()                                                     # Stage 3: no visit yet
    tt = {"tests": tr.tests}
    tr.early("sc_a", tr.c0)
    tr.early("sc_b", tr.c0)
    out["visit 1 runs only the unrun"] = M.ingame_to_run(tr.root, MOD, 1, tt) == (["sc_c"], ["sc_a", "sc_b"])
    c1 = BM.carried_rows(tr.root, MOD, 1)
    out["carried at visit 1"] = sorted(t for t in c1 if t) == ["sc_a", "sc_b"] and c1["sc_a"].get("_visit") == 1
    out["not carried before visit 1"] = not [t for t in BM.carried_rows(tr.root, MOD, 0) if t]
    out["runs of visit 1"] = [v for v, _ in BM.check_runs(tr.root, MOD, 1).get("sc_a", [])] == [1]
    # visit 1 then failed sc_a; a road-back fixer ran it again, live, before visit 2
    tr2 = Tree(moves=[IN_GAME_MOVE, BACK_MOVE])
    tr2.visit_rows({t: tr2.c0 for t in CHECKS})
    tr2.visit_rows({"sc_a": tr2.c0, "sc_b": tr2.c0, "sc_c": tr2.c0}, verdict="FAIL", outcome="MOD FAILURE")
    tr2.early("sc_a", tr2.c0)
    tr2.early("sc_b", tr2.c0)
    tr2.early("sc_c", tr2.c0, verdict="FAIL", outcome="MOD FAILURE")
    run, counted = M.ingame_to_run(tr2.root, MOD, 2, {"tests": tr2.tests})
    out["visit 2 counts the early passes"] = (run, counted) == (["sc_c"], ["sc_a", "sc_b"])
    out["visit 1's own carry is unchanged"] = BM.carried_rows(tr2.root, MOD, 1)["sc_a"].get("verdict") == "FAIL"
    # the exit of visit 1 reads the early rows of visit 1 as its own rows
    tr3 = Tree(stage="in_game", moves=[IN_GAME_MOVE])
    tr3.early("sc_a", tr3.c0)
    tr3.visit_rows({"sc_b": tr3.c0, "sc_c": tr3.c0})
    tr3.put(tr3.c("version/in_game/visit_1/SUMMARY.md"), "# s\n\n## Exit\n\ningame_rows: {sc_a: pass, sc_b: pass, "
            "sc_c: pass}\nstrange_open: 0\nsavegame: none.rws\nexit_met: true\n")
    ex = M.read_ingame_exit(tr3.root, MOD, 1, {"tests": tr3.tests})
    lines = ex.get("lines") or {}
    # what visit 1 counts is what came before its driver: its early rows, never its own rows (as before this change)
    out["visit 1 plan ignores its own rows"] = M.ingame_to_run(tr3.root, MOD, 1, {"tests": tr3.tests}) == (
        ["sc_b", "sc_c"], ["sc_a"])
    out["exit reads it"] = (lines.get("sc_a") or {}).get("count") == "pass" and \
        "in-game check sc_a has no row in rows.jsonl" not in " ".join(ex.get("why") or [])
    return all(out.values()), out


def t_a_change_the_check_reads_owes_it_again():
    tr = Tree(cs=True)                                              # c1 changes the C# every check reads
    tt = {"tests": tr.tests}
    tr.early("sc_a", tr.c0)                                         # ran before the change
    tr.early("sc_b", tr.c1)                                         # ran on the change
    run, counted = M.ingame_to_run(tr.root, MOD, 1, tt)
    return run == ["sc_a", "sc_c"] and counted == ["sc_b"], (run, counted)


def t_an_early_row_meets_its_unrun_row():
    tr = Tree()
    tr.unrun("sc_a", tr.c1)
    tr.unrun("sc_b", tr.c1)
    tr.early("sc_a", tr.c2)                                         # holds c1: met
    tr.early("sc_b", tr.c0)                                         # before c1: still owed
    owed = sorted(u["check"] for u in M.unrun_owed(tr.root, MOD))
    return owed == ["sc_b"], owed


def t_an_early_failure_holds_as_a_visit_failure():
    tr = Tree(stage="in_game", moves=[IN_GAME_MOVE])
    tt = {"tests": tr.tests}
    tr.early("sc_a", tr.c0, verdict="FAIL", outcome="UNRESOLVED")
    tr.visit_rows({"sc_a": tr.c0, "sc_b": tr.c0, "sc_c": tr.c0})    # a later PASS of visit 1
    runs = BM.check_runs(tr.root, MOD, 1).get("sc_a") or []
    rd = LK.reading(tr.tests["sc_a"], runs)
    held = bool(rd) and rd.get("count") in LK.HOLDS
    tr2 = Tree(moves=[IN_GAME_MOVE, BACK_MOVE])
    tr2.visit_rows({t: tr2.c0 for t in CHECKS})
    tr2.early("sc_b", tr2.c0, verdict="FAIL", outcome="UNRESOLVED")
    listed = "\n".join(M.unclassed_lines(tr2.root, MOD, 2, {"tests": tr2.tests}))
    tr3 = Tree()
    tr3.early("sc_c", tr3.c0, verdict="FAIL", outcome="UNRESOLVED")
    listed1 = "\n".join(M.unclassed_lines(tr3.root, MOD, 1, {"tests": tr3.tests}))
    return held and "`sc_b`" in listed and "`sc_c`" in listed1, (rd, listed, listed1)


def t_an_unrun_row_names_who_held_each_game():
    import game_lock as GL
    tr = Tree()
    real = GL.query_all
    try:
        GL.query_all = lambda pipe=True: [{"game": "a", "line": "ArchBig: HELD by BENCH since 22:17 PST, for: visit 12"},
                                          {"game": "b", "line": "ArchSmall: HELD by BENCH since 23:02 PST, for: scenes"}]
        a = M.record_unrun(tr.root, MOD, ITEM, "sc_a", "run sc_a", "o", tr.c0)
        GL.query_all = lambda pipe=True: 1 / 0
        b = M.record_unrun(tr.root, MOD, ITEM, "sc_b", "run sc_b", "o", tr.c0)
    finally:
        GL.query_all = real
    ga, gb = " | ".join(a.get("games") or []), " | ".join(b.get("games") or [])
    ok = "ArchBig: HELD by BENCH" in ga and "ArchSmall: HELD" in ga and "Steve1" in ga and \
        "could not look" in gb and "ZeroDivisionError" in gb
    return ok, (ga, gb)


def main():
    tests = (t_the_builder_brief_runs_touched_checks_on_a_free_game, t_every_fixer_brief_runs_touched_checks_on_a_free_game,
             t_each_brief_keeps_the_bindings, t_a_live_row_carries_what_a_visit_row_carries,
             t_a_live_row_belongs_to_the_next_visit, t_an_early_row_counts_as_a_row_of_its_visit,
             t_a_change_the_check_reads_owes_it_again, t_an_early_row_meets_its_unrun_row,
             t_an_early_failure_holds_as_a_visit_failure, t_an_unrun_row_names_who_held_each_game)
    bad = 0
    for t in tests:
        try:
            good, got = t()
        except Exception:       # noqa: BLE001
            good, got = False, traceback.format_exc()[-700:]
        print("%s  %s%s" % ("ok   " if good else "FAIL ", t.__name__, "" if good else ": %s" % (got,)))
        bad += not good
    shutil.rmtree(TMP, ignore_errors=True)
    print("%d of %d tests failed" % (bad, len(tests)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
