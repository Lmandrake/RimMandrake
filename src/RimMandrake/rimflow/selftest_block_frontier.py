#!/usr/bin/env python3
"""Selftest: `block --on X --until built|validated|done` and the block frontier (RIM-1).

    python3 src/RimMandrake/rimflow/selftest_block_frontier.py

What it pins:
  * `until` is folded by replay into `item.blocked_until` and cleared with the flag;
  * the frontier names an item whose blocker reached the asked level, and only then;
  * a DROPPED or SUPERSEDED blocker is named `confirm` and NEVER released;
  * nothing in the frontier lifts a block (the item stays `blocked`, `rank()` still skips it);
  * the CLI refuses a self/cyclic wait and a dead target, warns on an unfiled one, and prints the
    "blocker reached requested level (L)" / "blocker dropped, confirm" lines in `next` and `why`;
  * a default block (`--until done`) is written WITHOUT the field, byte-compatible;
  * the reader as committed BEFORE this change (BASE_REF) replays a ledger carrying `until`
    with zero errors: it strips the field and keeps the block.
Design: design/2026-10-25-rimflow-block-release.md.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "cli.py")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BASE_REF = "8680483545da"         # the last commit before RIM-1: the reader every clone runs today
PKG = "src/RimMandrake/rimflow"
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model, priority                              # noqa: E402

PASS, FAIL = [], []
CTX = {}


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


_N = [0]


def ev(**kw):
    _N[0] += 1
    kw.setdefault("ts", "2026-10-25T00:%02d:%02dZ" % (_N[0] // 60, _N[0] % 60))
    return kw


def filed(iid, for_="FOUNDRY"):
    return ev(seat="BENCH", event="file", id=iid, title="t", kind="task", **{"for": for_})


def world(*extra):
    base = [filed("WAITER_A"), filed("BLOCKER_B"), filed("BLOCKER_C")]
    return model.replay(base + list(extra), strict=True)


def kinds(w, **kw):
    return {(f[0].id, f[1]) for f in priority.block_frontier(w, **kw)}


IMPL = dict(seat="FOUNDRY", event="implemented", id="BLOCKER_B", sha="598dec613",
            ref="origin/main", needs="bridge", criteria=[{"id": "O1", "level": "L0", "text": "x"},
                                         {"id": "A1", "level": "L1", "text": "y"},
                                         {"id": "A4", "level": "L4", "text": "z"}])


# --------------------------------------------------------------------------
def t_until_is_folded_and_cleared():
    w = world(ev(seat="FOUNDRY", event="block", id="WAITER_A", reason="r", on="BLOCKER_B",
                 until="built"))
    a = w.items["WAITER_A"]
    assert a.blocked and a.blocked_on == "BLOCKER_B" and a.blocked_until == "built"
    w = world(ev(seat="FOUNDRY", event="block", id="WAITER_A", reason="r", on="BLOCKER_B",
                 until="built"), ev(seat="FOUNDRY", event="unblock", id="WAITER_A"))
    a = w.items["WAITER_A"]
    assert not a.blocked and a.blocked_on is None and a.blocked_until is None


def t_until_vocabulary_and_on_required():
    for bad, needle in ((dict(until="shipped", on="BLOCKER_B"), "--until must be"),
                        (dict(until="built"), "give --on")):
        try:
            model.validate(ev(seat="FOUNDRY", event="block", id="WAITER_A", reason="r", **bad))
        except model.SchemaError as e:
            assert needle in str(e), e
        else:
            raise AssertionError("accepted %r" % bad)


def t_default_level_is_done():
    blk = ev(seat="FOUNDRY", event="block", id="WAITER_A", reason="r", on="BLOCKER_B")
    w = world(blk, ev(**IMPL))
    assert w.items["BLOCKER_B"].state == "built"
    assert not kinds(w), "a default (done) block must not fire on built"
    w = world(blk, ev(seat="FOUNDRY", event="close", id="BLOCKER_B", sha="598dec613"))
    assert kinds(w) == {("WAITER_A", "satisfied")}


def t_built_level_fires_on_built_and_validated_not_before():
    blk = ev(seat="FOUNDRY", event="block", id="WAITER_A", reason="r", on="BLOCKER_B",
             until="built")
    assert not kinds(world(blk)), "fired while the blocker was still proposed"
    w = world(blk, ev(**IMPL))
    assert kinds(w) == {("WAITER_A", "satisfied")}
    vblk = dict(blk, until="validated", ts="2026-10-25T00:00:59Z")
    w = world(vblk, ev(**IMPL))
    assert not kinds(w), "`until validated` fired on built"
    w = world(vblk, ev(**IMPL), ev(seat="FOUNDRY", event="verify", id="BLOCKER_B",
                                   result="pass", config="min-13", criterion="A1", level="L1"))
    assert w.items["BLOCKER_B"].state == "validated" and kinds(w) == {("WAITER_A", "satisfied")}


def t_dropped_or_superseded_blocker_is_confirm_never_released():
    blk = ev(seat="FOUNDRY", event="block", id="WAITER_A", reason="r", on="BLOCKER_B",
             until="built")
    for end in (ev(seat="FOUNDRY", event="drop", id="BLOCKER_B", reason="no"),
                ev(seat="FOUNDRY", event="supersede", id="BLOCKER_B", by="BLOCKER_C")):
        w = world(blk, end)
        assert kinds(w) == {("WAITER_A", "confirm")}, kinds(w)
        a = w.items["WAITER_A"]
        assert a.blocked, "a dead blocker released its dependent"
        assert a not in priority.rank(w, "FOUNDRY"), "rank() offered a still-blocked item"
        line = priority.frontier_line(*priority.block_frontier(w)[0])
        assert line.startswith("blocker %s, confirm: WAITER_A" % w.items["BLOCKER_B"].state), line
        assert "NOT released" in line, line


def t_satisfied_is_announced_never_applied():
    w = world(ev(seat="FOUNDRY", event="block", id="WAITER_A", reason="r", on="BLOCKER_B"),
              ev(seat="FOUNDRY", event="close", id="BLOCKER_B", sha="598dec613"))
    a = w.items["WAITER_A"]
    assert a.blocked and a not in priority.rank(w, "FOUNDRY")
    line = priority.frontier_line(*priority.block_frontier(w)[0])
    assert line.startswith("blocker reached requested level (done): WAITER_A"), line
    why = "\n".join(priority.why_not(w, "FOUNDRY", "WAITER_A"))
    assert "blocker reached requested level (done): WAITER_A" in why, why


def t_seat_and_closed_dependents_filtered():
    w = world(ev(seat="FOUNDRY", event="block", id="WAITER_A", reason="r", on="BLOCKER_B"),
              ev(seat="FOUNDRY", event="close", id="BLOCKER_B", sha="598dec613"))
    assert not kinds(w, seat="BENCH") and kinds(w, seat="FOUNDRY")
    w = world(ev(seat="FOUNDRY", event="block", id="WAITER_A", reason="r", on="BLOCKER_B"),
              ev(seat="FOUNDRY", event="close", id="BLOCKER_B", sha="598dec613"),
              ev(seat="FOUNDRY", event="close", id="WAITER_A", sha="598dec613"))
    assert not kinds(w), "a closed dependent is not on the frontier"


def t_unfiled_target_is_skipped_by_the_reader():
    w = world(ev(seat="FOUNDRY", event="block", id="WAITER_A", reason="r", on="NEVER_FILED_Z"))
    assert w.items["WAITER_A"].blocked and not kinds(w)


def t_seventh_entry_is_never_hidden_and_kinds_alternate():
    base = [filed("WAITER_%02d" % n) for n in range(9)] + [filed("DEAD_X"), filed("DONE_Y")]
    evs = base + [ev(seat="BENCH", event="drop", id="DEAD_X", reason="no"),
                  ev(seat="BENCH", event="close", id="DONE_Y", sha="598dec613")]
    for n in range(9):
        evs.append(ev(seat="FOUNDRY", event="block", id="WAITER_%02d" % n, reason="r",
                      on="DEAD_X" if n < 7 else "DONE_Y"))
    w = model.replay(evs, strict=True)
    fr = priority.block_frontier(w, seat="FOUNDRY")
    assert len(fr) == 9, len(fr)
    assert [f[1] for f in fr[:4]] == ["confirm", "satisfied", "confirm", "satisfied"], \
        "7 confirms starved the satisfied entries: %r" % [f[1] for f in fr]
    shown = {f[0].id for f in fr[:priority.FRONTIER_FULL]}
    more = priority.frontier_overflow(fr, priority.FRONTIER_FULL)
    for f in fr:
        assert f[0].id in shown or f[0].id in more, "%s hidden: %s" % (f[0].id, more)


def t_frontier_is_current_state_regression_withdraws():
    blk = ev(seat="FOUNDRY", event="block", id="WAITER_A", reason="r", on="BLOCKER_B",
             until="built")
    w = world(blk, ev(**IMPL))
    assert kinds(w)
    w = world(blk, ev(**IMPL), ev(seat="FOUNDRY", event="claim", id="BLOCKER_B"),
              ev(seat="FOUNDRY", event="start", id="BLOCKER_B"))
    assert w.items["BLOCKER_B"].state == "doing", w.items["BLOCKER_B"].state
    assert not kinds(w), "a blocker that regressed still shows as reached"


def t_read_time_diagnostics_flag_merged_cycles_and_unfiled():
    # two clones each wrote one half of a cycle; both events stand, both are flagged
    w = world(ev(seat="FOUNDRY", event="block", id="WAITER_A", reason="r", on="BLOCKER_B"),
              ev(seat="FOUNDRY", event="block", id="BLOCKER_B", reason="r", on="WAITER_A"),
              ev(seat="FOUNDRY", event="block", id="BLOCKER_C", reason="r", on="NEVER_FILED_Z"))
    assert w.items["WAITER_A"].blocked and w.items["BLOCKER_B"].blocked, "an event was refused"
    why = "\n".join(priority.why_not(w, "FOUNDRY", "WAITER_A"))
    assert "wait CYCLE: WAITER_A -> BLOCKER_B -> WAITER_A" in why, why
    why = "\n".join(priority.why_not(w, "FOUNDRY", "BLOCKER_C"))
    assert "never been filed" in why, why


# ---- CLI ------------------------------------------------------------------
def env(seat="FOUNDRY"):
    e = {k: v for k, v in os.environ.items()
         if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")}
    e["RIMFLOW_LEDGER"] = os.path.join(CTX["led"], "events.jsonl")
    e["RIMFLOW_ITEMS"] = os.path.join(CTX["led"], "items")
    e["RIMFLOW_PROBE"] = "no-reading"
    e["RIMFLOW_SEAT"] = seat
    return e


def run(*args, **kw):
    p = subprocess.run([sys.executable, kw.get("cli", CLI)] + list(args), capture_output=True,
                       cwd=REPO, env=env(kw.get("seat", "FOUNDRY")))
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def ok(*args, **kw):
    rc, out, err = run(*args, **kw)
    assert rc == 0, "`%s` exited %d: %s %s" % (" ".join(args), rc, out[-500:], err[-500:])
    return out


def refused(needle, *args):
    rc, out, err = run(*args)
    assert rc != 0, "`%s` was accepted: %s" % (" ".join(args), out[-300:])
    assert needle in out + err, "refused without saying %r: %s %s" % (needle, out, err)


def ledger_events():
    model.EVENTS = os.path.join(CTX["led"], "events.jsonl")
    return model.read()


def setup_cli():
    CTX["root"] = tempfile.mkdtemp(prefix="rimflow_block_frontier_")
    CTX["led"] = os.path.join(CTX["root"], "ledger")
    os.makedirs(os.path.join(CTX["led"], "items"))
    for iid in ("FRONTIER_WAITER_A_PROBE_FIXTURE", "FRONTIER_BLOCKER_B_PROBE_FIXTURE", "FRONTIER_BLOCKER_C_PROBE_FIXTURE", "FRONTIER_WAITER_D_PROBE_FIXTURE"):
        ok("file", iid, "--for", "FOUNDRY", "--title", "t " + iid)


def t_cli_refuses_self_cycle_unfiled_and_dead_targets():
    refused("cycle refused", "block", "FRONTIER_WAITER_A_PROBE_FIXTURE", "--reason", "r", "--on", "FRONTIER_WAITER_A_PROBE_FIXTURE")
    ok("block", "FRONTIER_BLOCKER_B_PROBE_FIXTURE", "--reason", "r", "--on", "FRONTIER_BLOCKER_C_PROBE_FIXTURE")
    ok("block", "FRONTIER_BLOCKER_C_PROBE_FIXTURE", "--reason", "r", "--on", "FRONTIER_WAITER_A_PROBE_FIXTURE")
    refused("cycle refused: FRONTIER_WAITER_A_PROBE_FIXTURE -> FRONTIER_BLOCKER_B_PROBE_FIXTURE -> FRONTIER_BLOCKER_C_PROBE_FIXTURE -> FRONTIER_WAITER_A_PROBE_FIXTURE",
            "block", "FRONTIER_WAITER_A_PROBE_FIXTURE", "--reason", "r", "--on", "FRONTIER_BLOCKER_B_PROBE_FIXTURE")
    ok("unblock", "FRONTIER_BLOCKER_B_PROBE_FIXTURE")
    ok("unblock", "FRONTIER_BLOCKER_C_PROBE_FIXTURE")
    rc, out, err = run("block", "FRONTIER_WAITER_A_PROBE_FIXTURE", "--reason", "r",
                       "--on", "NOPE_NOT_FILED")
    assert rc == 0 and "never been filed" in err, (rc, out, err)   # warned, not refused
    ok("unblock", "FRONTIER_WAITER_A_PROBE_FIXTURE")
    refused("give --on", "block", "FRONTIER_WAITER_A_PROBE_FIXTURE", "--reason", "r", "--until", "built")


def t_cli_default_block_writes_no_until_field():
    ok("block", "FRONTIER_WAITER_A_PROBE_FIXTURE", "--reason", "waits", "--on", "FRONTIER_BLOCKER_B_PROBE_FIXTURE")
    ok("block", "FRONTIER_WAITER_D_PROBE_FIXTURE", "--reason", "waits", "--on", "FRONTIER_BLOCKER_C_PROBE_FIXTURE",
       "--until", "done")
    ok("block", "FRONTIER_WAITER_D_PROBE_FIXTURE", "--reason", "waits built", "--on", "FRONTIER_BLOCKER_C_PROBE_FIXTURE",
       "--until", "built")
    blocks = [e for e in ledger_events() if e.get("event") == "block"]
    assert "until" not in blocks[-3] and "until" not in blocks[-2], blocks[-3:]
    assert blocks[-1].get("until") == "built", blocks[-1]


def t_cli_drop_names_confirm_and_next_repeats_it():
    out = ok("drop", "FRONTIER_BLOCKER_B_PROBE_FIXTURE", "--reason", "abandoned")
    assert "blocker dropped, confirm: FRONTIER_WAITER_A_PROBE_FIXTURE" in out, out
    nxt = ok("next", "--peek")
    assert "blocker dropped, confirm: FRONTIER_WAITER_A_PROBE_FIXTURE" in nxt, nxt
    why = ok("why", "FRONTIER_WAITER_A_PROBE_FIXTURE")
    assert "blocker dropped, confirm: FRONTIER_WAITER_A_PROBE_FIXTURE" in why, why
    model.EVENTS = os.path.join(CTX["led"], "events.jsonl")
    assert model.replay(model.read()).items["FRONTIER_WAITER_A_PROBE_FIXTURE"].blocked, "drop released a dependent"
    # a dead target is WARNED and shown as confirm at once, never refused
    rc, out, err = run("block", "FRONTIER_WAITER_A_PROBE_FIXTURE", "--reason", "r2", "--on",
                       "FRONTIER_BLOCKER_B_PROBE_FIXTURE")
    assert rc == 0 and "will never deliver" in err, (rc, out, err)
    assert "replaces the current block: on FRONTIER_BLOCKER_B_PROBE_FIXTURE (until done)" in out, out
    assert "already ended: blocker dropped, confirm: FRONTIER_WAITER_A_PROBE_FIXTURE" in out, out


def t_cli_close_names_satisfied_and_bench_lists_it():
    out = ok("close", "FRONTIER_BLOCKER_C_PROBE_FIXTURE", "--sha", "598dec613")
    assert "blocker reached requested level (built): FRONTIER_WAITER_D_PROBE_FIXTURE" in out, out
    bench = ok("next", "--bench", seat="BENCH")
    assert "BLOCKERS ENDED" in bench and "blocker reached requested level (built): FRONTIER_WAITER_D_PROBE_FIXTURE" in bench, bench
    assert "blocker dropped, confirm: FRONTIER_WAITER_A_PROBE_FIXTURE" in bench, bench


def t_cli_already_satisfied_typed_cycle_is_accepted():
    """A is built and waits on B; `block B --on A --until built` closes no live loop."""
    a, b = "FRONTIER_TYPED_A_PROBE_FIXTURE", "FRONTIER_TYPED_B_PROBE_FIXTURE"
    ok("file", a, "--for", "FOUNDRY", "--title", "t")
    ok("file", b, "--for", "FOUNDRY", "--title", "t")
    sha = subprocess.check_output(("git", "rev-parse", "origin/main"), cwd=REPO).decode().strip()
    crit = os.path.join(CTX["root"], "crit.txt")
    with open(crit, "w") as fh:
        fh.write("O1 L0: compiles\nA1 L1: defs resolve\n")
    rc, out, err = run("implemented", a, "--sha", sha[:12], "--criteria-file", crit)
    assert rc == 0, (out, err)
    ok("block", a, "--reason", "waits on b", "--on", b)
    out = ok("block", b, "--reason", "waits on a built", "--on", a, "--until", "built")
    assert "already ended: blocker reached requested level (built): %s" % b in out, out
    refused("cycle refused", "block", b, "--reason", "x", "--on", a)   # until done: live loop


def t_cli_seventh_entry_visible_in_next():
    dead = "FRONTIER_SEVEN_DEAD_PROBE_FIXTURE"
    ok("file", dead, "--for", "BENCH", "--title", "t")
    ids = ["FRONTIER_SEVEN_%s_PROBE_FIXTURE" % c for c in "ABCDEFGH"]
    for i in ids:
        ok("file", i, "--for", "BENCH", "--title", "t", seat="BENCH")
        ok("block", i, "--reason", "r", "--on", dead, seat="BENCH")
    ok("drop", dead, "--reason", "abandoned", seat="BENCH")
    nxt = ok("next", "--peek", seat="BENCH")
    for i in ids:
        assert i in nxt, "%s hidden from `next`:\n%s" % (i, nxt)
    bench = ok("next", "--bench", seat="BENCH")
    for i in ids:
        assert i in bench, "%s hidden from `next --bench`" % i


def t_base_reader_tolerates_until():
    """The reader every clone runs today, extracted at BASE_REF, over this ledger."""
    # At repo depth, with Utils linked in: model.py imports rmpaths via parents[3].
    base = os.path.join(CTX["root"], "base")
    dest = os.path.join(base, "src", "RimMandrake", "rimflow")
    os.makedirs(dest)
    os.symlink(os.path.join(REPO, "src", "RimMandrake", "Utils"),
               os.path.join(base, "src", "RimMandrake", "Utils"))
    names = subprocess.check_output(("git", "ls-tree", "--name-only", BASE_REF, PKG + "/"),
                                    cwd=REPO).decode().split()
    for n in names:
        if n.endswith(".py"):
            with open(os.path.join(dest, os.path.basename(n)), "wb") as fh:
                fh.write(subprocess.check_output(("git", "show", "%s:%s" % (BASE_REF, n)),
                                                 cwd=REPO))
    code = ("import json,sys; sys.path.insert(0, %r)\nfrom rimflow import model\n"
            "model.EVENTS = %r\nw = model.replay(model.read())\n"
            "print(json.dumps({'errors': len(w.errors), 'tolerated': w.tolerated,"
            "'d': [w.items['FRONTIER_WAITER_D_PROBE_FIXTURE'].blocked, w.items['FRONTIER_WAITER_D_PROBE_FIXTURE'].blocked_on]}))"
            % (os.path.dirname(dest), os.path.join(CTX["led"], "events.jsonl")))
    p = subprocess.run([sys.executable, "-c", code], capture_output=True)
    assert p.returncode == 0, p.stderr.decode()
    r = json.loads(p.stdout.decode())
    assert r["errors"] == 0, r
    assert r["tolerated"] and all(t[1] == "block" and t[2] == ["until"]
                                  for t in r["tolerated"]), r["tolerated"]
    assert r["d"] == [True, "FRONTIER_BLOCKER_C_PROBE_FIXTURE"], "the base reader lost the block: %r" % r
    ok("why", "FRONTIER_WAITER_D_PROBE_FIXTURE", cli=os.path.join(dest, "cli.py"))


if __name__ == "__main__":
    for name, fn in sorted((k, v) for k, v in globals().items()
                           if k.startswith("t_") and not k.startswith("t_cli")
                           and k != "t_base_reader_tolerates_until"):
        case(name, fn)
    try:
        setup_cli()
        for fn in (t_cli_refuses_self_cycle_unfiled_and_dead_targets,
                   t_cli_default_block_writes_no_until_field,
                   t_cli_drop_names_confirm_and_next_repeats_it,
                   t_cli_close_names_satisfied_and_bench_lists_it,
                   t_cli_already_satisfied_typed_cycle_is_accepted,
                   t_cli_seventh_entry_visible_in_next,
                   t_base_reader_tolerates_until):
            case(fn.__name__, fn)
    finally:
        shutil.rmtree(CTX.get("root", "/nonexistent-rimflow-bf"), ignore_errors=True)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
