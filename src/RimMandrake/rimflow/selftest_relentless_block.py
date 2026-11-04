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
             RIMFLOW_SEAT="BUILD")
    return e


def cli(d, *a):
    p = subprocess.run([sys.executable, CLI] + list(a), capture_output=True, text=True, env=cli_env(d), cwd=REPO,
                       timeout=120)
    return p.returncode, p.stdout + p.stderr


def t_cli():
    d = tempfile.mkdtemp(prefix="rf-block-", dir=os.path.join(REPO, ".")) if os.access(REPO, os.W_OK) else tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(d, "items"))
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

    def item_state(self, item):
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


def main():
    for t in (t_fields_and_schema, t_holds_and_lifts, t_relentless_eligible, t_cli, t_snag_blocks,
              t_ledger_block_leaves_line, t_strikes):
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
