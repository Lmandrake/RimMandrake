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
                    ("unparseable expiresUtc", {"profile": "test", "expiresUtc": "Tuesday"})):
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
    cli._claimable = lambda *a, **k: [C("bridge")]
    ok("grant held and only grant work: nothing", cli._choose(None, "FOUNDRY", args, hctx, None)["kind"], "nothing")
finally:
    cli.priority.rank, cli.reconcile.guard, cli._claimable, cli.reconcile.assess = saved

# ---------------------------------------------------------------- the early warning (ops_watch)
ok("ops_watch has the companion family", ("companion" in OW.COLLECTORS, "companion" in OW.ORDER,
                                           "companion" in OW.FAMILIES), (True, True, True))
KEY = "companion.grant_hours_left"
ok("the Conductor's blind digest may show it", KEY in OW.BLIND_KEYS, True)
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
    ok("the target carries a why and a name", (bool(t.get("why")), bool(t.get("name"))), (True, True))
    ok("the name passes the mint rules", not cli.model.mint_problems(t["name"] + "_AB12", set()), True)
    aid = "%s:%s" % (t["tag"], KEY)
    st = lambda v, m="MEASURED": OW.target_state({KEY: {"v": v, "m": m}}, R).get(aid)
    # mutation-style: the line is exactly the configured value; either side of it flips the alarm
    ok("alarm: under the line crosses", st(t["value"] - 0.5), True)
    ok("alarm: over the line is clear", st(t["value"] + 0.5), False)
    ok("alarm: a lapsed grant (0 h, negative) crosses", (st(0.0), st(-5.0)), (True, True))
    ok("alarm: UNMEASURED holds (no file, no clear)", st(None, "UNMEASURED"), None)

print("\n%s: %d failed" % ("FAIL" if FAILED else "PASS", len(FAILED)))
sys.exit(1 if FAILED else 0)
