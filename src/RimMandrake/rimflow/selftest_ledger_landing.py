#!/usr/bin/env python3
"""selftest_ledger_landing.py: a rimflow write lands the paths it wrote (boundary
design/specs/2026-11-22-ledger-write-lands-its-shard/boundary.md). One case per promise, named as the promise.

    python3 src/RimMandrake/rimflow/selftest_ledger_landing.py            the promises, recorded sample included
    python3 src/RimMandrake/rimflow/selftest_ledger_landing.py --all      the equivalence on EVERY event in this tree
    python3 src/RimMandrake/rimflow/selftest_ledger_landing.py --freeze   rewrite the recorded sample from this tree

The end-to-end cases drive the real CLI against a temp clone of a temp bare repo: nothing here touches this repo's
ledger, its origin or any game. The equivalence replays recorded ledger events through `model.append` (a temp ledger)
and compares the shard the new home records with the shard the event lives in, and with what the two old paths named:
the detached brief's prose rule ("the seat's shard; OWNER.jsonl too after --per-ruling, --owner-said or --by-card") and
`detached_helper.publish_command`'s filed-nowhere route (seat shard + OWNER.jsonl, always both).
"""
import collections
import copy
import glob
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CLI = os.path.join(HERE, "cli.py")
SAMPLE = os.path.join(HERE, "selftest_ledger_landing_recorded.jsonl")
EVENTS_REL = "infrastructure/state/ledger/events"
LEDGER_REL = "infrastructure/state/ledger/events.jsonl"
ITEMS_REL = "infrastructure/state/items"
FLAGS = ("ownerSaid", "byCard", "perRuling")
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import ledger_landing as LL, model  # noqa: E402

FAIL = []
TMP = tempfile.mkdtemp(prefix="selftest_ledger_landing_")


def check(cond, what):
    print(("ok    " if cond else "FAIL  ") + what)
    if not cond:
        FAIL.append(what)


def _genv(**over):
    e = {k: v for k, v in os.environ.items()
         if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "RM_ROLE_UNIT")
         and not k.startswith("GIT_")}
    e.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    e.update(over)
    return e


def git(cwd, *a):
    r = subprocess.run(["git", "-C", cwd] + list(a), capture_output=True, text=True, env=_genv(), timeout=60)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr))
    return r.stdout.strip()


def fixture(name):
    """-> a clone of a fresh bare repo holding an empty ledger and items folder, pushed."""
    base = os.path.join(TMP, name)
    bare, clone = os.path.join(base, "bare.git"), os.path.join(base, "clone")
    os.makedirs(base)
    git(base, "init", "-q", "--bare", "-b", "main", bare)
    git(base, "clone", "-q", bare, clone)
    os.makedirs(os.path.join(clone, EVENTS_REL))
    os.makedirs(os.path.join(clone, ITEMS_REL, "closed"))
    open(os.path.join(clone, LEDGER_REL), "w").close()
    open(os.path.join(clone, ITEMS_REL, "closed", ".keep"), "w").close()
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "seed")
    git(clone, "push", "-q", "origin", "HEAD:main")
    return clone


def cli_env(clone):
    return _genv(RIMFLOW_LEDGER=os.path.join(clone, LEDGER_REL), RIMFLOW_ITEMS=os.path.join(clone, ITEMS_REL),
                 RIMFLOW_PROBE="no-reading", RIMFLOW_SCHEDULE=os.path.join(TMP, "no_schedule.json"),
                 RIMFLOW_DRIVER_LOCK="", RM_HOST="archmagi", RIMFLOW_BRIDGE_LOCK=os.path.join(TMP, "bridge.lock"),
                 RIMFLOW_GIT_CWD=clone, RM_FULLTEXT_DIR=os.path.join(TMP, "fulltext"),
                 RM_PUBLISH_SKIP_TREE_CHECKS="", RM_PUBLISH_SKIP_PIPELINE_CHECKS="",
                 PUBLISH_RM_ROOT=TMP)                 # the machine-wide push lock of the fixture's publishes, not the real one


def rimflow(clone, *args):
    r = subprocess.run([sys.executable, CLI] + list(args), capture_output=True, text=True, env=cli_env(clone),
                       cwd=clone, timeout=600, stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout, r.stderr


def landed(clone):
    """-> the paths origin/main's newest commit changed (fetched fresh)."""
    git(clone, "fetch", "-q", "origin")
    return sorted(git(clone, "show", "--no-renames", "--name-only", "--format=", "origin/main").split())


def origin_sha(clone):
    git(clone, "fetch", "-q", "origin")
    return git(clone, "rev-parse", "origin/main")


def seeded(name):
    """-> a fixture clone holding item ITEM_A (BENCH, published) and a ruling item RULING_A to cite."""
    c = fixture(name)
    for iid in ("RIMMANDRAKE_PROBE_LANDING_FIXTURE_ITEM_ONE", "RIMMANDRAKE_PROBE_LANDING_FIXTURE_RULING_ONE"):
        rc, out, err = rimflow(c, "file", iid, "--for", "BENCH", "--seat", "BENCH", "--why", "fixture", "--title", "fixture")
        assert rc == 0, (rc, out, err)
    git(c, "add", "-A")
    git(c, "commit", "-q", "-m", "items")
    git(c, "push", "-q", "origin", "HEAD:main")
    return c


ITEM = "RIMMANDRAKE_PROBE_LANDING_FIXTURE_ITEM_ONE"
RULING = "RIMMANDRAKE_PROBE_LANDING_FIXTURE_RULING_ONE"
SEAT_SHARD = EVENTS_REL + "/BENCH.jsonl"
OWNER_SHARD = EVENTS_REL + "/OWNER.jsonl"


# ---------------------------------------------------------------------------------------------------------------------
def t_publish_lands_exactly_the_written_paths():
    c = seeded("exact")
    rc, out, err = rimflow(c, "note", ITEM, "--text", "plain", "--seat", "BENCH", "--why", "t", "--publish")
    check(rc == 0 and "PUBLISHED " in out, "publish-lands-exactly-the-written-paths: a plain note publishes (rc %d)" % rc)
    check(landed(c) == [SEAT_SHARD], "publish-lands-exactly-the-written-paths: a plain note lands only %s: %s"
          % (SEAT_SHARD, landed(c)))
    rc, out, err = rimflow(c, "note", ITEM, "--text", "ruled", "--per-ruling", RULING, "--why", "t", "--publish")
    check(rc == 0 and "PUBLISHED " in out, "publish-lands-exactly-the-written-paths: a --per-ruling note publishes")
    check(landed(c) == [OWNER_SHARD], "publish-lands-exactly-the-written-paths: a --per-ruling note lands OWNER.jsonl, "
          "the one shard it wrote: %s" % landed(c))
    check(not git(c, "status", "--porcelain", "--", EVENTS_REL), "publish-lands-exactly-the-written-paths: no shard is "
          "left dirty")


def t_a_ledger_write_waits_for_no_peer_and_takes_no_peer_commit():
    import fcntl
    c = seeded("held")
    with open(os.path.join(c, "peer.txt"), "w") as f:
        f.write("a peer's unpublished work\n")
    git(c, "add", "--", "peer.txt")
    git(c, "commit", "-q", "-m", "peer")
    head = git(c, "rev-parse", "HEAD")
    with open(os.path.join(c, ".git", "publish.lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        old = os.environ.get("PUBLISH_LOCK_TIMEOUT")
        os.environ["PUBLISH_LOCK_TIMEOUT"] = "2"
        try:
            rc, out, err = rimflow(c, "note", ITEM, "--text", "past the lock", "--seat", "BENCH", "--why", "t", "--publish")
        finally:
            os.environ.pop("PUBLISH_LOCK_TIMEOUT") if old is None else os.environ.update(PUBLISH_LOCK_TIMEOUT=old)
    check(rc == 0 and "PUBLISHED " in out and landed(c) == [SEAT_SHARD], "a-ledger-write-waits-for-no-peer-and-takes-no-"
          "peer-commit: lands with the clone's publish lock held, its shard alone: rc %d %s %s" % (rc, landed(c), out[-200:]))
    check(git(c, "rev-parse", "HEAD") == head, "a-ledger-write-waits-for-no-peer-and-takes-no-peer-commit: the held "
          "clone's branch did not move")


def t_records_the_item_prose_a_write_made():
    c = seeded("prose")
    with open(os.path.join(c, ITEMS_REL, ITEM + ".md"), "w") as f:
        f.write("# prose\n")
    git(c, "add", "--", ITEMS_REL + "/" + ITEM + ".md")
    git(c, "commit", "-q", "-m", "prose")
    git(c, "push", "-q", "origin", "HEAD:main")
    rc, out, err = rimflow(c, "close", ITEM, "--no-code", "fixture", "--seat", "BENCH", "--why", "t", "--publish")
    want = sorted([SEAT_SHARD, ITEMS_REL + "/" + ITEM + ".md", ITEMS_REL + "/closed/" + ITEM + ".md"])
    check(rc == 0 and landed(c) == want, "publish-lands-exactly-the-written-paths / records-the-item-prose-a-write-made: "
          "close lands its shard and both sides of the prose move: rc %d %s" % (rc, landed(c)))
    # publish.py's carried_prose_moves would also add the move for a bare shard; the new home must name it itself
    named = next((ln for ln in out.splitlines() if ln.startswith("PUBLISHED ")), "")
    check(all(p in named.split("(", 1)[-1].rstrip(")").split() for p in want) and "carried with the ledger shard" not in out,
          "records-the-item-prose-a-write-made: the landing itself names both sides of the move: %s" % named)


def t_a_plain_write_runs_no_git():
    c = seeded("plain")
    before = origin_sha(c)
    calls = []
    LL.reset()
    real = subprocess.run
    rc, out, err = rimflow(c, "note", ITEM, "--text", "no publish", "--seat", "BENCH", "--why", "t")
    check(rc == 0 and "PUBLISHED" not in out and origin_sha(c) == before,
          "a-plain-write-runs-no-git: a note without --publish lands nothing")
    check(git(c, "status", "--porcelain", "--", EVENTS_REL).endswith("BENCH.jsonl"),
          "a-plain-write-runs-no-git: the shard stays written, dirty")
    # in process: main without --publish never calls land
    sys.path.insert(0, HERE)
    import rimflow.cli as C
    orig = C.ledger_landing.land
    C.ledger_landing.land = lambda *a, **k: calls.append(a) or 0
    try:
        env = cli_env(c)
        old = {k: os.environ.get(k) for k in env}
        os.environ.update(env)
        try:
            C.main(["note", ITEM, "--text", "in process", "--seat", "BENCH", "--why", "t"])
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
    finally:
        C.ledger_landing.land = orig
    check(calls == [] and real is subprocess.run, "a-plain-write-runs-no-git: main() without --publish never lands")


def t_a_failed_landing_is_named():
    c = seeded("failed")
    git(c, "remote", "set-url", "origin", os.path.join(TMP, "no-such-remote.git"))
    rc, out, err = rimflow(c, "note", ITEM, "--text", "x", "--seat", "BENCH", "--why", "t", "--publish")
    check(rc == LL.LANDING_FAILED, "a-failed-landing-is-named: exit %d on an unreachable origin (got %d)"
          % (LL.LANDING_FAILED, rc))
    check("WRITTEN, NOT PUBLISHED" in out and "./publish -m 'ledger: %s note' %s" % (ITEM, SEAT_SHARD) in out,
          "a-failed-landing-is-named: names the cause and the exact command: %s" % out.strip()[-300:])
    with open(os.path.join(c, EVENTS_REL, "BENCH.jsonl")) as f:
        check('"text":"x"' in f.read(), "a-failed-landing-is-named: the write itself stays")
    # unit: a publish that exits 0 but prints no PUBLISHED line is not a landing
    fake = lambda argv, **k: subprocess.CompletedProcess(argv, 0, "no change in the named paths\n", "")  # noqa: E731
    buf = io.StringIO()
    p = os.path.join(c, SEAT_SHARD)
    rc2 = LL.land("note", ITEM, 0, paths=[p], runner=lambda argv, **k: fake(argv) if "publish.py" in " ".join(argv)
                  else subprocess.run(argv, **k), out=buf)
    check(rc2 == LL.LANDING_FAILED, "a-failed-landing-is-named: exit 0 with no PUBLISHED line is a failed landing")
    buf = io.StringIO()
    rc3 = LL.land("note", ITEM, 0, paths=[os.path.join(TMP, "outside", "x.jsonl")], out=buf)
    check(rc3 == LL.LANDING_FAILED and "not in a git clone" in buf.getvalue(),
          "a-failed-landing-is-named: a path outside any clone is named, not landed: %s" % buf.getvalue().strip())


def t_a_write_of_nothing_says_so():
    c = seeded("nothing")
    before = origin_sha(c)
    rc, out, err = rimflow(c, "show", ITEM, "--publish")
    check(rc == 0 and "nothing to publish" in out and origin_sha(c) == before,
          "a-write-of-nothing-says-so: a read with --publish says so and lands nothing (rc %d)" % rc)


def t_a_refused_verb_lands_nothing():
    c = seeded("refused")
    before = origin_sha(c)
    rc, out, err = rimflow(c, "note", "RIMMANDRAKE_PROBE_NO_SUCH_ITEM_ANYWHERE_HERE", "--text", "x", "--seat", "BENCH",
                           "--why", "t", "--publish")
    check(rc != 0 and "PUBLISHED" not in out and origin_sha(c) == before,
          "a-refused-verb-lands-nothing: a refused note lands nothing (rc %d)" % rc)
    buf = io.StringIO()
    rc2 = LL.land("note", ITEM, 2, paths=[os.path.join(c, SEAT_SHARD)], out=buf)
    check(rc2 == 2 and "NOT PUBLISHED (the command exited 2)" in buf.getvalue() and SEAT_SHARD in buf.getvalue(),
          "a-refused-verb-lands-nothing: a refusal after a write names the paths and the command")


def t_records_the_shard_each_append_wrote():
    d = os.path.join(TMP, "records")
    os.makedirs(d)
    saved = model.EVENTS
    model.EVENTS = os.path.join(d, "events.jsonl")
    try:
        LL.reset()
        model.append({"seat": "BENCH", "event": "note", "id": "X_Y_Z", "text": "t"})
        model.append({"seat": "OWNER", "event": "game", "state": "UP", "why": "delegated: t"})
        got = [os.path.basename(p) for p in LL.written()]
        check(got == ["BENCH.jsonl", "OWNER.jsonl"], "records-the-shard-each-append-wrote: seat shard, then OWNER.jsonl "
              "for a flagless OWNER event (./game --why): %s" % got)
        LL.reset()
        try:
            model.append({"seat": "NOBODY", "event": "note", "id": "X_Y_Z", "text": "t"})
        except model.LedgerError:
            pass
        check(LL.written() == [], "records-the-shard-each-append-wrote: a refused append records nothing")
    finally:
        model.EVENTS = saved
        LL.reset()
    import importlib.util
    spec = importlib.util.spec_from_file_location("ledger_landing", os.path.join(HERE, "ledger_landing.py"))
    sys.modules["ledger_landing"] = twin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(twin)
    twin.wrote("/x/y")
    check(LL.written() == ["/x/y"], "records-the-shard-each-append-wrote: both import names share one record")
    LL.reset()
    del sys.modules["ledger_landing"]


# ---------------------------------------------------------------------------------------------------------------------
def shard_of(path):
    return os.path.basename(path)[:-len(".jsonl")]


def old_brief(ev, helper_seat):
    """The detached brief's prose rule, as written (detached_helper.FOOTER before this item)."""
    return {helper_seat} | ({"OWNER"} if any(ev.get(k) for k in FLAGS) else set())


def old_publish_command(ev, helper_seat):
    """detached_helper.publish_command's filed-nowhere route: the launch seat's shard and OWNER.jsonl, always both."""
    return {helper_seat, "OWNER"}


def tree_events():
    for p in sorted(glob.glob(os.path.join(REPO, EVENTS_REL, "*.jsonl"))):
        with open(p, encoding="utf-8") as f:
            for ln in f:
                if ln.strip():
                    yield shard_of(p), json.loads(ln)


def sample_events():
    with open(SAMPLE, encoding="utf-8") as f:
        for ln in f:
            row = json.loads(ln)
            yield row["shard"], row["event"]


def equivalence(rows, label):
    """Replay each recorded event through model.append into a temp ledger; -> counts by class."""
    d = tempfile.mkdtemp(prefix="eq_", dir=TMP)
    saved = model.EVENTS
    model.EVENTS = os.path.join(d, "events.jsonl")
    n = collections.Counter()
    diffs = collections.Counter()
    try:
        for shard, ev in rows:
            n["events"] += 1
            e = model.from_disk(copy.deepcopy(ev))
            helper = model.canonical(e.get("ranBy") or e.get("seat") or "?")
            if helper == "RELENTLESS":
                helper = "BENCH"
            want = shard        # the file it lives in: from_disk folds CONDUCTOR/RELENTLESS back to the key whose shard it is
            LL.reset()
            try:
                model.append(e)
            except model.LedgerError as x:
                n["not replayable (validate refused today: %s)" % type(x).__name__] += 1
                continue
            got = [shard_of(p) for p in LL.written()]
            n["new exact"] += got == [want]
            if got != [want]:
                diffs["NEW differs: in %s, recorded %s (%s)" % (shard, got, e.get("event"))] += 1
            for name, old in (("brief rule", old_brief), ("publish_command", old_publish_command)):
                s = old(ev, helper)
                if want not in s:
                    diffs["OLD %s misses %s.jsonl (%s, no owner flag)" % (name, want, e.get("event"))] += 1
                elif s != {want}:
                    n["OLD %s over-names (harmless)" % name] += 1
    finally:
        model.EVENTS = saved
        LL.reset()
    print("equivalence on %s: %s" % (label, dict(n)))
    for k, v in sorted(diffs.items()):
        print("    %6d  %s" % (v, k))
    return n, diffs


def t_matches_every_recorded_event(rows=None, label="the frozen sample"):
    n, diffs = equivalence(rows if rows is not None else list(sample_events()), label)
    check(n["events"] > 0, "matches-every-recorded-event: the sample is not empty (%d events)" % n["events"])
    replayed = n["events"] - sum(v for k, v in n.items() if k.startswith("not replayable"))
    check(replayed > 0 and n["new exact"] == replayed, "matches-every-recorded-event: the new home records the event's "
          "own shard for %d of %d replayed" % (n["new exact"], replayed))
    check(not any(k.startswith("NEW") for k in diffs), "matches-every-recorded-event: no NEW difference")
    check(any(k.startswith("OLD brief rule misses OWNER.jsonl") for k in diffs) or label != "the frozen sample",
          "matches-every-recorded-event: the sample holds the case the old brief rule missed (a flagless OWNER event)")


def freeze():
    """Up to 2 newest events per (shard, disk seat, event, flagged) group: every kind the tree holds, small."""
    groups = collections.defaultdict(list)
    for shard, ev in tree_events():
        groups[(shard, ev.get("seat"), ev.get("event"), any(ev.get(k) for k in FLAGS))].append(ev)
    rows = [{"shard": k[0], "event": e} for k in sorted(groups, key=str) for e in groups[k][-2:]]
    with open(SAMPLE, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    print("froze %d events from %d groups into %s" % (len(rows), len(groups), SAMPLE))


def main(argv):
    if argv[:1] == ["--freeze"]:
        freeze()
        return 0
    if argv[:1] == ["--all"]:
        t_matches_every_recorded_event(list(tree_events()), "every event in this tree")
    else:
        t_records_the_shard_each_append_wrote()
        t_matches_every_recorded_event()
        t_publish_lands_exactly_the_written_paths()
        t_a_ledger_write_waits_for_no_peer_and_takes_no_peer_commit()
        t_records_the_item_prose_a_write_made()
        t_a_plain_write_runs_no_git()
        t_a_failed_landing_is_named()
        t_a_write_of_nothing_says_so()
        t_a_refused_verb_lands_nothing()
    print("%s: %d failed" % ("FAIL" if FAIL else "PASS", len(FAIL)))
    if not FAIL:
        shutil.rmtree(TMP, ignore_errors=True)      # kept on a red, for the reader
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
