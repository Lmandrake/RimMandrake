#!/usr/bin/env python3
"""selftest_companion_grant.py - the companion test-profile grant: its reader, the ops_watch early warning and the
`rimflow next` preflight (item COMPANION_GRANT_WIRE_LAPSES_AT_BEDTIME). Temp files only: it never reads or writes
the real grant, the ledger or D:\\ClaudeWork."""
import io, json, os, shutil, subprocess, sys, tempfile, time, types
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
from rimflow import companion_grant as cg  # noqa: E402
from rimflow import cli  # noqa: E402
import ops_watch as OW  # noqa: E402

FAILED = []


def ok(name, got, want):
    if got != want:
        FAILED.append(name)
        print("FAIL %s: got %r want %r" % (name, got, want))
    else:
        print("ok   %s" % name)


NOW = time.time()
ISO = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))
CONF = cg.load_conf()

# ---------------------------------------------------------------- config: every setting carries its _why
ok("config holds no expiry setting", "hold_within_min" in CONF, False)
for k in ("profile_file", "test_profiles", "hold_needs"):
    ok("config has " + k, k in CONF, True)
    ok("config %s has a _why" % k, bool(CONF.get("_%s_why" % k)), True)
ok("config has a _why", bool(CONF.get("_why")), True)
ok("the hold needs are game needs the dispatcher knows", set(CONF["hold_needs"]) <= set(cli.HOLD_GAME_NEEDS), True)

# ---------------------------------------------------------------- the reader
D = tempfile.mkdtemp()
JB = os.path.join(D, "JawaBench")
os.makedirs(JB)
P = os.path.join(JB, "companion_profile.json")


def put(body):
    with open(P, "w") as f:
        f.write(body if isinstance(body, str) else json.dumps(body))


def rd(path=P):
    return cg.read(path=path, conf=CONF)


put({"profile": "test", "expiresUtc": ISO(NOW + 75 * 3600), "campaignSaves": ["x"]})
g = rd()
ok("test profile -> OK", g["state"], "OK")
ok("reading names its file and profile", (g["file"], g["profile"]), (P, "test"))
ok("reading carries no expiry", ("hours_left" in g, "expires" in g), (False, False))
put({"profile": "gm", "expiresUtc": ISO(NOW + 75 * 3600)})
ok("gm is test's alias -> OK", rd()["state"], "OK")
# the companion ignores expiresUtc since f3c90ff50c: an old, absent or malformed one never lapses a test grant
for label, body in (("expired", {"profile": "test", "expiresUtc": ISO(NOW - 3600)}),
                    ("years past", {"profile": "test", "expiresUtc": "2020-01-01T00:00:00Z"}),
                    ("no expiresUtc", {"profile": "test"}),
                    ("unparseable expiresUtc", {"profile": "test", "expiresUtc": "Tuesday"}),
                    ("null expiresUtc", {"profile": "test", "expiresUtc": None})):
    put(body)
    ok("%s expiresUtc on a test profile -> OK" % label, rd()["state"], "OK")
for label, body in (("torn json", "{torn"), ("not an object", "[1]"), ("campaign profile", {"profile": "campaign",
                     "expiresUtc": ISO(NOW + 75 * 3600)}), ("no profile", {"expiresUtc": ISO(NOW + 75 * 3600)})):
    put(body)
    g = rd()
    ok("%s -> LAPSED (the companion reads it as campaign)" % label, g["state"], "LAPSED")
    ok("%s says why" % label, bool(g["why"]), True)
os.remove(P)
ok("absent file in a visible folder -> LAPSED", rd()["state"], "LAPSED")
g = rd(path=os.path.join(D, "nope", "companion_profile.json"))
ok("folder not visible -> UNMEASURED (blind, not lapsed)", g["state"], "UNMEASURED")

# ---------------------------------------------------------------- the preflight `rimflow next` applies
for st, held in (("OK", False), ("LAPSED", True), ("UNMEASURED", True)):
    ctx = {}
    with redirect_stdout(io.StringIO()) as o:
        cli._apply_grant_preflight(ctx, reader=lambda st=st: {"state": st, "why": "w", "file": P})
    ok("preflight %s -> hold %s" % (st, held), bool(ctx.get("hold_grant")), held)
    ok("preflight %s loud line only when held" % st, ("companion grant" in o.getvalue()), held)
    if held:
        line = o.getvalue().strip().splitlines()[0]
        ok("the loud line cannot parse as an item line", line.startswith("("), True)


def boom():
    raise RuntimeError("reader broke")


ctx = {}
with redirect_stdout(io.StringIO()):
    cli._apply_grant_preflight(ctx, reader=boom)
ok("a reader that raises holds (fail closed)", bool(ctx.get("hold_grant")), True)
# review #3: a config that cannot load still holds, but only the grant's needs: offline work stays offered
_cp = cg.CONF_PATH
cg.CONF_PATH = os.path.join(D, "no_such_companion_grant.json")
cg.load_conf.__defaults__ = (cg.CONF_PATH,)
try:
    cctx = {}
    with redirect_stdout(io.StringIO()):
        cli._apply_grant_preflight(cctx)
finally:
    cg.CONF_PATH = _cp
    cg.load_conf.__defaults__ = (_cp,)
ok("config load failure -> hold", bool(cctx.get("hold_grant")), True)
from rimflow import priority as _prio
ok("KNOWN_NEEDS mirrors priority.BY_GAME", sorted(cg.KNOWN_NEEDS), sorted(_prio.BY_GAME))
# review2 #2: a READABLE config with a malformed hold_needs fails closed (load_conf refuses it), never filters nothing
BADC = os.path.join(D, "bad_conf.json")
for label, bad in (("a string", "bridge"), ("an empty list", []), ("an unknown need", ["bridge", "brige"]),
                   ("a non-string entry", ["bridge", 3]),
                   ("bridge alone (game-up leaks past a lapsed grant)", ["bridge"]), ("offline held", ["offline", "bridge", "game-up"])):
    json.dump(dict(CONF, hold_needs=bad), open(BADC, "w"))
    try:
        cg.load_conf(BADC)
        refused = False
    except ValueError:
        refused = True
    ok("load_conf refuses hold_needs as %s" % label, refused, True)
json.dump(dict(CONF, hold_needs="bridge"), open(BADC, "w"))
cg.load_conf.__defaults__ = (BADC,)
try:
    sctx = {}
    with redirect_stdout(io.StringIO()):
        cli._apply_grant_preflight(sctx, reader=lambda: {"state": "OK", "why": "w"})
finally:
    cg.load_conf.__defaults__ = (_cp,)
ok("malformed hold_needs + an OK grant still holds (fail closed)", bool(sctx.get("hold_grant")), True)
ok("malformed hold_needs -> default needs", tuple(sctx.get("hold_grant_needs") or ()), ("bridge", "game-up"))
ok("config load failure -> only bridge/game-up withheld", tuple(cctx.get("hold_grant_needs") or ()),
   ("bridge", "game-up"))


def next_e2e(profile):
    """GRANT_TEST_PROVE_NEXT_REALLY_WITHHOLDS: run the real `rimflow next` (cmd_next, lease and all) as a subprocess
    on a throwaway ledger holding one bridge, one game-up and one offline item, with the game stamped UP and the
    bridge free so only the grant can withhold the live two. -> its stdout."""
    t = tempfile.mkdtemp(prefix="rf_grant_next_")
    try:
        os.makedirs(os.path.join(t, "items"))
        prof = os.path.join(t, "companion_profile.json")
        with open(prof, "w") as f:
            json.dump({"profile": profile, "expiresUtc": "2020-01-01T00:00:00Z"}, f)
        with open(os.path.join(t, "schedule.json"), "w") as f:
            f.write("{}")
        env = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID",
                                                                "RM_PRIORITY_LIST")}
        env.update(RIMFLOW_LEDGER=os.path.join(t, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(t, "items"),
                   RIMFLOW_PROBE="no-reading",
                   RIMFLOW_DISPATCH_LOCK=os.path.join(t, "dispatch.lock"), RIMFLOW_SCHEDULE=os.path.join(t, "schedule.json"),
                   RIMFLOW_SEAT="BENCH", RM_COMPANION_PROFILE=prof)

        def rf(*a, seat="BENCH"):
            r = subprocess.run([sys.executable, os.path.join(HERE, "cli.py")] + list(a), env=dict(env, RIMFLOW_SEAT=seat),
                               capture_output=True, text=True, timeout=120)
            if r.returncode:
                raise RuntimeError("rimflow %s exited %d: %s" % (" ".join(a), r.returncode, (r.stderr or r.stdout)[-300:]))
            return r.stdout
        for iid, needs in E2E:
            rf("file", iid, "--for", "BENCH", "--title", "grant e2e " + needs, "--needs", needs, "--target", "v1",
               "--why", "selftest fixture")
        rf("game", "UP", seat="OWNER")
        return rf("next")
    finally:
        shutil.rmtree(t, ignore_errors=True)


E2E = (("GRANT_PROBE_BRIDGE_WORK_HELD", "bridge"), ("GRANT_PROBE_GAMEUP_WORK_HELD", "game-up"),
       ("GRANT_PROBE_OFFLINE_WORK_OFFERED", "offline"))
offer = lambda out: [ln.split()[3] for ln in out.splitlines() if ln.startswith("-> rimflow claim ")]
live_named = lambda out: [i for i, n in E2E[:2] if i in out]
o = next_e2e("test")
ok("cmd_next end-to-end control: a test grant with an old expiresUtc offers the bridge item", offer(o), ["GRANT_PROBE_BRIDGE_WORK_HELD"])
ok("cmd_next end-to-end control: no grant hold printed", "companion grant" in o, False)
o = next_e2e("campaign")
ok("cmd_next end-to-end: campaign grant prints the hold", "(companion grant LAPSED: items needing bridge/game-up are "
   "withheld" in o, True)
ok("cmd_next end-to-end: campaign grant withholds the bridge/game-up items", live_named(o), [])
ok("cmd_next end-to-end: campaign grant still offers the offline item", offer(o), ["GRANT_PROBE_OFFLINE_WORK_OFFERED"])

A = lambda needs: types.SimpleNamespace(item=types.SimpleNamespace(id="X_" + needs, needs=needs, raised=None),
                                        kind="build")
C = lambda needs: types.SimpleNamespace(id="C_" + needs, needs=needs, raised=None)
saved = (cli.priority.rank, cli.reconcile.guard, cli._claimable, cli.reconcile.assess)
try:
    cli.priority.rank = lambda *a, **k: [A("bridge"), A("game-up"), A("deploy"), A("offline")]
    cli.reconcile.guard = lambda offers, idx: (offers, [])
    cli._claimable = lambda *a, **k: [C("game-up"), C("offline")]
    cli.reconcile.assess = lambda it, idx: types.SimpleNamespace(kind="build", item=it)
    args = types.SimpleNamespace(target=None)
    ok("no hold: the bridge item comes first (control)", cli._choose(None, "FOUNDRY", args, {}, None)["item"].id,
       "X_bridge")
    hctx = {"hold_grant": "LAPSED", "hold_grant_needs": tuple(CONF["hold_needs"])}
    ok("grant held: bridge and game-up skipped, deploy still offered",
       cli._choose(None, "FOUNDRY", args, hctx, None)["item"].id, "X_deploy")
    cli.priority.rank = lambda *a, **k: [A("bridge")]
    h = cli._choose(None, "FOUNDRY", args, hctx, None)
    ok("grant held: claimable drops game-up", (h["kind"], [c.id for c in h["claimable"]]), ("claimable", ["C_offline"]))
    cli.priority.rank = lambda *a, **k: [A("bridge"), A("game-up"), A("deploy"), A("harvest"), A("offline")]
    ok("config-failure hold: deploy still offered", cli._choose(None, "FOUNDRY", args, cctx, None)["item"].id,
       "X_deploy")
    ok("malformed hold_needs hold: bridge/game-up withheld, deploy offered",
       cli._choose(None, "FOUNDRY", args, sctx, None)["item"].id, "X_deploy")
    ok("a hold with no needs recorded withholds only bridge/game-up",
       cli._choose(None, "FOUNDRY", args, {"hold_grant": "x"}, None)["item"].id, "X_deploy")
    cli.priority.rank = lambda *a, **k: [A("bridge")]
    cli._claimable = lambda *a, **k: [C("bridge")]
    ok("grant held and only grant work: nothing", cli._choose(None, "FOUNDRY", args, hctx, None)["kind"], "nothing")
finally:
    cli.priority.rank, cli.reconcile.guard, cli._claimable, cli.reconcile.assess = saved

# ---------------------------------------------------------------- the early warning (ops_watch)
ok("ops_watch has the companion family", ("companion" in OW.COLLECTORS, "companion" in OW.ORDER,
                                           "companion" in OW.FAMILIES), (True, True, True))
KEY = "companion.grant_test"
ok("the blind digest may show it", KEY in OW.BLIND_KEYS, True)
ok("no expiry series is left", any("grant_hours_left" in t.get("key", "") for t in OW.load_rules()["targets"]), False)
os.environ["RM_COMPANION_PROFILE"] = P
try:
    put({"profile": "test", "expiresUtc": "2020-01-01T00:00:00Z"})
    pts = OW.c_companion(NOW, OW.load_rules(), {})
    ok("collector: a test grant with an old expiresUtc is MEASURED 1", (pts[KEY]["m"], pts[KEY]["v"]), ("MEASURED", 1))
    ok("collector: says state and profile", (pts[KEY]["x"]["state"], pts[KEY]["x"]["profile"]), ("OK", "test"))
    os.remove(P)
    pts = OW.c_companion(NOW, OW.load_rules(), {})
    ok("collector: an absent grant is MEASURED 0", (pts[KEY]["m"], pts[KEY]["v"]), ("MEASURED", 0))
    os.environ["RM_COMPANION_PROFILE"] = os.path.join(D, "nope", "companion_profile.json")
    ok("collector: blind folder -> UNMEASURED", OW.c_companion(NOW, OW.load_rules(), {})[KEY]["m"], "UNMEASURED")
finally:
    os.environ.pop("RM_COMPANION_PROFILE", None)

R = OW.load_rules()
tg = [t for t in R["targets"] if t.get("key") == KEY and t.get("alarm")]
ok("one alarm target on the grant", len(tg), 1)
if tg:
    t = tg[0]
    ok("the target carries a why and a name", (bool(t.get("why")), bool(t.get("name"))), (True, True))
    ok("the name passes the mint rules", not cli.model.mint_problems(t["name"] + "_AB12", set()), True)
    aid = "%s:%s" % (t["tag"], KEY)
    st = lambda v, m="MEASURED": OW.target_state({KEY: {"v": v, "m": m}}, R).get(aid)
    ok("alarm: 0 (not a test profile) crosses", st(0), True)
    ok("alarm: 1 (a test profile) is clear", st(1), False)
    ok("alarm: UNMEASURED holds (no file, no clear)", st(None, "UNMEASURED"), None)

# collector -> alarm, end to end through run_alarms: healthy, then campaign, then folder blind, then fixed
ut = [t for t in R["targets"] if t.get("key") == "companion.grant_visible" and t.get("alarm")]
ok("one alarm target on grant visibility", len(ut), 1)
OPS = tempfile.mkdtemp()
os.environ["RM_OPS_WATCH_DIR"] = OPS
filed = []
_mint = OW.mint_name
OW.mint_name = lambda tag, known, prefix: "%s_%s" % (prefix, "AB%02d" % len(filed))


def filer(todo, conf):
    filed.extend(dict(a) for a in todo)
    return {a["name"]: None for a in todo}


def ow_pass(t, path):
    os.environ["RM_COMPANION_PROFILE"] = path
    pts = OW.c_companion(t, R, {})
    return pts, OW.run_alarms(pts, R, t, set(), filer)


try:
    put({"profile": "test", "expiresUtc": "2020-01-01T00:00:00Z"})
    pts, st = ow_pass(NOW, P)
    ok("e2e healthy (test, old expiresUtc): visible, nothing filed", (pts["companion.grant_visible"]["v"], filed), (1, []))
    put({"profile": "campaign"})
    pts, st = ow_pass(NOW + 900, P)
    ok("e2e campaign: GRANT_NOT_TEST filed once", [a["name"].rsplit("_", 2)[0] for a in filed], ["OPS_GRANT_ASK"])
    BLIND = os.path.join(D, "gone", "JawaBench", "companion_profile.json")
    pts, st = ow_pass(NOW + 1800, BLIND)
    ok("e2e folder gone: test UNMEASURED, visible MEASURED 0",
       (pts[KEY]["m"], pts["companion.grant_visible"]["m"], pts["companion.grant_visible"]["v"]), ("UNMEASURED", "MEASURED", 0))
    ok("e2e folder gone: GRANT_UNSEEN filed (fail closed, not silent)",
       [a["name"].rsplit("_", 2)[0] for a in filed if not a.get("note_only")], ["OPS_GRANT_ASK", "OPS_GRANT_PROBE"])
    put({"profile": "test"})   # fixed
    for i in range(int(R["alarm"]["clear_passes"])):
        pts, st = ow_pass(NOW + 3600 + i * 900, P)
    ok("e2e fixed: both alarms clear after clear_passes", sorted(k for k in st if k.startswith("GRANT_")), [])
    ok("e2e fixed: nothing new filed, only clear notes",
       [a["name"].rsplit("_", 2)[0] for a in filed if not a.get("note_only")], ["OPS_GRANT_ASK", "OPS_GRANT_PROBE"])
    def boom2(*a, **k):
        raise RuntimeError("reader broke")
    mods = [m for m in (cg, sys.modules.get("companion_grant")) if m]   # ops_watch imports it top-level
    saved_r = [m.read for m in mods]
    for m in mods:
        m.read = boom2
    try:
        pts = OW.c_companion(NOW, R, {})
    finally:
        for m, r in zip(mods, saved_r):
            m.read = r
    ok("collector: a reader that raises is visible 0 (alarms)", (pts["companion.grant_visible"]["m"],
       pts["companion.grant_visible"]["v"]), ("MEASURED", 0))
    # a readable but malformed config: the collector fails closed (visible 0 -> GRANT_UNSEEN)
    os.environ["RM_COMPANION_PROFILE"] = P
    json.dump(dict(CONF, hold_needs="bridge"), open(BADC, "w"))
    mods = [m for m in (cg, sys.modules.get("companion_grant")) if m]
    saved_d = [m.load_conf.__defaults__ for m in mods]
    for m in mods:
        m.load_conf.__defaults__ = (BADC,)
    try:
        pts = OW.c_companion(NOW, R, {})
    finally:
        for m, dd in zip(mods, saved_d):
            m.load_conf.__defaults__ = dd
    ok("collector: a malformed config alarms GRANT_UNSEEN", OW.target_state(pts, R).get("GRANT_UNSEEN:companion.grant_visible"),
       True)
finally:
    OW.mint_name = _mint
    os.environ.pop("RM_OPS_WATCH_DIR", None)
    os.environ.pop("RM_COMPANION_PROFILE", None)

print("\n%s: %d failed" % ("FAIL" if FAILED else "PASS", len(FAILED)))
sys.exit(1 if FAILED else 0)
