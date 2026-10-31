#!/usr/bin/env python3
"""selftest_companion_grant.py - the companion test-profile grant: its reader, the ops_watch early warning and the
`rimflow next` preflight (item COMPANION_GRANT_WIRE_LAPSES_AT_BEDTIME). Temp files only: it never reads or writes
the real grant, the ledger or D:\\ClaudeWork."""
import inspect, io, json, os, sys, tempfile, time, types
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
for k in ("profile_file", "test_profiles", "hold_within_min", "hold_needs"):
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


def rd(now=NOW, path=P):
    return cg.read(path=path, now=now, conf=CONF)


put({"profile": "test", "expiresUtc": ISO(NOW + 75 * 3600), "campaignSaves": ["x"]})
g = rd()
ok("75 h left -> OK", g["state"], "OK")
ok("hours_left measured", round(g["hours_left"]), 75)
ok("reading names its file and expiry", (g["file"], g["expires"]), (P, ISO(NOW + 75 * 3600)))
put({"profile": "gm", "expiresUtc": ISO(NOW + 75 * 3600)})
ok("gm is test's alias -> OK", rd()["state"], "OK")
hw = CONF["hold_within_min"] * 60
put({"profile": "test", "expiresUtc": ISO(NOW + hw - 60)})
ok("inside hold_within_min -> LAPSING", rd()["state"], "LAPSING")
put({"profile": "test", "expiresUtc": ISO(NOW + hw + 120)})
ok("just outside hold_within_min -> OK", rd()["state"], "OK")
put({"profile": "test", "expiresUtc": ISO(NOW - 3600)})
g = rd()
ok("expired -> LAPSED", g["state"], "LAPSED")
ok("expired hours_left is negative", g["hours_left"] < 0, True)
put({"profile": "test", "expiresUtc": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(NOW + 75 * 3600))})
ok("a naive expiresUtc is UTC", round(rd()["hours_left"]), 75)
for label, body in (("torn json", "{torn"), ("not an object", "[1]"), ("campaign profile", {"profile": "campaign",
                     "expiresUtc": ISO(NOW + 75 * 3600)}), ("no expiresUtc", {"profile": "test"}),
                    ("unparseable expiresUtc", {"profile": "test", "expiresUtc": "Tuesday"}),
                    # review #2: fromisoformat (3.11+) takes compact and date-only forms; none is a valid grant
                    ("numeric expiresUtc", {"profile": "test", "expiresUtc": 20991231}),
                    ("compact string expiresUtc", {"profile": "test", "expiresUtc": "20991231"}),
                    ("compact date-time expiresUtc", {"profile": "test", "expiresUtc": "20991231T235900Z"}),
                    ("date-only expiresUtc", {"profile": "test", "expiresUtc": "2099-12-31"}),
                    ("null expiresUtc", {"profile": "test", "expiresUtc": None}),
                    ("list expiresUtc", {"profile": "test", "expiresUtc": ["2099-12-31T23:59:00Z"]}),
                    # review2 #1: fromisoformat normalises an out-of-range offset (-07:60 -> -08:00) instead of refusing
                    ("offset minutes 60", {"profile": "test", "expiresUtc": "2099-11-01T01:30:00-07:60"}),
                    ("offset minutes 99", {"profile": "test", "expiresUtc": "2099-11-01T01:30:00+05:99"}),
                    ("offset hours 24", {"profile": "test", "expiresUtc": "2099-11-01T01:30:00+24:00"})):
    put(body)
    g = rd()
    ok("%s -> LAPSED (the companion reads it as campaign)" % label, (g["state"], g["hours_left"]), ("LAPSED", 0.0))
    ok("%s says why" % label, bool(g["why"]), True)
os.remove(P)
ok("absent file in a visible folder -> LAPSED", rd()["state"], "LAPSED")
g = rd(path=os.path.join(D, "nope", "companion_profile.json"))
ok("folder not visible -> UNMEASURED (blind, not lapsed)", (g["state"], g["hours_left"]), ("UNMEASURED", None))

# ---------------------------------------------------------------- the preflight `rimflow next` applies
for st, held in (("OK", False), ("LAPSING", True), ("LAPSED", True), ("UNMEASURED", True)):
    ctx = {}
    with redirect_stdout(io.StringIO()) as o:
        cli._apply_grant_preflight(ctx, reader=lambda st=st: {"state": st, "why": "w", "hours_left": 1.0,
                                                              "expires": "E", "file": P})
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
                   ("a non-string entry", ["bridge", 3])):
    json.dump(dict(CONF, hold_needs=bad), open(BADC, "w"))
    try:
        cg.load_conf(BADC)
        refused = False
    except ValueError:
        refused = True
    ok("load_conf refuses hold_needs as %s" % label, refused, True)
json.dump(dict(CONF, hold_within_min="120"), open(BADC, "w"))
try:
    cg.load_conf(BADC)
    refused = False
except ValueError:
    refused = True
ok("load_conf refuses a non-number hold_within_min", refused, True)
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
ok("cmd_next runs the preflight", "_apply_grant_preflight(ctx" in inspect.getsource(cli.cmd_next), True)

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
KEY = "companion.grant_hours_left"
ok("the blind digest may show it", KEY in OW.BLIND_KEYS, True)
os.environ["RM_COMPANION_PROFILE"] = P
try:
    put({"profile": "test", "expiresUtc": ISO(NOW + 30 * 3600)})
    pts = OW.c_companion(NOW, OW.load_rules(), {})
    ok("collector: MEASURED hours left", (pts[KEY]["m"], round(pts[KEY]["v"])), ("MEASURED", 30))
    ok("collector: says state and expiry", (pts[KEY]["x"]["state"], pts[KEY]["x"]["expires"]),
       ("OK", ISO(NOW + 30 * 3600)))
    os.remove(P)
    pts = OW.c_companion(NOW, OW.load_rules(), {})
    ok("collector: an absent grant is MEASURED lapsed (0 h)", (pts[KEY]["m"], pts[KEY]["v"]), ("MEASURED", 0.0))
    os.environ["RM_COMPANION_PROFILE"] = os.path.join(D, "nope", "companion_profile.json")
    ok("collector: blind folder -> UNMEASURED", OW.c_companion(NOW, OW.load_rules(), {})[KEY]["m"], "UNMEASURED")
finally:
    os.environ.pop("RM_COMPANION_PROFILE", None)

R = OW.load_rules()
tg = [t for t in R["targets"] if t.get("key") == KEY and t.get("alarm")]
ok("one alarm target on the grant", len(tg), 1)
if tg:
    t = tg[0]
    ok("the warning comes before the preflight hold", t["value"] * 60 > CONF["hold_within_min"], True)
    ok("the warning line is 12 h (the item's requirement, not derived from config)", (t["op"], t["value"]), ("<", 12))
    ok("the target carries a why and a name", (bool(t.get("why")), bool(t.get("name"))), (True, True))
    ok("the name passes the mint rules", not cli.model.mint_problems(t["name"] + "_AB12", set()), True)
    aid = "%s:%s" % (t["tag"], KEY)
    st = lambda v, m="MEASURED": OW.target_state({KEY: {"v": v, "m": m}}, R).get(aid)
    # mutation-style: the line is exactly the configured value; either side of it flips the alarm
    ok("alarm: under the line crosses", st(t["value"] - 0.5), True)
    ok("alarm: over the line is clear", st(t["value"] + 0.5), False)
    ok("alarm: a lapsed grant (0 h, negative) crosses", (st(0.0), st(-5.0)), (True, True))
    ok("alarm: UNMEASURED holds (no file, no clear)", st(None, "UNMEASURED"), None)

# review #4: fixed values around 12 h, independent of the configured line
if tg:
    aid = "GRANT_LAPSING:" + KEY
    fx = lambda v: OW.target_state({KEY: {"v": v, "m": "MEASURED"}}, R).get(aid)
    ok("12 h boundary: 11.9 h crosses, 12.1 h and 13 h clear, 3 h crosses", (fx(11.9), fx(12.1), fx(13.0), fx(3.0)),
       (True, False, False, True))

# review #1 + #4: collector -> alarm, end to end through run_alarms: healthy, then lapsing, then folder blind, renewed
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
    put({"profile": "test", "expiresUtc": ISO(NOW + 30 * 3600)})
    pts, st = ow_pass(NOW, P)
    ok("e2e healthy (30 h): visible, nothing filed", (pts["companion.grant_visible"]["v"], filed), (1, []))
    pts, st = ow_pass(NOW + 18.5 * 3600, P)     # 11.5 h left
    ok("e2e 11.5 h left: GRANT_LAPSING filed once", [a["name"].rsplit("_", 1)[0] for a in filed], ["OPS_GRANT_ASK"])
    BLIND = os.path.join(D, "gone", "JawaBench", "companion_profile.json")
    pts, st = ow_pass(NOW + 19 * 3600, BLIND)
    ok("e2e folder gone: hours UNMEASURED, visible MEASURED 0",
       (pts[KEY]["m"], pts["companion.grant_visible"]["m"], pts["companion.grant_visible"]["v"]), ("UNMEASURED", "MEASURED", 0))
    ok("e2e folder gone: GRANT_UNSEEN filed (fail closed, not silent)",
       [a["name"].rsplit("_", 1)[0] for a in filed if not a.get("note_only")], ["OPS_GRANT_ASK", "OPS_GRANT_PROBE"])
    put({"profile": "test", "expiresUtc": ISO(NOW + 100 * 3600)})   # renewed
    for i in range(int(R["alarm"]["clear_passes"])):
        pts, st = ow_pass(NOW + 20 * 3600 + i * 900, P)
    ok("e2e renewed: both alarms clear after clear_passes", sorted(k for k in st if k.startswith("GRANT_")), [])
    ok("e2e renewed: nothing new filed, only clear notes",
       [a["name"].rsplit("_", 1)[0] for a in filed if not a.get("note_only")], ["OPS_GRANT_ASK", "OPS_GRANT_PROBE"])
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
    # review2 #3: the collector keeps full precision, so 11 h 59 m 50 s crosses the 12 h line on this pass
    put({"profile": "test", "expiresUtc": ISO(NOW + 12 * 3600)})
    os.environ["RM_COMPANION_PROFILE"] = P
    pts = OW.c_companion(NOW + 10, R, {})
    ok("collector+alarm: 10 s under 12 h crosses (no rounding up to 12.0)",
       OW.target_state(pts, R).get("GRANT_LAPSING:" + KEY), True)
    pts = OW.c_companion(NOW - 10, R, {})
    ok("collector+alarm: 10 s over 12 h is clear", OW.target_state(pts, R).get("GRANT_LAPSING:" + KEY), False)
    # a readable but malformed config: the collector fails closed (visible 0 -> GRANT_UNSEEN)
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
