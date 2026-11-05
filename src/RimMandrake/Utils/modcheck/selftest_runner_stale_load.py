#!/usr/bin/env python3
"""Selftest for MODCHECK_SESSION_FIX_STALE_LIST_ACCEPTED: after composing ModsConfig, runner.run() must not accept a
session that is already Playing on the PREVIOUS list. It reads the running load (jawa/running_mods) and, unless it
equals the composed activeMods (or, under MODCHECK_KEEP_MODLIST, holds the mods under test), records the mod
UNMEASURED: no suite runs, no status entry is written. Offline: the bridge, ModsConfig and every side effect are stubbed."""
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import runner  # noqa: E402

FAILS = []


def ok(cond, what, got=None):
    print(("PASS  " if cond else "FAIL  ") + what + ("" if cond or got is None else "   got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


MINIMAL = ["ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
           "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey", "brrainz.harmony", "toy.dep"]
TOY = "mandrake.rimmandrake.toymod"
FULL = MINIMAL[:-1] + ["owner.big.mod%d" % i for i in range(40)]      # the previous (owner's) list: toy not on it


def write_config(ids):
    fd, path = tempfile.mkstemp(suffix="_ModsConfig.xml")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("<ModsConfigData>\n  <version>1.6</version>\n  <activeMods>\n%s  </activeMods>\n"
                "  <knownExpansions>\n    <li>ludeon.rimworld.royalty</li>\n    <li>stray.known.only</li>\n"
                "  </knownExpansions>\n</ModsConfigData>\n" % "".join("    <li>%s</li>\n" % p for p in ids))
    return path


class FakeBridge:
    def __init__(self, running):
        self.running, self.calls = running, []

    def connect(self):
        pass

    def call(self, tool, args):
        self.calls.append(tool)
        if tool != "jawa/running_mods":
            raise AssertionError("unexpected bridge call " + tool)
        if self.running is None:
            raise ConnectionError("bridge down")
        return {"success": True, "packageIds": list(self.running)}


class ReachedSuite(Exception):
    pass


def mods_root(ids):
    """A temp install root holding one <folder>/About/About.xml per id."""
    root = tempfile.mkdtemp(suffix="_Mods")
    for i, p in enumerate(ids):
        os.makedirs(os.path.join(root, "m%d" % i, "About"))
        with open(os.path.join(root, "m%d" % i, "About", "About.xml"), "w", encoding="utf-8") as f:
            f.write("<ModMetaData><name>m</name><packageId>%s</packageId></ModMetaData>" % p)
    return root


def attempt(running, config_ids, keep=False, keep_composed=False, restores=None, installed=None):
    """run() with one toy mod, a ModsConfig holding config_ids and a game whose running load is `running`.
    -> (results or None, reached_suite, record_run calls, bridge calls, sheets written)."""
    cfg = write_config(config_ids)
    bridge = FakeBridge(running)
    recorded, sheets = [], []
    fake_rb = types.ModuleType("rimbridge_client")
    fake_rb.resolve_endpoint = lambda *a, **k: ("h", 1, "t")
    fake_rb.RimBridge = lambda **k: bridge
    fake_gp = types.ModuleType("game_paths")
    fake_gp.MODS_CONFIG = cfg
    if installed is not None:
        fake_gp.LOCAL_MODS = mods_root(installed)
    fake_status = types.ModuleType("status")
    fake_status.record_run = lambda *a, **k: recorded.append(a)
    mods_saved = {n: sys.modules.get(n) for n in ("rimbridge_client", "game_paths", "status")}
    sys.modules.update(rimbridge_client=fake_rb, game_paths=fake_gp, status=fake_status)
    fake_suite = types.SimpleNamespace(chains=[("c1", None)])

    def reached():
        raise ReachedSuite()

    stubs = dict(swap_to_test_list=lambda *a, **k: None,
                 restore_full=lambda *a, **k: (restores if restores is not None else []).append(1),
                 compose_test_list=lambda *a, **k: [], find_mod_dir=lambda m: "/nonexistent/" + m,
                 composed_into=lambda m: None, mod_dependency_ids=lambda d: ["toy.dep"],
                 mod_package_id=lambda d: TOY, closure_ids=lambda m, f: [],
                 load_validation=lambda d: fake_suite, northstar_for=lambda m: ("walk", None),
                 visual_floor=lambda s, ns: {"bar": None}, refusal=lambda fl: None,
                 ensure_playing_map=lambda *a, **k: "playing", ensure_test_profile=reached,
                 write_sheet=lambda m, s: sheets.append((m, s)) or "/tmp/sheet.html")
    real = {n: getattr(runner, n) for n in stubs}
    env_saved = {k: os.environ.get(k) for k in ("MODCHECK_KEEP_MODLIST", "MODCHECK_SKIP_DEPLOY",
                                                "MODCHECK_STALE_KEEP_COMPOSED")}
    os.environ["MODCHECK_SKIP_DEPLOY"] = "1"
    os.environ.pop("MODCHECK_KEEP_MODLIST", None)
    if keep:
        os.environ["MODCHECK_KEEP_MODLIST"] = "1"
    os.environ.pop("MODCHECK_STALE_KEEP_COMPOSED", None)
    if keep_composed:
        os.environ["MODCHECK_STALE_KEEP_COMPOSED"] = "1"
    for n, f in stubs.items():
        setattr(runner, n, f)
    res, hit = None, False
    try:
        res = runner.run([("ToyMod", "X_ITEM")])
    except ReachedSuite:
        hit = True
    finally:
        for n, f in real.items():
            setattr(runner, n, f)
        for n, m in mods_saved.items():
            if m is None:
                sys.modules.pop(n, None)
            else:
                sys.modules[n] = m
        for k, v in env_saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        os.unlink(cfg)
    return res, hit, recorded, bridge.calls, sheets


composed = MINIMAL + [TOY]

# 1. the instance: the game was already Playing on the previous (full) list when run() composed MINIMAL + toy
res, hit, rec, calls, sheets = attempt(FULL, composed)
ok(not hit, "stale Playing session (previous list): no suite runs")
ok(calls == ["jawa/running_mods"], "the running load is read from the bridge", calls)
r = (res or {}).get("ToyMod", {})
ok(r.get("refused", "").startswith("UNMEASURED") and r.get("unmeasured") == "stale_load",
   "stale session: the mod is recorded UNMEASURED (stale_load)", r)
ok(r.get("all_green") is False, "stale session: never all_green", r.get("all_green"))
ok(TOY in r.get("refused", "") and "owner.big.mod0" in r.get("refused", ""),
   "the reason names the missing composed id and the stray loaded ids", r.get("refused"))
ok(rec == [], "stale session: no status entry written (not a verdict on the mod)", rec)
ok(len(sheets) == 1 and sheets[0][0] == "ToyMod", "stale session: the UNMEASURED sheet is written", sheets)

# 2. a stale list that already held the mod under test (a superset) is still not the composed list
res, hit, rec, _, _ = attempt(FULL + [TOY], composed)
ok(not hit and "loaded but not composed" in res["ToyMod"].get("refused", ""),
   "superset load (previous list + the mod): UNMEASURED, not certified", (res or {}).get("ToyMod"))

# 3. the running load equals the composed list: the suite is reached
_, hit, rec, _, _ = attempt(list(reversed(composed)), composed)
ok(hit, "running load == composed ModsConfig (any order): the suite runs")

# 4. knownExpansions entries do not count as the composed list (parsed, not a regex over <li>)
_cfg = write_config(composed)
ok("stray.known.only" not in runner.active_mods(_cfg), "active_mods reads <activeMods> only")
os.unlink(_cfg)

# 5. bridge unreadable: UNMEASURED, never certified
res, hit, rec, _, _ = attempt(None, composed)
ok(not hit and "running_mods raised" in res["ToyMod"].get("refused", "") and rec == [],
   "unreadable running load: UNMEASURED, no status entry", (res or {}).get("ToyMod"))

# 6. MODCHECK_KEEP_MODLIST (owner's list, never composed): the load must HOLD the mods under test, extras are fine
_, hit, _, _, _ = attempt(FULL + ["toy.dep", TOY], ["unrelated.config"], keep=True)
ok(hit, "keep mode, mod loaded on the owner's list: the suite runs")
res, hit, _, _, _ = attempt(FULL + ["toy.dep"], ["unrelated.config"], keep=True)
ok(not hit and "not loaded: %s" % TOY in res["ToyMod"].get("refused", ""),
   "keep mode, mod absent from the running load: UNMEASURED", (res or {}).get("ToyMod"))

# 7. load_gap: a folded member counts through its composed mod
ok(runner.load_gap(["a", "member"], {"a", "composed"}, exact=True, alias={"member": "composed"}) == [],
   "load_gap: folded member satisfied by its composed mod")
ok(runner.load_gap(["a"], None, exact=True) != [], "load_gap: unread running load is a gap")

# 8. STEVE_LANE_UNSTICK_BRAKED_UNOWNED_8EB8: the caller that owns the game asks run() to leave ModsConfig on the composed
#    list when it refuses stale_load, so a restart loads it; otherwise FULL is restored as always
import contextlib, io  # noqa: E402,E401
for keep_c, want_restore in ((False, 1), (True, 0)):
    restores, buf = [], io.StringIO()
    with contextlib.redirect_stdout(buf):
        attempt(FULL, composed, keep_composed=keep_c, restores=restores)
    ok(len(restores) == want_restore, "stale load, MODCHECK_STALE_KEEP_COMPOSED=%d: restore_full called %d time(s)"
       % (keep_c, want_restore), restores)
    ok(("STALE_LOAD: ToyMod:" in buf.getvalue()) == keep_c,
       "stale load, keep composed=%d: the STALE_LOAD line %s" % (keep_c, "printed" if keep_c else "absent"),
       buf.getvalue())
restores = []
attempt(list(composed), composed, keep_composed=True, restores=restores)
ok(restores == [1], "load fits, keep composed set: FULL still restored (only a stale refusal keeps the list)", restores)

# 9. MODCHECK_STALE_LOAD_FIX_UNINSTALLED_MOD (Steve canary J20261104T074700Z-42d8eb): a composed id that is not running
#    because no folder on the host holds it is mod_not_installed, not stale_load: ModsConfig is restored (no STALE_LOAD
#    line, so the worker spends no restart) and the reason names the id
CAM = "ray1203.simplecamerasetting"
on_host = [p for p in MINIMAL if not p.startswith("ludeon.")] + [TOY]
for keep_c in (False, True):
    restores, buf, err = [], io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
        res, hit, rec, _, sheets = attempt(composed, composed + [CAM], keep_composed=keep_c, restores=restores,
                                           installed=on_host)
    r = (res or {}).get("ToyMod", {})
    ok(not hit and r.get("unmeasured") == "mod_not_installed" and CAM in r.get("refused", ""),
       "uninstalled composed mod (keep composed=%d): UNMEASURED mod_not_installed, names it" % keep_c, r)
    ok(restores == [1] and "STALE_LOAD:" not in buf.getvalue(),
       "uninstalled composed mod (keep composed=%d): FULL restored, no STALE_LOAD line" % keep_c, buf.getvalue())
    ok(rec == [] and len(sheets) == 1, "uninstalled composed mod: no status entry, the UNMEASURED sheet is written")
    import re  # noqa: E402
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE)))),
                            "infrastructure", "stevedesktop", "worker.py"), encoding="utf-8").read()
    pat = re.search(r'NOT_INSTALLED_RE = re\.compile\(r"(.+?)", re\.M\)', src)
    ok(pat and re.search(pat.group(1), err.getvalue(), re.M) and not re.search(
        r"HARNESS UNMEASURED: the running load is not the composed list", err.getvalue()),
       "the runner's log line is what the Steve worker reads as mod_not_installed (and not as stale_load)",
       err.getvalue())
# the same gap with the mod installed (just not yet loaded) stays stale_load: a restart can load it
res, hit, _, _, _ = attempt(composed, composed + [CAM], installed=on_host + [CAM])
ok(res["ToyMod"].get("unmeasured") == "stale_load", "installed but not loaded: still stale_load", res.get("ToyMod"))
# an install root the instrument cannot see claims nothing: stale_load as before
res, hit, _, _, _ = attempt(composed, composed + [CAM], installed=[])
ok(res["ToyMod"].get("unmeasured") == "stale_load", "an empty install scan claims no mod uninstalled",
   res.get("ToyMod"))
ok(runner.not_installed(["a", "member", "ludeon.rimworld.odyssey"], {"composed"}, {"member": "composed"}) == ["a"],
   "not_installed: a folded member is installed through its composed mod; Ludeon ids are always installed")
ok(runner.not_installed(["a"], None) == [], "not_installed: an unmeasured install set names nothing")

print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)
