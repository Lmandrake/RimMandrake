#!/usr/bin/env python3
"""selftest_mod_model_pin.py: one mod's builder launches on a pinned model (mod_model.py, `pipe model`), the promises of
design/specs/2026-11-19-mod-model-pin/boundary.md, one test each of the same name. Item
RIMMANDRAKE_PIN_MOD_MODEL_FABLE_EVERY_STAGE_ROLES_OPUS. Written before the code and watched failing on the base commit.

No model run is launched: every launcher is a fake that records what it was given (the maturation launcher, the
autonomy launcher, the Dispatcher's role launcher, systemd-run), and the claude argv is built by the real argv builders
(detached_helper.launch_argv, role_launch.launch_argv) and read, never run. The control store is a temp file.

    python3 src/RimMandrake/rimflow/selftest_mod_model_pin.py      exit 0 when every check passes
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="selftest-mod-model-pin-")
os.environ["RM_CONTROL_DB"] = os.path.join(TMP, "control.db")     # never the live store
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
HOLDS = os.path.join(TMP, "mod_owner_hold.json")       # no live hold reaches these tests (Graffiti is held live)
with open(HOLDS, "w") as _f:
    json.dump({"holds": []}, _f)
os.environ["RM_OWNER_HOLD_FILE"] = HOLDS
import control as C                 # noqa: E402
import maturation as M              # noqa: E402
import maturation_autonomy as AUT   # noqa: E402
import maturation_dispatch as MD    # noqa: E402
import detached_helper as DH        # noqa: E402
import role_launch as RL            # noqa: E402

# The model variables are fixtures (design/specs/2026-11-22-run-spend-and-model-alias/boundary.md): Fable's names its
# id, Opus's and Sonnet's are unset, in the environment and in the settings file this process reads.
for _k in RL.MODEL_VARS.values():
    os.environ.pop(_k, None)
os.environ["ANTHROPIC_DEFAULT_FABLE_MODEL"] = "claude-fable-5-2"
RL.SETTINGS = os.path.join(TMP, "settings.json")
with open(RL.SETTINGS, "w") as _f:
    json.dump({"env": {}}, _f)

PIN, OTHER = "WreckedMachines", "Graffiti"
PINS_KEY = "_pins"      # mod_model.PINS_KEY, spelled here so the base commit runs these checks (and reads opus)
UNPINNED_CONCEPT = "SelftestUnpinned"     # an invented concept: the Designer fixture reads no real one
FABLE_ID = "claude-fable-5-2"
FAILS = []
BRIEF_SPEND_RX = re.compile(r"\$\s*\d|USD|budget|spend|cap_usd|cap_tokens|--cap-usd", re.I)


def check(ok, msg):
    print("%s  %s" % ("PASS" if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def fresh_store():
    p = os.environ["RM_CONTROL_DB"]
    for x in (p, p + "-wal", p + "-shm"):
        if os.path.exists(x):
            os.remove(x)
    C.init(p)
    return p


def opt(argv, name):
    return argv[argv.index(name) + 1] if name in argv else None


class Patch:
    """Swap module attributes for one block and put them back."""

    def __init__(self, *triples):
        self.t, self.was = triples, []

    def __enter__(self):
        for mod, name, val in self.t:
            self.was.append((mod, name, getattr(mod, name)))
            setattr(mod, name, val)
        return self

    def __exit__(self, *a):
        for mod, name, val in reversed(self.was):
            setattr(mod, name, val)
        return False


def shipped(**kw):
    return dict(MD.load_cfg(), advancing=[PIN, OTHER], max_live=4, **kw)


# ---------------------------------------------------------------- the Dispatch step, decide then execute, fakes only

def offline_facts():
    return {m: {"stage": "offline_build", "owed": "build", "refused_bars": ["B1", "B2"], "live_units": [],
                "stage_runs": {}, "run_tokens": {}} for m in (PIN, OTHER)}


def run_offline(pins):
    """decide + execute one offline build per mod; -> ({mod: (model, cap)}, rows)."""
    cfg = shipped(**({PINS_KEY: pins} if pins is not None else {}))
    st, now, got = {}, time.time(), {}
    rows, launches = MD.decide(cfg, st, offline_facts(), now, (True, "test account"), releases=([], 0))

    def fake_launch_mod(root, mod, cap, item, model="opus", seat="BENCH", **kw):
        got[mod] = (model, cap)
        return 0, "DETACHED rm-detached-fake-%s" % mod, "rm-detached-fake-%s" % mod
    fx = {"file": lambda item, title, why, **k: (True, "filed %s" % item), "publish": lambda item: (True, "ok"),
          "known": lambda: set()}
    with Patch((M, "launch_mod", fake_launch_mod), (M, "load", lambda root, mod: {"stage": "offline_build"}),
               (MD, "pilot_ledger", lambda root, mod: False)):
        MD.execute(TMP, cfg, st, rows, launches, now, fx)
    return got, rows, cfg


def t_pinned_offline_build_launches_on_the_pin():
    got, rows, cfg = run_offline({PIN: "fable"})
    check(got.get(PIN, (None,))[0] == "fable", "the pinned mod's offline build is given model fable: %r" % (got,))
    k = MD.launch_kind(cfg, {"mod": PIN, "stage": "offline_build"})
    check(k["model"] == "fable", "launch_kind prints fable for the pinned mod's offline build: %r" % k)
    fresh_store()
    fx = {"autonomy": False, "pins": lambda: {PIN: "fable"}, "facts": offline_facts, "account": lambda: (True, "t"),
          "releases": lambda: ([], 0), "code": lambda: "c0", "clone": lambda: (0, 0), "known": lambda: set(),
          "convergence": lambda root, rd: dict(rd, convergence={})}
    rd = MD.tick(TMP, shipped(), False, fx=fx, now=time.time(), page=False)
    lk = {m: (x or {}).get("launch") for m, x in (rd.get("mods") or {}).items()}
    check((lk.get(PIN) or {}).get("model") == "fable" and (lk.get(OTHER) or {}).get("model") == "opus",
          "the dry tick's table prints fable for %s and opus for %s: %r" % (PIN, OTHER, lk))
    rec = {"clone": TMP, "unit": "rm-detached-u", "seat": "BENCH", "item": "I", "model": "fable", "state": TMP, "budget_usd": 30.0,
           "out": os.path.join(TMP, "o"), "err": os.path.join(TMP, "e")}
    a = DH.launch_argv(rec, "MSG", "/usr/bin/claude")
    check(opt(a, "--model") == FABLE_ID, "the detached run's claude argv reads --model %s: %r" % (FABLE_ID, opt(a, "--model")))


def t_unpinned_mod_keeps_the_global_model():
    cfg0 = MD.load_cfg()
    got, rows, cfg = run_offline({PIN: "fable"})
    usd = RL.weighted_to_list_usd(cfg0["cap_tokens"])     # the launch's one dollar edge (--budget-usd)
    check(got.get(OTHER) == (cfg0["model"], usd),
          "the unpinned mod launches on the shipped model and cap %r: %r" % ((cfg0["model"], usd), got.get(OTHER)))
    got0, _, _ = run_offline({})
    check(got0.get(PIN) == (cfg0["model"], usd),
          "with no pin, the same mod launches on the shipped model and cap: %r" % (got0.get(PIN),))
    for aut, cap in (("steward", "steward_cap_tokens"), ("fixer", "fix_cap_tokens")):
        k = MD.launch_kind(cfg, {"mod": OTHER, "aut": aut, "fix_item": "X"})
        check(k["model"] == cfg0["steward_model"] and k["cap_tokens"] == cfg0[cap],
              "the unpinned mod's %s keeps %s at %s: %r" % (aut, cfg0["steward_model"], cfg0[cap], k))


def t_judges_and_live_driver_keep_their_models():
    cfg0 = MD.load_cfg()
    cfg = shipped(**{PINS_KEY: {PIN: "fable"}})
    for stage, model, cap in (("blind_challenge", cfg0["model"], cfg0["blind_cap_tokens"]),
                              ("in_game", cfg0["ingame_model"], cfg0["ingame_cap_tokens"])):
        got = {}

        def fake(root, mod, cap_, item, model="?", **kw):
            got.update(model=model, cap=cap_)
            return 0, "DETACHED u", "u"
        with Patch((M, "load", lambda root, mod: {"stage": stage}), (MD, "pilot_ledger", lambda root, mod: False)):
            MD.launch_stage(TMP, cfg, {}, PIN, cap, "ITEM", launch=fake)
        check(got.get("model") == model, "the pinned mod's %s launches on %s, not the pin: %r" % (stage, model, got))
        k = MD.launch_kind(cfg, {"mod": PIN, "stage": stage})
        check(k["model"] == model and k["cap_tokens"] == cap,
              "launch_kind: the pinned mod's %s keeps %s at its own cap %s: %r" % (stage, model, cap, k))


def t_every_builder_kind_launches_on_the_pin():
    cfg = shipped(**{PINS_KEY: {PIN: "fable"}})
    for r in ({"mod": PIN, "aut": "steward"}, {"mod": PIN, "aut": "fixer", "fix_item": "X"},
              {"mod": PIN, "holder_items": ["A"]}, {"mod": PIN, "cert_reds": ["t1"]}):
        k = MD.launch_kind(cfg, r)
        check(k["model"] == "fable", "launch_kind: the pinned mod's %s reads fable: %r" % (k.get("kind"), k))
    # the fixer's launch (maturation_autonomy._execute_one): the model the launcher is given
    seen = []

    def do_launch(item, brief, model, cap, seat, env=None):
        seen.append((model, cap, brief))
        return 0, "DETACHED u", "u"
    st = {"mods": {PIN: {}}}
    row = {"mod": PIN, "aut": "fixer", "fix_item": "RIMMANDRAKE_FIX_X", "cap": 20 * 250_000, "stage": "offline_build",
           "fix_for": "refused"}
    with Patch((MD, "pilot_ledger", lambda root, mod: False)):
        AUT._execute_one(TMP, cfg, st, row, time.time(), lambda *a, **k: (True, "filed"), do_launch, set())
    check(seen and seen[0][0] == "fable", "the pinned mod's fixer is launched on fable: %r" % ([s[:2] for s in seen],))
    # the builder on red deciders (cert_launch): the model the launcher is given
    seen2 = []

    def brief(item, text, model, cap, seat, env=None, **kw):
        seen2.append((model, cap))
        return 0, "DETACHED u", "u"
    row = {"mod": PIN, "cert_reds": ["t_one"], "known_red": {"t_one": "RIMMANDRAKE_RED_ONE"}, "cap": 30 * 250_000}
    MD.cert_launch(TMP, cfg, {"mods": {PIN: {}}}, row, time.time(),
                   {"launch_brief": brief, "pilot": lambda root, mod: False, "ended": lambda ids: set()}, set(),
                   lambda *a, **k: (True, "filed"))
    check(seen2 and seen2[0][0] == "fable", "the pinned mod's builder on red deciders is launched on fable: %r" % seen2)
    # the holder on its road-back items (road_back_holder): the model the launcher is given
    seen3 = []

    def hbrief(item, text, model, cap, seat, env=None, **kw):
        seen3.append((model, cap))
        return 0, "DETACHED u", "u"
    import modledger
    with Patch((M, "ledger_needs", lambda root, ids: {i: "offline" for i in ids}),
               (M, "game_takeable", lambda stage: False),
               (modledger, "resume_plan", lambda root, mod: {"action": "packet", "reconcile": False, "why": "-"}),
               (MD, "ledger_open", lambda *a, **k: {"brief": "B", "env": {}, "run": "r1", "packet": ""}),
               (MD, "ledger_after", lambda *a, **k: "ledger ok")):
        MD.road_back_holder(TMP, cfg, {"mods": {PIN: {}}}, PIN, "offline_build", [{"id": "RIMMANDRAKE_ROAD_A"}],
                            None, 30 * 250_000, time.time(), {"launch_brief": hbrief})
    check(seen3 and seen3[0][0] == "fable", "the pinned mod's holder is launched on fable: %r" % seen3)


def t_build_cap_scales_by_the_pin_price():
    cfg0 = MD.load_cfg()
    import mod_model as MM
    check(MM.PINS_KEY == PINS_KEY, "the tick's pins key is %r: %r" % (PINS_KEY, MM.PINS_KEY))
    x = MM.cap_scale("fable")
    check(x == 2, "Fable 5.2 over Opus 5.5 is exactly 2 on every price field: %r" % x)
    got, rows, cfg = run_offline({PIN: "fable"})
    usd = RL.weighted_to_list_usd(cfg0["cap_tokens"])     # the launch's one dollar edge (--budget-usd)
    check(got.get(PIN, (None, None))[1] == usd * 2,
          "the pinned mod's offline build cap is %s x 2: %r" % (usd, got.get(PIN)))
    for aut, key in (("steward", "steward_cap_tokens"), ("fixer", "fix_cap_tokens")):
        k = MD.launch_kind(cfg, {"mod": PIN, "aut": aut, "fix_item": "X"})
        check(k["cap_tokens"] == cfg0[key] * 2, "the pinned mod's %s cap is %s x 2: %r" % (aut, cfg0[key], k))
        row = dict({"mod": PIN, "aut": aut, "steward_key": "k", "fix_item": "X"})
        go, _ = AUT._gate(cfg, {}, row, 0, "0.1.0")
        check(go and row.get("cap") == cfg0[key] * 2, "the autonomy gate books the %s at %s x 2: %r" % (
            aut, cfg0[key], row.get("cap")))
    rec = {"clone": TMP, "unit": "rm-detached-u", "seat": "BENCH", "item": "I", "model": "fable", "state": TMP,
           "budget_usd": got[PIN][1], "out": os.path.join(TMP, "o"), "err": os.path.join(TMP, "e")}
    a = DH.launch_argv(rec, "MSG", "/usr/bin/claude")
    check(opt(a, "--cap-usd") == "%g" % (usd * 2) and "--max-budget-usd" not in a,
          "the scaled cap goes through spend_watchdog (--cap-usd %g), never --max-budget-usd" % (usd * 2))
    seen = []
    st = {"mods": {PIN: {}}}
    row = {"mod": PIN, "aut": "fixer", "fix_item": "RIMMANDRAKE_FIX_X", "cap": cfg0["fix_cap_tokens"] * 2,
           "stage": "offline_build", "fix_for": "refused"}
    with Patch((MD, "pilot_ledger", lambda root, mod: False)):
        AUT._execute_one(TMP, cfg, st, row, time.time(), lambda *a, **k: (True, "filed"),
                         lambda item, brief, model, cap, seat, env=None: seen.append(brief) or (0, "u", "u"), set())
    check(seen and not BRIEF_SPEND_RX.search(seen[0]), "the fixer's brief carries no cap or spend: %r" % (
        BRIEF_SPEND_RX.findall(seen[0]) if seen else "no brief"))


# ---------------------------------------------------------------- the store and `pipe model`

def t_a_pin_is_set_and_lifted_in_the_store():
    p = fresh_store()
    rc = C.main(["model", PIN, "fable", "--why", "selftest"])
    check(rc == C.OK and C.mod_models(p) == {PIN: "fable"}, "pipe model %s fable pins it at once: rc %r, %r" % (
        PIN, rc, C.mod_models(p)))
    acts = [x for x in C.log(50, p) if "model" in x]
    check(len(acts) == 1, "one act is written: %r" % acts)
    rc = C.main(["model", PIN, "default", "--why", "selftest"])
    check(rc == C.OK and C.mod_models(p) == {}, "pipe model %s default lifts it: rc %r, %r" % (PIN, rc, C.mod_models(p)))


def t_an_unknown_pin_is_refused_by_name():
    p = fresh_store()
    for bad in ("haiku", "opus", "fabel"):    # opus: a tier whose variable is unset (the fixture above)
        n0 = len(C.log(500, p))
        try:
            C.set_model(PIN, bad, "selftest", p=p)
            why = None
        except C.Refused as e:
            why = str(e)
        check(why is not None and bad in why and C.mod_models(p) == {} and len(C.log(500, p)) == n0,
              "pin %r is refused naming it and nothing is written: %r" % (bad, why))
    check(C.main(["model", PIN, "haiku", "--why", "selftest"]) == C.REFUSED, "pipe model ... haiku exits REFUSED")


def t_no_pin_reads_empty_not_unreadable():
    p = fresh_store()
    check(C.mod_models(p) == {}, "a store with no pin reads {}: %r" % C.mod_models(p))
    bad = os.path.join(TMP, "garbage.db")
    with open(bad, "wb") as f:
        f.write(b"this is not a sqlite file at all" * 64)
    try:
        r = C.mod_models(bad)
        got = "read %r" % (r,)
    except C.Unreadable as e:
        got = "Unreadable: %s" % e
    check(got.startswith("Unreadable"), "a store that cannot be read raises Unreadable, never {}: %s" % got)


# ---------------------------------------------------------------- the Designer: run-now, chain, sweep

def designer_fixture():
    import designer_stage as DS
    with open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8") as f:
        sch = json.load(f)
    row = next(r for r in sch["roles"] if isinstance(r, dict) and r.get("stage_machine") == "designer_stage")
    clone = os.path.join(TMP, "clone")
    row = dict(row, clone=clone)
    dirs = {}
    for m in (PIN, UNPINNED_CONCEPT):
        d = os.path.join(clone, "design", "concepts", m)
        if not os.path.isdir(d):
            DS.init(d, m, "SELFTEST_ITEM", cap=100000, reserve=10000)
        dirs[m] = d
    return {"roles": [row]}, row, dirs


def designer_launch(sch, row, req, now):
    """decide_roles + dispatcher.execute on one run-now request, the role launcher faked. -> the role it was given."""
    import dispatcher as D
    st = {"roles": {row["name"]: {"run_now": dict(req, at=now - 5)}}, "alarms": {}}
    acts = []
    robs = {"ops": lambda: None, "account": lambda: "acct", "unit_state": lambda u: "active",
            "result": lambda r: None, "off": lambda p: None}
    import designer_stage as DS
    croot = os.path.join(row["clone"], "design", "concepts")
    with Patch((DS, "concepts_root", lambda *a, **k: croot)):     # the orphan sweep sees the fixture's concepts only
        RL.decide_roles(sch, st, robs, now, lambda **kw: acts.append(kw), set(), None)
    la = [a for a in acts if a.get("do") == "role_launch"]
    seen = []

    def fake(r, unit, msg, root_, claude):
        seen.append((r, unit))
        return True, "ok", {}
    xroot = os.path.join(TMP, "exec")
    os.makedirs(xroot, exist_ok=True)
    fx = {"off": lambda p: None, "paused": lambda: None, "note": lambda i, t: (True, ""), "publish": lambda n: None,
          "role_launch": fake}
    D.execute(la, sch, st, xroot, True, now, fx)
    for a in la:
        RL.stage_abort(a["concept"], a["unit"])
    return seen[0] if seen else (None, None)


def designer_requests(sch, row, dirs, mod, now):
    """-> {path: request} for `mod`'s concept: a hand run-now, the harvest's chain, the orphan sweep."""
    import designer_stage as DS
    cfg = dict(RL.ROLE_DEFAULTS, **row)
    out = {"run-now": RL.run_now_request(sch, {"role": row["name"], "by": "BENCH", "why": "selftest",
                                               "concept": "design/concepts/%s" % mod}, now)}
    with Patch((RL, "owner_held", lambda *a: False)):
        rs = {}
        out["chain"] = RL.chain_ask(row["name"], rs, cfg, dirs[mod], 1, now, lambda **k: None, "rm-role-designer-0",
                                    row["ledger_item"], "run", "selftest chain", None)
        st = DS.load_state(dirs[mod])
        opened = dict(st, history=st["history"] + [{"at": "2026-11-19T16:00:00Z", "stage": 0, "what": "open",
                                                     "why": "run rm-role-designer-1, stage 0"}])
        rs = {}
        RL.chain_sweep(row["name"], rs, cfg, now, lambda **k: None, lambda: [(dirs[mod], opened, now - 3600)])
        out["sweep"] = rs.get("run_now")
    return out


def t_designer_run_now_chain_and_sweep_launch_on_the_pin():
    p = fresh_store()
    C.set_model(PIN, "fable", "selftest", p=p)
    sch, row, dirs = designer_fixture()
    now = time.time()
    for mod, model, budget in ((PIN, FABLE_ID, row["run_budget_usd"] * 2),
                               (UNPINNED_CONCEPT, row["model"], row["run_budget_usd"])):
        for path, req in designer_requests(sch, row, dirs, mod, now).items():
            if not req:
                check(False, "%s: the %s path asked no run (fixture)" % (mod, path))
                continue
            r, unit = designer_launch(sch, row, req, now)
            if r is None:
                check(False, "%s: the %s request launched nothing (fixture)" % (mod, path))
                continue
            a = RL.launch_argv(r, unit, "MSG", os.path.join(TMP, "o"), os.path.join(TMP, "e"), "/usr/bin/claude")
            tail = a[a.index("--") + 1:]
            check(opt(tail, "--model") == model and opt(tail, "--cap-usd") == "%g" % budget
                  and "--max-budget-usd" not in tail,
                  "%s, Designer %s: --model %s, run budget %g through spend_watchdog: got --model %r --cap-usd %r" % (
                      mod, path, model, budget, opt(tail, "--model"), opt(tail, "--cap-usd")))


def t_designer_launch_names_its_mod():
    p = fresh_store()
    sch, row, dirs = designer_fixture()
    now = time.time()
    req = RL.run_now_request(sch, {"role": row["name"], "by": "BENCH", "why": "selftest",
                                   "concept": "design/concepts/%s" % PIN}, now)
    r, unit = designer_launch(sch, row, req, now)
    C.switch("mod:%s" % PIN, True, "selftest: off before the launch", p=p)
    calls = []

    def runner(argv, **kw):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, "", "")
    ok, out, _ = RL.launch(r, unit + "-names", "MSG", os.path.join(TMP, "exec"), "/usr/bin/claude", runner=runner)
    check(not ok and "REFUSED by control" in out and not any("systemd-run" in str(c) for c in calls),
          "a Designer launch on %s is refused by `pipe off %s` (admitted under its mod): ok %r, %r" % (PIN, PIN, ok, out))
    C.switch("mod:%s" % PIN, False, "selftest", p=p)


# ---------------------------------------------------------------- could not look; could not price

def t_an_unreadable_pin_launches_nothing():
    fresh_store()

    def boom():
        raise C.Unreadable("selftest: the store is locked")

    def tick(pins):
        fx = {"autonomy": False, "pins": pins, "facts": offline_facts, "account": lambda: (True, "test"),
              "releases": lambda: ([], 0), "code": lambda: "c0", "clone": lambda: (0, 0), "known": lambda: set(),
              "convergence": lambda root, rd: dict(rd, convergence={})}
        rd = MD.tick(TMP, shipped(), False, fx=fx, now=time.time(), page=False)
        return {m: (x or {}).get("decision") for m, x in (rd.get("mods") or {}).items()}, rd.get("launched")
    go = ("launch", "would_launch")
    seen, launched = tick(lambda: {PIN: "fable"})
    check(seen.get(PIN) in go, "control: readable pins, the same dry tick would launch %s: %r" % (PIN, seen))
    seen, launched = tick(boom)
    check(not launched and seen and all(d not in go for d in seen.values()),
          "pins that cannot be read: the tick launches nothing: %r %r" % (seen, launched))
    sch, row, dirs = designer_fixture()
    good = os.environ["RM_CONTROL_DB"]
    bad = os.path.join(TMP, "garbage.db")
    with open(bad, "wb") as f:
        f.write(b"not a store" * 99)
    a = {"concept": dirs[PIN], "run_now": {"by": "BENCH", "why": "w"}, "why": "w"}
    os.environ["RM_CONTROL_DB"] = bad
    try:
        r = RL.launch_role(row, a)
        ok, out, _ = RL.launch(r, "rm-role-designer-unreadable", "MSG", os.path.join(TMP, "exec"), "/usr/bin/claude",
                               runner=lambda argv, **kw: subprocess.CompletedProcess(argv, 0, "", ""))
    finally:
        os.environ["RM_CONTROL_DB"] = good
    check(not ok and out.startswith("REFUSED by control") and PIN in out,
          "a Designer launch whose pin cannot be read is refused by control, naming it: %r" % out)


def t_a_pin_it_cannot_price_launches_nothing():
    cfg = shipped(**{PINS_KEY: {PIN: "haiku"}})
    rows, launches = MD.decide(cfg, {}, offline_facts(), time.time(), (True, "test"), releases=([], 0))
    r = next((x for x in rows if x["mod"] == PIN), {})
    check(r.get("decision") == "model_unknown" and "haiku" in str(r.get("why")) and PIN not in launches
          and OTHER in launches, "a pin it cannot price: model_unknown naming it, nothing launches on that mod: %r" % (
              (r.get("decision"), r.get("why"), launches),))
    sch, row, dirs = designer_fixture()
    out = RL.launch_role(row, {"concept": dirs[PIN], "run_now": {"by": "BENCH", "why": "w"}, "why": "w"})
    import mod_model as MM
    try:
        MM.role_for(row, PIN, {PIN: "haiku"})
        why = None
    except KeyError as e:
        why = str(e)
    check(why and "haiku" in why, "the Designer's route refuses an unpriceable pin by name: %r" % why)
    check(out.get("model") == row["model"], "an unpinned store leaves the Designer on its shipped model: %r" % out.get("model"))


def t_offline_build_ceiling_scales_by_the_pin_price():
    """The offline build's ceiling is the shipped stage_ceiling_tokens times the price ratio for a pinned mod, as its
    build caps are (every builder run of that stage runs on the pin, and a weighted token weighs its price). The blind
    challenge and in-game acceptance keep the shipped ceiling: their judge and live driver are never pinned. A
    Conductor's `pipe limit` on the mod stands as typed."""
    import mod_model as MM
    p = fresh_store()
    m = 1000000
    cfg = {"stage_ceiling_tokens": 100 * m, "cap_tokens": 15 * m, PINS_KEY: {PIN: "fable"}}
    for stage, want in (("offline_build", 200 * m), ("blind_challenge", 100 * m), ("in_game", 100 * m)):
        got = MD.stage_spend(cfg, PIN, stage, 0)[1]
        check(got == want, "a pinned mod's %s ceiling: %r (want %r)" % (stage, got, want))
        got = MD.stage_spend(MM.for_mod(cfg, PIN), PIN, stage, 0)[1]
        check(got == want, "the same through the mod's own settings (never scaled twice), %s: %r" % (stage, got))
    got = MD.stage_spend(cfg, OTHER, "offline_build", 0)[1]
    check(got == 100 * m, "an unpinned mod keeps the shipped offline-build ceiling: %r" % got)
    over, _rid = MD.ceiling_gate(MM.for_mod(cfg, PIN), {}, PIN, "offline_build", 150 * m, 30 * m, "the offline build",
                                 ([], 0))
    check(over is None, "the gate admits a pinned build run under the scaled ceiling (150M spent + 30M cap): %r" % over)
    over, _rid = MD.ceiling_gate(cfg, {}, OTHER, "offline_build", 150 * m, 15 * m, "the offline build", ([], 0))
    check(bool(over), "the gate still stops an unpinned mod past the shipped ceiling: %r" % over)
    C.set_limit(PIN, "spend_offline_build", 120 * m, "selftest", p=p)
    got = MD.stage_spend(cfg, PIN, "offline_build", 0)[1]
    check(got == 120 * m, "a Conductor's limit on the pinned mod stands as typed: %r" % got)

def t_designer_task_budget_scales_by_the_pin_price():
    """A pinned mod's Designer task budget, the budget of each of its runs and the judge-and-rework loop's park
    ceiling are the shipped ones times the price ratio, read from the store at each use (a pin set or lifted later
    moves them); an unpinned concept, or a store that cannot be read, keeps the shipped ones."""
    import designer_stage as DS
    p = fresh_store()
    cap = DS.DEFAULT_CAP

    def state(mod):
        return {"mod": mod, "item": "X", "stage": 4, "results": [], "history": [],
                "coverage_rounds": [{"judge": "rm-coverage-judge-1", "at": "2026-11-20T00:00:00Z"}],
                "budget": {"cap": cap, "reserve": DS.DEFAULT_RESERVE, "spent": 5 * cap // 4,
                           "charges": [{"kind": "review", "ref": "rm-coverage-judge-1", "at": "2026-11-20T00:00:01Z",
                                        "tokens": 9 * cap // 4}]}}
    C.set_model(PIN, "fable", "selftest", p=p)
    st = state(PIN)
    check(DS.task_cap(st) == 2 * cap, "a pinned concept's task budget: %r (want %r)" % (DS.task_cap(st), 2 * cap))
    check(DS.remaining(st) == 2 * cap - 5 * cap // 4, "a pinned concept's budget left: %r" % DS.remaining(st))
    fresh = dict(st, budget=dict(st["budget"], spent=0))
    b, over = DS.run_budget(fresh, 4000000)
    check((b, over) == (2 * cap - DS.DEFAULT_RESERVE, False),
          "a pinned concept's run budget passes the shipped run cap (4M), up to its scaled task budget: %r" % ((b, over),))
    b, over = DS.run_budget(st, 4000000)
    check((b, over) == (2 * cap - 5 * cap // 4 - DS.DEFAULT_RESERVE, False),
          "a pinned concept's run budget is at most what its scaled task budget has left: %r" % ((b, over),))
    check(DS.loop_ceiling(st) is None and DS.ceiling_crossed_at(st) is None,
          "a pinned loop at 2.25x the shipped cap is under its scaled park ceiling: %r" % DS.loop_ceiling(st))
    un = state(UNPINNED_CONCEPT)
    check(DS.task_cap(un) == cap and DS.remaining(un) == cap - 5 * cap // 4, "an unpinned concept keeps the shipped budget")
    b, over = DS.run_budget(un, 4000000)
    check(over is True and b == min(cap - DS.DEFAULT_RESERVE, 4000000),
          "an unpinned concept over its budget goes on, advisory, with the shipped run cap: %r" % ((b, over),))
    check(bool(DS.loop_ceiling(un)), "an unpinned loop at 2.25x its cap is past its park ceiling: %r" % DS.loop_ceiling(un))
    C.set_model(PIN, "default", "selftest", p=p)
    check(DS.task_cap(st) == cap and bool(DS.loop_ceiling(st)), "a lifted pin gives the shipped budget back at once")
    C.set_model(PIN, "fable", "selftest", p=p)
    good = os.environ["RM_CONTROL_DB"]
    bad = os.path.join(TMP, "garbage-ds.db")
    with open(bad, "w") as f:
        f.write("not a database")
    os.environ["RM_CONTROL_DB"] = bad
    try:
        check(DS.task_cap(st) == cap, "a store that cannot be read keeps the shipped budget, the stricter one: %r"
              % DS.task_cap(st))
    finally:
        os.environ["RM_CONTROL_DB"] = good


def main():
    tests = (t_a_pin_is_set_and_lifted_in_the_store, t_an_unknown_pin_is_refused_by_name, t_no_pin_reads_empty_not_unreadable,
             t_pinned_offline_build_launches_on_the_pin, t_unpinned_mod_keeps_the_global_model,
             t_judges_and_live_driver_keep_their_models, t_every_builder_kind_launches_on_the_pin,
             t_build_cap_scales_by_the_pin_price, t_designer_run_now_chain_and_sweep_launch_on_the_pin,
             t_designer_launch_names_its_mod, t_an_unreadable_pin_launches_nothing, t_a_pin_it_cannot_price_launches_nothing,
             t_offline_build_ceiling_scales_by_the_pin_price, t_designer_task_budget_scales_by_the_pin_price)
    try:
        for t in tests:
            try:
                t()
            except Exception as e:  # noqa: BLE001  a crash is a failure, named
                import traceback
                traceback.print_exc()
                check(False, "%s crashed: %s: %s" % (t.__name__, type(e).__name__, e))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("%d tests, %d failed check(s)" % (len(tests), len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
