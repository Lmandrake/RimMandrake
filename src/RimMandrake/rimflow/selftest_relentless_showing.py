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


def manifest(d, sha="abc123", mods=None, built_by="rm-show-u1"):
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "s1.png"), "wb").write(b"x")
    m = {"item": "A", "sha": sha, "route": "save", "save": "Showing_A", "mods": mods or [], "minutes": 4,
         "stations": [{"n": 1, "label": "1 moat", "shows": "the moat", "judge": "does it read", "capture": "s1.png"}],
         "built_by": built_by}
    json.dump(m, open(os.path.join(d, S.MANIFEST), "w"))
    m["_dir"] = d
    return m


def status_rows(tmp):
    d = os.path.join(tmp, "st")
    check(S.status(None, None, "abc", None, None)[0] == S.OWED, "nothing built reads OWED")
    m = manifest(d)
    check(S.status(m, None, "abc123", None, None)[0] == S.UNJUDGED, "built, not judged: not ready")
    j = {"judged_by": "rm-showj-u2", "sha": "abc123", "verdict": "pass"}
    check(S.status(m, j, "abc123", None, "rm-showj-u2")[0] == S.READY, "a pass from the launched blind judge: READY TO SHOW")
    check(S.status(m, dict(j, judged_by="rm-show-u1"), "abc123", None, "rm-show-u1")[0] == S.UNJUDGED,
          "the builder judging its own showing is no judge")
    check(S.status(m, j, "abc123", None, "rm-showj-other")[0] == S.UNJUDGED, "a judge.json the supervisor did not launch is no judge")
    check(S.status(m, dict(j, verdict="fail"), "abc123", None, "rm-showj-u2")[0] == S.FAILED, "a fail is not ready")
    check(S.status(m, j, "def456", None, "rm-showj-u2")[0] == S.STALE, "a new item sha makes it STALE")
    mods = os.path.join(tmp, "Mods", "Moat")
    os.makedirs(mods)
    open(os.path.join(mods, "a.xml"), "w").write("1")
    fp = S.mods_fp(["Moat"], os.path.join(tmp, "Mods"))
    m2 = dict(m, deployed=fp)
    check(S.status(m2, j, "abc123", fp, "rm-showj-u2")[0] == S.READY, "same deployed mod: still ready")
    time.sleep(0.01)
    open(os.path.join(mods, "a.xml"), "w").write("22")
    fp2 = S.mods_fp(["Moat"], os.path.join(tmp, "Mods"))
    check(fp2 != fp and S.status(m2, j, "abc123", fp2, "rm-showj-u2")[0] == S.STALE, "a changed deployed mod makes it STALE")
    os.remove(os.path.join(d, "s1.png"))
    check(S.status(m, j, "abc123", None, "rm-showj-u2")[0] == S.INCOMPLETE, "a capture missing on disk is not ready")


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
    a, b = item(built_sha="abc123", title="Drawbridge"), item(built_sha="fff000", title="Gate")
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
    json.dump({"judged_by": ju, "sha": "abc123", "verdict": "pass"}, open(os.path.join(fx.show_root, "A", S.JUDGE), "w"))
    fx.live.discard(ju)
    S.tick(store, fx, r, 1300, [], relentless)
    got = S.reading(store.root)["A"]
    check(got["state"] == S.READY and got["save"] == "Showing_A" and got["minutes"] == 4 and got["dir"].endswith("showings\\A"),
          "after the blind pass A reads READY TO SHOW with its save, time and folder: %s" % got)
    a.built_sha = "abc999"
    S.tick(store, fx, r, 1400, [], relentless)
    check(S.reading(store.root)["A"]["state"] in (S.STALE, S.BUILDING, S.OWED) and S.reading(store.root)["A"]["state"] != S.READY,
          "a new sha: A is no longer ready: %s" % S.reading(store.root)["A"])
    fx.items = rows[1:]
    S.tick(store, fx, r, 1500, [], relentless)
    check("A" not in S.reading(store.root), "an item no longer waiting on his look leaves the reading")


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
    rc, out = rf({"RIMFLOW_SEAT": "BENCH"}, "bridge", "take", "--for", "the Conductor's live session")
    rc2, out2 = rf(rel, "bridge", "take", "--idle-ok", "--for", "relentless showing A")
    check(rc2 != 0, "under the Conductor's hold too (whoever holds it): %s" % out2[-120:])


def blocker_rows(tmp):
    """2026-11-05: the drawbridge showing was built on the 10-22 ask while his 11-03 spec on a successor was unbuilt."""
    now = time.mktime((2026, 11, 5, 4, 0, 0, 0, 0, 0)) - time.timezone
    moat = item(built_sha="abc123", built_at="2026-10-22T10:00:00Z", blocked=False, superseded_by=None, caused_by=None)
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
    json.dump({"judged_by": "u2", "sha": "abc123", "verdict": "pass"}, open(os.path.join(d, S.JUDGE), "w"))
    S.tick(store, fx, r, 1000, [], relentless)
    row = S.reading(store.root)["DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS"]
    check(row["state"] == S.BLOCKED and row["blocked_on"] == "DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED" and not fx.launched,
          "the stage: BLOCKED on the successor, nothing built, never READY TO SHOW: %s" % row)


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
        owner_hold_rows(os.path.join(tmp, "cli"))
        wiring_rows()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
