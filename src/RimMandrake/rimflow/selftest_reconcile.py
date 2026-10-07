#!/usr/bin/env python3
"""Selftest for rimflow redesign step 1: the git check before `next` offers an item,
and the `reconcile` verb.

    python3 src/RimMandrake/rimflow/selftest_reconcile.py

Two halves. The UNIT half calls `gitindex` / `reconcile` / `model` in process. The CLI
half drives the real `cli.py` as a subprocess against a throwaway ledger
(`RIMFLOW_LEDGER`/`RIMFLOW_ITEMS`, the same hatch `selftest_cli.py` proves) and a git
FIXTURE (`RIMFLOW_GITINDEX=<json>`), so no case ever reads this repo's real history or
writes its real ledger. The last case checks the real ledger was never touched.

🔑 The case the redesign exists for is `t_same_item_built_twice_yet_offered`: an item
claimed, built in two commits, re-claimed — and `next` must say RECONCILE, not "build".
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "cli.py")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TMP_ROOT = os.path.join(REPO, ".rimflow_selftest_reconcile")   # beside the code, as selftest_cli
sys.path.insert(0, os.path.dirname(HERE))

from rimflow import gitindex, model, reconcile                  # noqa: E402

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
LATER = "2099-01-01T00:00:%02dZ"        # after any item this test files
EARLIER = "2000-01-01T00:00:00Z"        # before any item this test files


def sha(n):
    """A fake 40-hex sha with a digit in its first 9 (so the short form is unique)."""
    return "%09x" % (0xa10000000 + n) + "%031x" % n


def short(n):
    return sha(n)[:9]


def commit(n, subject, body="", files=("src/RimMandrake/Mod/Defs/X.xml",), t=None):
    return {"sha": sha(n), "ts": t or LATER % n, "subject": subject, "body": body,
            "files": list(files)}


def fresh(name):
    d = os.path.join(TMP_ROOT, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "items"))
    _TMP["dir"] = d
    write_fixture([])
    return d


def write_fixture(commits):
    with open(os.path.join(_TMP["dir"], "gitfixture.json"), "w") as fh:
        json.dump({"ref": "origin/main", "head": "f" * 40, "commits": commits}, fh)


def env(seat="FOUNDRY", fixture=True):
    e = {k: v for k, v in os.environ.items()
         if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_GITINDEX")}
    e["RIMFLOW_LEDGER"] = os.path.join(_TMP["dir"], "events.jsonl")
    e["RIMFLOW_ITEMS"] = os.path.join(_TMP["dir"], "items")
    e["RIMFLOW_PROBE"] = "no-reading"
    e["RIMFLOW_SEAT"] = seat
    if fixture:
        e["RIMFLOW_GITINDEX"] = os.path.join(_TMP["dir"], "gitfixture.json")
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
        " ".join(args), rc, out.strip()[-600:], err.strip()[-600:])
    return out


def refused(*args, **kw):
    rc, out, err = run(*args, **kw)
    assert rc != 0, "`%s` should have been refused and exited 0:\n%s" % (" ".join(args), out)
    return err


def ledger_bytes():
    """Every ledger file under this case's dir, path -> bytes (the shards included)."""
    out = {}
    for root, _dirs, files in os.walk(_TMP["dir"]):
        for f in files:
            if f.endswith(".jsonl"):
                p = os.path.join(root, f)
                with open(p, "rb") as fh:
                    out[p] = fh.read()
    return out


def ledger_events():
    evs = []
    for p, b in sorted(ledger_bytes().items()):
        evs += [json.loads(l) for l in b.decode().splitlines() if l.strip()]
    return evs


def file_ready(iid, seat="FOUNDRY"):
    """Filed and in plain `ready`. Step 3: `claim` now leases and STARTS the item, so the
    route to an unleased `ready` item is claim + the owning seat's own `reclaim`."""
    ok("file", iid, "--for", seat, "--title", "test item %s" % iid, seat=seat)
    ok("claim", iid, seat=seat)
    ok("reclaim", iid, seat=seat)


def release_offer(out, iid, seat="FOUNDRY"):
    """Give back the lease a non-peek `next` took (step 3), so the next call sees it."""
    import re as _re
    m = _re.search(r"lease token (\S+)", out)
    assert m, "next reserved nothing:\n" + out
    ok("release", iid, "--token", m.group(1), seat=seat)


def state_of(iid):
    out = ok("show", iid)
    return out.splitlines()[0].split()[1]

# ---------------------------------------------------------------------------
# UNIT CASES
# ---------------------------------------------------------------------------
def _fixture_index(commits):
    d = os.path.join(TMP_ROOT, "_unit")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "fx.json")
    with open(path, "w") as fh:
        json.dump({"ref": "origin/main", "head": "e" * 40, "commits": commits}, fh)
    return gitindex.from_fixture(path)


def t_index_reads_subjects_and_both_trailers():
    idx = _fixture_index([
        commit(1, "WRECK_FIELD_BUILD_1 slice 1: families"),
        commit(2, "Belt batch: three things", body="Some prose.\n\nCloses: LANCE_TETHER_PULL_1\n"
               "Implemented: STELLOCK_LACE_FORM_2, NEST_SORT_JOB_3\nCo-Authored-By: x"),
        commit(3, "plain subject naming nothing"),
        commit(4, "SUFFIX_WRECK_FIELD_BUILD_1 is a different id"),
    ])
    assert [m.short for m in idx.matches("WRECK_FIELD_BUILD_1")] == [short(1)], \
        idx.matches("WRECK_FIELD_BUILD_1")
    assert idx.matches("LANCE_TETHER_PULL_1")[0].how == "closes"
    assert [m.how for m in idx.matches("NEST_SORT_JOB_3")] == ["implemented"]
    assert idx.matches("STELLOCK_LACE_FORM_2"), "comma-separated Implemented: missed"
    assert idx.resolve(short(3)) is not None, "a commit naming nothing must still resolve"
    assert idx.resolve("abcdef") is None, "a 6-char prefix is not a sha"


def t_index_skips_bookkeeping_and_commits_before_creation():
    idx = _fixture_index([
        commit(1, "ledger: WRECK_FIELD_BUILD_1 noted",
               files=["infrastructure/state/ledger/events/FOUNDRY.jsonl"]),
        commit(2, "WRECK_FIELD_BUILD_1: an old mention", t=EARLIER),
        commit(3, "WRECK_FIELD_BUILD_1: the build"),
    ])
    got = [m.short for m in idx.matches("WRECK_FIELD_BUILD_1", since="2026-01-01T00:00:00Z")]
    assert got == [short(3)], got
    assert len(idx.matches("WRECK_FIELD_BUILD_1", include_bookkeeping=True)) == 3


def t_real_git_log_format_parses():
    """The parser on output shaped exactly like `git log _LOG_FORMAT --name-only`."""
    out = ("\x1e%s\x1f1791311617\x1fWRECK_FIELD_BUILD_1 slice 2: x\x1fbody\n\nCloses: "
           "NEST_SORT_JOB_3\n\x1f\n\nsrc/a.xml\nsrc/b.cs\n"
           "\x1e%s\x1f1791311000\x1fno ids here\x1f\x1f\n\nTransient/x.md\n") % (sha(1), sha(2))
    named, every = gitindex._parse_log(out)
    assert len(every) == 2 and len(named) == 1, (named, every)
    assert named[0][4] == {"WRECK_FIELD_BUILD_1": "subject", "NEST_SORT_JOB_3": "closes"}
    assert named[0][3] is False and named[0][1].endswith("Z")


def _item(iid="WRECK_FIELD_BUILD_1", created="2026-01-01T00:00:00Z"):
    it = model.Item(iid, 0)
    it.created_at, it.state, it.owner = created, "ready", "FOUNDRY"
    return it


def t_assess_kinds_and_verdict_suppression():
    idx = _fixture_index([commit(1, "WRECK_FIELD_BUILD_1 slice 1"),
                          commit(2, "WRECK_FIELD_BUILD_1 slice 2")])
    it = _item()
    assert reconcile.assess(it, idx).kind == "reconcile"
    assert reconcile.assess(it, None).kind == "build", "no git must never trigger"
    it.reconciles.append({"ts": "t1", "seat": "FOUNDRY", "verdict": "partial",
                          "shas": [short(1)], "remaining": "art"})
    a = reconcile.assess(it, idx)
    assert a.kind == "reconcile" and [m.short for m in a.unjudged] == [short(2)], a
    it.reconciles.append({"ts": "t2", "seat": "FOUNDRY", "verdict": "unrelated",
                          "shas": [short(2)], "remaining": None})
    a = reconcile.assess(it, idx)
    assert a.kind == "partial" and a.standing["remaining"] == "art", \
        "`unrelated` must not revoke the standing `partial`: %r" % a
    it.reconciles.append({"ts": "t3", "seat": "FOUNDRY", "verdict": "complete",
                          "shas": [sha(1)], "remaining": None})
    assert reconcile.assess(it, idx).kind == "complete"
    offers, skipped = reconcile.guard([it, _item("OTHER_THING_BUILD_1")], idx)
    assert [a.item.id for a in skipped] == ["WRECK_FIELD_BUILD_1"]
    assert [a.item.id for a in offers] == ["OTHER_THING_BUILD_1"]


def t_note_cited_sha_triggers_only_when_published():
    """WEBWORK_TRACTION_LANCE_BUILD_1's shape: the build commit names no item; only the
    item's own note cites it."""
    idx = _fixture_index([commit(7, "Belt batch: lance + lace (offline builds)")])
    it = _item("LANCE_TETHER_PULL_1")
    it.cited_shas = [short(7), "deadbee9", "1234567"]       # two not on the ref
    a = reconcile.assess(it, idx)
    assert a.kind == "reconcile" and [m.short for m in a.unjudged] == [short(7)], a
    assert a.unjudged[0].how == "note"


def t_model_reconcile_validates_and_changes_no_state():
    base = [{"seat": "FOUNDRY", "event": "file", "id": "WRECK_FIELD_BUILD_1", "for": "FOUNDRY",
             "title": "t", "kind": "task", "ts": "2026-01-01T00:00:00Z"},
            {"seat": "FOUNDRY", "event": "claim", "id": "WRECK_FIELD_BUILD_1",
             "ts": "2026-01-01T00:00:01Z"},
            {"seat": "FOUNDRY", "event": "note", "id": "WRECK_FIELD_BUILD_1",
             "ts": "2026-01-01T00:00:02Z", "text": "built at 598dec613; defaced is a word"}]
    good = {"seat": "BENCH", "event": "reconcile", "id": "WRECK_FIELD_BUILD_1",
            "verdict": "partial", "sha": "598dec613 a10000001", "remaining": "art install",
            "ts": "2026-01-01T00:00:03Z"}
    w = model.replay(base + [good])
    it = w.items["WRECK_FIELD_BUILD_1"]
    assert not w.errors, w.errors
    assert it.state == "ready" and it.owner == "FOUNDRY", "reconcile moved state/owner"
    assert it.cited_shas == ["598dec613"], it.cited_shas
    assert it.reconciles[0]["shas"] == ["598dec613", "a10000001"]
    for bad, why in ((dict(good, verdict="done"), "verdict"),
                     (dict(good, sha="XYZ"), "sha"),
                     (dict(good, remaining=""), "partial without remaining"),
                     (dict(good, reason="x"), "unknown field")):
        try:
            model.validate(dict(bad))
        except model.SchemaError:
            continue
        raise AssertionError("validate accepted a bad reconcile (%s)" % why)


def t_old_readers_ignore_reconcile():
    """A clone whose model predates the verb collects it into `world.errors` and
    projects every item exactly as before — never fatal, never a state change."""
    evs = [{"seat": "FOUNDRY", "event": "file", "id": "WRECK_FIELD_BUILD_1", "for": "FOUNDRY",
            "title": "t", "kind": "task", "ts": "2026-01-01T00:00:00Z"},
           {"seat": "FOUNDRY", "event": "claim", "id": "WRECK_FIELD_BUILD_1",
            "ts": "2026-01-01T00:00:01Z"},
           {"seat": "FOUNDRY", "event": "reconcile", "id": "WRECK_FIELD_BUILD_1",
            "verdict": "complete", "sha": "598dec613", "ts": "2026-01-01T00:00:02Z"}]
    saved = model.VERBS.pop("reconcile")
    try:
        old = model.replay(evs)
    finally:
        model.VERBS["reconcile"] = saved
    new = model.replay(evs)
    assert len(old.errors) == 1 and "unknown verb" in old.errors[0][2], old.errors
    o, n = old.items["WRECK_FIELD_BUILD_1"], new.items["WRECK_FIELD_BUILD_1"]
    assert (o.state, o.owner, o.blocked) == (n.state, n.owner, n.blocked) == \
        ("ready", "FOUNDRY", False)
    assert [e["event"] for e in model.canonical_order(list(reversed(evs)))] == \
        ["file", "claim", "reconcile"]

# ---------------------------------------------------------------------------
# CLI CASES — the real command, a throwaway ledger, a git fixture
# ---------------------------------------------------------------------------
def t_same_item_built_twice_yet_offered():
    """THE case: claimed, built in two commits, re-claimed. Before step 1 `next`
    offered it as fresh build work (SALVAGE_WRECKAGE_EVERYWHERE_1, 2026-10-06/07)."""
    fresh("built_twice")
    file_ready("WRECK_FIELD_BUILD_1")
    write_fixture([commit(1, "WRECK_FIELD_BUILD_1 slice 1: wreck families"),
                   commit(2, "WRECK_FIELD_BUILD_1 slice 2: placement + density")])
    # the second claim, hours later. Step 3: a claim now STARTS the item under a lease, so
    # it is no longer re-offered at all; `reclaim` puts it back in the pool, which is the
    # state this case is about (a ready item git already names).
    ok("claim", "WRECK_FIELD_BUILD_1")
    ok("reclaim", "WRECK_FIELD_BUILD_1")
    # the rendered queue's top entry says the same thing (render-on-read). Read BEFORE the
    # non-peek `next`, which reserves the item and so moves it to IN PROGRESS.
    view = ok("queue", "FOUNDRY")
    top = view[view.index("# NEXT"):]
    assert "action:   RECONCILE WRECK_FIELD_BUILD_1" in top, top[:1500]
    out = ok("next")
    assert "RECONCILE WRECK_FIELD_BUILD_1: commits %s %s" % (short(1), short(2)) in out, out
    assert "rimflow claim WRECK_FIELD_BUILD_1 --token" not in out, \
        "a built item was offered as build work:\n" + out
    assert "rimflow reconcile WRECK_FIELD_BUILD_1 --verdict" in out
    assert state_of("WRECK_FIELD_BUILD_1") == "ready", "next changed the state"
    view = ok("queue", "FOUNDRY")
    assert "lease:    LIVE" in view, "the reserved item must show as active:\n" + view[:2000]


def t_peek_writes_nothing():
    fresh("peek")
    file_ready("WRECK_FIELD_BUILD_1")
    write_fixture([commit(1, "WRECK_FIELD_BUILD_1 slice 1")])
    before = ledger_bytes()
    out = ok("next", "--peek")
    assert "RECONCILE WRECK_FIELD_BUILD_1" in out and "[peek:" in out, out
    assert ledger_bytes() == before, "`next --peek` wrote the ledger"


def t_partial_keeps_item_offered_with_remaining_line():
    fresh("partial")
    file_ready("WRECK_FIELD_BUILD_1")
    write_fixture([commit(1, "WRECK_FIELD_BUILD_1 slice 1"),
                   commit(2, "WRECK_FIELD_BUILD_1 slice 2")])
    refused("reconcile", "WRECK_FIELD_BUILD_1", "--verdict", "partial",
            "--sha", short(1), short(2))                     # partial needs --remaining
    ok("reconcile", "WRECK_FIELD_BUILD_1", "--verdict", "partial", "--sha", short(1),
       short(2), "--remaining", "slices 3-9: nest, appraisal, incident")
    out = ok("next")
    assert "RECONCILE" not in out, "judged commits were offered again:\n" + out
    assert "PARTLY BUILT" in out and "slices 3-9: nest, appraisal, incident" in out, out
    assert "-> rimflow claim WRECK_FIELD_BUILD_1" in out, out
    release_offer(out, "WRECK_FIELD_BUILD_1")
    ev = [e for e in ledger_events() if e["event"] == "reconcile"]
    assert len(ev) == 1 and ev[0]["id"] == "WRECK_FIELD_BUILD_1" and \
        ev[0]["sha"] == "%s %s" % (short(1), short(2)), ev
    assert state_of("WRECK_FIELD_BUILD_1") == "ready"
    # a NEW commit re-triggers, naming only the new one
    write_fixture([commit(1, "WRECK_FIELD_BUILD_1 slice 1"),
                   commit(2, "WRECK_FIELD_BUILD_1 slice 2"),
                   commit(3, "WRECK_FIELD_BUILD_1 slice 3")])
    out = ok("next")
    assert "RECONCILE WRECK_FIELD_BUILD_1: commits %s\n" % short(3) in out, out
    assert "Earlier verdict: PARTIAL" in out, out


def t_complete_is_not_offered_but_stays_open():
    fresh("complete")
    file_ready("WRECK_FIELD_BUILD_1")
    file_ready("YET_UNBUILT_THING_1")
    write_fixture([commit(1, "WRECK_FIELD_BUILD_1: whole build")])
    out = ok("next")
    assert "RECONCILE WRECK_FIELD_BUILD_1" in out, out       # oldest first: it is on top
    ok("reconcile", "WRECK_FIELD_BUILD_1", "--verdict", "complete", "--sha", short(1))
    release_offer(out, "WRECK_FIELD_BUILD_1")
    out = ok("next")
    assert "-> rimflow claim YET_UNBUILT_THING_1" in out, out
    assert "NOT offered as build work" in out and "WRECK_FIELD_BUILD_1" in out, out
    assert state_of("WRECK_FIELD_BUILD_1") == "ready", "complete must not close or move it"
    view = ok("queue", "FOUNDRY")
    assert "# RECONCILED COMPLETE" in view and "## WRECK_FIELD_BUILD_1" in view, view


def t_unrelated_returns_item_to_build_offer():
    fresh("unrelated")
    file_ready("WRECK_FIELD_BUILD_1")
    write_fixture([commit(1, "Docs sweep: mentions WRECK_FIELD_BUILD_1 in passing")])
    ok("reconcile", "WRECK_FIELD_BUILD_1", "--verdict", "unrelated", "--sha", short(1))
    out = ok("next")
    assert "RECONCILE" not in out and "-> rimflow claim WRECK_FIELD_BUILD_1" in out, out


def t_note_cited_build_commit_triggers():
    """WEBWORK_TRACTION_LANCE_BUILD_1's shape: a batch commit naming no item, linked
    only by the item's own note."""
    fresh("note_cited")
    file_ready("LANCE_TETHER_PULL_1")
    write_fixture([commit(5, "Belt batch: lance, lace, giant (offline builds)")])
    ok("note", "LANCE_TETHER_PULL_1", "--text",
       "%s: offline build published; live proof owed" % short(5))
    out = ok("next")
    assert "RECONCILE LANCE_TETHER_PULL_1: commits %s" % short(5) in out, out
    assert "cited in a note" in out, out


def t_bookkeeping_and_preexisting_commits_do_not_trigger():
    fresh("noise")
    file_ready("WRECK_FIELD_BUILD_1")
    write_fixture([commit(1, "ledger: WRECK_FIELD_BUILD_1 claimed",
                          files=["infrastructure/state/ledger/events/FOUNDRY.jsonl"]),
                   commit(2, "WRECK_FIELD_BUILD_1 named before it was filed", t=EARLIER)])
    out = ok("next")
    assert "RECONCILE" not in out and "-> rimflow claim WRECK_FIELD_BUILD_1" in out, out


def t_redirected_ledger_never_reads_real_history():
    """No fixture + a redirected ledger: the real repo's git must not be consulted, so a
    synthetic id that happens to exist in history cannot trigger."""
    fresh("no_fixture")
    file_ready("SALVAGE_WRECKAGE_EVERYWHERE_1")             # a REAL id with real commits
    out = ok("next", fixture=False)
    assert "RECONCILE" not in out and "-> rimflow claim SALVAGE_WRECKAGE_EVERYWHERE_1" in out, out


def t_reconcile_refuses_unknown_shas_and_items():
    fresh("refusals")
    file_ready("WRECK_FIELD_BUILD_1")
    write_fixture([commit(1, "WRECK_FIELD_BUILD_1 slice 1")])
    err = refused("reconcile", "WRECK_FIELD_BUILD_1", "--verdict", "complete",
                  "--sha", "0badc0de9")
    assert "0badc0de9" in err, err
    refused("reconcile", "NEVER_FILED_ITEM_1", "--verdict", "complete", "--sha", short(1))
    refused("reconcile", "WRECK_FIELD_BUILD_1", "--verdict", "maybe", "--sha", short(1))
    assert not [e for e in ledger_events() if e["event"] == "reconcile"], \
        "a refused reconcile reached the ledger"


def t_the_real_ledger_was_never_touched():
    real = model.shard_dir()
    assert os.path.isdir(real)
    for f in os.listdir(real):
        with open(os.path.join(real, f), encoding="utf-8") as fh:
            for line in fh:
                if '"event":"reconcile"' in line and "WRECK_FIELD_BUILD_1" in line:
                    raise AssertionError("a test reconcile reached the REAL ledger: %s" % f)


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
