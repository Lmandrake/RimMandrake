#!/usr/bin/env python3
"""Selftest for refresh.py's frozen-dump immunity.

⭐ WHY THIS RULE NEEDS A TEST RATHER THAN A COMMENT. The failure it prevents is
invisible and self-inflicting: if the official dump reads `STALE`, the board sits
permanently red, and sooner or later somebody clears the warning by re-freezing —
silently moving the design target that DECIDE and BUILD are both authoring against.
Nothing announces that. A stale warning is loud; a moved target is not.

⚠️ And the mismatch is not an edge case. Every new `Jawa_*` mod moves the live count by
one, so the official dump is drifting from the live list ALL THE TIME, on purpose.

    python3 src/RimMandrake/Utils/selftest_frozen_dumps.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import refresh                                                    # noqa: E402

PASS, FAIL = [], []


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as e:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, e))


def with_registry(lines):
    """Point refresh.registry() at a throwaway file under the repo."""
    d = tempfile.mkdtemp(prefix=".frozen_", dir=os.path.dirname(os.path.dirname(HERE)))
    path = os.path.join(d, "REGISTRY.jsonl")
    open(path, "w", encoding="utf-8").write("".join(lines))
    refresh._registry_path = lambda: path
    return d


# ⚠️ A REAL matching path, not a placeholder. An earlier draft used "…/DefDump", which
# matched nothing — so `t_a_verification_dump_is_never_immune` returned None because the
# PATH failed, not because `frozen` was False, and passed without ever exercising the
# rule it names. A test that passes for the wrong reason is worse than one that fails.
DUMP = ("C:/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios/DefDump")


def entry(**kw):
    d = {"id": "OFFICIAL-1", "kind": "official", "frozen": True,
         "modlist_count": 578, "path": "RimWorld by Ludeon Studios/DefDump",
         "by": "owner"}
    d.update(kw)
    return json.dumps(d) + "\n"


def t_frozen_entry_matches_by_suffix():
    """An absolute path from another machine must still resolve."""
    d = with_registry([entry()])
    try:
        got = refresh.frozen_entry(
            "C:/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
            "RimWorld by Ludeon Studios/DefDump")
        assert got and got["id"] == "OFFICIAL-1", got
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_verification_dump_is_never_immune():
    """`kind: verification` answers 'does the live game match?' — staleness applies."""
    d = with_registry([entry(id="verify-1", kind="verification", frozen=False,
                             modlist_count=13)])
    try:
        assert refresh.frozen_entry(DUMP) is None, (
            "a verification dump was treated as frozen; it would then never be "
            "reported stale, which is the only thing it is FOR")
        # …and prove the PATH is not what made it None, which is how this test
        # silently passed before.
        d2 = with_registry([entry(id="OFFICIAL-1", kind="official", frozen=True)])
        try:
            assert refresh.frozen_entry(DUMP) is not None, (
                "the path does not match at all, so the frozen=False case above "
                "proved nothing")
        finally:
            shutil.rmtree(d2, ignore_errors=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_newest_frozen_entry_wins():
    """The registry is append-only, so a re-freeze is a later line, not an edit."""
    d = with_registry([entry(id="OFFICIAL-1", modlist_count=575),
                       entry(id="OFFICIAL-2", modlist_count=578)])
    try:
        got = refresh.frozen_entry(DUMP)
        assert got and got["id"] == "OFFICIAL-2", got
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_torn_line_is_reported_not_skipped():
    """🔴 Silence here loses a frozen dump's immunity with no symptom at the cause."""
    d = with_registry([entry(), '{"id":"OFFICIAL-2","fro\n'])
    try:
        r = subprocess.run(
            [sys.executable, "-c",
             "import sys;sys.path.insert(0,%r);import refresh;"
             "refresh._registry_path=lambda: %r;refresh.registry()" % (HERE,
                                                                       os.path.join(d, "REGISTRY.jsonl"))],
            capture_output=True, text=True, timeout=30)
        assert "not valid JSON" in r.stdout, (
            "a malformed registry line was skipped silently. The symptom would be "
            "'the official dump went STALE', which points nowhere near the cause. "
            "Got: %r" % r.stdout[:200])
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_no_registry_is_not_an_error():
    d = with_registry([])
    try:
        os.unlink(os.path.join(d, "REGISTRY.jsonl"))
        assert refresh.registry() == []
        assert refresh.frozen_entry(DUMP) is None
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_the_shipped_registry_freezes_the_live_dump():
    """The real file, unmocked — the rule has to hold in the repo, not just in a test."""
    got = refresh.frozen_entry(refresh.D_DUMP)
    assert got and got.get("frozen") and got.get("kind") == "official", (
        "the shipped REGISTRY.jsonl does not freeze the live DefDump; it would go "
        "STALE on the next custom mod and demand a ~23-minute load for nothing. "
        "Got: %r" % (got,))


def t_a_root_freeze_still_covers_a_dated_capture():
    """🔴 The regression that the flat -> captures/ migration actually caused.

    Every shipped entry names the dump ROOT (`RimWorld by Ludeon Studios/DefDump`),
    but once the dump is migrated `DEF_DUMP` resolves to `<root>/captures/<id>`.
    A plain suffix match between the two fails, so the live dump read as NOT
    FROZEN and would have demanded a ~23-minute load for nothing. Measured
    2026-08-22 under DUMP_PRODUCER_DATED_CAPTURES_1.
    """
    d = with_registry(['{"id":"T","kind":"official","frozen":true,'
                       '"modlist_count":578,"path":"RimWorld by Ludeon Studios/DefDump",'
                       '"capturedUtc":"2026-08-21T22:44:59Z"}\n'])
    try:
        fe = refresh.frozen_entry(
            "/x/RimWorld by Ludeon Studios/DefDump/captures/2026-08-21T22-44-59Z")
        assert fe and fe.get("id") == "T", (
            "a freeze naming the dump ROOT must still cover a capture UNDER that "
            "root, or migrating the dump silently unfreezes it. Got: %r" % (fe,))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_freeze_naming_one_capture_does_not_cover_another():
    """🔑 The other half, and without it the fix above is a hole.

    Matching on the root alone would let an entry frozen at capture A report
    capture B as frozen — the exact silent-replacement failure the registry was
    hardened against, just reintroduced by the layout change.
    """
    d = with_registry(['{"id":"T","kind":"official","frozen":true,'
                       '"modlist_count":578,"path":"RimWorld by Ludeon Studios/DefDump",'
                       '"capture":"2026-08-21T22-44-59Z",'
                       '"capturedUtc":"2026-08-21T22:44:59Z"}\n'])
    try:
        fe = refresh.frozen_entry(
            "/x/RimWorld by Ludeon Studios/DefDump/captures/2026-08-22T09-11-02Z")
        assert fe is None, (
            "an entry naming capture 2026-08-21T22-44-59Z must NOT report a "
            "different capture as frozen. Got: %r" % (fe,))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_replaced_capture_is_not_reported_as_frozen():
    """🔴 A freeze that cannot detect replacement is not a freeze.

    Measured 2026-08-21: the registry froze 2026-08-20T15:08:30Z and the disk
    held 2026-08-21T08:20:20Z. Both were 578 mods, so the mod-count comparison
    — the only one the frozen branch made — saw nothing, and the design target
    moved silently. That is the failure this file's README calls worse than a
    stale warning.
    """
    d = with_registry(['{"id":"T","kind":"official","frozen":true,'
                       '"modlist_count":578,"path":"DefDump",'
                       '"capturedUtc":"2026-08-20T15:08:30Z"}\n'])
    try:
        fe = refresh.frozen_entry("/x/DefDump")
        assert fe, "the test registry did not take"
        assert fe["capturedUtc"] == "2026-08-20T15:08:30Z"
        # the branch must compare capturedUtc, not only the mod count
        src = open(os.path.join(HERE, "refresh.py"), encoding="utf-8").read()
        assert "REPLACED" in src, (
            "refresh.py no longer reports a replaced frozen capture")
        assert 'fe.get("capturedUtc")' in src, (
            "the frozen branch no longer compares capturedUtc, so a re-capture "
            "on the same mod count would pass unnoticed again")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _target_root(frozen_id, captured, extra_ids=()):
    """A throwaway DUMP_ROOT holding a frozen capture (manifest + defs body,
    so dump_fingerprint accepts it) plus optional empty newer captures."""
    root = tempfile.mkdtemp(prefix=".tgt_")
    cap = os.path.join(root, "captures", frozen_id)
    os.makedirs(os.path.join(cap, "defs"))
    json.dump({"capturedUtc": captured, "modCount": 2,
               "mods": [{"packageId": "a.one"}, {"packageId": "b.two"}]},
              open(os.path.join(cap, "manifest.json"), "w", encoding="utf-8"))
    open(os.path.join(cap, "defs", "ThingDef.json"), "w").write("{}")
    for i in extra_ids:
        d = os.path.join(root, "captures", i)
        os.makedirs(os.path.join(d, "defs"))
        json.dump({"capturedUtc": i.replace("-", ":").replace("T", "T", 1),
                   "modCount": 2,
                   "mods": [{"packageId": "a.one"}, {"packageId": "b.two"}]},
                  open(os.path.join(d, "manifest.json"), "w", encoding="utf-8"))
        open(os.path.join(d, "defs", "ThingDef.json"), "w").write("{}")
    return root, cap


def t_a_newer_capture_beside_the_frozen_one_is_not_replacement():
    """🔴 Measured 2026-09-04: three ordinary post-freeze captures sat beside
    the fully intact frozen one, and status() — comparing the freeze against
    the NEWEST capture — reported REPLACED after every game load, citing a
    superseded flat-layout entry while doing it. A permanent false alarm is
    how someone eventually re-freezes to clear the board, which is the silent
    target move the registry exists to prevent."""
    root, cap = _target_root("2026-08-29T13-30-02Z", "2026-08-29T13:30:02Z",
                             extra_ids=["2026-09-04T02-23-44Z"])
    sha = refresh.dump_fingerprint(cap)["hash"]
    reg = with_registry([
        entry(id="OFFICIAL-OLD", capturedUtc="2026-08-21T08:20:20Z"),
        entry(id="OFFICIAL-NEW", capture="2026-08-29T13-30-02Z",
              capturedUtc="2026-08-29T13:30:02Z", modlist_sha=sha)])
    try:
        fe, state, detail = refresh.design_target_state(root=root)
        assert fe and fe["id"] == "OFFICIAL-NEW", (
            "the ACTIVE freeze must be the newest entry, not %r" % (fe,))
        assert state == "FROZEN", (
            "an intact frozen capture with a newer sibling read %s (%s)"
            % (state, detail))
    finally:
        shutil.rmtree(reg, ignore_errors=True)
        shutil.rmtree(root, ignore_errors=True)


def t_a_genuinely_replaced_frozen_capture_still_reads_replaced():
    """The other half: the fix must not weaken detection. A manifest whose
    capturedUtc no longer says what the freeze recorded is a replacement."""
    root, cap = _target_root("2026-08-29T13-30-02Z", "2026-08-30T00:00:00Z")
    reg = with_registry([entry(id="OFFICIAL-NEW", capture="2026-08-29T13-30-02Z",
                               capturedUtc="2026-08-29T13:30:02Z")])
    try:
        _fe, state, _detail = refresh.design_target_state(root=root)
        assert state == "REPLACED", (
            "a rewritten frozen capture read %s" % state)
        # and a MISSING one is REPLACED too, not silently unfrozen
        shutil.rmtree(cap, ignore_errors=True)
        _fe, state, detail = refresh.design_target_state(root=root)
        assert state == "REPLACED" and "GONE" in detail, (state, detail)
    finally:
        shutil.rmtree(reg, ignore_errors=True)
        shutil.rmtree(root, ignore_errors=True)


def t_the_derived_db_is_outside_the_freeze():
    """`defs.sqlite` lives inside the frozen path and must NOT be frozen —
    it is a pure function of the capture, so rebuilding it cannot move the
    target, and freezing it would freeze its schema bugs."""
    readme = os.path.join(os.path.dirname(os.path.dirname(HERE)),
                          "..", "infrastructure", "state", "dumps", "README.md")
    readme = os.path.normpath(readme)
    if not os.path.exists(readme):
        return
    text = open(readme, encoding="utf-8").read()
    assert "defs.sqlite" in text and "never" in text.lower(), (
        "the README no longer records that the derived db is outside the freeze")


# ---------------------------------------------------------------------------
# `refresh.py --freeze` — folded in from freeze_dump.py, FREEZE_SHA_UNREPRODUCIBLE_1.
# The registry is append-only and points at the OWNER's design target, so every
# case below writes to a throwaway registry and a throwaway capture. None of
# them may touch the real one.
# ---------------------------------------------------------------------------

def _capture(captured="2026-09-01T00:00:00Z", mods=("a.one", "b.two")):
    """A throwaway DefDump holding only what freeze() reads."""
    d = tempfile.mkdtemp(prefix=".capture_")
    json.dump({"capturedUtc": captured, "gameVersion": "1.6.9999 rev1",
               "modCount": len(mods),
               "mods": [{"loadOrder": i + 1, "name": m, "packageId": m,
                         "rootDir": "/nowhere/" + m} for i, m in enumerate(mods)]},
              open(os.path.join(d, "manifest.json"), "w", encoding="utf-8"))
    return d


def t_a_dry_run_writes_nothing_and_says_so():
    reg = with_registry([entry(capturedUtc="2026-08-21T08:20:20Z")])
    before = open(refresh._registry_path(), encoding="utf-8").read()
    e, wrote = refresh.freeze(_capture(), by="")
    assert wrote is False, "a freeze with no --by owner reported that it wrote"
    assert open(refresh._registry_path(), encoding="utf-8").read() == before, (
        "the dry run appended to the registry anyway")
    assert e["id"] == "OFFICIAL-2026-09-01", e["id"]
    shutil.rmtree(reg, ignore_errors=True)


def t_only_the_owner_can_write_a_freeze():
    reg = with_registry([entry(capturedUtc="2026-08-21T08:20:20Z")])
    for who in ("BUILD", "check", "Owner", "owner "):
        _, wrote = refresh.freeze(_capture(), by=who)
        assert wrote is False, "`--by %s` was accepted as the owner" % who
    _, wrote = refresh.freeze(_capture(), by="owner")
    assert wrote is True, "the owner could not write a freeze"
    lines = [l for l in open(refresh._registry_path(), encoding="utf-8") if l.strip()]
    assert len(lines) == 2, "expected exactly one appended line, got %d" % len(lines)
    shutil.rmtree(reg, ignore_errors=True)


def t_the_sha_it_writes_is_reproducible():
    """🔴 The defect this item was filed for. `OFFICIAL-2026-08-21` carried
    `e0f11692cf69e516`, which no code on this machine produces. A freeze is a
    claim about an artifact, and a claim nobody can recompute can only be
    believed."""
    reg = with_registry([entry(capturedUtc="2026-08-21T08:20:20Z")])
    cap = _capture()
    e, _ = refresh.freeze(cap, by="")
    again = (refresh.dump_fingerprint(cap) or {}).get("hash") or "see manifest.json"
    assert e["modlist_sha"] == again, (
        "the sha in the entry (%s) is not what dump_fingerprint recomputes (%s)"
        % (e["modlist_sha"], again))
    shutil.rmtree(reg, ignore_errors=True)


def t_refreezing_the_same_capture_is_refused():
    """Not a courtesy. A no-op freeze is what "clear the warning" looks like."""
    reg = with_registry([entry(capturedUtc="2026-09-01T00:00:00Z")])
    try:
        refresh.freeze(_capture("2026-09-01T00:00:00Z"), by="owner")
        raise AssertionError("re-freezing the already-frozen capture was allowed")
    except RuntimeError as exc:
        assert "already frozen" in str(exc), str(exc)
    shutil.rmtree(reg, ignore_errors=True)


def t_a_writer_refuses_to_append_past_a_corrupt_line():
    """A READER degrades and warns; a WRITER must not. Appending past a line
    nobody can parse is how a frozen dump loses its immunity with the symptom
    nowhere near the cause."""
    reg = with_registry([entry(), "{not json at all\n"])
    assert len(refresh.registry()) == 1, "the lenient read should still return the good line"
    try:
        refresh.registry(strict=True)
        raise AssertionError("strict=True parsed a corrupt registry without complaint")
    except refresh.RegistryCorrupt:
        pass
    try:
        refresh.freeze(_capture(), by="owner")
        raise AssertionError("freeze appended past a corrupt registry line")
    except refresh.RegistryCorrupt:
        pass
    shutil.rmtree(reg, ignore_errors=True)


def t_freeze_is_reachable_from_the_command_line():
    """⛔ The whole point of FREEZE_SHA_UNREPRODUCIBLE_1: refresh.py's header has
    promised `--freeze` since 2026-08-20 and its argparse never had it. A
    capability named but not handed over is not handed over."""
    out = subprocess.run([sys.executable, os.path.join(HERE, "refresh.py"), "--help"],
                         capture_output=True, text=True).stdout
    assert "--freeze" in out, "refresh.py --help still does not offer --freeze"
    assert "--by" in out, "refresh.py --help does not mention --by"


def t_there_is_exactly_one_command_that_freezes():
    """Two tools answering one question is two answers. freeze_dump.py was folded
    into refresh.py rather than kept beside it."""
    assert not os.path.exists(os.path.join(HERE, "freeze_dump.py")), (
        "freeze_dump.py is back — either it or refresh.py --freeze must go")


def t_no_registry_entry_carries_an_unreproducible_sha():
    """The ACTIVE entry's sha must recompute. History is exempt, and the reason
    matters more than the rule.

    🔑 **A superseded entry describes a capture that no longer exists**, because
    a capture overwrites the previous one in place. Its sha was recomputable the
    day it was written and nothing on disk can confirm it now — that is
    UNVERIFIABLE, not FABRICATED, and the two must not be conflated. This test
    said otherwise and went red the moment a second capture was frozen: it
    judged the 08:20 entry against the 22:44 dump's fingerprint.

    ⇒ Only the newest official entry is checked. ⚠️ And the exemption is itself
    a symptom — `DUMP_PRODUCER_DATED_CAPTURES_1` gives each capture its own
    directory, after which a superseded entry still has its artifact and this
    could check every row again.

    🔴 SELFTEST_DRIFT_REPAIR_1: this case went red 2026-08-30 with the active
    entry (OFFICIAL-2026-08-29, capture 2026-08-29T13-30-02Z) claiming
    modlist_sha 1742630eb6253187 and `refresh.dump_fingerprint()` — called with
    NO argument — recomputing c0b45bcbe2caaa1b instead. That is not an
    unreproducible sha: `dump_fingerprint()`'s default argument is `D_DUMP`,
    which resolves to the NEWEST capture on disk (`game_paths.newest_capture()`),
    and a newer capture (2026-08-31T04-57-37Z, taken after this entry was
    frozen) had since been produced by an ordinary game load — exactly the
    "our own mods change the count constantly" drift the frozen-dump immunity
    exists to shrug off. The bug was in THIS test: it fingerprinted whatever is
    current instead of the specific capture the active entry names. Recomputing
    against `<DUMP_ROOT>/captures/<active["capture"]>` (falling back to the flat
    root for a pre-migration entry with no `capture` field) reproduces
    1742630eb6253187 exactly — the registry entry was correct all along."""
    real = os.path.normpath(os.path.join(
        os.path.dirname(os.path.dirname(HERE)), "..",
        "infrastructure", "state", "dumps", "REGISTRY.jsonl"))
    if not os.path.exists(real):
        return
    rows = [json.loads(l) for l in open(real, encoding="utf-8") if l.strip()]
    official = [e for e in rows if e.get("kind") == "official"]
    if not official:
        return
    active = official[-1]
    import game_paths as gp
    cap_id = active.get("capture")
    cap_path = os.path.join(gp.DUMP_ROOT, "captures", cap_id) if cap_id else gp.DUMP_ROOT
    known = {(refresh.dump_fingerprint(cap_path) or {}).get("hash"), "see manifest.json"}
    known.discard(None)
    sha = active.get("modlist_sha")
    assert sha in known, (
        "the ACTIVE frozen entry %s claims modlist_sha %r, which nothing on this "
        "machine produces (recomputable: %s). This is the design target — a claim "
        "about it that cannot be recomputed can only be believed."
        % (active.get("id"), sha, sorted(known)))
    # Every entry must still carry SOMETHING checkable rather than a blank.
    for i, e in enumerate(rows, 1):
        assert e.get("modlist_sha"), (
            "REGISTRY.jsonl line %d has no modlist_sha at all" % i)


# ---------------------------------------------------------------------------
# Dated captures — DUMP_STORAGE_LAYOUT_RULING_1, owner 2026-08-21:
# *"Option (a) all the way. Keep last three."*
#
# 🪤 The original proposal used `current`/`official` SYMLINKS and that is
# impossible here: measured the same day, a symlink WSL creates under LocalLow
# succeeds from bash and is unreadable from Windows (`Mode d----l`, empty
# LinkType, PathNotFound through it), so the GAME could never follow one.
# The ids are ISO-8601 instead, which makes `current` = max(dirname) and needs
# no pointer at all. See BUILDABLE.md.
# ---------------------------------------------------------------------------

def _layout(ids, flat=True):
    """A throwaway DefDump root. `ids` become capture dirs; `flat` also writes a
    manifest at the root, which is the pre-migration shape."""
    d = tempfile.mkdtemp(prefix=".dump_")
    if flat:
        json.dump({"capturedUtc": "2026-08-01T00:00:00Z"},
                  open(os.path.join(d, "manifest.json"), "w"))
    for i in ids:
        os.makedirs(os.path.join(d, "captures", i))
    return d


def t_the_flat_layout_still_resolves_after_the_change():
    """⚠️ The migration has no flag day. Until the producer is changed there is
    no `captures/`, and every reader must go on working unchanged."""
    import game_paths as gp
    d = _layout([])
    assert gp.captures(os.path.join(d, "captures")) == []
    assert gp.newest_capture(os.path.join(d, "captures")) is None, (
        "a dump with no captures/ claimed to have a newest capture")
    shutil.rmtree(d, ignore_errors=True)


def t_newest_capture_is_the_lexicographically_last_id():
    """🔑 ISO-8601 with fixed-width fields, so a string sort IS a date sort —
    which is what lets the C# producer agree with Python for free."""
    import game_paths as gp
    ids = ["2026-08-21T08-20-20Z", "2026-09-01T00-00-00Z", "2026-08-09T23-59-59Z"]
    d = _layout(ids, flat=False)
    root = os.path.join(d, "captures")
    assert gp.captures(root) == sorted(ids), gp.captures(root)
    assert os.path.basename(gp.newest_capture(root)) == "2026-09-01T00-00-00Z"
    shutil.rmtree(d, ignore_errors=True)


def t_a_directory_that_is_not_a_capture_id_is_ignored():
    """`captures/` may end up holding a scratch dir, a partial write or a
    `.tmp`. Anything that is not exactly an id is not a capture."""
    import game_paths as gp
    d = _layout(["2026-08-21T08-20-20Z"], flat=False)
    root = os.path.join(d, "captures")
    for junk in ("tmp", "2026-08-21", "2026-08-21T08-20-20Z.partial", "backup"):
        os.makedirs(os.path.join(root, junk), exist_ok=True)
    assert gp.captures(root) == ["2026-08-21T08-20-20Z"], gp.captures(root)
    shutil.rmtree(d, ignore_errors=True)


def t_freezing_marks_the_capture_so_retention_cannot_delete_it():
    """🔴 The official capture is frozen precisely because it must not move. It
    must therefore also not age out of a three-deep retention window."""
    import game_paths as gp
    reg = with_registry([entry(capturedUtc="2026-08-21T08:20:20Z")])
    cap = _capture("2026-09-02T00:00:00Z")
    _, wrote = refresh.freeze(cap, by="owner")
    assert wrote
    marker = os.path.join(cap, gp.KEEP_MARKER)
    assert os.path.exists(marker), (
        "freeze did not write %s — retention could delete the design target"
        % gp.KEEP_MARKER)
    assert "design target" in open(marker, encoding="utf-8").read()
    shutil.rmtree(reg, ignore_errors=True)
    shutil.rmtree(cap, ignore_errors=True)


def t_a_freeze_of_a_dated_capture_records_which_one():
    import game_paths as gp
    reg = with_registry([entry(capturedUtc="2026-08-21T08:20:20Z")])
    parent = tempfile.mkdtemp(prefix=".caps_")
    cap = os.path.join(parent, "2026-09-03T04-05-06Z")
    os.makedirs(cap)
    src = _capture("2026-09-03T04:05:06Z")
    shutil.copy(os.path.join(src, "manifest.json"), cap)
    e, _ = refresh.freeze(cap, by="")
    assert e.get("capture") == "2026-09-03T04-05-06Z", (
        "the entry does not name the capture directory it froze: %r"
        % e.get("capture"))
    for d in (reg, parent, src):
        shutil.rmtree(d, ignore_errors=True)


def t_the_flat_layout_freeze_names_no_capture():
    """Under the pre-migration shape there is no capture id, and inventing one
    would be a claim about a directory that does not exist."""
    reg = with_registry([entry(capturedUtc="2026-08-21T08:20:20Z")])
    src = _capture("2026-09-04T00:00:00Z")
    e, _ = refresh.freeze(src, by="")
    assert "capture" not in e, "a flat-layout freeze invented a capture id: %r" % e.get("capture")
    shutil.rmtree(reg, ignore_errors=True)
    shutil.rmtree(src, ignore_errors=True)


def t_two_captures_on_one_day_get_distinct_ids():
    """🔴 Measured live 2026-08-21, the first day it could happen: the 08:20
    capture and the 22:44 one both derived `OFFICIAL-2026-08-21`, so the registry
    held two entries with one id and the newer said `supersedes` its own name.
    An id that is not unique cannot be looked up; a self-referential chain cannot
    be walked."""
    reg = with_registry([entry(id="OFFICIAL-2026-09-05",
                               capturedUtc="2026-09-05T08:00:00Z")])
    e, _ = refresh.freeze(_capture("2026-09-05T22:44:59Z"), by="")
    assert e["id"] != "OFFICIAL-2026-09-05", (
        "a second capture on the same day reused the id: %s" % e["id"])
    assert e["id"] == "OFFICIAL-2026-09-05T22-44-59Z", e["id"]
    assert e.get("supersedes") != e["id"], "the entry supersedes itself"
    assert e.get("supersedes") == "OFFICIAL-2026-09-05"
    shutil.rmtree(reg, ignore_errors=True)


def t_the_first_capture_of_a_day_keeps_the_plain_id():
    """The disambiguator must not fire when there is nothing to disambiguate —
    `OFFICIAL-<date>` is the readable form and stays the default."""
    reg = with_registry([entry(id="OFFICIAL-2026-09-04",
                               capturedUtc="2026-09-04T08:00:00Z")])
    e, _ = refresh.freeze(_capture("2026-09-05T10:00:00Z"), by="")
    assert e["id"] == "OFFICIAL-2026-09-05", e["id"]
    assert e["supersedes"] == "OFFICIAL-2026-09-04"
    shutil.rmtree(reg, ignore_errors=True)


def t_an_explicit_id_is_written_as_given():
    """⚠️ Only the DEFAULT is disambiguated. An id the owner typed is his word."""
    reg = with_registry([entry(id="OFFICIAL-2026-09-06",
                               capturedUtc="2026-09-06T08:00:00Z")])
    e, _ = refresh.freeze(_capture("2026-09-06T22:00:00Z"), by="",
                          id_="OFFICIAL-2026-09-06")
    assert e["id"] == "OFFICIAL-2026-09-06", e["id"]
    assert "supersedes" not in e, (
        "it superseded itself: %s" % e.get("supersedes"))
    assert e.get("supersedesCapturedUtc") == "2026-09-06T08:00:00Z", e
    shutil.rmtree(reg, ignore_errors=True)


def t_a_sealed_entry_that_was_edited_is_detected():
    """🔴 The defect FROZEN_FINGERPRINT_OVERWRITTEN_1 was filed for: an already
    frozen `modlist_sha` was rewritten in place, `capturedUtc` untouched, on a
    claim that the old value was unreproducible. It was reproducible. Nothing on
    disk could have contradicted it afterwards, because the capture the number
    described had already been replaced. The seal does not prevent the edit; it
    makes the edit impossible to miss."""
    e = json.loads(entry(id="OFFICIAL-2026-09-07",
                         capturedUtc="2026-09-07T08:00:00Z",
                         modlist_sha="e0f11692cf69e516"))
    e[refresh.SEAL_FIELD] = refresh.seal_of(e)
    reg = with_registry([json.dumps(e) + "\n"])
    assert refresh.registry_tamper() == [], "a freshly sealed entry read as tampered"
    shutil.rmtree(reg, ignore_errors=True)   # ⚠️ or the second with_registry() orphans it

    e["modlist_sha"] = "5ef6eec3daf6c325"          # the in-place rewrite, replayed
    reg = with_registry([json.dumps(e) + "\n"])
    bad = refresh.registry_tamper()
    assert bad and bad[0][0] == "OFFICIAL-2026-09-07", (
        "an edited frozen entry was NOT detected: %r" % bad)
    shutil.rmtree(reg, ignore_errors=True)


def t_freezing_past_an_edited_entry_raises():
    """⛔ Detection that does not stop anything is a comment. A freeze appended
    after a tampered line would bless the edit by carrying on past it."""
    e = json.loads(entry(id="OFFICIAL-2026-09-08",
                         capturedUtc="2026-09-08T08:00:00Z"))
    e[refresh.SEAL_FIELD] = refresh.seal_of(e)
    e["modlist_count"] = 999                       # edited AFTER sealing
    reg = with_registry([json.dumps(e) + "\n"])
    try:
        refresh.freeze(_capture("2026-09-09T08:00:00Z"), by="owner")
    except RuntimeError as exc:
        assert "EDITED after sealing" in str(exc), str(exc)
    else:
        raise AssertionError("freeze() appended past an edited frozen entry")
    shutil.rmtree(reg, ignore_errors=True)


def t_an_unsealed_entry_is_unmeasured_not_clean():
    """🔑 Entries written before the seal existed cannot be checked, and calling
    them clean would be the same lie the seal guards against."""
    reg = with_registry([entry(id="OFFICIAL-2026-09-10",
                               capturedUtc="2026-09-10T08:00:00Z")])
    assert refresh.SEAL_FIELD not in refresh.registry()[0]
    assert refresh.registry_tamper() == [], (
        "an UNSEALED entry was reported as tampered - it is unmeasured, not dirty")
    shutil.rmtree(reg, ignore_errors=True)


def t_a_superseded_fingerprint_is_recorded_not_deleted():
    """⛔ Superseding records the prior value. The old number is the only way to
    tell a changed ALGORITHM from a changed CAPTURE, and deleting it is what made
    the 2026-08-21 rewrite unfalsifiable from disk."""
    reg = with_registry([entry(id="OFFICIAL-2026-09-11",
                               capturedUtc="2026-09-11T08:00:00Z",
                               modlist_sha="e0f11692cf69e516")])
    e, _ = refresh.freeze(_capture("2026-09-12T08:00:00Z"), by="")
    assert e.get("supersededModlistSha") == "e0f11692cf69e516", e
    assert e.get("modlist_sha_algo"), "the fingerprint does not name its algorithm"
    shutil.rmtree(reg, ignore_errors=True)


def t_no_source_still_claims_the_old_sha_is_unreproducible():
    """The docstring taught the false claim to every future reader. Grep is the
    right instrument here: the assertion was prose, not a value."""
    import pathlib
    src = pathlib.Path(refresh.__file__).read_text(encoding="utf-8")
    for phrase in ("reproduces from\n    NOTHING", "reproduces from NOTHING"):
        assert phrase not in src, (
            "refresh.py still asserts the old sha reproduces from nothing")
    assert "CORRECTED 2026-08-21" in src, (
        "the correction is not recorded where the false claim was")

if __name__ == "__main__":
    real = refresh._registry_path
    for k, v in sorted(globals().items()):
        if k.startswith("t_"):
            if k == "t_the_shipped_registry_freezes_the_live_dump":
                refresh._registry_path = real
            case(k[2:], v)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
