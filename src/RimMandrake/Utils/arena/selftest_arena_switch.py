#!/usr/bin/env python3
"""selftest_arena_switch.py - arena.py (the switch), each criterion proven by FORCED FAILURE.

ARENA_SWITCH_BUILD_ONE_ARM_LIVE_ONLY. Nothing here starts systemd, dbus, a private manager or touches a cgroup or a real
unit: every `systemctl` is src/RimMandrake/Utils/arena/fixtures/fake_systemctl.py, which emulates a transactional
`start A B` (fails on conflicting jobs) and a sequential `start B` (stops A through Conflicts=), reading the RENDERED
unit files from a temp dir. The real user unit dir, the real seats, arm.toml, the real ModsConfig.xml and the real
event log are never read or written; git work happens in throwaway repos under a temp dir.

  fix round 1    (switch_test_report.md) hooks_path: a round-0 .git/hooks install under core.hooksPath lets a stopped
                 production clone push unalarmed (RED) and who (e) flags it; the core.hooksPath install refuses+alarms,
                 chains owner hooks, honours [production] scope, alarms PUSH_HOOK_CRASH, never executes $(...) in the
                 toml path. trial_and_members: v3+trial together, lane-tagged locks, untagged/swapped flagged, enabled
                 foreign member at boot -> who (a), switch disables it and never enables. clone_dirt: detached, stash,
                 dirty, untracked, submodule, non-origin, missing; --allow-dirty-untracked recorded. switch_safety:
                 lock, already-live no-op/--force, interrupt cleans STOP, stale STOP/idle -> who (f), exit 16, rollback.
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
        """the installer's own unit plan (targets incl. trial, member drop-ins, the replay unit) into the temp dir"""
        cfg = cfg or self.cfg
        for p, t in INS.plan_units(cfg, self.units):
            if skip_conflicts and p.name.endswith(".target"):
                t = "\n".join(l for l in t.splitlines() if not l.startswith("Conflicts=")) + "\n"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(t)

    def alarm_file(self):
        return self.arena / "alarms" / "arena.jsonl"

    def install_hooks(self, clone, arm, name, arena_py=None):
        """the installer's hook plan for ONE temp clone (core.hooksPath -> arena-hooks), applied (temp world only)"""
        files, hp, _ = AR.plan_clone_hooks(clone, arm, name, str(self.toml), str(self.alarm_file()), arena_py)
        INS.apply_plan([("file", p, x) for p, x in files] + [("hookspath", clone, hp)], True, out=lambda m: None)

    def active(self):
        return sorted(json.loads(self.state.read_text())["active"])

    def clone(self, arm, hooks=True):
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
        if hooks:
            self.install_hooks(c, "production" if arm in AR.PROD_CLONES else arm, arm)
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
        d.bridge_locks = lambda: []          # never the real ledger
        d.modlist_restore = lambda: {"active": 2}
        d.t = t
        for k, v in over.items():
            setattr(d, k, v)
        return d

    events = None

    def signer_ok(self, arm, event, **kw):
        self.events = (self.events or []) + [dict(arm=arm, event=event, **kw)]
        return dict(arm=arm, event=event, **kw)


def idle_status(w, arm, state, epoch=1_800_000_000.0):
    p = w.arena / "status" / ("%s.json" % arm)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"state": state, "epoch": epoch}))


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
    r3 = AR.switch("trial", w.toml, w.deps())
    check(w.active() == sorted([AR.target_name("v3"), "rm-dispatcher.service", AR.target_name("trial"), AR.REPLAY_UNIT]),
          "trial: v3 (the control) AND rm-arm-trial.target with the replay runner are live (%s)" % w.active())
    check(r3["who"]["exit"] == 0, "trial: arena who is 0 in a correct trial (%s)" % r3["who"]["exit"])
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
    check(not (w.arena / "STOP.ralph_a").exists(), "...the STOP the refused switch wrote is removed (the live arm resumes)")
    last = json.loads((w.arena / "switch_last.json").read_text())
    check(last["result"] == "refused" and last["resumed"] == ["ralph_a"], "...and switch_last.json records refused + resumed (%s)" % last.get("result"))
    git(c, "push", "-q", "origin", "arena/ralph_a/a")
    AR.switch("trio", w.toml, w.deps(unpushed=AR.unpushed))
    check(AR.target_name("trio") in w.active(), "after pushing, the same switch goes through")
    # real unpushed(): no commit outside remotes -> []; git error raises
    check(AR.unpushed(c) == [] and [i["kind"] for i in AR.unpushed(TMP / "nogit")] == ["missing"],
          "unpushed() is empty for a clean clone; a MISSING clone is reported (not passed)")
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
    check("arena.py" in L.ENTRYPOINTS, "arena_eventlog.ENTRYPOINTS allows arena.py (the real signer can sign switch events)")
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
    plan = INS.plan_hooks(w.cfg, str(w.toml), alarm_file=str(w.alarm_file()))
    INS.apply_plan(plan, True, out=lambda m: None)      # a RE-install over World.clone's: idempotent
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
    check(rc == AR.PREPUSH_REFUSED and got and got[0][0] == "PUSH_REFUSED" and got[0][1]["arm"] == "ralph_c", "fake alarm sink receives the stopped-arm refusal")
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
    check(rc == AR.PREPUSH_REFUSED and got == ["PUSH_REFUSED"], "FORCED unreadable arm.toml refuses and alarms (fail closed)")
    # production clones
    AR.set_mode(w.toml, "production")
    cb = AR.clone_path(w.cfg, "bench")
    (cb / "z").write_text("1"); git(cb, "add", "z"); git(cb, "commit", "-qm", "z")
    r = push("bench", "main"); check(r.returncode == 0, "production mode: bench pushes main")
    r = push("bench", "main:refs/heads/arena/ralph_a/x"); check(r.returncode != 0 and "arena ref" in r.stderr, "FORCED a production clone never pushes arena refs")
    AR.set_mode(w.toml, "ralph_a")
    (cb / "z2").write_text("1"); git(cb, "add", "z2"); git(cb, "commit", "-qm", "z2")
    r = push("bench", "main"); check(r.returncode != 0 and "STOPPED" in r.stderr, "FORCED a production clone is refused while an arena arm is the live mode")
    hook = (AR.clone_path(w.cfg, "ralph_a") / ".git" / AR.HOOKS_DIRNAME / "pre-push")
    check(os.access(hook, os.X_OK) and "prepush --arm 'ralph_a'" in hook.read_text(), "installed hook is executable and names its arm")


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
    cb = w.clone("bench", hooks=False)
    r = subprocess.run([sys.executable, str(HERE / "arena_install.py"), "hooks", "--arm-toml", str(w.toml)], capture_output=True, text=True)
    hp = git(cb, "config", "--local", "--get", "core.hooksPath", check_rc=False).stdout.strip()
    check(r.returncode == 0 and "would write" in r.stdout and "would run" in r.stdout and "skip ralph_a" in r.stdout
          and not (cb / ".git" / AR.HOOKS_DIRNAME).exists() and hp == "", "hooks CLI without --apply writes nothing, sets no hooksPath, reports missing clones")
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


# ------------------------------------------------------------------ fix round 1 (switch_test_report.md H1-H4, M1-M6, L1-L5)
def sc_state(w):
    return json.loads(w.state.read_text())


def sc_set(w, **kv):
    s = sc_state(w); s.update(kv); w.state.write_text(json.dumps(s))


def commit(c, name, msg=None):
    (c / name).write_text(name); git(c, "add", name); git(c, "commit", "-qm", msg or name)


def who_quiet(w, d, **over):
    kw = dict(bridge_locks=lambda: [], cwds=lambda: [(1, "/")], events=lambda *a: 0, pushed=lambda *a: [])
    kw.update(over)
    return AR.who(AR.load_config(w.toml), d, **kw)


def t_hooks_path():
    """H1: bench/foundry set core.hooksPath, so a hook in .git/hooks never runs. L2/L3: crash alarm, quoting. M5 scope."""
    w = World("hp", mode="ralph_a", active=("ralph_a",))
    owner = w.root / "owner_githooks"; owner.mkdir()
    marks = w.root / "marks"; marks.mkdir()
    for n in ("pre-commit", "pre-push"):
        (owner / n).write_text("#!/bin/sh\ncat > /dev/null\necho ran >> %s\n[ -e %s ] && exit 1\nexit 0\n"
                               % (AR.sh_quote(str(marks / n)), AR.sh_quote(str(marks / (n + ".fail")))))
        os.chmod(owner / n, 0o755)
    cb = w.clone("bench", hooks=False)
    git(cb, "config", "--local", "core.hooksPath", str(owner))       # what bench/foundry really do
    # RED: the round-0 install (.git/hooks/pre-push) is bypassed - a STOPPED production clone pushes main
    legacy = cb / ".git" / "hooks" / "pre-push"
    legacy.write_text(AR.render_hook("production", str(w.toml), clone="bench", alarm_file=str(w.alarm_file())))
    os.chmod(legacy, 0o755)
    commit(cb, "r1")
    r = git(cb, "push", "-q", "origin", "main", check_rc=False)
    check(r.returncode == 0 and not w.alarm_file().exists(),
          "RED (round-0 install): with core.hooksPath set, .git/hooks/pre-push never runs: a stopped production clone pushes, unalarmed")
    d = w.deps()
    e = who_quiet(w, d)
    check(e["exit"] & 32 and any("bench" in p and "never runs" in p for p in e["checks"]["e"]["problems"]),
          "FORCED who (e): bench's effective hooks dir is not the arena dir -> bit 32 (%s)" % e["exit"])
    # GREEN: install through core.hooksPath, chaining the owner's hooks
    w.install_hooks(cb, "production", "bench")
    eff, arena_dir = AR.hook_dirs(cb)
    check(eff == arena_dir and (arena_dir / "CHAIN_FROM").read_text().strip() == str(owner),
          "install points core.hooksPath at arena-hooks and records the owner's dir in CHAIN_FROM")
    check((owner / "pre-push").read_text().startswith("#!/bin/sh\ncat") and (arena_dir / "pre-commit").exists(),
          "the owner's hooks are untouched and chained (wrapper for pre-commit)")
    for m in marks.iterdir():
        m.unlink()                                                   # the RED push ran the owner hooks
    commit(cb, "r2")
    check((marks / "pre-commit").exists(), "the owner's pre-commit still runs through the wrapper")
    r = git(cb, "push", "-q", "origin", "main", check_rc=False)
    recs = [json.loads(l) for l in w.alarm_file().read_text().splitlines()] if w.alarm_file().exists() else []
    check(r.returncode != 0 and "STOPPED" in r.stderr and recs and recs[-1]["kind"] == "PUSH_REFUSED" and recs[-1]["clone"] == "bench",
          "GREEN: the stopped production clone's push is refused AND alarmed through core.hooksPath")
    check(not (marks / "pre-push").exists(), "...and the chained owner pre-push did not run for a refused push")
    check(who_quiet(w, d)["checks"]["e"]["ok"], "who (e) passes once installed")
    AR.set_mode(w.toml, "production")
    r = git(cb, "push", "-q", "origin", "main", check_rc=False)
    check(r.returncode == 0 and (marks / "pre-push").exists(), "production mode: bench pushes and its own pre-push ran after the arena check")
    (marks / "pre-push.fail").write_text("1"); commit(cb, "r3")
    r = git(cb, "push", "-q", "origin", "main", check_rc=False)
    check(r.returncode != 0, "FORCED the chained owner pre-push failing still refuses the push")
    (marks / "pre-push.fail").unlink()
    snap = {p.name: p.read_text() for p in arena_dir.iterdir()}
    w.install_hooks(cb, "production", "bench")
    check({p.name: p.read_text() for p in arena_dir.iterdir()} == snap, "re-install is idempotent (CHAIN_FROM kept, no self-chain)")
    # who (e) forced: an edited hook, a repointed hooksPath
    pp = arena_dir / "pre-push"; keep = pp.read_text()
    pp.write_text(keep + "exit 0\n")
    check(who_quiet(w, d)["exit"] & 32, "FORCED who (e): an edited arena pre-push is flagged")
    pp.write_text(keep)
    git(cb, "config", "--local", "core.hooksPath", str(owner))
    check(who_quiet(w, d)["exit"] & 32, "FORCED who (e): core.hooksPath repointed away from arena-hooks is flagged")
    git(cb, "config", "--local", "core.hooksPath", str(arena_dir))
    (owner / "commit-msg").write_text("#!/bin/sh\nexit 0\n"); os.chmod(owner / "commit-msg", 0o755)
    check(who_quiet(w, d)["exit"] & 32, "FORCED who (e): a new owner hook with no wrapper is flagged (it would stop running)")
    (owner / "commit-msg").unlink()
    # M5: [production] scope honoured by the hook
    w.toml.write_text(w.toml.read_text().replace('scope = ["bench", "foundry"]', 'scope = ["foundry"]'))
    commit(cb, "r4")
    r = git(cb, "push", "-q", "origin", "main", check_rc=False)
    check(r.returncode != 0 and "outside [production] scope" in r.stderr, "FORCED production mode, bench outside scope: its push is refused")
    cfg = AR.load_config(w.toml)
    check(AR.prepush_verdict(cfg, "production", [], clone="foundry") == [], "...foundry (in scope) may push")
    w.toml.write_text(w.toml.read_text().replace('scope = ["foundry"]', 'scope = ["bench", "foundry"]'))
    # L2: a crashing arena check refuses AND alarms PUSH_HOOK_CRASH
    cf = w.clone("foundry", hooks=False)
    w.install_hooks(cf, "production", "foundry", arena_py=str(w.root / "no such dir" / "arena.py"))
    commit(cf, "c1")
    n0 = len(w.alarm_file().read_text().splitlines())
    r = git(cf, "push", "-q", "origin", "main", check_rc=False)
    recs = [json.loads(l) for l in w.alarm_file().read_text().splitlines()]
    check(r.returncode != 0 and len(recs) == n0 + 1 and recs[-1]["kind"] == "PUSH_HOOK_CRASH" and recs[-1]["clone"] == "foundry",
          "FORCED hook crash (arena.py missing): push refused AND PUSH_HOOK_CRASH alarmed (%s)" % recs[-1:])
    check(AR.alarms_since(w.alarm_file(), 0) == len(recs), "ops_watch's reader counts every alarm line")
    # L3: a hostile arm.toml path is a literal string in the hook
    inj = w.root / "inj $(touch PWNED) `touch PWNED2` 'q\"" / "arm.toml"
    inj.parent.mkdir()
    inj.write_text(w.toml.read_text())
    ca = w.clone("ralph_a", hooks=False)
    AR.set_mode(inj, "ralph_a")
    files, hp, _ = AR.plan_clone_hooks(ca, "ralph_a", "ralph_a", str(inj), str(w.alarm_file()))
    INS.apply_plan([("file", p, x) for p, x in files] + [("hookspath", ca, hp)], True, out=lambda m: None)
    git(ca, "checkout", "-q", "-b", "arena/ralph_a/inj"); commit(ca, "i1")
    r = git(ca, "push", "-q", "origin", "arena/ralph_a/inj", check_rc=False)
    pwned = [str(p) for p in TMP.rglob("PWNED*")] + [p for p in ("PWNED", "PWNED2") if os.path.exists(p)]
    check(r.returncode == 0 and not pwned, "a path holding $(...), backticks and quotes is passed verbatim, nothing executes (%s %s)"
          % (r.returncode, pwned))
    AR.set_mode(inj, "trio")
    r = git(ca, "push", "-q", "origin", "arena/ralph_a/inj:arena/ralph_a/inj2", check_rc=False)
    check(r.returncode != 0 and "STOPPED" in r.stderr, "...and the hook really read THAT toml (mode trio there -> refused)")
    try:
        AR.render_replay_unit(str(inj)); ok = False
    except AR.SwitchError:
        ok = True
    check(ok, "FORCED the replay unit refuses a path it could not quote in a unit file")


def t_trial_and_members():
    """H3 trial unit set; H4 member units of other arms (enabled timers at boot); M6 per-lane, untagged locks."""
    w = World("tri", mode="v3", active=("v3",))
    base = AR.read_unit_dir(w.units)
    check(AR.REPLAY_UNIT in base and AR.check_graph(base) == [], "trial target + replay unit rendered, graph sound")
    bad = dict(base); bad["rm-arm-trial.target"] += "Conflicts=rm-arm-v3.target\n"
    check(any("must NOT conflict" in p for p in AR.check_graph(bad)), "FORCED v3/trial rendered as conflicting is reported")
    rc, out = w.sc.run("start", AR.target_name("v3"), AR.target_name("trial"))
    check(rc == 0 and AR.target_name("trial") in w.active() and AR.REPLAY_UNIT in w.active(), "v3 + trial start together (%s)" % out.strip()[:80])
    rc, out = w.sc.run("start", AR.target_name("trial"), AR.target_name("trio"))
    check(rc != 0 and "conflicting jobs" in out, "trial still conflicts with every other arm")
    w.sc.run("stop", AR.target_name("trial"))
    for a in ("ralph_a", "trio", "bench", "foundry"):
        w.clone(a)
    AR.set_mode(w.toml, "v3")
    r = AR.switch("trial", w.toml, w.deps())
    check(r["who"]["exit"] == 0 and sorted(r["event"]["detail"]["targets"]) == [AR.target_name("trial"), AR.target_name("v3")],
          "switch v3 -> trial: who 0, event names both targets")
    cfg = AR.load_config(w.toml); d = w.deps()
    good = [{"lane": "steve", "purpose": "arena trio steve r1: x"}, {"lane": "archmagi", "purpose": "arena ralph_c archmagi r1: x"}]
    check(who_quiet(w, d, bridge_locks=lambda: good)["exit"] == 0, "trial: lane locks tagged with the lane's own arm pass (c)")
    swapped = [{"lane": "steve", "purpose": "arena ralph_c steve r1: x"}]
    check(who_quiet(w, d, bridge_locks=lambda: swapped)["exit"] == 4, "FORCED trial: steve lane holding ralph_c's lock -> 4")
    check(who_quiet(w, d, bridge_locks=lambda: [{"lane": "steve", "purpose": "testq job 9"}])["exit"] == 4,
          "FORCED trial: an UNTAGGED lock is unknown -> 4")
    check(who_quiet(w, d, events=lambda root, a, ts: 3 if a in ("ralph_a", "v3c") else 0)["exit"] == 0,
          "trial: the replay arms' events are not a stopped arm's (d)")
    check(who_quiet(w, d, events=lambda root, a, ts: 1 if a == "production" else 0)["exit"] == 8, "FORCED trial: a production event -> 8")
    AR.set_mode(w.toml, "ralph_a")
    check(AR.lock_problems(AR.load_config(w.toml), [{"lane": "steve", "purpose": "x"}]), "FORCED ralph_a mode: untagged lock flagged")
    check(AR.lock_problems(dict(cfg, mode="v3"), [{"lane": "steve", "purpose": "x"}]) == [], "v3 mode: an untagged (v3's own) lock is fine")
    AR.set_mode(w.toml, "trial")
    # default reader: one lock per lane from the ledger + the shared file; unreadable shared file raises
    import types
    shared = w.root / "shared_bridge.json"
    fake = types.SimpleNamespace(DEFAULT_BRIDGE_HOST="archmagi", shared_bridge_path=lambda: str(shared),
                                 replay=lambda: types.SimpleNamespace(bridge_hosts={
                                     "stevedesktop": {"holder": "BENCH", "purpose": "arena trio steve r: a"},
                                     "archmagi": {"holder": "FOUNDRY", "purpose": "arena ralph_c archmagi r: b"},
                                     "idlehost": {"holder": None}}))
    old = sys.modules.get("model"); sys.modules["model"] = fake
    try:
        shared.write_text(json.dumps({"holder": "FOUNDRY", "purpose": "arena ralph_c archmagi r: b"}))
        L = AR.default_bridge_locks()
        check(sorted((l["lane"], l["source"]) for l in L) == [("archmagi", "ledger"), ("archmagi", "shared"), ("steve", "ledger")],
              "default_bridge_locks reads one lock per lane plus the shared file (%s)" % [(l["lane"], l["source"]) for l in L])
        shared.write_text("{corrupt")
        try:
            AR.default_bridge_locks(); ok = False
        except AR.SwitchError:
            ok = True
        check(ok, "FORCED an unreadable shared lock file raises (unmeasured, not 'no lock')")
    finally:
        if old is None: sys.modules.pop("model", None)
        else: sys.modules["model"] = old
    r = subprocess.run([sys.executable, str(HERE / "arena.py"), "trial-runner"], capture_output=True, text=True)
    check(r.returncode == 3 and "OWED" in r.stderr, "trial-runner says the replay loop is OWED (exit 3), never pretends")
    # H4: enabled member timers of another arm come up at boot beside the live target
    w = World("mem", mode="ralph_a", active=("ralph_a",))
    for a in ("ralph_a", "trio", "bench", "foundry"):
        w.clone(a)
    sc_set(w, enabled=[AR.target_name("ralph_a"), "rm-dispatcher.service"])
    w.sc.run("boot")
    d = w.deps()
    r = who_quiet(w, d)
    check("rm-dispatcher.service" in w.active() and r["exit"] & 1 and r["checks"]["a"]["foreign_members"][0]["unit"] == "rm-dispatcher.service",
          "FORCED boot with v3's member enabled: it runs beside ralph_a and who (a) flags it (%s)" % r["exit"])
    log0 = len(sc_state(w)["log"])
    r = AR.switch("trio", w.toml, d)
    s = sc_state(w)
    check("rm-dispatcher.service" in r["disabled"] and "rm-dispatcher.service" not in s["enabled"]
          and "rm-dispatcher.service" not in s["active"], "switch disables AND stops the other arm's member (%s)" % r["disabled"])
    check(not any(l.startswith("CMD enable") for l in s["log"][log0:]), "switch never enables anything")
    w.sc.run("boot")
    check("rm-dispatcher.service" not in w.active(), "after a reboot the disabled member stays down")
    w.sc.run("start", "rm-dispatcher.service")
    check(who_quiet(w, d)["exit"] & 1, "FORCED a manually started member of a stopped arm -> who (a)")


def t_clone_dirt():
    """M1: everything a stopped clone would strand, plus --allow-dirty-untracked."""
    w = World("dirt", mode="ralph_a", active=("ralph_a",))
    c = w.clone("ralph_a")
    kinds = lambda: sorted({i["kind"] for i in AR.clone_dirt(c)})
    check(kinds() == [], "a clean pushed clone has no dirt")
    (c / "u.txt").write_text("u")
    check(kinds() == ["untracked"], "FORCED untracked file seen")
    (c / "u.txt").unlink(); (c / "f.txt").write_text("changed")
    check(kinds() == ["dirty"], "FORCED uncommitted tracked change seen")
    git(c, "stash", "-q")
    check(kinds() == ["stash"], "FORCED stash seen")
    git(c, "stash", "drop", "-q")
    git(c, "checkout", "-q", "--detach"); commit(c, "det")
    check("detached" in kinds(), "FORCED detached-HEAD commit seen")
    git(c, "checkout", "-q", "arena/ralph_a/a")
    other = w.root / "remotes" / "other.git"; subprocess.run(["git", "init", "-q", "--bare", str(other)], check=True)
    git(c, "remote", "add", "other", str(other)); git(c, "checkout", "-q", "-b", "arena/ralph_a/o"); commit(c, "o")
    git(c, "push", "-q", "--no-verify", "other", "arena/ralph_a/o")
    check(any("arena/ralph_a/o" in i["what"] for i in AR.clone_dirt(c) if i["kind"] == "unpushed"),
          "FORCED a branch pushed only to a non-origin remote is still unpushed")
    git(c, "push", "-q", "origin", "arena/ralph_a/o"); git(c, "branch", "-q", "-D", "arena/ralph_a/o", check_rc=False)
    subprocess.run(["git", "-C", str(c), "checkout", "-q", "arena/ralph_a/a"], capture_output=True)
    git(c, "branch", "-q", "-D", "arena/ralph_a/o")
    sub = w.root / "subsrc"; subprocess.run(["git", "init", "-q", "-b", "main", str(sub)], check=True, env=GENV); commit(sub, "s")
    git(c, "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(sub), "sub"); git(c, "commit", "-qm", "sub")
    git(c, "push", "-q", "origin", "arena/ralph_a/a")
    (c / "sub" / "inner.txt").write_text("x")
    k = AR.clone_dirt(c)
    check(any("submodule" in i["what"] and i["kind"] == "untracked" for i in k), "FORCED untracked file inside a submodule seen (%s)" % [i["what"] for i in k][:3])
    (c / "sub" / "inner.txt").unlink()
    check(AR.clone_dirt(c) == [], "clean again after removing it")
    check([i["kind"] for i in AR.clone_dirt(w.root / "nope")] == ["missing"], "FORCED a missing clone path is dirt (refuse)")
    # the switch: untracked refuses; --allow-dirty-untracked lets it through and records the override
    for a in ("bench", "foundry"):
        w.clone(a)
    idle_status(w, "ralph_a", "idle")
    (c / "scratch.log").write_text("x")
    try:
        AR.switch("trio", w.toml, w.deps(unpushed=AR.clone_dirt)); ok = False; msg = ""
    except AR.Refused as e:
        ok, msg = True, str(e)
    check(ok and "scratch.log" in msg and AR.target_name("ralph_a") in w.active(), "FORCED untracked file in the stopped clone refuses the switch")
    git(c, "stash", "-q", "-u")
    try:
        AR.switch("trio", w.toml, w.deps(unpushed=AR.clone_dirt), allow_dirty_untracked=True); ok = False
    except AR.Refused as e:
        ok = "stash" in str(e)
    check(ok, "FORCED --allow-dirty-untracked does NOT override a stash")
    git(c, "stash", "pop", "-q")
    r = AR.switch("trio", w.toml, w.deps(unpushed=AR.clone_dirt), allow_dirty_untracked=True)
    check(AR.target_name("trio") in w.active() and any("scratch.log" in o for o in r["event"]["detail"]["overrides"]),
          "--allow-dirty-untracked switches and the override is recorded in the switch event")
    # production -> arm with a dirty foundry refuses (4h2)
    w2 = World("dirt2", mode="production", active=("production",))
    for a in ("trio", "bench", "foundry"):
        w2.clone(a)
    (AR.clone_path(w2.cfg, "foundry") / "f.txt").write_text("edit")
    try:
        AR.switch("trio", w2.toml, w2.deps(unpushed=AR.clone_dirt)); ok = False
    except AR.Refused as e:
        ok = "foundry" in str(e)
    check(ok and AR.target_name("production") in w2.active(), "FORCED production -> trio with a dirty foundry refuses")


def t_switch_safety():
    """M2 lock, M3 idempotence, M4 refused/interrupted STOP cleanup + stale STOP/idle, L1 exit 16, L5 rollback record."""
    w = World("safe", mode="ralph_a", active=("ralph_a",))
    for a in ("ralph_a", "trio", "bench", "foundry"):
        w.clone(a)
    idle_status(w, "ralph_a", "idle")
    d = w.deps()
    with AR.switch_lock(d):
        try:
            AR.switch("trio", w.toml, w.deps()); ok = False
        except AR.Refused as e:
            ok = "another arena switch" in str(e)
        check(ok and AR.target_name("ralph_a") in w.active() and w.events is None, "FORCED a second concurrent switch is refused, changes nothing")
        (w.arena / "STOP.ralph_a").write_text("{}")
        check(who_quiet(w, d)["checks"]["f"]["ok"], "a STOP on the live arm while a switch holds the lock is not stale")
    check(who_quiet(w, d)["exit"] == 64, "FORCED who (f): a STOP left on the live arm with no switch running -> 64")
    (w.arena / "STOP.ralph_a").unlink()
    r = AR.switch("ralph_a", w.toml, w.deps())
    check(r.get("already_live") and w.events is None and not (w.arena / "STOP.ralph_a").exists(),
          "switch to the already-live mode is a no-op 'already live' (no STOP, no wait, no event)")
    r = AR.switch("ralph_a", w.toml, w.deps(), force=True)
    check(not r.get("already_live") and w.events and w.events[-1]["detail"].get("force") is True
          and AR.target_name("ralph_a") in w.active(), "--force restarts it and records force")
    # interrupted during the idle wait: our STOP removed, live arm resumes, switch_last says interrupted
    idle_status(w, "ralph_a", "busy")
    d = w.deps()
    def interrupt(s): raise KeyboardInterrupt()
    d.sleep = interrupt
    try:
        AR.switch("trio", w.toml, d); ok = False
    except KeyboardInterrupt:
        ok = True
    last = json.loads((w.arena / "switch_last.json").read_text())
    check(ok and not (w.arena / "STOP.ralph_a").exists() and AR.target_name("ralph_a") in w.active()
          and last["result"] == "interrupted" and who_quiet(w, w.deps())["exit"] == 0,
          "FORCED interrupt during the wait: STOP removed, ralph_a still live, recorded, who 0")
    # stale status: idle from 7 h ago is flagged (f) and does not count as idle now (L4)
    idle_status(w, "ralph_a", "idle", epoch=1_800_000_000.0 - 7 * 3600)
    check(who_quiet(w, w.deps())["exit"] == 64, "FORCED who (f): a live arm 'idle' for 7 h is flagged")
    d = w.deps()
    check(not d.is_idle("ralph_a"), "FORCED a stale idle status is not idle for the switch")
    idle_status(w, "ralph_a", "idle")
    check(d.is_idle("ralph_a") and who_quiet(w, d)["exit"] == 0, "a fresh idle status is idle and not flagged")
    # L5: a start failure is recorded with the steps done and how to recover
    sc_set(w, fail_start=[AR.target_name("trio")])
    try:
        AR.switch("trio", w.toml, w.deps()); ok = False
    except AR.SwitchError:
        ok = True
    last = json.loads((w.arena / "switch_last.json").read_text())
    check(ok and last["result"] == "failed" and "rollback" in last and any("signed" in s for s in last["steps"])
          and last["arm_toml_mode"] == "trio", "FORCED start failure: switch_last.json records steps + rollback (%s)" % last.get("steps"))
    sc_set(w, fail_start=[])
    # L1: corrupt arm.toml -> exit 16, distinguishable from check (a)
    env = dict(os.environ, ARENA_SYSTEMCTL_JSON=json.dumps(w.sc.cmd), ARENA_ARM_TOML=str(w.toml), ARENA_ROOT=str(w.arena))
    w.toml.write_text("mode = [")
    for verb in ("who", "mode"):
        p = subprocess.run([sys.executable, str(HERE / "arena.py"), verb], capture_output=True, text=True, env=env)
        check(p.returncode == AR.EXIT_CONFIG and "Traceback" not in p.stderr, "FORCED corrupt arm.toml: `arena %s` exits 16, no traceback (rc %d)" % (verb, p.returncode))
    # the docstring tells the truth about bypass
    doc = AR.__doc__
    check("SERVER_SIDE_REQUIREMENTS" in doc and "--no-verify" in doc and "unbypassable" in doc, "arena.py states the client-hook limit and the server-side requirement")


def main():
    try:
        for t in (t_two_targets, t_graph, t_switch_production, t_switch_forced, t_who, t_push, t_installer, t_ops_watch,
                  t_hooks_path, t_trial_and_members, t_clone_dirt, t_switch_safety):
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
