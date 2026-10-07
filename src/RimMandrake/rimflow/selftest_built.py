#!/usr/bin/env python3
"""Selftest for rimflow redesign step 2: the `built` and `validated` states, the
`implemented` verb, `verify --level/--criterion`, and the acceptance view.

    python3 src/RimMandrake/rimflow/selftest_built.py

UNIT half: `model` / `priority` in process over hand-built event lists. CLI half: the
real `cli.py` as a subprocess against a throwaway ledger (`RIMFLOW_LEDGER`/
`RIMFLOW_ITEMS`) and a git FIXTURE (`RIMFLOW_GITINDEX=<json>`) — the same hatches
selftest_reconcile.py uses — so no case reads this repo's history or writes its ledger.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "cli.py")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TMP_ROOT = os.path.join(REPO, ".rimflow_selftest_built")
sys.path.insert(0, os.path.dirname(HERE))

from rimflow import model, priority, render                     # noqa: E402

PASS, FAIL = [], []
_TMP = {"dir": None}

def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as e:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, e))
    except Exception as e:                                       # noqa: BLE001
        FAIL.append(name)
        print("FAIL  %s\n        unexpected %s: %s" % (name, type(e).__name__, e))


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
IID = "LANCE_TETHER_PULL_1"


def T(n):
    return "2026-10-07T00:00:%02dZ" % n


def sha(n):
    return "%09x" % (0xb20000000 + n) + "%031x" % n


def ev(n, seat, verb, iid=IID, **kw):
    e = {"seat": seat, "event": verb, "ts": T(n)}
    if iid:
        e["id"] = iid
    e.update(kw)
    return e


def filed(seat="FOUNDRY", iid=IID, n=0):
    return [ev(n, seat, "file", iid, **{"for": seat, "title": "t " + iid, "kind": "task"}),
            ev(n + 1, seat, "claim", iid)]


def crit(*pairs):
    return [{"id": c, "level": l, "text": "observe %s" % c} for c, l in pairs]


def impl(n, criteria, seat="FOUNDRY", iid=IID, s=None):
    owed = [c["level"] for c in criteria if c["level"] != "L0"]
    e = ev(n, seat, "implemented", iid, sha=(s or sha(1))[:12], ref="origin/main",
           criteria=criteria)
    if owed:
        e["needs"] = model.needs_for_levels(owed)
    return e


def fresh(name):
    d = os.path.join(TMP_ROOT, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "items"))
    _TMP["dir"] = d
    write_fixture([1, 2])
    return d


def write_fixture(published):
    """Commits `sha(n)` for n in `published` are on the fixture's origin/main."""
    commits = [{"sha": sha(n), "ts": "2099-01-01T00:00:%02dZ" % n,
                "subject": "unrelated commit %d" % n, "body": "",
                "files": ["src/RimMandrake/Mod/X.xml"]} for n in published]
    with open(os.path.join(_TMP["dir"], "gitfixture.json"), "w") as fh:
        json.dump({"ref": "origin/main", "head": "f" * 40, "commits": commits}, fh)


def env(seat="FOUNDRY", fixture=True):
    e = {k: v for k, v in os.environ.items()
         if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_GITINDEX")}
    e["RIMFLOW_LEDGER"] = os.path.join(_TMP["dir"], "events.jsonl")
    e["RIMFLOW_ITEMS"] = os.path.join(_TMP["dir"], "items")
    e["RIMFLOW_PROBE"] = "no-reading"
    e["RIMFLOW_SEAT"] = seat
    e["RIMFLOW_GITINDEX"] = os.path.join(_TMP["dir"], "gitfixture.json") if fixture else "off"
    return e


def run(*args, **kw):
    p = subprocess.Popen([sys.executable, CLI] + list(args), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=REPO,
                         env=env(kw.get("seat", "FOUNDRY"), kw.get("fixture", True)))
    out, err = p.communicate()
    return p.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


def ok(*args, **kw):
    rc, out, err = run(*args, **kw)
    assert rc == 0, "`%s` exited %d\n  stdout: %s\n  stderr: %s" % (
        " ".join(args), rc, out.strip()[-700:], err.strip()[-700:])
    return out


def refused(*args, **kw):
    rc, out, err = run(*args, **kw)
    assert rc != 0, "`%s` should have been refused and exited 0:\n%s" % (" ".join(args), out)
    return err


def ledger_events():
    evs = []
    for root, _d, files in os.walk(_TMP["dir"]):
        for f in sorted(files):
            if f.endswith(".jsonl"):
                with open(os.path.join(root, f), encoding="utf-8") as fh:
                    evs += [json.loads(l) for l in fh if l.strip()]
    return evs


def write_prose(iid, criteria_text):
    with open(os.path.join(_TMP["dir"], "items", "%s.md" % iid), "w") as fh:
        fh.write("# %s\n\n## spec\nbuild it\n\n## criteria\n%s\n" % (iid, criteria_text))


def file_ready(iid=IID, seat="FOUNDRY"):
    ok("file", iid, "--for", seat, "--title", "test item %s" % iid, seat=seat)
    ok("claim", iid, seat=seat)


def state_of(iid=IID):
    return ok("show", iid).splitlines()[0].split()[1]


def criteria_file(text):
    p = os.path.join(_TMP["dir"], "crit.txt")
    with open(p, "w") as fh:
        fh.write(text)
    return p


# ---------------------------------------------------------------------------
# UNIT — model / priority
# ---------------------------------------------------------------------------
def t_levels_ladder_and_needs_derivation():
    assert model.cheapest_level(["L4", "GREEN-FULL", "L2"]) == "L2"
    assert model.needs_for_levels(["L4", "L1"]) == "bridge", "cheapest, not first written"
    assert model.needs_for_levels(["L4"]) == "owner"
    assert model.needs_for_levels(["GREEN-FULL", "L3"]) == "bridge"
    assert model.needs_for_levels(["L0"]) == "offline"
    assert model.needs_for_levels([]) is None
    for lv in model.LEVELS:
        assert lv in model.LEVEL_NEEDS and model.LEVEL_NEEDS[lv] in model.NEEDS, lv


def t_parse_criteria_tags_and_untagged():
    c, u = model.parse_criteria("- O1 L0: compiles\n- A1 L1 defs resolve\n"
                                "* A2 GREEN-FULL — full list green\n1. A3 L4: fun\n"
                                "- just prose, no tag\nplain paragraph line\n")
    assert [(x["id"], x["level"]) for x in c] == [("O1", "L0"), ("A1", "L1"),
                                                   ("A2", "GREEN-FULL"), ("A3", "L4")], c
    assert c[0]["text"] == "compiles", c[0]
    assert u == ["- just prose, no tag"], u
    c, _ = model.parse_criteria("- A1 L10: not a level\n")
    assert not c, "L10 parsed as L1: %r" % c


def t_implemented_enters_built_with_derived_needs():
    w = model.replay(filed() + [impl(2, crit(("O1", "L0"), ("A1", "L1"), ("A4", "L4")))])
    it = w.items[IID]
    assert not w.errors, w.errors
    assert it.state == "built" and it.needs == "bridge", (it.state, it.needs)
    assert it.outstanding == ["A1", "A4"], "L0 is attested, never owed: %r" % it.outstanding
    assert it.level_reached == "L0" and it.built_sha == sha(1)[:12]
    assert it.open, "built is still open work"


def t_implemented_with_nothing_owed_is_done():
    w = model.replay(filed() + [impl(2, crit(("O1", "L0")))])
    it = w.items[IID]
    assert it.state == "done" and it.closed_sha == sha(1)[:12], (it.state, it.closed_sha)
    w = model.replay(filed() + [impl(2, [])])
    assert w.items[IID].state == "done"


def t_implemented_refuses_bad_manifest_and_mismatched_needs():
    base = filed()
    bad = [impl(2, crit(("A1", "L1"))), ]
    bad[0]["needs"] = "offline"
    for e, why in ((bad[0], "needs disagrees with cheapest level"),
                   (dict(impl(2, crit(("A1", "L1"), ("A1", "L2"))), needs="bridge"), "dup id"),
                   (dict(impl(2, []), criteria=[{"id": "A1", "level": "L9"}]), "bad level"),
                   (dict(impl(2, []), criteria="A1 L1"), "not a list"),
                   (dict(impl(2, []), sha="HEAD"), "not a sha")):
        w = model.replay(base + [e])
        assert w.errors and w.items[IID].state == "ready", "%s accepted: %r" % (why, w.errors)
        try:
            model.check(e, model.replay(base))
        except model.LedgerError:
            pass
        else:
            raise AssertionError("check() accepted: %s" % why)


def t_implemented_on_terminal_item_is_refused():
    w = model.replay(filed() + [ev(2, "FOUNDRY", "close", sha="abcdef1")])
    try:
        model.check(impl(3, crit(("A1", "L1"))), w)
    except model.TransitionError:
        return
    raise AssertionError("implemented reopened a closed item")


def t_verify_pass_advances_built_validated_done():
    evs = filed() + [impl(2, crit(("O1", "L0"), ("A1", "L1"), ("A2", "GREEN-FULL"),
                                   ("A4", "L4")))]
    evs.append(ev(3, "FOUNDRY", "verify", result="pass", config="min-13", level="L1",
                  criterion="A1", sha=sha(1)[:12]))
    it = model.replay(evs).items[IID]
    assert it.state == "validated" and it.outstanding == ["A2", "A4"], (it.state, it.outstanding)
    assert it.level_reached == "L1" and it.needs == "bridge", (it.level_reached, it.needs)
    assert it.runs[-1].criterion == "A1" and it.runs[-1].level == "L1"
    evs.append(ev(4, "FOUNDRY", "verify", result="pass", config="full-631",
                  criterion="A2"))
    it = model.replay(evs).items[IID]
    assert it.needs == "owner" and it.next_level() == "L4", (it.needs, it.next_level())
    evs.append(ev(5, "OWNER", "verify", result="pass", config="review", criterion="A4",
                  sha=sha(1)[:12]))
    w = model.replay(evs)
    it = w.items[IID]
    assert not w.errors, w.errors
    assert it.state == "done" and not it.outstanding and it.level_reached == "L4", it
    assert it.closed_sha == sha(1)[:12]


def t_verify_fail_records_but_moves_nothing():
    evs = filed() + [impl(2, crit(("A1", "L1")))]
    evs.append(ev(3, "FOUNDRY", "verify", result="fail", config="min-13", criterion="A1"))
    it = model.replay(evs).items[IID]
    assert it.state == "built" and it.outstanding == ["A1"] and len(it.runs) == 1


def t_verify_refuses_unknown_or_mismatched_criterion():
    base = filed() + [impl(2, crit(("A1", "L1")))]
    w = model.replay(base)
    for e, why in ((ev(3, "FOUNDRY", "verify", result="pass", config="c", criterion="Z9"),
                    "unknown criterion"),
                   (ev(3, "FOUNDRY", "verify", result="pass", config="c", criterion="A1",
                       level="L2"), "level contradicts the tag"),
                   (ev(3, "FOUNDRY", "verify", result="pass", config="c", level="L7"),
                    "bad level")):
        try:
            model.check(e, w)
        except model.LedgerError:
            continue
        raise AssertionError("accepted: %s" % why)
    # a criterion pass against an item that is not built is refused
    w2 = model.replay(filed() + [impl(2, crit(("A1", "L1"))), ev(3, "FOUNDRY", "claim")])
    assert w2.items[IID].state == "ready"
    try:
        model.check(ev(4, "FOUNDRY", "verify", result="pass", config="c", criterion="A1"), w2)
    except model.TransitionError:
        pass
    else:
        raise AssertionError("a pass on an un-built item was accepted")


def t_any_seat_may_pass_a_criterion_on_a_built_item():
    """FOUNDRY owns acceptance (owner, 2026-10-06): it records a pass on BENCH's item."""
    base = filed("BENCH") + [impl(2, crit(("A1", "L1"), ("A4", "L4")), seat="BENCH")]
    w = model.replay(base)
    model.check(ev(3, "FOUNDRY", "verify", result="pass", config="min-13", criterion="A1"), w)
    try:   # without a criterion the owning-seat rule stands
        model.check(ev(3, "FOUNDRY", "verify", result="pass", config="min-13"), w)
    except model.PermissionError_:
        return
    raise AssertionError("a criterion-less run on another seat's item was accepted")


def t_built_items_never_enter_the_implementation_pool():
    evs = filed() + [impl(2, crit(("A1", "L1")))] + filed(iid="OTHER_READY_WORK_1", n=3)
    w = model.replay(evs)
    ids = [i.id for i in priority.rank(w, "FOUNDRY")]
    assert ids == ["OTHER_READY_WORK_1"], ids
    why = " ".join(priority.why_not(w, "FOUNDRY", IID))
    assert "built" in why and "--acceptance" in why, why


def t_acceptance_groups_by_cheapest_level_and_seat():
    evs = (filed() + [impl(2, crit(("A1", "L2"), ("A4", "L4")))]
           + filed("BENCH", "SECOND_BUILT_THING_1", 3)
           + [impl(5, crit(("A1", "GREEN-FULL")), "BENCH", "SECOND_BUILT_THING_1")]
           + filed("BENCH", "THIRD_BUILT_THING_1", 6)
           + [impl(8, crit(("A9", "L4")), "BENCH", "THIRD_BUILT_THING_1")]
           + filed(iid="FOURTH_BUILT_THING_1", n=9)
           + [impl(11, crit(("B1", "L1"), ("B2", "L2")), iid="FOURTH_BUILT_THING_1")])
    w = model.replay(evs)
    g = [(lv, [i.id for i in items]) for lv, items in priority.acceptance(w)]
    assert g == [("L1", ["FOURTH_BUILT_THING_1"]), ("L2", [IID]),
                 ("GREEN-FULL", ["SECOND_BUILT_THING_1"]), ("L4", ["THIRD_BUILT_THING_1"])], g
    f = [lv for lv, _ in priority.acceptance(w, "FOUNDRY")]
    b = [lv for lv, _ in priority.acceptance(w, "BENCH")]
    assert f == ["L1", "L2", "GREEN-FULL"] and b == ["L4"], (f, b)
    text = render.acceptance_view(w, "FOUNDRY")
    assert "GREEN-FULL" in text and "FULL list" in text and IID in text, text


def t_queue_view_has_a_built_section_not_next():
    evs = filed() + [impl(2, crit(("A1", "L1")))]
    w = model.replay(evs)
    ranked, sections = render.view_sections(w, "FOUNDRY")
    assert IID not in {i.id for i in ranked}
    built = [items for title, items, _n, _x in sections if title.startswith("BUILT")]
    assert built and [i.id for i in built[0]] == [IID], sections


def t_reimplement_replaces_manifest_and_forgets_passes():
    evs = filed() + [impl(2, crit(("A1", "L1"), ("A2", "L2")))]
    evs.append(ev(3, "FOUNDRY", "verify", result="pass", config="m", criterion="A1"))
    evs.append(impl(4, crit(("A1", "L1"), ("A3", "L3")), s=sha(2)))
    it = model.replay(evs).items[IID]
    assert it.state == "built" and it.outstanding == ["A1", "A3"], (it.state, it.outstanding)
    assert it.built_sha == sha(2)[:12] and it.level_reached == "L0" and len(it.runs) == 1


def t_unknown_field_on_known_verb_is_tolerated_in_replay_only():
    """Forward compatibility: a future field on an existing verb degrades to the old
    meaning in non-strict replay, and is still refused on the writing path."""
    e = ev(2, "FOUNDRY", "note", text="hi", lease="tok-1")
    w = model.replay(filed() + [e])
    assert not w.errors and w.tolerated == [(2, "note", ["lease"])], (w.errors, w.tolerated)
    try:
        model.check(e, model.replay(filed()))
    except model.UnknownFieldError:
        pass
    else:
        raise AssertionError("the writing path accepted an unknown field")
    w = model.replay(filed() + [ev(2, "FOUNDRY", "frobnicate")])
    assert len(w.errors) == 1, "an unknown VERB must stay an error: %r" % w.errors


# ---------------------------------------------------------------------------
# CLI — every verb end to end against a throwaway ledger
# ---------------------------------------------------------------------------
def t_cli_implemented_from_prose_then_acceptance_then_verify_to_done():
    fresh("full_path")
    file_ready()
    write_prose(IID, "- O1 L0: compiles\n- A1 L1: defs resolve\n- A4 L4: fun to use\n")
    out = ok("implemented", IID, "--sha", sha(1)[:9])
    assert "-> built" in out and "needs bridge" in out, out
    imp = [e for e in ledger_events() if e["event"] == "implemented"]
    assert len(imp) == 1 and imp[0]["needs"] == "bridge" and imp[0]["sha"] == sha(1)[:12], imp
    assert [c["id"] for c in imp[0]["criteria"]] == ["O1", "A1", "A4"], imp
    assert state_of() == "built"
    out = ok("next")
    assert "rimflow start %s" % IID not in out, "built item offered as build work:\n" + out
    acc = ok("next", "--acceptance")
    assert "## L1" in acc and IID in acc and "A1 L1" in acc, acc
    assert IID not in ok("next", "--acceptance", seat="BENCH"), "L1 is FOUNDRY's sitting"
    assert IID in ok("queue", "FOUNDRY", "--acceptance")
    q = ok("queue", "FOUNDRY")
    assert "# BUILT" in q and IID in q.split("# BUILT", 1)[1], q
    out = ok("verify", IID, "--criterion", "A1", "--result", "pass", "--config", "min-13")
    assert "built -> validated" in out, out
    run_ev = [e for e in ledger_events() if e["event"] == "verify"][-1]
    assert run_ev["sha"] == sha(1)[:12] and run_ev["level"] == "L1", run_ev
    assert IID in ok("next", "--acceptance", seat="BENCH"), "L4 is BENCH's sitting"
    out = ok("verify", IID, "--criterion", "A4", "--result", "pass", "--config", "review",
             seat="BENCH")
    assert "validated -> done" in out, out
    assert state_of() == "done"
    assert os.path.exists(os.path.join(_TMP["dir"], "items", "closed", "%s.md" % IID)), \
        "prose was not moved to items/closed/ on the done transition"


def t_cli_implemented_refuses_unpublished_sha():
    fresh("unpublished")
    file_ready()
    write_prose(IID, "- A1 L1: x\n")
    err = refused("implemented", IID, "--sha", sha(7)[:9])
    assert "not an ancestor" in err and "origin/main" in err, err
    assert not [e for e in ledger_events() if e["event"] == "implemented"]


def t_cli_implemented_real_git_fallback_without_index():
    """No index (RIMFLOW_GITINDEX=off): the CLI asks git `merge-base --is-ancestor`. A
    commit on origin/main passes; a fabricated sha is refused."""
    fresh("realgit")
    file_ready()
    real = subprocess.check_output(("git", "rev-parse", "origin/main~1"),
                                   cwd=REPO).decode().strip()
    ok("implemented", IID, "--sha", real[:9], "--none-owed", fixture=False)
    assert state_of() == "done"
    file_ready("SECOND_REAL_THING_1")
    refused("implemented", "SECOND_REAL_THING_1", "--sha", "0badc0de0badc0de", "--none-owed",
            fixture=False)


def t_cli_implemented_refuses_untagged_or_missing_criteria():
    fresh("untagged")
    file_ready()
    write_prose(IID, "- A1 L1: tagged\n- quicktest shows it working\n")
    err = refused("implemented", IID, "--sha", sha(1)[:9])
    assert "no level tag" in err and "quicktest" in err, err
    file_ready("NO_CRITERIA_AT_ALL_1")
    err = refused("implemented", "NO_CRITERIA_AT_ALL_1", "--sha", sha(1)[:9])
    assert "--none-owed" in err, err
    err = refused("implemented", IID, "--sha", sha(1)[:9], "--none-owed",
                  "--criteria-file", criteria_file("A1 L2: owed\n"))
    assert "--none-owed" in err and "A1 L2" in err, err
    assert not [e for e in ledger_events() if e["event"] == "implemented"]


def t_cli_implemented_criteria_file_and_none_owed():
    fresh("critfile")
    file_ready()
    out = ok("implemented", IID, "--sha", sha(2)[:9], "--criteria-file",
             criteria_file("# header comment\nO1 L0: builds\nA1 GREEN-FULL: full list\n"
                           "A2 L4: owner plays it\n"))
    assert "needs bridge" in out and "cheapest GREEN-FULL" in out, out
    file_ready("OFFLINE_ONLY_THING_1")
    out = ok("implemented", "OFFLINE_ONLY_THING_1", "--sha", sha(2)[:9], "--none-owed")
    assert "-> done" in out, out
    err = refused("implemented", "OFFLINE_ONLY_THING_1", "--sha", sha(2)[:9], "--none-owed")
    assert "already" in err or "terminal" in err, err


def t_cli_verify_level_without_criterion_moves_nothing():
    fresh("levelonly")
    file_ready()
    ok("implemented", IID, "--sha", sha(1)[:9], "--criteria-file", criteria_file("A1 L1: x\n"))
    out = ok("verify", IID, "--level", "L1", "--result", "pass", "--config", "min-13")
    assert "drops nothing" in out, out
    assert state_of() == "built"
    err = refused("verify", IID, "--criterion", "Z1", "--result", "pass", "--config", "c")
    assert "no criterion Z1" in err, err


def t_cli_close_unchanged_but_warns_when_criteria_owed():
    fresh("close")
    file_ready()
    ok("close", IID, "--sha", "abcdef1")                     # no manifest: as before
    assert state_of() == "done"
    file_ready("OWES_STILL_THING_1")
    ok("implemented", "OWES_STILL_THING_1", "--sha", sha(1)[:9], "--criteria-file",
       criteria_file("A1 L2: x\n"))
    rc, out, err = run("close", "OWES_STILL_THING_1", "--sha", "abcdef1")
    assert rc == 0 and "OWES A1 L2" in err, (rc, out, err)
    assert state_of("OWES_STILL_THING_1") == "done"


def t_cli_show_prints_the_manifest():
    fresh("show")
    file_ready()
    ok("implemented", IID, "--sha", sha(1)[:9], "--criteria-file",
       criteria_file("A1 L1: x\nA2 L3: art reads right\n"))
    out = ok("show", IID)
    assert "built:" in out and "owes:     A1 L1, A2 L3" in out, out


def t_the_real_ledger_was_never_touched():
    real = model.shard_dir()
    for f in os.listdir(real):
        with open(os.path.join(real, f), encoding="utf-8") as fh:
            for line in fh:
                # IID only: real "implemented" events are legitimate in the real ledger now (the verb shipped), so the old
                # blanket '"event":"implemented"' clause false-positived on genuine work
                if IID in line:
                    raise AssertionError("a test event reached the REAL ledger: %s" % f)


CASES = [v for k, v in sorted(globals().items()) if k.startswith("t_") and callable(v)]


if __name__ == "__main__":
    try:
        for fn in CASES:
            if fn is t_the_real_ledger_was_never_touched:
                continue
            case(fn.__name__, fn)
        case("t_the_real_ledger_was_never_touched", t_the_real_ledger_was_never_touched)
    finally:
        shutil.rmtree(TMP_ROOT, ignore_errors=True)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
