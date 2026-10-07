#!/usr/bin/env python3
"""Selftest for rimflow redesign step 3: expiring claim leases and the dispatcher lock.

    python3 src/RimMandrake/rimflow/selftest_lease.py

Drives the real `cli.py` as subprocesses against a throwaway ledger in a temp dir
(`RIMFLOW_LEDGER`/`RIMFLOW_ITEMS`) and a git FIXTURE (`RIMFLOW_GITINDEX`), so no case reads
this repo's history or writes its ledger. The lock is the redirected-ledger lock beside the
temp ledger (lease.lock_path), never the real git dir's.

Cases: concurrent `next` callers get different items (with a sanity probe proving they DO
race for one top item without the lease); expiry -> re-offer labelled LAPSED, through the
git check, and RECONCILE when git names the item; wrong token refused; renew keeps it,
renew after expiry refused; claim hides the item and the queue view shows it active;
reassign/reclaim revoke; replay judges by event timestamps; an OLD reader (0884bcc72, the
last commit before step 3) tolerates every lease event.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "cli.py")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OLD_REF = "0884bcc72"
PKG = "src/RimMandrake/rimflow"
sys.path.insert(0, os.path.dirname(HERE))

from rimflow import lease, model                                  # noqa: E402

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


# ---------------------------------------------------------------------------
def fresh(name, commits=()):
    d = os.path.join(CTX["root"], name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "items"))
    CTX["dir"] = d
    with open(os.path.join(d, "gitfixture.json"), "w") as fh:
        json.dump({"ref": "origin/main", "head": "f" * 40, "commits": list(commits)}, fh)
    return d


def env(seat="FOUNDRY", ttl=None):
    e = {k: v for k, v in os.environ.items()
         if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_GITINDEX",
                      "RIMFLOW_LEASE_TTL", "RIMFLOW_DISPATCH_LOCK")}
    e["RIMFLOW_LEDGER"] = os.path.join(CTX["dir"], "events.jsonl")
    e["RIMFLOW_ITEMS"] = os.path.join(CTX["dir"], "items")
    e["RIMFLOW_PROBE"] = "no-reading"
    e["RIMFLOW_SEAT"] = seat
    e["RIMFLOW_GITINDEX"] = os.path.join(CTX["dir"], "gitfixture.json")
    if ttl is not None:
        e["RIMFLOW_LEASE_TTL"] = str(ttl)
    return e


def run(*args, **kw):
    cli = kw.get("cli", CLI)
    p = subprocess.run([sys.executable, cli] + list(args), capture_output=True, cwd=REPO,
                       env=env(kw.get("seat", "FOUNDRY"), kw.get("ttl")))
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def ok(*args, **kw):
    rc, out, err = run(*args, **kw)
    assert rc == 0, "`%s` exited %d\n  stdout: %s\n  stderr: %s" % (
        " ".join(args), rc, out.strip()[-700:], err.strip()[-700:])
    return out


def refused(needle, *args, **kw):
    rc, out, err = run(*args, **kw)
    assert rc != 0, "`%s` should have been refused:\n%s" % (" ".join(args), out)
    assert needle.lower() in (out + err).lower(), "refused without %r:\n%s%s" % (needle, out, err)
    return err


def ready(iid, seat="FOUNDRY"):
    """Filed, then plain `ready` and unleased (claim + the owning seat's own reclaim)."""
    ok("file", iid, "--for", seat, "--title", "lease test %s" % iid, seat=seat)
    ok("claim", iid, seat=seat)
    ok("reclaim", iid, seat=seat)


def reserved(out):
    """-> (item id, token) a `next`/`claim` reserved, from its printed instructions."""
    m = re.search(r"rimflow renew (\S+) --token (\S+)", out)
    assert m, "nothing was reserved:\n" + out
    return m.group(1), m.group(2)


def events(verb=None):
    out = []
    for root, _d, files in os.walk(CTX["dir"]):
        for f in files:
            if f.endswith(".jsonl"):
                with open(os.path.join(root, f), encoding="utf-8") as fh:
                    out += [json.loads(l) for l in fh if l.strip()]
    return [e for e in out if verb is None or e.get("event") == verb]


def parallel(n, *args, **kw):
    """Run `cli.py *args` n times at once (released together); -> [stdout]."""
    gate = threading.Barrier(n)
    outs = [None] * n

    def one(i):
        gate.wait()
        outs[i] = ok(*args, **kw)
    ts = [threading.Thread(target=one, args=(i,)) for i in range(n)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return outs


# ---------------------------------------------------------------------------
N = 6


def t_peek_callers_race_for_one_item_sanity_probe():
    """The failure shape, measured: without a reservation every caller gets the SAME top
    item. If this ever stops holding, the concurrency case below proves nothing."""
    fresh("probe")
    for i in range(N):
        ready("RACE_ITEM_HERE_%d" % (i + 1))
    outs = parallel(N, "next", "--peek")
    tops = {o.split("\n")[1].split()[0] for o in outs}
    assert tops == {"RACE_ITEM_HERE_1"}, tops


def t_concurrent_next_callers_get_different_items():
    fresh("concurrent")
    for i in range(N):
        ready("RACE_ITEM_HERE_%d" % (i + 1))
    outs = parallel(N, "next")
    got = [reserved(o) for o in outs]
    ids = [g[0] for g in got]
    assert len(set(ids)) == N, "two callers were handed the same item: %r" % ids
    assert len({g[1] for g in got}) == N, "tokens must be unique per reservation"
    # exactly one `take` per caller (the fixture's own claim+reclaim leases excluded)
    takes = [e for e in events("lease") if e["token"] in {g[1] for g in got}]
    assert len(takes) == N and all(e["action"] == "take" for e in takes), takes
    # a seventh caller finds every item reserved -> nothing, and says why
    out = ok("next")
    assert "nothing offered" in out and "LEASED" in out, out
    # ...and the state did not move: a reservation is not a start
    w = model.replay(_read())
    assert all(w.items[i].state == "ready" for i in ids), {i: w.items[i].state for i in ids}


def t_concurrent_claimable_offers_are_reserved_too():
    """`next` with nothing ranked offers the oldest PROPOSED item; that is reserved too."""
    fresh("concurrent_proposed")
    for i in range(3):
        ok("file", "PROPOSED_ITEM_HERE_%d" % (i + 1), "--for", "FOUNDRY", "--title", "p")
    outs = parallel(3, "next")
    ids = sorted(reserved(o)[0] for o in outs)
    assert ids == ["PROPOSED_ITEM_HERE_1", "PROPOSED_ITEM_HERE_2", "PROPOSED_ITEM_HERE_3"], ids


def t_wrong_token_refused():
    fresh("wrong_token")
    ready("TOKEN_CHECK_ITEM_1")
    iid, tok = reserved(ok("next"))
    refused("does not hold", "renew", iid, "--token", "FOUNDRY.someone.deadbeef")
    refused("does not hold", "release", iid, "--token", "FOUNDRY.someone.deadbeef")
    # a token-less claim is a TAKE, and the item is someone else's live lease
    refused("LEASED until", "claim", iid)
    # the holder's own token works, and the claim STARTS it
    out = ok("claim", iid, "--token", tok)
    assert "-> doing" in out, out
    ok("release", iid, "--token", tok)
    refused("already released", "release", iid, "--token", tok)


def _sleep_until(t):
    time.sleep(max(0.0, t - time.time()))


def t_renew_keeps_it_and_expiry_reoffers_through_the_git_check():
    """Stamps are whole seconds, so the timing is laid out against S = the take's stamp,
    which lies in [t0, t1] (before/after the `next` call). TTL 6 s:
      renew   at t1+3     -> floor >= S+3, so the renewed expiry is >= S+9 (and the renew
                             lands well before S+6, so it is live)
      check   at t1+6.05  -> floor >= S+6: the ORIGINAL lease has lapsed; the renewed one
                             (>= S+9) has not, so nothing may be offered
      expiry  at t1+11.1  -> past any renewed expiry (<= S+5+6)."""
    fresh("renew_expiry")
    ready("RENEWED_ITEM_HERE_1")
    iid, tok = reserved(ok("next", ttl=6))
    t1 = time.time()
    _sleep_until(t1 + 3.0)
    out = ok("renew", iid, "--token", tok, ttl=6)
    assert "renewed" in out, out
    _sleep_until(t1 + 6.05)
    out = ok("next", ttl=6)
    assert "nothing offered" in out, "a renewed lease was re-offered:\n" + out
    _sleep_until(t1 + 11.1)
    refused("EXPIRED", "renew", iid, "--token", tok, ttl=6)
    out = ok("next", ttl=6)
    assert reserved(out)[0] == iid, out
    assert "LAPSED LEASE" in out and "was checked: no unjudged commit" in out, out
    assert "rimflow claim %s --token" % iid in out, out


def t_expired_claim_comes_back_as_reconcile_when_git_names_it():
    """(d): a `doing` item whose lease lapsed is offerable again — but git names it, so the
    offer is RECONCILE, never 'build this'."""
    fresh("expiry_reconcile")
    ok("file", "BUILT_THEN_LAPSED_1", "--for", "FOUNDRY", "--title", "t")
    out = ok("claim", "BUILT_THEN_LAPSED_1", ttl=1)
    assert "-> doing" in out, out
    with open(os.path.join(CTX["dir"], "gitfixture.json"), "w") as fh:
        json.dump({"ref": "origin/main", "head": "f" * 40, "commits": [
            {"sha": "a1b2c3d4e" + "0" * 31, "ts": "2099-01-01T00:00:00Z",
             "subject": "BUILT_THEN_LAPSED_1: the whole build", "body": "",
             "files": ["src/RimMandrake/X/Defs/X.xml"]}]}, fh)
    time.sleep(2.2)
    out = ok("next")
    assert "RECONCILE BUILT_THEN_LAPSED_1" in out, out
    assert "LAPSED LEASE" in out and "judge them before anything is rebuilt" in out, out
    assert "rimflow claim BUILT_THEN_LAPSED_1 --token" not in out, out


def t_claim_hides_the_item_and_the_view_shows_it_active():
    fresh("claim_hides")
    ok("file", "CLAIMED_AND_HIDDEN_1", "--for", "FOUNDRY", "--title", "t")
    ok("file", "SECOND_IN_LINE_1", "--for", "FOUNDRY", "--title", "t")
    ok("claim", "CLAIMED_AND_HIDDEN_1")
    out = ok("next")
    assert reserved(out)[0] == "SECOND_IN_LINE_1", out
    view = ok("queue", "FOUNDRY")
    prog = view[view.index("# IN PROGRESS"):view.index("# BLOCKED")]
    assert "## CLAIMED_AND_HIDDEN_1" in prog and "## SECOND_IN_LINE_1" in prog, prog
    assert prog.count("lease:    LIVE") == 2, prog
    nxt = view[view.index("# NEXT"):view.index("# IN PROGRESS")]
    assert "## " not in nxt, nxt
    # why says who holds it, not "state is ready"
    assert "LEASED until" in ok("why", "SECOND_IN_LINE_1")


def t_start_still_works_and_reclaim_revokes():
    fresh("start_reclaim")
    ok("file", "SCRIPTED_START_ITEM_1", "--for", "FOUNDRY", "--title", "t")
    iid, tok = reserved(ok("next"))
    assert "-> doing" in ok("start", iid), "a bare start must keep working for scripts"
    ok("reclaim", iid)
    refused("does not hold", "renew", iid, "--token", tok)
    out = ok("next")
    assert reserved(out)[0] == iid and "LAPSED" not in out, out


def t_replay_judges_by_event_timestamps():
    """Liveness at replay is the event's own ts vs `expires` — pure over the ledger."""
    def ev(ts, **kw):
        return dict({"ts": ts, "seat": "FOUNDRY", "id": "PURE_REPLAY_ITEM_1"}, **kw)
    base = [ev("2026-10-07T00:00:00Z", event="file", title="t", kind="task",
               **{"for": "FOUNDRY"}),
            ev("2026-10-07T00:00:01Z", event="lease", action="take", token="FOUNDRY.a.00000001",
               expires="2026-10-07T00:45:01Z")]
    late_renew = ev("2026-10-07T00:46:00Z", event="lease", action="renew",
                    token="FOUNDRY.a.00000001", expires="2026-10-07T01:31:00Z")
    rival = ev("2026-10-07T00:30:00Z", event="lease", action="take",
               token="FOUNDRY.b.00000002", expires="2026-10-07T01:15:00Z")
    after = ev("2026-10-07T00:46:00Z", event="lease", action="take",
               token="FOUNDRY.b.00000002", expires="2026-10-07T01:31:00Z")
    w = model.replay(base + [late_renew])
    assert len(w.errors) == 1 and "EXPIRED" in w.errors[0][2], w.errors
    w = model.replay(base + [rival])
    assert len(w.errors) == 1 and "LEASED until" in w.errors[0][2], w.errors
    w = model.replay(base + [after])
    assert not w.errors and w.items["PURE_REPLAY_ITEM_1"].lease["token"].endswith("02")
    it = w.items["PURE_REPLAY_ITEM_1"]
    assert model.lease_status(it, model.epoch("2026-10-07T01:00:00Z")) == "live"
    assert model.lease_status(it, model.epoch("2026-10-07T01:31:00Z")) == "lapsed"
    too_long = ev("2026-10-07T00:00:02Z", event="lease", action="take",
                  token="FOUNDRY.c.00000003", expires="2026-10-08T00:00:00Z")
    w = model.replay(base[:1] + [too_long])
    assert w.errors and "maximum" in w.errors[0][2], w.errors


def t_real_ledger_lock_lives_in_this_clones_git_dir():
    """Computed only — nothing is created in the real git dir by this test."""
    saved = os.environ.pop("RIMFLOW_DISPATCH_LOCK", None)
    ev_saved = model.EVENTS
    try:
        model.EVENTS = os.path.join(model.STATE, "ledger", "events.jsonl")
        p = lease.lock_path()
        assert p == os.path.join(model.ROOT, ".git", lease.LOCK_NAME), p
    finally:
        model.EVENTS = ev_saved
        if saved is not None:
            os.environ["RIMFLOW_DISPATCH_LOCK"] = saved


# ---------------------------------------------------------------------------
# OLD READER — the rimflow package as committed at OLD_REF, on a ledger with leases
# ---------------------------------------------------------------------------
def extract_old_package(dest):
    names = subprocess.check_output(("git", "ls-tree", "--name-only", OLD_REF, PKG + "/"),
                                    cwd=REPO).decode().split()
    pkg = os.path.join(dest, "rimflow")
    os.makedirs(pkg)
    for n in names:
        if n.endswith(".py"):
            blob = subprocess.check_output(("git", "show", "%s:%s" % (OLD_REF, n)), cwd=REPO)
            with open(os.path.join(pkg, os.path.basename(n)), "wb") as fh:
                fh.write(blob)
    return os.path.join(pkg, "cli.py")


def t_old_reader_tolerates_leases():
    fresh("old_reader")
    old_cli = extract_old_package(os.path.join(CTX["dir"], "old"))
    ok("file", "OLD_SEES_CLAIMED_1", "--for", "FOUNDRY", "--title", "t")
    ready("OLD_SEES_RESERVED_1")
    ok("claim", "OLD_SEES_CLAIMED_1")                         # lease take + claim + start
    iid, tok = reserved(ok("next"))                         # lease take only
    assert iid == "OLD_SEES_RESERVED_1", iid
    ok("renew", iid, "--token", tok)
    code = ("import json,sys; sys.path.insert(0, %r)\n"
            "from rimflow import model, priority\n"
            "model.EVENTS = %r\n"
            "w = model.replay(model.read())\n"
            "print(json.dumps({'items': {k: v.state for k, v in w.items.items()},"
            " 'errors': [e[1] for e in w.errors],"
            " 'rank': [i.id for i in priority.rank(w, 'FOUNDRY')]}))\n"
            % (os.path.dirname(os.path.dirname(old_cli)),
               os.path.join(CTX["dir"], "events.jsonl")))
    p = subprocess.run([sys.executable, "-c", code], capture_output=True)
    assert p.returncode == 0, "the OLD model raised on a lease ledger:\n" + p.stderr.decode()
    r = json.loads(p.stdout.decode())
    CTX["old"] = r
    assert r["errors"] and set(r["errors"]) == {"lease"}, r["errors"]
    assert r["items"]["OLD_SEES_CLAIMED_1"] == "doing", r["items"]
    # ⚠️ the known gap: a reservation alone is invisible to an old clone
    assert r["items"]["OLD_SEES_RESERVED_1"] == "ready" and \
        r["rank"] == ["OLD_SEES_RESERVED_1"], r
    for args in (("next", "--peek"), ("show", iid), ("queue", "FOUNDRY"), ("why", iid)):
        ok(*args, cli=old_cli)


def report():
    r = CTX.get("old")
    if r:
        print("\nOLD CLONE (%s) on a step-3 ledger: %d lease events -> world.errors; "
              "claimed item %s; reserved-only item %s and offered by old rank: %s"
              % (OLD_REF, len(r["errors"]), r["items"]["OLD_SEES_CLAIMED_1"],
                 r["items"]["OLD_SEES_RESERVED_1"], ", ".join(r["rank"]) or "none"))


def _read():
    saved = model.EVENTS
    try:
        model.EVENTS = os.path.join(CTX["dir"], "events.jsonl")
        return model.read()
    finally:
        model.EVENTS = saved


if __name__ == "__main__":
    CTX["root"] = tempfile.mkdtemp(prefix="rimflow_lease_")
    try:
        for fn in (t_peek_callers_race_for_one_item_sanity_probe,
                   t_concurrent_next_callers_get_different_items,
                   t_concurrent_claimable_offers_are_reserved_too,
                   t_wrong_token_refused,
                   t_renew_keeps_it_and_expiry_reoffers_through_the_git_check,
                   t_expired_claim_comes_back_as_reconcile_when_git_names_it,
                   t_claim_hides_the_item_and_the_view_shows_it_active,
                   t_start_still_works_and_reclaim_revokes,
                   t_replay_judges_by_event_timestamps,
                   t_real_ledger_lock_lives_in_this_clones_git_dir,
                   t_old_reader_tolerates_leases):
            case(fn.__name__, fn)
        report()
    finally:
        shutil.rmtree(CTX["root"], ignore_errors=True)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
