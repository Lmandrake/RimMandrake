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

⚠️ THE ESCAPE HATCH IS `RIMFLOW_LEDGER`/`RIMFLOW_ITEMS`, and this file drives the CLI
through that env — which is also the proof that the hatch works. Without it, a bug in
this file would append to the REAL ledger, which is append-only and has no undo.
`model.read`/`model.append` resolve every path at CALL time (`model.py`'s own header
says why, and `_bind_paths()` sets `model.EVENTS` from that env), so the redirect is
total: the per-seat shards it writes are derived from the ledger in use, never from the
module constant.

🔴 `RIMFLOW_LEDGER` NAMES THE HEAD, AND THE LEDGER IS SEVERAL FILES. `events.jsonl` is
frozen history; every new event lands in `events/<SEAT>.jsonl` beside it. A case that
opens `<tmp>/events.jsonl` directly reads an EMPTY ledger — use `_ledger_text()` /
`_ledger_events()`.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "cli.py")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
# under the repo, ON 9p, on purpose; per process, so a second run cannot delete this run's ledgers
TMP_PARENT = os.path.join(REPO, ".rimflow_selftest_cli")
TMP_ROOT = os.path.join(TMP_PARENT, "run-%d" % os.getpid())

GRANT_FIXTURE = os.path.join(TMP_ROOT, "grant.json")

PASS, FAIL = [], []
_print_lock = threading.Lock()
_tls = threading.local()


def _tmp():
    """This CASE's own scratch dir under TMP_ROOT — never the shared root itself.

    Cases run concurrently, each still driving the CLI as real subprocesses (see this
    file's own header on why that must stay true, never in-process calls).
    PARALLELIZE_SELFTEST_CLI_INTERNAL_1: the 43 cases (each driving one or more real
    `cli.py` subprocess spawns) used to share ONE hardcoded `TMP`, wiped by `fresh()`
    at the top of each case — which made them logically independent already, just
    unable to run at the same time without racing on that one directory. Giving each
    case its own subtree under `TMP_ROOT` is the whole fix; nothing about what a case
    tests, or that it drives the CLI as a subprocess, changes.
    """
    return _tls.dir


def body(out):
    """`next` opens with a `(game …, bridge …)` line. Strip it before matching an ID.

    Added 2026-08-21 when that header was introduced: POLICY.md opened a turn with
    `cli.py game`, which takes a required positional and errors bare, so the state
    question is answered here instead and the turn lost a command.
    """
    return out.split("\n", 1)[1] if out.startswith("(game ") else out


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        msg = "ok    %s" % name
    except AssertionError as e:
        FAIL.append(name)
        msg = "FAIL  %s\n        %s" % (name, e)
    except Exception as e:
        FAIL.append(name)
        msg = "FAIL  %s\n        unexpected %s: %s" % (name, type(e).__name__, e)
    with _print_lock:
        print(msg)


# ---------------------------------------------------------------------------
def env(seat="BUILD", **over):
    e = {k: v for k, v in os.environ.items()
         if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")}
    e["RIMFLOW_LEDGER"] = os.path.join(_tmp(), "events.jsonl")
    e["RIMFLOW_ITEMS"] = os.path.join(_tmp(), "items")
    # The probe reads the REAL machine; without this, any case that stamps a
    # game state is silently "corrected" to whatever the owner's actual game
    # is doing right now (see probe.measure's seam note, 2026-09-04).
    e["RIMFLOW_PROBE"] = "no-reading"
    # The rest of what `next` and the bridge read from the machine: an ambient value here would change a verdict
    # or, for the driver lock, displace a real driver. No schedule file means no seat focus; "" means no lock.
    e["RIMFLOW_SCHEDULE"] = os.path.join(TMP_ROOT, "no_schedule.json")
    e["RIMFLOW_DRIVER_LOCK"] = ""
    e["RIMFLOW_SHARED_BRIDGE"] = ""
    e["RIMFLOW_BRIDGE_LOCK"] = os.path.join(TMP_ROOT, "bridge.lock")
    e["RM_COMPANION_PROFILE"] = GRANT_FIXTURE
    if seat:
        e["RIMFLOW_SEAT"] = seat
    e.update(over)
    return e


def scratch_env(e):
    """Every CLI subprocess goes through this: the ledger it writes is proved scratch BEFORE it can write."""
    for k in ("RIMFLOW_LEDGER", "RIMFLOW_ITEMS"):
        assert (e.get(k) or "").startswith(TMP_ROOT + os.sep), "%s=%r is not scratch" % (k, e.get(k))
    return e


def run(*args, **kw):
    """-> (rc, stdout, stderr). Never raises on a non-zero exit; that is the subject."""
    p = subprocess.Popen([sys.executable, CLI] + list(args),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=scratch_env(kw.get("env") or env(kw.get("seat", "BUILD"))), cwd=REPO)
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
    assert needle.lower() in err.lower(), (
        "refused, but the model's message did not survive to the terminal — it must be "
        "printed VERBATIM, because it is the part that says what to do instead.\n"
        "  wanted %r\n  got: %s" % (needle, (out + err).strip()))
    return err


def prose(iid, spec="do the thing", verify="run it", criteria="it works"):
    d = os.path.join(_tmp(), "items")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "%s.md" % iid), "w", encoding="utf-8") as fh:
        fh.write("## spec\n%s\n\n## verify\n%s\n\n## criteria\n%s\n"
                 % (spec, verify, criteria))


def make_ready(iid, seat="BUILD"):
    """-> put `iid` in plain `ready` (owned, unleased) — the state `rank()` offers.

    🔑 Step 3 (2026-10-07): `claim` no longer lands in `ready`. It takes a lease and
    STARTS the item, because a claimed item used to be re-advertised to every subagent
    (system doc §3.4). The supported CLI route to a plain `ready` item is now the owning
    seat's own `reclaim` (doing -> ready, lease revoked), so ranking tests set up their
    pool that way instead of relying on the old claim -> ready."""
    ok("claim", iid, seat=seat)
    ok("reclaim", iid, seat=seat)


def token_of(out):
    """-> the lease token a `next`/`claim` printed (`… lease token <T>`)."""
    import re as _re
    m = _re.search(r"lease token (\S+)", out)
    assert m, "no lease token printed: %s" % out
    return m.group(1)


def fresh():
    """Wipe this case's own throwaway ledger so each fresh() call states its own
    premise (some cases call it more than once)."""
    d = _tmp()
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "items"), exist_ok=True)


# ---------------------------------------------------------------------------
def t_next_on_an_empty_ledger_still_explains_itself():
    """⭐ 'Nothing to do' is the answer that sends a seat back to hand-reading queues."""
    fresh()
    out = ok("next", "--seat", "FOUNDRY", seat="FOUNDRY")
    assert "nothing offered for FOUNDRY" in out, out
    assert "owns no open items" in out, (
        "an empty result must say WHY in one line, or the seat goes hunting: %s" % out)
    # ⚠️ `next` MEASURES the live machine (probe wins, silently), so this test cannot
    # pin WHICH state — it ran green for days only while the real game happened to be
    # down. What it owes: the state is printed at all.
    assert "(game " in out, "the game state is half of why anything is offered: %s" % out


def t_a_proposed_bridge_item_says_how_to_take_it_too():
    fresh()
    ok("game", "UP", "--owner-said", "game up", seat="OWNER")
    ok("file", "BRIDGE_PROPOSED_HINT_PROBE_FIXTURE", "--for", "CHECK", "--title", "drive the bridge",
       "--needs", "bridge")
    out = ok("next", "--seat", "CHECK", seat="CHECK")
    assert "nothing is CLAIMED" in out and "rimflow bridge take" in out, out


def t_a_proposed_partial_item_goes_the_ranked_way():
    """The claimable branch prints no REMAINING line, so a partial must not take it."""
    import types
    sys.path.insert(0, os.path.dirname(CLI))
    import cli as C
    it = types.SimpleNamespace(id="X", raised=None, needs="offline")
    saved = (C.priority.rank, C.reconcile.guard, C._claimable, C.reconcile.assess)
    try:
        C.priority.rank = lambda *a: []
        C.reconcile.guard = lambda offers, idx: (offers, [])
        C._claimable = lambda *a: [it]
        C.reconcile.assess = lambda c, idx: types.SimpleNamespace(kind="partial", item=c)
        ch = C._choose(None, "BENCH", types.SimpleNamespace(target=None), {"now": 0}, {})
    finally:
        C.priority.rank, C.reconcile.guard, C._claimable, C.reconcile.assess = saved
    assert ch["kind"] == "offer" and ch["offer"].kind == "partial", ch


def t_a_free_bridge_offer_says_how_to_take_it():
    """⭐ A bridge item is now offered while the lock is FREE, so the offer must say how
    to start it. Handing a seat live work with no way to begin is the same stranding."""
    fresh()
    ok("game", "UP", "--owner-said", "game up", seat="OWNER")
    ok("file", "BRIDGE_OFFER_HINT_PROBE_FIXTURE", "--for", "CHECK", "--title", "drive the bridge",
       "--needs", "bridge")
    open(os.path.join(_tmp(), "items", "BRIDGE_OFFER_HINT_PROBE_FIXTURE.md"), "w").write(
        "## spec\nx\n## verify\ny\n## criteria\nz\n")
    make_ready("BRIDGE_OFFER_HINT_PROBE_FIXTURE", seat="CHECK")
    out = ok("next", "--seat", "CHECK", seat="CHECK")
    assert "BRIDGE_OFFER_HINT_PROBE_FIXTURE" in out, (
        "a bridge item was withheld with the bridge FREE — the original defect: %s" % out)
    assert "rimflow bridge take" in out, (
        "offered bridge work without saying how to take the lock: %s" % out)


def t_file_claim_start_close():
    fresh()
    out = ok("file", "DESERT_STORM_TUNING_PROBE_FIXTURE", "--for", "BUILD",
             "--title", "Tune the sandstorm", "--row", "3")
    assert "filed for BUILD" in out and "proposed" in out, out
    assert "## spec" in out, "filing must name the sections still missing: %s" % out
    prose("DESERT_STORM_TUNING_PROBE_FIXTURE")
    # step 3: claim takes a lease AND starts it; a bare `start` still works for scripts
    out = ok("claim", "DESERT_STORM_TUNING_PROBE_FIXTURE")
    assert "-> doing" in out and "lease token" in out, out
    assert "-> doing" in ok("start", "DESERT_STORM_TUNING_PROBE_FIXTURE")
    out = ok("close", "DESERT_STORM_TUNING_PROBE_FIXTURE", "--sha", "deadbee")
    assert "closed at deadbee" in out, out


def _git_fixture():
    """-> (clone_dir, published_sha, local_sha): origin/main holds the first commit, the clone one more."""
    base = os.path.join(_tmp(), "gitfx")
    os.makedirs(base)
    def g(cwd, *a):
        return subprocess.check_output(("git",) + a, cwd=cwd, stderr=subprocess.STDOUT).decode().strip()
    g(base, "init", "-q", "--bare", "-b", "main", "origin.git")
    g(base, "clone", "-q", "origin.git", "clone")
    c = os.path.join(base, "clone")
    for k, v in (("user.name", "t"), ("user.email", "t@t")):
        g(c, "config", k, v)
    open(os.path.join(c, "a"), "w").write("1")
    g(c, "add", "a"); g(c, "commit", "-q", "-m", "one"); g(c, "push", "-q", "origin", "HEAD:main")
    g(c, "fetch", "-q", "origin")
    pub = g(c, "rev-parse", "HEAD")
    open(os.path.join(c, "a"), "w").write("2")
    g(c, "commit", "-q", "-am", "two")
    return c, pub, g(c, "rev-parse", "HEAD")


def t_close_refuses_unpublished_sha_and_head_fallback():
    """CLOSE_SHAS_AUDIT_NAME_NO_COMMIT: publish rebases local commits, so a close citing one cites a ghost."""
    fresh()
    c, pub, loc = _git_fixture()
    e = env("BUILD"); e["RIMFLOW_GIT_CWD"] = c
    ok("file", "GHOST_SHA_CLOSE_PROBE_FIXTURE", "--for", "BUILD", "--title", "t")
    prose("GHOST_SHA_CLOSE_PROBE_FIXTURE")
    ok("claim", "GHOST_SHA_CLOSE_PROBE_FIXTURE")
    rc, out, err = run("close", "GHOST_SHA_CLOSE_PROBE_FIXTURE", "--sha", loc[:10], env=e)
    assert rc != 0 and "Publish FIRST" in (out + err), (rc, out, err)
    rc, out, err = run("close", "GHOST_SHA_CLOSE_PROBE_FIXTURE", env=e)       # HEAD fallback = local commit
    assert rc != 0 and "implicit HEAD" in (out + err), (rc, out, err)
    rc, out, err = run("close", "GHOST_SHA_CLOSE_PROBE_FIXTURE", "--sha", pub[:10], env=e)
    assert rc == 0 and "closed at" in out, (rc, out, err)


def t_close_takes_git_head_when_no_sha_given():
    fresh()
    c, pub, loc = _git_fixture()
    subprocess.check_call(("git", "push", "-q", "origin", "HEAD:main"), cwd=c)
    subprocess.check_call(("git", "fetch", "-q", "origin"), cwd=c)
    e = env("BUILD"); e["RIMFLOW_GIT_CWD"] = c
    ok("file", "SHA_FROM_GIT_PROBE_FIXTURE", "--for", "BUILD", "--title", "t")
    prose("SHA_FROM_GIT_PROBE_FIXTURE")
    ok("claim", "SHA_FROM_GIT_PROBE_FIXTURE")
    out = ok("close", "SHA_FROM_GIT_PROBE_FIXTURE", env=e)
    sha = out.split("closed at ")[1].split()[0].strip(" .")
    assert len(sha) >= 7 and subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=c).decode().strip().startswith(sha), (
        "a close with no commit behind it is a claim, not a close: %s" % out)


def t_replaces_moves_the_parents_prose_like_any_terminal_verb():
    fresh()
    ok("file", "REPLACED_PARENT_PROBE_FIXTURE", "--for", "BUILD", "--title", "t")
    prose("REPLACED_PARENT_PROBE_FIXTURE")
    ok("file", "REPLACING_CHILD_PROBE_FIXTURE", "--for", "BUILD", "--title", "t", "--replaces", "REPLACED_PARENT_PROBE_FIXTURE")
    items = os.path.join(_tmp(), "items")
    assert os.path.isfile(os.path.join(items, "closed", "REPLACED_PARENT_PROBE_FIXTURE.md")) \
        and not os.path.exists(os.path.join(items, "REPLACED_PARENT_PROBE_FIXTURE.md")), "a superseded parent's prose stayed live"


def t_cross_seat_close_lands_and_names_the_ruling_seat():
    """Owner's ruling, 2026-09-19: ANY seat closes an item it has proven dead.

    🔴 This test USED to assert the opposite — that a cross-seat close is refused
    and teaches `--owner-said`. That rule is gone: the seat that can see an item is
    done is routinely not the seat that owns it, and routing the observation to the
    owner meant tickets were simply left open. What the test protects now is the
    other half of his ruling: the close must SAY who ruled it, so the echo and the
    ledger both name the closing seat, not just the owning one.
    """
    fresh()
    ok("file", "BUILDS_OWN_ITEM_PROBE_FIXTURE", "--for", "BUILD", "--title", "t")
    prose("BUILDS_OWN_ITEM_PROBE_FIXTURE")
    ok("claim", "BUILDS_OWN_ITEM_PROBE_FIXTURE")
    out = ok("close", "BUILDS_OWN_ITEM_PROBE_FIXTURE", "--sha", "abc1234",
             "--reason", "shipped at 51e0ceb", seat="CHECK")
    assert "ruled by CHECK (BUILD's item)" in out, (
        "a cross-seat close must name the ruling seat AND the owning seat: %s" % out)
    assert "shipped at 51e0ceb" in out, (
        "the --reason is the ruling; it was dropped from the echo: %s" % out)


def t_reopening_a_closed_item_is_refused():
    fresh()
    ok("file", "ALREADY_CLOSED_ITEM_PROBE_FIXTURE", "--for", "BUILD", "--title", "t")
    prose("ALREADY_CLOSED_ITEM_PROBE_FIXTURE")
    ok("claim", "ALREADY_CLOSED_ITEM_PROBE_FIXTURE")
    ok("close", "ALREADY_CLOSED_ITEM_PROBE_FIXTURE", "--sha", "abc1234")
    refused(("claim", "ALREADY_CLOSED_ITEM_PROBE_FIXTURE"), "cannot be reopened",
            "a closed item was reopened, which erases that it ever closed")


def t_incomplete_item_starts_fine_and_the_tool_does_not_block():
    # 🔴 Owner, 2026-08-21: the completeness gate is removed. Asserting its ABSENCE so
    # that reinstating it fails the suite.
    fresh()
    ok("file", "NO_PROSE_ITEM_HERE_PROBE_FIXTURE", "--for", "BUILD", "--title", "t")
    ok("claim", "NO_PROSE_ITEM_HERE_PROBE_FIXTURE")
    ok("start", "NO_PROSE_ITEM_HERE_PROBE_FIXTURE")


def t_next_prints_one_item_with_its_spec():
    fresh()
    ok("file", "OFFER_THIS_ONE_PROBE_FIXTURE", "--for", "BUILD", "--title", "The offered one",
       "--row", "2")
    ok("file", "LATER_ROW_ITEM_PROBE_FIXTURE", "--for", "BUILD", "--title", "Later", "--row", "9")
    prose("OFFER_THIS_ONE_PROBE_FIXTURE", spec="SPEC-MARKER")
    prose("LATER_ROW_ITEM_PROBE_FIXTURE")
    make_ready("OFFER_THIS_ONE_PROBE_FIXTURE")
    make_ready("LATER_ROW_ITEM_PROBE_FIXTURE")
    out = ok("next", "--seat", "BUILD")
    assert body(out).startswith("OFFER_THIS_ONE_PROBE_FIXTURE"), "row 2 must beat row 9: %s" % out
    assert "LATER_ROW_ITEM_PROBE_FIXTURE" not in out, "`next` prints ONE item, not a list: %s" % out
    assert "SPEC-MARKER" in out, "next must carry the spec or the seat opens the file anyway"
    assert "-> rimflow claim OFFER_THIS_ONE_PROBE_FIXTURE --token " in out, out


def t_next_offers_unclaimed_spec_complete_work_instead_of_nothing():
    """🔴 The DECIDE->BUILD handoff used to end silently here.

    `priority.rank()` filters `state == "ready"`, an item filed FOR a seat lands in
    `proposed`, and POLICY tells a seat its turn is three commands ending in `next`.
    So a fully specced item was unreachable by the only command anyone runs. Measured
    2026-08-21: BUILD held 21 proposed, 18 spec-complete, while `next` offered 3.
    """
    fresh()
    ok("file", "HANDED_TO_BUILD_PROBE_FIXTURE", "--for", "BUILD", "--title", "Specced by someone else")
    prose("HANDED_TO_BUILD_PROBE_FIXTURE", spec="HANDOFF-MARKER")
    out = ok("next", "--seat", "BUILD")
    assert "nothing offered" not in out, (
        "a spec-complete unclaimed item must not read as nothing to do: %s" % out)
    assert "HANDED_TO_BUILD_PROBE_FIXTURE" in out, out
    assert "rimflow claim HANDED_TO_BUILD_PROBE_FIXTURE" in out, (
        "the answer must name the verb that unblocks it: %s" % out)


def t_a_thin_proposal_is_OFFERED_and_says_what_is_thin():
    """🔴 THE COMPLETENESS GATE IS GONE FROM THE OFFER PATH TOO — owner, 2026-08-22.

    This test used to assert the opposite: *"an item nobody can work must NOT be offered
    as claimable."* The owner removed the completeness gate on 2026-08-21; the removal
    reached `claim` and `start` and never reached the offer path, where `_claimable()`
    still filtered on `model._complete()`. So a thin item was not refused, it was
    INVISIBLE, and `next` blamed whoever filed it — *"whoever filed them owes the prose;
    until then nobody can work them."* Three of BUILD's open items were starved that way.

    🔑 The replacement is an information duty, and BOTH halves are the contract: the
    item is offered, AND the seat is told what was left unsaid so it knows what it is
    walking into. Asserting only the first half would let the warning rot away.
    """
    fresh()
    ok("file", "NO_PROSE_HANDOFF_PROBE_FIXTURE", "--for", "BUILD", "--title", "t")
    out = ok("next", "--seat", "BUILD")
    assert "NO_PROSE_HANDOFF_PROBE_FIXTURE" in out and "waiting for BUILD to claim" in out, (
        "a thin item must be OFFERED, not hidden: %s" % out)
    assert "THIN ITEM" in out and "## spec" in out, (
        "offered, but the seat must be told what is missing: %s" % out)
    assert "cannot be claimed" not in out and "owes the prose" not in out, (
        "the removed gate's wording came back: %s" % out)
    # ...and it must actually be claimable, not merely advertised as such. Step 3:
    # `next` RESERVED it, so the claim carries the token it printed.
    assert "-> doing" in ok("claim", "NO_PROSE_HANDOFF_PROBE_FIXTURE", "--token", token_of(out))


def t_an_empty_target_offers_every_target_like_rank_does():
    """`--target ""` means "no target filter" in `priority.rank()` (`if target and ...`).
    `_claimable()` once filtered `i.target in (None, target)` with no such guard, so an
    empty target HID every v1 and v2 proposal from the offer path while `rank()` showed
    the claimed ones: the two halves of `next` disagreed about what "" means."""
    fresh()
    ok("file", "EMPTY_TARGET_VONE_PROBE_FIXTURE", "--for", "BUILD", "--title", "t",
       "--target-field", "v1")
    ok("file", "EMPTY_TARGET_VTWO_PROBE_FIXTURE", "--for", "BUILD", "--title", "t",
       "--target-field", "v2")
    out = ok("next", "--seat", "BUILD", "--target", "")
    # 🔴 NOT a bare id check: the "nothing offered ... N open items" diagnostic names
    # hidden items too, so an id-in-output assertion passed on the broken code.
    assert "2 items waiting for BUILD to claim" in out and "nothing offered" not in out, (
        "an empty --target must OFFER proposals of every target: %s" % out)
    # the default filter still holds: v1 offered, v2 not
    fresh()
    ok("file", "EMPTY_TARGET_VONE_PROBE_FIXTURE", "--for", "BUILD", "--title", "t",
       "--target-field", "v1")
    ok("file", "EMPTY_TARGET_VTWO_PROBE_FIXTURE", "--for", "BUILD", "--title", "t",
       "--target-field", "v2")
    out = ok("next", "--seat", "BUILD")
    assert "1 item waiting for BUILD to claim" in out, out
    assert "EMPTY_TARGET_VTWO_PROBE_FIXTURE" not in out, (
        "the default v1 target must still withhold a v2 proposal: %s" % out)


def t_why_explains_a_v2_item_as_planning_not_breakage():
    fresh()
    ok("file", "SOMEDAY_ITEM_HERE_PROBE_FIXTURE", "--for", "BUILD", "--title", "t",
       "--target-field", "v2")
    prose("SOMEDAY_ITEM_HERE_PROBE_FIXTURE")    # left unclaimed: a lease would withhold it whatever the v2 filter did
    out = ok("why", "SOMEDAY_ITEM_HERE_PROBE_FIXTURE")
    assert "targeted at v2" in out, out
    assert "planning decision, not a defect" in out, (
        "a v2 item must not read as broken: %s" % out)
    assert "nothing offered" in ok("next", "--seat", "BUILD")


def t_why_separates_a_closed_window_from_a_defect():
    fresh()
    ok("file", "BRIDGE_WORK_ITEM_PROBE_FIXTURE", "--for", "CHECK", "--title", "t", "--needs",
       "bridge")
    prose("BRIDGE_WORK_ITEM_PROBE_FIXTURE")
    ok("claim", "BRIDGE_WORK_ITEM_PROBE_FIXTURE", seat="CHECK")
    out = ok("why", "BRIDGE_WORK_ITEM_PROBE_FIXTURE", seat="CHECK")
    assert "NOT blocked" in out, out
    assert "window is simply closed" in out, out


def t_bridge_is_refused_for_a_non_window_seat():
    fresh()
    refused(("bridge", "take"), "only a live window",
            "BUILD took the bridge", seat="BUILD")
    refused(("bridge", "take"), "neither can attribute",
            "the reason the rule exists was dropped from the message", seat="BUILD")
    assert "bridge taken by CHECK" in ok("bridge", "take", seat="CHECK")


def t_every_path_cli_writes_binds_to_scratch():
    """scratch_env checks strings; this asks the CLI itself where its writes land. The ledger audit can only see fixture names."""
    fresh()
    code = ("import sys, json; sys.path.insert(0, %r); import cli; cli._bind_paths(); m = cli.model; "
            "print(json.dumps([m.EVENTS, m.ITEMS, m.CLOSED] + list(m.ledger_files())))" % HERE)
    got = json.loads(subprocess.check_output([sys.executable, "-c", code], env=scratch_env(env("BUILD")), cwd=REPO).decode())
    bad = [p for p in got if not os.path.abspath(p).startswith(os.path.abspath(_tmp()))]
    assert len(got) >= 3 and not bad, "the CLI would write outside the scratch: %s" % bad


def t_a_refused_bridge_take_leaves_the_driver_lock_alone():
    fresh()
    dl = os.path.join(_tmp(), "driver.lock")
    refused(("bridge", "take", "--force", "--for", "x"), "only a live window", "BUILD took the bridge", seat="BUILD",
            env_=env("BUILD", RIMFLOW_DRIVER_LOCK=dl))
    assert not os.path.exists(dl), "a seat the ledger refuses wrote the driver lock"
    ok("bridge", "take", "--for", "x", env=env("CHECK", RIMFLOW_DRIVER_LOCK=dl))
    assert os.path.exists(dl), "the probe is blind: a good take wrote no lock at this path"


def _ledger_paths():
    """-> every file the throwaway ledger is spread across, head first then shards.

    🔴 THE LEDGER IS SEVERAL FILES since 2026-09-23. `RIMFLOW_LEDGER` names the HEAD
    (`events.jsonl`, frozen history), and `rimflow` appends every new event to
    `events/<SEAT>.jsonl` beside it, so two seats can never conflict in one
    git-tracked file. A case that opens the head alone reads an EMPTY ledger and its
    assertion passes or fails for the wrong reason — which is exactly what SEVEN of
    these cases did the moment the sharding landed (measured, not estimated).
    """
    paths = [os.path.join(_tmp(), "events.jsonl")]
    d = os.path.join(_tmp(), "events")
    try:
        paths += [os.path.join(d, n) for n in sorted(os.listdir(d))
                  if n.endswith(".jsonl")]
    except OSError:
        pass
    return [x for x in paths if os.path.exists(x)]


def _ledger_text():
    """-> the raw bytes of the whole throwaway ledger, for `"…" in led` assertions."""
    out = []
    for f in _ledger_paths():
        with open(f, encoding="utf-8") as fh:
            out.append(fh.read())
    return "".join(out)


def _ledger_events():
    """-> every event in the throwaway ledger, ts-ordered. Missing ledger -> []."""
    import json
    out = []
    for f in _ledger_paths():
        with open(f, encoding="utf-8") as fh:
            out += [json.loads(l) for l in fh if l.strip()]
    # (ts, tsn): the reader's own order since 2026-10-02 (model.canonical_order) — a
    # ts-only stable sort fell back to FILE order, which union-merged shards lack.
    out.sort(key=lambda e: (str(e.get("ts") or ""), e.get("tsn") or 0))
    return out


def _bridge_events():
    """Every bridge event in the throwaway ledger, oldest first.

    ⚠️ A ledger that does not exist yet is EMPTY, not an error — the file is created
    by the first append, so a case that asserts "nothing was written" has no file to
    read. Raising there made a passing assertion look like a broken test.
    """
    return [e for e in _ledger_events() if e.get("event") == "bridge"]


def _mirror_holder():
    """Who the BRIDGE mirror names, or None for FREE. The file is beside the ledger."""
    p = os.path.join(_tmp(), "BRIDGE")
    if not os.path.exists(p):
        return None
    for line in open(p, encoding="utf-8"):
        if line.startswith("HELD"):
            return line.split()[1]
        if line.startswith("FREE"):
            return None
    return None


def _ledger_holder():
    evs = _bridge_events()
    if not evs:
        return None
    last = evs[-1]
    return last["seat"] if last.get("state") == "taken" else None


def t_the_bridge_mirror_never_disagrees_with_the_ledger_under_concurrent_takes():
    """🔴 BRIDGE_TAKE_TOCTOU_AND_EPOCH_SENTINEL_1. Every branch used to mirror the holder
    it had just DECIDED on, so a take that lost a race appended its event (harmless —
    the ledger's last event wins) and then wrote its own name into the one line both
    windows read at a glance. `bridge who` re-derived correctly, but only for someone
    who already doubted the answer.

    ⭐ ASSERTS THE INVARIANT, NOT THE RACE. Which window wins is timing, and a test that
    demanded a particular winner would be flaky for the wrong reason. What must hold
    every time, whoever wins, is that the mirror says what the ledger says.

    🔑 It also asserts NOBODY IS LEFT AT A DEAD END: this system errs toward allowing a
    take (owner, 2026-09-02). A loser may be refused — that is the same answer a live
    holder always gets — but the refusal must hand over `--force`, never just "no".
    """
    # ⭐ THE `--force` ARM IS THE ONE THAT PROVES IT. A plain take re-derives the holder
    # just before writing and usually backs off, so the plain arm rarely reaches the
    # code this case exists to cover; `--force` skips that re-check by design, so both
    # windows always append and one always loses — measured 15/15, and pre-fix each of
    # those 15 wrote the LOSER's own name into the mirror.
    for forced in (True, True, False, False, False, False):
        fresh()
        argv = ["bridge", "take"] + (["--force"] if forced else [])
        procs = [subprocess.Popen(
            [sys.executable, CLI] + argv + ["--for", "race %s" % s],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=scratch_env(env(s)), cwd=REPO)
            for s in ("BENCH", "FOUNDRY")]
        outs = [p.communicate() for p in procs]
        for p, (o, e) in zip(procs, outs):
            blob = o.decode("utf-8", "replace") + e.decode("utf-8", "replace")
            assert p.returncode == 0 or "--force" in blob, (
                "a racing take was refused with no way through — mutual lockout is the "
                "expensive failure here, not two drivers: %s" % blob)
        assert _mirror_holder() == _ledger_holder(), (
            "the BRIDGE mirror says %r and the ledger's last event says %r — the one "
            "glanceable line is exactly the thing that must not lie"
            % (_mirror_holder(), _ledger_holder()))


def t_one_malformed_timestamp_cannot_promote_an_item():
    """🔴 BRIDGE_TAKE_TOCTOU_AND_EPOCH_SENTINEL_1, half two. `_epoch` answers 0.0 for an
    unreadable stamp, which is 1970 — so a single bad `ts` anywhere in the ledger read
    as an age of ~495,000 h and forced a distress score, silently reordering the queue
    with nothing on screen to say why. An unreadable stamp is NO EVIDENCE, not evidence
    of enormous age."""
    import json
    fresh()
    prose("MALFORMED_TS_PROBE_PROBE_FIXTURE")
    # needs=deploy scores 1: the +2 of a bad "claimed long ago" age is what would cross the line of 3
    ok("file", "MALFORMED_TS_PROBE_PROBE_FIXTURE", "--for", "BENCH", "--title", "probe",
       "--needs", "deploy", "--kind", "task")
    ok("claim", "MALFORMED_TS_PROBE_PROBE_FIXTURE", seat="BENCH")
    ok("start", "MALFORMED_TS_PROBE_PROBE_FIXTURE", seat="BENCH")
    before = ok("next", "--bench", seat="BENCH")
    assert "MALFORMED_TS_PROBE_PROBE_FIXTURE" not in before.split("IN TROUBLE")[1].split("NEEDS HIM")[0], (
        "the premise is broken: a just-claimed item already scores ≥3, so this case "
        "cannot show the bad stamp doing anything:\n%s" % before)

    # ⚠️ The corruption has to be written back into the file the event ACTUALLY lives
    # in, which since the sharding is `events/<SEAT>.jsonl`, not the frozen head.
    hit = 0
    for p in _ledger_paths():
        lines = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
        touched = False
        for e in lines:
            if e.get("verb") in ("claim", "start") or e.get("event") in ("claim", "start"):
                e["ts"] = "not-a-timestamp"
                hit += 1
                touched = True
        if touched:
            with open(p, "w", encoding="utf-8") as fh:
                for e in lines:
                    fh.write(json.dumps(e) + "\n")
    assert hit, ("no claim event to corrupt — the ledger shape changed: %s"
                 % _ledger_events())

    after = ok("next", "--bench", seat="BENCH")
    trouble = after.split("IN TROUBLE")[1].split("NEEDS HIM")[0]
    assert "MALFORMED_TS_PROBE_PROBE_FIXTURE" not in trouble, (
        "one unreadable timestamp promoted an item into IN TROUBLE:\n%s" % trouble)
    assert "495" not in trouble and "1970" not in trouble, (
        "a 1970 sentinel reached the reasons a seat reads:\n%s" % trouble)


def t_a_stray_target_on_bridge_take_is_an_error_not_a_no_op():
    """⭐ `bridge take BOGUS` used to exit 0 and discard the word (argparse accepts the
    `give`-only positional for every action). A typo that prints success is worse than
    one that fails."""
    fresh()
    refused(("bridge", "take", "BOGUS", "--for", "x"), "takes no target",
            "a stray target was silently swallowed by `bridge take`", seat="BENCH")
    refused(("bridge", "release", "BENCH"), "takes no target",
            "a stray target was silently swallowed by `bridge release`", seat="BENCH")


def t_an_owner_give_and_a_forced_take_are_attributable_from_the_ledger_alone():
    """🔴 BRIDGE_OVERRIDE_ATTRIBUTION_GAP_1. `events.jsonl` is this system's sole source
    of truth, and both of these used to produce a line byte-identical to an ordinary
    uncontested take — the real story lived only in the BRIDGE mirror, which the very
    next bridge call overwrites. The question that must be answerable a year later is
    'was this normal, or did someone cross a live holder, and who'."""
    fresh()
    ok("bridge", "take", "--for", "foundry work", seat="FOUNDRY")
    ok("bridge", "take", "--force", "--for", "bench work", seat="BENCH")
    ok("bridge", "give", "FOUNDRY", "--seat", "OWNER", "--for", "handover", seat=None)
    ok("bridge", "give", "free", "--seat", "OWNER", seat=None)
    evs = _bridge_events()
    assert len(evs) == 4, evs

    # ⚠️ EACH EVENT IS FOUND BY WHAT IT SAYS, NOT BY ITS INDEX. All four land in the
    # same second, and since the ledger was sharded by seat their relative order across
    # two shards is resolved by a deterministic tie-break, not by who wrote first —
    # `model.read()`'s docstring has the reasoning. That never mattered to this case:
    # the claim under test is that each KIND of bridge event is attributable FROM THE
    # EVENT, which is precisely the property an index-based assertion could not see.
    def one(**want):
        hits = [e for e in evs if all(e.get(k) == v for k, v in want.items())]
        assert len(hits) == 1, "expected exactly one %r in %r" % (want, evs)
        return hits[0]

    uncontested = one(state="taken", purpose="foundry work")
    forced = one(state="taken", purpose="bench work")
    handover = one(state="taken", purpose="handover")
    clear = one(state="released")
    assert uncontested.get("override") is None, (
        "an uncontested take must stay unmarked, or the marking means nothing: %s"
        % uncontested)
    assert "--force" in (forced.get("override") or "") and \
        "FOUNDRY" in forced["override"], (
            "a forced take across a live holder is invisible in the ledger: %s" % forced)
    assert "OWNER" in (handover.get("override") or ""), (
        "an owner handover reads as the target window taking it itself: %s" % handover)
    assert handover["seat"] == "FOUNDRY", (
        "the holder must still be the target window — `_apply` reads `seat`: %s" % handover)
    assert "OWNER" in (clear.get("override") or ""), (
        "an owner clear reads as the holder releasing it itself: %s" % clear)


def t_a_window_cannot_forge_the_owners_name_with_bridge_give():
    """🔴 THE WORST BUG THIS FILE GUARDS. `give` emits under the TARGET seat so the
    holder records correctly — which means `model._may` sees BENCH/FOUNDRY and never
    fires, so this branch had NO permission check at all. Any window could write
    "the OWNER handed the bridge to X" into an append-only ledger, bypassing staleness
    and --force on the way. Stamping `override` (2026-09-02) made the forgery durable
    by putting a false claim in the one field treated as evidence of a deliberate
    crossing. Found in review the same day; this is the regression lock."""
    fresh()
    refused(("bridge", "give", "FOUNDRY"), "is the OWNER's switch",
            "a window forged an owner handover", seat="FOUNDRY")
    refused(("bridge", "give", "free"), "is the OWNER's switch",
            "a window forged an owner clear", seat="BENCH")
    assert not _bridge_events(), (
        "a refused give still wrote to the ledger — the append-only file has no undo")
    # and the owner's own switch must still work, or `./bridge` is broken
    ok("bridge", "give", "FOUNDRY", "--seat", "OWNER", "--for", "handover", seat=None)
    evs = _bridge_events()
    assert len(evs) == 1 and evs[0]["seat"] == "FOUNDRY", evs
    assert "OWNER" in (evs[0].get("override") or ""), evs[0]


def t_releasing_a_bridge_you_do_not_hold_is_allowed_but_recorded():
    """⭐ Freeing someone else's lock stays ALLOWED — this system errs toward clearing a
    wedged bridge, never toward mutual lockout. What was wrong is that it happened with
    nothing on the event to say a boundary had been crossed."""
    fresh()
    ok("bridge", "take", "--for", "foundry work", seat="FOUNDRY")
    ok("bridge", "release", seat="BENCH")
    # ⚠️ BY STATE, NOT BY INDEX: the take and the release land in the same second in two
    # different seats' shards, so `[-1]` no longer means "the one written last".
    # See the same note in `t_an_owner_give_and_a_forced_take_are_attributable…`.
    evs = _bridge_events()
    rel = [e for e in evs if e["state"] == "released"]
    assert len(rel) == 1 and rel[0]["seat"] == "BENCH", evs
    assert "FOUNDRY" in (rel[0].get("override") or ""), (
        "BENCH cleared FOUNDRY's lock and the event does not say so: %s" % rel[0])
    # releasing your OWN lock is ordinary and must stay unmarked
    fresh()
    ok("bridge", "take", "--for", "mine", seat="BENCH")
    ok("bridge", "release", seat="BENCH")
    mine = [e for e in _bridge_events() if e["state"] == "released"]
    assert len(mine) == 1 and mine[0].get("override") is None, mine


def t_game_state_is_owner_only():
    fresh()
    refused(("game", "UP"), "only the OWNER announces game state",
            "a seat announced the game state", seat="CHECK")
    assert "game is UP" in ok("game", "UP", seat="OWNER")


def t_an_unresolvable_seat_refuses_rather_than_guessing():
    """🔴 A wrong seat is a permanent lie in a file with no delete."""
    e = env(seat=None)
    refused(("note", "SOME_ITEM_HERE_PROBE_FIXTURE", "--text", "x"), "cannot tell which seat I am",
            "the CLI guessed a seat instead of refusing", env_=e)
    refused(("note", "SOME_ITEM_HERE_PROBE_FIXTURE", "--text", "x"), "set_agent_window.sh",
            "the refusal did not say how to fix it", env_=e)


def t_show_and_why_still_work_with_no_seat():
    """Debugging the queue is exactly what you do when the window is misconfigured."""
    fresh()
    ok("file", "SHOWABLE_ITEM_HERE_PROBE_FIXTURE", "--for", "BUILD", "--title", "t")
    rc, out, err = run("show", "SHOWABLE_ITEM_HERE_PROBE_FIXTURE", env=env(seat=None))
    assert rc == 0, "show refused for want of a seat, but it writes nothing: %s" % err
    assert "SHOWABLE_ITEM_HERE_PROBE_FIXTURE" in out


def t_show_renders_the_causal_chain_run_finding_spawn():
    """⭐ The R&D path of §4, end to end, through the actual commands."""
    fresh()
    ok("file", "LIVE_CHECK_ITEM_PROBE_FIXTURE", "--for", "CHECK", "--title", "t")
    prose("LIVE_CHECK_ITEM_PROBE_FIXTURE")
    ok("claim", "LIVE_CHECK_ITEM_PROBE_FIXTURE", seat="CHECK")
    out = ok("verify", "LIVE_CHECK_ITEM_PROBE_FIXTURE", "--result", "fail", "--config", "full-578",
             "--evidence", "observed/logs/Player_x.log", seat="CHECK")
    assert "LIVE_CHECK_ITEM_PROBE_FIXTURE/run-1@full-578" in out and "IMMUTABLE" in out, out
    ok("finding", "--from", "LIVE_CHECK_ITEM_PROBE_FIXTURE/run-1@full-578",
       "--name", "BLACKSTAR_SPAWNS_VESSELLESS_PROBE_FIXTURE", "--type", "integration",
       "--severity", "high", seat="CHECK")
    ok("spawn", "--from", "BLACKSTAR_SPAWNS_VESSELLESS_PROBE_FIXTURE", "--for", "BUILD",
       "--name", "BLACKSTAR_VESSEL_DEF_PROBE_FIXTURE", seat="CHECK")
    out = ok("show", "BLACKSTAR_VESSEL_DEF_PROBE_FIXTURE")
    assert "caused by BLACKSTAR_SPAWNS_VESSELLESS_PROBE_FIXTURE" in out, out
    assert "LIVE_CHECK_ITEM_PROBE_FIXTURE/run-1@full-578" in out, (
        "the chain must reach the RUN, or a spawned item reads as somebody's opinion "
        "rather than the consequence of a run on the record: %s" % out)
    # ⚠️ The fail run stands; the source item is NOT reopened.
    src = ok("show", "LIVE_CHECK_ITEM_PROBE_FIXTURE")
    assert "run-1@full-578  fail" in src, src


def t_a_failed_run_does_not_reopen_the_item():
    fresh()
    ok("file", "TWICE_RUN_ITEM_PROBE_FIXTURE", "--for", "BUILD", "--title", "t")
    prose("TWICE_RUN_ITEM_PROBE_FIXTURE")
    ok("claim", "TWICE_RUN_ITEM_PROBE_FIXTURE")
    ok("verify", "TWICE_RUN_ITEM_PROBE_FIXTURE", "--result", "fail", "--config", "min-13")
    ok("verify", "TWICE_RUN_ITEM_PROBE_FIXTURE", "--result", "pass", "--config", "min-13")
    out = ok("show", "TWICE_RUN_ITEM_PROBE_FIXTURE")
    assert "run-1@min-13  fail" in out and "run-2@min-13  pass" in out, (
        "a failure must stand forever beside the later pass: %s" % out)
    ok("close", "TWICE_RUN_ITEM_PROBE_FIXTURE", "--sha", "abc1234")
    out = ok("verify", "TWICE_RUN_ITEM_PROBE_FIXTURE", "--result", "fail", "--config", "min-13")
    assert "not reope" in out, out
    head = ok("show", "TWICE_RUN_ITEM_PROBE_FIXTURE").splitlines()[0].split()
    assert head[1] == "done", "a failed run changed a closed item's state: %s" % head


def t_this_deployment_jumps_the_queue_and_clears_when_the_game_goes_down():
    fresh()
    ok("file", "ROW_ONE_ITEM_HERE_PROBE_FIXTURE", "--for", "CHECK", "--title", "t", "--row", "1")
    ok("file", "HOST_ITEM_HERE_PROBE_N9", "--for", "CHECK", "--title", "t")
    prose("ROW_ONE_ITEM_HERE_PROBE_FIXTURE")
    prose("HOST_ITEM_HERE_PROBE_N9")
    make_ready("ROW_ONE_ITEM_HERE_PROBE_FIXTURE", seat="CHECK")
    make_ready("HOST_ITEM_HERE_PROBE_N9", seat="CHECK")
    ok("game", "UP", seat="OWNER")
    ok("spawn", "--from", "HOST_ITEM_HERE_PROBE_N9", "--for", "CHECK",
       "--name", "URGENT_FOLLOWUP_HERE_PROBE_N9", "--this-deployment", seat="CHECK")
    prose("URGENT_FOLLOWUP_HERE_PROBE_N9")
    make_ready("URGENT_FOLLOWUP_HERE_PROBE_N9", seat="CHECK")
    out = ok("next", "--peek", seat="CHECK")    # a peek takes no lease: a leased item would drop out of the second look anyway
    assert body(out).startswith("URGENT_FOLLOWUP_HERE_PROBE_N9"), (
        "the live window is closing and row 1 is not: %s" % out)
    assert "THIS DEPLOYMENT" in out, out
    ok("game", "DOWN", seat="OWNER")
    out = ok("next", seat="CHECK")
    assert body(out).startswith("ROW_ONE_ITEM_HERE_PROBE_FIXTURE"), (
        "--this-deployment leaked past the window into false urgency: %s" % out)


def t_blocked_is_reported_and_the_item_is_withheld():
    fresh()
    ok("file", "WAITING_ON_OWNER_PROBE_FIXTURE", "--for", "BUILD", "--title", "t")
    prose("WAITING_ON_OWNER_PROBE_FIXTURE")
    make_ready("WAITING_ON_OWNER_PROBE_FIXTURE")
    ok("block", "WAITING_ON_OWNER_PROBE_FIXTURE", "--reason", "needs a ruling", "--on",
       "SOME_DECISION_ITEM_PROBE_FIXTURE")
    out = ok("why", "WAITING_ON_OWNER_PROBE_FIXTURE")
    assert "BLOCKED: needs a ruling" in out and "SOME_DECISION_ITEM_PROBE_FIXTURE" in out, out
    assert "1  BLOCKED" in ok("next", "--seat", "BUILD"), (
        "the empty answer must bucket the reasons, not just say nothing")
    ok("unblock", "WAITING_ON_OWNER_PROBE_FIXTURE")
    assert body(ok("next", "--seat", "BUILD")).startswith("WAITING_ON_OWNER_PROBE_FIXTURE")


def t_reassign_is_bench_only():
    fresh()
    ok("file", "REASSIGNABLE_ITEM_PROBE_FIXTURE", "--for", "FOUNDRY", "--title", "t")
    refused(("reassign", "REASSIGNABLE_ITEM_PROBE_FIXTURE", "--to", "BENCH", "--reason", "x"),
            "only BENCH", "FOUNDRY reassigned its own item", seat="FOUNDRY")
    assert "reassign" in ok("reassign", "REASSIGNABLE_ITEM_PROBE_FIXTURE", "--to", "CHECK",
                            "--reason", "x", seat="BENCH")
    moved = [ev for ev in _ledger_events() if ev.get("event") == "reassign"]
    assert moved and moved[-1].get("to") == "CHECK", moved
    assert "REASSIGNABLE_ITEM_PROBE_FIXTURE" in ok("next", "--seat", "CHECK", seat="CHECK"), "CHECK does not own it now"


# ---- the OWNER is never refused by a seat rule -----------------------------
#
# Owner's ruling, 2026-08-22, after being told `reassign` was DECIDE-only and that
# *"OWNER is not exempt for that verb, so even you can't do it as OWNER"*:
# *"That's bullshit. OWNER absolutely can and should be able to override and shift
# items between agents if necessary. A warning may be appropriate, but I have to be
# able to override."*
def t_owner_may_reassign_and_is_told_that_he_overrode():
    fresh()
    ok("file", "OWNER_TAKES_THIS_BACK_PROBE_FIXTURE", "--for", "BUILD", "--title", "t")
    rc, out, err = run("reassign", "OWNER_TAKES_THIS_BACK_PROBE_FIXTURE", "--to", "CHECK",
                       "--reason", "mine now", seat="OWNER")
    assert rc == 0, "the OWNER was refused a reassign\n  %s" % (out + err).strip()
    assert "CHECK" in ok("show", "OWNER_TAKES_THIS_BACK_PROBE_FIXTURE"), "the reassign did nothing"
    assert "OVERRIDE" in err.upper(), (
        "the override was silent. He asked to be able to override AND to be warned; "
        "an unannounced bypass is the failure mode, not the bypass.\n  stderr: %r" % err)
    led = _ledger_text()
    assert '"override"' in led, (
        "the override is not in the ledger. A year later it must read as a deliberate "
        "crossing of a seat boundary, not as a boundary that never existed.")


def t_owner_override_does_not_reach_the_state_machine():
    """`_may` governs WHO, and only WHO.

    ⛔ Being the OWNER must not become a way past the record. `claim` on a dropped item
    is a TERMINAL violation and stays refused for him; a typo'd id is not a seat
    boundary at all and stays refused too, or he would file events about nothing.
    ✅ `reassign` on a terminal item is ALLOWED and does not revive it — the owner may
    change who holds a closed item; he may not reopen it.
    """
    fresh()
    ok("file", "OWNER_CANNOT_REVIVE_THIS_PROBE_FIXTURE", "--for", "BUILD", "--title", "t")
    ok("drop", "OWNER_CANNOT_REVIVE_THIS_PROBE_FIXTURE", "--reason", "x", seat="BUILD")
    refused(("claim", "OWNER_CANNOT_REVIVE_THIS_PROBE_FIXTURE"),
            "drop", "OWNER restarted a dropped item by being the OWNER", seat="OWNER")
    ok("reassign", "OWNER_CANNOT_REVIVE_THIS_PROBE_FIXTURE", "--to", "CHECK", "--reason", "x",
       seat="OWNER")
    assert "dropped" in ok("show", "OWNER_CANNOT_REVIVE_THIS_PROBE_FIXTURE"), (
        "an owner reassign revived a terminal item")
    refused(("reassign", "NO_SUCH_ITEM_ANYWHERE_PROBE_FIXTURE", "--to", "CHECK", "--reason", "x"),
            "never been filed", "OWNER overrode a typo into an event about nothing",
            seat="OWNER")


def t_owner_is_not_warned_where_the_rule_already_admits_him():
    """`retarget` is ("DECIDE", "owner") — he was always allowed. No warning for it."""
    fresh()
    ok("file", "OWNER_RETARGETS_QUIETLY_PROBE_FIXTURE", "--for", "BUILD", "--title", "t")
    rc, out, err = run("retarget", "OWNER_RETARGETS_QUIETLY_PROBE_FIXTURE", "v2",
                       "--reason", "x", seat="OWNER")
    assert rc == 0, (out + err).strip()
    assert "OVERRIDE" not in err.upper(), (
        "warned about an override that did not happen — the rule admits the owner "
        "outright. Crying wolf here is how the real warning stops being read.")


def t_sweep_transient_lists_and_never_deletes():
    fresh()
    def seen():
        roots = [(REPO, n) for n in os.listdir(REPO) if n.startswith("TRANSIENT_")]
        d = os.path.join(REPO, "Transient")
        roots += [(d, n) for n in os.listdir(d) if n != "README.md" and not n.startswith(".")] if os.path.isdir(d) else []
        got = {}
        for r, n in roots:
            top = os.path.join(r, n)
            paths = [top] + [os.path.join(w, f) for w, ds, fs in os.walk(top) for f in ds + fs]     # nested notes too
            for path in paths:
                try:
                    st = os.stat(path)
                except OSError:
                    continue
                got[os.path.relpath(path, REPO)] = (st.st_size, st.st_mtime_ns)
        return got
    before = seen()
    out = ok("sweep", "--transient")
    after = seen()
    gone = {k: v for k, v in before.items() if after.get(k) != v}
    assert not gone, (
        "sweep DELETED or changed something. It lists; deciding a file is stale is a judgement "
        "and destroying working notes is not recoverable: %r" % sorted(gone))
    assert ("THIS LISTS ONLY" in out) if before else ("no transient files." in out), out


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


def t_the_bench_scan_is_refused_to_a_seat_that_could_game_it():
    """⛔ `next --bench` IS REP'S AND THE OWNER'S, AND THAT IS NOT SENIORITY.

    It is the one rimflow output that scores actions seats CHOOSE rather than facts about
    the world, so it is the only one that can be gamed — and the specific pressure is
    harmful: penalise upstream reassignment and a seat learns to absorb mis-scoped work
    rather than hand it back, which is worse and invisible. `facts/distress_signals.md`.
    ⭐ The refusal must carry that REASON, not just the word no.
    """
    fresh()
    err = refused(("next", "--bench"), "distress_signals.md",
                  "FOUNDRY must not be handed a score to optimise", seat="FOUNDRY")
    assert "gamed" in err.lower(), (
        "the refusal has to say WHY, or the next seat reads it as rank: %s" % err)
    ok("next", "--bench", seat="BENCH")
    ok("next", "--bench", seat="OWNER")


def _cli():
    """The cli module itself, for the handful of units that are worth calling directly.

    ⚠️ Everything that can be driven as a COMMAND is driven as a command — see this
    file's own opening note on why. These in-process cases are for pure functions whose
    inputs a subprocess cannot reach: a path shape that only occurs on another machine's
    layout, a staleness decision that would otherwise need two racing windows and a
    45-minute clock, a counting rule buried three sections deep in a printed report.
    """
    import importlib
    sys.path.insert(0, os.path.dirname(HERE))
    return importlib.import_module("rimflow.cli")


def t_the_queue_views_are_rendered_beside_the_ledger_in_use():
    """🔴 EVERY WRITE RENDERED THE SYNTHETIC QUEUES INTO THE REPO ROOT.

    `_emit` derived its output root as `dirname(dirname(EVENTS))`, which is right for
    `infrastructure/state/ledger/events.jsonl` and one level too high for the throwaway
    ledger THIS FILE builds — so `<repo>/queue/BENCH.md` and
    `<repo>/derived/queue_preview/` were created and rewritten on every selftest run:
    untracked, not gitignored, sitting at the top of the tree where a careless
    `git add` would sweep test fixtures into the repo. Measured 2026-09-03, four files.

    ⭐ Asserts BOTH halves. That the real repo is untouched is the safety property; that
    the throwaway root DID get its views is what proves the render still happens at all
    — a fix that simply stopped rendering would pass the first assertion alone.
    """
    fresh()
    repo_queue = os.path.join(REPO, "queue")
    repo_derived = os.path.join(REPO, "derived")
    def seen():
        got = {}
        for root in (repo_queue, repo_derived):
            got[root] = os.path.exists(root)
            for d, _, names in os.walk(root):
                for n in names:
                    st = os.stat(os.path.join(d, n))
                    got[os.path.join(d, n)] = (st.st_size, st.st_mtime_ns)
        return got
    before = seen()
    ok("file", "RENDER_ROOT_PROBE_PROBE_FIXTURE", "--for", "BENCH", "--title", "t")
    assert seen() == before, (
        "a write rendered the throwaway ledger's queue views into the REPO ROOT "
        "(%s / %s). The whole point of RIMFLOW_LEDGER is that a test touches nothing "
        "real." % (repo_queue, repo_derived))
    assert os.path.isdir(os.path.join(_tmp(), "queue")), (
        "nothing was rendered beside the ledger in use — the views are now silently "
        "not published at all, which is the other half of the same defect: %s"
        % sorted(os.listdir(_tmp())))


def t_state_root_is_derived_by_shape_not_by_counting_dirnames():
    """The unit under the case above. Two layouts, one rule, no repo involved."""
    cli = _cli()
    assert cli._state_root("/x/infrastructure/state/ledger/events.jsonl") == \
        "/x/infrastructure/state", "the real layout must still resolve to STATE"
    assert cli._state_root("/x/.rimflow_selftest_cli/events.jsonl") == \
        "/x/.rimflow_selftest_cli", (
            "a ledger that is NOT inside a `ledger/` directory publishes beside itself, "
            "never one level up into whatever happens to contain it")


def t_going_down_does_not_claim_to_clear_this_deployment():
    """🔴 THE CLI ANNOUNCED A CLEARING THE MODEL DOES NOT PERFORM.

    `model._apply` clears `--this-deployment` on entering DOWN and ONLY on DOWN — the
    narrowing is deliberate, because GOING_DOWN is exactly when the flag is most
    load-bearing: the window is closing and the this-deployment list is what a seat
    works first. `cmd_game` still said "every --this-deployment flag is now cleared" for
    every state that was not UP, so at GOING_DOWN a seat was told its urgent list had
    just been emptied while every flag was still set.

    ⭐ Read through `show`, not `next`: `show` is READ_ONLY and never measures the live
    machine, so this case cannot be moved by whether RimWorld happens to be running.
    """
    fresh()
    ok("file", "DEPLOYMENT_FLAG_HOST_PROBE_FIXTURE", "--for", "CHECK", "--title", "t")
    ok("game", "UP", seat="OWNER")
    ok("spawn", "--from", "DEPLOYMENT_FLAG_HOST_PROBE_FIXTURE", "--for", "CHECK",
       "--name", "DEPLOYMENT_FLAG_PROBE_PROBE_FIXTURE", "--this-deployment", seat="CHECK")
    out = ok("game", "GOING_DOWN", seat="OWNER")
    assert "cleared" not in out, (
        "GOING_DOWN announced a clearing that did not happen — the flag is still set "
        "and the seat was told otherwise: %s" % out)
    assert "THIS DEPLOYMENT" in ok("show", "DEPLOYMENT_FLAG_PROBE_PROBE_FIXTURE"), (
        "the premise moved: GOING_DOWN now really does clear the flag, and the "
        "message this case guards would have been right all along")
    out = ok("game", "DOWN", seat="OWNER")
    assert "cleared" in out, (
        "DOWN stopped saying it clears the flags, and DOWN is the state that does: %s"
        % out)
    assert "THIS DEPLOYMENT" not in ok("show", "DEPLOYMENT_FLAG_PROBE_PROBE_FIXTURE")


def t_the_bench_scan_sees_a_spawned_item():
    """🔴 EVERY ITEM BORN OF A FINDING WAS INVISIBLE TO THE OWNER'S OWN BOARD.

    `_apply`'s spawn branch never sets `target`, so a spawned item carries `None` —
    which `priority.rank()` explicitly admits (`it.target not in (None, target)`) and
    `cmd_bench` did not (`i.target == args.target`). So `next` would offer an item that
    the triage the owner reads insisted did not exist, in all four of its sections, and
    neither screen said anything.
    """
    fresh()
    ok("file", "SPAWN_VISIBILITY_HOST_PROBE_FIXTURE", "--for", "BENCH", "--title", "host")
    ok("spawn", "--from", "SPAWN_VISIBILITY_HOST_PROBE_FIXTURE", "--for", "BENCH",
       "--name", "SPAWNED_UNBLOCKED_ITEM_PROBE_FIXTURE", seat="BENCH")
    out = ok("next", "--bench", seat="BENCH")
    assert "SPAWNED_UNBLOCKED_ITEM_PROBE_FIXTURE" in out, (
        "a spawned item is missing from the BENCH scan entirely — it has no `target`, "
        "and the scan filtered on equality where the priority engine admits None:\n%s"
        % out)
    ripe = out.split("\nRIPE")[1].split("IN TROUBLE")[0]
    assert "SPAWNED_UNBLOCKED_ITEM_PROBE_FIXTURE" in ripe, (
        "counted but not RIPE — unblocked offline proposed work is the definition:\n%s"
        % ripe)


def t_owner_said_authorizes_where_no_seat_is_configured():
    """🔴 THE ROUTE THROUGH EVERY REFUSAL WAS ITSELF REFUSED.

    CHARTER.md and the global rules both send an agent to `--owner-said "<his verbatim
    words>"` when a guard refuses it. `main` resolved the seat FIRST, so a window with
    no `RIMFLOW_SEAT`, no `AGENT_SEAT` and no session role file was told *"I cannot tell
    which seat I am, and I will not guess"* on a command the owner had just told it to
    run — with the words that settle the question sitting unread on the same line.

    ⚠️ This grants nothing new: `--seat OWNER --owner-said "…"` was always accepted. And
    a seat that IS named is still validated, because a typo silently discarded is the
    same defect `bridge take BOGUS` was fixed for.
    """
    fresh()
    out = ok("game", "UP", "--owner-said", "game up", env=env(seat=None))
    assert "game is UP" in out, out
    led = _ledger_text()
    assert '"ownerSaid":"game up"' in led.replace(", ", ",").replace('" : "', '":"'), (
        "his words are the authorization and must be ON the event: %s" % led)
    refused(("game", "UP", "--seat", "NOTASEAT", "--owner-said", "game up"),
            "not one of", "a typo'd --seat was silently discarded because a quote "
            "was also present", env_=env(seat=None))
    refused(("game", "UP", "--owner-said", "yes"), "not the agreement",
            "bare assent stood in for an instruction", env_=env(seat=None))
    refused(("game", "UP", "--owner-said", "should the game be up?"), "is a question",
            "a question stood in for an instruction", env_=env(seat=None))


def t_each_kind_of_authority_lands_in_its_own_field():
    """Owner, by card 2026-10-11: his words, his card clicks, a standing ruling cited by
    reference and the agent's own reason each get their OWN field, so nothing lands in
    `ownerSaid` by mistake (the census found 87 agent sentences, 68 card labels and 57
    re-quoted rulings there). `--by-card` / `--per-ruling` carry OWNER authority;
    `--why` grants nothing and leaves the acting seat as it was."""
    fresh()
    ok("file", "REBOOT_RULING_PROBE_FIXTURE", "--for", "BUILD", "--title", "t")   # --per-ruling must resolve
    ok("game", "UP", "--by-card", "Restart now? -> Restart now", env=env(seat=None))
    ok("game", "DOWN", "--per-ruling", "REBOOT_RULING_PROBE_FIXTURE", "--why",
       "FOUNDRY restart to load the new DLL", env=env(seat=None))
    games = [e for e in _ledger_events() if e.get("event") == "game"]
    assert len(games) == 2, games
    card, rul = games
    assert card.get("seat") == "OWNER" and card.get("byCard") == "Restart now? -> Restart now", card
    assert "ownerSaid" not in card and "why" not in card, card
    assert rul.get("seat") == "OWNER" and rul.get("perRuling") == "REBOOT_RULING_PROBE_FIXTURE", rul
    assert rul.get("why") == "FOUNDRY restart to load the new DLL" and "ownerSaid" not in rul, rul
    refused(("game", "UP", "--per-ruling", "when bridge is available go ahead"),
            "takes a reference", "a re-quoted ruling went into --per-ruling",
            env_=env(seat=None))
    # --why alone is the agent's own reason: recorded, and the seat stays the agent's.
    ok("file", "WHY_FIELD_PROBE_FIXTURE", "--for", "BUILD", "--title", "probe",
       "--why", "found while sweeping")
    filed = [e for e in _ledger_events() if e.get("id") == "WHY_FIELD_PROBE_FIXTURE"]
    assert filed and filed[0].get("seat") == "BUILD" and filed[0].get("why") == \
        "found while sweeping" and "ownerSaid" not in filed[0], filed
    out = ok("show", "WHY_FIELD_PROBE_FIXTURE")
    assert "agent's reason: found while sweeping" in out, out


def t_bridge_give_refuses_a_target_that_is_not_a_window():
    """`give` writes the OWNER's name onto a permanent event; the target must be real.

    ⭐ And `give free` must work when the bridge is ALREADY free — it is the one
    command he reaches for when he does not know who holds it, so it may not depend on
    someone holding it. That path emits under OWNER rather than under a window, which
    is the branch `model._may` refuses and the owner override then admits.
    """
    fresh()
    refused(("bridge", "give", "SOMEWHERE"), "give it to BENCH", "the owner's switch "
            "accepted a target that is not a window", seat="OWNER")
    assert not _bridge_events(), "a refused give still wrote to the ledger"
    out = ok("bridge", "give", "free", seat="OWNER")
    assert "FREE" in out, out
    assert _ledger_holder() is None and _mirror_holder() is None, (
        "clearing an already-free bridge left a holder behind: ledger=%r mirror=%r"
        % (_ledger_holder(), _mirror_holder()))


def t_the_take_rule_frees_a_silent_holder_and_protects_a_working_one():
    """The staleness rule, as a unit — the one decision that decides mutual lockout.

    🔑 Driving this as commands would need two windows and a 45-minute clock, so the
    rule was only ever exercised through its uncontested branch. `_take_decision` is
    pure, so every branch is one line here, including the one that matters most:
    `idle is None` means NO EVIDENCE THE HOLDER IS ALIVE and must read as STALE. Read
    the other way round, an unreadable timestamp wedges the bridge forever — which is
    exactly the failure the owner named on 2026-09-02.
    """
    cli = _cli()
    import importlib
    m = importlib.import_module("rimflow.model")
    stale = m.BRIDGE_STALE_SECONDS
    assert cli._take_decision(None, "BENCH", None, False, None) == (None, None), (
        "an uncontested take must be granted and left UNMARKED, or the marking on a "
        "contested one means nothing")
    assert cli._take_decision("BENCH", "BENCH", 5, False, None) == (None, None), (
        "re-taking your own lock is not a crossing")
    why, refusal = cli._take_decision("FOUNDRY", "BENCH", 60, False, None)
    assert refusal and "--force" in refusal, (
        "a live holder refused with no way through — mutual lockout is the expensive "
        "failure here, not two drivers: %r" % refusal)
    why, refusal = cli._take_decision("FOUNDRY", "BENCH", stale, False, None)
    assert refusal is None and why and "quiet" in why, (
        "a holder silent for the whole staleness window still held the lock: %r" % why)
    why, refusal = cli._take_decision("FOUNDRY", "BENCH", None, False, None)
    assert refusal is None and why, (
        "an unreadable last-seen stamp read as a LIVE holder. No evidence that a "
        "window is alive is not evidence that it is: %r / %r" % (why, refusal))
    why, refusal = cli._take_decision("FOUNDRY", "BENCH", 1, True, None)
    assert refusal is None and why == "forced", (
        "--force must always land, and must always be marked: %r" % why)


def t_the_distress_counters_measure_direction_and_recency():
    """The two loops inside `next --bench`'s score, which nothing could reach before.

    🔑 `_upstream_reassigns` counts DIRECTION, not reassignments: the fact file's top
    thrashing item had 11 reassignments and closed in 1.0 h, while upstream-reassigned
    items live 10.5 h against 1.5 h. `_notes_since_last_commit` resets on every event
    carrying a sha, which is what makes "2 notes and no commit since" mean something
    and "2 notes across a month of commits" mean nothing.
    """
    cli = _cli()
    import types

    def score(evs):
        return cli._upstream_reassigns(
            types.SimpleNamespace(history=list(range(len(evs)))), evs)

    assert score([{"event": "file", "for": "CHECK", "seat": "BENCH"},
                  {"event": "reassign", "to": "BUILD", "seat": "BENCH"}]) == 1, (
        "CHECK -> BUILD is a seat handing work back up the conveyor and must count")
    assert score([{"event": "file", "for": "BUILD", "seat": "BENCH"},
                  {"event": "reassign", "to": "CHECK", "seat": "BENCH"}]) == 0, (
        "downstream is the conveyor WORKING (0.55x, protective) and must not score")
    assert score([{"event": "reassign", "to": "BUILD", "seat": "BENCH"}]) == 0, (
        "`reassign` carries no `from`, so an item whose FIRST event is one has no "
        "previous owner to infer direction from — it must score 0, never guess")

    def notes(evs):
        return cli._notes_since_last_commit(
            types.SimpleNamespace(history=list(range(len(evs)))), evs)

    assert notes([{"event": "note"}, {"event": "note"}]) == (2, 0)
    assert notes([{"event": "note"}, {"event": "note"},
                  {"event": "close", "sha": "abc1234"}, {"event": "note"}]) == (1, 1), (
        "the note counter must RESET on a commit, or talk-without-work fires on any "
        "item that has ever been chatty")


def t_the_real_ledger_was_never_touched():
    """🔴 The whole point of RIMFLOW_LEDGER. If this fails, everything above lied.
    This case proves the real paths differ from the scratch ones. That no event landed is proved by scratch_env on
    every subprocess, and by _audit_real_ledger once every case has finished: this case runs beside the writers."""
    import importlib
    sys.path.insert(0, os.path.dirname(HERE))
    m = importlib.import_module("rimflow.model")
    real = m.EVENTS
    assert not real.startswith(TMP_ROOT), real
    assert os.path.abspath(real) != os.path.abspath(os.path.join(_tmp(), "events.jsonl"))
    # 🔴 THE SHARDS TOO. Since 2026-09-23 the CLI appends to `events/<SEAT>.jsonl`, not
    # to `events.jsonl`.
    for path in m.ledger_files():
        assert not path.startswith(TMP_ROOT), path


def _ledger_sizes():
    sys.path.insert(0, os.path.dirname(HERE))
    import importlib
    m = importlib.import_module("rimflow.model")
    return {f: os.path.getsize(f) for f in m.ledger_files()}


def _real_prose():
    """Fixture-named prose in the real items/ and items/closed/: a fixture moved or written there leaves no ledger line."""
    sys.path.insert(0, os.path.dirname(HERE))
    import importlib
    m = importlib.import_module("rimflow.model")
    return {os.path.join(d, n) for d in (m.ITEMS, m.CLOSED) if os.path.isdir(d) for n in os.listdir(d)
            if re.search(r"_PROBE_(FIXTURE|N\d)", n)}


def _audit_real_ledger(sizes, files=None):
    """After every case: the bytes added to the real ledger during this run. Other seats may append while this runs,
    so a changed file is not a leak; a fixture's name, or a run-only reason, in the new bytes is. -> the leaks."""
    leaks = []
    for f in (files if files is not None else _ledger_sizes()):
        with open(f, "rb") as fh:
            fh.seek(sizes.get(f, 0))
            leaks += ["%s: %s" % (f, line[:120]) for line in fh.read().decode("utf-8", "replace").splitlines()
                      if re.search(r"_PROBE_(FIXTURE|N\d)|after the stale one|\"my load\"", line)]
    return leaks


def t_the_real_ledger_audit_can_see_a_leak():
    """The instrument, proved: new bytes with a fixture name are a leak; old bytes, and another seat's event, are not."""
    fresh()
    f = os.path.join(_tmp(), "shard.jsonl")
    with open(f, "w", encoding="utf-8") as fh:
        fh.write('{"item": "OLD_ONE_PROBE_FIXTURE"}\n')
    mark = os.path.getsize(f)
    with open(f, "a", encoding="utf-8") as fh:
        fh.write('{"item": "A_REAL_ITEM"}\n')
    assert not _audit_real_ledger({f: mark}, [f]), "bytes from before the run, or a real event, read as a leak"
    with open(f, "a", encoding="utf-8") as fh:
        fh.write('{"item": "NEW_ONE_PROBE_FIXTURE"}\n')
    assert len(_audit_real_ledger({f: mark}, [f])) == 1, "the audit did not see a leaked fixture"


def t_a_take_in_another_clone_refuses_until_forced_or_stale():
    """BRIDGE_LOCK_CROSS_CLONE_RACE_1: two seat clones keep separate ledgers, so a take
    in one was invisible to the other until pushed (2026-10-07: both held it, two loads
    killed). The shared lock file outside git is what the other clone sees at once."""
    fresh()
    shared = os.path.join(_tmp(), "BRIDGE_SHARED.json")
    other = os.path.join(_tmp(), "clone_b")
    os.makedirs(os.path.join(other, "items"), exist_ok=True)
    env_a = lambda seat: env(seat, RIMFLOW_SHARED_BRIDGE=shared)
    env_b = lambda seat: env(seat, RIMFLOW_SHARED_BRIDGE=shared,
                             RIMFLOW_LEDGER=os.path.join(other, "events.jsonl"),
                             RIMFLOW_ITEMS=os.path.join(other, "items"))
    ok("bridge", "take", "--for", "load round", env=env_a("FOUNDRY"))
    body = json.load(open(shared))
    assert body.get("holder") == "FOUNDRY", "a take did not write the shared lock: %s" % body
    refused(["bridge", "take", "--for", "my load"], "another clone",
            "the other clone's live take was invisible", seat="BENCH", env_=env_b("BENCH"))
    out = ok("bridge", "who", env=env_b("BENCH"))
    assert "another clone" in out, "who hid the other clone's hold: %s" % out
    # the holder's ordinary events keep the lock fresh
    body = json.load(open(shared))
    t0 = body["touched"] = "2020-01-01T00:00:00Z"
    json.dump(body, open(shared, "w"))
    ok("file", "SHARED_TOUCH_ITEM_PROBE_FIXTURE", "--for", "FOUNDRY", "--title", "t", env=env_a("FOUNDRY"))
    assert json.load(open(shared))["touched"] != t0, "an ordinary event of the holder left the shared lock's touched"
    body = json.load(open(shared))
    body["touched"] = t0
    json.dump(body, open(shared, "w"))
    ok("claim", "SHARED_TOUCH_ITEM_PROBE_FIXTURE", env=env_a("FOUNDRY"))
    assert json.load(open(shared))["touched"] != t0, "a claim, written as a lease group, left the shared lock's touched"
    # --force crosses it, and says so on the event
    ok("bridge", "take", "--force", "--for", "urgent", env=env_b("BENCH"))
    evs = []
    d = os.path.join(other, "events")   # the ledger is shards beside the head (see _ledger_paths)
    for f in (sorted(os.listdir(d)) if os.path.isdir(d) else []):
        if f.endswith(".jsonl"):
            evs += [json.loads(l) for l in open(os.path.join(d, f)) if l.strip()]
    tk = [e for e in evs if e.get("event") == "bridge" and e.get("state") == "taken"]
    assert tk and "another clone" in (tk[-1].get("override") or ""), tk
    assert json.load(open(shared))["holder"] == "BENCH"
    ok("bridge", "release", env=env_b("BENCH"))
    assert json.load(open(shared)).get("holder") is None, "release left the shared lock held"
    # a stale shared hold (older than the staleness window) does not block
    ok("bridge", "release", env=env_a("FOUNDRY"))    # this clone's own ledger hold, so the take below meets only the stale one
    with open(shared, "w") as fh:
        json.dump({"holder": "BENCH", "since": "2020-01-01T00:00:00Z", "touched": "2020-01-01T00:00:00Z",
                   "clone": "/elsewhere"}, fh)
    ok("bridge", "take", "--for", "after the stale one", env=env_a("FOUNDRY"))
    assert json.load(open(shared))["holder"] == "FOUNDRY"


def _assert_no_leaks(leaks):
    assert not leaks, "reached the REAL ledger, which is append-only and has no undo: %s" % leaks[:3]


def write_grant_fixture():
    """A valid grant, whatever the machine's real one says. A case about the preflight passes its own."""
    sys.path.insert(0, os.path.dirname(HERE))
    from rimflow import companion_grant
    conf = companion_grant.load_conf()
    exp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 7 * 86400))
    with open(GRANT_FIXTURE, "w", encoding="utf-8") as fh:
        json.dump({"profile": conf["test_profiles"][0], "expiresUtc": exp}, fh)


CASES = [(k[2:], v) for k, v in sorted(globals().items()) if k.startswith("t_")]


def _run_case(name, fn):
    """Give this case its own directory under TMP_ROOT before running it, so it can
    run concurrently with every other case without racing on a shared one."""
    _tls.dir = os.path.join(TMP_ROOT, name)
    shutil.rmtree(_tls.dir, ignore_errors=True)
    os.makedirs(os.path.join(_tls.dir, "items"), exist_ok=True)
    try:
        case(name, fn)
    finally:
        shutil.rmtree(_tls.dir, ignore_errors=True)


if __name__ == "__main__":
    os.makedirs(TMP_ROOT, exist_ok=True)
    try:
        write_grant_fixture()
        sizes = _ledger_sizes()
        prose_before = _real_prose()
        with ThreadPoolExecutor(max_workers=12) as pool:
            futures = [pool.submit(_run_case, name, fn) for name, fn in CASES]
            for f in as_completed(futures):
                f.result()  # surface a harness-level exception, not just a case failure
        leaks = _audit_real_ledger(sizes)
        case("no_case_wrote_the_real_ledger", lambda: _assert_no_leaks(leaks))
        case("no_case_wrote_real_prose", lambda: _assert_no_leaks(sorted(_real_prose() - prose_before)))
    finally:
        shutil.rmtree(TMP_ROOT, ignore_errors=True)
        try:
            os.rmdir(TMP_PARENT)
        except OSError:
            pass        # another run is still inside it
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
