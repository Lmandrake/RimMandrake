#!/usr/bin/env python3
"""Selftest for rimflow/cli.py — the CLI driven end to end, as a subprocess.

    python3 src/RimMandrake/rimflow/selftest_cli.py

⭐ THIS RUNS THE REAL COMMAND, NOT A FUNCTION CALL. Every case shells out to
`python3 .../cli.py <verb> ...` and asserts on the exit code and the bytes that came
back, because the two things most likely to be wrong in a CLI are exactly the two an
in-process call cannot see: **what exit code a refusal returns**, and **whether the
model's own message survived to the terminal**. A refusal that prints a paraphrase and
exits 0 passes any test that only checks a return value.

🔴 THE THROWAWAY LEDGER LIVES UNDER THE REPO, DELIBERATELY.
`/tmp` on this machine is tmpfs — a *different filesystem* from `/mnt/d`, which is 9p.
`selftest_concurrency.py` was first written against `tempfile.mkdtemp()` and passed
3600/3600 while the real repo filesystem was losing 83% of its writes. A green test on
the wrong disk is worse than no test, so this one puts its scratch ledger beside the
code it is testing and deletes it afterwards.

⚠️ `model.read` and `model.append` bind `EVENTS` as a **default argument**, evaluated at
import — so setting `model.EVENTS` alone does NOT redirect them. The CLI honours
`RIMFLOW_LEDGER`/`RIMFLOW_ITEMS` and rebinds those defaults in `_bind_paths()`, and
this test drives it through that env, which is also the proof that the escape hatch
works. Without it, a bug in this file would append to the REAL ledger, which is
append-only and has no undo.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "cli.py")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TMP = os.path.join(REPO, ".rimflow_selftest_cli")      # under the repo, ON 9p, on purpose

PASS, FAIL = [], []


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as e:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, e))
    except Exception as e:
        FAIL.append(name)
        print("FAIL  %s\n        unexpected %s: %s" % (name, type(e).__name__, e))


# ---------------------------------------------------------------------------
def env(seat="BUILD", **over):
    e = {k: v for k, v in os.environ.items()
         if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")}
    e["RIMFLOW_LEDGER"] = os.path.join(TMP, "events.jsonl")
    e["RIMFLOW_ITEMS"] = os.path.join(TMP, "items")
    if seat:
        e["RIMFLOW_SEAT"] = seat
    e.update(over)
    return e


def run(*args, **kw):
    """-> (rc, stdout, stderr). Never raises on a non-zero exit; that is the subject."""
    p = subprocess.Popen([sys.executable, CLI] + list(args),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=kw.get("env") or env(kw.get("seat", "BUILD")), cwd=REPO)
    out, err = p.communicate()
    return p.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


def ok(*args, **kw):
    rc, out, err = run(*args, **kw)
    assert rc == 0, "`%s` exited %d\n  stdout: %s\n  stderr: %s" % (
        " ".join(args), rc, out.strip(), err.strip())
    return out


def refused(args, needle, why, seat="BUILD", env_=None):
    """A refusal must exit NON-ZERO and carry the model's own words to stderr."""
    rc, out, err = run(*args, seat=seat, env=env_)
    assert rc != 0, "NOT REFUSED (exit 0): %s\n  stdout: %s" % (why, out.strip())
    blob = (out + err).lower()
    assert needle.lower() in blob, (
        "refused, but the model's message did not survive to the terminal — it must be "
        "printed VERBATIM, because it is the part that says what to do instead.\n"
        "  wanted %r\n  got: %s" % (needle, (out + err).strip()))
    return err


def prose(iid, spec="do the thing", verify="run it", criteria="it works"):
    d = os.path.join(TMP, "items")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "%s.md" % iid), "w", encoding="utf-8") as fh:
        fh.write("## spec\n%s\n\n## verify\n%s\n\n## criteria\n%s\n"
                 % (spec, verify, criteria))


def fresh():
    """Wipe the throwaway ledger between cases so each one states its own premise."""
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(os.path.join(TMP, "items"), exist_ok=True)


# ---------------------------------------------------------------------------
def t_next_on_an_empty_ledger_still_explains_itself():
    """⭐ 'Nothing to do' is the answer that sends a seat back to hand-reading queues."""
    fresh()
    out = ok("next", "--seat", "BUILD")
    assert "nothing offered for BUILD" in out, out
    assert "owns no open items" in out, (
        "an empty result must say WHY in one line, or the seat goes hunting: %s" % out)
    assert "game DOWN" in out, "the game state is half of why anything is offered: %s" % out


def t_file_claim_start_close():
    fresh()
    out = ok("file", "DESERT_STORM_TUNING_1", "--for", "BUILD",
             "--title", "Tune the sandstorm", "--row", "3")
    assert "filed for BUILD" in out and "proposed" in out, out
    assert "## spec" in out, "filing must name the sections still missing: %s" % out
    prose("DESERT_STORM_TUNING_1")
    assert "-> ready" in ok("claim", "DESERT_STORM_TUNING_1")
    assert "-> doing" in ok("start", "DESERT_STORM_TUNING_1")
    out = ok("close", "DESERT_STORM_TUNING_1", "--sha", "deadbee")
    assert "closed at deadbee" in out, out


def t_close_takes_git_head_when_no_sha_given():
    fresh()
    ok("file", "SHA_FROM_GIT_1", "--for", "BUILD", "--title", "t")
    prose("SHA_FROM_GIT_1")
    ok("claim", "SHA_FROM_GIT_1")
    out = ok("close", "SHA_FROM_GIT_1")
    assert "closed at" in out and len(out.split("closed at ")[1].strip(" .\n")) >= 7, (
        "a close with no commit behind it is a claim, not a close: %s" % out)


def t_cross_seat_close_is_refused_in_the_models_own_words():
    fresh()
    ok("file", "BUILDS_OWN_ITEM_1", "--for", "BUILD", "--title", "t")
    prose("BUILDS_OWN_ITEM_1")
    ok("claim", "BUILDS_OWN_ITEM_1")
    refused(("close", "BUILDS_OWN_ITEM_1", "--sha", "abc1234"), "belongs to",
            "CHECK closed BUILD's item", seat="CHECK")
    refused(("close", "BUILDS_OWN_ITEM_1", "--sha", "abc1234"),
            "Filing work FOR another seat is normal", "the actionable half of the "
            "refusal was dropped", seat="CHECK")


def t_reopening_a_closed_item_is_refused():
    fresh()
    ok("file", "ALREADY_CLOSED_ITEM_1", "--for", "BUILD", "--title", "t")
    prose("ALREADY_CLOSED_ITEM_1")
    ok("claim", "ALREADY_CLOSED_ITEM_1")
    ok("close", "ALREADY_CLOSED_ITEM_1", "--sha", "abc1234")
    refused(("claim", "ALREADY_CLOSED_ITEM_1"), "cannot be reopened",
            "a closed item was reopened, which erases that it ever closed")


def t_incomplete_item_cannot_start_and_the_tool_names_what_is_missing():
    fresh()
    ok("file", "NO_PROSE_ITEM_HERE_1", "--for", "BUILD", "--title", "t")
    ok("claim", "NO_PROSE_ITEM_HERE_1")
    refused(("start", "NO_PROSE_ITEM_HERE_1"), "## spec",
            "an item with no spec/verify/criteria was started")


def t_next_prints_one_item_with_its_spec():
    fresh()
    ok("file", "OFFER_THIS_ONE_1", "--for", "BUILD", "--title", "The offered one",
       "--row", "2")
    ok("file", "LATER_ROW_ITEM_1", "--for", "BUILD", "--title", "Later", "--row", "9")
    prose("OFFER_THIS_ONE_1", spec="SPEC-MARKER")
    prose("LATER_ROW_ITEM_1")
    ok("claim", "OFFER_THIS_ONE_1")
    ok("claim", "LATER_ROW_ITEM_1")
    out = ok("next", "--seat", "BUILD")
    assert out.startswith("OFFER_THIS_ONE_1"), "row 2 must beat row 9: %s" % out
    assert "LATER_ROW_ITEM_1" not in out, "`next` prints ONE item, not a list: %s" % out
    assert "SPEC-MARKER" in out, "next must carry the spec or the seat opens the file anyway"
    assert "-> rimflow start OFFER_THIS_ONE_1" in out, out


def t_why_explains_a_v2_item_as_planning_not_breakage():
    fresh()
    ok("file", "SOMEDAY_ITEM_HERE_1", "--for", "BUILD", "--title", "t",
       "--target-field", "v2")
    prose("SOMEDAY_ITEM_HERE_1")
    ok("claim", "SOMEDAY_ITEM_HERE_1")
    out = ok("why", "SOMEDAY_ITEM_HERE_1")
    assert "targeted at v2" in out, out
    assert "planning decision, not a defect" in out, (
        "a v2 item must not read as broken: %s" % out)
    assert "nothing offered" in ok("next", "--seat", "BUILD")


def t_why_separates_a_closed_window_from_a_defect():
    fresh()
    ok("file", "BRIDGE_WORK_ITEM_1", "--for", "CHECK", "--title", "t", "--needs",
       "bridge")
    prose("BRIDGE_WORK_ITEM_1")
    ok("claim", "BRIDGE_WORK_ITEM_1", seat="CHECK")
    out = ok("why", "BRIDGE_WORK_ITEM_1", seat="CHECK")
    assert "NOT blocked" in out, out
    assert "window is simply closed" in out, out


def t_bridge_is_refused_for_a_non_check_seat():
    fresh()
    refused(("bridge", "take"), "only CHECK takes the bridge",
            "BUILD took the bridge", seat="BUILD")
    refused(("bridge", "take"), "neither can attribute",
            "the reason the rule exists was dropped from the message", seat="BUILD")
    assert "bridge taken by CHECK" in ok("bridge", "take", seat="CHECK")


def t_game_state_is_owner_only():
    fresh()
    refused(("game", "UP"), "only the OWNER announces game state",
            "a seat announced the game state", seat="CHECK")
    assert "game is UP" in ok("game", "UP", seat="OWNER")


def t_an_unresolvable_seat_refuses_rather_than_guessing():
    """🔴 A wrong seat is a permanent lie in a file with no delete."""
    e = env(seat=None)
    refused(("note", "SOME_ITEM_HERE_1", "--text", "x"), "cannot tell which seat I am",
            "the CLI guessed a seat instead of refusing", env_=e)
    refused(("note", "SOME_ITEM_HERE_1", "--text", "x"), "set_agent_window.sh",
            "the refusal did not say how to fix it", env_=e)


def t_show_and_why_still_work_with_no_seat():
    """Debugging the queue is exactly what you do when the window is misconfigured."""
    fresh()
    ok("file", "SHOWABLE_ITEM_HERE_1", "--for", "BUILD", "--title", "t")
    rc, out, err = run("show", "SHOWABLE_ITEM_HERE_1", env=env(seat=None))
    assert rc == 0, "show refused for want of a seat, but it writes nothing: %s" % err
    assert "SHOWABLE_ITEM_HERE_1" in out


def t_show_renders_the_causal_chain_run_finding_spawn():
    """⭐ The R&D path of §4, end to end, through the actual commands."""
    fresh()
    ok("file", "LIVE_CHECK_ITEM_1", "--for", "CHECK", "--title", "t")
    prose("LIVE_CHECK_ITEM_1")
    ok("claim", "LIVE_CHECK_ITEM_1", seat="CHECK")
    out = ok("verify", "LIVE_CHECK_ITEM_1", "--result", "fail", "--config", "full-578",
             "--evidence", "observed/logs/Player_x.log", seat="CHECK")
    assert "LIVE_CHECK_ITEM_1/run-1@full-578" in out and "IMMUTABLE" in out, out
    ok("finding", "--from", "LIVE_CHECK_ITEM_1/run-1@full-578",
       "--name", "BLACKSTAR_SPAWNS_VESSELLESS_1", "--type", "integration",
       "--severity", "high", seat="CHECK")
    ok("spawn", "--from", "BLACKSTAR_SPAWNS_VESSELLESS_1", "--for", "BUILD",
       "--name", "BLACKSTAR_VESSEL_DEF_1", seat="CHECK")
    out = ok("show", "BLACKSTAR_VESSEL_DEF_1")
    assert "caused by BLACKSTAR_SPAWNS_VESSELLESS_1" in out, out
    assert "LIVE_CHECK_ITEM_1/run-1@full-578" in out, (
        "the chain must reach the RUN, or a spawned item reads as somebody's opinion "
        "rather than the consequence of a run on the record: %s" % out)
    # ⚠️ The fail run stands; the source item is NOT reopened.
    src = ok("show", "LIVE_CHECK_ITEM_1")
    assert "run-1@full-578  fail" in src, src


def t_a_failed_run_does_not_reopen_the_item():
    fresh()
    ok("file", "TWICE_RUN_ITEM_1", "--for", "BUILD", "--title", "t")
    prose("TWICE_RUN_ITEM_1")
    ok("claim", "TWICE_RUN_ITEM_1")
    ok("verify", "TWICE_RUN_ITEM_1", "--result", "fail", "--config", "min-13")
    ok("verify", "TWICE_RUN_ITEM_1", "--result", "pass", "--config", "min-13")
    out = ok("show", "TWICE_RUN_ITEM_1")
    assert "run-1@min-13  fail" in out and "run-2@min-13  pass" in out, (
        "a failure must stand forever beside the later pass: %s" % out)


def t_this_deployment_jumps_the_queue_and_clears_when_the_game_goes_down():
    fresh()
    ok("file", "ROW_ONE_ITEM_HERE_1", "--for", "CHECK", "--title", "t", "--row", "1")
    ok("file", "HOST_ITEM_HERE_9", "--for", "CHECK", "--title", "t")
    prose("ROW_ONE_ITEM_HERE_1")
    prose("HOST_ITEM_HERE_9")
    ok("claim", "ROW_ONE_ITEM_HERE_1", seat="CHECK")
    ok("claim", "HOST_ITEM_HERE_9", seat="CHECK")
    ok("game", "UP", seat="OWNER")
    ok("spawn", "--from", "HOST_ITEM_HERE_9", "--for", "CHECK",
       "--name", "URGENT_FOLLOWUP_HERE_9", "--this-deployment", seat="CHECK")
    prose("URGENT_FOLLOWUP_HERE_9")
    ok("claim", "URGENT_FOLLOWUP_HERE_9", seat="CHECK")
    out = ok("next", seat="CHECK")
    assert out.startswith("URGENT_FOLLOWUP_HERE_9"), (
        "the live window is closing and row 1 is not: %s" % out)
    assert "THIS DEPLOYMENT" in out, out
    ok("game", "DOWN", seat="OWNER")
    out = ok("next", seat="CHECK")
    assert out.startswith("ROW_ONE_ITEM_HERE_1"), (
        "--this-deployment leaked past the window into false urgency: %s" % out)


def t_blocked_is_reported_and_the_item_is_withheld():
    fresh()
    ok("file", "WAITING_ON_OWNER_1", "--for", "BUILD", "--title", "t")
    prose("WAITING_ON_OWNER_1")
    ok("claim", "WAITING_ON_OWNER_1")
    ok("block", "WAITING_ON_OWNER_1", "--reason", "needs a ruling", "--on",
       "SOME_DECISION_ITEM_1")
    out = ok("why", "WAITING_ON_OWNER_1")
    assert "BLOCKED: needs a ruling" in out and "SOME_DECISION_ITEM_1" in out, out
    assert "1  BLOCKED" in ok("next", "--seat", "BUILD"), (
        "the empty answer must bucket the reasons, not just say nothing")
    ok("unblock", "WAITING_ON_OWNER_1")
    assert ok("next", "--seat", "BUILD").startswith("WAITING_ON_OWNER_1")


def t_reassign_is_decide_only():
    fresh()
    ok("file", "REASSIGNABLE_ITEM_1", "--for", "BUILD", "--title", "t")
    refused(("reassign", "REASSIGNABLE_ITEM_1", "--to", "CHECK", "--reason", "x"),
            "only DECIDE", "BUILD reassigned its own item", seat="BUILD")
    assert "reassign" in ok("reassign", "REASSIGNABLE_ITEM_1", "--to", "CHECK",
                            "--reason", "x", seat="DECIDE")


def t_sweep_transient_lists_and_never_deletes():
    fresh()
    before = sorted(n for n in os.listdir(REPO) if n.startswith("TRANSIENT_"))
    out = ok("sweep", "--transient")
    after = sorted(n for n in os.listdir(REPO) if n.startswith("TRANSIENT_"))
    assert before == after, (
        "sweep DELETED something. It lists; deciding a file is stale is a judgement "
        "and destroying working notes is not recoverable. before=%r after=%r"
        % (before, after))
    assert "THIS LISTS ONLY" in out, out
    for n in before:
        assert n in out, "%s was not listed: %s" % (n, out)


def t_render_is_delegated_never_reimplemented():
    """⛔ render.py is another agent's file. This CLI must not grow a second renderer.

    ⚠️ This resolves the delegation WITHOUT executing it. `render()` writes into the
    REAL infrastructure/state/derived/ — running it from a selftest would have this
    file quietly rewriting another agent's output as a side effect of being tested,
    which is precisely the shared-tree damage the whole ledger design is about.
    """
    fresh()
    sys.path.insert(0, os.path.dirname(HERE))
    import importlib
    cli = importlib.import_module("rimflow.cli")
    mod = cli._render_module()
    if mod is None:
        refused(("render",), "render.py", "the missing renderer failed opaquely")
        refused(("reindex",), "another agent's file",
                "the refusal did not say whose file it is")
        return
    assert callable(getattr(mod, "main", None)) or callable(getattr(mod, "render", None)), (
        "render.py exists but exposes no entry point this CLI can call")
    # 🔑 The sharper invariant: this CLI opens NO file for writing. Every byte it puts
    # on disk goes through `model.append`, which holds the flock. A renderer would
    # have to write files, so "no write mode anywhere" is what actually keeps the two
    # apart — and it doubles as the guarantee that no CLI verb can tear the ledger.
    src = open(CLI, encoding="utf-8").read()
    for banned in ('"w"', "'w'", '"a"', "'a'", "os.O_WRONLY"):
        assert banned not in src, (
            "cli.py opens a file for writing (%s). Every write must go through "
            "model.append, which holds the lock 9p needs." % banned)


def t_runs_as_a_module_too():
    """`python3 -m rimflow.cli` must work, not only the script path."""
    e = env()
    e["PYTHONPATH"] = os.path.dirname(HERE)
    p = subprocess.Popen([sys.executable, "-m", "rimflow.cli", "next", "--seat", "BUILD"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=e, cwd=REPO)
    out, err = p.communicate()
    assert p.returncode == 0, err.decode()
    assert b"nothing offered" in out, out


def t_the_real_ledger_was_never_touched():
    """🔴 The whole point of RIMFLOW_LEDGER. If this fails, everything above lied."""
    import importlib
    sys.path.insert(0, os.path.dirname(HERE))
    m = importlib.import_module("rimflow.model")
    real = m.EVENTS
    assert not real.startswith(TMP), real
    assert os.path.abspath(real) != os.path.abspath(os.path.join(TMP, "events.jsonl"))
    if os.path.exists(real):
        with open(real, encoding="utf-8") as fh:
            body = fh.read()
        for marker in ("DESERT_STORM_TUNING_1", "BLACKSTAR_VESSEL_DEF_1",
                       "URGENT_FOLLOWUP_HERE_9"):
            assert marker not in body, (
                "%s reached the REAL ledger, which is append-only and has no undo. "
                "The default-argument binding of model.EVENTS is not being honoured."
                % marker)


CASES = [(k[2:], v) for k, v in sorted(globals().items()) if k.startswith("t_")]

if __name__ == "__main__":
    try:
        for name, fn in CASES:
            case(name, fn)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
