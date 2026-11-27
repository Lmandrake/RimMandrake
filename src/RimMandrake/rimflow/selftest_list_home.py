#!/usr/bin/env python3
"""selftest_list_home.py - the home of a list ticket (list_home.py, `rimflow home`).

Item RIMMANDRAKE_GROUP_OLD_TICKETS_BY_HOME_AND_KEEP_THE_LIST_FOR_GOOD; page
design/specs/2026-11-23-old-tickets-by-home/boundary.md (each t_ function is one promise of it, by name). Offline: a
throwaway ledger. Written before the code; seen failing on the base (list_home.py absent, `rimflow home` unknown).
"""
import os
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
FAILS = []
X = {}


def chk(fn, what):
    try:
        cond = fn()
    except Exception as e:  # noqa: BLE001
        cond, what = False, "%s (raised %s: %s)" % (what, type(e).__name__, str(e)[:300])
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def LH():
    import list_home
    return list_home


def cli(*args):
    env = dict(os.environ, RIMFLOW_SEAT="BENCH")
    for k in ("CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "RM_ROLE_UNIT"):
        env.pop(k, None)
    r = subprocess.run([sys.executable, CLI] + list(args), cwd=REPO, env=env, capture_output=True, text=True,
                       timeout=180, stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout + r.stderr


def world():
    import model as LM
    LM.EVENTS = os.environ["RIMFLOW_LEDGER"]
    LM.ITEMS = os.environ["RIMFLOW_ITEMS"]
    LM.CLOSED = os.path.join(LM.ITEMS, "closed")
    return LM.replay()


def events():
    import model as LM
    LM.EVENTS = os.environ["RIMFLOW_LEDGER"]
    return LM.read()


def fil(iid):
    rc, out = cli("file", iid, "--for", "BENCH", "--title", "t " + iid, "--why", "selftest")
    if rc:
        raise RuntimeError(out[-300:])
    return iid


def rows(text):
    p = os.path.join(X["top"], "rows.tsv")
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def t_the_ledger_carries_the_home():
    i = fil("RIMMANDRAKE_TEST_HOME_LEDGER_CARRIES_IT")
    rc, out = cli("home", i, "--home", "mod:FlowWorks", "--group", "pipe-art", "--flag", "LOOKS CURRENT", "--why", "t")
    it = world().items[i]
    chk(lambda: rc == 0 and it.home["home"] == "mod:FlowWorks" and it.home["group"] == "pipe-art"
        and it.home["flag"] == "LOOKS CURRENT" and it.home["at"] and it.home["seat"] == "BENCH",
        "the event replays into Item.home (rc %d: %s)" % (rc, out[-200:]))
    cli("home", i, "--home", "pipeline:bridge", "--group", "locks", "--flag", "LOOKS OVERTAKEN", "--reason",
        "driver lock", "--why", "t")
    it = world().items[i]
    chk(lambda: it.home["home"] == "pipeline:bridge" and it.home["reason"] == "driver lock", "the last event stands")
    chk(lambda: it.state == "proposed", "the state does not move")
    cli("reassign", i, "--to", "DECIDE", "--owner-said", "give it to them, please")     # an act across a seat boundary
    cli("home", "--from", rows("%s\tmod:X\tg\tCANNOT TELL\t\n" % i), "--why", "t")
    evs = [e for e in events() if e.get("id") == i]
    chk(lambda: any(e.get("override") for e in evs if e["event"] == "reassign"), "the planted override is on the ledger")
    chk(lambda: evs[-1]["event"] == "home" and not evs[-1].get("override"),
        "a home event never carries an override that an older event made (%s)" % evs[-1])


def t_a_bad_row_writes_nothing_and_names_the_repair():
    i = fil("RIMMANDRAKE_TEST_HOME_BAD_ROW_WRITES_NOTHING")
    n = len(events())
    for what, home, group, flag, reason in (
            ("an unknown kind", "biome:Scald", "g", "LOOKS CURRENT", ""),
            ("an empty name", "mod:", "g", "LOOKS CURRENT", ""),
            ("no colon", "FlowWorks", "g", "LOOKS CURRENT", ""),
            ("a group that is no slug", "mod:X", "Big Group", "LOOKS CURRENT", ""),
            ("an empty group", "mod:X", "", "LOOKS CURRENT", ""),
            ("an unknown flag", "mod:X", "g", "STALE", ""),
            ("overtaken with no reason", "mod:X", "g", "LOOKS OVERTAKEN", ""),
            ("unplaced with no reason", "unplaced", "g", "CANNOT TELL", "")):
        chk(lambda: LH().fields(home, group, flag, reason)[0] is None and LH().fields(home, group, flag, reason)[1],
            "%s is refused with words" % what)
        rc, out = cli("home", i, "--home", home, "--group", group, "--flag", flag, "--reason", reason, "--why", "t")
        chk(lambda: rc == 2 and "home refused" in out and len(events()) == n, "%s writes nothing (rc %d)" % (what, rc))
    chk(lambda: LH().fields("unplaced", "g", "CANNOT TELL", "two subjects")[1] is None, "unplaced with a reason passes")
    rc, out = cli("home", "--from", rows("%s\tmod:X\tg\tLOOKS CURRENT\t\n%s\tbad\tg\tLOOKS CURRENT\t\n" % (i, i + "_B")),
                  "--why", "t")
    chk(lambda: rc == 2 and len(events()) == n and "line 2" in out, "one bad row stops the whole file (%s)" % out[-200:])
    rc, out = cli("home", "--from", rows("RIMMANDRAKE_NEVER_FILED_THIS_ONE_AT_ALL\tmod:X\tg\tLOOKS CURRENT\t\n"), "--why", "t")
    chk(lambda: rc == 2 and "never been filed" in out and len(events()) == n, "a row of an id never filed is a bad row")


def t_a_rows_file_may_run_again():
    a, b = fil("RIMMANDRAKE_TEST_HOME_ROWS_AGAIN_FIRST"), fil("RIMMANDRAKE_TEST_HOME_ROWS_AGAIN_CLOSED")
    cli("drop", b, "--reason", "selftest", "--why", "t")
    p = rows("# a comment\n%s\tgame:audio\tpipeline\tCANNOT TELL\t\n%s\tgame:audio\tpipeline\tCANNOT TELL\t\n" % (a, b))
    rc, out = cli("home", "--from", p, "--why", "t")
    n = len(events())
    chk(lambda: rc == 0 and world().items[a].home["home"] == "game:audio" and world().items[b].home is None
        and "closed" in out, "the open row is written, the closed row is skipped and said (%s)" % out[-200:])
    rc, out = cli("home", "--from", p, "--why", "t")
    chk(lambda: rc == 0 and len(events()) == n, "the same file again writes nothing")


def H(home, group="g", flag="LOOKS CURRENT"):
    return {"home": home, "group": group, "flag": flag, "reason": None}


def t_a_ticket_with_no_home_is_named():
    v = LH().view({"A_B_C": None, "D_E_F": H("mod:X")})
    chk(lambda: v["no_home"] == ["A_B_C"] and v["homes"]["mod:X"]["count"] == 1, "no home: named and in no home")
    text = "\n".join(LH().lines(v, planned=lambda m: False))
    chk(lambda: "no home: 1" in text and "A_B_C" in text, "the list names it")


def t_the_list_is_by_home_and_group_with_counts():
    v = LH().view({"A": H("mod:X", "g1"), "B": H("mod:X", "g2", "LOOKS OVERTAKEN"), "C": H("mod:X", "g1"),
                   "D": H("pipeline:bridge", "g1"), "E": None})
    h = v["homes"]["mod:X"]
    chk(lambda: h["count"] == 3 and [(g, len(i)) for g, i in h["groups"].items()] == [("g1", 2), ("g2", 1)]
        and h["flags"] == {"LOOKS CURRENT": 2, "LOOKS OVERTAKEN": 1}, "groups and flags are counted (%s)" % h)
    chk(lambda: sum(x["count"] for x in v["homes"].values()) + len(v["no_home"]) == v["total"] == 5, "the counts sum")
    text = "\n".join(LH().lines(v, planned=lambda m: m == "X"))
    chk(lambda: "mod:X" in text and "planned" in text and "g1" in text, "the list prints homes, groups, planned")
    only = "\n".join(LH().lines(v, planned=lambda m: False, only="pipeline:bridge"))
    chk(lambda: "D" in only and "mod:X" not in only, "--home prints one home with its tickets")


def t_a_closed_ticket_leaves_the_list():
    class It(object):
        def __init__(self, state):
            self.state, self.home, self.title = state, H("mod:X"), "t"
    got = LH().open_homes({"A": It("ready"), "B": It("done"), "C": It("dropped"), "D": It("superseded")}, ["A", "B", "C", "D"])
    chk(lambda: sorted(got) == ["A"], "only the open one is left (%s)" % sorted(got))


def t_could_not_look_is_not_an_empty_list():
    def boom():
        raise RuntimeError("no ledger")
    rc = LH().main(["counts"], read=boom)
    chk(lambda: rc == 2, "a read that fails exits 2")


def t_a_home_never_launches_or_closes():
    i = fil("RIMMANDRAKE_TEST_HOME_CHANGES_NOTHING_ELSE")
    a = world().items[i]
    cli("home", i, "--home", "machine:Archmagi", "--group", "g", "--flag", "CANNOT TELL", "--why", "t")
    b = world().items[i]
    keys = ("state", "owner", "shape", "shape_named", "effect", "lease", "wait_until", "blocked", "needs", "claim_ts")
    chk(lambda: b.home and all(getattr(a, k) == getattr(b, k) for k in keys), "no other field moved")


def t_a_parked_ticket_is_not_offered():
    """A ticket whose block holds (kind owner here: he decides) or whose dated wait is ahead is not offered to a lane or
    to Codex; it is counted and named as parked. A block that ended and a wait that passed offer it again."""
    import time
    owner, waited, free = (fil("RIMMANDRAKE_TEST_HOME_PARKED_" + s) for s in ("OWNER_BLOCK", "WAIT_AHEAD", "FREE"))
    ended, passed = fil("RIMMANDRAKE_TEST_HOME_PARKED_BLOCK_ENDED"), fil("RIMMANDRAKE_TEST_HOME_PARKED_WAIT_PASSED")
    tomorrow = time.strftime("%Y-%m-%d", time.gmtime(time.time() + 86400))
    cli("block", owner, "--kind", "owner", "--reason", "faction work starts on his word", "--why", "t")
    cli("block", ended, "--kind", "time", "--lift-at", tomorrow, "--reason", "after tomorrow", "--why", "t")
    w = world()
    # a dated wait is written on started work only (claim, wait, release); the offer reads the replayed fields
    w.items[waited].wait_until, w.items[waited].wait_reason = "2099-01-01", "read again then"
    w.items[passed].wait_until, w.items[passed].wait_reason = tomorrow, "r"
    ids = [owner, waited, free, ended, passed]
    later = time.time() + 3 * 86400        # past the second wait's date, long before 2099
    o = LH().offer(w.items, ids, set(), reading=lambda it: {}, now=later)
    chk(lambda: sorted(o["offer"]) == sorted([free, ended, passed]) and sorted(o["parked"]) == sorted([owner, waited]),
        "a holding block and a wait ahead are parked, not offered (%s)" % o)
    chk(lambda: "faction work starts on his word" in o["parked"].get(owner, "")
        and "2099-01-01" in o["parked"].get(waited, ""), "each parked ticket names its reason (%s)" % o.get("parked"))
    text = "\n".join(LH().offer_lines(o, w.items))
    chk(lambda: "parked, not offered" in text and owner in text and waited in text, "the offer lines name the parked")


def _old(iid, home=None, caused_by=None, title=None, **kw):
    import types
    x = types.SimpleNamespace(id=iid, state="proposed", title=title or ("t " + iid), caused_by=caused_by, effect=None,
                              shape=None, shape_named=None, created_at="2026-11-01T00:00:00Z",
                              home={"home": home, "group": "g", "flag": "LOOKS CURRENT"} if home else None)
    for k, v in kw.items():
        setattr(x, k, v)
    return x


WORDS = ["LeaningScrub", "FeverWood"]
BEFORE = 1795500000.0      # 2026-11-17: the fakes above were filed before it


def t_an_old_ticket_takes_a_home_by_rule():
    """The nearest ancestor with a real home first (its mod by mod_work, or its own home that is not unplaced), then the
    mod that its id or title names, else no home: with the group of the rule, CANNOT TELL, and a reason that names it."""
    items = {"P0": _old("P0", "pipeline:bridge"), "P1": _old("P1", caused_by="P0"), "C": _old("C", caused_by="P1"),
             "MP": _old("MP"), "MC": _old("MC", caused_by="MP"),
             "U": _old("U", "unplaced", caused_by="P0"), "CU": _old("CU", caused_by="U"),
             "A": _old("A", caused_by="B"), "B": _old("B", caused_by="A"),
             "LEANINGSCRUB_FIX_X": _old("LEANINGSCRUB_FIX_X"),
             "AGARILUX_FIX_Y": _old("AGARILUX_FIX_Y", title="Plant NRE in FeverWood after load"),
             "FEVERWOOD_Z": _old("FEVERWOOD_Z", caused_by="P0"), "N": _old("N", caused_by="GONE")}

    def reading(it):
        return {"mod": "FlowWorks"} if it.id == "MP" else {"mod": None}
    rh = lambda i: LH().rule_home(items[i], items, reading, WORDS)      # noqa: E731
    got = rh("C")
    chk(lambda: got and got[0] == "pipeline:bridge" and got[1] == "by-rule-cause" and "P0" in got[2] and "2 hop" in got[2],
        "the nearest ancestor with a home, two hops up, names that ancestor (%s)" % (got,))
    chk(lambda: rh("MC")[:2] == ("mod:FlowWorks", "by-rule-cause"), "an ancestor that is one mod's work gives that mod")
    chk(lambda: rh("CU")[0] == "pipeline:bridge", "an unplaced ancestor is no home: the walk goes on past it")
    chk(lambda: rh("A") is None and rh("B") is None, "a loop in the chain ends, with no home")
    chk(lambda: rh("LEANINGSCRUB_FIX_X")[:2] == ("mod:LeaningScrub", "by-rule-name"), "the mod its id names")
    w = rh("AGARILUX_FIX_Y")
    chk(lambda: w[0] == "mod:FeverWood" and "list_dispatch.mod_of" in w[2], "the mod its title names (%s)" % (w,))
    chk(lambda: rh("FEVERWOOD_Z")[0] == "pipeline:bridge", "the chain comes before the name")
    chk(lambda: rh("N") is None, "no ancestor in the ledger and no mod named: no home (the lane names it for Shape)")
    for i in ("C", "MC", "LEANINGSCRUB_FIX_X"):
        h, g, r = rh(i)
        chk(lambda h=h, g=g, r=r: LH().fields(h, g, "CANNOT TELL", r)[0] is not None, "%s: the row is a valid home" % i)


def t_place_writes_only_rule_homes():
    items = {"P0": _old("P0", "pipeline:bridge"), "OK": _old("OK", caused_by="P0"),
             "OWN": _old("OWN", "game:flight", caused_by="P0"), "UNP": _old("UNP", "unplaced", caused_by="P0"),
             "TESTED": _old("TESTED", caused_by="P0", effect="cmd:false"), "MODW": _old("MODW", caused_by="P0"),
             "NEW": _old("NEW", caused_by="P0", created_at="2026-11-25T00:00:00Z"),
             "SHUT": _old("SHUT", caused_by="P0", state="done"), "NONE": _old("NONE"),
             "BLIND": _old("BLIND", caused_by="P0")}

    def reading(it):
        return {"mod": "FlowWorks"} if it.id == "MODW" else {"unreadable": "x"} if it.id == "BLIND" else {"mod": None}
    rows = LH().place_rows(items, reading, WORDS, BEFORE)
    chk(lambda: [i for i, _f in rows] == ["OK"] and rows[0][1]["flag"] == "CANNOT TELL"
        and rows[0][1]["group"] == "by-rule-cause", "only an old open ticket with no home, no test and no mod reading is "
        "a row (%s)" % rows)
    # the write, on the throwaway ledger: one act, and a second run writes nothing new
    p0 = fil("RIMMANDRAKE_TEST_HOME_PLACE_PARENT")
    cli("home", p0, "--home", "pipeline:bridge", "--group", "g", "--flag", "LOOKS CURRENT", "--why", "t")
    rc, out = cli("file", "RIMMANDRAKE_TEST_HOME_PLACE_CHILD", "--for", "BENCH", "--title", "t", "--caused-by", p0,
                  "--why", "selftest")
    late = 4102444800.0     # 2100: every ticket of this ledger is old
    n1 = LH().place_main(apply=True, before=late, words=WORDS, reading=lambda it: {"mod": None}, publish=False)
    child = world().items["RIMMANDRAKE_TEST_HOME_PLACE_CHILD"]
    chk(lambda: rc == 0 and child.home and child.home["home"] == "pipeline:bridge" and child.home["group"] == "by-rule-cause",
        "place --apply writes the rule home (%s; %s)" % (child.home, out[-200:]))
    before = len(events())
    n2 = LH().place_main(apply=True, before=late, words=WORDS, reading=lambda it: {"mod": None}, publish=False)
    chk(lambda: n1 >= 1 and n2 == 0 and len(events()) == before, "a second run writes nothing new (%s, %s)" % (n1, n2))
    dry_n = LH().place_main(apply=False, before=late, words=WORDS, reading=lambda it: {"mod": None}, publish=False)
    chk(lambda: dry_n == 0 and len(events()) == before, "a dry run writes nothing")


def main():
    top = X["top"] = tempfile.mkdtemp(prefix="selftest_list_home_")
    env = dict(RIMFLOW_LEDGER=os.path.join(top, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(top, "items"),
               RIMFLOW_GITINDEX="off", RIMFLOW_PROBE="no-reading", RM_CONTROL_DB=os.path.join(top, "control.db"),
               RM_DISPATCHER_STATE=os.path.join(top, "dstate"))
    saved = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    os.makedirs(env["RIMFLOW_ITEMS"])
    try:
        for t in (t_the_ledger_carries_the_home,
                  t_a_bad_row_writes_nothing_and_names_the_repair,
                  t_a_rows_file_may_run_again,
                  t_a_ticket_with_no_home_is_named,
                  t_the_list_is_by_home_and_group_with_counts,
                  t_a_closed_ticket_leaves_the_list,
                  t_could_not_look_is_not_an_empty_list,
                  t_a_home_never_launches_or_closes,
                  t_a_parked_ticket_is_not_offered,
                  t_an_old_ticket_takes_a_home_by_rule,
                  t_place_writes_only_rule_homes):
            try:
                t()
            except Exception as e:  # noqa: BLE001
                chk(lambda: False, "%s (raised %s: %s)" % (t.__name__, type(e).__name__, str(e)[:300]))
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        shutil.rmtree(top, ignore_errors=True)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
