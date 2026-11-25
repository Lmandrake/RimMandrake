#!/usr/bin/env python3
"""selftest_list_shape.py - the Workshop Pipeline's Shape stage (list_shape.py, `rimflow shape`, the lane's Shape lines).

Item RIMMANDRAKE_BUILD_SHAPE_STAGE_CHECK_TESTS_THE_NEED_NOT_PAPER; page design/specs/2026-11-23-list-shape/boundary.md
(each t_ function is one promise of it, by name). Offline: a throwaway ledger (RIMFLOW_LEDGER / RIMFLOW_ITEMS), a
throwaway check root, fake lane facts and a fake launch. Written before the code; seen failing on the base
(list_shape.py absent, `rimflow shape` unknown).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CLI = os.path.join(HERE, "cli.py")
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
os.environ["RM_LIST_DISPATCH_DIR"] = tempfile.mkdtemp(prefix="ls_selftest_ld_")

FAILS = []
X = {}
NOW = 1_800_000_000.0
CFG = {"enabled": True, "max_live": 2, "max_chain_depth": 2, "max_runs_per_item": 2, "max_never_started": 2,
       "sonnet_cap_usd": 5, "opus_cap_usd": 12, "seat": "BENCH"}
R_OK = {"who": "owner", "ask": "pick one of two designs", "resumes": "his card answer"}


def chk(fn, what):
    try:
        cond = fn()
    except Exception as e:  # noqa: BLE001
        cond, what = False, "%s (raised %s: %s)" % (what, type(e).__name__, str(e)[:300])
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def LS():
    import list_shape
    return list_shape


def LD():
    import list_dispatch
    return list_dispatch


def page(name, text):
    p = os.path.join(X["root"], name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def cli(*args, seat="BENCH", unit=None):
    env = dict(os.environ)
    for k in ("CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "RM_ROLE_UNIT"):
        env.pop(k, None)
    env["RIMFLOW_SEAT"] = seat
    if unit:
        env["RM_ROLE_UNIT"] = unit
    r = subprocess.run([sys.executable, CLI] + list(args), cwd=REPO, env=env, capture_output=True, text=True,
                       timeout=180, stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout + r.stderr


def holds_cli(iid):
    r = subprocess.run([sys.executable, os.path.join(HERE, "list_shape.py"), "holds", iid], cwd=REPO,
                       env=dict(os.environ), capture_output=True, text=True, timeout=180, stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout + r.stderr


def events():
    import model as LM
    LM.EVENTS = os.environ["RIMFLOW_LEDGER"]
    return LM.read()


def world():
    import model as LM
    LM.EVENTS = os.environ["RIMFLOW_LEDGER"]
    LM.ITEMS = os.environ["RIMFLOW_ITEMS"]
    LM.CLOSED = os.path.join(LM.ITEMS, "closed")
    return LM.replay()


def file_item(iid, effect=None):
    args = ["file", iid, "--for", "BENCH", "--title", "t " + iid, "--why", "selftest"]
    if effect:
        args += ["--effect", effect]
    return cli(*args)


def part(name="p1", effect="path-has:sh/page.md::DONE MARK", fooled_by="the mark in an appendix", route=None, **kw):
    d = {"name": name, "effect": effect, "fooled_by": fooled_by, "route": route}
    d.update(kw)
    return d


def lane_it(**kw):
    d = {"state": "proposed", "blocked": False, "effect": None, "verdict": None, "depth": 0, "waits_on": [],
         "title": "a title", "shape_due": True, "shape_why": "named for Shape", "route": None}
    d.update(kw)
    return d


def decide(items, runs=None, st=None, cfg=None, account=(True, ""), **top):
    facts = {"items": items, "runs": runs or {}, "other_live": 0}
    facts.update(top)
    st = st if st is not None else {"items": {}}
    rows, launches = LD().decide(dict(cfg or CFG), st, facts, NOW, account=account)
    return {r["item"]: r for r in rows}, launches, st


# ---- the promises ---------------------------------------------------------------------------------------------------

def t_an_item_filed_with_its_check_never_enters_shape():
    chk(lambda: LS().needs_shape_run({"effect": "cmd:false", "route": None, "parts": None}) is False,
        "an item with its check needs no Shape run")
    chk(lambda: LS().due({"effect": "cmd:false", "named": True, "filed": NOW - 9e5}, {"shape_from": 0,
                                                                                     "shape_grace_h": 24}, NOW)[0] is False,
        "an item with its check is never due for Shape, even when named")
    rows, launches, _ = decide({"A": lane_it(effect="cmd:false", verdict="fails", shape_due=False)})
    chk(lambda: rows["A"]["decision"] == "launch" and rows["A"].get("kind") != "shape",
        "the lane decides on an item with a check as before: a Work run (%s)" % rows["A"])


def t_a_routed_item_needs_no_shape_run():
    chk(lambda: LS().needs_shape_run({"effect": None, "route": R_OK, "parts": None}) is False,
        "an item with a full route needs no Shape run")
    rows, launches, _ = decide({"A": lane_it(route=R_OK, shape_due=False)})
    why = rows["A"].get("why") or ""
    chk(lambda: rows["A"]["decision"] == "routed" and not launches, "a routed item reads routed, nothing launches")
    chk(lambda: "owner" in why and "pick one of two designs" in why and "his card answer" in why,
        "the routed row names who, what is asked and what resumes it (%s)" % why)
    rows, launches, _ = decide({"A": lane_it(effect="cmd:false", verdict="fails", route=R_OK, shape_due=False)})
    chk(lambda: rows["A"]["decision"] == "routed" and not launches,
        "an item whose check fails while a part is routed reads routed, and no Work run launches (%s)"
        % rows["A"]["decision"])
    acc = "src/x_accept.py"
    for s, kw in (({}, {"accept_s": None}), ({}, {"accept_s": 1.0}),
                  ({"adopt_refused": {"fp": [acc, 5], "why": "r"}}, {"accept_s": 1.0})):
        rows, launches, _ = decide({"A": lane_it(accept=acc, events=5, route=R_OK, shape_due=False, **kw)},
                                   st={"items": {"A": s}})
        chk(lambda: rows["A"]["decision"] == "routed" and not launches,
            "a routed item whose ## verify names an acceptance script reads routed, never adopted or refused (%s)"
            % rows["A"]["decision"])


def t_shaped_means_every_part_has_a_check_or_a_full_route():
    s = LS().shaped
    chk(lambda: s([part("a"), part("b", effect=None, fooled_by=None, route=R_OK)])["shaped"] is True,
        "a check part and a routed part: shaped")
    chk(lambda: s([part("a"), part("b", effect=None, fooled_by=None)])["unshaped"] == ["b"],
        "a part with neither is named in unshaped")
    chk(lambda: s([part("a", effect="this is not a check")])["unshaped"] == ["a"],
        "a check text a program cannot read is not a check")
    chk(lambda: s([part("a", effect=None, route={"who": "someone", "ask": "x", "resumes": "y"})])["shaped"] is False,
        "a route to nobody we know is not a hand-over")
    chk(lambda: s([part("a", effect=None, route={"who": "judge", "ask": "", "resumes": "y"})])["shaped"] is False,
        "a route that asks nothing is not a hand-over")
    chk(lambda: s([part("a", effect=None, route={"who": "conductor", "ask": "choose", "resumes": " "})])["unshaped"] == ["a"],
        "a route that does not say what resumes the item is not a hand-over")
    chk(lambda: s([])["shaped"] is False and s(None)["shaped"] is False, "no parts is not shaped")
    chk(lambda: s(["not a dict"])["shaped"] is False, "a part that is not an object is not shaped")


def t_weak_is_a_mark_never_a_stop():
    r = LS().shaped([part("a", fooled_by=None), part("b", fooled_by="  ")])
    chk(lambda: r["weak"] == ["a", "b"] and r["shaped"] is True, "a check with no fooled_by line is weak and shaped")
    iid = "RIMMANDRAKE_TEST_SHAPE_WEAK_IS_WRITTEN"
    file_item(iid)
    page("sh/page.md", "nothing yet\n")
    n0 = len(events())
    rc, out = cli("shape", iid, "--parts", json.dumps([part("a", fooled_by=None)]), "--why", "selftest")
    chk(lambda: rc == 0 and len(events()) == n0 + 1, "a weak split is written (rc %d: %s)" % (rc, out[-300:]))
    chk(lambda: "weak" in out.lower() and "a" in out, "the write names the weak part (%s)" % out[-200:])


def t_the_shape_write_refuses_an_unshaped_split_and_names_the_repair():
    iid = "RIMMANDRAKE_TEST_SHAPE_REFUSES_UNSHAPED"
    file_item(iid)
    page("sh/page.md", "nothing yet\n")
    n0 = len(events())
    rc, out = cli("shape", iid, "--parts", json.dumps([part("good"), part("lost_part", effect=None, fooled_by=None)]),
                  "--why", "selftest")
    chk(lambda: rc != 0 and len(events()) == n0, "an unshaped split is refused and nothing is written (rc %d)" % rc)
    chk(lambda: "lost_part" in out and "route" in out and "judge" in out,
        "the refusal names the part and the repair (%s)" % out[-300:])
    rc, out = cli("shape", iid, "--parts", "[not json", "--why", "selftest")
    chk(lambda: rc != 0 and len(events()) == n0, "an unreadable list is refused, nothing written (rc %d)" % rc)
    rc, out = cli("shape", iid, "--parts", json.dumps([part("a")]), "--size", "huge", "--why", "selftest")
    chk(lambda: rc != 0 and len(events()) == n0, "a size other than small or large is refused (rc %d)" % rc)


def t_each_check_part_is_seen_failing():
    iid = "RIMMANDRAKE_TEST_SHAPE_EACH_PART_SEEN_FAILING"
    file_item(iid)
    page("sh/done.md", "DONE MARK\n")
    page("sh/page.md", "nothing yet\n")
    n0 = len(events())
    rc, out = cli("shape", iid, "--parts", json.dumps([part("open"), part("already", effect="path-has:sh/done.md::DONE MARK")]),
                  "--why", "selftest")
    chk(lambda: rc != 0 and len(events()) == n0 and "already" in out,
        "a part whose check holds now, with no holds_why, is refused by name (rc %d: %s)" % (rc, out[-300:]))
    rc, out = cli("shape", iid, "--parts", json.dumps([part("vac", effect="cmd:true")]), "--why", "selftest")
    chk(lambda: rc != 0 and len(events()) == n0, "a vacuous check part is refused (rc %d)" % rc)
    rc, out = cli("shape", iid, "--parts", json.dumps([part("open"), part("already", effect="path-has:sh/done.md::DONE MARK",
                                                                          holds_why="done before it was filed")]),
                  "--why", "selftest")
    chk(lambda: rc == 0 and len(events()) == n0 + 1, "a holds_why lets a part that holds in (rc %d: %s)" % (rc, out[-300:]))


def t_the_item_check_covers_every_part():
    ic = LS().item_check
    hc = "cmd:python3 src/RimMandrake/rimflow/list_shape.py holds X"
    chk(lambda: ic("X", [part("a", effect="cmd:test -f x")]) == "cmd:test -f x", "one check part: the item check is its check")
    chk(lambda: ic("X", [part("a"), part("b")]) == hc, "two check parts: the holds command")
    chk(lambda: ic("X", [part("a"), part("b", effect=None, route=R_OK)]) == hc, "a check part and a route: the holds command")
    chk(lambda: ic("X", [part("a", effect=None, route=R_OK)]) is None, "all routed: no item check")


def t_holds_keeps_fails_apart_from_could_not_look():
    page("sh/h1.md", "MARK ONE\n")
    page("sh/h2.md", "MARK TWO\n")
    hp = LS().holds_parts
    root = X["root"]
    p1 = part("one", effect="path-has:sh/h1.md::MARK ONE")
    p2 = part("two", effect="path-has:sh/h2.md::MARK TWO")
    pf = part("missing", effect="path-has:sh/h1.md::NOT THERE")
    pu = part("blind", effect="path-lacks:sh/absent.md::x")
    pr = part("routed", effect=None, route=R_OK)
    chk(lambda: hp([p1, p2], root)[0] == 0, "every part holds: 0")
    chk(lambda: hp([p1, pf], root)[0] == 1, "one part fails: 1")
    chk(lambda: hp([p1, pr], root)[0] == 1, "a routed part: 1")
    chk(lambda: hp([p1, pu], root)[0] == 2, "a part unmeasured and none failing: 2")
    chk(lambda: hp([pu, pf], root)[0] == 1, "a part fails beside an unmeasured one: 1 (the fail is known)")
    chk(lambda: hp([], root)[0] == 2 and hp(None, root)[0] == 2, "no parts: 2, never 0")
    rc, out = holds_cli("RIMMANDRAKE_TEST_SHAPE_NEVER_FILED_AT_ALL")
    chk(lambda: rc == 2, "holds on an item never filed: 2 (rc %d: %s)" % (rc, out[-200:]))
    iid = "RIMMANDRAKE_TEST_SHAPE_HOLDS_CLI_READS_PARTS"
    file_item(iid)
    rc, out = holds_cli(iid)
    chk(lambda: rc == 2, "holds on an item with no parts: 2 (rc %d)" % rc)
    page("sh/h3.md", "nothing\n")
    rc, out = cli("shape", iid, "--parts", json.dumps([part("a", effect="path-has:sh/h3.md::THREE"),
                                                       part("b", effect="path-has:sh/h3.md::FOUR")]), "--why", "selftest")
    rc1, out1 = holds_cli(iid)
    page("sh/h3.md", "THREE FOUR\n")
    rc2, out2 = holds_cli(iid)
    chk(lambda: rc == 0 and rc1 == 1 and rc2 == 0,
        "holds reads the item's parts from the ledger: fails, then holds (%d %d %d: %s)" % (rc, rc1, rc2, out1[-200:]))


def t_the_ledger_carries_the_shape():
    iid = "RIMMANDRAKE_TEST_SHAPE_LEDGER_CARRIES_IT"
    file_item(iid)
    page("sh/page.md", "nothing yet\n")
    rc, out = cli("shape", iid, "--enter", "--why", "selftest: named")
    it = world().items.get(iid)
    chk(lambda: rc == 0 and it.shape_named, "--enter replays into Item.shape_named (rc %d: %s)" % (rc, out[-200:]))
    rc, out = cli("shape", iid, "--parts", json.dumps([part("a"), part("b", effect=None, fooled_by=None, route=R_OK)]),
                  "--size", "large", "--why", "selftest")
    it = world().items.get(iid)
    chk(lambda: rc == 0 and it.shape and [p["name"] for p in it.shape["parts"]] == ["a", "b"]
        and it.shape["size"] == "large", "the parts and the size replay into Item.shape (rc %d: %s)" % (rc, out[-200:]))
    chk(lambda: it.effect == "cmd:python3 src/RimMandrake/rimflow/list_shape.py holds %s" % iid,
        "the derived check replays into Item.effect (%s)" % it.effect)
    rc, out = cli("shape", iid, "--parts", json.dumps([part("b", effect=None, fooled_by=None, route=R_OK)]), "--why",
                  "selftest")
    it = world().items.get(iid)
    chk(lambda: rc == 0 and it.effect is None and LS().facts(it)["route"] == R_OK,
        "a split that is all routed leaves no check, and facts() reads the route (rc %d, effect %s)" % (rc, it.effect))
    chk(lambda: it.shape["size"] == "small", "the size defaults to small")


def t_old_items_enter_only_when_named():
    cfg = {"shape_from": NOW - 10 * 86400, "shape_grace_h": 24}
    due = LS().due
    old = {"effect": None, "route": None, "parts": None, "named": None, "filed": NOW - 20 * 86400}
    new_young = dict(old, filed=NOW - 3600)
    new_ripe = dict(old, filed=NOW - 2 * 86400)
    chk(lambda: due(old, cfg, NOW)[0] is False, "an old item, not named: not due")
    chk(lambda: due(dict(old, named=NOW - 60), cfg, NOW)[0] is True, "an old item, named: due")
    chk(lambda: due(new_young, cfg, NOW)[0] is False, "a new item inside the grace: not due")
    chk(lambda: due(new_ripe, cfg, NOW)[0] is True, "a new item past the grace: due")
    chk(lambda: due(dict(new_ripe, route=R_OK), cfg, NOW)[0] is False, "a routed item: not due")
    chk(lambda: all(str(due(x, cfg, NOW)[1]).strip() for x in (old, new_young, new_ripe)), "each reading says why")
    chk(lambda: due(new_ripe, {}, NOW)[0] is False, "no shape_from set: no new item enters by itself")


def t_a_naming_can_be_taken_off():
    iid = "RIMMANDRAKE_TEST_SHAPE_NAMING_TAKEN_OFF"
    file_item(iid)
    cfg = {"shape_from": NOW + 9e9, "shape_grace_h": 24}        # every item is old: only a naming makes it due
    cli("shape", iid, "--enter", "--why", "selftest")
    chk(lambda: LS().due(LS().facts(world().items[iid]), cfg, NOW)[0] is True, "named: due")
    rc, out = cli("shape", iid, "--leave", "--why", "selftest: the owner stopped it")
    it = world().items[iid]
    chk(lambda: rc == 0 and it.shape_named is None and LS().due(LS().facts(it), cfg, NOW)[0] is False,
        "--leave takes the naming off: not due (rc %d: %s)" % (rc, out[-200:]))
    n = len(events())
    rc, out = cli("shape", iid, "--leave", "--why", "selftest")
    chk(lambda: rc == 0 and len(events()) == n and "not named" in out, "--leave on an unnamed item writes nothing (%s)" % out[-200:])
    rc, out = cli("shape", iid, "--enter", "--leave", "--why", "selftest")
    chk(lambda: rc != 0 and len(events()) == n, "--enter with --leave is refused and writes nothing")
    cli("shape", iid, "--enter", "--why", "selftest")
    chk(lambda: bool(world().items[iid].shape_named), "a later --enter names it again")
    sp = "RIMMANDRAKE_TEST_SHAPE_LEAVE_KEEPS_THE_SPLIT"
    file_item(sp)
    page("sh/page.md", "nothing yet\n")
    cli("shape", sp, "--enter", "--why", "selftest")
    cli("shape", sp, "--parts", json.dumps([part("a")]), "--why", "selftest")
    cli("shape", sp, "--leave", "--why", "selftest")
    it = world().items[sp]
    chk(lambda: it.shape and it.effect and it.shape_named is None, "--leave keeps the split and the check")


def t_the_lane_launches_a_shape_run_through_every_gate():
    rows, launches, _ = decide({"A": lane_it()})
    chk(lambda: rows["A"]["decision"] == "shape" and launches == ["A"] and rows["A"].get("kind") == "shape"
        and rows["A"].get("model") == "opus", "a due item reads shape and launches one opus run (%s)" % rows["A"])
    for name, kw, top, want in (
            ("disabled", {}, {"cfg": dict(CFG, enabled=False)}, "disabled"),
            ("the pause", {}, {"paused": "paused by test"}, "pipeline_paused"),
            ("pipe off", {"off": "OFF (test)"}, {}, "off"),
            ("a held mod", {"held": "HELD BY OWNER: X"}, {}, "held"),
            ("a claim", {"claimed": "doing under BENCH"}, {}, "claimed"),
            ("a wait ahead", {"wait_until": NOW + 3600, "wait_reason": "r"}, {}, "waiting"),
            ("the account", {}, {"account": (False, "drain")}, "account_hold"),
            ("the chain rule", {"depth": 2}, {}, "chain_stop"),
            ("the clone pool", {}, {"pool": "pool full"}, "pool_full")):
        cfg = top.pop("cfg", None)
        account = top.pop("account", (True, ""))
        rows, launches, _ = decide({"A": lane_it(**kw)}, cfg=cfg, account=account, **top)
        chk(lambda: rows["A"]["decision"] == want and not launches,
            "%s stops a Shape launch: %s (%s)" % (name, want, rows["A"]["decision"]))
    items = {"L1": lane_it(), "L2": lane_it(), "A": lane_it()}
    runs = {"L1": {"live": ["u1"], "ended": []}, "L2": {"live": ["u2"], "ended": []}}
    rows, launches, _ = decide(items, runs=runs)
    chk(lambda: rows["A"]["decision"] == "slots_full" and not launches,
        "live Shape runs fill the lane's slots (%s)" % rows["A"]["decision"])
    rd = LD().tick(CFG, False, fx={"facts": lambda s: {"items": items, "runs": runs}, "account": lambda: (True, "")},
                   now=NOW, only=["A"])
    chk(lambda: rd["items"]["A"]["decision"] == "slots_full" and list(rd["items"]) == ["A"],
        "a run-now of one due item meets the same full slots (%s)" % rd["items"]["A"]["decision"])
    got = []
    fx = {"launch": lambda iid, model, cap, brief, seat, mod: (got.append((iid, model, brief)) or (0, "DETACHED u9", "u9"))}
    rows, launches, st = decide({"A": lane_it()})
    LD().execute(CFG, st, list(rows.values()), launches, {"items": {"A": lane_it()}}, NOW, fx)
    att = st["items"]["A"]["attempts"]
    chk(lambda: got and "rimflow" in got[0][2] and "shape" in got[0][2] and att[0]["kind"] == "shape"
        and att[0]["unit"] == "u9", "execute launches the Shape brief and records the attempt as kind shape (%s)" % att)
    chk(lambda: LD().tick(CFG, False, fx={"facts": lambda s: {"items": {"A": lane_it()}, "runs": {}},
                                         "account": lambda: (True, "")}, now=NOW)["items"]["A"]["decision"]
        == "would_shape", "a dry tick reads would_shape and launches nothing")


def t_a_shape_run_that_left_neither_check_nor_route_is_stopped():
    st = {"items": {"A": {"attempts": [{"at": NOW - 3600, "unit": "u1", "kind": "shape", "next": None}]}}}
    runs = {"A": {"live": [], "ended": ["u1"]}}
    rows, launches, st = decide({"A": lane_it()}, runs=runs, st=st)
    n = rows["A"].get("need") or {}
    chk(lambda: rows["A"]["decision"] == "stopped" and not launches, "the item reads stopped (%s)" % rows["A"])
    chk(lambda: n.get("outcome") and n.get("why_not_recovered") and n.get("smallest_act"),
        "the stop names the outcome, the reason and the smallest act")
    chk(lambda: "None" not in n["outcome"] and "neither" in n["outcome"],
        "the outcome says that the item has neither, never that a check 'None' fails (%s)" % n.get("outcome"))
    st["items"]["A"]["attempts"][0]["next"] = "LEFT OPEN: try again"
    rows, launches, _ = decide({"A": lane_it()}, runs=runs, st=st)
    chk(lambda: rows["A"]["decision"] == "stopped" and not launches,
        "a LEFT OPEN note does not buy a second Shape run (%s)" % rows["A"]["decision"])
    wk = [{"at": NOW - 9000, "unit": "u0", "kind": "work", "next": None}]
    runs = {"A": {"live": [], "ended": ["u0", "u1"]}}
    rows, launches, _ = decide({"A": lane_it()}, runs=runs, st={"items": {"A": {"attempts": [dict(wk[0])]}}})
    chk(lambda: rows["A"]["decision"] == "shape" and launches == ["A"],
        "a Work run is no Shape run: an item whose wrong check was cleared and that was named gets its Shape run (%s: %s)"
        % (rows["A"]["decision"], rows["A"]["why"]))
    rows, launches, _ = decide({"A": lane_it()}, runs=runs, st={"items": {"A": {"attempts": wk + [
        {"at": NOW - 3600, "unit": "u1", "kind": "shape", "next": None}]}}})
    chk(lambda: rows["A"]["decision"] == "stopped" and "u1" in rows["A"]["why"],
        "and its one Shape run is still the most (%s)" % rows["A"]["why"])


def t_a_large_shape_run_is_not_a_work_run():
    eff = dict(effect="cmd:false", verdict="fails", shape_due=False)
    shape_att = {"at": NOW - 7200, "unit": "u1", "kind": "shape", "next": None}
    runs = {"A": {"live": [], "ended": ["u1", "u2", "u3"]}}
    st = {"items": {"A": {"attempts": [dict(shape_att)]}}}
    rows, launches, _ = decide({"A": lane_it(shape_size="large", **eff)}, runs=runs, st=st)
    chk(lambda: rows["A"]["decision"] == "launch" and rows["A"].get("run_n") == 1,
        "after a large Shape run with no note, Work run 1 launches (%s)" % rows["A"])
    st = {"items": {"A": {"attempts": [dict(shape_att), {"at": NOW - 3600, "unit": "u2", "next": "LEFT OPEN: x"}]}}}
    rows, launches, _ = decide({"A": lane_it(shape_size="large", **eff)}, runs=runs, st=st)
    chk(lambda: rows["A"]["decision"] == "launch" and rows["A"].get("run_n") == 2,
        "a large item still gets Work run 2 on a named next act (%s)" % rows["A"])
    st["items"]["A"]["attempts"].append({"at": NOW - 60, "unit": "u3", "next": "LEFT OPEN: y"})
    rows, launches, _ = decide({"A": lane_it(shape_size="large", **eff)}, runs=runs, st=st)
    chk(lambda: rows["A"]["decision"] == "stopped", "two Work runs is still the most (%s)" % rows["A"]["decision"])
    st = {"items": {"A": {"attempts": [dict(shape_att)]}}}
    rows, launches, _ = decide({"A": lane_it(shape_size="small", **eff)}, runs=runs, st=st)
    chk(lambda: rows["A"]["decision"] == "stopped",
        "a small Shape-and-Work run that ended with no note and a failing check: stopped (%s)" % rows["A"]["decision"])
    st = {"items": {"A": {"attempts": [dict(shape_att, next="LEFT OPEN: finish part b")]}}}
    rows, launches, _ = decide({"A": lane_it(shape_size="small", **eff)}, runs=runs, st=st)
    chk(lambda: rows["A"]["decision"] == "launch" and rows["A"].get("run_n") == 2,
        "a small Shape-and-Work run counts as Work run 1 (%s)" % rows["A"])


def t_a_due_item_enters_shape_when_its_adoption_cannot_happen():
    acc = "src/x_accept.py"
    rows, launches, _ = decide({"A": lane_it(accept=acc, accept_s=None, accept_why="it did not end inside 120s")})
    chk(lambda: rows["A"]["decision"] == "shape" and launches == ["A"],
        "a due item whose acceptance script is too heavy to adopt enters Shape (%s)" % rows["A"]["decision"])
    st = {"items": {"A": {"adopt_refused": {"fp": [acc, 5], "why": "it holds now"}}}}
    rows, launches, _ = decide({"A": lane_it(accept=acc, accept_s=1.0, events=5)}, st=st)
    chk(lambda: rows["A"]["decision"] == "shape" and launches == ["A"],
        "a due item whose adoption was refused enters Shape (%s)" % rows["A"]["decision"])
    for s, kw, want in (({}, {"accept_s": None}, "adopt_too_heavy"),
                        ({"adopt_refused": {"fp": [acc, 5], "why": "r"}}, {"accept_s": 1.0}, "adopt_refused")):
        rows, launches, _ = decide({"A": lane_it(accept=acc, events=5, shape_due=False, **kw)}, st={"items": {"A": s}})
        chk(lambda: rows["A"]["decision"] == want and not launches,
            "an item that is not due still reads %s (%s)" % (want, rows["A"]["decision"]))
    rows, launches, _ = decide({"A": lane_it(accept=acc, accept_s=1.0)})
    chk(lambda: rows["A"]["decision"] == "adopt" and not launches,
        "a due item whose script can be adopted is adopted first (%s)" % rows["A"]["decision"])
    iid = "RIMMANDRAKE_TEST_SHAPE_GATHER_HEAVY_ACCEPT_IS_DUE"
    file_item(iid)
    cli("shape", iid, "--enter", "--why", "selftest: named")
    with open(os.path.join(os.environ["RIMFLOW_ITEMS"], iid + ".md"), "w", encoding="utf-8") as f:
        f.write("## verify\npython3 src/RimMandrake/rimflow/acceptance/step4_shape_accept.py\n")
    ld = LD()
    keep = ld.timed_accept
    ld.timed_accept = lambda *a, **k: None
    try:
        g = ld.gather({"items": {}})
    finally:
        ld.timed_accept = keep
    it = (g["items"] or {}).get(iid) or {}
    chk(lambda: it.get("accept") and it.get("accept_s", 0) is None and it.get("shape_due") is True,
        "gather keeps a named item due beside its heavy script (%s)" % it)


def t_a_passed_wait_never_keeps_a_due_item_out_of_shape():
    past = {"wait_until": NOW - 3600, "wait_reason": "r"}
    rows, launches, _ = decide({"A": lane_it(**past)})
    chk(lambda: rows["A"]["decision"] == "shape" and launches == ["A"],
        "a due item with no check whose wait passed enters Shape (%s)" % rows["A"]["decision"])
    rows, launches, _ = decide({"A": lane_it(effect="cmd:false", verdict="fails", shape_due=False, **past)})
    chk(lambda: rows["A"]["decision"] == "reshape" and not launches,
        "an item with a failing check whose wait passed still launches nothing (%s)" % rows["A"]["decision"])
    st = {"items": {"A": {"attempts": [{"at": NOW - 7200, "unit": "u1", "kind": "shape", "next": None}]}}}
    rows, launches, _ = decide({"A": lane_it(**past)}, runs={"A": {"live": [], "ended": ["u1"]}}, st=st)
    chk(lambda: rows["A"]["decision"] == "stopped" and not launches,
        "a Shape run that left only a wait buys no second Shape run when the wait passes (%s)" % rows["A"]["decision"])


def t_a_reshape_by_another_party_starts_the_run_count_again():
    eff = dict(effect="cmd:false", verdict="fails", shape_due=False, shape_size="small")
    runs = {"A": {"live": [], "ended": ["u1", "u2"]}}

    def go(atts, **kw):
        return decide({"A": lane_it(**dict(eff, **kw))}, runs=runs, st={"items": {"A": {"attempts": atts}}})
    sh = {"at": NOW - 7200, "unit": "u1", "kind": "shape", "next": None}
    rows, launches, _ = go([dict(sh)], shape_at=NOW - 60, shape_unit=None)
    chk(lambda: rows["A"]["decision"] == "launch" and rows["A"].get("run_n") == 1,
        "the party that answered a route shapes the item again: Work run 1 launches (%s)" % rows["A"])
    rows, launches, _ = go([dict(sh), dict(sh, unit="u2", kind="work")], shape_at=NOW - 60, shape_unit="rm-detached-other")
    chk(lambda: rows["A"]["decision"] == "launch" and rows["A"].get("run_n") == 1,
        "so does a helper that is no run of this item (%s)" % rows["A"])
    rows, launches, _ = go([dict(sh)], shape_at=NOW - 7000, shape_unit="u1")
    chk(lambda: rows["A"]["decision"] == "stopped",
        "the item's own run writing its shape starts nothing again (%s)" % rows["A"]["decision"])
    rows, launches, _ = go([dict(sh)], shape_at=NOW - 7000, shape_unit="u2")
    chk(lambda: rows["A"]["decision"] == "stopped",
        "nor does a detached run of this item that the lane did not launch (%s)" % rows["A"]["decision"])
    rows, launches, _ = go([dict(sh)], shape_at=NOW - 9000, shape_unit=None)
    chk(lambda: rows["A"]["decision"] == "stopped",
        "a run launched after the re-shape counts (%s)" % rows["A"]["decision"])
    iid = "RIMMANDRAKE_TEST_SHAPE_FACTS_CARRY_WHO_AND_WHEN"
    file_item(iid)
    page("sh/page.md", "nothing yet\n")
    cli("shape", iid, "--parts", json.dumps([part("a")]), "--why", "selftest")
    f = LS().facts(world().items.get(iid))
    chk(lambda: isinstance(f.get("shape_at"), (int, float)) and f["shape_at"] > 0 and "shape_unit" in f
        and f["shape_unit"] is None, "facts() carries when the item was shaped and by which unit (%s)" % f)
    cli("shape", iid, "--parts", json.dumps([part("a")]), "--why", "selftest", unit="rm-detached-x")
    f = LS().facts(world().items.get(iid))
    chk(lambda: f.get("shape_unit") == "rm-detached-x", "a re-shape by a run replays its unit (%s)" % f)
    g = LD().gather({"items": {}})
    d = (g["items"] or {}).get(iid) or {}
    chk(lambda: d.get("shape_at") and "shape_unit" in d, "gather hands both to decide (%s)" % d)
    chk(lambda: d.get("second_look") is True, "gather: an item filed since shape_from may have a second look (%s)" % d)
    chk(lambda: "raised" in d and d["raised"] is None, "gather: an item never raised has no raise order (%s)" % d.get("raised"))
    cli("raise", iid, "--reason", "selftest", "--why", "selftest")
    d = (LD().gather({"items": {}})["items"] or {}).get(iid) or {}
    chk(lambda: d.get("raised") and d["raised"][0] == 0, "gather: a raised item carries its raise order (%s)" % (d.get("raised"),))
    chk(lambda: isinstance(g.get("load"), float), "gather hands the load average to decide (%s)" % g.get("load"))


def t_status_lists_every_item_due_for_shape():
    iid = "RIMMANDRAKE_TEST_SHAPE_STATUS_DUE_BY_AGE"
    file_item(iid)
    ld, out = LD(), []
    keep = ld.load_cfg
    ld.load_cfg = lambda *a, **k: {"shape_from": 0.5, "shape_grace_h": 0}
    import builtins
    real = builtins.print
    builtins.print = lambda *a, **k: out.append(" ".join(str(x) for x in a))
    try:
        LS().status_main([])
    finally:
        builtins.print, ld.load_cfg = real, keep
    chk(lambda: any(ln.startswith(iid) and " due " in ln for ln in out),
        "status with no ids lists an item due by age, never named (%s)" % out[-1:])


def t_the_shape_brief_asks_for_the_need():
    b = LS().brief_text("RIMMANDRAKE_TEST_BRIEF_ITEM", {"title": "a title"}, {})
    for w in ("RIMMANDRAKE_TEST_BRIEF_ITEM", "worth the touch", "fooled_by", "leave the need unmet", "judge", "owner", "conductor", "review",
              "small", "large", "cli.py shape", "LEFT OPEN:"):
        chk(lambda w=w: w in b, "the brief says %r" % w)
    chk(lambda: not re.search(r"\{[a-z_]+\}", b), "the brief has no unfilled placeholder")


def t_each_limit_names_its_danger():
    with open(os.path.join(HERE, "list_dispatch.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    for k in ("shape_grace_h", "shape_from"):
        chk(lambda k=k: k in cfg and str(cfg.get("_%s_doc" % k) or "").strip(), "%s has its danger doc" % k)


def main():
    top = tempfile.mkdtemp(prefix="selftest_list_shape_")
    X.update(root=os.path.join(top, "root"))
    os.makedirs(X["root"])
    keys = ("RIMFLOW_LEDGER", "RIMFLOW_ITEMS", "RIMFLOW_GITINDEX", "RIMFLOW_PROBE", "RM_LIST_EFFECT_ROOT",
            "RM_CONTROL_DB", "RM_PIPELINE_PAUSE_FILE", "RM_DISPATCHER_STATE", "RM_ROLE_UNIT")
    saved = {k: os.environ.get(k) for k in keys}
    os.environ.update(RIMFLOW_LEDGER=os.path.join(top, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(top, "items"),
                      RIMFLOW_GITINDEX="off", RIMFLOW_PROBE="no-reading", RM_LIST_EFFECT_ROOT=X["root"],
                      RM_CONTROL_DB=os.path.join(top, "control.db"),
                      RM_PIPELINE_PAUSE_FILE=os.path.join(top, "pause.json"),
                      RM_DISPATCHER_STATE=os.path.join(top, "dstate"))
    os.environ.pop("RM_ROLE_UNIT", None)
    os.makedirs(os.environ["RIMFLOW_ITEMS"])
    try:
        for t in (t_an_item_filed_with_its_check_never_enters_shape,
                  t_a_routed_item_needs_no_shape_run,
                  t_shaped_means_every_part_has_a_check_or_a_full_route,
                  t_weak_is_a_mark_never_a_stop,
                  t_the_shape_write_refuses_an_unshaped_split_and_names_the_repair,
                  t_each_check_part_is_seen_failing,
                  t_the_item_check_covers_every_part,
                  t_holds_keeps_fails_apart_from_could_not_look,
                  t_the_ledger_carries_the_shape,
                  t_old_items_enter_only_when_named,
                  t_a_naming_can_be_taken_off,
                  t_the_lane_launches_a_shape_run_through_every_gate,
                  t_a_shape_run_that_left_neither_check_nor_route_is_stopped,
                  t_a_large_shape_run_is_not_a_work_run,
                  t_a_due_item_enters_shape_when_its_adoption_cannot_happen,
                  t_a_passed_wait_never_keeps_a_due_item_out_of_shape,
                  t_a_reshape_by_another_party_starts_the_run_count_again,
                  t_status_lists_every_item_due_for_shape,
                  t_the_shape_brief_asks_for_the_need,
                  t_each_limit_names_its_danger):
            try:
                t()
            except Exception as e:  # noqa: BLE001
                chk(lambda: False, "%s (raised %s: %s)" % (t.__name__, type(e).__name__, str(e)[:300]))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(top, ignore_errors=True)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
