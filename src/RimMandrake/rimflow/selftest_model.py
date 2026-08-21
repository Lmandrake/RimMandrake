#!/usr/bin/env python3
"""Selftest for rimflow/model.py and rimflow/priority.py.

⭐ THE REFUSALS ARE THE PRODUCT. Every rule in `FORBIDDEN`, every permission check and
the completeness gate exists because the markdown queues let it happen at least once —
an item reopened after closing, a seat editing another seat's row, a `state: done`
written next to an empty spec. A refusal that does not actually refuse is worse than
no refusal, because the whole design rests on "the tool prevents this, so nobody has
to remember it".

So this file spends most of its cases proving that the forbidden things are forbidden,
and it runs entirely against a throwaway ledger — never the real one.

    python3 src/RimMandrake/rimflow/selftest_model.py
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model, priority                              # noqa: E402

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


def refuses(fn, needle, why):
    """Assert fn() raises a LedgerError whose message actually explains itself."""
    try:
        fn()
    except model.LedgerError as e:
        assert needle.lower() in str(e).lower(), (
            "refused, but the message does not mention %r — a refusal nobody can act "
            "on is a wall. Got: %s" % (needle, e))
        return
    raise AssertionError("NOT REFUSED: %s" % why)


def ev(**kw):
    kw.setdefault("ts", "2026-08-20T00:00:00Z")
    return kw


def filed(iid="SANDSTORM_WEATHER_TUNING_1", seat="DECIDE", for_="BUILD", **kw):
    d = dict(seat=seat, event="file", id=iid, title="t", kind="task")
    d["for"] = for_
    d.update(kw)
    return ev(**d)


# --------------------------------------------------------------------------
def t_atomicity_guard():
    big = ev(seat="BUILD", event="note", id="X_Y_1", text="z" * 5000)
    refuses(lambda: model.append(big, os.path.join(TMP, "e.jsonl")),
            "atomic",
            "a 5 KB event was accepted. Above PIPE_BUF the O_APPEND atomicity "
            "guarantee is gone and a concurrent writer can tear the line in half.")


def t_append_returns_growing_offset():
    p = os.path.join(TMP, "idx.jsonl")
    a = model.append(filed("FIRST_ITEM_HERE_1"), p)
    b = model.append(filed("SECOND_ITEM_HERE_1"), p)
    assert a == 0 and b > a, "offsets were %r,%r" % (a, b)
    assert b == os.path.getsize(p) - len(open(p).readlines()[-1]), (
        "the offset must be where the line STARTS")


def t_caused_by_must_be_a_name_not_a_number():
    """🔑 Line indices do not survive the monthly roll; names do."""
    refuses(lambda: model.validate(ev(seat="BUILD", event="note", id="A_B_1",
                                      text="x", caused_by=17)),
            "not a line number",
            "caused_by took a line index — after events.jsonl rolls into "
            "events/2026-08.jsonl every such reference silently points elsewhere")
    model.validate(ev(seat="BUILD", event="note", id="A_B_1", text="x",
                      caused_by="C40/run-3@full-578"))
    model.validate(ev(seat="BUILD", event="note", id="A_B_1", text="x",
                      caused_by="BLACKSTAR_SPAWNS_VESSELLESS_1"))


def t_unknown_verb():
    refuses(lambda: model.validate(ev(seat="BUILD", event="yolo", id="A_B_1")),
            "unknown verb", "an invented verb was accepted")


def t_unknown_field():
    refuses(lambda: model.validate(ev(seat="BUILD", event="note", id="A_B_1",
                                      text="x", severity="high")),
            "no field", "an unknown field was accepted; scalars must live in one place")


def t_id_shape():
    refuses(lambda: model.validate(filed("has spaces")),
            "three_descriptive_words", "an id with spaces was accepted")


def t_legacy_id_still_ok():
    model.validate(filed("B58"))          # legacy IDs resolve and are never renamed


# ---- the refusals the plan names, one case each ---------------------------
def _closed_world():
    evs = [filed("CLOSED_ITEM_HERE_1"),
           ev(seat="BUILD", event="claim", id="CLOSED_ITEM_HERE_1"),
           ev(seat="BUILD", event="close", id="CLOSED_ITEM_HERE_1", sha="abc1234")]
    w = model.replay(evs, strict=True)
    assert w.items["CLOSED_ITEM_HERE_1"].state == "done"
    return evs


def t_close_then_ready_refused():
    evs = _closed_world() + [ev(seat="BUILD", event="claim", id="CLOSED_ITEM_HERE_1")]
    refuses(lambda: model.replay(evs, strict=True), "cannot be reopened",
            "a closed item was reopened — which erases that it ever closed")


def t_close_then_block_refused():
    evs = _closed_world() + [ev(seat="BUILD", event="block", id="CLOSED_ITEM_HERE_1",
                                reason="x")]
    refuses(lambda: model.replay(evs, strict=True), "closed",
            "a closed item was blocked")


def t_drop_then_ready_refused():
    evs = [filed("DROPPED_ITEM_HERE_1"),
           ev(seat="BUILD", event="drop", id="DROPPED_ITEM_HERE_1", reason="no"),
           ev(seat="BUILD", event="claim", id="DROPPED_ITEM_HERE_1")]
    refuses(lambda: model.replay(evs, strict=True), "revived",
            "a dropped item was revived instead of a new one being filed")


def t_cross_seat_write_refused():
    evs = [filed("OTHER_SEATS_ITEM_1", for_="BUILD"),
           ev(seat="CHECK", event="close", id="OTHER_SEATS_ITEM_1", sha="abc1234")]
    refuses(lambda: model.replay(evs, strict=True), "belongs to",
            "CHECK closed BUILD's item")


def t_filing_for_another_seat_is_fine():
    w = model.replay([filed("FILED_BY_DECIDE_1", seat="DECIDE", for_="BUILD")],
                     strict=True)
    assert w.items["FILED_BY_DECIDE_1"].owner == "BUILD"


def t_a_seat_may_retarget_its_own_item():
    """⚠️ `retarget`'s `who` is the mixed tuple ("DECIDE", "owner").

    Treating a tuple as a literal seat list made the "owner" sentinel match nothing,
    so no seat could retarget its own item and only DECIDE and OWNER could retarget at
    all. The model's own tests had exercised only the pure-tuple case; the CLI's
    selftest caught it by trying the thing a seat would actually do.
    """
    evs = [filed("MY_OWN_ITEM_HERE_1", for_="BUILD"),
           ev(seat="BUILD", event="retarget", id="MY_OWN_ITEM_HERE_1",
              to="v2", reason="not v1")]
    w = model.replay(evs, strict=True)
    assert w.items["MY_OWN_ITEM_HERE_1"].target == "v2"


def t_a_seat_may_not_retarget_another_seats_item():
    evs = [filed("NOT_MY_ITEM_HERE_1", for_="BUILD"),
           ev(seat="CHECK", event="retarget", id="NOT_MY_ITEM_HERE_1",
              to="v2", reason="x")]
    refuses(lambda: model.replay(evs, strict=True), "retarget",
            "CHECK retargeted BUILD's item")


def t_decide_may_retarget_anything():
    evs = [filed("ANY_ITEM_HERE_1", for_="BUILD"),
           ev(seat="DECIDE", event="retarget", id="ANY_ITEM_HERE_1",
              to="v2", reason="scope call")]
    assert model.replay(evs, strict=True).items["ANY_ITEM_HERE_1"].target == "v2"


def t_ledger_path_is_redirectable():
    """🔴 The one that protects the production ledger.

    `def read(path=EVENTS)` binds the real file at import, so a test that reassigns
    `model.EVENTS` still reads — and on any write path, APPENDS TO — the real,
    append-only ledger. There is no undo for that file.
    """
    probe = os.path.join(TMP, "redirect.jsonl")
    real = model.EVENTS
    model.EVENTS = probe
    try:
        model.append(filed("REDIRECTED_ITEM_HERE_1"))
        assert os.path.exists(probe), "append ignored the reassigned model.EVENTS"
        assert len(model.read()) == 1, "read ignored the reassigned model.EVENTS"
        assert "REDIRECTED_ITEM_HERE_1" in model.replay().items, (
            "replay ignored the reassigned model.EVENTS")
        model.check(ev(seat="BUILD", event="note", id="REDIRECTED_ITEM_HERE_1",
                       text="x"))
    finally:
        model.EVENTS = real
    assert not os.path.exists(real) or "REDIRECTED_ITEM_HERE_1" not in \
        open(real, encoding="utf-8").read(), (
            "🔴 the probe event reached the REAL ledger at %s" % real)


def t_only_check_takes_bridge():
    refuses(lambda: model.replay([ev(seat="BUILD", event="bridge", state="taken")],
                                 strict=True),
            "only check", "BUILD took the bridge")
    w = model.replay([ev(seat="CHECK", event="bridge", state="taken")], strict=True)
    assert w.bridge_holder == "CHECK"


def t_only_owner_sets_game():
    refuses(lambda: model.replay([ev(seat="CHECK", event="game", state="UP")],
                                 strict=True),
            "only the owner", "CHECK announced the game state")


def t_owner_overrides_seat_ownership():
    evs = [filed("STUCK_ITEM_HERE_1", for_="BUILD"),
           ev(seat="OWNER", event="drop", id="STUCK_ITEM_HERE_1", reason="owner call")]
    w = model.replay(evs, strict=True)
    assert w.items["STUCK_ITEM_HERE_1"].state == "dropped"


# ---- the completeness gate -----------------------------------------------
def t_incomplete_item_cannot_start():
    evs = [filed("NO_SPEC_ITEM_HERE_1"),
           ev(seat="BUILD", event="start", id="NO_SPEC_ITEM_HERE_1")]
    refuses(lambda: model.replay(evs, strict=True), "missing",
            "an item with no spec/verify/criteria was started — the exact failure "
            "POLICY.md's manual refusal was supposed to prevent and did not")


def t_complete_item_can_start():
    os.makedirs(model.ITEMS, exist_ok=True)
    with open(os.path.join(model.ITEMS, "FULL_ITEM_HERE_1.md"), "w") as fh:
        fh.write("## spec\nx\n\n## verify\ny\n\n## criteria\nz\n")
    w = model.replay([filed("FULL_ITEM_HERE_1"),
                      ev(seat="BUILD", event="start", id="FULL_ITEM_HERE_1")],
                     strict=True)
    assert w.items["FULL_ITEM_HERE_1"].state == "doing"


# ---- runs are immutable, failures stand ----------------------------------
def t_failed_run_does_not_reopen():
    evs = [filed("VERIFIED_ITEM_HERE_1"),
           ev(seat="BUILD", event="verify", id="VERIFIED_ITEM_HERE_1",
              result="fail", config="full-578"),
           ev(seat="BUILD", event="verify", id="VERIFIED_ITEM_HERE_1",
              result="pass", config="full-578")]
    w = model.replay(evs, strict=True)
    it = w.items["VERIFIED_ITEM_HERE_1"]
    assert len(it.runs) == 2, "runs were collapsed; a failure must stand forever"
    assert it.runs[0].name == "VERIFIED_ITEM_HERE_1/run-1@full-578", it.runs[0].name
    assert it.runs[0].result == "fail", "the failure was rewritten by the later pass"


def t_run_numbering_is_per_config():
    evs = [filed("MULTI_CONFIG_ITEM_1"),
           ev(seat="BUILD", event="verify", id="MULTI_CONFIG_ITEM_1",
              result="pass", config="min-13"),
           ev(seat="BUILD", event="verify", id="MULTI_CONFIG_ITEM_1",
              result="pass", config="full-578")]
    runs = model.replay(evs, strict=True).items["MULTI_CONFIG_ITEM_1"].runs
    assert [r.n for r in runs] == [1, 1], (
        "run numbers must restart per config: a pass on 13 mods and a pass on 578 are "
        "different questions, and run-1 vs run-2 would imply a retry. Got %r"
        % [r.name for r in runs])


# ---- the causal graph ----------------------------------------------------
def t_spawn_needs_no_host_item():
    """⚠️ §4's command is `spawn --from <FINDING> --for BUILD --name <NEW>` — no host.

    `spawn` used to require an `id` naming some existing item, which forced the caller
    to nominate an unrelated host and made the documented command impossible. Its cause
    is `from`; its product is `name`. Passing an `id` is now the error.
    """
    refuses(lambda: model.validate(ev(seat="CHECK", event="spawn", id="ANY_ITEM_HERE_9",
                                      **{"from": "F_1", "for": "BUILD", "name": "N_1"})),
            "drop the id", "spawn still demanded a host item")
    model.validate(ev(seat="CHECK", event="spawn",
                      **{"from": "F_1", "for": "BUILD", "name": "NEW_WORK_HERE_1"}))


def t_spawn_records_its_cause():
    evs = [filed("SOURCE_ITEM_HERE_1", for_="CHECK"),
           ev(seat="CHECK", event="finding", id="SOURCE_ITEM_HERE_1",
              **{"from": "SOURCE_ITEM_HERE_1/run-1@full-578", "type": "integration",
                 "severity": "high", "name": "BLACKSTAR_SPAWNS_VESSELLESS_1"}),
           ev(seat="CHECK", event="spawn",
              **{"from": "BLACKSTAR_SPAWNS_VESSELLESS_1", "for": "BUILD",
                 "name": "BLACKSTAR_VESSEL_DEF_1"})]
    w = model.replay(evs, strict=True)
    assert "BLACKSTAR_SPAWNS_VESSELLESS_1" in w.findings
    new = w.items["BLACKSTAR_VESSEL_DEF_1"]
    assert new.owner == "BUILD", new.owner
    assert new.caused_by == "BLACKSTAR_SPAWNS_VESSELLESS_1", (
        "the spawned item lost its cause; caused_by IS the causal graph, and it names "
        "the finding rather than a line number so it survives the monthly roll. Got %r"
        % new.caused_by)


# ---- needs vs blocked, and the game-state coupling -----------------------
def _ready(iid, needs="offline", **kw):
    """File an item with a complete items/<ID>.md and claim it, so it reaches `ready`.

    ⚠️ The claim must come from the OWNING seat — a seat cannot claim another seat's
    item, and getting that wrong here produced four confusing failures that looked
    like model bugs and were test bugs.
    """
    os.makedirs(model.ITEMS, exist_ok=True)
    with open(os.path.join(model.ITEMS, "%s.md" % iid), "w") as fh:
        fh.write("## spec\nx\n## verify\ny\n## criteria\nz\n")
    owner = kw.get("for_", "BUILD")
    return [filed(iid, needs=needs, **kw), ev(seat=owner, event="claim", id=iid)]


def t_needs_is_not_blocked():
    evs = _ready("BRIDGE_ONLY_ITEM_1", needs="bridge", for_="CHECK")
    w = model.replay(evs, strict=True)
    it = w.items["BRIDGE_ONLY_ITEM_1"]
    assert it.state == "ready" and not it.blocked, "a closed window is not a defect"
    assert priority.next_item(w, "CHECK") is None, "offered while the game is DOWN"
    why = " ".join(priority.why_not(w, "CHECK", "BRIDGE_ONLY_ITEM_1"))
    assert "not blocked" in why.lower(), (
        "why_not must say the window is closed rather than implying breakage: %s" % why)


def t_bridge_item_offered_when_check_holds_it():
    evs = _ready("BRIDGE_ONLY_ITEM_2", needs="bridge", for_="CHECK")
    evs += [ev(seat="OWNER", event="game", state="UP"),
            ev(seat="CHECK", event="bridge", state="taken")]
    w = model.replay(evs, strict=True)
    got = priority.next_item(w, "CHECK")
    assert got and got.id == "BRIDGE_ONLY_ITEM_2", got


def t_game_down_clears_this_deployment():
    evs = _ready("HOST_ITEM_HERE_1", for_="CHECK")
    evs += [ev(seat="OWNER", event="game", state="UP"),
            ev(seat="CHECK", event="spawn",
               **{"from": "HOST_ITEM_HERE_1", "for": "CHECK",
                  "name": "URGENT_FOLLOWUP_HERE_1", "this_deployment": True}),
            ev(seat="OWNER", event="game", state="DOWN")]
    w = model.replay(evs, strict=True)
    assert not w.items["URGENT_FOLLOWUP_HERE_1"].this_deployment, (
        "--this-deployment survived the game going down, which turns it into false "
        "urgency nobody can trace to a cause")


# ---- the priority ordering ----------------------------------------------
def t_ordering_is_deterministic_and_correct():
    evs = []
    evs += _ready("THIRD_BY_ROW_1", row="9")
    evs += _ready("FIRST_BY_ROW_1", row="2")
    evs += _ready("UNROWED_ITEM_HERE_1")
    order = [i.id for i in priority.rank(model.replay(evs, strict=True), "BUILD")]
    assert order == ["FIRST_BY_ROW_1", "THIRD_BY_ROW_1", "UNROWED_ITEM_HERE_1"], (
        "unrowed items must sort LAST — a row means someone placed it. Got %r" % order)


def _spawn_urgent(host, name):
    return [ev(seat="OWNER", event="game", state="UP"),
            ev(seat="CHECK", event="spawn",
               **{"from": host, "for": "CHECK", "needs": "game-up",
                  "name": name, "this_deployment": True})]


def t_this_deployment_does_not_bypass_the_completeness_gate():
    """⭐ Urgency is not an exemption, and this is the case worth having.

    A spawned `--this-deployment` item is the most tempting thing in the system to
    wave through: the window is closing and someone will argue the paperwork can
    follow. It cannot — without spec/verify/criteria the item stays `proposed` and is
    never offered, exactly like any other. The pressure to skip the gate is highest
    precisely where skipping it costs most, which is why the gate is a precondition
    rather than a reviewer's judgement.
    """
    evs = _ready("HOST_ITEM_HERE_3", for_="CHECK")
    evs += _spawn_urgent("HOST_ITEM_HERE_3", "UNSPECCED_URGENT_HERE_1")
    w = model.replay(evs, strict=True)
    assert w.items["UNSPECCED_URGENT_HERE_1"].state == "proposed"
    assert priority.next_item(w, "CHECK") is None or \
        priority.next_item(w, "CHECK").id != "UNSPECCED_URGENT_HERE_1", (
            "an unspecced item was offered because it was marked urgent")


def t_this_deployment_jumps_the_queue():
    evs = _ready("LOW_ROW_ITEM_HERE_1", row="1", for_="CHECK")
    evs += _ready("HOST_ITEM_HERE_2", for_="CHECK")
    evs += _spawn_urgent("HOST_ITEM_HERE_2", "URGENT_FOLLOWUP_HERE_2")
    # The spawned item earns `ready` the same way as everything else.
    with open(os.path.join(model.ITEMS, "URGENT_FOLLOWUP_HERE_2.md"), "w") as fh:
        fh.write("## spec\nx\n## verify\ny\n## criteria\nz\n")
    evs += [ev(seat="CHECK", event="claim", id="URGENT_FOLLOWUP_HERE_2")]
    top = priority.next_item(model.replay(evs, strict=True), "CHECK")
    assert top and top.id == "URGENT_FOLLOWUP_HERE_2", (
        "the live window is closing and row 1 is not; got %r" % (top and top.id))


def t_v2_is_not_offered_but_is_not_broken():
    evs = _ready("V2_ITEM_HERE_1", target="v2")
    w = model.replay(evs, strict=True)
    assert priority.next_item(w, "BUILD") is None
    why = " ".join(priority.why_not(w, "BUILD", "V2_ITEM_HERE_1"))
    assert "planning decision" in why, why


# ---- replay tolerance ----------------------------------------------------
def t_replay_collects_rather_than_dies():
    evs = [filed("GOOD_ITEM_HERE_1"),
           ev(seat="CHECK", event="game", state="UP"),          # refused: not OWNER
           filed("ALSO_GOOD_ITEM_1")]
    w = model.replay(evs)                                        # non-strict
    assert len(w.errors) == 1, w.errors
    assert "GOOD_ITEM_HERE_1" in w.items and "ALSO_GOOD_ITEM_1" in w.items, (
        "one bad event stopped the replay; an append-only file WILL contain mistakes "
        "and every downstream tool must still work")


def t_torn_line_is_reported_not_skipped():
    p = os.path.join(TMP, "torn.jsonl")
    with open(p, "w") as fh:
        fh.write('{"ts":"x","seat":"BUILD","event":"note","id":"A_B_1","text":"ok"}\n')
        fh.write('{"ts":"x","seat":"BUI\n')
    refuses(lambda: model.read(p), "torn",
            "a torn line was skipped silently — the ledger would then lie quietly, "
            "which is the one failure it exists to end")


CASES = [(k[2:], v) for k, v in sorted(globals().items()) if k.startswith("t_")]

if __name__ == "__main__":
    # 🔴 UNDER THE REPO, NOT /tmp — and this file fell into the exact trap its sibling
    # `selftest_concurrency.py` was written to warn about. `/tmp` is tmpfs here and the
    # repo is on a 9p mount; the two behave differently enough that concurrent appends
    # pass on one and lose 83% of writes on the other. A test that exercises the ledger
    # anywhere but where the ledger lives is measuring the wrong disk.
    TMP = tempfile.mkdtemp(prefix=".rimflow_selftest_",
                           dir=os.path.dirname(os.path.dirname(HERE)))
    model.ITEMS = os.path.join(TMP, "items")
    model.EVENTS = os.path.join(TMP, "events.jsonl")
    try:
        for name, fn in CASES:
            case(name, fn)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
