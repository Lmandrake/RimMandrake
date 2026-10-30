#!/usr/bin/env python3
"""selftest_arena_switch.py - arena.py (the switch), each criterion proven by FORCED FAILURE.

ARENA_SWITCH_BUILD_ONE_ARM_LIVE_ONLY. Nothing here starts systemd, dbus, a private manager or touches a cgroup or a real
unit: every `systemctl` is src/RimMandrake/Utils/arena/fixtures/fake_systemctl.py, which emulates a transactional
`start A B` (fails on conflicting jobs) and a sequential `start B` (stops A through Conflicts=), reading the RENDERED
unit files from a temp dir. The real user unit dir, the real seats, arm.toml, the real ModsConfig.xml and the real
event log are never read or written; git work happens in throwaway repos under a temp dir.

  two targets    start A B fails for every pair (incl. production) and changes nothing. Forced: units rendered without
                 a Conflicts= line -> the same transaction SUCCEEDS (the shim can see), and check_graph names the hole
  graph          rendered templates pass check_graph; forced: a missing/one-way Conflicts=, a member with no PartOf=,
                 a member PartOf two targets, an unknown target -> each reported
  switch         ralph_a -> production rehearsed end to end with the shim (STOP, idle wait, stop, both bridges
                 released, list restored by PARSING ModsConfig, event signed, new target started, who 0). Forced:
                 never idle (forced stop at 90 min, injectable clock), unpushed commit (refused, old target stays),
                 signer failure (new target NOT started), bridge release failure, a restore that leaves different
                 activeMods, a ModsConfig where grep would be fooled
  who            exit 0 when sound; forced: a -> 1, b -> 2, c -> 4, d -> 8 (and combinations); a reader that raises
                 fails its check; the /proc cwd reader sees a real child process (instrument probe)
  push           throwaway bare remote + clone with the installed hook: live arm to arena/<arm>/x OK; main refused;
                 a delete refused; a STOPPED arm (mode changed) refused AND alarmed (fake sink and the file sink);
                 an unreadable arm.toml refuses; the production clones may not push arena refs
  installer      dry run writes nothing; --apply writes only into the dir it is given; real unit dir untouched
  ops_watch      ARENA_TWO_LIVE rule exists, the collector reads MEASURED 0 when sound / bitmask when forced / UNMEASURED
                 with no arm.toml; target_state crosses only on a MEASURED nonzero
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp(prefix="selftest_arena_switch_"))
os.environ["ARENA_ROOT"] = str(TMP / "arena")
os.environ["ARENA_CLONES"] = str(TMP / "clones")
os.environ["ARENA_ARM_TOML"] = str(TMP / "arena" / "arm.toml")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arena as AR  # noqa: E402
import arena_install as INS  # noqa: E402

FAILS = []
SHIM = HERE / "fixtures" / "fake_systemctl.py"
GENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
REAL_UNIT_DIR = INS.DEFAULT_UNIT_DIR


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def git(repo, *a, check_rc=True):
    r = subprocess.run(["git", "-C", str(repo)] + list(a), capture_output=True, text=True, env=GENV)
    if check_rc and r.returncode != 0:
        raise RuntimeError("git %s: %s" % (a, r.stderr))
    return r


def snapshot(d):
    d = Path(d)
    return sorted((str(p.relative_to(d)), p.stat().st_size) for p in d.rglob("*")) if d.exists() else None


# ------------------------------------------------------------------ fixtures
TOML = '''mode = "%s"
[production]
scope = ["bench", "foundry"]
[clones]
bench = "%s/clones/bench"
foundry = "%s/clones/foundry"
[arms.ralph_a]
units = ["rm-ralph-loop@a.service"]
[arms.ralph_c]
units = ["rm-ralph-loop@a1.service", "rm-runner@steve.service"]
[arms.trio]
units = ["rm-testpilot@steve.service"]
[arms.v3]
units = ["rm-dispatcher.service"]
[arms.production]
units = ["rm-prod-loop.service"]
'''


class World:
    """A throwaway arena: arm.toml, rendered units, a shim state file, arena dir, git clones with bare remotes."""

    def __init__(self, name, mode="ralph_a", active=("ralph_a",), skip_conflicts=False):
        self.root = TMP / name
        os.environ["ARENA_CLONES"] = str(self.root / "clones")
        self.arena = self.root / "arena"
        self.units = self.root / "units"
        self.state = self.root / "shim_state.json"
        self.toml = self.arena / "arm.toml"
        self.arena.mkdir(parents=True)
        self.units.mkdir()
        self.toml.write_text(TOML % (mode, self.root, self.root))
        self.cfg = AR.load_config(self.toml)
        self.render(skip_conflicts)
        self.state.write_text(json.dumps({"active": sorted(AR.target_name(a) for a in active)}))
        self.sc = AR.Systemctl([sys.executable, str(SHIM), "--state", str(self.state), "--unit-dir", str(self.units)])
        self.remotes = {}

    def render(self, skip_conflicts=False, cfg=None):
        cfg = cfg or self.cfg
        for arm in AR.ARMS:
            t = AR.render_target(arm, cfg)
            if skip_conflicts:
                t = "\n".join(l for l in t.splitlines() if not l.startswith("Conflicts=")) + "\n"
            (self.units / AR.target_name(arm)).write_text(t)
            for u in cfg["units"].get(arm, []):
                d = self.units / (u + ".d"); d.mkdir(exist_ok=True)
                (d / "10-arm.conf").write_text(AR.render_dropin(arm))

    def active(self):
        return sorted(json.loads(self.state.read_text())["active"])

    def clone(self, arm):
        """a clone of the arm with an 'origin' bare remote, one pushed commit on arena/<arm>/a (or main for production)."""
        c = AR.clone_path(self.cfg, arm)
        bare = self.root / "remotes" / ("%s.git" % arm)
        bare.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True, env=GENV)
        c.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", "-b", "main", str(c)], check=True, env=GENV)
        git(c, "remote", "add", "origin", str(bare))
        (c / "f.txt").write_text("1\n"); git(c, "add", "f.txt"); git(c, "commit", "-qm", "base")
        br = "main" if arm in AR.PRODUCTION_ARMS else "arena/%s/a" % arm
        git(c, "checkout", "-q", "-B", br)
        git(c, "push", "-q", "origin", br)
        self.remotes[arm] = bare
        return c

    def deps(self, **over):
        d = AR.Deps(root=self.arena, systemctl=self.sc, signer=self.signer_ok)
        t = {"now": 1_800_000_000.0}
        d.clock = lambda: t["now"]
        d.sleep = lambda s: t.__setitem__("now", t["now"] + s)
        d.poll_s = 60.0
        d.log = lambda m: None
        self.released = []
        d.bridge_release = lambda h: (self.released.append(h) or True, "ok")
        d.unpushed = lambda c: []
        d.modlist_restore = lambda: {"active": 2}
        d.t = t
        for k, v in over.items():
            setattr(d, k, v)
        return d

    events = None

    def signer_ok(self, arm, event, **kw):
        self.events = (self.events or []) + [dict(arm=arm, event=event, **kw)]
        return dict(arm=arm, event=event, **kw)


def idle_status(w, arm, state):
    p = w.arena / "status" / ("%s.json" % arm)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"state": state}))


# ------------------------------------------------------------------ tests
def t_two_targets():
    w = World("two", active=())
    pairs = [(a, b) for i, a in enumerate(AR.ARMS) for b in AR.ARMS[i + 1:]]
    bad = []
    for a, b in pairs:
        rc, out = w.sc.run("start", AR.target_name(a), AR.target_name(b))
        if rc == 0 or "conflicting jobs" not in out or w.active():
            bad.append((a, b, rc, w.active()))
    check(not bad, "starting two arm targets in one transaction fails for all %d pairs (incl. production) and changes nothing %s" % (len(pairs), bad[:2]))
    w.sc.start(AR.target_name("trio")); w.sc.start(AR.target_name("production"))
    check(w.active() == sorted([AR.target_name("production"), "rm-prod-loop.service"]), "sequential start of a second target stops the first via Conflicts= (%s)" % w.active())
    w.sc.start(AR.target_name("ralph_c"))
    check(w.active() == sorted([AR.target_name("ralph_c"), "rm-ralph-loop@a1.service", "rm-runner@steve.service"]),
          "starting ralph_c wants its members and nothing else (%s)" % w.active())
    w.sc.start(AR.target_name("ralph_a"))
    check(w.active() == sorted([AR.target_name("ralph_a"), "rm-ralph-loop@a.service"]), "...and ralph_a stops ralph_c's members (%s)" % w.active())
    # FORCED FAILURE: units without Conflicts= -> two targets start fine; the check_graph names it
    f = World("two_forced", active=(), skip_conflicts=True)
    rc, out = f.sc.run("start", AR.target_name("ralph_a"), AR.target_name("trio"))
    check(rc == 0 and len(f.active()) >= 2, "FORCED: targets rendered with no Conflicts= DO start together (the shim can see) %s" % f.active())
    probs = AR.check_graph(AR.read_unit_dir(f.units))
    check(any("lacks Conflicts" in p for p in probs), "FORCED: check_graph names the missing Conflicts= (%d problems)" % len(probs))
    # the arena's own start path passes exactly one unit per call
    calls = []
    class Rec(AR.Systemctl):
        def run(self, *a, **k): calls.append(a); return super().run(*a, **k)
    w2 = World("two_rec", active=("ralph_a",), mode="ralph_a")
    d = w2.deps(); d.systemctl = Rec(w2.sc.cmd)
    w2.clone("ralph_a"); [w2.clone(c) for c in ("bench",)]
    for c in ("foundry",): w2.clone(c)
    AR.switch("trio", w2.toml, d)
    starts = [c for c in calls if c[0] == "start"]
    check(starts and all(len(c) == 2 for c in starts), "switch starts one target per systemctl call %s" % starts)


def t_graph():
    w = World("graph", active=())
    check(AR.check_graph(AR.read_unit_dir(w.units)) == [], "rendered templates: Conflicts= mutual, every member PartOf one target")
    base = AR.read_unit_dir(w.units)
    one_way = dict(base); one_way["rm-arm-trio.target"] = one_way["rm-arm-trio.target"].replace("rm-arm-ralph_a.target", "")
    p = AR.check_graph(one_way)
    check(any("lacks Conflicts=rm-arm-ralph_a.target" in x for x in p) and any("not mutual" in x for x in p), "FORCED one-way Conflicts= reported (%s)" % p[:2])
    nopart = dict(base); nopart["rm-ralph-loop@a.service"] = "[Unit]\nDescription=x\n"
    check(any("PartOf" in x for x in AR.check_graph(nopart)), "FORCED member with no PartOf= reported")
    two = dict(base); two["rm-ralph-loop@a.service"] = "[Unit]\nPartOf=rm-arm-ralph_a.target rm-arm-trio.target\n"
    check(any("exactly one" in x for x in AR.check_graph(two)), "FORCED member PartOf two targets reported")
    unk = dict(base); unk["rm-ralph-loop@a.service"] = "[Unit]\nPartOf=rm-arm-nope.target\n"
    check(any("unknown target" in x for x in AR.check_graph(unk)), "FORCED PartOf unknown target reported")
    miss = {k: v for k, v in base.items() if k != "rm-arm-production.target"}
    check(any("missing target" in x for x in AR.check_graph(miss)), "FORCED missing production target reported")
    prod = base["rm-arm-production.target"]
    check("X-RM-Scope=bench,foundry" in prod, "production target carries its scope")
    c2 = dict(w.cfg, scope=["foundry"])
    check("X-RM-Scope=foundry" in AR.render_target("production", c2), "scope setting changes the production target")
    for bad_scope in ("scope = []", 'scope = ["dispatch"]', 'scope = ["bench", "bench"]'):
        w.toml.write_text(TOML.replace('scope = ["bench", "foundry"]', bad_scope) % ("production", w.root, w.root))
        try:
            AR.load_config(w.toml); ok = False
        except AR.SwitchError:
            ok = True
        check(ok, "FORCED bad scope %s refused by the loader" % bad_scope)
    w.toml.write_text('mode = "everything"\n')
    try:
        AR.load_config(w.toml); ok = False
    except AR.SwitchError:
        ok = True
    check(ok, "FORCED unknown mode refused by the loader")


def t_switch_production():
    w = World("sw")
    for a in ("ralph_a", "bench", "foundry"):
        w.clone(a)
    idle_status(w, "ralph_a", "busy")
    d = w.deps()
    # become idle after 7 polls (7 minutes of fake clock)
    n = {"i": 0}
    def sleep(s):
        d.t["now"] += s; n["i"] += 1
        if n["i"] == 7:
            idle_status(w, "ralph_a", "idle")
    d.sleep = sleep
    # restore by PARSING: live ModsConfig reformatted + a decoy <li> in knownExpansions that a grep would find
    full = w.root / "FULL.xml"; live = w.root / "ModsConfig.xml"
    full.write_text("<ModsConfigData><activeMods><li>ludeon.rimworld</li><li>Mandrake.X</li></activeMods></ModsConfigData>")
    live.write_text("<ModsConfigData>\n <version>1</version><activeMods>\n  <li>ludeon.rimworld</li>\n  <li>mandrake.x</li>\n </activeMods>"
                    "<knownExpansions><li>zzz</li></knownExpansions></ModsConfigData>")
    d.modlist_restore = lambda: AR.verify_restored(live, full)
    r = AR.switch("production", w.toml, d)
    check(w.active() == sorted([AR.target_name("production"), "rm-prod-loop.service"]), "production mode: only the production target + its member live (%s)" % w.active())
    check(AR.load_config(w.toml)["mode"] == "production", "arm.toml now says production")
    check(r["stopped"] == ["ralph_a"] and not r["forced"] and 6 * 60 <= r["waited_s"] <= 8 * 60, "STOP honoured at idle after ~7 min, no forced stop (%s)" % r["waited_s"])
    check(sorted(w.released) == ["archmagi", "stevedesktop"], "both bridges released (%s)" % w.released)
    check(r["restored"] == {"active": 2}, "list restored and verified by parsing activeMods")
    ev = w.events[-1]
    check(ev["event"] == "switch" and ev["arm"] == "production" and ev["lane"] == "none" and ev["detail"]["from"] == "ralph_a"
          and ev["detail"]["scope"] == ["bench", "foundry"], "switch event signed with from/to/scope %s" % ev["detail"])
    import arena_eventlog as L
    try:
        L.validate_record(dict(ts=ev["ts"], arm=ev["arm"], lane=ev["lane"], run_id=ev["run_id"], event="switch", detail=ev["detail"])); ok = True
    except L.Rejected as e:
        ok = False; print(e)
    check(ok, "the switch record passes arena_eventlog.validate_record")
    check(r["who"]["exit"] == 0, "arena who is 0 after the switch")
    check(not (w.arena / "STOP.production").exists() and (w.arena / "STOP.ralph_a").exists(), "STOP file written for the old arm, cleared for the new")
    check(json.loads((w.arena / "switch_state.json").read_text())["mode"] == "production", "switch_state recorded")
    # back to an arena arm and to trial
    r2 = AR.switch("trio", w.toml, w.deps()); check(w.active() == sorted([AR.target_name("trio"), "rm-testpilot@steve.service"]), "production -> trio")
    AR.switch("trial", w.toml, w.deps()); check(w.active() == sorted([AR.target_name("v3"), "rm-dispatcher.service"]), "trial keeps v3 (the control) as the only target")
    # arm.toml parse not grep: a restore that leaves different mods
    for label, body in (("different activeMods", "<ModsConfigData><activeMods><li>ludeon.rimworld</li></activeMods></ModsConfigData>"),
                        ("grep-fooling: id only in knownExpansions", "<ModsConfigData><activeMods><li>ludeon.rimworld</li></activeMods><knownExpansions><li>mandrake.x</li></knownExpansions></ModsConfigData>"),
                        ("no activeMods", "<ModsConfigData></ModsConfigData>")):
        live.write_text(body)
        try:
            AR.verify_restored(live, full); ok = False
        except AR.SwitchError:
            ok = True
        check(ok, "FORCED restore verify fails: %s" % label)


def t_switch_forced():
    # never idle -> forced stop at 90 minutes
    w = World("sw_idle")
    for a in ("ralph_a", "bench", "foundry"):
        w.clone(a)
    idle_status(w, "ralph_a", "busy")
    d = w.deps()
    r = AR.switch("trio", w.toml, d)
    check(r["forced"] == ["ralph_a"] and 90 * 60 <= r["waited_s"] < 91 * 60 + 1, "FORCED never idle: target stopped after 90 min on the injected clock (%s)" % r["waited_s"])
    check(AR.target_name("trio") in w.active() and AR.target_name("ralph_a") not in w.active(), "...and trio is live, ralph_a not")
    # status file missing for an ACTIVE target is not idle (unmeasured never passes)
    w = World("sw_nofile")
    for a in ("ralph_a", "bench", "foundry"):
        w.clone(a)
    d = w.deps(); r = AR.switch("trio", w.toml, d)
    check(r["forced"] == ["ralph_a"], "FORCED missing status file is NOT idle (forced stop after the wait)")
    # unpushed commit -> refused, old arm untouched
    w = World("sw_unpushed")
    for a in ("ralph_a", "bench", "foundry"):
        w.clone(a)
    c = AR.clone_path(w.cfg, "ralph_a"); (c / "g.txt").write_text("x"); git(c, "add", "g.txt"); git(c, "commit", "-qm", "unpushed")
    idle_status(w, "ralph_a", "idle")
    d = w.deps(unpushed=AR.unpushed)
    try:
        AR.switch("trio", w.toml, d); ok = False; msg = ""
    except AR.Refused as e:
        ok = True; msg = str(e)
    check(ok and "unpushed" in msg and w.active()[0:1] and AR.target_name("ralph_a") in w.active() and AR.target_name("trio") not in w.active(),
          "FORCED unpushed commit: switch refused, ralph_a still the live arm, nothing new started")
    check(AR.load_config(w.toml)["mode"] == "ralph_a" and not w.released and w.events is None, "...mode unchanged, no bridge released, no event")
    check((w.arena / "STOP.ralph_a").exists(), "...STOP stays so the arm does not start a new pass")
    git(c, "push", "-q", "origin", "arena/ralph_a/a")
    AR.switch("trio", w.toml, w.deps(unpushed=AR.unpushed))
    check(AR.target_name("trio") in w.active(), "after pushing, the same switch goes through")
    # real unpushed(): no commit outside remotes -> []; git error raises
    check(AR.unpushed(c) == [] and AR.unpushed(TMP / "nogit") == [], "unpushed() is empty for a clean clone and a non-repo path")
    # unmeasured git state refuses
    def boom(_): raise RuntimeError("git exploded")
    w = World("sw_boom"); idle_status(w, "ralph_a", "idle")
    try:
        AR.switch("trio", w.toml, w.deps(unpushed=boom)); ok = False
    except AR.Refused:
        ok = True
    check(ok, "FORCED unreadable git state refuses (unmeasured never passes)")
    # signer failure -> old stopped, new NOT started
    w = World("sw_sign")
    for a in ("ralph_a", "bench", "foundry"):
        w.clone(a)
    idle_status(w, "ralph_a", "idle")
    def bad_signer(*a, **k): raise RuntimeError("entrypoint arena.py is not a harness entrypoint")
    try:
        AR.switch("trio", w.toml, w.deps(signer=bad_signer)); ok = False; msg = ""
    except AR.SwitchError as e:
        ok = True; msg = str(e)
    check(ok and "NOT started" in msg and w.active() == [] and AR.load_config(w.toml)["mode"] == "ralph_a",
          "FORCED signer refused: nothing is live, the new target was not started (%s)" % w.active())
    import arena_eventlog as L
    check("arena.py" not in L.ENTRYPOINTS, "OWED: arena_eventlog.ENTRYPOINTS does not yet allow arena.py (the real signer is refused until it does)")
    # bridge release failure
    w = World("sw_bridge")
    for a in ("ralph_a", "bench", "foundry"):
        w.clone(a)
    idle_status(w, "ralph_a", "idle")
    try:
        AR.switch("trio", w.toml, w.deps(bridge_release=lambda h: (False, "lock held by BENCH"))); ok = False
    except AR.SwitchError as e:
        ok = "bridge release failed" in str(e)
    check(ok and AR.target_name("trio") not in w.active(), "FORCED bridge release failure stops the switch before the new target")
    # restore failure
    w = World("sw_restore"); idle_status(w, "ralph_a", "idle")
    def rbad():
        raise AR.SwitchError("after restore activeMods differs")
    try:
        AR.switch("trio", w.toml, w.deps(modlist_restore=rbad)); ok = False
    except AR.SwitchError:
        ok = True
    check(ok and AR.target_name("trio") not in w.active(), "FORCED restore failure stops the switch before the new target")
    # bad mode
    try:
        AR.switch("nonsense", w.toml, w.deps()); ok = False
    except AR.Refused:
        ok = True
    check(ok, "FORCED unknown mode refused")
    # real cli: switch with a nonsense mode exits via argparse (no systemctl involved)
    r = subprocess.run([sys.executable, str(HERE / "arena.py"), "switch", "nonsense"], capture_output=True, text=True, env=os.environ)
    check(r.returncode == 2, "cli rejects an unknown mode (rc 2)")


def t_who():
    w = World("who", mode="ralph_a", active=("ralph_a",))
    d = w.deps()
    ok_kw = dict(bridge_locks=lambda: [], cwds=lambda: [(1, "/")], events=lambda *a: 0, pushed=lambda *a: [])
    r = AR.who(w.cfg, d, **ok_kw)
    check(r["exit"] == 0, "sound: who exits 0 %s" % r["exit"])
    # (a)
    w.state.write_text(json.dumps({"active": [AR.target_name("ralph_a"), AR.target_name("trio")]}))
    r = AR.who(w.cfg, d, **ok_kw); check(r["exit"] == 1 and not r["checks"]["a"]["ok"], "FORCED (a) two targets active -> exit 1")
    w.state.write_text(json.dumps({"active": []}))
    r = AR.who(w.cfg, d, **ok_kw); check(r["exit"] == 1, "FORCED (a) the expected target not active -> exit 1")
    w.state.write_text(json.dumps({"active": [AR.target_name("trio")]}))
    r = AR.who(w.cfg, d, **ok_kw); check(r["exit"] == 1, "FORCED (a) wrong target active -> exit 1")
    w.state.write_text(json.dumps({"active": [AR.target_name("ralph_a")]}))
    # (b)
    stopped = AR.clone_path(w.cfg, "trio"); (stopped / "sub").mkdir(parents=True)
    r = AR.who(w.cfg, d, **dict(ok_kw, cwds=lambda: [(4242, str(stopped / "sub"))]))
    check(r["exit"] == 2 and r["checks"]["b"]["inside_stopped_clone"][0][0] == 4242, "FORCED (b) process cwd inside a stopped arm's clone -> exit 2")
    live_c = AR.clone_path(w.cfg, "ralph_a"); live_c.mkdir(parents=True)
    r = AR.who(w.cfg, d, **dict(ok_kw, cwds=lambda: [(4242, str(live_c))]))
    check(r["exit"] == 0, "a cwd inside the LIVE arm's clone is fine")
    r = AR.who(w.cfg, d, **dict(ok_kw, cwds=lambda: [(4242, str(AR.clone_path(w.cfg, "bench")))]))
    check(r["exit"] == 2, "FORCED (b) a seat in bench while ralph_a is live is a stopped (production) clone -> exit 2")
    # real /proc reader sees a real child
    p = subprocess.Popen(["sleep", "30"], cwd=str(stopped / "sub"))
    try:
        seen = [pid for pid, cwd in AR.proc_cwds() if pid == p.pid and cwd == str((stopped / "sub").resolve())]
        check(seen == [p.pid], "INSTRUMENT: proc_cwds sees a real child process in a stopped clone")
        r = AR.who(w.cfg, d, **dict(ok_kw, cwds=AR.proc_cwds))
        check(r["exit"] == 2, "FORCED (b) with the real /proc reader -> exit 2")
    finally:
        p.kill(); p.wait()
    # (c)
    lk = [{"lane": "steve", "holder": "FOUNDRY", "purpose": "arena trio steve run1: test"}]
    r = AR.who(w.cfg, d, **dict(ok_kw, bridge_locks=lambda: lk)); check(r["exit"] == 4, "FORCED (c) bridge lock names another arm -> exit 4")
    lk = [{"lane": "steve", "holder": "FOUNDRY", "purpose": "arena ralph_a steve run1: test"}]
    r = AR.who(w.cfg, d, **dict(ok_kw, bridge_locks=lambda: lk)); check(r["exit"] == 0, "a lock held by the live arm is fine")
    def lboom(): raise RuntimeError("lock file unreadable")
    r = AR.who(w.cfg, d, **dict(ok_kw, bridge_locks=lboom)); check(r["exit"] == 4, "FORCED (c) unreadable lock fails the check")
    # (d)
    AR.write_json(d.state_file(), {"epoch": d.clock() - 600, "ts": "x", "mode": "ralph_a"})
    r = AR.who(w.cfg, d, **dict(ok_kw, events=lambda root, a, ts: 2 if a == "trio" else 0))
    check(r["exit"] == 8 and r["checks"]["d"]["events_since_switch"] == {"trio": 2}, "FORCED (d) stopped arm wrote an event since the switch -> exit 8")
    r = AR.who(w.cfg, d, **dict(ok_kw, pushed=lambda cfg, a, ts: ["refs/remotes/origin/arena/v3c/x"] if a == "v3c" else []))
    check(r["exit"] == 8 and "v3c" in r["checks"]["d"]["pushed_since_switch"], "FORCED (d) stopped arm pushed a ref since the switch -> exit 8")
    # the real event reader: a line after the switch ts counts, before does not, junk counts
    ev = w.arena / "events"; ev.mkdir()
    import datetime as dt
    t0 = d.clock()
    def iso(t): return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (ev / "trio.jsonl").write_text(json.dumps({"ts": iso(t0 - 5000), "event": "pass_start"}) + "\n" + json.dumps({"ts": iso(t0 + 5), "event": "switch"}) + "\n")
    check(AR.events_since(w.arena, "trio", t0 - 600) == 0, "events_since: old event and a switch line do not count")
    with open(ev / "trio.jsonl", "a") as fh:
        fh.write(json.dumps({"ts": iso(t0 + 9), "event": "pass_start"}) + "\n" + "garbage\n")
    check(AR.events_since(w.arena, "trio", t0 - 600) == 2, "FORCED events_since counts a post-switch event and an unreadable line")
    r = AR.who(w.cfg, d, bridge_locks=lambda: [], cwds=lambda: [(1, "/")], pushed=lambda *a: [])
    check(r["exit"] == 8, "FORCED (d) through the real event reader -> exit 8")
    # combinations and the cli exit code
    w.state.write_text(json.dumps({"active": []}))
    r = AR.who(w.cfg, d, **dict(ok_kw, bridge_locks=lambda: lk[:0] + [{"purpose": "arena trio s r: x"}], events=lambda *a: 1))
    check(r["exit"] == 1 + 4 + 8, "failures combine as a bitmask (%d)" % r["exit"])
    env = dict(os.environ, ARENA_SYSTEMCTL_JSON=json.dumps(w.sc.cmd), ARENA_ARM_TOML=str(w.toml), ARENA_ROOT=str(w.arena))
    w.state.write_text(json.dumps({"active": [AR.target_name("ralph_a"), AR.target_name("trio")]}))
    p = subprocess.run([sys.executable, str(HERE / "arena.py"), "who"], capture_output=True, text=True, env=env)
    check(p.returncode & 1 == 1 and p.returncode != 0, "CLI `arena who` exits non-zero when forced (rc %d)" % p.returncode)
    # an inert cli `who` against a sound shim state: exit has only unrelated bits cleared (a ok); rc without bit 1
    w.state.write_text(json.dumps({"active": [AR.target_name("ralph_a")]}))
    p = subprocess.run([sys.executable, str(HERE / "arena.py"), "who"], capture_output=True, text=True, env=env)
    check(p.returncode & 1 == 0, "CLI `arena who` check (a) passes through the env shim when sound (rc %d)" % p.returncode)


def t_push():
    w = World("push", mode="ralph_a", active=("ralph_a",))
    for a in ("ralph_a", "ralph_c", "bench", "foundry"):
        w.clone(a)
    plan = INS.plan_hooks(w.cfg, str(w.toml))
    INS.apply_plan(plan, True, out=lambda m: None)
    envp = dict(GENV, ARENA_ROOT=str(w.arena), ARENA_ARM_TOML=str(w.toml))
    def push(arm, refspec, *flags):
        c = AR.clone_path(w.cfg, arm)
        return subprocess.run(["git", "-C", str(c), "push", "-q"] + list(flags) + ["origin", refspec], capture_output=True, text=True, env=envp)
    ca = AR.clone_path(w.cfg, "ralph_a")
    git(ca, "checkout", "-q", "-b", "arena/ralph_a/b"); (ca / "x").write_text("1"); git(ca, "add", "x"); git(ca, "commit", "-qm", "b")
    r = push("ralph_a", "arena/ralph_a/b"); check(r.returncode == 0, "live arm pushes arena/ralph_a/b (hook allows) %s" % r.stderr[-120:])
    alarms = w.arena / "alarms" / "arena.jsonl"
    check(not alarms.exists(), "no alarm for an allowed push")
    r = push("ralph_a", "HEAD:refs/heads/main"); check(r.returncode != 0 and "outside refs/heads/arena/ralph_a/" in r.stderr, "FORCED live arm pushing main is refused")
    r = push("ralph_a", "arena/ralph_a/b:refs/heads/arena/trio/steal"); check(r.returncode != 0, "FORCED live arm pushing into another arm's namespace is refused")
    r = push("ralph_a", ":arena/ralph_a/a"); check(r.returncode != 0 and "deleting" in r.stderr, "FORCED deleting an arena branch is refused")
    n0 = len(alarms.read_text().splitlines()) if alarms.exists() else 0
    check(n0 >= 3, "refusals are alarmed too (%d)" % n0)
    # stopped arm: ralph_c while ralph_a is live
    cc = AR.clone_path(w.cfg, "ralph_c")
    git(cc, "checkout", "-q", "-b", "arena/ralph_c/b"); (cc / "x").write_text("1"); git(cc, "add", "x"); git(cc, "commit", "-qm", "b")
    r = push("ralph_c", "arena/ralph_c/b")
    recs = [json.loads(l) for l in alarms.read_text().splitlines()]
    check(r.returncode != 0 and "STOPPED" in r.stderr, "FORCED a push from a STOPPED arm is refused")
    check(recs[-1]["kind"] == "PUSH_REFUSED" and recs[-1]["arm"] == "ralph_c" and "STOPPED" in recs[-1]["reasons"][0] and len(recs) > n0, "...and ALARMED in the file sink")
    heads = git(w.remotes["ralph_c"], "branch", "--list", "arena/ralph_c/b").stdout.strip()
    check(heads == "", "...and the remote never got the ref")
    # fake sink, in-process
    got = []
    rc = AR.prepush("ralph_c", "refs/heads/arena/ralph_c/b %s refs/heads/arena/ralph_c/b %s\n" % ("a" * 40, "0" * 40), w.toml,
                    sink=lambda kind, **f: got.append((kind, f)), deps=w.deps())
    check(rc == 1 and got and got[0][0] == "PUSH_REFUSED" and got[0][1]["arm"] == "ralph_c", "fake alarm sink receives the stopped-arm refusal")
    got.clear()
    rc = AR.prepush("ralph_a", "refs/heads/arena/ralph_a/z %s refs/heads/arena/ralph_a/z %s\n" % ("a" * 40, "0" * 40), w.toml, sink=lambda k, **f: got.append(k), deps=w.deps())
    check(rc == 0 and not got, "in-process: the live arm's own ref passes with no alarm")
    # switch the mode: the former live arm is now stopped
    AR.set_mode(w.toml, "ralph_c")
    git(ca, "checkout", "-q", "arena/ralph_a/b"); (ca / "y").write_text("1"); git(ca, "add", "y"); git(ca, "commit", "-qm", "c")
    r = push("ralph_a", "arena/ralph_a/b"); check(r.returncode != 0 and "STOPPED" in r.stderr, "FORCED after the mode change the old arm is refused")
    r = push("ralph_c", "arena/ralph_c/b"); check(r.returncode == 0, "...and the new live arm pushes")
    # unreadable arm.toml fails closed
    got.clear()
    rc = AR.prepush("ralph_c", "refs/heads/arena/ralph_c/b %s refs/heads/arena/ralph_c/b %s\n" % ("a" * 40, "b" * 40), TMP / "no.toml", sink=lambda k, **f: got.append(k), deps=w.deps())
    check(rc == 1 and got == ["PUSH_REFUSED"], "FORCED unreadable arm.toml refuses and alarms (fail closed)")
    # production clones
    AR.set_mode(w.toml, "production")
    cb = AR.clone_path(w.cfg, "bench")
    (cb / "z").write_text("1"); git(cb, "add", "z"); git(cb, "commit", "-qm", "z")
    r = push("bench", "main"); check(r.returncode == 0, "production mode: bench pushes main")
    r = push("bench", "main:refs/heads/arena/ralph_a/x"); check(r.returncode != 0 and "arena ref" in r.stderr, "FORCED a production clone never pushes arena refs")
    AR.set_mode(w.toml, "ralph_a")
    (cb / "z2").write_text("1"); git(cb, "add", "z2"); git(cb, "commit", "-qm", "z2")
    r = push("bench", "main"); check(r.returncode != 0 and "STOPPED" in r.stderr, "FORCED a production clone is refused while an arena arm is the live mode")
    hook = (AR.clone_path(w.cfg, "ralph_a") / ".git" / "hooks" / "pre-push")
    check(os.access(hook, os.X_OK) and 'prepush --arm "ralph_a"' in hook.read_text(), "installed hook is executable and names its arm")


def t_installer():
    w = World("inst", active=())
    ud = TMP / "inst_units"
    before = snapshot(REAL_UNIT_DIR)
    plan = INS.plan_units(w.cfg, ud)
    lines = []
    INS.apply_plan(plan, False, out=lines.append)
    check(not ud.exists() and any("dry run" in l for l in lines), "dry run writes nothing")
    r = subprocess.run([sys.executable, str(HERE / "arena_install.py"), "units", "--unit-dir", str(ud), "--arm-toml", str(w.toml)], capture_output=True, text=True)
    check(r.returncode == 0 and not ud.exists() and "would write" in r.stdout, "CLI without --apply writes nothing (rc %d)" % r.returncode)
    r = subprocess.run([sys.executable, str(HERE / "arena_install.py"), "hooks", "--arm-toml", str(w.toml)], capture_output=True, text=True)
    check(r.returncode == 0 and "would write" in r.stdout and not (AR.clone_path(w.cfg, "bench") / ".git").exists(), "hooks CLI without --apply writes nothing")
    INS.apply_plan(plan, True, out=lambda m: None)
    check(ud.exists() and AR.check_graph(AR.read_unit_dir(ud)) == [], "--apply (into a temp dir) writes units whose graph is sound")
    dup = dict(w.cfg, units=dict(w.cfg["units"], trio=["rm-ralph-loop@a.service"]))
    try:
        INS.plan_units(dup, ud); ok = False
    except AR.SwitchError:
        ok = True
    check(ok, "FORCED a unit listed in two arms refuses the plan")
    check(snapshot(REAL_UNIT_DIR) == before, "the real user unit dir was not touched")
    check(Path(AR.TEMPLATES, "arm.toml.template").exists() and not (REAL_UNIT_DIR / "rm-arm-trio.target").exists(), "template is in the repo, no real arm target installed")


def t_ops_watch():
    import ops_watch as OW
    rules = OW.load_rules()
    tg = [t for t in rules["targets"] if t["key"] == "arena.two_live"]
    check(len(tg) == 1 and tg[0]["tag"] == "ARENA_TWO_LIVE" and tg[0]["alarm"] and tg[0]["op"] == ">" and tg[0]["value"] == 0, "ARENA_TWO_LIVE rule is in ops_watch_rules.json")
    check("arena" in OW.COLLECTORS and "arena" in OW.ORDER, "the arena collector is registered")
    w = World("ow", active=("ralph_a",))
    env_old = {k: os.environ.get(k) for k in ("ARENA_SYSTEMCTL_JSON", "ARENA_ARM_TOML", "ARENA_ROOT")}
    os.environ.update(ARENA_SYSTEMCTL_JSON=json.dumps(w.sc.cmd), ARENA_ARM_TOML=str(w.toml), ARENA_ROOT=str(w.arena))
    try:
        # sound except the real (b)/(c) readers: patch them to quiet fixtures
        orig = (AR.proc_cwds, AR.default_bridge_locks)
        AR.proc_cwds = lambda *a: []; AR.default_bridge_locks = lambda: []
        pts = OW.COLLECTORS["arena"](0, rules, {})
        check(pts["arena.two_live"]["m"] == "MEASURED" and pts["arena.two_live"]["v"] == 0, "collector: MEASURED 0 when one arm is live")
        check(OW.target_state(pts, rules).get("ARENA_TWO_LIVE:arena.two_live") is False, "rule: not crossed at 0")
        w.state.write_text(json.dumps({"active": [AR.target_name("ralph_a"), AR.target_name("trio")]}))
        pts = OW.COLLECTORS["arena"](0, rules, {})
        check(pts["arena.two_live"]["v"] == 1, "FORCED two live targets -> collector reads 1")
        check(OW.target_state(pts, rules).get("ARENA_TWO_LIVE:arena.two_live") is True, "FORCED rule crossed -> ARENA_TWO_LIVE alarm")
        AR.proc_cwds, AR.default_bridge_locks = orig
        w.toml.rename(w.toml.with_suffix(".gone"))
        pts = OW.COLLECTORS["arena"](0, rules, {})
        check(pts["arena.two_live"]["m"] == "UNMEASURED" and OW.target_state(pts, rules).get("ARENA_TWO_LIVE:arena.two_live") is None,
              "no arm.toml -> UNMEASURED, rule holds (None), never 0")
        w.toml.with_suffix(".gone").rename(w.toml)
        w.toml.write_text("mode = [")
        r = AR.ops_two_live(w.toml, w.deps())
        check(r["value"] == 16, "FORCED unreadable arm.toml -> 16")
    finally:
        for k, v in env_old.items():
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v


def main():
    try:
        for t in (t_two_targets, t_graph, t_switch_production, t_switch_forced, t_who, t_push, t_installer, t_ops_watch):
            print("== %s" % t.__name__)
            t()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("\nFAILS: %d" % len(FAILS))
    for f in FAILS:
        print("  - " + f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
