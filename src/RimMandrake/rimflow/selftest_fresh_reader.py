#!/usr/bin/env python3
"""selftest_fresh_reader.py: the promises of design/specs/2026-11-26-fresh-reader-ticket/boundary.md (each t_ function
is one promise, by name). Offline: a fixture fix, fake facts for the lane, a fake review record. No real fixing run.
Red on the base: fresh_reader.py absent, no reader rule in fixer_rule.py or the footer.

    python3 src/RimMandrake/rimflow/selftest_fresh_reader.py
"""
import json
import os
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils"), os.path.join(REPO, "src", "RimMandrake")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
os.environ["RM_LIST_DISPATCH_DIR"] = tempfile.mkdtemp(prefix="fr_ld_")
os.environ["RM_WORK_BUNDLE_DIR"] = tempfile.mkdtemp(prefix="fr_wb_")
SHA, PATH, MAKER = "44c696d883", "src/RimMandrake/rimflow/list_effect.py", "rm-detached-bench-a-fix-1795700000"


def FR():
    import fresh_reader
    return fresh_reader


def fixture_ticket():
    """The fixture: the ticket a fixing run files for its fix, as the lane's facts read it."""
    f = FR()
    argv = f.file_argv(SHA, [PATH], MAKER)
    val = {argv[i]: argv[i + 1] for i in range(len(argv) - 1) if argv[i].startswith("--")}
    return argv, {"state": "proposed", "blocked": False, "effect": val["--effect"], "verdict": "fails", "depth": 0,
                  "waits_on": [], "out": "DIRTY %s (never marked clean)" % PATH, "title": val["--title"]}


def t_the_fixing_run_files_one_reader_ticket():
    argv, it = fixture_ticket()
    f = FR()
    assert argv[3] == f.ticket_id(SHA) == "RIMMANDRAKE_READ_FIX_44C696D883_WITH_FRESH_EYES", argv[3]
    assert "--not-now" in argv and argv[argv.index("--not-now") + 1].startswith("independent:"), argv
    assert f.parse_title(it["title"]) == ([PATH], SHA, MAKER), f.parse_title(it["title"])
    assert f.is_reader(it) and not f.is_reader({"title": "Fix the pump"})
    import time_budget
    r = subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), "namecheck", argv[3]], capture_output=True,
                       text=True, timeout=time_budget.CALL_S)
    assert r.returncode == 0, "the ticket name does not parse: %s" % (r.stdout + r.stderr)[-300:]


def t_the_lane_offers_the_reader_ticket():
    import list_dispatch as LD
    _, it = fixture_ticket()
    cfg = {"enabled": True, "max_live": 2, "max_chain_depth": 2, "max_runs_per_item": 2, "max_never_started": 2,
           "sonnet_cap_usd": 5, "opus_cap_usd": 12, "seat": "BENCH"}
    rows, launches = LD.decide(cfg, {"items": {}}, {"items": {"R": it}, "runs": {}, "other_live": 0}, 1_800_000_000.0,
                               account=(True, ""))
    row = {r["item"]: r for r in rows}["R"]
    assert row["decision"] == "launch" and launches, row
    fake = lambda paths: [("CLEAN", p, "design/specs/2026-11-22-list-outcome-checks/boundary.md: promises covered 18 "
                                        "of 18, src/RimMandrake/rimflow/selftest_list_effect.py passes") for p in paths]
    b = LD.brief_text("R", it, row) + FR().brief_block(it, runner=fake)
    assert "FRESH READER" in LD.brief_text("R", it, row), "the lane's brief has no reader part"
    assert "design/specs/2026-11-22-list-outcome-checks/boundary.md" in b and "selftest_list_effect.py" in b, b
    assert "Do NOT read the diff" in b and "You are not %s" % MAKER in b, b
    # a window has no unit: `file` then names the maker "a window" (its default), and the brief still names the files
    wt = {"title": FR().title(SHA, [PATH, "src/b.py"], "a window")}
    assert FR().parse_title(wt["title"]) == ([PATH, "src/b.py"], SHA, "a window"), FR().parse_title(wt["title"])
    wb = FR().brief_block(wt, runner=fake)
    assert PATH in wb and "src/b.py" in wb and "You are not a window" in wb, wb


def t_the_check_holds_on_a_review_record():
    f = FR()
    ok = lambda argv: types.SimpleNamespace(returncode=0, stdout="READ-CLEAN %s" % argv[-1])
    dirty = lambda argv: types.SimpleNamespace(returncode=1, stdout="DIRTY %s (never marked clean)" % argv[-1])
    none = lambda rel: False

    def boom(argv):
        raise subprocess.TimeoutExpired(argv, 1)

    def unreadable(rel):
        raise OSError("flags shard unreadable")
    assert f.holds(SHA, [PATH], ok, none) == 0
    assert f.holds(SHA, [PATH], dirty, none) == 1
    assert f.holds(SHA, [PATH], boom, none) == 2, "a record that cannot be read is could not look, never holds"
    # `check --record` reads DIRTY on a FLAGGED file (selftest_code_review_page_state.py pins it): the flag is read apart
    # (seen 2026-11-27: the reader of c7021894fe flagged RM_SuspensionProofs.cs and the check stayed red)
    assert f.holds(SHA, [PATH], dirty, lambda rel: rel == PATH) == 0, "a FLAGGED file holds though check --record reads DIRTY"
    assert f.holds(SHA, [PATH], dirty, unreadable) == 2, "flags that cannot be read on a DIRTY file: could not look"
    assert f.holds(SHA, [PATH], ok, unreadable) == 0, "a READ-CLEAN record holds without the flags"
    crash = lambda argv: types.SimpleNamespace(returncode=1, stdout="")
    assert f.holds(SHA, [PATH], crash, none) == 2, "a check that printed nothing (rc 1, a crash) is could not look"
    # the real flag reader, on a moved root: a flag counts only on the bytes it was made on
    import code_review_status as CRS
    old_root = CRS.ROOT
    with tempfile.TemporaryDirectory() as tmp:
        try:
            CRS.ROOT = tmp
            os.makedirs(os.path.join(tmp, "src"))
            fp = os.path.join(tmp, "src", "a.cs")
            with open(fp, "w") as fh:
                fh.write("one")
            assert f.flagged_on_bytes(fp) is False, "no flag shard: not flagged"
            os.makedirs(CRS.flag_dir())
            with open(os.path.join(CRS.flag_dir(), "BENCH.jsonl"), "w") as fh:
                fh.write(json.dumps({"event": "flag", "path": "src/a.cs", "why": "w", "ts": "t", "seat": "BENCH",
                                     "sha256": CRS.file_hash("src/a.cs")}) + "\n")
            assert f.flagged_on_bytes(fp) is True, "a flag on the present bytes"
            with open(fp, "w") as fh:
                fh.write("two")
            assert f.flagged_on_bytes(fp) is False, "a flag on older bytes is no record of the present bytes"
            # a file FLAGGED before a later fix changed it: nobody reviews it again (code_review.md: "If you are the
            # reader of a FLAGGED file, stop"), so its reader ticket holds; the weekly examination reads it (seen
            # 2026-11-27: list_dispatch.py, flagged 2026-11-25, changed by 3318e30be0, kept its reader ticket red)
            assert f.flag_kind(fp) == "older", "a flag on older bytes is still a flag (%s)" % f.flag_kind(fp)
            assert f.holds(SHA, [fp], dirty) == 0, "a file flagged before the fix holds: nobody reviews it again"
            os.remove(os.path.join(CRS.flag_dir(), "BENCH.jsonl"))
            assert f.flag_kind(fp) is None and f.holds(SHA, [fp], dirty) == 1, "no flag and DIRTY: does not hold"
        finally:
            CRS.ROOT = old_root


def t_the_rule_is_in_every_brief():
    import fixer_rule
    import detached_helper as DH
    assert fixer_rule.READER_RULE in DH.FOOTER, "the footer every brief gets lacks the reader rule"
    for p in ("CLAUDE.md", "design/RimMandrake/standing_rulings.md"):
        with open(os.path.join(REPO, p), encoding="utf-8") as fh:
            assert fixer_rule.READER_LINE in " ".join(fh.read().split()), "%s lacks the reader line" % p


def t_a_reviewed_file_is_owed_no_reader():
    """A fix to a FLAGGED file (nobody reviews it again) owes no reader: `file` files nothing and says why, and with two
    files only the one with no review record is filed (RIMMANDRAKE_SPARE_CONDUCTOR_PROBE_WAKES_FIVE_IN_ELEVEN_MINUTES:
    the filing gate refused a reader ticket whose check already held on detached_helper.py, FLAGGED, 2026-11-27)."""
    import contextlib
    import io
    f = FR()
    rec = {"a.py": 0, "b.py": 1}
    assert f.owed_paths(SHA, ["a.py", "b.py"], holds_fn=lambda sha, ps: rec[ps[0]]) == ["b.py"]
    real = (f.holds, f.subprocess.run)
    filed = []
    try:
        f.holds = lambda sha, ps, **kw: 0
        f.subprocess.run = lambda argv, **kw: filed.append(argv) or types.SimpleNamespace(returncode=0)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = f.main(["file", "--fix", SHA, PATH])
        assert rc == 0 and filed == [] and "no reader owed" in out.getvalue(), (rc, filed, out.getvalue())
        f.holds = lambda sha, ps, **kw: 0 if ps == [PATH] else 1
        with contextlib.redirect_stdout(io.StringIO()):
            rc = f.main(["file", "--fix", SHA, PATH, "src/b.py"])
        assert rc == 0 and len(filed) == 1 and PATH not in filed[0][filed[0].index("--title") + 1], filed
    finally:
        f.holds, f.subprocess.run = real


def t_a_second_filing_for_one_fix_is_not_a_refusal():
    """A filing for a fix whose reader ticket exists and names each file files nothing, exits 0 and names that ticket;
    a file that no reader ticket of the fix names is filed under a twin id that parses, never the taken id (item
    RIMMANDRAKE_ACCEPT_READER_ALREADY_FILED_HAND_ACT_ALSO_REFUSED: `rimflow file` refused the taken id, exit 2, for
    b553269938 and 5f4a5eaecc, 2026-11-27, and so did the hand act that the bundle's line named)."""
    import contextlib
    import io
    f = FR()
    base = f.ticket_id(SHA)
    assert f.resolve(SHA, [PATH], {}) == (base, [PATH]), "no ticket yet: the fix's own id"
    assert f.resolve(SHA, [PATH], {base: [PATH]}) == (base, []), "the ticket names each file: nothing to file"
    tid, rest = f.resolve(SHA, [PATH, "src/b.py"], {base: [PATH]})
    assert rest == ["src/b.py"] and tid != base and tid.startswith("RIMMANDRAKE_READ_FIX_") and tid.endswith(
        "_WITH_FRESH_EYES"), (tid, rest)
    assert f.resolve(SHA, ["src/b.py"], {base: [PATH], tid: ["src/b.py"]}) == (tid, []), "the twin names it: nothing"
    import time_budget
    r = subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), "namecheck", tid], capture_output=True,
                       text=True, timeout=time_budget.CALL_S)
    assert r.returncode == 0, "the twin id does not parse: %s" % (r.stdout + r.stderr)[-300:]
    real = (f.holds, f.subprocess.run, f.reader_tickets)
    filed = []
    try:
        f.holds = lambda sha, ps, **kw: 1
        f.subprocess.run = lambda argv, **kw: filed.append(argv) or types.SimpleNamespace(returncode=0)
        f.reader_tickets = lambda: {base: [PATH]}
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = f.main(["file", "--fix", SHA, PATH])
        assert rc == 0 and filed == [] and base in out.getvalue(), (rc, filed, out.getvalue())
        with contextlib.redirect_stdout(io.StringIO()):
            rc = f.main(["file", "--fix", SHA, PATH, "src/b.py"])
        assert rc == 0 and len(filed) == 1 and filed[0][3] == tid, filed
        t = filed[0][filed[0].index("--title") + 1]
        assert f.parse_title(t)[0] == ["src/b.py"], t
        # a ledger that cannot be read: the filing goes on under the fix's id (rimflow itself refuses a taken name)
        f.reader_tickets = lambda: 1 / 0
        with contextlib.redirect_stdout(io.StringIO()):
            rc = f.main(["file", "--fix", SHA, PATH])
        assert rc == 0 and len(filed) == 2 and filed[1][3] == base, filed[1:]
    finally:
        f.holds, f.subprocess.run, f.reader_tickets = real


def main():
    failed = 0
    tests = [t_the_fixing_run_files_one_reader_ticket, t_the_lane_offers_the_reader_ticket,
             t_the_check_holds_on_a_review_record, t_the_rule_is_in_every_brief,
             t_a_reviewed_file_is_owed_no_reader, t_a_second_filing_for_one_fix_is_not_a_refusal]
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001 - a promise whose test cannot run is a FAIL, never a crash
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, str(e)[:400]))
    print("FAILED %d of %d" % (failed, len(tests)) if failed else "ALL PASS (%d)" % len(tests))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
