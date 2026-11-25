#!/usr/bin/env python3
"""selftest_maturation_autonomy.py: no mod waits on the Conductor's hand (item
RIMMANDRAKE_AUTOMATE_MATURATION_HAND_STEPS_MODS_SAT_WAITING). Each check is one dispatch tick: a fixture of facts in,
the mod's class (launch / wait / paused / owner) and the launch out. It drives maturation_dispatch.tick only (fake filer,
fake launchers, a temp state folder, a temp root), so on the base it runs and fails check by check (no class, a Needs
Conductor line instead of a launch). Watched failing on c0cec5b054 before the build.

    python3 src/RimMandrake/rimflow/selftest_maturation_autonomy.py       exit 0 when every check prints PASS

The six waits measured 2026-11-15: (1) a locked change with no chain after it, (2) a Designer concept with no record,
(3) an in-game visit owed with the game free, a not-met visit's failed lines routed back and fixed, then the next visit,
a fair queue across mods, (5) is out of scope here (SteveDesktop, its own item), (6) a stall raises maturation.stalled.
Input kinds: no record, a stale exam (locked change newer than the last look), a held game, a dead steward run (spent),
a refused judge (exit not met), an unreadable file (PAUSED, never a crash), a launch that fails, a full slot.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
if os.environ.get("MAT_AUT_BASE_DIR"):      # watch it fail: a folder holding the base maturation_dispatch.py
    sys.path.insert(0, os.environ["MAT_AUT_BASE_DIR"])
import maturation_dispatch as MD
import run_void as RV    # noqa: E402

CLOCK = 1794750000.0
FAILS = []
CFG = {"enabled": True, "advancing": [], "cap_usd": 15, "max_live": 2, "settle_s": 180, "blind_enabled": True,
       "blind_cap_usd": 20, "blind_auto_cycles_per_visit": 3, "ingame_enabled": True, "ingame_cap_usd": 30,
       "ingame_auto_runs_per_visit": 1, "steward_cap_usd": 5, "fix_cap_usd": 10, "steward_model": "opus",
       "stalled_min": 10, "seat": "BENCH"}


def ok(cond, what):
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


def ingame(mod, owed, visit=1, live=(), why=(), ingame_live=()):
    return {"mod": mod, "stage": "in_game", "version": "0.1.0", "owed": owed, "visit": visit, "live_units": list(live),
            "last_end": None, "ingame_live": list(ingame_live), "ingame_runs": [], "opened": "2026-11-15T01:00:00-08:00",
            "exit": {"state": {"run": "absent", "exit not met": "not_met", "exit met": "met"}.get(owed, owed),
                     "why": list(why) or ["-"], "record": "design/concepts/%s/version/in_game/visit_%d" % (mod, visit)},
            "blocked": []}


def offline(mod, owed, refused=(), hand=()):
    return {"mod": mod, "stage": "offline_build", "version": "0.1.0", "owed": owed, "refused_bars": list(refused),
            "build_refusals": ["every_bar_has_a_check_that_runs"] if refused else [], "hand_steps": list(hand),
            "other_refusals": [], "observed": {}, "live_units": [], "last_end": None, "stage_runs": {}, "run_usd": {},
            "ingame_live": [], "since": "2026-11-15T01:00:00-08:00"}


class World:
    def __init__(self, facts, dstate=None, open_items=None, locked=False, found=(), bridge=(True, "free")):
        self.facts, self.dstate, self.items = facts, dstate or {}, open_items or {}
        self.locked, self.found, self.bridge = locked, list(found), bridge
        self.filed, self.launched, self.briefs, self.cards, self.seeded = [], [], [], [], []
        self.specs = {}
        self.fail_launch = False
        self.fail_texts = []        # launcher failures to return, one per launch, before it succeeds
        self.published = []
        self.dunits = {}
        self.dchain = {}
        self.autolocked, self.evidence = [], {}

    def fx(self):
        def autolock(root, mod, now=None):
            self.autolocked.append(mod)
            self.locked = True
            return "PUBLISHED fake-lock"

        def launch(mod, cap, item):
            self.launched.append(("stage", mod, item))
            return 0, "DETACHED rm-fake-%d" % len(self.launched), "rm-fake-%d" % len(self.launched)

        def launch_brief(item, text, model, cap, seat, **kw):     # kw: env (the real seam carries RM_CONTROL_MOD)
            self.launched.append(("brief", item, model))
            self.briefs.append(text)
            if self.fail_texts:
                return 1, self.fail_texts.pop(0).replace("X", item), None
            if self.fail_launch:
                return 1, "LAUNCH FAILED pool full", None
            return 0, "DETACHED rm-fake-%d" % len(self.launched), "rm-fake-%d" % len(self.launched)

        def file(item, title, why, needs="offline", spec=None):
            self.filed.append(item)
            self.specs[item] = spec
            return True, "filed %s" % item

        def seed(root, mod):
            self.seeded.append(mod)
            if mod == "Unseedable":
                raise ValueError("its stage cannot be read")
            return "PUBLISHED fake"
        return {"facts": lambda: self.facts, "account": lambda: (True, "ok"), "bridge": lambda p: self.bridge,
                "file": file, "publish": lambda item: (self.published.append(item), (True, "pushed"))[1],
                "launch": launch, "launch_brief": launch_brief, "known": lambda: set(),
                "open_items": lambda ids: self.items.get(ids[0], []) if self.items is not None else None,
                "designer_state": lambda m: self.dstate.get(m), "designer_unit": lambda m: self.dunits.get(m),
                "designer_chain": lambda m: self.dchain.get(m), "version_locked": lambda m: self.locked,
                "version_evidence": lambda m: self.evidence.get(m, []), "autolock": autolock,
                "discovered": lambda: self.found, "seed": seed, "card": self.cards.append,
                "page": lambda: type("R", (), {"returncode": 0})(),
                # the tick's repair launcher: it repairs a form refusal in place (form_fault route 1)
                "repair_launch": lambda *a, **k: (True, "fixture: repaired in place", None)}


def run(world, mods, root, now=CLOCK, cfg=None):
    c = dict(cfg or CFG, advancing=list(mods))
    rd = MD.tick(root, c, True, fx=world.fx(), now=now)
    return rd, (lambda m: (rd["mods"].get(m) or {}))


def fresh_state():
    d = os.environ["RM_MATURATION_DISPATCH_DIR"]
    for f in ("state.json", "reading.json", "ticks.jsonl"):
        if os.path.exists(os.path.join(d, f)):
            os.remove(os.path.join(d, f))


GIT_LOCK = ("refused: X is not on origin/main; publish infrastructure/state/ledger/events/RUNNER.jsonl first")
FILED_LOCK = ("publish: add failed (the lines stay in the working tree; the next ingest retries): fatal: Unable to "
              "create '/home/mandrake/rm/dispatch/.git/index.lock': File exists.")


def live_steward_checks(root):
    """RIMMANDRAKE_SEE_LIVE_STEWARD_BEFORE_CALLING_IT_SPENT: a steward run still live on its own state is never read
    'ended and the state has not moved' (steward_spent, PAUSED). Measured 2026-11-20 4:47 PM PST: GimmeSomeSlack's
    preflight steward (rm-detached-bench-rimmandrake-steward-gimmesomeslack-prefl-1795220569, systemd active) read
    PAUSED steward_spent 24 min into its run, with an un-pause line that would launch a second steward beside it."""
    briefs = lambda w: [x[1] for x in w.launched if x[0] == "brief"]   # noqa: E731
    for stage, facts in (("in_game", lambda: ingame("A", "exit not met", why=["sc_ruins reads FAIL"])),
                         ("preflight", lambda: {"mod": "A", "stage": "preflight", "version": "0.1.0", "live_units": [],
                                                "owed": "steward", "exit": {"state": "not_met", "why": ["-"]}})):
        fresh_state()
        w = World({"A": facts()})
        rd, g = run(w, ["A"], root)
        first = g("A").get("decision")
        units = [x for x in briefs(w)]
        w.facts["A"]["live_units"] = ["rm-fake-%d" % len(w.launched)]
        rd, g = run(w, ["A"], root, now=CLOCK + 600)
        ok(g("A").get("decision") != "steward_spent" and g("A").get("klass") == "wait" and len(briefs(w)) == len(units),
           "live steward (%s): its own unit live a tick later reads wait, never PAUSED steward_spent, no second launch "
           "(first %s, read %s/%s: %s; briefs %d -> %d)" % (stage, first, g("A").get("klass"), g("A").get("decision"),
                                                            str(g("A").get("status"))[:100], len(units), len(briefs(w))))
        w.facts["A"]["live_units"] = []
        rd, g = run(w, ["A"], root, now=CLOCK + 1200)
        if units:
            ok(g("A").get("decision") == "steward_spent",
               "live steward (%s): once it ended unmoved the state is spent as before (read %s)" % (
                   stage, g("A").get("decision")))


def launch_retry_checks(root):
    """RIMMANDRAKE_RETRY_STEWARD_LAUNCH_GIT_LOCK_COUNTED_AS_SPENT: a steward or fixer that FAILED TO LAUNCH on a
    transient fault (a git index.lock at publish, its item not yet on origin/main) is not a spent run. Measured
    2026-11-15 08:00 PST: ExplosiveKnockback read PAUSED 'the steward run is spent ... failed to launch'."""
    import maturation_autonomy as AUT
    import maturation_dispatch as MD2
    briefs = lambda w: [x[1] for x in w.launched if x[0] == "brief"]   # noqa: E731
    fresh_state()
    w = World({"A": ingame("A", "exit not met", why=["sc_ruins reads FAIL"])})
    w.fail_texts = [GIT_LOCK]
    rd, g = run(w, ["A"], root)
    ok(g("A").get("klass") == "wait" and "next tick" in str(g("A").get("status")),
       "retry 1: a launch refused on a transient fault (item not on origin/main) reads wait, a retry next tick, never "
       "PAUSED (read %s: %s)" % (g("A").get("klass"), str(g("A").get("status"))[:120]))
    rd, g = run(w, ["A"], root, now=CLOCK + 60)
    b = briefs(w)
    ok(g("A").get("klass") == "launch" and len(b) == 2 and b[0] == b[1] and len(w.filed) == 1
       and w.published == [b[0]],
       "retry 1: the next tick launches it on the SAME item, published again, not filed twice (read %s, briefs %s, "
       "filed %s, published %s)" % (g("A").get("klass"), b, w.filed, w.published))
    rd, g = run(w, ["A"], root, now=CLOCK + 120)
    ok(g("A").get("klass") == "paused" and g("A").get("decision") == "steward_spent" and len(briefs(w)) == 2,
       "retry 1: once it launched and ended unmoved, the state is spent as before: no third launch")
    # every try fails on the lock: a bounded count, then PAUSED with the real reason
    fresh_state()
    w = World({"A": ingame("A", "exit not met", why=["sc_ruins reads FAIL"])})
    w.fail_texts = [GIT_LOCK] * 10
    for i in range(6):
        rd, g = run(w, ["A"], root, now=CLOCK + 60 * i)
    st = str(g("A").get("status"))
    # RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT: the three tries are system faults, never the steward's run
    sa = json.load(open(os.path.join(os.environ["RM_MATURATION_DISPATCH_DIR"], "state.json")))["mods"]["A"]
    # 2026-11-21 (form_fault): past its retries the launch owes a repair naming the real reason, never system_fault
    ok(g("A").get("decision") == "repairing" and "not on origin/main" in st
       and not any(x.get("unit") for x in (sa.get("steward") or {}).values()),
       "retry 2: three transient failures, then a repair naming the real reason, the steward key unspent (read %d "
       "launches, %s)" % (len(briefs(w)), st[:160]))
    # a filing whose own publish hit the lock, then the launcher refused: the same, its item reused
    fresh_state()
    w = World({"A": offline("A", "hand step", hand=["walk_bars_confirmed"])})
    w.fail_texts = [GIT_LOCK]
    rd, g = run(w, ["A"], root)
    d = os.environ["RM_MATURATION_DISPATCH_DIR"]
    sj = json.load(open(os.path.join(d, "state.json")))
    for v in sj["mods"]["A"].get("steward", {}).values():     # the shape on disk before this fix: no tries, no filed
        v.pop("tries", None)
        v.pop("filed", None)
        v["failed"] = "filed %s; %s; %s" % (v["item"], FILED_LOCK, GIT_LOCK.replace("X", v["item"]))
    json.dump(sj, open(os.path.join(d, "state.json"), "w"))
    rd, g = run(w, ["A"], root, now=CLOCK + 60)
    b = briefs(w)
    ok(g("A").get("klass") == "launch" and len(b) == 2 and b[0] == b[1] and len(w.filed) == 1,
       "retry 3: a record of the old shape (no try count), as ExplosiveKnockback's state.json holds it, retries on its "
       "filed item (read %s, briefs %s)" % (g("A").get("klass"), b))
    # a non-transient launch failure stays spent; `clear` releases a key that never launched
    fresh_state()
    w = World({"A": offline("A", "hand step", hand=["walk_bars_confirmed"])})
    w.fail_launch = True
    run(w, ["A"], root)
    rd, g = run(w, ["A"], root, now=CLOCK + 60)
    # RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT: this read "a non-transient launch failure is PAUSED" (spent
    # until a hand clear), the rule the owner forbade 2026-11-18; a launch that never started is void_system
    ok(g("A").get("decision") == "repairing" and len(briefs(w)) == 2,
       "clear 1: a non-transient launch failure is a fault of form: the next tick launches it again with no clear (read "
       "%s, %d launches)" % (g("A").get("decision"), len(briefs(w))))
    MD2.main(["clear", "A", "--why", "selftest"])
    w.fail_launch = False
    rd, g = run(w, ["A"], root, now=CLOCK + 120)
    ok(g("A").get("klass") == "launch" and len(briefs(w)) == 3,
       "clear 1: after a clear (which resets the system-fault count) the next tick launches "
       "(read %s, %d launches)" % (g("A").get("klass"), len(briefs(w))))
    tr = getattr(AUT, "transient", None)
    ok(tr and tr("ingest.lock stayed busy; nothing filed") and not tr("LAUNCH FAILED pool full") and not tr(None), "transient(): a lock or an unpublished shard is transient, a full pool is not")
    # RIMMANDRAKE_UNSTICK_DISPATCH_CLONE_PUBLISH_LINT_REFUSES_HEAD (2026-11-16): a clone held by a dead run read transient
    # because the filing's own publish line said "publish stopped", and three tries were spent on it in two minutes
    held = ("retry 3 of X, filed earlier; publish: publish stopped: ledger_lint refuses HEAD, the commit stays local; "
            "refused: clone /c/X.det is held: run u is recorded running but its unit is gone, so its finish step never "
            "ran; to pass: detached_helper.py finish --unit u, then return --unit u, then launch again")
    ok(tr and not tr(held), "transient(): a clone held by a dead run is not transient, whatever the publish line said")
    ok(tr and tr("LAUNCH FAILED u: systemd-run did not answer (TimeoutExpired); systemd reads the unit inactive"),
       "transient(): a systemd-run that did not answer (no unit, record launch_failed) is transient")


AGAINST = "version/VERSION.json state reads 'not started: waits for Pyrelands 0.1.0 to pass'"


def designer_lock_checks(root):
    """RIMMANDRAKE_GATE_DESIGNER_LOCKED_ON_VERSION_FILE_NOT_TREE (watched failing on e696f33db1, decision steward): the
    Designer's stage.json `locked` is the concept tree's gate; only VERSION.json locked is the Design Version lock.
    RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME (owner 2026-11-15, the Evidence-for-Ask rule; watched
    failing on 6dcc361c54, every lock an OWNER card): a NEW mod's first Design Version is 0.1.0, locked by the pipeline;
    it reaches him only when recorded evidence says 0.1.0 is wrong, and the card quotes that evidence."""
    import maturation_autonomy as A

    def lane(r, ver, dst, locked, ev=None):
        try:
            A._designer_lane(r, "Graffiti", ver, dst, locked, **({"evidence": ev} if ev else {}))
        except TypeError as e:       # the base has no evidence hook: a FAIL, never a crash
            r["error"] = str(e)
    r = {}
    lane(r, "UNMEASURED", {"status": "locked", "stage": 5}, lambda m: False)
    ok(r.get("decision") == "autolock" and r.get("aut") == "autolock" and not r.get("card"),
       "evidence-for-ask 1: a locked tree, no VERSION.json lock and no evidence against 0.1.0: the pipeline locks "
       "0.1.0 itself, no card (read %s)" % r.get("decision"))
    r = {}
    lane(r, "UNMEASURED", {"status": "locked", "stage": 5}, lambda m: False, ev=lambda m: [AGAINST])
    ok(r.get("decision") == "owner" and not r.get("aut") and AGAINST in str(r.get("why"))
       and AGAINST in str(r.get("card")),
       "evidence-for-ask 2: recorded evidence against 0.1.0 is an OWNER card whose why and text quote it (read %s: %s)"
       % (r.get("decision"), str(r.get("card") or r.get("error"))[:120]))
    r = {}
    lane(r, "0.1.0", {"status": "locked", "stage": 5}, lambda m: True, ev=lambda m: [AGAINST])
    ok(r.get("decision") == "steward" and r.get("steward_kind") == "designer_locked",
       "evidence-for-ask 3: a locked tree with VERSION.json locked is the steward's advance, untouched by the lock")
    r = {}
    A._designer_lane(r, "Graffiti", "0.1.0", {"status": "drafting", "stage": 5}, lambda m: True)
    ok(r.get("decision") == "steward", "designer lock: stage 5 with VERSION.json locked is the steward's advance")
    r = {}
    lane(r, "UNMEASURED", {"status": "drafting", "stage": 5}, lambda m: False)
    ok(r.get("decision") == "designer_wait" and not r.get("aut") and not r.get("card"),
       "evidence-for-ask 4: an unlocked tree (stage 5, drafting) does nothing: the Designer's wait, never an OWNER "
       "card or a lock (read %s)" % r.get("decision"))
    # the tick: the lock act runs once, then the locked version is the steward's; a dry pass only says it would
    fresh_state()
    w = World({}, dstate={"Gf": {"status": "locked", "stage": 5, "history": []}}, locked=False)
    w.facts = {"Gf": {"mod": "Gf", "stage": "designer", "live_units": []}}
    rd, g = run(w, ["Gf"], root)
    rd2, g2 = run(w, ["Gf"], root, now=CLOCK + 60)
    ok(w.autolocked == ["Gf"] and g("Gf").get("klass") == "launch" and "PUBLISHED" in str(g("Gf").get("why"))
       and not w.cards and g2("Gf").get("decision") == "launched" and w.launched and w.launched[0][0] == "brief",
       "evidence-for-ask 1: the tick locks 0.1.0 once (the act lands it), writes no card, then the steward advances "
       "the locked version (read %s / %s, locks %s, cards %d)" % (g("Gf").get("decision"), g2("Gf").get("decision"),
                                                                    w.autolocked, len(w.cards)))
    fresh_state()
    w = World({}, dstate={"Gf": {"status": "locked", "stage": 5, "history": []}}, locked=False)
    w.facts = {"Gf": {"mod": "Gf", "stage": "designer", "live_units": []}}
    rd = MD.tick(root, dict(CFG, advancing=["Gf"]), False, fx=w.fx(), now=CLOCK)
    ok(rd["mods"]["Gf"].get("decision") == "would_launch" and not w.autolocked,
       "evidence-for-ask 1: a dry tick writes nothing: it says the lock would run")
    fresh_state()
    w = World({}, dstate={"Gf": {"status": "locked", "stage": 5, "history": []}}, locked=False)
    w.facts = {"Gf": {"mod": "Gf", "stage": "designer", "live_units": []}}
    w.evidence = {"Gf": [AGAINST]}
    rd, g = run(w, ["Gf"], root)
    rd2, g2 = run(w, ["Gf"], root, now=CLOCK + 60)
    ok(g("Gf").get("klass") == "owner" and g2("Gf").get("klass") == "owner" and not w.autolocked and not w.launched
       and len([c for c in w.cards if "Gf" in c and AGAINST in c]) == 1,
       "evidence-for-ask 2: with evidence the tick reads OWNER, locks nothing, writes the card quoting it once "
       "(read %s, cards %d)" % (g("Gf").get("decision"), len(w.cards)))
    fresh_state()
    w = World({}, dstate={"Gf": {"status": "locked", "stage": 5, "history": []}}, locked=True)
    w.facts = {"Gf": {"mod": "Gf", "stage": "designer", "live_units": []}}
    rd, g = run(w, ["Gf"], root)
    ok(not w.autolocked and g("Gf").get("decision") == "launched",
       "evidence-for-ask 3: an already-locked version is never re-locked; the steward advances it")
    upstream_wait_checks()
    evidence_and_act_checks()


def upstream_wait_checks():
    """RIMMANDRAKE_READ_STALE_OWNER_HOLD_AS_WAITING (watched failing on 8586d42006, decision owner): an OWNER HOLD on
    the Designer whose VERSION.json says the version waits for another mod's version to pass reads as waiting on that
    mod's version while it has not passed, never as his; once it has passed, the hold is his again."""
    import maturation_autonomy as A
    tmp = tempfile.mkdtemp(prefix="upw_")
    try:
        concept(tmp, "PyM", {"version/VERSION.json": {"mod": "PyM", "version": "0.1.0", "state":
                             "not started: waits for Pyr 0.1.0 to pass; stays out of test mod lists until then"}})
        concept(tmp, "Pyr", {"version/VERSION.json": {"mod": "Pyr", "version": "0.1.0", "state": "locked"},
                             "version/stage_record.json": {"mod": "Pyr", "version": "0.1.0", "stage": "offline_build"}})
        hold = {"status": "blocked", "stage": 4, "blocked_on": "REFUSAL_NOTHING_COULD_EVER_PASS: OWNER HOLD, not a "
                "refusal: the Designer loop is held while the Design Version 0.1.0 entry lands"}

        def lane():
            r = {"mod": "PyM"}
            try:
                A._designer_lane(r, "PyM", "0.1.0", hold, lambda m: True, root=tmp)
            except TypeError as e:      # the base takes no root: a FAIL, never a crash
                r["error"] = str(e)
            return r
        r = lane()
        ok(r.get("decision") not in ("owner", None) and "Pyr 0.1.0" in str(r.get("why")) and not r.get("card")
           and not r.get("aut"),
           "upstream wait: an OWNER HOLD whose version waits for Pyr 0.1.0 (not passed) reads as waiting on Pyr 0.1.0, "
           "no card, no launch (read %s: %s)" % (r.get("decision"), str(r.get("why") or r.get("error"))[:160]))
        if not r.get("error"):
            A._klass({}, {}, r, CLOCK, {})
            ok(r.get("klass") == "wait" and "waiting on Pyr 0.1.0 to pass" in str(r.get("status")) and not r["stalled"],
               "upstream wait: the board line reads 'waiting on Pyr 0.1.0 to pass' (read %s)" % r.get("status"))
        concept(tmp, "Pyr", {"version/stage_record.json": {"mod": "Pyr", "version": "0.1.0", "stage": "passed"}})
        r = lane()
        ok(r.get("decision") == "owner",
           "upstream wait: once Pyr 0.1.0 has passed, the OWNER HOLD is his again (read %s)" % r.get("decision"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def concept(root, mod, files):
    c = os.path.join(root, "design", "concepts", mod)
    for rel, data in files.items():
        os.makedirs(os.path.dirname(os.path.join(c, rel)), exist_ok=True)
        with open(os.path.join(c, rel), "w", encoding="utf-8") as f:
            f.write(data if isinstance(data, str) else json.dumps(data))
    return c


def evidence_and_act_checks():
    """The evidence reader and the lock act on real files (a temp root; the act's landing is faked)."""
    import maturation_autonomy as A
    ve, act = getattr(A, "version_evidence", None), getattr(A, "autolock_and_land", None)
    ok(callable(ve) and callable(act), "evidence-for-ask: version_evidence() and autolock_and_land() exist")
    if not (callable(ve) and callable(act)):
        return
    tmp = tempfile.mkdtemp(prefix="efa_")
    try:
        rec = {"mod": "X", "version": "UNMEASURED", "stage": "designer"}
        concept(tmp, "New", {"stage.json": {"status": "locked", "stage": 5}, "version/stage_record.json": rec})
        concept(tmp, "Held", {"version/VERSION.json": {"mod": "Held", "version": "0.1.0",
                                                       "state": "not started: waits for Pyrelands 0.1.0 to pass"},
                              "version/stage_record.json": rec})
        concept(tmp, "Open", {"version/VERSION.json": {"mod": "Open", "version": "0.1.0", "state": "open: admitted"},
                              "version/stage_record.json": rec})
        concept(tmp, "Later", {"version/VERSION.json": {"mod": "Later", "version": "0.2.0", "state": "open"},
                               "version/stage_record_0.1.0.json": rec, "version/stage_record.json": rec})
        concept(tmp, "Objected", {"record.json": {"version_objection": "this continues RM_Old 1.4, not a new mod"},
                                  "version/stage_record.json": rec})
        got = {m: ve(tmp, m) for m in ("New", "Held", "Open", "Later", "Objected")}
        ok(got["New"] == [] and got["Open"] == [],
           "evidence-for-ask: a new mod (no VERSION.json, or one still open at 0.1.0) has no evidence against 0.1.0 "
           "(read %s)" % {m: got[m] for m in ("New", "Open")})
        ok(any("not started" in x for x in got["Held"]) and any("0.2.0" in x for x in got["Later"])
           and any("stage_record_0.1.0.json" in x for x in got["Later"])
           and any("RM_Old 1.4" in x for x in got["Objected"]),
           "evidence-for-ask: a recorded hold, another version, an earlier version's record and a written objection "
           "are each quoted as evidence (read %s)" % {m: got[m] for m in ("Held", "Later", "Objected")})
        c = concept(tmp, "Lockme", {"stage.json": {"status": "locked", "stage": 5,
                                                   "budget": {"spent": 1234, "charges": []}},
                                    "tree.json": {"leaves": [{"id": "a"}, {"id": "b"}]},
                                    "record.json": {"inventory": [{"id": "c"}]},
                                    "version/stage_record.json": rec})
        landed = []
        out = act(tmp, "Lockme", now=CLOCK, land=lambda subj, paths: (landed.append((subj, paths)), "PUBLISHED f00d")[1])
        v = json.load(open(os.path.join(c, "version", "VERSION.json")))
        ok(v.get("version") == "0.1.0" and v.get("state") == "locked" and v.get("locked_by") == "pipeline"
           and v.get("per_ruling") == A.M.EVIDENCE_FOR_ASK and "owner_words" not in v and v.get("tokens_spent") == 1234
           and v.get("bars_total") == 3 and v.get("bars_met") == "UNMEASURED" and out == "PUBLISHED f00d",
           "evidence-for-ask: the act writes VERSION.json locked 0.1.0 by the pipeline under the ruling, no owner "
           "words, numbers measured or UNMEASURED (read %s)" % {k: v.get(k) for k in ("state", "locked_by",
                                                                                     "tokens_spent", "bars_total")})
        dg = [p for p in (landed[0][1] if landed else []) if p.startswith("infrastructure/state/delegated/")]
        ok(len(landed) == 1 and "design/concepts/Lockme/version/VERSION.json" in landed[0][1] and len(dg) == 1,
           "evidence-for-ask: one landing carries VERSION.json and the digest record (read %s)" % landed)
        if dg:
            import delegated_digest as DD
            r = DD.verdict_read(tmp, os.path.join(tmp, "infrastructure", "state", "delegated"), added={})
            got = [x[2] for x in r["items"]]
            ok(len(got) == 1 and got[0].get("decision") and got[0].get("class") == "design"
               and got[0].get("item") == A.M.EVIDENCE_FOR_ASK,
               "evidence-for-ask: the lock reaches his daily digest (the digest's own reader reads it: %s)" % got)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def road_back_checks(root):
    """RIMMANDRAKE_RUN_ROAD_BACK_FIXERS_SAME_STAGE_SKIPPED_THEM (acceptance test folded in, watched failing on
    e696f33db1): a blind_challenge -> blind_challenge road back gives each open item its fixer before the next cycle
    launches; its closing makes the state new for the steward (the key grows |after:<item>), once; a second steward on
    the same cycle keeps the first one's items; an empty road back on an unmoved mod waits for the clone's ledger."""
    import maturation_autonomy as A
    cfg = dict(CFG)
    facts = {"M": {"version": "0.1.0", "live_units": []}}
    why = "1 Problem(s) not FIXED: RIMMANDRAKE_PAIR_X"

    def res(st, dec, items, stage="blind_challenge"):
        rows = [{"mod": "M", "stage": stage, "decision": dec, "cycle": 1 if dec.startswith("exit") else 2, "why": why}]
        fx = {"open_items": lambda ids: [x for i in ids for x in items.get(i, [])], "designer_state": lambda m: {},
              "version_locked": lambda m: True}
        rows, launches = A.resolve(root, cfg, st, facts, rows, ["M"] if dec in A.LAUNCH else [], CLOCK, fx)
        return rows[0], launches

    for dec in ("launch", "would_launch"):
        st = {"mods": {"M": {"road_back": {"caused_by": "ROUTE_X", "from": "blind_challenge"}}}}
        r, la = res(st, dec, {"ROUTE_X": [{"id": "FIX_ME"}]})
        ok(r.get("fix_item") == "FIX_ME" and r.get("aut") == "fixer" and la == ["M"],
           "road back: a %s row with an open road-back item gets its fixer first (read %s, %s)" % (
               dec, r.get("decision"), r.get("fix_item")))
    st = {"mods": {"M": {"road_back": {"caused_by": "ROUTE_X", "from": "blind_challenge"}}}}
    st["mods"]["M"]["fixers"] = {"FIX_ME": {"item": "FIX_ME"}}
    r, la = res(st, "launch", {"ROUTE_X": [{"id": "FIX_ME"}]})
    ok(r.get("decision") == "fixer_spent" and la == [], "road back: a spent fixer on a still-open item holds the "
       "launch (read %s, launches %s)" % (r.get("decision"), la))
    st = {"mods": {"M": {"road_back": {"caused_by": "ROUTE_X", "from": "blind_challenge"}}}}
    r, la = res(st, "launch", {})
    ok(r.get("decision") == "launch" and la == ["M"] and not st["mods"]["M"].get("road_back"),
       "road back: every item closed, the next cycle launches and the road back is popped")
    # the unmoved mod (GimmeSomeSlack, 2026-11-15): the steward held at exit_not_met, its items get fixers
    k1 = "0.1.0|blind_challenge|exit_not_met|1|%s" % A._h(why)
    st = {"mods": {"M": {"road_back": {"caused_by": "ROUTE_X", "from": "blind_challenge"},
                         "steward": {k1: {"item": "ROUTE_X", "unit": "u1"}}}}}
    r, _ = res(st, "exit_not_met", {"ROUTE_X": [{"id": "FIX_ME"}]})
    ok(r.get("fix_item") == "FIX_ME", "road back: an unmoved exit_not_met mod's open item gets its fixer (read %s)" %
       r.get("decision"))
    r, _ = res(st, "exit_not_met", {})
    ok(r.get("aut") == "steward" and r.get("steward_key") == k1 + "|after:ROUTE_X"
       and r.get("road_back_after") == ["ROUTE_X"] and not st["mods"]["M"].get("road_back"),
       "road back: its items closed, the steward reads a new state (key %s)" % r.get("steward_key"))
    brief = A.steward_brief(root, "M", dict(r, steward_kind="exit_not_met"))
    ok("ROUTE_X opened is CLOSED" in brief, "road back: the second steward's brief says the road back closed")
    st["mods"]["M"]["steward"][r["steward_key"]] = {"item": "ROUTE_X_RUN_TWO", "unit": "u2"}
    r, _ = res(st, "exit_not_met", {})
    ok(r.get("decision") == "steward_spent", "road back: that second steward ended unmoved, filing nothing: spent, "
       "never a third (read %s)" % r.get("decision"))
    # a second steward on the same cycle replaced road_back: the first one's open item still gets its fixer
    k2 = "0.1.0|blind_challenge|exit_not_met|1|deadbeef"
    st = {"mods": {"M": {"road_back": {"caused_by": "ROUTE_X_RUN_TWO", "from": "blind_challenge"},
                         "steward": {k1: {"item": "ROUTE_X"}, k2: {"item": "ROUTE_X_RUN_TWO"}}}}}
    r, la = res(st, "launch", {"ROUTE_X": [{"id": "PAIR_TWIN"}]})
    ok(r.get("fix_item") == "PAIR_TWIN", "road back: a sibling steward's open item on the same cycle gets its fixer "
       "(read %s)" % r.get("decision"))
    # the clone's ledger lags: an empty road back on an unmoved mod stays open, then its items get fixers
    st = {"mods": {"M": {"road_back": {"caused_by": "ROUTE_X", "from": "blind_challenge"},
                         "steward": {k1: {"item": "ROUTE_X", "unit": "u1"}}}}}
    r, _ = res(st, "exit_not_met", {})
    ok(r.get("decision") == "steward_spent" and st["mods"]["M"].get("road_back") and not
       st["mods"]["M"]["steward"][k1].get("road_back_closed"),
       "road back: empty on an unmoved mod (filings not yet in the clone): spent, the road back kept, nothing marked")
    r, _ = res(st, "exit_not_met", {"ROUTE_X": [{"id": "FIX_LATE"}]})
    ok(r.get("fix_item") == "FIX_LATE", "road back: the late filings get their fixer")


STOP = {"status": "blocked", "stage": 5, "item": "CONCEPT_P", "blocked_on": "REFUSAL_NOTHING_COULD_EVER_PASS: stopped",
        "history": [{"at": "2026-11-15T13:54:40Z", "what": "locked_change"},
                    {"at": "2026-11-15T13:56:22Z", "what": "coverage_release"},
                    {"at": "2026-11-15T14:05:35Z", "what": "coverage_stop", "why": "round 6 not_covered"}]}


def _res(root, st, dst, tickets=(), runs=None, live=(), dec="ready", stage="offline_build", extra=None):
    """One resolve + classify on mod P (coverage-stopped by default) -> (row, launches)."""
    import maturation_autonomy as A
    facts = {"P": {"version": "0.1.0", "live_units": []}}
    for i, u in enumerate(live):
        facts["L%d" % i] = {"version": "0.1.0", "live_units": [u]}
    fx = {"designer_state": lambda m: dst, "version_locked": lambda m: False, "open_items": lambda ids: [],
          "version_evidence": lambda m: [], "designer_unit": lambda m: None, "designer_chain": lambda m: None,
          "stop_tickets": lambda m, d, s: None if tickets is None else [{"id": t} for t in tickets],
          "ticket_runs": lambda i: (runs or {}).get(i, [])}
    fx.update(extra or {})
    rows = [{"mod": "P", "stage": stage, "decision": dec, "why": "decide's reading", "need": "P: ready to advance"}]
    rows, launches = A.resolve(root, dict(CFG), st, facts, rows, [], CLOCK, fx)
    A.classify(dict(CFG), st, rows, CLOCK)
    return rows[0], launches


def paused_fix_checks(root):
    """RIMMANDRAKE_RUN_FIX_TICKETS_WHILE_PAUSED ("paused-fix"): a coverage-stopped mod's own open fix tickets (the
    granted look's items, its road back, the fix items caused by its concept item) get their one fixer run each while
    it stays paused, within max_live and the caps, and its status names the ticket. Watched failing on 6d8f7fe94c."""
    import types
    import maturation_autonomy as A
    st = {"mods": {}}
    r, la = _res(root, st, STOP, ["FIX_T"])
    ok(r.get("aut") == "fixer" and r.get("fix_item") == "FIX_T" and la == ["P"] and "FIX_T" in str(r.get("status")),
       "paused-fix: a coverage-stopped mod with an open fix ticket launches one fixer on it, its status naming it "
       "(read %s, %s)" % (r.get("decision"), r.get("status")))
    ok(not r.get("need"), "paused-fix: a fixer launch owes no Needs Conductor line (read %s)" % r.get("need"))
    st = {"mods": {}}
    r, la = _res(root, st, STOP, ["FIX_T"], live=["rm-u1", "rm-u2"])
    ok(r.get("decision") == "slots_full" and la == [] and "FIX_T" in str(r.get("status")),
       "paused-fix: full slots: the ticket's fixer waits, its status naming the ticket (read %s, %s)" % (
           r.get("decision"), r.get("status")))
    st = {"mods": {}}
    unit = "rm-detached-bench-fix-t-1794775111"
    r, la = _res(root, st, STOP, ["FIX_T"], runs={"FIX_T": [(unit, "running")]})
    ok(la == [] and r.get("klass") == "wait" and unit in str(r.get("status")) and "FIX_T" in str(r.get("status")),
       "paused-fix: a live hand run on the ticket is waited on, never doubled (read %s, %s)" % (
           r.get("decision"), r.get("status")))
    ok((st["mods"]["P"].get("fixers") or {}).get("FIX_T", {}).get("unit") == unit,
       "paused-fix: the live hand run is booked as the ticket's one fixer run")
    st = {"mods": {}}
    r, la = _res(root, st, STOP, ["FIX_T"], runs={"FIX_T": [("rm-old", "launch_failed"), ("rm-done", "finished")]})
    ok(la == [] and r.get("decision") == "coverage_stop" and r.get("klass") == "paused"
       and "FIX_T" in str(r.get("status")) and "FIX_T" in str(r.get("need")),
       "paused-fix: an earlier run on the still-open ticket counts: PAUSED naming the spent ticket, no second run "
       "(read %s, %s)" % (r.get("decision"), r.get("status")))
    st = {"mods": {"P": {"fixers": {"FIX_T": {"item": "FIX_T", "unit": "u9"}}}}}
    r, la = _res(root, st, STOP, ["FIX_T", "FIX_U"])
    ok(r.get("fix_item") == "FIX_U" and la == ["P"], "paused-fix: the next unspent ticket gets its fixer (read %s)" %
       r.get("fix_item"))
    for tk, what in (([], "no ticket"), (None, "an unreadable ledger")):
        st = {"mods": {}}
        r, la = _res(root, st, STOP, tk)
        ok(la == [] and not r.get("aut") and r.get("decision") == "coverage_stop" and "PAUSED" in str(r.get("status")),
           "paused-fix: %s: PAUSED on the stop as before, never launched on (read %s)" % (what, r.get("decision")))
    # the default ticket reader: grant items, road-back items, fix items caused by the concept's item; open ones only
    it = lambda st_, kind, cb: types.SimpleNamespace(state=st_, kind=kind, caused_by=cb)     # noqa: E731
    items = {"FIX_G": it("ready", "task", None), "FIX_K": it("proposed", "fix", "CONCEPT_P"),
             "BUILD_K": it("proposed", "build", "CONCEPT_P"), "FIX_DONE": it("done", "fix", "CONCEPT_P"),
             "FIX_R": it("doing", "task", "ROUTE_P"), "FIX_OTHER": it("ready", "fix", "CONCEPT_Q")}
    dst = dict(STOP, coverage_release_granted={"at": "x", "why": "y", "after": ["FIX_G", "FIX_NEVER"]})
    got = A.stop_tickets(dst, {"road_back": {"caused_by": "ROUTE_P"}}, items) if hasattr(A, "stop_tickets") else None
    ok([x["id"] for x in got or []] == ["FIX_G", "FIX_R", "FIX_K"],
       "paused-fix: the default reader finds the granted, road-back and concept fix tickets, open only, in that order "
       "(read %s)" % [x["id"] for x in got or []])
    # RIMMANDRAKE_FIND_CHAIN_STEWARD_FIXES_WHILE_STOPPED_TICK_BLIND: a locked-change chain steward's look stops judging
    # and it files the gaps caused by its own item; those fix tickets get their fixer runs too (they were invisible)
    items = dict(items, FIX_C=it("proposed", "fix", "CHAIN_P"), TASK_C=it("proposed", "task", "CHAIN_P"),
                 FIX_C2=it("proposed", "fix", "CHAIN_OLD"))
    s_ = {"steward": {"0.1.0|chain|2026-11-17T17:26:00Z": {"item": "CHAIN_P"},
                      "0.1.0|blind_challenge|exit_not_met|1|x": {"item": "CHAIN_OLD"}}}
    got = A.stop_tickets(dict(STOP), s_, items)
    ok([x["id"] for x in got or []] == ["FIX_K", "FIX_C"],
       "paused-fix: the default reader finds a chain steward's own fix tickets after the concept's, fix kind only, "
       "never another steward's (read %s)" % [x["id"] for x in got or []])


def final_look_checks(root):
    """RIMMANDRAKE_GRANT_LOOK_AFTER_FIXES_CLOSE ("final look"): a stop after the final look (a release coverage_judge
    applied from a grant) is the owner's: an OWNER card naming coverage_verdict.json, even after a later locked change;
    a stop after a plain release stays PAUSED. Watched failing on 6d8f7fe94c."""
    rel = {"at": "2026-11-15T15:00:00Z", "why": "per d_x", "final": True, "granted_at": "2026-11-15T14:30:00Z",
           "after": ["FIX_T"]}
    hist = STOP["history"] + [{"at": "2026-11-15T14:58:00Z", "what": "locked_change"},
                              {"at": "2026-11-15T15:00:00Z", "what": "coverage_release"},
                              {"at": "2026-11-15T15:20:00Z", "what": "coverage_stop", "why": "round 7 not_covered"}]
    dst = dict(STOP, history=hist, coverage_releases=[rel])
    r, la = _res(root, {"mods": {}}, dst, ["FIX_T"])
    ok(r.get("klass") == "owner" and la == [] and "final look" in str(r.get("card"))
       and "coverage_verdict.json" in str(r.get("card")),
       "final look: a stop after the final look is an OWNER card naming coverage_verdict.json, no fixer (read %s, %s)" % (
           r.get("decision"), str(r.get("card"))[:100]))
    dst2 = dict(dst, status="ready", history=hist + [{"at": "2026-11-15T16:00:00Z", "what": "locked_change"}])
    r, la = _res(root, {"mods": {}}, dst2, [], dec="not_offline", stage="designer")
    ok(r.get("klass") == "owner" and la == [], "final look: a locked change after it is still his, never a chain "
       "(read %s)" % r.get("decision"))
    dst3 = dict(dst, coverage_releases=[dict(rel, final=False)])
    r, la = _res(root, {"mods": {}}, dst3, [])
    ok(r.get("decision") == "coverage_stop", "final look: a stop after a plain release stays PAUSED (read %s)" %
       r.get("decision"))


def repin_wait_checks(root):
    """RIMMANDRAKE_REPIN_WHEN_GRANT_ITEMS_CLOSE ("re-pin wait"): a LOCKED concept's grant whose --after items are all
    closed waits on the re-pin alone (coverage_judge.grant_waits, read for real here over a fixture concept). The tick
    names that wait, and the pipeline re-pins as an act (autorepin: no brief, no run, one landing) citing the sources
    designer_stage.repin_sources found, or stays PAUSED with the refusal record (evidence, would_pass, smallest_fix) and
    the hand command. Once a locked_change is written after the stop, the grant is due and chain_owed fires; an
    unlocked concept never waits on a re-pin."""
    import types
    import coverage_judge as CJ
    import maturation_autonomy as A
    vd = os.path.join(root, "design", "concepts", "P", "version")
    os.makedirs(vd, exist_ok=True)

    def version(state):
        with open(os.path.join(vd, "VERSION.json"), "w") as f:
            json.dump({"mod": "P", "version": "0.1.0", "state": state}, f)
    grant = {"at": "2026-11-15T14:30:00Z", "why": "per d_x", "after": ["FIX_T"]}
    dst = dict(STOP, coverage_release_granted=grant,
               history=STOP["history"] + [{"at": grant["at"], "what": "coverage_release_granted"}])
    closed = {"FIX_T": types.SimpleNamespace(state="done", kind="task", caused_by=None)}
    asked = []
    src = ["OWNER:1794926130118775229@" + "a" * 40]
    refusal = {"clause": "locked_change_cites_his_cards", "evidence": ["%s fix: text: cites CONDUCTOR:17, a delegated "
               "call, never his word" % ("b" * 40)], "observed": "1 of 1 commits ... carry out no card of his",
               "would_pass": "every commit ... is tied to the card of his it carries out",
               "smallest_fix": {"what": "a ledger event on his card's item naming the sha", "attainable": "yes",
                                "cost": "edit"}}

    def plan(result):
        return lambda m: asked.append(m) or result
    x = lambda items, res: {"ledger_items": lambda: items, "repin_plan": plan(res)}       # noqa: E731
    version("locked")
    states = lambda ids: {i: closed[i].state for i in ids if i in closed}                 # noqa: E731
    w = CJ.grant_waits(dst, states, d=os.path.join(root, "design", "concepts", "P"))
    ok(len(w or []) == 1 and "re-pin" in w[0], "re-pin wait: the fixture grant waits on the re-pin alone (read %s)" % w)
    r, la = _res(root, {"mods": {}}, dst, [], extra=x(closed, (src, None)))
    ok(r.get("aut") == "autorepin" and la == ["P"] and r.get("klass") == "launch" and r.get("repin_sources") == src
       and "re-pin" in str(r.get("status")) and "|repin|" in str(r.get("steward_key")),
       "re-pin wait: items closed, his cards found: the pipeline's re-pin act launches citing them (read %s, %s)" % (
           r.get("decision"), str(r.get("status"))[:120]))
    ok(not r.get("need"), "re-pin wait: the act owes no Needs Conductor line (read %s)" % r.get("need"))
    r, la = _res(root, {"mods": {}}, dst, [], extra=x(closed, (src, refusal)))
    need = str(r.get("need"))
    ok(la == [] and not r.get("aut") and r.get("klass") == "paused" and "waits on the re-pin" in need
       and "designer_stage.py repin design/concepts/P" in need and "CONDUCTOR:17" in need
       and "ledger event on his card's item" in need,
       "re-pin wait: a refused re-pin stays PAUSED naming the wait, the hand command, the evidence and the smallest fix "
       "(read %s, %s)" % (r.get("decision"), need[:160]))
    rf = r.get("refusal") or {}
    ok(all(rf.get(k) for k in ("evidence", "would_pass", "smallest_fix")), "re-pin wait: the row carries the refusal "
       "record (read %s)" % sorted(rf))
    # an open --after item: the grant waits on it, its fixer runs as before, no re-pin is planned
    asked[:] = []
    open_ = {"FIX_T": types.SimpleNamespace(state="doing", kind="task", caused_by=None)}
    r, la = _res(root, {"mods": {}}, dst, ["FIX_T"], extra=x(open_, (src, None)))
    ok(r.get("fix_item") == "FIX_T" and r.get("aut") == "fixer" and not asked,
       "re-pin wait: an open --after item gets its fixer and no re-pin is planned (read %s, planned %s)" % (
           r.get("decision"), asked))
    # a live fixer run on a ticket: the re-pin waits for it
    r, la = _res(root, {"mods": {}}, dst, ["FIX_R"], runs={"FIX_R": [("rm-u7", "running")]}, extra=x(closed, (src, None)))
    ok(la == [] and r.get("klass") == "wait" and not r.get("aut"), "re-pin wait: a live ticket run is waited on "
       "before the re-pin (read %s)" % r.get("decision"))
    # the act already tried and failed for good: no second try on its own
    key = "0.1.0|repin|%s" % grant["at"]
    st = {"mods": {"P": {"steward": {key: {"item": None, "failed": "Refused: commit x is not tied", "tries": 1}}}}}
    r, la = _res(root, st, dst, [], extra=x(closed, (src, None)))
    ok(la == [] and r.get("decision") == "launch_failed" and "re-pin" in str(r.get("why")),
       "re-pin wait: a failed re-pin act is not retried on its own (read %s)" % r.get("decision"))
    # execute: the act runs the re-pin with the planned sources and books it under its key
    calls = []
    st = {"mods": {"P": {}}}
    row = {"mod": "P", "aut": "autorepin", "decision": "autorepin", "steward_key": key, "repin_sources": src}
    A.execute(root, dict(CFG), st, [row], ["P"], CLOCK, {"known": lambda: set(), "autorepin":
              lambda rt, m, sv, now=None: calls.append((m, list(sv))) or "PUBLISHED abc1234"})
    ok(calls == [("P", src)] and (st["mods"]["P"]["steward"].get(key) or {}).get("landed") == "PUBLISHED abc1234"
       and row.get("decision") == "launched", "re-pin wait: execute re-pins with the planned sources and books the "
       "landing (read %s, %s)" % (calls, row.get("decision")))
    # repin_and_land: an unlanded re-pin is no re-pin: stage.json is put back byte for byte
    sp = os.path.join(root, "design", "concepts", "P", "stage.json")
    with open(sp, "w") as f:
        json.dump(dst, f)
    before = open(sp, "rb").read()

    def fake_repin(d, sources, why, repo=None):
        with open(os.path.join(d, "stage.json"), "w") as f:
            json.dump(dict(dst, history=dst["history"] + [{"what": "locked_change"}]), f)

    def no_land(subject, paths):
        raise RuntimeError("land.sh exited 1")
    try:
        A.repin_and_land(root, "P", src, now=CLOCK, land=no_land, repin=fake_repin)
        raised = False
    except Exception:       # noqa: BLE001
        raised = True
    ok(hasattr(A, "repin_and_land") and raised and open(sp, "rb").read() == before,
       "re-pin wait: a failed landing puts stage.json back")
    os.remove(sp)
    # after the re-pin: a locked_change after the stop -> the grant is due and the chain is owed
    dst2 = dict(dst, history=dst["history"] + [{"at": "2026-11-15T14:40:00Z", "what": "locked_change"}])
    w2 = CJ.grant_waits(dst2, states, d=os.path.join(root, "design", "concepts", "P"))
    ok(w2 == [] and (A.chain_owed(dst2) or {}).get("what") == "locked_change" and not A.coverage_stopped(dst2),
       "re-pin wait: after a locked_change the grant is due and chain_owed fires (read %s, %s)" % (
           w2, A.chain_owed(dst2)))
    # an unlocked concept: no re-pin wait, no re-pin planned
    version("draft")
    asked[:] = []
    w3 = CJ.grant_waits(dst, states, d=os.path.join(root, "design", "concepts", "P"))
    r, la = _res(root, {"mods": {}}, dst, [], extra=x(closed, (src, None)))
    ok(w3 == [] and r.get("aut") != "autorepin" and not asked and "re-pin" not in str(r.get("need")),
       "re-pin wait: an unlocked concept shows no re-pin wait (read %s, %s)" % (w3, r.get("decision")))
    shutil.rmtree(os.path.join(root, "design", "concepts", "P"), ignore_errors=True)


def exam_gate_checks(root):
    """RIMMANDRAKE_RETAKE_FAILING_EXAM_NOT_SILENT ("exam gate"): a stage-5 concept whose exam fails its gate is owed
    work: one exam_retake steward whose brief is roles/designer_exam.md in full; a spent retake is PAUSED with the
    gate's text; a passing exam stays a Designer wait. Watched failing on 6d8f7fe94c."""
    import maturation_autonomy as A
    ds = {"status": "ready", "stage": 5, "history": []}
    errs = ["exam: no scenario is the Challenger's", "exam: no control copy"]
    gate = {"exam_gate": lambda m: (errs, "treehash123456")}
    st = {"mods": {}}
    r, la = _res(root, st, ds, dec="not_offline", stage="designer", extra=gate)
    ok(r.get("aut") == "steward" and r.get("steward_kind") == "exam_retake" and la == ["P"]
       and "exam fails its gate" in str(r.get("status")),
       "exam gate: a failing exam launches one exam_retake steward, its status saying so (read %s, %s)" % (
           r.get("decision"), r.get("status")))
    brief = A.steward_brief(root, "P", r) if r.get("aut") else ""
    ok("roles/designer_exam.md" in brief and "Challenger" in brief and "no control copy" in brief,
       "exam gate: the retake brief names roles/designer_exam.md and the gate's errors")
    # RIMMANDRAKE_UNPIN_RETAKE_DONE_FROM_A_RESULT_NEVER_WRITTEN: `designer_stage.py check` validates an open
    # Designer run's result.json; a steward retake opens no run, so no correct retake could ever meet that clause
    ok("designer_stage.py check" not in brief and "coverage_judge.py status" in brief,
       "exam gate: the retake brief's done clause is the exam gate a steward can meet (coverage_judge.py status), "
       "never `designer_stage.py check` (an open run's result.json)")
    spec = A.advance_checks(r) if r.get("aut") else None
    ok(spec == "## launch-checks\nmust-pass: python3 src/RimMandrake/rimflow/designer_stage.py open design/concepts/P "
       "--run launch-check --preview\n", "exam gate: the retake steward's item is filed with the Designer open preview "
       "as its launch check (RIMMANDRAKE_PREVIEW_THREE_GATES_READ_ONLY_FOR_LAUNCH_CHECKS) (read %r)" % (spec,))
    name = A.item_name(dict(r, mod="Pyrelands"), set()) if r.get("aut") else ""
    ok(name == "RIMMANDRAKE_RETAKE_PYRELANDS_EXAM_FAILING_ITS_GATE", "exam gate: its item is named for it (read %s)" %
       name)
    st["mods"]["P"]["steward"] = {r.get("steward_key"): {"item": name, "unit": "rm-u7"}}
    r, la = _res(root, st, ds, dec="not_offline", stage="designer", extra=gate)
    ok(r.get("klass") == "paused" and la == [] and "exam fails its gate" in str(r.get("status")),
       "exam gate: a spent retake on the same tree is PAUSED with the gate's text (read %s)" % r.get("status"))
    r, la = _res(root, {"mods": {}}, ds, dec="not_offline", stage="designer",
                 extra={"exam_gate": lambda m: ([], "treehash123456")})
    ok(r.get("decision") == "designer_wait" and la == [], "exam gate: a passing exam stays a Designer wait (read %s)" %
       r.get("decision"))
    r, la = _res(root, {"mods": {}}, dict(ds, stage=3), dec="not_offline", stage="designer", extra=gate)
    ok(r.get("decision") == "designer_wait", "exam gate: before stage 5 the exam is not read (read %s)" %
       r.get("decision"))
    # RIMMANDRAKE_SPARE_EXAM_RETAKE_WHEN_ONLY_SCENES_MOVED: Graffiti 2026-11-18, a locked change that moved only
    # scenes.json (re-pinned stages 3 and 4) left the exam passing its gate on the same tree and sheet, yet the chain
    # brief ordered a full retake its Readers would have answered from identical inputs
    lc = {"status": "ready", "stage": 5, "history": [{"at": "2026-11-18T17:58:16Z", "what": "locked_change",
                                                       "why": "re-pinned stage 3 (scenes); stage 4 (scenes)"}]}
    r, la = _res(root, {"mods": {}}, lc, dec="not_offline", stage="designer",
                 extra={"exam_gate": lambda m: ([], "treehash123456")})
    need = str(r.get("steward_need"))
    ok(r.get("steward_kind") == "chain" and "stands" in need and "treehash123" in need
       and "retake the Cold Reader exam on the new tree" not in need,
       "exam gate: a chain whose exam still passes its gate on the current tree and sheet keeps it, no retake "
       "(read %s)" % need[:200])
    r, la = _res(root, {"mods": {}}, lc, dec="not_offline", stage="designer", extra=gate)
    need = str(r.get("steward_need"))
    ok(r.get("steward_kind") == "chain" and "retake the Cold Reader exam on the new tree" in need,
       "exam gate: a chain whose exam fails its gate retakes it in full (read %s)" % need[:200])
    r, la = _res(root, {"mods": {}}, lc, dec="not_offline", stage="designer",
                 extra={"exam_gate": lambda m: ([], None)})
    ok("retake the Cold Reader exam on the new tree" in str(r.get("steward_need")),
       "exam gate: a chain whose exam gate could not be read (no tree hash) retakes it in full")
    # RIMMANDRAKE_SKIP_CHAIN_LOOK_ON_SIGNED_TREE_CARRIED_CERTIFICATE: ExplosiveKnockback 2026-11-24, the Conductor
    # carried the owner certificate onto the reworded tree (644106e197) and the tick still launched a chain steward for
    # a look coverage_judge.plan refuses on a signed tree ("already signed"); its next brief would order a whole paid
    # exam retake for a floor.hash re-pin
    r, la = _res(root, {"mods": {}}, lc, dec="not_offline", stage="designer",
                 extra={"exam_gate": gate["exam_gate"], "coverage_signed": lambda m: True})
    ok(r.get("steward_kind") != "chain" and not any("chain" in str(x) for x in la),
       "signed tree: a locked change on a tree whose coverage signature is valid owes no chain look (read %s, %s)" % (
           r.get("steward_kind"), r.get("decision")))
    r, la = _res(root, {"mods": {}}, lc, dec="not_offline", stage="designer",
                 extra={"exam_gate": gate["exam_gate"], "coverage_signed": lambda m: False})
    ok(r.get("steward_kind") == "chain",
       "signed tree: an unsigned tree after a locked change still owes the chain (read %s)" % r.get("steward_kind"))
    r, la = _res(root, {"mods": {}}, lc, dec="not_offline", stage="designer",
                 extra={"exam_gate": gate["exam_gate"], "coverage_signed": lambda m: None})
    ok(r.get("steward_kind") == "chain",
       "signed tree: a signature that could not be read (None) still owes the chain (read %s)" % r.get("steward_kind"))


def worked_after_checks(root):
    """Pyrelands 2026-11-16: its 'ready' steward refused a false pass (owed scene parts), builders then closed the owed
    tickets and the reading came back 'every exit test passes', the same key: paused steward_spent for good. A run
    that works the mod after its steward ended makes the next reading a new state; nothing else does
    (RIMMANDRAKE_UNSTICK_FIVE_STILL_MODS_TWO_OF_TWELVE_MOVING)."""
    fresh_state()
    w = World({"P": offline("P", "ready to advance")})
    rd, g = run(w, ["P"], root)
    briefs = lambda: [x for x in w.launched if x[0] == "brief"]  # noqa: E731
    ok(g("P").get("klass") == "launch" and len(briefs()) == 1, "worked-after: a ready mod gets one steward run")
    own = briefs() and "rm-fake-%d" % len(w.launched)
    w.facts = {"P": dict(offline("P", "ready to advance"), live_units=[own])}
    rd, g = run(w, ["P"], root, now=CLOCK + 300)
    w.facts = {"P": offline("P", "ready to advance")}
    rd, g = run(w, ["P"], root, now=CLOCK + 900)
    ok(g("P").get("klass") == "paused" and len(briefs()) == 1,
       "worked-after: the steward's own run live then ended, state unmoved: paused, no second steward")
    w.facts = {"P": dict(offline("P", "ready to advance"), live_units=["rm-detached-bench-autobuild-p-1"])}
    rd, g = run(w, ["P"], root, now=CLOCK + 1200)
    w.facts = {"P": offline("P", "ready to advance")}
    rd, g = run(w, ["P"], root, now=CLOCK + 1800)
    ok(g("P").get("klass") == "launch" and len(briefs()) == 2,
       "worked-after: a builder worked it after the steward ended: the same reading is a new state, one more steward")
    own2 = "rm-fake-%d" % len(w.launched)
    done = [{"unit": own2, "end": CLOCK + 2000}, {"unit": "rm-detached-bench-autobuild-p-1", "end": CLOCK + 1500}]
    w.facts = {"P": dict(offline("P", "ready to advance"), ended_runs=done)}
    rd, g = run(w, ["P"], root, now=CLOCK + 2400)
    ok(g("P").get("klass") == "paused" and len(briefs()) == 2,
       "worked-after: that second steward is spent too (a run that ended before it is no new work): paused")
    # RIMMANDRAKE_SEE_RESCUE_RUN_ON_ITS_MOD: a run seen only as ended, after the steward ended, is new work
    w.facts = {"P": dict(offline("P", "ready to advance"),
                         ended_runs=done + [{"unit": "rm-detached-bench-lay-p-1", "end": CLOCK + 2900}])}
    rd, g = run(w, ["P"], root, now=CLOCK + 3000)
    ok(g("P").get("klass") == "launch" and len(briefs()) == 3,
       "worked-after: a run never seen live that ended after the steward ended: one more steward")
    rd, g = run(w, ["P"], root, now=CLOCK + 3600)
    ok(g("P").get("klass") == "paused" and len(briefs()) == 3,
       "worked-after: that third steward is spent too: paused, never a fourth without new work")


def rearrival_checks(root):
    """RIMMANDRAKE_SEE_SECOND_ARRIVAL_AT_STEWARD_STAGE_NOT_SPENT: a steward stage's key was `<ver>|<stage>`, so a mod
    that reached the stage again at the same version read its first arrival's steward as spent. Measured 2026-11-22
    06:03Z: GimmeSomeSlack 0.1.1 reached the walk brief (Stage 7) at 04:33 PST 11-21, its steward (…-pre-h-1795265290)
    wrote arrival_1 and advanced it to his walk; it went back to Stage 6 and arrived at Stage 7 again at 21:40 PST, and
    read PAUSED 'the steward run is spent … ended and the state has not moved'. A steward booked before the mod's latest
    arrival at the stage worked an earlier arrival, never this one."""
    for stage in ("pre_human", "preflight"):
        fresh_state()
        facts = lambda arrived: {"mod": "S", "stage": stage, "version": "0.1.1", "live_units": [],  # noqa: E731
                                 "owed": "steward", "exit": {"state": "not_met", "why": ["-"]},
                                 "arrived": {stage: arrived}}
        briefs = lambda w: [x for x in w.launched if x[0] == "brief"]  # noqa: E731
        w = World({"S": facts(CLOCK - 60)})
        rd, g = run(w, ["S"], root)
        ok(g("S").get("klass") == "launch" and len(briefs(w)) == 1,
           "re-arrival (%s): the first arrival gets one steward (read %s/%s)" % (
               stage, g("S").get("klass"), g("S").get("decision")))
        rd, g = run(w, ["S"], root, now=CLOCK + 900)
        ok(g("S").get("decision") == "steward_spent" and len(briefs(w)) == 1,
           "re-arrival (%s): that steward ended on the same arrival: spent, no second (read %s)" % (
               stage, g("S").get("decision")))
        w.facts = {"S": facts(CLOCK + 5000)}
        rd, g = run(w, ["S"], root, now=CLOCK + 5600)
        ok(g("S").get("klass") == "launch" and len(briefs(w)) == 2,
           "re-arrival (%s): a later arrival at the same version is a new state, one steward (read %s/%s: %s)" % (
               stage, g("S").get("klass"), g("S").get("decision"), str(g("S").get("status"))[:120]))
        rd, g = run(w, ["S"], root, now=CLOCK + 6600)
        ok(g("S").get("decision") == "steward_spent" and len(briefs(w)) == 2,
           "re-arrival (%s): that second steward is spent too on its own arrival, never a third (read %s)" % (
               stage, g("S").get("decision")))


def main():
    if os.environ.get("MAT_AUT_BASE_DIR"):
        print("against the base dispatcher in %s" % os.path.dirname(MD.__file__))
    tmp = tempfile.mkdtemp(prefix="mat_aut_")
    root = os.path.join(tmp, "root")
    with open(os.path.join(tmp, "mod_owner_hold.json"), "w") as f:     # the fixture holds nothing: the live list is
        json.dump({"holds": []}, f)                                 # selftest_mod_owner_hold.py's (mod_owner_hold.py)
    os.environ["RM_OWNER_HOLD_FILE"] = os.path.join(tmp, "mod_owner_hold.json")
    os.makedirs(os.path.join(root, "design", "concepts"))
    os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(tmp, "state")
    os.environ["MATURATION_BRIEF_DIR"] = os.path.join(tmp, "briefs")
    os.makedirs(os.environ["RM_MATURATION_DISPATCH_DIR"])
    try:
        # (3) an in-game visit owed, the game free: launch; two owed, one driver: the second waits with a queue position
        fresh_state()
        w = World({"A": ingame("A", "run"), "B": ingame("B", "run")})
        rd, g = run(w, ["A", "B"], root)
        ok(g("A").get("klass") == "launch" and ("stage", "A", "RIMMANDRAKE_DRIVE_A_IN_GAME_ACCEPTANCE_VISIT_ONE")
           in w.launched, "wait 3: an owed visit on a free game launches its live driver (item name ends in a word)")
        ok(g("B").get("klass") == "wait" and g("B").get("queue") == 1,
           "wait 3: the second owed visit waits on the driver with its game-queue position recorded")
        # fairness: B queued first; next tick A is owed again (visit 2) and B, the longer waiter, goes first
        w2 = World({"A": ingame("A", "run", visit=2), "B": ingame("B", "run")})
        rd, g = run(w2, ["A", "B"], root, now=CLOCK + 600)
        ok(g("B").get("klass") == "launch" and g("A").get("klass") == "wait",
           "wait 3: visits queue fairly: the mod queued longest gets the free game, not the first in list order")
        # held game: wait, never a launch
        fresh_state()
        w = World({"A": ingame("A", "run")}, bridge=(False, "OWNER hold"))
        rd, g = run(w, ["A"], root)
        ok(g("A").get("klass") == "wait" and not w.launched, "a held game: wait (bridge held), nothing launched")
        # a refused judge (visit not met): ONE steward run routes the failed lines back
        fresh_state()
        w = World({"A": ingame("A", "exit not met", why=["sc_ruins reads UNMEASURED at 100% of rows"])})
        rd, g = run(w, ["A"], root)
        st = [x for x in w.launched if x[0] == "brief"]
        ok(g("A").get("klass") == "launch" and st and "ROUTE_A_VISIT_ONE_FAILURES_BACK" in st[0][1] and st[0][2] == "opus",
           "wait 5: a not-met visit launches one opus steward run that files the failed lines and routes them back")
        ok(w.briefs and "--caused-by RIMMANDRAKE_ROUTE_A_VISIT_ONE_FAILURES_BACK" in w.briefs[0]
           and "Never certify" in w.briefs[0], "the steward brief files items caused by its own item and forbids "
           "certify/lock/classify")
        # the steward ended, the state did not move: PAUSED, never a second try
        rd, g = run(w, ["A"], root, now=CLOCK + 900)
        ok(g("A").get("klass") == "paused" and len([x for x in w.launched if x[0] == "brief"]) == 1
           and "A: " in " ".join(rd.get("paused") or []), "a dead steward run on an unmoved state: PAUSED, listed for "
           "the alarm, no second launch")
        # the road back: the steward moved A to the offline build and filed two items: one fixer per item
        w.facts = {"A": offline("A", "ready to advance")}
        w.items = {"RIMMANDRAKE_ROUTE_A_VISIT_ONE_FAILURES_BACK": [{"id": "RIMMANDRAKE_FIX_A_RUINS_SCENE_SPAWNS"},
                                                                   {"id": "RIMMANDRAKE_FIX_A_ULLAI_SCENE_READS"}]}
        n0 = len(w.launched)
        rd, g = run(w, ["A"], root, now=CLOCK + 1200)
        ok(g("A").get("klass") == "launch" and w.launched[n0:] == [("brief", "RIMMANDRAKE_FIX_A_RUINS_SCENE_SPAWNS",
                                                                     "opus")],
           "wait 5: an open road-back item gets one fixer run (the existing item, not a new one)")
        # every road-back item closed: the mod moves on (ready to advance -> a steward advance)
        w.items = {"RIMMANDRAKE_ROUTE_A_VISIT_ONE_FAILURES_BACK": []}
        n0 = len(w.launched)
        rd, g = run(w, ["A"], root, now=CLOCK + 1500)
        ok(g("A").get("klass") == "launch" and any("ADVANCE_A_PAST_OFFLINE_BUILD" in x[1] for x in w.launched[n0:]),
           "wait 5: when the road-back items close, ready-to-advance is a steward advance, not a Conductor line")
        ok(not rd.get("needs_conductor"), "no Needs Conductor line for a ready mod")
        adv = [i for i in w.specs if "ADVANCE_A_PAST_OFFLINE_BUILD" in i]
        ok(adv and w.specs[adv[0]] == "## launch-checks\nmust-pass: python3 src/RimMandrake/rimflow/maturation.py gate A "
           "--to blind_challenge\n" and not any(v for k, v in w.specs.items() if "ROUTE_A" in k),
           "the advance steward's item is filed with its gate as a launch check (GATE_FIRST); a routing steward's is not")
        # (1) a locked change newer than every look: the chain
        fresh_state()
        ds = {"status": "blocked", "stage": 5, "history": [
            {"at": "2026-11-15T06:14:43Z", "what": "coverage_stop"},
            {"at": "2026-11-15T13:23:41Z", "what": "locked_change", "why": "his card: fix all 12"}]}
        w = World({"P": ingame("P", "exit not met", why=["x"])}, dstate={"P": ds})
        rd, g = run(w, ["P"], root)
        ok(g("P").get("klass") == "launch" and any("RETAKE_P_EXAM_AFTER_LOCKED_CHANGE" in x[1] for x in w.launched),
           "wait 1: a locked change with no look after it launches the chain (re-pin, exam retake, one look)")
        ok(any("close an `after` item" in b and "origin/main" in b for b in w.briefs),
           "wait 1: the chain brief closes a landed `after` item of a granted look (a fixer that left its ticket open)")
        # RIMMANDRAKE_GUARD_ONE_COVERAGE_LOOK_STEWARD_LAUNCHER_BOTH_RAN: the steward claims stage 5 before its hand look,
        # so the launcher's stage-5 run (whose pre-step is the judge) cannot open beside it; and the plain release IS
        # what applies a standing grant (coverage_judge.release), so the brief never says "release nothing by hand"
        ok(any("designer_stage.py open" in b and "stage5-program" in b and "release nothing by hand" not in b
               for b in w.briefs),
           "wait 1: the chain brief claims stage 5 before its one look and closes the claim by stage5-program")
        # RIMMANDRAKE_CLAIM_FIXED_GAPS_BEFORE_FINAL_LOOK_JUDGE_AGREED: Pyrelands round 11, the judge found all three
        # fixed gaps answered, but no coverage_fixes.json claim named them, so delta_merge carried them open and the final
        # look read not_covered; and a claim after a stop closes with no result (stage5-program would return it to 3)
        ok(any("coverage_fixes.json" in b and "--tokens 0" in b for b in w.briefs),
           "wait 1: the chain brief files the fix claims before the look and closes a stopped claim with no result")
        ds2 =dict(ds, history=ds["history"] + [{"at": "2026-11-15T15:00:00Z", "what": "coverage_release"}])
        fresh_state()
        w = World({"P": offline("P", "build", refused=["b1"])}, dstate={"P": ds2})
        rd, g = run(w, ["P"], root)
        ok(not any("RETAKE" in x[1] for x in w.launched), "wait 1: a look after the change: no second chain")
        # (2) a Designer concept with no record is discovered and seeded; a fixture marker keeps one out
        fresh_state()
        os.makedirs(os.path.join(root, "design", "concepts", "Gr"))
        open(os.path.join(root, "design", "concepts", "Gr", "stage.json"), "w").write("{}")
        os.makedirs(os.path.join(root, "design", "concepts", "_fixture"))
        open(os.path.join(root, "design", "concepts", "_fixture", "stage.json"), "w").write("{}")
        open(os.path.join(root, "design", "concepts", "_fixture", ".maturation-exclude"), "w").write("test fixture\n")
        try:
            import maturation_autonomy as AUT
            found = AUT.discovered(root)
        except ImportError as e:
            found = "ImportError: %s" % e
        ok(found == ["Gr"], "wait 2: discovery sees a Designer concept and skips one carrying .maturation-exclude "
           "(read %s)" % found)
        w = World({"Gr": {"mod": "Gr", "stage": "designer", "version": "0.1.0", "live_units": []}},
                  dstate={"Gr": {"status": "waiting_owner", "stage": 5, "history": [{"why": "parked"}],
                                 "pending_decision": "fix gaps"}}, found=found)
        rd, g = run(w, [], root)
        ok(w.seeded == ["Gr"] and "Gr" in rd["mods"], "wait 2: the tick seeds the concept's record and decides on it")
        ok(g("Gr").get("klass") == "owner" and len(w.cards) == 1 and "Gr" in w.cards[0],
           "a Designer turn waiting on him: OWNER, its card text written to the Conductor log")
        rd, g = run(w, [], root, now=CLOCK + 60)
        ok(len(w.cards) == 1, "the owner card is written once, not every tick")
        w = World({}, found=["Unseedable"])
        rd, g = run(w, [], root, now=CLOCK + 120)
        ok(g("Unseedable").get("klass") == "paused", "a concept whose record cannot be seeded: PAUSED, not a crash")
        # his walk: OWNER
        fresh_state()
        w = World({"H": {"mod": "H", "stage": "his_walk", "version": "0.1.0", "live_units": []}})
        rd, g = run(w, ["H"], root)
        ok(g("H").get("klass") == "owner" and not w.launched, "his walk: OWNER, nothing launched")
        # a passed version rests (Evidence-for-Ask): no card to him; opening the next version is an ordering call
        fresh_state()
        w = World({"P": {"mod": "P", "stage": "passed", "version": "0.1.0", "live_units": []}})
        rd, g = run(w, ["P"], root)
        ok(g("P").get("klass") == "rested" and not w.launched and not w.cards
           and not any(x.startswith("P:") for x in (rd.get("owner") or []) + (rd.get("paused") or [])),
           "a passed version: RESTED, no owner card, no pause alarm, nothing launched")
        # an unreadable designer state: PAUSED
        w = World({"U": {"mod": "U", "stage": "designer", "version": "0.1.0", "live_units": []}}, dstate={})
        rd, g = run(w, ["U"], root)
        ok(g("U").get("klass") == "paused", "an unreadable stage.json: PAUSED, not a crash")
        # exit met: a steward confirmation run, not a hand step
        fresh_state()
        w = World({"A": ingame("A", "exit met", why=["all rows PASS"])})
        rd, g = run(w, ["A"], root)
        ok(any("CONFIRM_A_VISIT_ONE_EXIT_MET" in x[1] for x in w.launched), "an exit met: a steward reads and confirms")
        # a failed steward launch is void_system (RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT; this read "PAUSED,
        # never retried", which spent the steward's one run on a system fault): relaunched, the faults counted apart,
        # and at the third a system_fault stop with no fourth try
        fresh_state()
        w = World({"A": offline("A", "hand step", hand=["walk_bars_confirmed"])})
        w.fail_launch = True
        for i in range(4):
            rd, g = run(w, ["A"], root, now=CLOCK + 60 * i)
        sa = json.load(open(os.path.join(os.environ["RM_MATURATION_DISPATCH_DIR"], "state.json")))["mods"]["A"]
        # 2026-11-21 (form_fault): a never-started launch is a fault of form: repaired (here in place) and relaunched
        # each tick, never a steward run spent; a repair that did not hold counts once, so three repeats bring the
        # fault loop (and its own repair run)
        ok(g("A").get("decision") == "repairing" and len(w.launched) == 4
           and not any(x.get("unit") for x in (sa.get("steward") or {}).values()) and RV.faults(sa) == 3,
           "a failed steward launch: a fault of form, repaired and relaunched; each repair that did not hold counts "
           "once, no steward run spent (read %s, %d launches, faults %d)" % (
               g("A").get("decision"), len(w.launched), RV.faults(sa)))
        # full slots: wait
        fresh_state()
        f = offline("A", "ready to advance")
        f["live_units"] = []
        w = World({"A": f, "L1": dict(offline("L1", "build", ["x"]), live_units=["rm-u1"]),
                   "L2": dict(offline("L2", "build", ["y"]), live_units=["rm-u2"])})
        rd, g = run(w, ["L1", "L2", "A"], root)
        ok(g("A").get("klass") == "wait" and g("L1").get("waits_on") == "rm-u1",
           "two live runs fill the slots: the steward waits; a live mod waits on its named unit")
        # (6) a stall: a wait with nothing running for 10 minutes
        fresh_state()
        w = World({"D": {"mod": "D", "stage": "designer", "version": "0.1.0", "live_units": []}},
                  dstate={"D": {"status": "ready", "stage": 2, "history": []}})
        rd, g = run(w, ["D"], root)
        ok(not rd.get("stalled"), "a fresh Designer wait is not a stall yet")
        rd, g = run(w, ["D"], root, now=CLOCK + 660)
        ok(rd.get("stalled") == ["D"], "wait 6: nothing running on it for 10 minutes: maturation.stalled names it")
        w.dunits = {"D": "rm-role-designer-7"}
        rd, g = run(w, ["D"], root, now=CLOCK + 720)
        ok(not rd.get("stalled") and g("D").get("waits_on") == "rm-role-designer-7",
           "a live Designer role run on the concept: wait on that unit, not a stall")
        # stalled blind spot 1: the Designer run ends; the stall counts from its end, not from the first wait
        w.dunits = {}
        rd, g = run(w, ["D"], root, now=CLOCK + 780)
        ok(not rd.get("stalled") and g("D").get("for_min") == 0,
           "stalled 1: a Designer run that just ended restarts the clock (read for_min %s, stalled %s)" % (
               g("D").get("for_min"), rd.get("stalled")))
        rd, g = run(w, ["D"], root, now=CLOCK + 780 + 660)
        ok(rd.get("stalled") == ["D"], "stalled 1: 11 minutes with nothing running after the run ended: stalled")
        # stalled blind spot 2: the Designer chain daily cap is named, PAUSED, with its cure
        fresh_state()
        w = World({"G": {"mod": "G", "stage": "designer", "version": "0.1.0", "live_units": []}},
                  dstate={"G": {"status": "ready", "stage": 3, "history": []}})
        w.dchain = {"G": (8, 8)}
        rd, g = run(w, ["G"], root)
        ok(g("G").get("klass") == "paused" and "chain_max_per_day" in str(g("G").get("status"))
           and "run-now --role Designer --concept design/concepts/G" in str(g("G").get("status")),
           "stalled 2: a concept at the Designer's daily chain cap reads PAUSED naming the cap and the run-now cure "
           "(read %s)" % str(g("G").get("status"))[:120])
        w.dchain = {"G": (3, 8)}
        rd, g = run(w, ["G"], root, now=CLOCK + 60)
        ok(g("G").get("decision") == "designer_wait", "stalled 2: under the cap it is still a Designer wait")
        # stalled blind spot 3: a coverage stop pauses the mod on the judge stop, never slots_full or a launch
        fresh_state()
        stop = {"status": "blocked", "stage": 5, "blocked_on": "REFUSAL_NOTHING_COULD_EVER_PASS: judging stopped",
                "history": [{"at": "2026-11-15T13:54:40Z", "what": "locked_change"},
                            {"at": "2026-11-15T13:56:22Z", "what": "coverage_release"},
                            {"at": "2026-11-15T14:05:35Z", "what": "coverage_stop", "why": "round 6 not_covered"}]}
        w = World({"P": offline("P", "ready to advance"), "L1": dict(offline("L1", "build", ["x"]), live_units=["rm-u1"]),
                   "L2": dict(offline("L2", "build", ["y"]), live_units=["rm-u2"])}, dstate={"P": stop})
        rd, g = run(w, ["L1", "L2", "P"], root)
        ok(g("P").get("klass") == "paused" and g("P").get("decision") == "coverage_stop"
           and "coverage_judge.py release" in str(g("P").get("status")),
           "stalled 3: a coverage-stopped mod reads PAUSED on the judge stop, not slots_full (read %s)" % g("P").get(
               "decision"))
        need = " ".join(x for x in rd.get("needs_conductor") or [] if x.startswith("P:"))
        ok("ready to advance" not in need and "PAUSED, coverage judging stopped" in need,
           "stalled 3: its Needs Conductor line says the coverage pause, not ready to advance (read %s)" % need[:120])
        fresh_state()
        w = World({"P": offline("P", "build", refused=["b1"])}, dstate={"P": stop})
        rd, g = run(w, ["P"], root)
        ok(not w.launched and g("P").get("decision") == "coverage_stop",
           "stalled 3: a coverage-stopped mod is never launched on (read %s, launched %s)" % (
               g("P").get("decision"), w.launched))
        # every class is one of six (held: the owner's hold, mod_owner_hold.py), on every row of every tick above
        ok(all(m.get("klass") in ("launch", "wait", "paused", "owner", "rested", "held") for m in rd["mods"].values()),
           "every row has one of the six classes")
        # the ops_watch side: the alarm targets and the route exist
        rules = json.load(open(os.path.join(HERE, "..", "Utils", "ops_watch_rules.json")))
        names = {t.get("name"): t.get("key") for t in rules.get("targets") or []}
        ok(names.get("OPS_MATURATION_MOD_PAUSED") == "maturation.paused"
           and names.get("OPS_MATURATION_MOD_STALLED") == "maturation.stalled",
           "ops_watch_rules.json carries the two fixed alarms (paused, stalled)")
        routes = json.load(open(os.path.join(HERE, "alarm_routes.json")))
        rs = routes.get("routes", routes) if isinstance(routes, dict) else routes
        ok("maturation.stalled" in json.dumps(rs), "alarm_routes.json routes maturation.stalled")
        road_back_checks(root)
        paused_fix_checks(root)
        final_look_checks(root)
        repin_wait_checks(root)
        exam_gate_checks(root)
        worked_after_checks(root)
        rearrival_checks(root)
        designer_lock_checks(root)
        launch_retry_checks(root)
        live_steward_checks(root)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
