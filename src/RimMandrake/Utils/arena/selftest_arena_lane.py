#!/usr/bin/env python3
"""selftest_arena_lane.py — arena_lane.py and ralph_c_runner.py, each requirement proven by FORCED FAILURE, offline.

ARENA_LANE_BUILD_MINIMAL_LIST_ONLY criteria, and the failure planted for each (a FakeDriver stands in for the game,
the bridge and the swap tools; nothing live is touched):
  stale       a result for a superseded sha is refused by record_result and by lane_record; a builder re-publishing
              DURING a run makes that run's result `stale` (nothing written); the current sha is accepted (control)
  dead        a colony with 0 live colonists gives `invalid` with a red canary and an `invalid` event, the proof is
              never run, and the candidate stays pending; a live colony passes (control)
  full        a `full` profile is refused at publish and at Lane.reload, before the game is stopped or a list swapped
  loadtime    a minimal+deps reload records its MEASURED launch-to-ready seconds in the reload event and load_times
  restore     the owner's list is restored on release, its minutes charged to the arm, also when the body raised;
              a failed restore is loud (RestoreFailed) and the release event says error
plus: C# deploy while the game runs, a flyer's flight and the canonical save are refused; his presence is never
read (owner 2026-10-30): owner_playing in the config, an owner-return probe answering "back" before, during the launch or
during the proof change nothing and the probe is never called; every canary
check (stale log, wrong/unpinned version, wrong deployed sha, mod not active, unreadable facts) turns it red; a proof
exit code other than 0/1 is invalid; 3 failed rounds park an item; an event outside the schema is refused.
t_review replays every confirmed finding of the two blind reviews (Transient-free: ClaudeWork arena_lane_build/review
a1.md, a2.md) as a forced failure: post-proof death, crash vs assertion, tier cap, swap marker, claims, requeue.
Writes only under a temp dir (ARENA_ROOT points there).
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="selftest_arena_lane_"))
os.environ["ARENA_ROOT"] = str(TMP / "arena")
import arena_lane as L  # noqa: E402
import ralph_c_runner as R  # noqa: E402

FAILS = []
SHA_A = "a" * 40
SHA_B = "b" * 40
CANON = "CANON_START_SAVE"
L.canonical_saves = lambda: {CANON}          # canon.yml is read live; the selftest pins its own name
CANON_WORLD = {"name": "Canon'World", "seed": "canonseed"}
REAL_CANONICAL_WORLDS = L.canonical_worlds
L.canonical_worlds = lambda: [dict(CANON_WORLD)]   # the .rws is read live; the selftest pins its own world


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def raises(exc, fn, *a, **k):
    try:
        fn(*a, **k)
    except exc as e:
        return str(e)
    return None


class FakeDriver:
    def __init__(self, colonists=3, version="1.6.4633 rev1", running=False, launch_s=22.0, proof_rc=0,
                 take_ok=True, restore_ok=True, owner_back=False, on_proof=None, proof_txt=None):
        self.t = 1000.0
        self.colonists, self.version, self.running, self.launch_s = colonists, version, running, launch_s
        self.proof_rc, self.take_ok, self.restore_ok, self.owner_back = proof_rc, take_ok, restore_ok, owner_back
        self.on_proof, self.proof_txt = on_proof, proof_txt
        self.stop_sticks = False        # the game is still up after stop_game
        self.stop_raises = None         # stop_game raises this
        self.dirty = []                 # clone_dirty answer
        self.calls = []
        self.head = {}
        self.log_mtime = 0.0
        self.active = ["ludeon.rimworld"]
        self.facts_override = {}
        self.mods_restore_ok = True

    def clock(self):
        return self.t

    def bridge_take(self, host, purpose, idle_ok):
        self.calls.append(("take", host, idle_ok))
        return self.take_ok, "taken" if self.take_ok else "held by OTHER (awake)"

    def bridge_release(self, host):
        self.calls.append(("release", host))
        return True, "released"

    def game_running(self):
        return self.running

    def stop_game(self):
        self.calls.append(("stop",))
        if self.stop_raises:
            raise self.stop_raises
        if not self.stop_sticks:
            self.running = False

    TIERS = {"slime": ["ludeon.rimworld", "mandrake.rm.slime"],
             "everything": ["ludeon.rimworld"] + ["owner.mod%d" % i for i in range(200)]}

    def known_tiers(self):
        return set(self.TIERS)

    def expected_active(self, profile, tier):
        return ["ludeon.rimworld"] if profile == "minimal" else self.TIERS[tier]

    def clone_dirty(self, clone):
        return list(self.dirty)

    def apply_minimal(self):
        self.calls.append(("minimal",))
        return True, "swapped"

    def apply_tier(self, tier):
        self.calls.append(("tier", tier))
        return True, "wrote"

    def restore_modlist(self):
        self.calls.append(("restore",))
        self.t += 30.0
        return self.restore_ok, "restored" if self.restore_ok else "FULL.LATEST missing"

    def clone_head(self, clone):
        return self.head.get(clone)

    def restore_mods(self, mods, clone):
        self.calls.append(("restore_mods", tuple(mods), clone, self.running))
        self.t += 10.0
        return self.mods_restore_ok, "main redeployed" if self.mods_restore_ok else "deploy rc 1", "c" * 40

    def deploy(self, mod, clone):
        self.calls.append(("deploy", mod, self.running))
        self.active.append("mandrake.rm.%s" % mod.lower())
        return True, "deployed"

    def package_ids(self, mods, clone):
        return ["mandrake.rm.%s" % m.lower() for m in mods]

    def launch_and_wait(self):
        self.calls.append(("launch",))
        self.t += self.launch_s
        self.running = True
        self.log_mtime = self.t
        return True, "bridge token seen"

    def start_quicktest(self):
        self.t += 5.0
        return True, "Playing"

    def load_save(self, name):
        self.calls.append(("load_save", name))
        return True, "loaded"

    def owner_returned(self):
        # the retired presence probe: no harness code may call it (owner 2026-10-30). It answers "back" when
        # owner_back is set, so a call that changed anything would show.
        self.calls.append(("owner_probe",))
        return self.owner_back

    def game_facts(self):
        f = {"ingame_canary": {"ok": self.colonists > 0,
                               "problems": [] if self.colonists > 0 else ["no live colonist"]},
             "live_colonists": self.colonists, "player_log_mtime": self.log_mtime, "game_version": self.version,
             "active_mods": list(self.active), "world": {"name": "Quick-IX", "seed": "wulan"}}
        f.update(self.facts_override)
        return f

    def checkout(self, clone, sha):
        self.head[clone] = sha
        return True, ""

    def run_proof(self, argv, clone):
        self.calls.append(("proof", tuple(argv)))
        if self.on_proof:
            self.on_proof()
        return self.proof_rc, self.proof_txt or "proof output rc=%d" % self.proof_rc


def fresh(name, version_pin="1.6.4633 rev1", owner_playing=None):
    root = TMP / name
    p = R.rpaths(root)
    cfg = {"steve": {"game_version": version_pin}, "archmagi": {"game_version": version_pin}}
    if owner_playing is not None:
        cfg["archmagi"]["owner_playing"] = owner_playing
    L.write_config(p, cfg)
    return p


def events(p, event=None):
    return [e for e in L.read_events(p, R.ARM) if event is None or e["event"] == event]


def pub(p, item="ITEM_X", sha=SHA_A, profile="minimal", tier=None, mods=("Slime",), has_dll=False):
    return R.publish(p, item, sha, "A1", list(mods), has_dll, profile, tier, ["python3", "proof.py"])


# ---------------------------------------------------------------- stale sha
def t_stale():
    p = fresh("stale")
    pub(p, sha=SHA_A)
    pub(p, sha=SHA_B)
    why = raises(R.StaleResult, R.record_result, p, {"run_id": "r1", "item": "ITEM_X", "sha": SHA_A,
                                                       "verdict": "pass", "canary": {"ok": True}})
    check(why is not None and "stale sha" in why, "stale: a result for the superseded sha is refused (%s)" % why)
    check(not list(p["results"].glob("*.json")) if p["results"].is_dir() else True, "stale: nothing was written")
    R.record_result(p, {"run_id": "r2", "item": "ITEM_X", "sha": SHA_B, "verdict": "pass", "ts": "2",
                        "canary": {"ok": True}, "cand": R.current(p)["ITEM_X"]["cand"]})
    check(R.lane_record(p, "ITEM_X", SHA_B)["run_id"] == "r2", "stale control: the current sha's result is accepted")
    check(raises(R.StaleResult, R.lane_record, p, "ITEM_X", SHA_A) is not None,
          "stale: the gate's read for the old head is refused")
    # a re-publish during the run: the runner's own result goes stale and is not counted
    p2 = fresh("stale_race")
    pub(p2, sha=SHA_A)
    d = FakeDriver(on_proof=lambda: pub(p2, sha=SHA_B))
    r = R.run_one(p2, "steve", d, "/clone")
    check(r["verdict"] == "stale" and not list(p2["results"].glob("*.json")),
          "stale: a sha superseded mid-run gives verdict stale and writes no result")
    check([c["sha"] for c in R.pending(p2)] == [SHA_B], "stale: the new sha is what is pending")
    check(any("stale sha" in (e.get("detail") or {}).get("why", "") for e in events(p2, "invalid")),
          "stale: an invalid event names the stale sha")


# ---------------------------------------------------------------- dead colony
def t_dead():
    p = fresh("dead")
    pub(p)
    d = FakeDriver(colonists=0)
    r = R.run_one(p, "steve", d, "/clone")
    check(r["verdict"] == "invalid", "dead: a dead colony gives invalid (got %s)" % r["verdict"])
    check(r["canary"] and not r["canary"]["ok"] and any("dead colony" in x for x in r["canary"]["problems"]),
          "dead: the canary is red and names the dead colony")
    check(not any(c[0] == "proof" for c in d.calls), "dead: the proof never ran on an invalid environment")
    check([c["item"] for c in R.pending(p)] == ["ITEM_X"], "dead: the candidate is re-queued (still pending)")
    check(any(e["event"] == "invalid" for e in events(p)) and any(
        e["event"] == "canary" and e["verdict"] == "fail" for e in events(p)), "dead: canary fail + invalid events")
    check(R.fail_rounds(p, "ITEM_X") == 0, "dead: an invalid run is not a failed round")
    p2 = fresh("alive")
    pub(p2)
    r2 = R.run_one(p2, "steve", FakeDriver(), "/clone")
    check(r2["verdict"] == "pass" and r2["canary"]["ok"], "dead control: a live colony passes (got %s %s)"
          % (r2["verdict"], r2.get("canary")))
    check(R.pending(p2) == [] and R.lane_record(p2, "ITEM_X", SHA_A)["verdict"] == "pass",
          "dead control: the pass is counted and the gate can read it")
    te = events(p2, "test_end")
    ts = events(p2, "test_start")
    check(ts and ts[0]["detail"]["tester"] != ts[0]["detail"]["builder"] and te and te[0]["verdict"] == "pass",
          "events: test_start names a tester other than the builder; test_end carries the verdict")


# ---------------------------------------------------------------- full list refused
def t_full():
    p = fresh("full")
    why = raises(R.CandidateRefused, pub, p, profile="full")
    check(why is not None and "trial" in why, "full: a full-list candidate is refused at publish (%s)" % why)
    d = FakeDriver(running=True)
    with L.Lane("steve", R.ARM, d, "full test", root=p["root"]) as lane:
        why = raises(L.LaneRefused, lane.reload, "full", None, "R0")
    check(why is not None and "trial" in why, "full: Lane.reload refuses profile full in trial mode")
    check(not any(c[0] in ("stop", "minimal", "tier", "deploy", "launch") for c in d.calls),
          "full: refused before the game was stopped or any list swapped")
    check(not any(c[0] == "restore" for c in d.calls), "full: nothing swapped, so nothing restored")
    with L.Lane("steve", R.ARM, FakeDriver(), "x", root=p["root"]) as lane:
        check(raises(L.LaneRefused, lane.reload, "minimal+deps", None, "R0") is not None,
              "profile: minimal+deps with no tier is refused")
        check(raises(L.LaneRefused, lane.reload, "minimal", None, "R9") is not None,
              "profile: a reload rule outside M1's R0-R3 is refused")


# ---------------------------------------------------------------- measured load time
def t_loadtime():
    p = fresh("loadtime")
    d = FakeDriver(launch_s=137.0)
    d.head["/clone"] = SHA_A
    with L.Lane("steve", R.ARM, d, "deps", root=p["root"]) as lane:
        ev = lane.reload("minimal+deps", "slime", "R0", mods=["Slime"], clone="/clone", sha=SHA_A)
    check(("tier", "slime") in d.calls, "loadtime: minimal+deps swaps through modset_builder --tier")
    check(ev["detail"]["launch_to_ready_s"] == 142.0 and ev["minutes"] == round(142 / 60, 3),
          "loadtime: the reload event records the measured launch-to-ready (got %s)" % ev["detail"]["launch_to_ready_s"])
    rows = L.load_times(p, "steve")
    check(len(rows) == 1 and rows[0]["profile"] == "minimal+deps" and rows[0]["launch_to_ready_s"] == 142.0,
          "loadtime: load_times.jsonl carries the profile's measured seconds")
    check(ev["rule"] == "R0" and ev["detail"]["deploy"][0]["mod"] == "Slime", "loadtime: rule and deploy logged")


# ---------------------------------------------------------------- restore
def t_restore():
    p = fresh("restore")
    d = FakeDriver()
    d.head["/c"] = SHA_A
    try:
        with L.Lane("steve", R.ARM, d, "boom", root=p["root"]) as lane:
            lane.reload("minimal", None, "R0", mods=["Slime"], clone="/c", sha=SHA_A)
            raise RuntimeError("planted crash mid-test")
    except RuntimeError:
        pass
    rel = events(p, "live_release")
    check(("restore",) in d.calls and rel and rel[-1]["detail"]["restored"] and rel[-1]["detail"]["aborted"],
          "restore: a crash mid-test still restores the owner's list")
    check(rel[-1]["detail"]["charged_to"] == R.ARM and rel[-1]["minutes"] > 0,
          "restore: its minutes (%s) are charged to the arm that swapped" % rel[-1]["minutes"])
    check(d.calls.index(("stop",)) < d.calls.index(("restore",)) if ("stop",) in d.calls else False,
          "restore: the game is stopped before the list is written back")
    d2 = FakeDriver(restore_ok=False)
    d2.head["/c"] = SHA_A

    def body():
        with L.Lane("steve", R.ARM, d2, "x", root=p["root"]) as lane:
            lane.reload("minimal", None, "R0")
    check(raises(L.RestoreFailed, body) is not None and events(p, "live_release")[-1]["verdict"] == "error",
          "restore: a failed restore is loud and the release event says error")
    check(L.swap_marker(p, "steve").is_file(), "restore: a failed restore leaves the swap marker on disk")
    d3 = FakeDriver()
    with L.Lane("steve", R.ARM, d3, "next hold", root=p["root"]):
        pass
    rel = events(p, "live_release")[-1]
    check(("restore",) in d3.calls and rel["detail"]["inherited_swap"] and not L.swap_marker(p, "steve").is_file(),
          "restore: the next hold inherits the marker and puts the owner's list back (self-heal)")
    d4 = FakeDriver()
    with L.Lane("steve", R.ARM, d4, "read only", root=p["root"]):
        pass
    check(("restore",) not in d4.calls and events(p, "live_release")[-1]["detail"]["charged_to"] is None,
          "restore control: a hold that never swapped (and inherited nothing) restores and charges nothing")
    # a killed runner: the marker outlives the process
    pk = fresh("killed")
    dk = FakeDriver()
    lane = L.Lane("steve", R.ARM, dk, "killed", root=pk["root"])
    lane.take()
    lane.reload("minimal", None, "R0")
    del lane                                   # no __exit__: the process "died" with the list swapped
    check(L.swap_marker(pk, "steve").is_file(), "restore: a runner killed mid-hold leaves the marker")
    dn = FakeDriver(running=True)
    with L.Lane("steve", R.ARM, dn, "after kill", root=pk["root"]):
        pass
    check(("restore",) in dn.calls and dn.calls.index(("stop",)) < dn.calls.index(("restore",)),
          "restore: the hold after a killed runner stops the game and restores")
    # stop raises / the game will not go down: the bridge is still released, the restore withheld and loud
    for name, plant in (("stop raises", lambda d: setattr(d, "stop_raises", RuntimeError("planted"))),
                        ("game still up", lambda d: setattr(d, "stop_sticks", True))):
        ps = fresh("rel_" + name.replace(" ", "_"))
        ds = FakeDriver()

        def body2():
            with L.Lane("steve", R.ARM, ds, name, root=ps["root"]) as lane:
                lane.reload("minimal", None, "R0")
                plant(ds)
                ds.running = True
        why = raises(L.RestoreFailed, body2)
        check(why is not None and ("restore",) not in ds.calls and any(c[0] == "release" for c in ds.calls)
              and events(ps, "live_release")[-1]["verdict"] == "error" and L.swap_marker(ps, "steve").is_file(),
              "restore: %s -> no restore written, bridge still released, release says error, marker kept" % name)


# ---------------------------------------------------------------- main's mod files restored (N11)
def t_mods_restore():
    p = fresh("modsrestore")
    d = FakeDriver(running=True)
    d.head["/c"] = SHA_A
    with L.Lane("steve", R.ARM, d, "files", root=p["root"]) as lane:
        lane.reload("minimal", None, "R0", mods=["Slime", "Abyss"], clone="/c", sha=SHA_A)
    rm = [c for c in d.calls if c[0] == "restore_mods"]
    rel = events(p, "live_release")[-1]
    check(rm == [("restore_mods", ("Slime", "Abyss"), "/c", False)],
          "N11: release redeploys main's version of every deployed mod, from the deploy clone, game down (%s)" % rm)
    check(d.calls.index(("restore",)) < d.calls.index(rm[0]) and rel["verdict"] == "ok"
          and rel["detail"]["mods_restored"] == ["Slime", "Abyss"] and rel["detail"]["main_sha"] == "c" * 40
          and not L.swap_marker(p, "steve").is_file(),
          "N11: list then files; the release event names the mods and main's sha; the marker is gone")
    d0 = FakeDriver()
    with L.Lane("steve", R.ARM, d0, "no deploy", root=p["root"]) as lane:
        lane.reload("minimal", None, "R0")
    check(not any(c[0] == "restore_mods" for c in d0.calls), "N11 control: a hold that deployed nothing redeploys nothing")
    # a failed file restore is loud, keeps the marker with the mods, and the next hold redeploys them
    pf = fresh("modsrestore_fail")
    df = FakeDriver()
    df.head["/c"] = SHA_A
    df.mods_restore_ok = False

    def body():
        with L.Lane("steve", R.ARM, df, "x", root=pf["root"]) as lane:
            lane.reload("minimal", None, "R0", mods=["Slime"], clone="/c", sha=SHA_A)
    why = raises(L.RestoreFailed, body)
    mk = L.swap_marker(pf, "steve")
    check(why is not None and "mod-file restore" in why and events(pf, "live_release")[-1]["verdict"] == "error"
          and mk.is_file() and json.loads(mk.read_text())["mods"] == ["Slime"],
          "N11: a failed file restore raises RestoreFailed, release says error, the marker keeps the mods")
    dn = FakeDriver()
    with L.Lane("steve", "other_arm", dn, "next", root=pf["root"]):
        pass
    rel = [e for e in L.read_events(pf, "other_arm") if e["event"] == "live_release"]
    check(("restore_mods", ("Slime",), "/c", False) in dn.calls and not mk.is_file()
          and len(rel) == 1 and rel[-1]["detail"]["charged_to"] == R.ARM and rel[-1]["detail"].get("mods_restored"),
          "N11: the next hold inherits the mods from the marker and redeploys main (charged to the arm that swapped)")
    # a deploy that dies half way still restores: the marker is written before the first copy
    pk = fresh("modsrestore_killed")
    dk = FakeDriver()
    dk.head["/c"] = SHA_A
    dk.deploy = lambda mod, clone: (_ for _ in ()).throw(KeyboardInterrupt())
    lane = L.Lane("steve", R.ARM, dk, "killed", root=pk["root"])
    lane.take()
    try:
        lane.reload("minimal", None, "R0", mods=["Slime"], clone="/c", sha=SHA_A)
    except KeyboardInterrupt:
        pass
    del lane
    mk = json.loads(L.swap_marker(pk, "steve").read_text())
    check(mk.get("mods") == ["Slime"] and mk.get("clone") == "/c",
          "N11: a runner killed mid-deploy leaves the marker naming the mod and clone")
    # a seat clone is refused before anything is deployed
    ps = fresh("modsrestore_seat")
    dsx = FakeDriver()
    dsx.head[str(L.REPO)] = SHA_A
    with L.Lane("steve", R.ARM, dsx, "seat", root=ps["root"]) as lane:
        why = raises(L.LaneRefused, lane.reload, "minimal", None, "R0", mods=["Slime"], clone=str(L.REPO), sha=SHA_A)
    check(why is not None and "seat clone" in why and not any(c[0] == "deploy" for c in dsx.calls),
          "N11: a deploy from a seat clone is refused (main can never be checked out there to restore)")
    # game still up at release: files withheld, loud
    pu = fresh("modsrestore_up")
    du = FakeDriver()
    du.head["/c"] = SHA_A

    def body3():
        with L.Lane("steve", R.ARM, du, "up", root=pu["root"]) as lane:
            lane.reload("minimal", None, "R0", mods=["Slime"], clone="/c", sha=SHA_A)
            du.stop_sticks = True
    check(raises(L.RestoreFailed, body3) is not None and not any(c[0] == "restore_mods" for c in du.calls),
          "N11: game still running at release -> main's files are not written under it (DLL lock), loud")


# ---------------------------------------------------------------- the other lane rules
def t_rules():
    p = fresh("rules")
    d = FakeDriver(running=True)
    d.head["/c"] = SHA_A
    with L.Lane("steve", R.ARM, d, "dll", root=p["root"]) as lane:
        why = raises(L.LaneRefused, lane.deploy, ["Slime"], True, "/c", SHA_A)
        check(why is not None and "DLL" in why and not any(c[0] == "deploy" for c in d.calls),
              "rules: a C# deploy while the game runs is refused")
        check(raises(L.LaneRefused, lane.deploy, ["Slime"], False, "/c", SHA_B) is not None,
              "rules: deploying from a clone not at the candidate sha is refused")
        why = raises(L.LaneRefused, lane.load_save, CANON + ".rws")
        check(why is not None and "canonical" in why and not any(c[0] == "load_save" for c in d.calls),
              "rules: the canonical world save is refused before the bridge is asked")
        lane.load_save("FIXTURE_SAVE")
        check(lane.loaded_save == "FIXTURE_SAVE", "rules control: a fixture save loads")
    check(raises(L.LaneRefused, L.Lane, "steve", R.ARM, FakeDriver(), "fly", root=p["root"], flyer_flight=True)
          is not None, "rules: a flyer's flight is refused before any take")
    check(raises(R.CandidateRefused, R.publish, p, "F", SHA_A, "A1", ["Slime"], False, "minimal", None, ["x"], True)
          is not None, "rules: a flyer-flight candidate is refused at publish")
    for cfg in (None, True, False):
        pp = fresh("idle_%s" % cfg, owner_playing=cfg)
        dd = FakeDriver(owner_back=True)
        with L.Lane("archmagi", R.ARM, dd, "idle", root=pp["root"]):
            pass
        check(("take", "archmagi", False) in dd.calls and ("owner_probe",) not in dd.calls,
              "rules: archmagi owner_playing=%s -> a plain take, the presence probe never called" % cfg)
        check("owner_playing" not in L.lane_config(pp, "archmagi"), "rules: an old owner_playing key is dropped")
    ds = FakeDriver()
    with L.Lane("steve", R.ARM, ds, "steve", root=p["root"]):
        pass
    check(("take", "stevedesktop", False) in ds.calls, "rules: steve takes plainly too")
    # take refused: no hold, no release, a refused live_take
    pr = fresh("take_refused")
    pub(pr)
    dr = FakeDriver(take_ok=False)
    r = R.run_one(pr, "steve", dr, "/c")
    check(r["verdict"] == "refused" and not any(c[0] == "release" for c in dr.calls)
          and events(pr, "live_take")[-1]["verdict"] == "refused", "rules: a refused take holds and releases nothing")
    # owner 2026-10-30: his coming back is not an event. With the probe answering "back" from the start and
    # owner_playing set, the archmagi run swaps, launches, proves and records exactly as if he were away.
    po = fresh("owner", owner_playing=True)
    pub(po, item="OLD")
    do = FakeDriver(owner_back=True)
    r = R.run_one(po, "archmagi", do, "/c")
    check(r["verdict"] == "pass" and r["item"] == "OLD", "rules: owner 'back' before the swap -> the run still passes "
          "(got %s)" % r.get("verdict"))
    check(("minimal",) in do.calls and any(c[0] == "launch" for c in do.calls) and ("owner_probe",) not in do.calls,
          "rules: the list is swapped and the game launched; the presence probe is never called")
    check([e.get("verdict") for e in events(po, "reload")] == ["ok"], "rules: the reload is ok, never yielded")
    check(raises(ValueError, L.emit, p, {"event": "deploy", "arm": "x", "lane": "steve", "run_id": "r"}) is not None,
          "events: an event outside the §1.7 schema is refused")


# ---------------------------------------------------------------- canary checks
def t_canary():
    p = fresh("canary")
    cases = [
        ("stale Player.log", lambda d: d.facts_override.update(player_log_mtime=1.0), "stale"),
        ("wrong game version", lambda d: d.facts_override.update(game_version="1.5.4409"), "expected"),
        ("version unreadable", lambda d: d.facts_override.update(game_version=None), "UNMEASURED"),
        ("colonist count unreadable", lambda d: d.facts_override.update(live_colonists=None), "UNMEASURED"),
        ("deployed mod not active", lambda d: d.facts_override.update(active_mods=["ludeon.rimworld"]), "not active"),
        ("in-game probe missing", lambda d: d.facts_override.update(ingame_canary=None), "in-game canary"),
        ("on the canonical world (name)", lambda d: d.facts_override.update(
            world={"name": "canon'world", "seed": "other"}), "canonical world"),
        ("on the canonical world (seed)", lambda d: d.facts_override.update(
            world={"name": "Other", "seed": "CanonSeed"}), "canonical world"),
        ("world identity partial", lambda d: d.facts_override.update(world={"name": "Quick-IX"}), "UNMEASURED"),
        ("world identity blank", lambda d: d.facts_override.update(world={"name": " ", "seed": "x"}), "UNMEASURED"),
        ("world identity not text", lambda d: d.facts_override.update(world={"name": {"error": 1}, "seed": "x"}),
         "UNMEASURED"),
    ]
    for name, plant, needle in cases:
        d = FakeDriver()
        d.head["/c"] = SHA_A
        with L.Lane("steve", R.ARM, d, name, root=p["root"]) as lane:
            lane.reload("minimal", None, "R0", mods=["Slime"], clone="/c", sha=SHA_A)
            plant(d)
            res = lane.canary(SHA_A)
        check(not res["ok"] and any(needle in x for x in res["problems"]),
              "canary: %s -> red (%s)" % (name, "; ".join(res["problems"])[:90]))
    d = FakeDriver()
    d.head["/c"] = SHA_A
    with L.Lane("steve", R.ARM, d, "sha", root=p["root"]) as lane:
        lane.reload("minimal", None, "R0", mods=["Slime"], clone="/c", sha=SHA_A)
        check(not lane.canary(SHA_B)["ok"], "canary: deployed sha != candidate sha -> red")
        check(lane.canary(SHA_A)["ok"], "canary control: everything right -> green")
    pu = fresh("unpinned", version_pin=None)
    d = FakeDriver()
    with L.Lane("steve", R.ARM, d, "unpinned", root=pu["root"]) as lane:
        lane.reload("minimal", None, "R0")
        res = lane.canary(None)
    check(not res["ok"] and any("not pinned" in x for x in res["problems"]), "canary: an unpinned version -> red")
    d = FakeDriver()
    with L.Lane("steve", R.ARM, d, "nolaunch", root=p["root"]) as lane:
        res = lane.canary(None)
    check(not res["ok"] and any("never launched" in x for x in res["problems"]),
          "canary: a hold that never launched cannot prove a fresh Player.log -> red")

    class Boom(FakeDriver):
        def game_facts(self):
            raise ConnectionError("bridge gone")
    d = Boom()
    with L.Lane("steve", R.ARM, d, "boom", root=p["root"]) as lane:
        lane.reload("minimal", None, "R0")
        res = lane.canary(None)
    check(not res["ok"] and any("unreadable" in x for x in res["problems"]), "canary: unreadable facts -> red")


# ---------------------------------------------------------------- proof codes and parking
def t_verdicts():
    p = fresh("verdicts")
    pub(p, item="ODD")
    r = R.run_one(p, "steve", FakeDriver(proof_rc=3), "/c")
    check(r["verdict"] == "invalid" and R.pending(p), "verdicts: proof exit 3 is invalid and re-queued")
    pp = fresh("park")
    for i, sha in enumerate(("1" * 40, "2" * 40, "3" * 40)):
        pub(pp, item="BAD", sha=sha)
        r = R.run_one(pp, "steve", FakeDriver(proof_rc=1), "/c")
        check(r["verdict"] == "fail", "verdicts: round %d fails" % (i + 1))
    pub(pp, item="BAD", sha="4" * 40)
    check(R.parked(pp) == ["BAD"] and R.pending(pp) == [], "verdicts: 3 failed rounds park the item, not close it")
    check(raises(R.CandidateRefused, R.publish, pp, "Y", "HEAD", "A1", [], False, "minimal", None, ["x"]) is not None,
          "publish: a non-sha ('HEAD') is refused")
    # oldest first
    po = fresh("order")
    pub(po, item="FIRST", sha=SHA_A)
    pub(po, item="SECOND", sha=SHA_B)
    check([c["item"] for c in R.pending(po)] == ["FIRST", "SECOND"], "queue: oldest candidate first")


# ---------------------------------------------------------------- round-1 review regressions
def t_review():
    # H1: the colony dies (or the harness crashes) during the proof -> invalid, never fail
    p = fresh("h1")
    pub(p)
    d = FakeDriver(proof_rc=1)
    d.on_proof = lambda: setattr(d, "colonists", 0)
    r = R.run_one(p, "steve", d, "/c")
    check(r["verdict"] == "invalid" and R.fail_rounds(p, "ITEM_X") == 0 and R.pending(p),
          "H1: a colony dead after the proof makes rc 1 invalid, not fail (got %s)" % r["verdict"])
    p = fresh("h1tb")
    pub(p)
    r = R.run_one(p, "steve", FakeDriver(proof_rc=1, proof_txt="Traceback (most recent call last):\nImportError: x"),
                  "/c")
    check(r["verdict"] == "invalid" and "harness crashed" in r["why"], "H1: rc 1 with a Python traceback is invalid")
    p = fresh("h1rc")
    R.publish(p, "ITEM_X", SHA_A, "A1", ["Slime"], False, "minimal", None, ["p"], fail_rc=7)
    r1 = R.run_one(p, "steve", FakeDriver(proof_rc=1), "/c")
    r7 = R.run_one(p, "steve", FakeDriver(proof_rc=7), "/c")
    check(r1["verdict"] == "invalid" and r7["verdict"] == "fail", "H1: a declared fail_rc is the only fail code")
    # H4: an unknown tier is refused
    with L.Lane("steve", R.ARM, FakeDriver(), "tier", root=p["root"]) as lane:
        check(raises(L.LaneRefused, lane.reload, "minimal+deps", "full", "R0") is not None,
              "H4: a tier modset_builder does not name is refused")
    # H4: extra active mods beyond the profile -> red
    d = FakeDriver()
    d.head["/c"] = SHA_A
    with L.Lane("steve", R.ARM, d, "extra", root=p["root"]) as lane:
        lane.reload("minimal", None, "R0", mods=["Slime"], clone="/c", sha=SHA_A)
        d.active.append("owner.bigmod")
        res = lane.canary(SHA_A)
    check(not res["ok"] and any("beyond" in x for x in res["problems"]), "H4: a mod active beyond the profile -> red")
    d = FakeDriver()
    d.expected_active = lambda pr, t: (_ for _ in ()).throw(RuntimeError("no modset_builder"))
    with L.Lane("steve", R.ARM, d, "exp", root=p["root"]) as lane:
        lane.reload("minimal", None, "R0")
        res = lane.canary(None)
    check(not res["ok"] and any("expected mod set is UNMEASURED" in x for x in res["problems"]),
          "H4: an unmeasured expected set -> red")
    # H3: a dirty clone is refused; a missing world identity is red; version pin is exact
    d = FakeDriver()
    d.head["/c"] = SHA_A
    d.dirty = [" M Source/x.cs"]
    with L.Lane("steve", R.ARM, d, "dirty", root=p["root"]) as lane:
        check(raises(L.LaneRefused, lane.deploy, ["Slime"], False, "/c", SHA_A) is not None
              and not any(c[0] == "deploy" for c in d.calls), "H3: a dirty clone is never deployed")
    for name, plant, needle in (("world identity unmeasured", lambda d: d.facts_override.update({}) or
                                 d.__setattr__("game_facts", lambda f=FakeDriver.game_facts, dd=d:
                                               {k: v for k, v in f(dd).items() if k != "world"}), "world identity"),
                                ("version prefix only", lambda d: d.facts_override.update(game_version="1.6.4633"),
                                 "expected")):
        d = FakeDriver()
        with L.Lane("steve", R.ARM, d, name, root=p["root"]) as lane:
            lane.reload("minimal", None, "R0")
            plant(d)
            res = lane.canary(None)
        check(not res["ok"] and any(needle in x for x in res["problems"]), "H3/L3: %s -> red" % name)
    # the canon save's world cannot be read -> red; a quicktest world is green (control)
    keep = L.canonical_worlds
    for name, fn, want_ok in (("canon world unreadable", lambda: (_ for _ in ()).throw(OSError("no rws")), False),
                              ("quicktest world control", keep, True)):
        L.canonical_worlds = fn
        try:
            d = FakeDriver()
            with L.Lane("steve", R.ARM, d, name, root=p["root"]) as lane:
                lane.reload("minimal", None, "R0")
                res = lane.canary(None)
        finally:
            L.canonical_worlds = keep
        check(res["ok"] == want_ok and (want_ok or any("unreadable" in x for x in res["problems"])),
              "world canary: %s -> %s" % (name, "green" if want_ok else "red"))
    # canonical_worlds reads the .rws with an XML parser: named and numeric character references decode
    import game_paths
    keep_saves, keep_cs = game_paths.SAVES, L.canonical_saves
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "C1.rws").write_bytes(b"<savegame><game><world>\r\n<planetType>T</planetType><info>\r\n"
                                          b"<name>Ash&apos;&#107;arr</name><planetCoverage>1</planetCoverage>"
                                          b"<seedString>&#115;afety</seedString></info></world></game></savegame>")
        (Path(td) / "C2.rws").write_bytes(b"<savegame><game><world><info><name>N</name></info></world></game>")
        game_paths.SAVES, L.canonical_saves = td, (lambda: {"C1"})
        try:
            got = REAL_CANONICAL_WORLDS()
            L.canonical_saves = lambda: {"C2"}
            bad = raises(ValueError, REAL_CANONICAL_WORLDS)
        finally:
            game_paths.SAVES, L.canonical_saves = keep_saves, keep_cs
    check(got == [{"name": "Ash'karr", "seed": "safety"}], "canonical_worlds: references decode (%s)" % got)
    check(bad is not None, "canonical_worlds: a save with no seedString raises (-> red), never an empty identity")
    # package_ids reads src/<Tier>/<Mod>/About/About.xml (deploy_custom_mods' bare folder name), exactly one hit
    with tempfile.TemporaryDirectory() as td:
        a = Path(td) / "src" / "RimMandrake" / "Vis" / "About"
        a.mkdir(parents=True)
        (a / "About.xml").write_text("<ModMetaData><packageId> mandrake.rm.vis </packageId></ModMetaData>")
        for t in ("RimA", "RimB"):
            b = Path(td) / "src" / t / "Twin" / "About"
            b.mkdir(parents=True)
            (b / "About.xml").write_text("<ModMetaData><packageId>x.%s</packageId></ModMetaData>" % t)
        got = L.RealDriver().package_ids(["Vis", "Nope", "Twin"], td)
    check(got == ["mandrake.rm.vis", "<unreadable:Nope>", "<unreadable:Twin>"],
          "package_ids: tier-nested About.xml read; missing and ambiguous are unreadable (%s)" % got)
    # M7: canonical save in any case or path
    for n in ("canon_start_save", "Saves\\CANON_START_SAVE.rws", "C:/x/Canon_Start_Save.RWS"):
        check(L.is_canonical(n), "M7: %r is the canonical save" % n)
    check(not L.is_canonical("FIXTURE_SAVE"), "M7 control: a fixture save is not canonical")
    # H6: starvation guards
    p = fresh("h6")
    check(raises(R.CandidateRefused, R.publish, p, "E", SHA_A, "A1", [], False, "minimal", None, ["x"]) is not None,
          "H6: a candidate with no mod is refused")
    c = R.publish(p, "W", "  " + SHA_A.upper() + "\n", "A1", ["Slime"], False, "minimal", None, ["x"])
    check(c["sha"] == SHA_A, "H6: a sha is stored stripped and lower-case")
    R.publish(p, "NEXT", SHA_B, "A1", ["Slime"], False, "minimal", None, ["x"])
    for _ in range(R.MAX_INVALID_ROUNDS):
        r = R.run_one(p, "steve", FakeDriver(colonists=0), "/c")
        check(r["item"] == "W" and r["verdict"] == "invalid", "H6: W runs invalid")
    check([x["item"] for x in R.stuck(p)] == ["W"] and [x["item"] for x in R.pending(p)] == ["NEXT"]
          and R.fail_rounds(p, "W") == 0, "H6: %d invalid rounds make W stuck (not failed); NEXT is next"
          % R.MAX_INVALID_ROUNDS)
    # M1: a reverted sha is a new publication, tested again, and the gate can read it
    p = fresh("m1")
    pub(p, sha=SHA_A)
    R.run_one(p, "steve", FakeDriver(proof_rc=1), "/c")
    pub(p, sha=SHA_B)
    R.run_one(p, "steve", FakeDriver(), "/c")
    pub(p, sha=SHA_A)
    check([x["sha"] for x in R.pending(p)] == [SHA_A], "M1: a reverted sha is pending again")
    check(raises(R.StaleResult, R.lane_record, p, "ITEM_X", SHA_A) is not None,
          "M1: the old A result does not count for the new A publication")
    R.run_one(p, "steve", FakeDriver(), "/c")
    check(R.lane_record(p, "ITEM_X", SHA_A)["verdict"] == "pass", "M1: after its re-test the gate reads A")
    # M2: a claimed candidate is skipped by a second runner
    p = fresh("m2")
    pub(p, item="ONE", sha=SHA_A)
    pub(p, item="TWO", sha=SHA_B)
    check(R.claim(p, R.pending(p)[0]["cand"], "other-runner"), "M2: a first claim succeeds")
    r = R.run_one(p, "steve", FakeDriver(), "/c")
    check(r["item"] == "TWO", "M2: the second runner skips the claimed candidate (got %s)" % r["item"])
    check(R.run_one(p, "steve", FakeDriver(), "/c") is None, "M2: nothing free while ONE is claimed")
    # M4: owner "returns" during the proof -> nothing changes, the result is recorded (owner 2026-10-30)
    p = fresh("m4", owner_playing=True)
    pub(p)
    d = FakeDriver()
    d.on_proof = lambda: setattr(d, "owner_back", True)
    r = R.run_one(p, "archmagi", d, "/c")
    check(r["verdict"] == "pass" and p["results"].is_dir() and list(p["results"].glob("*.json"))
          and ("owner_probe",) not in d.calls,
          "M4: an owner back during the proof changes nothing: a pass is recorded, the probe never called")
    # M5: a non-LaneRefused harness fault is invalid with an invalid event and a test_end
    p = fresh("m5")
    pub(p)
    d = FakeDriver()
    d.launch_and_wait = lambda: (_ for _ in ()).throw(OSError("planted disk error"))
    r = R.run_one(p, "steve", d, "/c")
    check(r["verdict"] == "invalid" and "harness fault" in r["why"] and events(p, "invalid")
          and events(p, "test_end")[-1]["verdict"] == "invalid" and ("restore",) in d.calls,
          "M5: a harness fault is invalid, logged, ended and the list restored")
    # L4: failed launches stay out of the measured load times
    p = fresh("l4")
    d = FakeDriver()
    d.launch_and_wait = lambda: (False, "no bridge token")
    with L.Lane("steve", R.ARM, d, "l4", root=p["root"]) as lane:
        raises(L.LaneRefused, lane.reload, "minimal", None, "R0")
    check(L.load_times(p, "steve") == [] and len(L.load_times(p, "steve", ok_only=False)) == 1,
          "L4: a failed launch is logged but not a measured load time")
    # L5: the rule is R0 when the game is down, R2 when a stale deploy is running
    p = fresh("l5")
    pub(p, item="DOWN", sha=SHA_A)
    pub(p, item="UP", sha=SHA_B)
    R.run_one(p, "steve", FakeDriver(), "/c")
    R.run_one(p, "steve", FakeDriver(running=True), "/c")
    rules = [e["rule"] for e in events(p, "reload")]
    check(rules == ["R0", "R2"], "L5: reload rules R0 (down) then R2 (running) (got %s)" % rules)
    # ---- round-2 review regressions
    # N1: a STUCK candidate re-enters the queue when its sha is republished after the lane is fixed
    p = fresh("n1", version_pin=None)
    pub(p, item="W")
    for _ in range(R.MAX_INVALID_ROUNDS):
        R.run_one(p, "steve", FakeDriver(), "/c")
    check([x["item"] for x in R.stuck(p)] == ["W"] and R.pending(p) == [], "N1: unpinned lane -> W stuck")
    L.write_config(p, {"steve": {"game_version": "1.6.4633 rev1"}})
    pub(p, item="W")
    r = R.run_one(p, "steve", FakeDriver(), "/c")
    check(r and r["verdict"] == "pass" and R.stuck(p) == [], "N1: republished after the fix, W is tested and passes")
    pub(p, item="W")
    check(R.pending(p) == [], "N1 control: republishing a non-stuck sha is still a no-op")
    # N2: an assertion failure with a traceback is a FAIL; an uncaught non-assertion exception is invalid
    for txt, want in (("FAIL: test_x\nTraceback (most recent call last):\n  File x\nAssertionError: 3 != 4\n"
                       "FAILED (failures=1)", "fail"),
                      ("Traceback (most recent call last):\n  File x\nAssertionError: slime count", "fail"),
                      ("Traceback (most recent call last):\n  File x\nModuleNotFoundError: No module named y", "invalid"),
                      ("Traceback (most recent call last):\n  File x\nrimdrive.BridgeError: timeout", "invalid"),
                      ("2 checks red", "fail")):
        p = fresh("n2_%d" % len(txt))
        pub(p)
        r = R.run_one(p, "steve", FakeDriver(proof_rc=1, proof_txt=txt), "/c")
        check(r["verdict"] == want, "N2: rc 1 with %r -> %s (got %s)" % (txt.splitlines()[-1][:40], want, r["verdict"]))
    # N3: a tier that is the full list in disguise is refused before anything stops or swaps
    p = fresh("n3")
    d = FakeDriver(running=True)
    with L.Lane("steve", R.ARM, d, "big", root=p["root"]) as lane:
        why = raises(L.LaneRefused, lane.reload, "minimal+deps", "everything", "R0")
    check(why is not None and "trial cap" in why and not any(c[0] in ("stop", "tier") for c in d.calls),
          "N3: a 200-mod tier is refused under the trial cap before the game is stopped (%s)" % (why or "")[:60])
    d = FakeDriver()
    d.expected_active = lambda pr, t: (_ for _ in ()).throw(RuntimeError("scan failed"))
    with L.Lane("steve", R.ARM, d, "unres", root=p["root"]) as lane:
        check(raises(L.LaneRefused, lane.reload, "minimal+deps", "slime", "R0") is not None,
              "N3: a tier whose closure cannot be resolved is refused")
    check(raises(R.CandidateRefused, R.publish, p, "T", SHA_A, "A1", ["Slime"], False, "minimal+deps", "nope", ["x"],
                 known_tiers={"slime"}) is not None, "L1: publish refuses an unknown tier")
    # N5: an inherited swap's restore is charged to the arm that swapped
    p = fresh("n5")
    d = FakeDriver(restore_ok=False)
    raises(L.RestoreFailed, lambda: L.Lane("steve", R.ARM, d, "x", root=p["root"]).__enter__().reload(
        "minimal", None, "R0") or None)
    lane = L.Lane("steve", R.ARM, d, "x", root=p["root"])
    lane.take()
    lane.reload("minimal", None, "R0")
    raises(L.RestoreFailed, lane.release)
    with L.Lane("steve", "other_arm", FakeDriver(), "next", root=p["root"]):
        pass
    rel = [e for e in L.read_events(p, "other_arm") if e["event"] == "live_release"][-1]
    check(rel["detail"]["charged_to"] == R.ARM, "N5: the inherited restore is charged to %s (got %s)"
          % (R.ARM, rel["detail"]["charged_to"]))
    # N9: a failure inside take() after the bridge was taken still releases it
    p = fresh("n9")
    real_marker = L.swap_marker
    L.swap_marker = lambda pp, ln: (_ for _ in ()).throw(OSError("planted: marker unreadable"))
    d = FakeDriver()
    try:
        raised = raises(OSError, lambda: L.Lane("steve", R.ARM, d, "n9", root=p["root"]).__enter__())
    finally:
        L.swap_marker = real_marker
    check(raised is not None and any(c[0] == "release" for c in d.calls), "N9: a take that fails after the bridge "
          "was taken releases it")
    # owner back + restore failed -> the verdict stands (owner back is not an event), restore_failed carried
    p = fresh("own_rf", owner_playing=True)
    pub(p)
    d = FakeDriver(restore_ok=False)
    d.on_proof = lambda: setattr(d, "owner_back", True)
    r = R.run_one(p, "archmagi", d, "/c")
    check(r["verdict"] != "aborted" and r.get("restore_failed") and ("owner_probe",) not in d.calls,
          "M8: owner back + failed restore -> not aborted, restore_failed carried (got %s)" % r.get("verdict"))
    # review of 9456c1f533: the real driver's take is the delegated one, so his OWNER hold (any age) and flight
    # wording refuse at the bridge too, not only while fresh
    rd = L.RealDriver()
    seen = []
    rd._rf = lambda *a: (seen.append(a), (0, "taken"))[1]
    rd.bridge_take("archmagi", "arena A archmagi r1: proof", False)
    check(seen and "--idle-ok" in seen[0] and "--force" not in seen[0],
          "RealDriver.bridge_take is a delegated take (--idle-ok): %s" % (seen,))
    # N10: unclaim drops only our own claim
    p = fresh("n10")
    R.claim(p, "cand1", "runnerA")
    R.unclaim(p, "cand1", "runnerB")
    check((p["claims"] / "cand1").is_file(), "N10: another runner's claim is not dropped")
    R.unclaim(p, "cand1", "runnerA")
    check(not (p["claims"] / "cand1").is_file(), "N10 control: our own claim is dropped")
    # queue order is publish order, not dict order (X@A, Y@B, X@C -> [Y, X])
    p = fresh("order2")
    pub(p, item="X", sha=SHA_A)
    pub(p, item="Y", sha=SHA_B)
    pub(p, item="X", sha="c" * 40)
    check([x["item"] for x in R.pending(p)] == ["Y", "X"], "queue: a republished item goes behind older ones")


def t_realdriver_git():
    """RALPHA_GIT_DEDUPE_REALDRIVER_PLAIN_GIT: RealDriver.restore_mods / clone_head / clone_dirty run git through
    arena_safe_git, so a core.fsmonitor or core.hooksPath planted in the candidate clone's .git runs nothing."""
    import subprocess
    import types
    d = TMP / "rdgit"
    d.mkdir()

    def g(*a, cwd=None):
        return subprocess.run(["git"] + list(a), cwd=str(cwd or d), capture_output=True, text=True,
                              env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                                       GIT_COMMITTER_EMAIL="t@t"))
    g("init", "-q", "-b", "main", "src")
    src = d / "src"
    (src / "f").write_text("x\n")
    g("add", "f", cwd=src)
    g("commit", "-q", "-m", "i", cwd=src)
    g("clone", "-q", str(src), "runner_clone")
    clone = d / "runner_clone"
    g("checkout", "-q", "-b", "main", "origin/main", cwd=clone)
    g("remote", "set-url", "origin", str(src), cwd=clone)
    g("branch", "-q", "-u", "origin/main", cwd=clone)
    mark = d / "mark"
    hook = d / "hook.sh"
    hook.write_text("#!/bin/sh\ntouch %s\n" % mark)
    hook.chmod(0o755)
    hdir = d / "hooks"
    hdir.mkdir()
    (hdir / "post-checkout").write_text("#!/bin/sh\ntouch %s\n" % mark)
    (hdir / "post-checkout").chmod(0o755)
    g("config", "core.fsmonitor", str(hook), cwd=clone)
    g("config", "core.hooksPath", str(hdir), cwd=clone)
    g("status", "--porcelain", cwd=clone)
    g("checkout", "-q", "--detach", "origin/main", cwd=clone)
    sane = mark.exists()                                      # plain git runs the planted command
    mark.unlink(missing_ok=True)

    def probe(mod):
        rd = mod.RealDriver()
        head, dirty = rd.clone_head(str(clone)), rd.clone_dirty(str(clone))
        ok, out, mhead = rd.restore_mods([], str(clone))
        return head, dirty, ok, mhead, mark.exists()
    want = g("rev-parse", "HEAD", cwd=src).stdout.strip()
    head, dirty, ok, mhead, ran = probe(L)
    check(sane and not ran and head == want and dirty == "" and ok and mhead == want,
          "RealDriver git: head/dirty/restore_mods run no planted fsmonitor or hook (got %s)" % ((head, dirty, ok, ran),))
    (clone / "u").write_text("z\n")
    check(L.RealDriver().clone_dirty(str(clone)) == "?? u", "RealDriver.clone_dirty reports an untracked file (stdout only)")
    (clone / "u").unlink()
    mark.unlink(missing_ok=True)
    text = (HERE / "arena_lane.py").read_text()
    anchor = "p = SG.git_run(clone, *a, transport=transport, capture_output=True,"
    assert text.count(anchor) == 1
    m = types.ModuleType("arena_lane_plain")
    m.__file__ = str(HERE / "arena_lane.py")
    exec(compile(text.replace(anchor, "p = subprocess.run(['git', '-C', str(clone)] + list(a), capture_output=True,"
                              ).replace("transport=transport, capture_output", "capture_output"), m.__file__, "exec"), m.__dict__)
    try:
        ran2 = probe(m)[4]
    except Exception:  # noqa: BLE001
        ran2 = True
    check(ran2, "RealDriver git mutation (plain git) runs the planted command: the test goes RED")
    # a clone-local remote.origin.uploadpack must not run on restore_mods' fetch (the fetch passes --upload-pack itself)
    g("config", "remote.origin.uploadpack", str(hook), cwd=clone)
    mark.unlink(missing_ok=True)
    ok3 = L.RealDriver().restore_mods([], str(clone))[0]
    check(ok3 and not mark.exists(), "RealDriver.restore_mods fetch runs no clone-local remote.origin.uploadpack (ok=%s)" % ok3)
    mark.unlink(missing_ok=True)
    plain = text.replace('"fetch", "-q", "--upload-pack=git-upload-pack", "origin"', '"fetch", "-q", "origin"')
    assert plain != text
    m2 = types.ModuleType("arena_lane_noup")
    m2.__file__ = str(HERE / "arena_lane.py")
    exec(compile(plain, m2.__file__, "exec"), m2.__dict__)
    m2.RealDriver().restore_mods([], str(clone))
    check(mark.exists(), "dropping --upload-pack from the fetch runs the planted uploadpack: the test goes RED")


for t in (t_stale, t_dead, t_full, t_loadtime, t_restore, t_mods_restore, t_rules, t_canary, t_verdicts, t_review,
          t_realdriver_git):
    t()
shutil.rmtree(TMP, ignore_errors=True)
print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
