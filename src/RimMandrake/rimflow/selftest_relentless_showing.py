#!/usr/bin/env python3
"""OWNER_REVIEW_BUILD_SHOWS_READY_BEFORE_ASKED: an item waiting only on the owner's look is staged before he is asked.

The owner, 2026-11-05: "Sloppy. For all the items waiting for human review, please have them pre-build anything needed
for the live showing." Rows: the trigger (needs=owner, an L4 look clause, a cosmetic gate; never a Designer first touch),
READY TO SHOW only after a complete manifest and a pass from the blind judge the supervisor launched, STALE on a new sha
or a changed deployed mod, the tick's one-build-at-a-time bridge discipline, and the hold: under an OWNER or Conductor
bridge hold nothing deploys or restarts (the real cli refuses Relentless's take). Touches nothing real."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
RIM = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, RIM)
os.environ.setdefault("RELENTLESS_SHOWINGS_DIR", tempfile.mkdtemp(prefix="rs_show_dir_"))
import relentless  # noqa: E402
import relentless_showing as S  # noqa: E402

CLI = os.path.join(HERE, "cli.py")
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def item(**kw):
    d = dict(open=True, title="t", criteria=[], outstanding=[], built_sha=None, cited_shas=[])
    d.update(kw)
    return types.SimpleNamespace(**d)


def trigger_rows():
    no_ft = lambda i: False  # noqa: E731
    check(S.wants("A", item(), True, no_ft) == "needs=owner", "needs=owner (is_his) enrols")
    look = [{"id": "A4", "level": "L4", "text": "The owner looks at the moat live and it reads right"}]
    check(S.wants("A", item(criteria=look, outstanding=["A4"]), False, no_ft) == "only a look clause is owed",
          "an L4 'he looks' clause as the only owed criterion enrols")
    gate = [{"id": "C1", "level": "L2", "text": "Cosmetic: nothing ships before his look"}]
    check(S.wants("A", item(criteria=gate, outstanding=["C1"]), False, no_ft) is not None, "a cosmetic gate enrols")
    more = look + [{"id": "B1", "level": "L3", "text": "the gate opens under load"}]
    check(S.wants("A", item(criteria=more, outstanding=["A4", "B1"]), False, no_ft) is None,
          "a look clause beside other owed work does not enrol")
    check(S.wants("X_DESIGN_FIRST_TOUCH", item(), True, lambda i: i.endswith("_DESIGN_FIRST_TOUCH")) is None,
          "a Designer first-touch pass is a sign-off, not a showing")
    check(S.wants("A", item(open=False), True, no_ft) is None, "a closed item does not enrol")
    check(S.route(item(title="Reskin the walker sprites")) == "sheet" and S.route(item(title="Drawbridge over a moat")) == "save",
          "art takes the review-sheet route, the rest a review save")


def manifest(d, sha="abc1234", mods=None, built_by="rm-show-u1"):
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "s1.png"), "wb").write(b"x")
    mods = mods or ["Moat"]
    m = {"item": os.path.basename(d), "sha": sha, "route": "save", "save": "Showing_" + os.path.basename(d), "mods": mods, "minutes": 4,
         "deployed": S.mods_fp(mods, os.path.join(os.path.dirname(os.path.dirname(d)), "Mods")),
         "stations": [{"n": 1, "label": "1 moat", "shows": "the moat", "judge": "does it read", "capture": "s1.png"}],
         "built_by": built_by}
    json.dump(m, open(os.path.join(d, S.MANIFEST), "w"))
    m["_dir"] = d
    return m


def status_rows(tmp):
    d = os.path.join(tmp, "st")
    check(S.status(None, None, "abc", None, None)[0] == S.OWED, "nothing built reads OWED")
    m = manifest(d)
    check(S.status(m, None, "abc1234", None, None)[0] == S.UNJUDGED, "built, not judged: not ready")
    j = {"judged_by": "rm-showj-u2", "sha": "abc1234", "verdict": "pass", "stations": {"1": "the moat reads"}}
    check(S.status(m, j, "abc1234", None, "rm-showj-u2")[0] == S.READY, "a pass from the launched blind judge: READY TO SHOW")
    check(S.status(m, dict(j, judged_by="rm-show-u1"), "abc1234", None, "rm-show-u1")[0] == S.UNJUDGED,
          "the builder judging its own showing is no judge")
    check(S.status(m, j, "abc1234", None, "rm-showj-other")[0] == S.UNJUDGED, "a judge.json the supervisor did not launch is no judge")
    check(S.status(m, dict(j, verdict="fail"), "abc1234", None, "rm-showj-u2")[0] == S.FAILED, "a fail is not ready")
    check(S.status(m, j, "def4567", None, "rm-showj-u2")[0] == S.STALE, "a new item sha makes it STALE")
    mods = os.path.join(tmp, "Mods", "Moat")
    os.makedirs(mods)
    open(os.path.join(mods, "a.xml"), "w").write("1")
    fp = S.mods_fp(["Moat"], os.path.join(tmp, "Mods"))
    m2 = dict(m, deployed=fp)
    check(S.status(m2, j, "abc1234", fp, "rm-showj-u2")[0] == S.READY, "same deployed mod: still ready")
    time.sleep(0.01)
    open(os.path.join(mods, "a.xml"), "w").write("22")
    fp2 = S.mods_fp(["Moat"], os.path.join(tmp, "Mods"))
    check(fp2 != fp and S.status(m2, j, "abc1234", fp2, "rm-showj-u2")[0] == S.STALE, "a changed deployed mod makes it STALE")
    check(S.status(m, dict(j, stations={}), "abc1234", None, "rm-showj-u2")[0] == S.UNJUDGED,
          "a pass that leaves a station without a note is no verdict")
    check(S.status(dict(m, mods=[]), j, "abc1234", None, "rm-showj-u2")[0] == S.INCOMPLETE,
          "a review save naming no deployed mods is incomplete (nothing could say it went stale)")
    check(S.status(dict(m, deployed=None), j, "abc1234", None, "rm-showj-u2")[0] == S.INCOMPLETE,
          "a review save with no deployed fingerprint from its builder is incomplete")
    check(S.status(dict(m, sha="a"), dict(j, sha="a"), "abc1234", None, "rm-showj-u2")[0] != S.READY,
          "a one-letter sha prefix names no build")
    check(S.status(m, j, "abc1234", None, "rm-showj-u2", None, "OTHER")[0] == S.INCOMPLETE, "another item's manifest is never this one's showing")
    two = [dict(m["stations"][0]), dict(m["stations"][0], label="1 again")]
    check(S.status(dict(m, stations=two), j, "abc1234", None, "rm-showj-u2")[0] == S.INCOMPLETE, "repeated station numbers are incomplete")
    check(S.status(dict(m, route="art"), j, "abc1234", None, "rm-showj-u2")[0] == S.INCOMPLETE, "a route neither save nor sheet is incomplete")
    check(S.status(dict(m, sha=None), dict(j, sha=None), None, None, "rm-showj-u2")[0] == S.INCOMPLETE,
          "a showing naming no sha is never ready, even with no ledger sha")
    check(S.status(m, dict(j, sha=None), "abc1234", None, "rm-showj-u2")[0] == S.STALE, "a judge naming no sha is no verdict on this build")
    saves = os.path.join(tmp, "Saves")
    os.makedirs(saves, exist_ok=True)
    check(S.status(m, j, "abc1234", None, "rm-showj-u2", saves)[0] == S.INCOMPLETE, "a save not in the Saves folder is not ready")
    open(os.path.join(saves, "Showing_st.rws"), "w").write("<savegame/>")
    dg = S.digest(d, m, saves)
    time.sleep(0.01)
    open(os.path.join(saves, "Showing_st.rws"), "w").write("<savegame>other</savegame>")
    check(S.digest(d, m, saves) != dg, "an overwritten review save changes the judged digest")
    check(S.status(m, j, "abc1234", None, "rm-showj-u2", saves)[0] == S.READY, "and once it is there, ready")
    check(S.route(item(title="Review hose sprites laid on a map")) == "save", "an in-place title takes the save route")
    check(S.status(dict(m, sha=123), j, "abc1234", None, "rm-showj-u2")[0] == S.INCOMPLETE and
          S.status(dict(m, mods=[{}]), j, "abc1234", None, "rm-showj-u2")[0] == S.INCOMPLETE and S.mods_fp([{}], tmp),
          "a non-string sha or mod name is incomplete, never a crash")
    check(S.status(dict(m, stations=[None]), j, "abc1234", None, "rm-showj-u2")[0] == S.INCOMPLETE,
          "a malformed station is incomplete, never a crash")
    os.remove(os.path.join(d, "s1.png"))
    check(S.status(m, j, "abc1234", None, "rm-showj-u2")[0] == S.INCOMPLETE, "a capture missing on disk is not ready")


class Fx:
    def __init__(self, tmp, items, hold=None):
        self.show_root = os.path.join(tmp, "showings")
        self.mods_root = os.path.join(tmp, "Mods")
        self.items, self.hold, self.launched, self.live, self.takes, self.releases = items, hold, [], set(), 0, 0

    def showing_items(self):
        return self.items

    def showing_clone(self):
        return "/clone", None

    def bridge_take(self, purpose):
        self.takes += 1
        return self.hold

    def bridge_release(self):
        self.releases += 1

    holder = "RELENTLESS"

    def bridge_reading(self):
        return {"holder": self.holder}

    def launch(self, st, run, prompt, agent, clone, max_s, env):
        self.launched.append((st["item"], run["unit"], agent, prompt))
        self.live.add(run["unit"])

    def alive(self, run):
        return bool(run) and run["unit"] in self.live

    def stop(self, run, force):
        self.live.discard(run["unit"])


def tick_rows(tmp):
    r = {"showings": {"enabled": True}, "seat": "BENCH"}
    store = relentless.Store(os.path.join(tmp, "root"))
    a, b = item(built_sha="abc1234", title="Drawbridge"), item(built_sha="fff0000", title="Gate")
    rows = [("A", a, "needs=owner", "is the moat right", None), ("B", b, "needs=owner", "is the gate right", None)]
    held = Fx(tmp, rows, hold="bridge NOT TAKEABLE: held by OWNER for the drawbridge session")
    acts = []
    S.tick(store, held, r, 1000, acts, relentless)
    check(not held.launched and held.takes >= 1 and any(x["do"] == "showing_waits" and "OWNER" in x["why"] for x in acts),
          "under an OWNER bridge hold no showing builds (nothing deploys or restarts under it): %s" % acts)
    check(S.reading(store.root)["A"]["state"] == S.OWED, "and the item reads OWED, never ready")
    fx = Fx(tmp, rows)
    acts = []
    S.tick(store, fx, r, 1100, acts, relentless)
    check(len(fx.launched) == 1 and fx.launched[0][0] == "A" and fx.launched[0][2] == "rm-testpilot",
          "a free bridge: ONE showing build starts: %s" % [x[:3] for x in fx.launched])
    check("Showing_A" in fx.launched[0][3] and "numbered" in fx.launched[0][3], "its brief asks for the numbered review save")
    import relentless_game
    check(relentless_game.busy(store, None) == "showing A", "the game lane sees the showing build: no staging or round under it")
    check(S.reading(store.root)["A"]["state"] == S.BUILDING and any(x.get("item") == "B" and x["do"] == "showing_waits" for x in acts),
          "A reads BUILDING, B waits for it")
    unit = fx.launched[0][1]
    manifest(os.path.join(fx.show_root, "A"), built_by=unit)
    fx.live.discard(unit)
    acts = []
    S.tick(store, fx, r, 1200, acts, relentless)
    check(fx.releases == 1, "the bridge is released the moment the build ends")
    judge = [x for x in fx.launched if x[2] == "rm-judge"]
    check(len(judge) == 1 and judge[0][0] == "A" and judge[0][1] != unit, "a blind judge, a unit that did not build it, is launched")
    check(any(x[0] == "B" and x[2] == "rm-testpilot" for x in fx.launched), "and B's build starts now the bridge is free")
    check(S.reading(store.root)["A"]["state"] == S.JUDGING, "A reads JUDGING, not ready")
    ju = judge[0][1]
    json.dump({"judged_by": ju, "sha": "abc1234", "verdict": "pass", "stations": {"1": "ok"}}, open(os.path.join(fx.show_root, "A", S.JUDGE), "w"))
    fx.live.discard(ju)
    S.tick(store, fx, r, 1300, [], relentless)
    got = S.reading(store.root)["A"]
    check(got["state"] == S.READY and got["save"] == "Showing_A" and got["minutes"] == 4 and got["dir"].endswith("showings\\A"),
          "after the blind pass A reads READY TO SHOW with its save, time and folder: %s" % got)
    time.sleep(0.01)
    open(os.path.join(fx.show_root, "A", "s1.png"), "wb").write(b"a different picture")
    S.tick(store, fx, r, 1350, [], relentless)
    check(S.reading(store.root)["A"]["state"] != S.READY, "a capture replaced after the pass voids it: %s" % S.reading(store.root)["A"]["state"])
    a.built_sha = "abc9999"
    S.tick(store, fx, r, 1400, [], relentless)
    check(S.reading(store.root)["A"]["state"] in (S.STALE, S.BUILDING, S.OWED) and S.reading(store.root)["A"]["state"] != S.READY,
          "a new sha: A is no longer ready: %s" % S.reading(store.root)["A"])
    fx.items = rows[1:]
    S.tick(store, fx, r, 1500, [], relentless)
    check("A" not in S.reading(store.root), "an item no longer waiting on his look leaves the reading")
    supervision_rows(tmp)


def supervision_rows(tmp):
    """Codex review of the stage: a lost bridge renewal stops the build; an item leaving the stage mid-build has its
    run stopped and its bridge released; an item with no ledger sha is not STALE against the HEAD it was built at."""
    r = {"showings": {"enabled": True, "renew_s": 100}, "seat": "BENCH"}
    store = relentless.Store(os.path.join(tmp, "sroot"))
    a = item(built_sha="abc1234", title="Drawbridge")
    fx = Fx(os.path.join(tmp, "s"), [("A", a, "needs=owner", "q", None)])
    S.tick(store, fx, r, 1000, [], relentless)
    unit = fx.launched[0][1]
    fx.hold = "bridge NOT TAKEABLE: held by OWNER"
    acts = []
    S.tick(store, fx, r, 1200, acts, relentless)
    check(unit not in fx.live and any(x["do"] == "showing_stopped" for x in acts), "a refused renewal stops the build at once: %s" % acts)
    fx.hold = None
    S.tick(store, fx, r, 1300, [], relentless)       # settled; a second try starts
    unit2 = fx.launched[-1][1]
    rel = fx.releases
    fx.items = []
    acts = []
    S.tick(store, fx, r, 1400, acts, relentless)
    check(unit2 not in fx.live and any(x["do"] == "showing_stopped" for x in acts), "an item leaving the stage mid-build: its run is stopped")
    S.tick(store, fx, r, 1500, [], relentless)
    check(fx.releases == rel + 1 and "A" not in S.load_state(store)["rows"], "and its bridge released, its row gone")
    # a running build: his take of the bridge, or a new blocker, stops it on the next pass, not at renewal
    store3 = relentless.Store(os.path.join(tmp, "s3root"))
    fx3 = Fx(os.path.join(tmp, "s3"), [("A", a, "needs=owner", "q", None)])
    S.tick(store3, fx3, r, 1000, [], relentless)
    u3 = fx3.launched[-1][1]
    fx3.holder = "OWNER"
    acts = []
    S.tick(store3, fx3, r, 1010, acts, relentless)
    check(u3 not in fx3.live and any(x["do"] == "showing_stopped" and "OWNER" in x["why"] for x in acts),
          "his take of the bridge mid-build stops it on the next pass: %s" % acts)
    fx3.holder = "RELENTLESS"
    S.tick(store3, fx3, r, 1020, [], relentless)
    u4 = fx3.launched[-1][1]
    fx3.items = [("A", a, "needs=owner", "q", ("DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED", "his note is not built yet"))]
    acts = []
    S.tick(store3, fx3, r, 1030, acts, relentless)
    check(u4 != u3 and u4 not in fx3.live and any(x["do"] == "showing_stopped" for x in acts),
          "a blocker that appears mid-build stops it: %s" % acts)
    S.tick(store3, fx3, r, 1040, [], relentless)
    check(S.reading(store3.root)["A"]["state"] == S.BLOCKED and len(fx3.launched) == 2, "and it reads BLOCKED, not rebuilt: %s %s" % (S.reading(store3.root)["A"], [x[1] for x in fx3.launched]))
    # malformed worker output never crashes the pass; a new build gets fresh blind judges
    store4 = relentless.Store(os.path.join(tmp, "s4root"))
    g4 = item(built_sha="abc1234", title="Gate")
    fx4 = Fx(os.path.join(tmp, "s4"), [("G", g4, "needs=owner", "q", None)])
    S.tick(store4, fx4, r, 1000, [], relentless)
    m4 = manifest(os.path.join(fx4.show_root, "G"), built_by=fx4.launched[-1][1])
    m4.pop("_dir")
    json.dump(dict(m4, stations=1, mods=5), open(os.path.join(fx4.show_root, "G", S.MANIFEST), "w"))
    fx4.live.clear()
    S.tick(store4, fx4, r, 1100, [], relentless)
    check(S.reading(store4.root)["G"]["state"] in (S.INCOMPLETE, S.BUILDING), "stations 1, mods 5: incomplete, no crash: %s"
          % S.reading(store4.root)["G"])
    st4 = S.load_state(store4)
    fx4.live.clear()
    st4["rows"]["G"].update(judge_tries=2, tries=0, phase=None, run=None, bridge=False)
    S.save_state(store4, st4)
    n = len(fx4.launched)
    S.tick(store4, fx4, r, 1200, [], relentless)
    check(len(fx4.launched) == n + 1 and S.load_state(store4)["rows"]["G"].get("judge_tries") == 0,
          "a new build starts with no spent judge tries")
    # a passing sheet showing goes STALE when the owed look now needs the item in place (a save)
    store5 = relentless.Store(os.path.join(tmp, "s5root"))
    look = [{"id": "A2", "level": "L4", "text": "the owner looks at the walker sprites"}]
    sk = item(built_sha="abc1234", title="Reskin the walker sprites", criteria=look, outstanding=["A2"])
    fx5 = Fx(os.path.join(tmp, "s5"), [("K", sk, "needs=owner", "", None)])
    d5 = os.path.join(fx5.show_root, "K")
    m5 = manifest(d5, built_by="u1")
    m5.pop("_dir")
    pre = os.path.join(d5, "s.prereview.json")
    open(pre, "w").write("{}")
    open(os.path.join(d5, "s.html"), "w").write("<html/>")
    json.dump(dict(m5, route="sheet", sheet=pre.replace("prereview.json", "html"), prereview=pre), open(os.path.join(d5, S.MANIFEST), "w"))
    m5s = dict(m5, route="sheet", sheet="/missing/s.html", prereview=pre, _dir=d5)
    check(S.complete(m5s) and S.complete(dict(m5s, sheet="http://x/s.html")) and S.complete(dict(m5s, sheet=pre, prereview="s.json")),
          "a sheet or prereview that is not there is incomplete")
    json.dump({"judged_by": "u2", "sha": "abc1234", "verdict": "pass", "stations": {"1": "ok"}}, open(os.path.join(d5, S.JUDGE), "w"))
    st5 = S.load_state(store5)
    st5["rows"]["K"] = {"phase": None, "tries": 2, "enrolled": 0, "judged": "u2", "built_sha": "abc1234"}
    S.save_state(store5, st5)
    S.tick(store5, fx5, r, 1000, [], relentless)
    check(S.reading(store5.root)["K"]["state"] == S.READY, "the sheet showing reads ready: %s" % S.reading(store5.root)["K"])
    st5 = S.load_state(store5)
    st5["rows"]["K"]["judge_digest"] = S.digest(d5, S.read_json(os.path.join(d5, S.MANIFEST)))
    S.save_state(store5, st5)
    open(pre, "w").write('{"changed": 1}')
    check(S.digest(d5, S.read_json(os.path.join(d5, S.MANIFEST))) != st5["rows"]["K"]["judge_digest"],
          "a sheet's prereview changed since the judge read it changes the digest that voids the pass")
    st5["rows"]["K"].pop("judge_digest")
    S.save_state(store5, st5)
    sk.criteria = [{"id": "A2", "level": "L4", "text": "the owner looks at the walker sprites live in game"}]
    S.tick(store5, fx5, r, 1100, [], relentless)
    check(S.reading(store5.root)["K"]["state"] in (S.STALE, S.BUILDING) and fx5.launched,
          "its look now needs a save: STALE, rebuilt with new tries: %s" % S.reading(store5.root)["K"])
    # switched off mid-build: the run is stopped, then its bridge released and its row gone
    store6 = relentless.Store(os.path.join(tmp, "s6root"))
    fx6 = Fx(os.path.join(tmp, "s6"), [("A", item(built_sha="abc1234", title="Drawbridge"), "needs=owner", "q", None)])
    S.tick(store6, fx6, r, 1000, [], relentless)
    u6 = fx6.launched[-1][1]
    off = {"showings": {"enabled": False}, "seat": "BENCH"}
    acts = []
    S.tick(store6, fx6, off, 1010, acts, relentless)
    check(u6 not in fx6.live and any(x["do"] == "showing_stopped" for x in acts), "switched off: its running build is stopped")
    S.tick(store6, fx6, off, 1020, [], relentless)
    check(fx6.releases == 1 and not S.load_state(store6)["rows"], "then its bridge released and its row gone")
    store2 = relentless.Store(os.path.join(tmp, "s2root"))
    h = item(built_sha=None, cited_shas=[], title="Gate")
    fx2 = Fx(os.path.join(tmp, "s2"), [("H", h, "needs=owner", "q", None)])
    S.tick(store2, fx2, r, 1000, [], relentless)
    manifest(os.path.join(fx2.show_root, "H"), sha="feed123", built_by=fx2.launched[0][1])
    fx2.live.clear()
    S.tick(store2, fx2, r, 1100, [], relentless)
    check(S.reading(store2.root)["H"]["state"] in (S.UNJUDGED, S.JUDGING), "no ledger sha: the HEAD it was built at stands, not STALE: %s"
          % S.reading(store2.root)["H"])


def owner_hold_rows(tmp):
    """The real cli: an OWNER hold refuses Relentless's `bridge take --idle-ok`, the call every showing and staging makes."""
    base = {k: v for k, v in os.environ.items() if k not in (
        "RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "CLAUDECODE", "RIMFLOW_RAN_BY", "RM_DRIVER_PID",
        "RIMFLOW_BRIDGE_SEAT", "RELENTLESS_SUPERVISOR", "RM_HOST_GUARD_GEN")}
    os.makedirs(os.path.join(tmp, "items"), exist_ok=True)
    base.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(tmp, "items"),
                RIMFLOW_SHARED_BRIDGE=os.path.join(tmp, "shared.json"), RIMFLOW_PROBE="no-reading",
                RIMFLOW_DISPATCH_LOCK=os.path.join(tmp, "dispatch.lock"), RIMFLOW_BRIDGE_LOCK=os.path.join(tmp, "bridge.lock"),
                RIMFLOW_OWNER_ACT_STAMP=os.path.join(tmp, "act.json"), RIMFLOW_DRIVER_LOCK="")

    def rf(env, *a):
        p = subprocess.run([sys.executable, CLI, *a], env=dict(base, **env), capture_output=True, text=True, timeout=120, cwd=tmp)
        return p.returncode, p.stdout + p.stderr
    owner = {"RIMFLOW_SEAT": "OWNER"}
    rel = {"RIMFLOW_SEAT": "BENCH", "RIMFLOW_BRIDGE_SEAT": "RELENTLESS", "RIMFLOW_BRIDGE_SEAT_IN_TEST": "1"}
    rc, out = rf(owner, "bridge", "take", "--for", "the owner's drawbridge session")
    check(rc == 0, "the owner takes the bridge: %s" % out[-120:])
    rc, out = rf(rel, "bridge", "take", "--idle-ok", "--for", "relentless showing A: review savegame")
    check(rc != 0, "Relentless's showing take --idle-ok is refused under his hold: %s" % out[-120:])
    rc, out = rf(rel, "bridge", "take", "--idle-ok", "--for", "relentless staging A: deploy and restart")
    check(rc != 0, "and so is a staging take: nothing deploys or restarts under it")
    rc, out = rf(owner, "bridge", "release")
    check(rc == 0, "the owner releases it: %s" % out[-120:])
    rc, out = rf({"RIMFLOW_SEAT": "BENCH"}, "bridge", "take", "--for", "the Conductor's live session")
    check(rc == 0, "the Conductor's window takes it: %s" % out[-120:])
    rc2, out2 = rf(rel, "bridge", "take", "--idle-ok", "--for", "relentless showing A")
    check(rc2 != 0, "under the Conductor's hold too (whoever holds it): %s" % out2[-120:])


def blocker_rows(tmp):
    """2026-11-05: the drawbridge showing was built on the 10-22 ask while his 11-03 spec on a successor was unbuilt."""
    now = time.mktime((2026, 11, 5, 4, 0, 0, 0, 0, 0)) - time.timezone
    moat = item(built_sha="abc1234", built_at="2026-10-22T10:00:00Z", blocked=False, superseded_by=None, caused_by=None)
    up = item(blocked=False, superseded_by=None, caused_by=None)      # DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED, unbuilt
    items = {"DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS": moat, "DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED": up}
    spec = {"seat": "OWNER", "event": "note", "id": "DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED", "ts": "2026-11-03T21:00:00Z",
            "text": "holds 55/85/75, no plank stack, no double leaves"}
    got = S.blockers("DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS", moat, items, [spec], now)
    check(got and got[0] == "DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED", "his 11-03 note on an open same-subject item blocks the showing: %s" % (got,))
    up.open = False
    check(S.blockers("DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS", moat, items, [spec], now) is None, "once that item is built and closed, no block")
    up.open = True
    old = dict(spec, ts="2026-10-01T00:00:00Z")
    check(S.blockers("DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS", moat, items, [old], now) is None, "a note older than 14 days does not block")
    check(S.blockers("DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS", moat, items, [spec], now, lambda i: i == "DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED") is None,
          "a sibling itself waiting only on his look does not block")
    own = dict(spec, id="DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS")
    got = S.blockers("DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS", moat, items, [own], now)
    check(got and got[0] == "DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS", "his note on the item after its build blocks it: %s" % (got,))
    kid = item(caused_by="DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS", blocked=False, superseded_by=None)
    got = S.blockers("DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS", moat, {"DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS": moat, "WINCH_X": kid}, [], now)
    check(got and got[0] == "WINCH_X", "an open child blocks it: %s" % (got,))
    hand = item(blocked=True, blocked_on="DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED", blocked_reason="his spec first")
    got = S.blockers("X", hand, {}, [], now)
    check(got and got[0] == "DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED", "a ledger block blocks it: %s" % (got,))
    # through the stage: a blocked item reads BLOCKED, never builds, never READY even with a passing showing on disk
    r = {"showings": {"enabled": True}, "seat": "BENCH"}
    store = relentless.Store(os.path.join(tmp, "broot"))
    fx = Fx(os.path.join(tmp, "b"), [("DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS", moat, "needs=owner", "q", got)])
    d = os.path.join(fx.show_root, "DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS")
    manifest(d, built_by="u1")
    json.dump({"judged_by": "u2", "sha": "abc1234", "verdict": "pass", "stations": {"1": "ok"}}, open(os.path.join(d, S.JUDGE), "w"))
    S.tick(store, fx, r, 1000, [], relentless)
    row = S.reading(store.root)["DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS"]
    check(row["state"] == S.BLOCKED and row["blocked_on"] == "DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED" and not fx.launched,
          "the stage: BLOCKED on the successor, nothing built, never READY TO SHOW: %s" % row)


def harden_rows(tmp):
    """SHOWINGS_HARDEN_FLYERS_OUT_SUBJECTS_TIGHT: a flyer's flight is never pre-built (by rule, no ledger block), the
    same-subject test is the item family or a named defName (not the first id word), and a laid-hose look is a save."""
    now = time.mktime((2026, 11, 5, 4, 0, 0, 0, 0, 0)) - time.timezone
    lr = __import__("relentless_live").live_rules({})
    bird = item(id="MYNOCK_BUILD_WINGS_AT_LAST", title="Mynock flies over the canyon", blocked=False)
    check(S.flyer(bird, "does it fly right", lr), "a flyer's flight is caught by rule, with no ledger block")
    look = [{"id": "A4", "level": "L4", "text": "the owner looks at the mynock in flight"}]
    check(S.flyer(item(title="Mynock roost", criteria=look, outstanding=["A4"]), "", lr), "an owed criterion naming flight is caught")
    check(S.flyer(item(title="Gravship flies to the seabed layer"), "", lr) is None, "a vehicle's flight is no flyer's")
    check(S.flyer(item(title="Drawbridge over a moat"), "is the moat right", lr) is None, "a drawbridge is no flyer")
    r = {"showings": {"enabled": True}, "seat": "BENCH"}
    store = relentless.Store(os.path.join(tmp, "froot"))
    fx = Fx(os.path.join(tmp, "f"), [("MYNOCK_BUILD_WINGS_AT_LAST", bird, "needs=owner", "does it fly right", None)])
    S.tick(store, fx, r, 1000, [], relentless)
    row = S.reading(store.root)["MYNOCK_BUILD_WINGS_AT_LAST"]
    check(row["state"] == S.JOINT and not fx.launched and fx.takes == 0,
          "the stage: a flyer reads JOINT SESSION, no bridge taken, nothing built: %s" % row)
    # the subject: family words, one a word-prefix of the other, not the first id word
    check(S.same_family("DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS", "DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED"), "DRAWBRIDGE and DRAWBRIDGE_UP are one family")
    check(not S.same_family("REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH", "REEL_HOSE_FIX_KINKS_EVERYWHERE"), "REEL_NOZZLE and REEL_HOSE are not")
    check(not S.same_family("PIPE_ELBOW_BUILD_BENDS_AT_LAST", "PIPE_VALVE_FIX_LEAKS_LESS"), "PIPE_ELBOW and PIPE_VALVE are not")
    check(S.same_family("WATER_TOWER_2", "WATER_TOWER_FIX_STANDS_TALL"), "a legacy _N id: its words without the number")
    reel = item(title="Redrawn reel: coupler beneath the outlet of RM_HoseReel", blocked=False, superseded_by=None, caused_by=None,
                built_at="2026-10-23T14:14:20Z")
    hose = item(title="Hose kinks", blocked=False, superseded_by=None, caused_by=None)
    items = {"REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH": reel, "REEL_HOSE_FIX_KINKS_EVERYWHERE": hose}
    note = {"seat": "OWNER", "event": "note", "id": "REEL_HOSE_FIX_KINKS_EVERYWHERE", "ts": "2026-11-03T21:00:00Z", "text": "kinks at bends"}
    check(S.blockers("REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH", reel, items, [note], now) is None,
          "his note on another reel family does not block")
    named = dict(note, text="the RM_HoseReel outlet is wrong too")
    got = S.blockers("REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH", reel, items, [named], now)
    check(got and got[0] == "REEL_HOSE_FIX_KINKS_EVERYWHERE" and "RM_HoseReel" in got[1],
          "his note naming the showing's defName blocks it across families: %s" % (got,))
    # the route: REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH's look is a laid hose in place, a save not a sheet
    a2 = [{"id": "A2", "level": "L4", "text": "owner looks at a south-facing Scrapper reel with laid hose: brass coupling drawn over the open outlet bore"}]
    rt = S.route(item(id="REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH", criteria=a2, outstanding=["A2"],
                      title="Redrawn reel (south facing, Scrapper): the laid hose's coupler draws BENEATH the reel's drawn open outlet pipe"))
    check(rt == "save", "the reel's laid-hose look takes the save route: %s" % rt)
    check(S.route(item(title="Gate, south facing")) == "save", "'facing' is no art word")
    check(S.route(item(title="Reskin the walker sprites")) == "sheet", "a reskin still takes the sheet route")
    check(S.flyer(item(title="Redraw the mynock flight frames"), "", lr) and
          S.route(item(title="Redraw the mynock flight frames")) == "sheet", "a flyer's frames on a sheet are art, not flight: the rule is for the save route")


def wiring_rows():
    src = open(os.path.join(HERE, "relentless.py"), encoding="utf-8").read()
    check("relentless_showing.tick(store, fx, r, now, acts" in src, "relentless.tick runs the showing stage")
    rules = json.load(open(os.path.join(HERE, "relentless_rules.json"), encoding="utf-8"))
    check((rules.get("showings") or {}).get("enabled") is True, "the stage is on in relentless_rules.json")


def main():
    tmp = tempfile.mkdtemp(prefix="rs_show_")
    try:
        trigger_rows()
        status_rows(tmp)
        tick_rows(tmp)
        blocker_rows(tmp)
        harden_rows(tmp)
        owner_hold_rows(os.path.join(tmp, "cli"))
        wiring_rows()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
