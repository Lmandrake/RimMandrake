#!/usr/bin/env python3
"""Selftest: blocked-on is structured data at the dispatch level (PLAN_BUILD_BLOCKED_BY_IS_TEXT_ONLY), and two strikes
change tack with a token cap (RELENTLESS_STRIKES_HARDEN_CHANGE_TACK).

    python3 src/RimMandrake/rimflow/selftest_relentless_block.py

Pins:
  * `block --kind/--on (repeatable)/--lift-at` replays into fields; the schema refuses a kind/time mismatch;
  * priority.block_holds: an item wait lifts when EVERY --on id reaches its level, a dead blocker never lifts, a time
    wait lifts at its date, owner/judge/live/external/other hold until `unblock`; rank() and relentless.eligible obey it;
  * the CLI: `show` prints the block and whether it holds; `claim` of an item whose block ended writes the unblock;
  * relentless: a snag of a blocker class writes a ledger block and leaves the line (no worker, no failed approach);
    a queued item blocked on the ledger leaves the line; both come back by themselves when the block ends;
  * the shipped rules: two strikes of one class change the approach, the ladder ends in a hold for the Conductor with
    a summary, and the per-item token cap holds with the same summary.
No ledger of the repo is touched: the CLI runs on a throwaway RIMFLOW_LEDGER; relentless runs on its FakeWorld.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from rimflow import model, priority          # noqa: E402
import relentless as R                       # noqa: E402
import relentless_block                      # noqa: E402
import selftest_relentless as SR             # noqa: E402

CLI = os.path.join(HERE, "cli.py")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
FAILS = []
NOW = 1793600000        # 2026-11-02, the clock every pure case reads


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


_N = [0]


def ev(**kw):
    _N[0] += 1
    kw.setdefault("ts", "2026-10-25T00:%02d:%02dZ" % (_N[0] // 60, _N[0] % 60))     # before the close gate's date
    return kw


def filed(iid, seat="BUILD"):
    return ev(seat="BENCH", event="file", id=iid, title="t", kind="task", **{"for": seat})


def ready(iid, seat="BUILD"):
    return [ev(seat=seat, event="claim", id=iid)]


def world(*extra):
    base = [filed("WAITER_A"), filed("PRED_B"), filed("PRED_C")] + ready("WAITER_A")
    return model.replay(base + list(extra), strict=True)


def done(iid):
    return ev(seat="BUILD", event="close", id=iid, sha="598dec613")


# ---------------------------------------------------------------- the ledger and the dispatch rule

def t_fields_and_schema():
    w = world(ev(seat="BUILD", event="block", id="WAITER_A", reason="r", on="PRED_B", also_on=["PRED_C"], kind="item"))
    it = w.items["WAITER_A"]
    ok(it.blocked and it.blocked_kind == "item" and priority.block_ons(it) == ("PRED_B", "PRED_C"),
       "block replays kind and every --on id")
    w = world(ev(seat="BUILD", event="block", id="WAITER_A", reason="r"))
    ok(priority.block_kind(w.items["WAITER_A"]) == "other", "a bare reason is kind other (old blocks keep working)")
    for bad, why in ((dict(kind="time"), "time with no lift_at"), (dict(kind="owner", lift_at="2026-11-03T00:00:00Z"),
                                                                    "lift_at off a time block"),
                     (dict(kind="nonsense"), "an unknown kind")):
        try:
            model.replay([filed("WAITER_A"), ev(seat="BUILD", event="block", id="WAITER_A", reason="r", **bad)],
                         strict=True)
            ok(False, "schema refuses %s" % why)
        except Exception:       # noqa: BLE001  the strict replay raises the model's own SchemaError
            ok(True, "schema refuses %s" % why)
    w = world(ev(seat="BUILD", event="block", id="WAITER_A", reason="r", on="PRED_B", kind="item"),
              ev(seat="BUILD", event="unblock", id="WAITER_A"))
    it = w.items["WAITER_A"]
    ok(not it.blocked and it.blocked_kind is None and it.blocked_also == (), "unblock clears every block field")


def t_holds_and_lifts():
    blk = ev(seat="BUILD", event="block", id="WAITER_A", reason="r", on="PRED_B", also_on=["PRED_C"], kind="item")
    w = world(blk)
    ok(priority.block_holds(w, w.items["WAITER_A"], NOW), "an item wait holds while its predecessors are open")
    ok("WAITER_A" not in [i.id for i in priority.rank(w, "BUILD", ctx={"now": NOW})], "rank() does not offer it")
    w = world(blk, done("PRED_B"))
    ok(priority.block_holds(w, w.items["WAITER_A"], NOW), "one of two predecessors done: still holds")
    w = world(blk, done("PRED_B"), done("PRED_C"))
    it = w.items["WAITER_A"]
    ok(not priority.block_holds(w, it, NOW) and "PRED_B done" in priority.release_reason(w, it, NOW),
       "every predecessor done: the block ends by itself")
    ok("WAITER_A" in [i.id for i in priority.rank(w, "BUILD", ctx={"now": NOW})], "rank() offers it again, no event")
    w = world(ev(seat="BUILD", event="block", id="WAITER_A", reason="r", on="PRED_B", kind="item"),
              ev(seat="BENCH", event="drop", id="PRED_B", reason="x"))
    ok(priority.block_holds(w, w.items["WAITER_A"], NOW), "a dropped predecessor never releases (confirm)")
    t = model.stamp(NOW + 3600)
    w = world(ev(seat="BUILD", event="block", id="WAITER_A", reason="r", kind="time", lift_at=t))
    it = w.items["WAITER_A"]
    ok(priority.block_holds(w, it, NOW) and not priority.block_holds(w, it, NOW + 3601), "a time wait lifts at its date")
    for kind in ("owner", "judge", "live", "external", "other"):
        w = world(ev(seat="BUILD", event="block", id="WAITER_A", reason="r", kind=kind))
        ok(priority.block_holds(w, w.items["WAITER_A"], NOW + 10 ** 7), "a %s block holds until unblock" % kind)


def t_relentless_eligible():
    r = dict(SR.RULES, pool_seats=["BUILD"], pool_needs=["offline"], pool_ids_exclude=[], staffing=None)
    blk = ev(seat="BUILD", event="block", id="PRED_C", reason="r", on="PRED_B", kind="item")
    w = world(blk)
    it = w.items["PRED_C"]
    ok(not R.eligible(it, r, w, NOW), "relentless: a held block is never in the pool")
    w = world(blk, done("PRED_B"))
    ok(R.eligible(w.items["PRED_C"], r, w, NOW), "relentless: the predecessor closed, the item is in the pool again")


# ---------------------------------------------------------------- the CLI

def cli_env(d):
    e = {k: v for k, v in os.environ.items()
         if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID") and not k.startswith("GIT_")}
    e.update(RIMFLOW_LEDGER=os.path.join(d, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(d, "items"),
             RIMFLOW_PROBE="no-reading", RIMFLOW_SCHEDULE=os.path.join(d, "no_schedule.json"), RIMFLOW_DRIVER_LOCK="",
             RIMFLOW_SHARED_BRIDGE="", RIMFLOW_BRIDGE_LOCK=os.path.join(d, "bridge.lock"), RM_HOST="archmagi",
             RIMFLOW_SEAT="BUILD", RIMFLOW_GIT_CWD=d)
    return e


def cli(d, *a):
    p = subprocess.run([sys.executable, CLI] + list(a), capture_output=True, text=True, env=cli_env(d), cwd=REPO,
                       timeout=120)
    return p.returncode, p.stdout + p.stderr


def t_cli():
    d = tempfile.mkdtemp(prefix="rf-block-", dir=os.path.join(REPO, ".")) if os.access(REPO, os.W_OK) else tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(d, "items"))
        # `close --no-code` stamps HEAD: the fixture's own repo, so an export with no history (a checker's box) can run this
        for g in (["init", "-q"], ["-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid", "commit", "-q", "--allow-empty", "-m", "fixture"]):
            subprocess.run(["git"] + g, cwd=d, check=True, capture_output=True, timeout=60,
                           env={k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
        for i in ("WAITER_PROBE_FIXTURE", "PRED_PROBE_FIXTURE", "PRED_TWO_PROBE_FIXTURE"):
            rc, out = cli(d, "file", i, "--for", "BUILD", "--title", "t")
            assert rc == 0, out
        rc, out = cli(d, "block", "WAITER_PROBE_FIXTURE", "--reason", "Follows the two preds", "--on",
                      "PRED_PROBE_FIXTURE", "--on", "PRED_TWO_PROBE_FIXTURE")
        ok(rc == 0, "cli: block with two --on ids")
        rc, out = cli(d, "show", "WAITER_PROBE_FIXTURE")
        ok("kind item" in out and "PRED_PROBE_FIXTURE, PRED_TWO_PROBE_FIXTURE" in out and "holds" in out,
           "cli: show prints the kind, both predecessors and that it holds")
        rc, out = cli(d, "block", "WAITER_PROBE_FIXTURE", "--reason", "r", "--kind", "time")
        ok(rc != 0 and "--lift-at" in out, "cli: --kind time without --lift-at is refused")
        rc, out = cli(d, "block", "WAITER_PROBE_FIXTURE", "--reason", "r", "--kind", "judge", "--on", "PRED_PROBE_FIXTURE")
        ok(rc != 0, "cli: --on with a non-item kind is refused")
        for i in ("PRED_PROBE_FIXTURE", "PRED_TWO_PROBE_FIXTURE"):
            rc, out = cli(d, "close", i, "--no-code", "a fixture")
        rc, out = cli(d, "show", "WAITER_PROBE_FIXTURE")
        closed = "ENDED" in out
        ok(closed or "holds" in out, "cli: show says whether the block ended")
        if closed:
            rc, out = cli(d, "claim", "WAITER_PROBE_FIXTURE")
            ok(rc == 0 and "unblocked WAITER_PROBE_FIXTURE" in out, "cli: claim writes the unblock of an ended block")
            rc, out = cli(d, "show", "WAITER_PROBE_FIXTURE")
            ok("BLOCKED" not in out.split("---")[0], "cli: after the claim the books no longer call it blocked")
        else:
            ok(False, "cli: closing both predecessors ended the block (close refused here: %s)" % out[-200:])
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------- relentless: snag and sweep

class BlockWorld(SR.FakeWorld):
    def __init__(self, n=2):
        super().__init__(n)
        self.blocks = {}        # item -> (kind, ons, reason)
        self.block_fail = None

    def item_state(self, item, fresh=False):
        st = super().item_state(item)
        if st is not None:
            b = self.blocks.get(item)
            holds = bool(b) and not (b[0] == "item" and b[1] and all(self.items.get(x) == "done" for x in b[1]))
            st.update(block_holds=holds, block=repr(b) if b else None)
        return st

    def ledger_block(self, item, kind, ons, reason):
        if self.block_fail:
            return self.block_fail
        self.blocks[item] = (kind, list(ons), reason)


def rig(n=2, **rules):
    x = SR.Rig(n=n, share=1.0, max_workers=1, **rules)
    x.w = BlockWorld(n)
    return x


def t_snag_blocks():
    x = rig()
    x.run_one("I0")
    st = x.st("I0")
    R.snag(x.s, "I0", st["gen"], "blocked_by_predecessor", "Predecessor I1 still proposed", x.r, now=x.now, on=["I1"])
    x.w.up[st["run"]["unit"]] = False
    for _ in range(3):
        x.tick()
    st = x.st("I0")
    ok(st["status"] == "blocked" and x.w.blocks.get("I0", (None,))[:2] == ("item", ["I1"]),
       "snag blocked_by_predecessor: the ledger gets a structured block on the id named in the detail")
    ok(not R.failed_approaches(x.s, "I0") and not st["failures"], "a block is no failed approach")
    n = len(x.w.launches)
    for _ in range(4):
        x.tick(600)
    ok(all(lz[0] != "I0" for lz in x.w.launches[n:]), "blocked: no worker is sent")
    x.w.items["I1"] = "done"
    x.tick()
    ok(x.st("I0")["status"] == "queued", "the predecessor closed: back in line by itself")
    x.done()
    # explicit --blocker, and a write that fails keeps it out of the line until the write lands
    x = rig()
    x.run_one("I0")
    st = x.st("I0")
    x.w.block_fail = "rimflow down"
    R.snag(x.s, "I0", st["gen"], "needs_a_look", "a judge must rule", x.r, now=x.now, blocker="judge")
    x.w.up[st["run"]["unit"]] = False
    x.tick(); x.tick()
    ok(x.st("I0")["status"] == "blocked" and x.st("I0").get("block_pending"), "a failed block write keeps it pending")
    x.w.block_fail = None
    x.tick()
    ok(x.w.blocks["I0"][0] == "judge" and not x.st("I0").get("block_pending"), "the write lands on a later tick")
    x.tick(); x.tick()
    ok(x.st("I0")["status"] == "blocked", "a judge block holds until someone unblocks")
    del x.w.blocks["I0"]
    x.tick()
    ok(x.st("I0")["status"] == "queued", "unblocked on the ledger: back in line")
    x.done()
    # wait_hours wins: time is not a block
    x = rig()
    x.run_one("I0")
    st = x.st("I0")
    R.snag(x.s, "I0", st["gen"], "blocked_on_dependency", "sample filling", x.r, now=x.now, wait_hours=1)
    ok(not x.st("I0").get("block_pending"), "snag --wait-hours stays a time wait, never a block")
    x.done()
    # the id is read from the detail when the worker named none
    led = {"BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND": {"state": "proposed"}, "DONE_ONE_X": {"state": "done"}}
    k, ons, why = relentless_block.resolve(
        {"kind": "item", "on": [], "class": "blocked_by_predecessor",
         "detail": "Predecessor BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND still proposed; DONE_ONE_X done; NOT_FILED_Y"},
        "STONE_BUILDSTATS_TUNE_GRANITE_GETS_RIVALS", led.get)
    ok(k == "item" and ons == ["BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND"],
       "the open filed predecessor named in the detail is the block (STONE's case); done and unfiled ids are not")
    # no named predecessor: external, said so
    k, ons, why = relentless_block.resolve({"kind": "item", "on": [], "class": "blocked_x", "detail": "no id here"},
                                           "I0", lambda i: None)
    ok(k == "external" and not ons and "no open predecessor" in why, "an item block with no id found is external")


def t_ledger_block_leaves_line():
    x = rig(n=3)
    x.w.blocks["I2"] = ("owner", [], "his call")
    x.tick(); x.tick()
    ok(x.st("I2") is None or x.st("I2")["status"] in ("blocked",) or all(lz[0] != "I2" for lz in x.w.launches),
       "an item blocked on the ledger is never launched")
    st = x.st("I2")
    if st is not None and st["status"] == "queued":
        ok(False, "a queued item blocked on the ledger leaves the line")
    x.done()
    # enrolled first, blocked after
    x = rig(n=1)
    x.tick()
    ok(x.st("I0") is not None, "enrolled")
    x.w.blocks["I0"] = ("external", [], "a vendor")
    with x.s.lock():
        cur = x.s.load("I0")
        if cur["status"] != "queued":       # launched on the first tick: hand it back to the line for this case
            cur["status"] = "queued"
            cur["run"] = None
        x.s.save(cur)
    x.tick()
    ok(x.st("I0")["status"] == "blocked", "a queued item blocked on the ledger moves out of the line")
    x.done()


def t_returned_run_not_restaffed():
    """RELENTLESS_FIX_PARKED_ITEM_STILL_STAFFED: the owner's card blocked CLOSE_GATE_ENFORCE_DONE_IS_EARNED at 23:32Z, and
    gen 19 was leased about 23:37Z. The tick's sweep runs before the steps, so a run ending in this tick's step comes
    back to `queued` after the sweep looked; only lease() is left to see the block."""
    x = rig(n=1)
    x.run_one("I0")
    st = x.st("I0")
    x.w.items["I0"] = "doing"       # started by us, so eligible() and the pool have no say in what follows
    x.w.blocks["I0"] = ("other", [], "PARKED by owner card")
    n = len(x.w.launches)
    x.tick()
    # RELENTLESS_FIX_PARKED_RUN_WORKS_ON_ANYWAY: a block is "stop now", not "after this run lands"
    ok((st["run"]["unit"], False) in x.w.stops, "a run blocked while it works is stopped")
    ok(x.st("I0")["gen"] == st["gen"] + 1, "and fenced: its gen moved, so its finish is refused")
    try:
        R.beat(x.s, "I0", st["gen"], now=x.now)
        ok(False, "a fenced worker's beat is refused")
    except R.Fenced:
        ok(True, "a fenced worker's beat is refused")
    ok(not R.failed_approaches(x.s, "I0") and not x.st("I0")["failures"], "a block stop is no failed approach")
    x.tick()
    returned = x.st("I0")
    ok(all(lz[0] != "I0" for lz in x.w.launches[n:]), "the tick its run ends: a blocked doing item gets no new worker")
    ok(returned["status"] == "blocked", "the same tick it leaves the line (read %s)" % returned["status"])
    gen = returned["gen"]
    ok(gen == st["gen"] + 1, "one gen for the stop, none for the block")
    for _ in range(4):
        x.tick(600)
    ok(all(lz[0] != "I0" for lz in x.w.launches[n:]) and x.st("I0")["gen"] == gen, "later ticks send no worker either")
    del x.w.blocks["I0"]
    x.tick()
    ok(x.st("I0")["status"] in ("queued", "running"), "unblocked on the ledger: back in line")
    x.tick(600)
    ok(any(lz[0] == "I0" for lz in x.w.launches[n:]), "and it is staffed again")
    x.done()
    # a block that no longer holds stops nothing: a finished predecessor, the case sweep lifts
    x = rig(n=2)
    x.run_one("I0")
    st = x.st("I0")
    x.w.items["I0"] = "doing"
    x.w.items["I1"] = "done"
    x.w.blocks["I0"] = ("item", ["I1"], "predecessor")
    n = len(x.w.launches)
    x.w.up[st["run"]["unit"]] = False
    for _ in range(4):
        x.tick(600)
    ok(any(lz[0] == "I0" for lz in x.w.launches[n:]), "a block released by its own rule does not keep the item out")
    x.done()


# ---------------------------------------------------------------- strikes and the token cap (shipped rules)

def shipped(**over):
    r = R.rules(os.path.join(R.HERE, "relentless_rules.json"))
    return dict(SR.RULES, same_failure_limit=r["same_failure_limit"], max_approach_changes=r["max_approach_changes"],
                **over)


def t_strikes():
    r = R.rules(os.path.join(R.HERE, "relentless_rules.json"))
    ok(r["same_failure_limit"] == 2 and r["max_approach_changes"] == 2, "shipped: two strikes, two changes")
    ok(r["item_spend_limit"] <= 5 * 10 ** 6, "shipped: a per-item advisory threshold of a few million (was 10^12, off)")
    x = SR.Rig(n=1, share=1.0)
    x.r = dict(x.r, **shipped(snag_again_wait_h=0))
    x.tick()
    seen = []
    for n in range(7):
        if x.st("I0")["status"] == "held":
            break
        x.run_one("I0")
        st = x.st("I0")
        R.snag(x.s, "I0", st["gen"], "blind_fail_like", "red again %d" % n, x.r, now=x.now)
        x.w.up[st["run"]["unit"]] = False
        x.tick()
        seen.append(x.st("I0")["approach"])
    ok(seen[1] == "redesign", "two strikes of one class: the second worker after them gets a different approach")
    st = x.st("I0")
    ok(st["status"] == "held" and st["hold"]["kind"] == "strikes", "the ladder climbed: held, not turned again")
    ok("gen " in st["hold"]["why"] and "blind_fail_like" in st["hold"]["why"], "the hold carries a summary: %s"
       % st["hold"]["why"][:120])
    x.tick()
    ok(x.w.seat_holds == ["I0"] and not x.w.needs, "a strikes hold goes to the seat, not to needs=owner")
    R.unhold(x.s, "I0", "go on")
    ok(not x.st("I0")["failures"], "unhold of a strikes hold starts a fresh count")
    x.done()
    # the cap
    x = SR.Rig(n=1, share=1.0, item_spend_limit=5000)
    x.tick()
    with x.s.lock():
        cur = x.s.load("I0")
        cur["status"], cur["spent"], cur["run"] = "queued", 6000, None
        x.s.save(cur)
    x.tick()
    st = x.st("I0")
    ok(st["status"] != "held" and not st.get("hold"), "over the token threshold: not held (advisory, owner 2026-11-02)")
    ok(any("I0 spent 6000" in a and "item_spend_limit 5000" in a for a in x.w.attn),
       "over the token threshold: the Conductor hears what crossed and by how much")
    x.done()


def t_scope_snag_blocks():
    """OPS_CHURN_DIAGNOSE_RELENTLESS_IPFI_XNYX: RELENTLESS_TICK_MEASURE_OUTLASTS_ITS_NAP went back 3 times on `snag --class
    scope_exceeds_item` naming its two filed follow-ups; the class was no blocker, so each return re-staffed a worker
    (~1M tokens) to re-find that the rest of the scope lives in those items. The shipped rules make it an item block."""
    with open(R.RULES) as f:
        rules = json.load(f)
    for k in ("scope_exceeds_item", "scope_split", "rescope_needed"):
        ok(relentless_block.blocker_kind(k, rules) == "item", "shipped rules: snag --class %s is an item block" % k)
    detail = ("gen7: no retry, nothing changed since gen5. The open clauses are the whole scope of "
              "TICKSLOW_REWIRE_CLONES_OFF_THE_BELT and RELWAITS_PRUNE_PAUSES_WITH_NO_REASON (both proposed). Supervisor: "
              "rescope to profile+inventory and close on 48d6789366, or drop RELENTLESS_TICK_MEASURE_OUTLASTS_ITS_NAP")
    blk = relentless_block.from_snag("scope_exceeds_item", detail, rules)
    led = {"TICKSLOW_REWIRE_CLONES_OFF_THE_BELT": {"state": "proposed"},
           "RELWAITS_PRUNE_PAUSES_WITH_NO_REASON": {"state": "proposed"}}
    k, ons, why = relentless_block.resolve(blk or {"kind": None, "on": []}, "RELENTLESS_TICK_MEASURE_OUTLASTS_ITS_NAP", led.get)
    ok(k == "item" and ons == ["TICKSLOW_REWIRE_CLONES_OFF_THE_BELT", "RELWAITS_PRUNE_PAUSES_WITH_NO_REASON"],
       "the instance's gen7 snag waits on its two follow-ups, not back in line")


def t_unfiled_wait_refused_at_write():
    """RIMFLOW_FIX_BLOCKS_LIFT_ON_CLOSE: a snag naming an id the ledger has never seen does not wait on it."""
    known = {"OPEN_PRED_BUILD_X": {"state": "doing"}}
    kind, ons, why = relentless_block.resolve({"kind": "item", "on": ["NEVER_FILED_FIX_Y", "OPEN_PRED_BUILD_X"],
                                               "class": "blocked_by_predecessor", "detail": "d"},
                                              "ITEM_A_B", known.get)
    ok(kind == "external" and ons == [] and "never filed: NEVER_FILED_FIX_Y" in why and "OPEN_PRED_BUILD_X" in why,
       "RELENTLESS_BLOCK_HARDEN_MIGRATION_GATE: a multi-item wait with an unfiled id never narrows to the filed one "
       "(its close would resume an item still waiting on the unfiled one): %s %s %s" % (kind, ons, why[:120]))
    kind, ons, why = relentless_block.resolve({"kind": "item", "on": ["NEVER_FILED_FIX_Y"], "class": "blocked_x",
                                               "detail": "nothing named"}, "ITEM_A_B", known.get)
    ok(kind == "external" and ons == [] and "NEVER_FILED_FIX_Y" in why,
       "only an unfiled --on: external, never a wait nothing can close (%s)" % kind)
    kind, ons, why = relentless_block.resolve({"kind": "judge", "on": ["OPEN_PRED_BUILD_X"], "class": "blocked_x",
                                               "detail": "d"}, "ITEM_A_B", known.get)
    ok(kind == "judge" and ons == [] and "OPEN_PRED_BUILD_X" in why,
       "--blocker judge with --on: no --on reaches `rimflow block --kind judge` (it refuses that pair): %s %s" % (kind, ons))


def t_store_ledger_diff_and_three_day_gate():
    led = {"Q_HOLDS_A": {"state": "doing", "block_holds": True}, "B_LIFTED_A": {"state": "doing", "block_holds": False},
           "B_HOLDS_A": {"state": "doing", "block_holds": True}, "Q_FREE_A": {"state": "ready", "block_holds": False},
           "B_DONE_A": {"state": "done", "block_holds": True}}
    states = [{"item": "Q_HOLDS_A", "status": "queued"}, {"item": "B_LIFTED_A", "status": "blocked", "wait": {}},
              {"item": "B_HOLDS_A", "status": "blocked"}, {"item": "Q_FREE_A", "status": "queued"},
              {"item": "B_DONE_A", "status": "blocked"}, {"item": "P_PENDING_A", "status": "blocked",
                                                         "block_pending": {"kind": "item"}},
              {"item": "R_RUN_A", "status": "running"}, {"item": "B_GONE_A", "status": "blocked"}]
    d = relentless_block.diff(states, led.get)
    got = sorted(x["item"] for x in d["disagree"])
    ok(got == ["B_DONE_A", "B_GONE_A", "B_LIFTED_A", "Q_HOLDS_A"] and d["count"] == 4 and d["in_transit"] == 1
       and d["compared"] == 6, "the diff names each side that disagrees, pending is in transit: %s" % d)
    ok(relentless_block.diff([{"item": "Q_FREE_A", "status": "queued"}], led.get)["count"] == 0,
       "an agreeing store reads 0 (the instrument can read 0 and non-0)")
    tmp = tempfile.mkdtemp(prefix="rb_diff_")
    try:
        log = os.path.join(tmp, "d.jsonl")

        def put(at, n, **kw):
            with open(log, "a") as f:
                f.write(json.dumps(dict({"at": at, "count": n, "compared": 3, "in_transit": 0, "unreadable": 0},
                                        **kw)) + "\n")
        ok(not relentless_block.ready_to_delete(log)[0], "no log: not ready")
        put("2026-11-01T03:00:00Z", 0)
        put("2026-11-02T03:00:00Z", 0)
        ok(not relentless_block.ready_to_delete(log)[0], "two days: not ready")
        put("2026-11-03T03:00:00Z", 0)
        put("2026-11-03T05:00:00Z", 2)
        ok(not relentless_block.ready_to_delete(log)[0], "a non-zero reading on a counted day: not ready")
        put("2026-11-04T03:00:00Z", 0)
        ok(not relentless_block.ready_to_delete(log)[0], "the bad day is still one of the last three")
        put("2026-11-05T03:00:00Z", 0)
        put("2026-11-06T03:00:00Z", 0)
        ok(relentless_block.ready_to_delete(log)[0], "0 on three distinct days: ready")
        # RELENTLESS_BLOCK_HARDEN_MIGRATION_GATE: a 0 that saw nothing is not a 0
        for label, kw in (("an unreadable store row", {"unreadable": 1}),
                          ("every row in transit, none compared", {"compared": 0, "in_transit": 4}),
                          ("an older reading with no unreadable count", {"unreadable": None})):
            os.remove(log)
            for day in ("2026-11-04", "2026-11-05"):
                put(day + "T03:00:00Z", 0)
            put("2026-11-06T03:00:00Z", 0, **kw)
            if kw.get("unreadable", 0) is None:
                rows = [json.loads(x) for x in open(log)]
                rows[-1].pop("unreadable")
                with open(log, "w") as f:
                    f.write("".join(json.dumps(r) + "\n" for r in rows))
            ok(not relentless_block.ready_to_delete(log)[0], "%s on a counted day: not ready" % label)
        with open(log, "a") as f:
            f.write("{not json\n")
        ok(not relentless_block.ready_to_delete(log)[0], "a log line that does not parse: not ready")
        for line in ("[]", json.dumps({"count": 0, "compared": 3, "unreadable": 0})):
            os.remove(log)
            for day in ("2026-11-04", "2026-11-05", "2026-11-06"):
                put(day + "T03:00:00Z", 0)
            ok(relentless_block.ready_to_delete(log)[0], "three clean days before the odd line")
            with open(log, "a") as f:
                f.write(line + "\n")
            ok(not relentless_block.ready_to_delete(log)[0], "a line that is not a dated reading (%s): not ready" % line)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_diff_cli_counts_unreadable_rows():
    """RELENTLESS_BLOCK_HARDEN_MIGRATION_GATE: `diff` records an unreadable store row; it never vanishes into a 0."""
    tmp = tempfile.mkdtemp(prefix="rb_cli_")
    try:
        for name, body in (("Q_FREE_A", json.dumps({"item": "Q_FREE_A", "status": "running"})),
                           ("B_BROKEN_A", "{truncated")):
            os.makedirs(os.path.join(tmp, "store", "items", name))
            with open(os.path.join(tmp, "store", "items", name, "state.json"), "w") as f:
                f.write(body)
        log = os.path.join(tmp, "d.jsonl")
        real = relentless_block._live_item_state
        relentless_block._live_item_state = lambda: (lambda iid: None)
        try:
            import io
            import contextlib
            with contextlib.redirect_stdout(io.StringIO()):
                rc = relentless_block.main(["diff", "--root", tmp, "--log", log])
        finally:
            relentless_block._live_item_state = real
        rec = json.loads(open(log).read().splitlines()[-1])
        ok(rc == 0 and rec["unreadable"] == 1 and rec["rows"] == 2 and rec["count"] == 0
           and relentless_block.reading_clean(rec), "the broken row is counted and the reading is not clean: %s" % rec)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    for t in (t_fields_and_schema, t_holds_and_lifts, t_relentless_eligible, t_cli, t_snag_blocks,
              t_ledger_block_leaves_line, t_returned_run_not_restaffed, t_strikes, t_scope_snag_blocks,
              t_unfiled_wait_refused_at_write, t_store_ledger_diff_and_three_day_gate, t_diff_cli_counts_unreadable_rows):
        print("--", t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001
            import traceback
            traceback.print_exc()
            ok(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("selftest_relentless_block: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
