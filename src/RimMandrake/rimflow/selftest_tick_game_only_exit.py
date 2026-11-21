#!/usr/bin/env python3
"""selftest_tick_game_only_exit: the promises of design/specs/2026-11-20-tick-game-only-exit/boundary.md, one test per
promise, each named as the promise is. At an offline stage whose open road-back items all need the live game, the tick
takes the game-only exit itself (the act autogameonly: `maturation.py advance --to in_game --game-only`, landed), once
the version's own open offline Problems have closed; before this the row only printed that move for a hand, and
FlowWorks sat at Stage 3 for 515 minutes (item RIMMANDRAKE_UNPARK_FLOWWORKS_STUCK_AT_OFFLINE_STAGE_EIGHT_HOURS).
Offline, on temp roots; no claude, unit, bridge or real landing is touched."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="tick_game_only_")
os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(TMP, "_dispatch")   # never the live dispatcher's state
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "_dispatcher")
os.environ["RM_REFUSAL_DIR"] = os.path.join(TMP, "_refusals")               # never the live refusal store
os.environ["RM_OPS_WATCH_DIR"] = os.path.join(TMP, "_ops")
os.environ["RM_STAGE_LAND"] = "0"
for _k in ("RM_MODLEDGER_WRITER", "RM_MODLEDGER_TOKEN", "RM_ROLE_UNIT"):
    os.environ.pop(_k, None)
import maturation_autonomy as A     # noqa: E402
import maturation as M              # noqa: E402
import maturation_dispatch as MD    # noqa: E402
import modledger as L               # noqa: E402

PILOT = (L.config().get("pilot_mods") or ["ExplosiveKnockback"])[0]
VER = "0.1.0"
LIVE_A, LIVE_B = "RIMMANDRAKE_PROVE_X_LIVE_ONE_A", "RIMMANDRAKE_PROVE_X_LIVE_TWO_B"
BUG_V = "RIMMANDRAKE_REBUILD_X_VERSION_PROBLEM_V"
ALL_LIVE = [{"id": LIVE_A, "needs": "game-up"}, {"id": LIVE_B, "needs": "bridge"}]
ROUTE = "RIMMANDRAKE_ROUTE_X_VISIT_TWO_FAILURES_BACK"


def road_back(items, stage="offline_build", bugs=(), s=None):
    s = s if s is not None else {"road_back": {"caused_by": ROUTE}}
    row = {"mod": PILOT, "stage": stage}
    A._road_back(s, row, lambda ids: items, 100, ver=VER,
                 version_bugs=(lambda m, v: None) if bugs is None else (lambda m, v: list(bugs)))
    return row, s


class It(object):
    def __init__(self, iid, title, kind="bug", needs="offline", state="proposed", idx=0):
        self.id, self.title, self.kind, self.needs, self.state, self.created_index = iid, title, kind, needs, state, idx


def t_game_only_road_back_takes_the_exit():
    row, _ = road_back(ALL_LIVE)
    return (row.get("aut") == "autogameonly" and row.get("decision") == "autogameonly"
            and row.get("game_only_items") == [LIVE_A, LIVE_B] and not row.get("fix_item") and not row.get("need")
            and str(row.get("steward_key") or "").startswith("%s|offline_build|game_only|" % VER)
            and "autogameonly" in A.ACTS and "autogameonly" in MD.NO_SLOT_AUT), row


def t_version_bug_goes_before_the_exit():
    row, _ = road_back(ALL_LIVE, bugs=[{"id": BUG_V, "needs": "offline"}])
    brief = A.fixer_brief(BUG_V, PILOT, 15, row.get("fix_for"))
    return (row.get("aut") == "fixer" and row.get("fix_item") == BUG_V and row.get("fix_for") == "version"
            and row.get("decision") == "fixer" and not row.get("game_only_items")
            and "Road-back fix" not in brief and "drop the item" not in brief and BUG_V in brief
            and "Never take the bridge" in brief), (row, brief[:300])


def t_spent_version_bug_holds_the_exit():
    s = {"road_back": {"caused_by": ROUTE}, "fixers": {BUG_V: {"unit": "u1", "at": 50, "failed": None, "tries": 1}}}
    row, _ = road_back(ALL_LIVE, bugs=[{"id": BUG_V, "needs": "offline"}], s=s)
    return (row.get("decision") == "fixer_spent" and not row.get("aut") and BUG_V in str(row.get("need"))
            and "--game-only" in str(row.get("need"))), row


def t_unreadable_version_bugs_take_no_exit():
    row, _ = road_back(ALL_LIVE, bugs=None)
    return row.get("decision") == "blind" and not row.get("aut"), row


def t_version_bugs_read_by_title_kind_and_needs():
    t = "%s %s" % (PILOT, VER)
    items = {x.id: x for x in (
        It("B_LATE", t + ", Convergent (a Problem): later", idx=9),
        It("B_EARLY", t + ", Convergent (a Problem): earlier", idx=3),
        It("B_DONE", t + ": closed", state="done", idx=1),
        It("B_TASK", t + ": a task", kind="task", idx=2),
        It("B_LIVE", t + " inv_x in game: a bug", needs="game-up", idx=4),
        It("B_NEXT", "%s 0.1.01: another version" % PILOT, idx=5),
        It("B_OTHER", "OtherMod %s: another mod" % VER, idx=6),
        It("B_NOVER", "%s: no version named" % PILOT, idx=7))}
    got = [x["id"] for x in A.version_bugs(PILOT, VER, items)]
    return got == ["B_EARLY", "B_LATE"] and A.version_bugs(PILOT, None, items) is None, got


def _root():
    root = tempfile.mkdtemp(prefix="r_", dir=TMP)
    cdir = os.path.join(root, "design", "concepts", PILOT)
    os.makedirs(os.path.join(cdir, "version"))
    L.append(root, PILOT, "DISPATCH", "version.open", "version", body={"version": VER}, version=VER)
    ev = os.path.join(root, "infrastructure", "state", "ledger", "events")
    os.makedirs(ev)
    with open(os.path.join(ev, "BENCH.jsonl"), "w", encoding="utf-8") as fh:
        for e in ({"event": "file", "id": LIVE_A, "caused_by": ROUTE, "needs": "game-up"},
                  {"event": "file", "id": LIVE_B, "caused_by": ROUTE, "needs": "bridge"},
                  {"event": "file", "id": "RIMMANDRAKE_FIX_X_OFFLINE_C", "caused_by": ROUTE, "needs": "offline"},
                  {"event": "close", "id": "RIMMANDRAKE_FIX_X_OFFLINE_C", "sha": "abc1234"}):
            fh.write(json.dumps(e) + "\n")
    with open(os.path.join(cdir, "version", "VERSION.json"), "w") as f:
        json.dump({"version": VER}, f)
    with open(os.path.join(cdir, M.RECORD), "w") as f:
        json.dump({"mod": PILOT, "version": VER, "stage": "offline_build", "cycles": {"visit": 3, "total": 4},
                   "moves": [{"from": "blind_challenge", "to": "in_game", "at": "2026-11-19T20:41:00-08:00"},
                             {"from": "in_game", "to": "offline_build", "at": "2026-11-19T23:54:35-08:00"}]}, f)
    with open(os.path.join(cdir, "journal.md"), "w") as f:
        f.write("# %s\n\n- **Stage now:** Stage 3.\n- **Waiting on:** the game.\n" % PILOT)
    return root, cdir


def _snap(cdir):
    out = {}
    for d, _, fs in os.walk(cdir):
        for n in fs:
            p = os.path.join(d, n)
            with open(p, "rb") as f:
                out[os.path.relpath(p, cdir)] = f.read()
    return out


def t_act_advances_and_lands():
    root, cdir = _root()
    landed = []
    text = A.gameonly_and_land(root, PILOT, [LIVE_A, LIVE_B], now=100,
                               land=lambda subject, paths: landed.append((subject, sorted(paths))) or "PUBLISHED abc")
    rec = M.load(root, PILOT)
    mv = (rec.get("moves") or [{}])[-1]
    paths = landed[0][1] if landed else []
    rel = "design/concepts/%s/" % PILOT
    return (text == "PUBLISHED abc" and rec.get("stage") == "in_game" and mv.get("by") == "DISPATCH"
            and mv.get("confirmed", {}).get("game_only") == "%s, %s" % (LIVE_A, LIVE_B)
            and rel + M.RECORD in paths and rel + "journal.md" in paths
            and all(p.startswith(rel) for p in paths) and len(landed) == 1), (text, rec.get("stage"), mv, landed)


def t_unlanded_act_puts_files_back():
    root, cdir = _root()
    was = _snap(cdir)

    def boom(subject, paths):
        raise RuntimeError("land.sh exited 1")
    try:
        A.gameonly_and_land(root, PILOT, [LIVE_A, LIVE_B], now=100, land=boom)
        raised = False
    except RuntimeError:
        raised = True
    now = _snap(cdir)
    return raised and now == was, (raised, sorted(set(now) ^ set(was)),
                                   [k for k in was if now.get(k) != was[k]])


def t_refused_act_raises_and_writes_nothing():
    root, cdir = _root()
    was = _snap(cdir)
    landed = []
    try:
        A.gameonly_and_land(root, PILOT, [LIVE_A], now=100,          # LIVE_B, an open sibling, unnamed: refused
                            land=lambda subject, paths: landed.append(paths) or "PUBLISHED x")
        raised = False
    except RuntimeError as e:
        raised = "game_only" in str(e)
    return raised and not landed and _snap(cdir) == was, (raised, landed)


def t_execute_books_the_act_once():
    st = {"mods": {PILOT: {}}}
    row, _ = road_back(ALL_LIVE)
    got = []
    A.execute(TMP, {"seat": "BENCH"}, st, [row], [PILOT], 100, fx={
        "known": lambda: set(), "autogameonly": lambda root, mod, ids, now=None: got.append(list(ids)) or "PUBLISHED s1"})
    x = (st["mods"][PILOT].get("steward") or {}).get(row.get("steward_key"))
    return (got == [[LIVE_A, LIVE_B]] and row.get("decision") == "launched" and x and x.get("landed") == "PUBLISHED s1"
            and x.get("items") == [LIVE_A, LIVE_B] and not x.get("failed")), (got, row.get("decision"), x)


def t_pilot_holder_skips_game_only_set_at_offline_stage():
    s = {"road_back": {"caused_by": ROUTE, "at": 50, "from": "in_game"}}
    rows = [{"mod": PILOT, "stage": "offline_build", "decision": "fixer", "aut": "fixer", "fix_item": BUG_V,
             "fix_for": "version"}]
    facts = {PILOT: {"stage": "offline_build", "live_units": []}}
    fx = {"open_items": lambda ids: list(ALL_LIVE), "account": lambda: (True, "ok"), "pilot": lambda root, mod: True}
    rs, la = MD.pilot_holders(TMP, {"cap_usd": 15, "max_live": 4, "seat": "BENCH"}, {"mods": {PILOT: s}}, facts,
                              rows, [PILOT], 100, fx)
    spent = [{"mod": PILOT, "stage": "offline_build", "decision": "fixer_spent", "aut": None}]
    rs2, _ = MD.pilot_holders(TMP, {"cap_usd": 15, "max_live": 4, "seat": "BENCH"}, {"mods": {PILOT: dict(s)}}, facts,
                              spent, [], 100, fx)
    return (rs[0].get("aut") == "fixer" and rs[0].get("fix_item") == BUG_V and not rs[0].get("holder_items")
            and rs2[0].get("decision") == "fixer_spent" and not rs2[0].get("holder_items")), (rs[0], rs2[0])


def main():
    tests = [t_game_only_road_back_takes_the_exit, t_version_bug_goes_before_the_exit,
             t_spent_version_bug_holds_the_exit, t_unreadable_version_bugs_take_no_exit,
             t_version_bugs_read_by_title_kind_and_needs, t_act_advances_and_lands, t_unlanded_act_puts_files_back,
             t_refused_act_raises_and_writes_nothing, t_execute_books_the_act_once,
             t_pilot_holder_skips_game_only_set_at_offline_stage]
    fails = []
    for fn in tests:
        try:
            good, got = fn()
        except Exception as e:  # noqa: BLE001 - a test that raises is a failure by name, never a pass
            good, got = False, "%s: %s" % (type(e).__name__, e)
        print("%s  %s%s" % ("PASS" if good else "FAIL", fn.__name__[2:].replace("_", "-"),
                            "" if good else "  got: %s" % str(got)[:600]))
        if not good:
            fails.append(fn.__name__)
    shutil.rmtree(TMP, ignore_errors=True)
    if fails:
        print("FAIL selftest_tick_game_only_exit: %d of %d red" % (len(fails), len(tests)))
        return 1
    print("PASS selftest_tick_game_only_exit: %d tests" % len(tests))
    return 0


if __name__ == "__main__":
    sys.exit(main())
