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
import game_names as _GN             # noqa: E402  (a game reads by its name on this machine: ArchBig, ArchSmall)

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
            # it closes offline and runs its touched in-game check on a free game (owner, 2026-11-24)
            and "maturation.py live-row" in brief and "Never take the bridge" not in brief), (row, brief[:300])


def t_spent_version_bug_holds_the_exit():
    s = {"road_back": {"caused_by": ROUTE}, "fixers": {BUG_V: {"unit": "u1", "at": 50, "failed": None, "tries": 1}}}
    row, _ = road_back(ALL_LIVE, bugs=[{"id": BUG_V, "needs": "offline"}], s=s)
    return (row.get("decision") == "fixer_spent" and not row.get("aut") and BUG_V in str(row.get("need"))
            and "--game-only" in str(row.get("need"))), row


def t_unreadable_version_bugs_take_no_exit():
    row, _ = road_back(ALL_LIVE, bugs=None)
    # the real reader on a ledger that raises: a could-not-look answer (probe_result), read blind with its cause
    real = A.ledger_items

    def broken():
        raise OSError("ledger locked")
    A.ledger_items = broken
    try:
        ans = A.read_version_bugs(PILOT, VER)
        row2 = {"mod": PILOT, "stage": "offline_build"}
        A._road_back({"road_back": {"caused_by": ROUTE}}, row2, lambda ids: ALL_LIVE, 100, ver=VER,
                     version_bugs=A.read_version_bugs)
    finally:
        A.ledger_items = real
    noversion = A.read_version_bugs(PILOT, None)
    good = (row.get("decision") == "blind" and not row.get("aut")
            and getattr(ans, "kind", None) == "could_not_look" and "ledger locked" in str(ans.cause)
            and row2.get("decision") == "blind" and not row2.get("aut") and "ledger locked" in row2.get("why", "")
            and getattr(noversion, "kind", None) == "could_not_look")
    return good, {"row": row, "answer": repr(ans), "row2": row2, "noversion": repr(noversion)}


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


def t_a_file_git_ignores_is_never_landed():
    """The move's own lock (design/concepts/*/.stage_move.lock, in .gitignore) was handed to land.sh, which refused
    it: FlowWorks' game-only exit failed at 9:24 PM PST 2026-11-20 ("The following paths are ignored")."""
    import subprocess
    root, cdir = _root()
    subprocess.run(["git", "init", "-q", root], check=True)
    with open(os.path.join(root, ".gitignore"), "w") as f:
        f.write("design/concepts/*/.stage_move.lock\n")
    landed = []
    A.gameonly_and_land(root, PILOT, [LIVE_A, LIVE_B], now=100,
                        land=lambda subject, paths: landed.append(sorted(paths)) or "PUBLISHED abc")
    paths = landed[0] if landed else []
    made = os.path.exists(os.path.join(cdir, ".stage_move.lock"))
    return (made and paths and not any(x.endswith(".stage_move.lock") for x in paths)
            and "design/concepts/%s/%s" % (PILOT, M.RECORD) in paths), (made, paths)


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
        "known": lambda: set(), "autogameonly": lambda root, mod, ids, now=None, **k: got.append(list(ids)) or "PUBLISHED s1"})
    x = (st["mods"][PILOT].get("steward") or {}).get(row.get("steward_key"))
    return (got == [[LIVE_A, LIVE_B]] and row.get("decision") == "launched" and x and x.get("landed") == "PUBLISHED s1"
            and x.get("items") == [LIVE_A, LIVE_B] and not x.get("failed")), (got, row.get("decision"), x)


CFG2 = {"cap_usd": 15, "max_live": 4, "seat": "BENCH", "game_instances": ["a", "b"]}
FACTS = {PILOT: {"stage": "offline_build", "live_units": []}}


def _bridge(free):
    """A bridge reading that names its game (pick_game's two-argument form): free is the set of takeable games."""
    def read(purpose, game="a"):
        return (True, "TAKEABLE  delegated") if game in free else (False, "NOT TAKEABLE  game %s: rm-pyrelands-visit "
                                                                         "holds the driver lock" % game)
    return read


def _spent_rows():
    return [{"mod": PILOT, "stage": "offline_build", "decision": "fixer_spent", "aut": None,
             "why": "spent", "need": "%s: PAUSED, the game-only exit waits on ..." % PILOT}]


def _fx(free):
    return {"open_items": lambda ids: list(ALL_LIVE), "account": lambda: (True, "ok"), "pilot": lambda root, mod: True,
            "bridge": _bridge(free), "hold": lambda g: None}


def _s():
    return {"road_back": {"caused_by": ROUTE, "at": 50, "from": "in_game"}}


def t_pilot_holder_waits_for_the_version_problem_fixer():
    rows = [{"mod": PILOT, "stage": "offline_build", "decision": "fixer", "aut": "fixer", "fix_item": BUG_V,
             "fix_for": "version"}]
    rs, la = MD.pilot_holders(TMP, CFG2, {"mods": {PILOT: _s()}}, FACTS, rows, [PILOT], 100, _fx({"a", "b"}))
    return (rs[0].get("aut") == "fixer" and rs[0].get("fix_item") == BUG_V and not rs[0].get("holder_items")), rs[0]


def t_a_spent_game_only_set_goes_to_a_free_game():
    rs, la = MD.pilot_holders(TMP, CFG2, {"mods": {PILOT: _s()}}, FACTS, _spent_rows(), [], 100, _fx({"b"}))
    r = rs[0]
    # a game a live in-game run drives is not free, whatever its bridge reading says
    facts = {PILOT: dict(FACTS[PILOT]), "Pyrelands": {"stage": "in_game", "live_units": ["rm-pyr"],
                                                      "ingame_live": ["rm-pyr"], "ingame_games": {"rm-pyr": "a"}}}
    rs2, _ = MD.pilot_holders(TMP, CFG2, {"mods": {PILOT: _s()}}, facts, _spent_rows(), [], 100, _fx({"a", "b"}))
    return (PILOT in la and r.get("decision") == "launch" and r.get("holder_game") == "b"
            and [x["id"] for x in r.get("holder_items") or []] == [LIVE_A, LIVE_B] and _GN.show("b") in str(r.get("why"))
            and not r.get("need") and rs2[0].get("holder_game") == "b"), (r, rs2[0])


def t_no_free_game_names_each_game():
    rs, la = MD.pilot_holders(TMP, CFG2, {"mods": {PILOT: _s()}}, FACTS, _spent_rows(), [], 100, _fx(set()))
    r = rs[0]
    text = "%s | %s" % (r.get("why"), r.get("waits_on"))
    return (PILOT not in la and r.get("decision") == "no_game_free" and not r.get("holder_items")
            and _GN.show("a") + ":" in text and _GN.show("b") + ":" in str(r.get("why"))
            and _GN.show("b") + ":" in str(r.get("waits_on"))
            and not r.get("need") and "no_game_free" in A.WAIT and "the live game" not in text), r


def t_the_offline_holder_run_drives_its_named_game():
    seen = []

    def brief(item, text, model, cap, seat, env=None, **kw):
        seen.append((item, text, dict(env or {})))
        return 0, "DETACHED u", "u"
    saved = (M.ledger_needs, L.resume_plan, MD.ledger_open, MD.ledger_after)
    M.ledger_needs = lambda root, ids: {}
    L.resume_plan = lambda root, mod: {"action": "packet", "reconcile": False, "why": "-"}
    MD.ledger_open = lambda *a, **k: {"brief": a[3] if len(a) > 3 else k.get("brief", ""), "env": {}, "run": "r1",
                                      "packet": ""}
    MD.ledger_after = lambda *a, **k: "ledger ok"
    try:
        rc, text, unit, item = MD.road_back_holder(TMP, CFG2, {"mods": {PILOT: {}}}, PILOT, "offline_build",
                                                   list(ALL_LIVE), None, 15.0, 100, {"launch_brief": brief}, game="b")
    finally:
        M.ledger_needs, L.resume_plan, MD.ledger_open, MD.ledger_after = saved
    txt = seen[0][1] if seen else ""
    return (rc == 0 and unit == "u" and seen and seen[0][2].get("RM_GAME_INSTANCE") == "b" and "## Your game: %s" % _GN.show("b") in txt
            and "on %s" % _GN.show("b") in str(text)
            and "The bridge and the game" in txt and "Not yours" not in txt), (rc, text, txt[-900:])


def main():
    tests = [t_game_only_road_back_takes_the_exit, t_version_bug_goes_before_the_exit,
             t_spent_version_bug_holds_the_exit, t_unreadable_version_bugs_take_no_exit,
             t_version_bugs_read_by_title_kind_and_needs, t_act_advances_and_lands, t_a_file_git_ignores_is_never_landed,
             t_unlanded_act_puts_files_back,
             t_refused_act_raises_and_writes_nothing, t_execute_books_the_act_once,
             t_pilot_holder_waits_for_the_version_problem_fixer, t_a_spent_game_only_set_goes_to_a_free_game,
             t_no_free_game_names_each_game, t_the_offline_holder_run_drives_its_named_game]
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
