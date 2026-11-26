#!/usr/bin/env python3
"""selftest_item_packet.py - the item packet in each detached brief (item_packet.py, detached_helper.brief_message).

Item RIMMANDRAKE_PASTE_ITEM_HISTORY_INTO_BRIEFS_1503_SHOWS_CUT; page design/specs/2026-11-23-item-packet/boundary.md (each
t_ function is one promise of it, by name). Offline; a ledger in a throwaway git repo. The blind roles, one named test each:
blind judge, fresh reader, examiner, challenger, coverage judge (t_blind_roles_get_none).
"""
import inspect
import json
import os
import re
import subprocess
import sys
import tempfile
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
import item_packet as IP  # noqa: E402

FAILS = []
IT = "RIMMANDRAKE_SOME_ITEM_FOR_THIS_TEST_ONLY"
SPEND = re.compile(r"\$\s?\d|\bweighted\b|\bbudget|\bcap.usd\b|\bspend|\b\d[\d,.]*\s*[kM]?\s*tokens?\b", re.I)


def chk(fn, what):
    try:
        cond = fn()
    except Exception as e:  # noqa: BLE001
        cond, what = False, "%s (raised %s: %s)" % (what, type(e).__name__, str(e)[:300])
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def n(text, i=0, **k):
    return dict({"ts": "2026-11-%02dT00:00:00Z" % (i % 28 + 1), "seat": "BENCH", "text": text}, **k)


def facts(**k):
    f = {"state": "doing", "title": "a title", "prose": "## spec\nbuild it", "notes": [n("first note"), n("last note", 3)],
         "runs": [{"ts": "t1", "result": "pass", "evidence": "log_one.txt"}],
         "linked": [{"id": "RIMMANDRAKE_OTHER_ITEM_HERE", "state": "done", "title": "other"}], "criteria": ["it glows"],
         "commits": [{"sha": "abc1234", "subject": "a commit"}], "as_of": "8:00 PM PST 11-23"}
    f.update(k)
    return f


def pk(room=12000, **k):
    return IP.packet(IT, facts(**k), room)


BIG = [n("routine %03d " % i + "z" * 400, i) for i in range(100)]


def t_holds_the_item():
    t = pk()["text"]
    for s in ("State: doing", "a title", "build it", "first note", "last note", "pass: log_one.txt",
              "RIMMANDRAKE_OTHER_ITEM_HERE [done]", "it glows", "abc1234 a commit", "8:00 PM PST 11-23"):
        chk(lambda s=s: s in t, "holds-the-item: %s" % s)
    chk(lambda: t.index("first note") < t.index("last note"), "holds-the-item: the notes stay oldest first")
    chk(lambda: pk()["left_out"] == [] and "Nothing was left out" in t, "holds-the-item: under the limit nothing goes")
    linked = "RIMMANDRAKE_OTHER_ITEM_HERE"
    r = pk(linked=[{"id": linked, "state": "done", "title": "Check the account-level guard. Keep the work visible."}])
    chk(lambda: "- %s [done] Keep the work visible." % linked in r["text"],
        "holds-the-item: a linked item keeps its ID and [done] after title redaction")
    chk(lambda: "account-level" not in r["text"] and any("linked item " + linked in x for x in r["left_out"]),
        "holds-the-item: a linked title redaction is counted")
    run = {"ts": "2026-10-30T20:45:21Z", "result": "partial",
           "config": "BENCH independent offline e2e through real writers (bfeed.py 17/18: MEASURED, units exact, dedup ok, "
                     "judge spend off-arm, 8 broken feeds UNMEASURED) + 14 mutants all killed (mutB.txt); FAIL probe d1: "
                     "tester spend unmetered -> ARENA_TESTER_SPEND_ENFORCE_METERED_HOME",
           "evidence": r"D:\ClaudeWork\rimmandrake\arena_verify2_20261030\bfeed.txt"}
    r = pk(runs=[run])
    chk(lambda: "- %s partial: %s" % (run["ts"], run["evidence"]) in r["text"] and not SPEND.search(r["text"])
        and any("run of %s (partial)" % run["ts"] in x for x in r["left_out"]),
        "holds-the-item: a partial run keeps its time, result and bfeed.txt after redaction")
    child = "LINT_EXCLUDE_LAKE_SUBMERGED_1"
    finding = "LINT_COUNTS_LAKE_AS_LAND_1"
    events = EVENTS[:3] + [ev("verify", 3, result="partial", config="full-583", evidence="run.txt"),
                          ev("finding", 4, name=finding, type="defect", severity="medium",
                             **{"from": IT + "/run-1@full-583"}),
                          {"seat": "BENCH", "event": "spawn", "name": child, "kind": "task", "needs": "offline",
                           "spec": "Add the lake exclusion.", "for": "BENCH", "from": finding, "ts": ev("note", 5)["ts"]},
                          ev("supersede", 6, by=child)]
    with tempfile.TemporaryDirectory() as d:
        c = make_clone(os.path.join(d, "c"), events)
        g = IP.gather(child, c)
        t = IP.packet(child, g)["text"]
        chk(lambda: IT not in g["prose"] and t.count(IT + " [superseded]") == 1,
            "holds-the-item: a spawn from a run finding links its superseded source once")


def t_decisive_notes_are_kept():
    for w, extra in (("LEFT OPEN: finish the half", {}), ("PROGRESS: theory: x | next: y", {}), ("RULING: never do x", {}),
                     ("REFUSED: one hole", {}), ("the judge REFUSED it for one hole", {}),
                     ("Conductor's ruling: end at five", {}), ("state of it\nLEFT OPEN: the rest", {}),
                     ("do it this way", {"owner_said": "do it this way"}), ("picked B", {"by_card": "which -> B"}),
                     ("an owner event", {"seat": "OWNER"})):
        for at in (0, 50):
            notes = BIG[:at] + [n(w, 1, **extra)] + BIG[at:]
            chk(lambda: w in pk(8000, notes=notes)["text"], "decisive-notes-are-kept: %r at %d among 100" % (w[:24], at))
    chk(lambda: "the last " + "q" * 9000 in pk(8000, notes=BIG + [n("the last " + "q" * 9000)])["text"],
        "decisive-notes-are-kept: the last note is whole, past the limit itself")
    chk(lambda: "the last real note" in pk(8000, notes=BIG + [n("the last real note"), n("reason: gone", event="wait")])[
        "text"] and "reason: gone" in pk(8000, notes=BIG + [n("x"), n("reason: gone", event="wait")])["text"],
        "decisive-notes-are-kept: the last note, and the last event after it")
    runs = [{"ts": "t%d" % i, "result": "fail" if i == 3 else "pass", "evidence": "e%03d" % i + "y" * 200}
            for i in range(90)]
    chk(lambda: "t3 fail: e003" in pk(8000, notes=BIG, runs=runs)["text"] and "t5 pass" not in pk(
        8000, notes=BIG, runs=runs)["text"], "decisive-notes-are-kept: a fail run stays, old passes go")
    chk(lambda: "it glows" in pk(2000, notes=BIG)["text"], "decisive-notes-are-kept: the open criteria")


def t_oldest_routine_notes_go_first():
    t = pk(8000, notes=BIG)["text"]
    kept = [i for i in range(100) if "routine %03d " % i in t]
    chk(lambda: kept and kept == list(range(kept[0], 100)) and kept[0] > 0,
        "oldest-routine-notes-go-first: the newest ones stay, without a gap")
    chk(lambda: len(t) <= 8000 and len(t) > 6500, "oldest-routine-notes-go-first: it fits, and drops no more than it must")
    chk(lambda: "abc1234" in t and "RIMMANDRAKE_OTHER_ITEM_HERE" in t, "oldest-routine-notes-go-first: before the rest")
    long = "p" * 9000
    chk(lambda: long in pk(8000 + 4000, prose=long, notes=BIG)["text"], "oldest-routine-notes-go-first: prose stays")
    r = pk(8000, prose=long, prose_path="infrastructure/state/items/X.md")
    chk(lambda: long not in r["text"] and any("items/X.md" in x for x in r["left_out"]) and "items/X.md" in r["text"],
        "oldest-routine-notes-go-first: prose longer than the limit is left out whole, by its path")
    commits = [{"sha": "c%03d" % i, "subject": "s" * 300} for i in range(60)]
    t2 = pk(8000, notes=[n("only")], commits=commits)["text"]
    chk(lambda: "c000 " in t2 and "c059 s" not in t2, "oldest-routine-notes-go-first: the newest commits stay")


def t_a_note_is_whole_or_left_out():
    notes = [n("START%03d " % i + "w" * (300 + 7 * i) + " END%03d" % i, i) for i in range(80)]
    for room in (3000, 5000, 8000, 12000):
        t = pk(room, notes=notes)["text"]
        chk(lambda: all(("START%03d " % i in t) == ("w END%03d" % i in t) for i in range(80)),
            "a-note-is-whole-or-left-out: at %d" % room)
    odd = "  two  spaces;\n\n    an indent; `code`\n\ttab"
    chk(lambda: odd in pk(notes=[n(odd)])["text"], "a-note-is-whole-or-left-out: not a character of it is changed")


def t_left_out_is_counted():
    r = pk(8000, notes=BIG)
    gone = [i + 1 for i in range(100) if "routine %03d " % i not in r["text"]]
    chk(lambda: len(r["left_out"]) == len(gone) and all(any(x.startswith("note %d of 100 " % g) for x in r["left_out"])
                                                       for g in gone), "left-out-is-counted: each dropped note, by name")
    chk(lambda: "LEFT OUT of this packet: %d part(s): notes %d-%d of 100" % (len(gone), gone[0], gone[-1]) in r["text"],
        "left-out-is-counted: the count and the numbers stand in the text")
    chk(lambda: "`python3 src/RimMandrake/rimflow/cli.py show %s`" % IT in r["text"], "left-out-is-counted: the command")
    mid = pk(8000, notes=BIG[:20] + [n("RULING: x")] + BIG[20:])["text"]
    chk(lambda: re.search(r"notes 1-20, 22-\d+ of 101", mid), "left-out-is-counted: a kept note parts the range")
    chk(lambda: pk(6000, notes=[n("q" * 100)], linked=[{"id": "L%d" % i, "state": "done", "title": "t" * 300}
        for i in range(40)])["text"].count("linked item L") > 0, "left-out-is-counted: a linked item is named")
    chk(lambda: "3 bookkeeping events" in pk(bookkeeping=3)["text"], "left-out-is-counted: bookkeeping is a count")


def t_could_not_look_is_said():
    for kind, none in (("prose", "no prose"), ("notes", "no notes"), ("runs", "no runs"), ("linked", "no linked"),
                       ("commits", "no commits"), ("criteria", "no open criteria")):
        a, b = pk(**{kind: None}), pk(**{kind: "" if kind == "prose" else []})
        chk(lambda: [c for c in a["could_not_look"] if c.startswith(kind)] and none not in a["text"].lower()
            and "could not look" in a["text"].lower(), "could-not-look-is-said: %s None" % kind)
        chk(lambda: b["could_not_look"] == [] and none in b["text"].lower() and "could not look" not in
            b["text"].lower(), "could-not-look-is-said: %s empty is looked and found none" % kind)
    chk(lambda: any(c.startswith("state") for c in pk(state=None)["could_not_look"]), "could-not-look-is-said: the state")
    chk(lambda: "the disk is gone" in pk(notes=None, why={"notes": "the disk is gone"})["text"],
        "could-not-look-is-said: the cause")
    with tempfile.TemporaryDirectory() as d:
        g = IP.gather(IT, os.path.join(d, "no_such_clone"))
        r = IP.packet(IT, g)
        chk(lambda: all(g[k] is None for k in ("state", "notes", "runs", "linked", "commits", "prose", "ledger")) and
            len(r["could_not_look"]) >= 7 and "no notes" not in r["text"].lower(), "could-not-look-is-said: no clone at all")


def make_clone(d, events, prose=None, behind=0):
    """A git repo with a one-shard ledger, its own origin/main `behind` ledger commits ahead."""
    sh = os.path.join(d, "infrastructure", "state", "ledger", "events")
    items = os.path.join(d, "infrastructure", "state", "items")
    os.makedirs(sh)
    os.makedirs(items)

    def git(*a):
        subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@example.invalid"] + list(a), check=True,
                       capture_output=True, stdin=subprocess.DEVNULL)

    def put(evs):
        with open(os.path.join(sh, "BENCH.jsonl"), "a", encoding="utf-8") as f:
            f.writelines(json.dumps(e) + "\n" for e in evs)
    put(events)
    open(os.path.join(items, "keep"), "w").close()
    if prose is not None:
        with open(os.path.join(items, IT + ".md"), "w", encoding="utf-8") as f:
            f.write(prose)
    git("init", "-q", "-b", "main")
    git("add", "-A")
    git("commit", "-q", "-m", IT + ": the real work")
    git("commit", "-q", "--allow-empty", "-m", "ledger: %s note" % IT)
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    if behind:
        for i in range(behind):
            put([{"seat": "BENCH", "event": "note", "id": IT, "text": "later %d" % i, "ts": "2026-11-20T01:00:0%dZ" % i}])
            git("commit", "-q", "-am", "ledger: more")
        git("update-ref", "refs/remotes/origin/main", "HEAD")
        git("reset", "-q", "--hard", "HEAD~%d" % behind)
    return d


def ev(event, i, **k):
    return dict({"seat": "BENCH", "event": event, "id": IT, "ts": "2026-11-20T00:00:%02dZ" % i, "why": "t"}, **k)


EVENTS = [ev("file", 0, title="A title of it", kind="task", target="v1", needs="offline", **{"for": "BENCH"},
             spec="the filed spec text"), ev("claim", 1), ev("start", 2),
          ev("note", 3, text="an early note"), ev("note", 4, text="his call", ownerSaid="make it red"),
          ev("reconcile", 4, verdict="partial", sha="abc1234567", remaining="the second half"),
          dict(ev("finding", 4, type="UNTRIAGED", severity="medium", why="the pump leaks at the seam"), name="FIND_ONE", **{
              "from": IT}),
          ev("live", 4, seat="RUNNER", result="broken", detail="the timer reads disabled"),
          ev("wait", 5, until="2026-12-30T00:00:00Z", reason="the owner walks it"), ev("note", 6, text="the newest note")]


def t_an_unknown_item_is_said():
    with tempfile.TemporaryDirectory() as d:
        c = make_clone(os.path.join(d, "c"), EVENTS, prose="## spec\nthe prose of it")
        g = IP.gather(IT, c)
        t = IP.packet(IT, g)["text"]
        for s in ("A title of it", "the prose of it", "the filed spec text", "an early note", "the owner's words: \"make it red\"",
                  "the owner walks it", "the timer reads disabled",
                  "the second half", "the pump leaks at the seam", "the newest note", IT + ": the real work", "State: doing", "level with origin/main"):
            chk(lambda s=s: s in t, "gather: %s" % s)
        chk(lambda: "ledger: %s note" % IT not in t and "bookkeeping events" in t, "gather: a ledger commit is not a commit of the work")
        chk(lambda: t.count("UNTRIAGED") == 1 and "no time" not in t, "gather: a finding is read once, with its time")
        chk(lambda: "role_unit" not in t and "tsn" not in t, "gather: machine stamps are not text")
        for i in range(IP.COMMITS + 4):
            subprocess.run(["git", "-C", c, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q",
                            "--allow-empty", "-m", "%s: step %d" % (IT + ("_AND_ANOTHER_ITEM" if i < 2 else ""), i)], check=True)
        r = IP.packet(IT, IP.gather(IT, c))
        chk(lambda: "step 1\n" not in r["text"] and "step 15" in r["text"], "gather: a longer item name is another item")
        chk(lambda: any(x.startswith("3 older commit(s)") for x in r["left_out"]) and "git log --extended-regexp --grep=" in
            r["text"], "left-out-is-counted: the commits past the newest ones, with their own command")
        u = IP.packet("RIMMANDRAKE_NOBODY_FILED_THIS_ONE", IP.gather("RIMMANDRAKE_NOBODY_FILED_THIS_ONE", c))
        chk(lambda: "does not know this item" in u["text"] and u["could_not_look"] == [] and "does not know" not in t,
            "an-unknown-item-is-said")
    for bad in ("", "  ", None):
        def raises(bad=bad):
            try:
                IP.packet(bad, facts())
            except ValueError:
                return True
            return False
        chk(raises, "an-unknown-item-is-said: %r is a ValueError" % (bad,))


def t_a_stale_ledger_is_said():
    with tempfile.TemporaryDirectory() as d:
        t = IP.packet(IT, IP.gather(IT, make_clone(os.path.join(d, "c"), EVENTS, behind=3)))["text"]
        chk(lambda: "BEHIND origin/main by 3 commit(s)" in t and "later 0" not in t, "a-stale-ledger-is-said")
    r = pk(ledger=None, why={"ledger": "git is gone"})
    chk(lambda: any("git is gone" in c for c in r["could_not_look"]) and "git is gone" in r["text"],
        "a-stale-ledger-is-said: unreadable is said")


def t_no_spend_in_the_text():
    for s in ("The run used $21.6 of the $30 budget.", "It cost 41.9M weighted tokens.", "That is 12M weighted, all of it.",
              "The spend cap was 3.", "steven has 12% left."):
        r = pk(notes=[n("%s The fix is in foo.py." % s)])
        chk(lambda: not SPEND.search(r["text"]) and "12% left" not in r["text"] and "The fix is in foo.py." in r["text"],
            "no-spend-in-the-text: %s" % s)
        chk(lambda: any("note 1 of 1" in x for x in r["left_out"]) and str(len(r["left_out"])) in r["text"],
            "no-spend-in-the-text: and it is counted")
    for k, v in (("title", "a $30 budget"), ("prose", "x\nA $30 budget.\ny"), ("commits", [{"sha": "a", "subject": "$9 spend"}]),
                 ("linked", [{"id": "A", "state": "done", "title": "cap the $9 spend"}]), ("criteria", ["under $30 spend"]),
                 ("runs", [{"ts": "t", "result": "pass", "evidence": "used $3 budget"}]),
                 ("notes", [n("x", owner_said="a $30 budget")])):
        chk(lambda: not SPEND.search(pk(**{k: v})["text"]), "no-spend-in-the-text: in the %s" % k)
        chk(lambda: pk(**{k: v})["left_out"], "no-spend-in-the-text: in the %s, counted" % k)
    r = pk(title="cap the $9 spend", state="doing; the account resets Tuesday")
    chk(lambda: len(r["left_out"]) == 2 and any("title" in x for x in r["left_out"]) and "LEFT OUT of this packet: 2" in
        r["text"] and "Nothing was left out" not in r["text"] and "Title: (left out, below)" in r["text"],
        "no-spend-in-the-text: the title and the state, counted")


BLIND = (("blind judge", "You are the blind judge: you did not build this mod."),
         ("blind judge", "You are a NEW blind judge."),
         ("blind judge", "**You are the same blind judge, resumed (session x).**"),
         ("blind judge", "## You judge ExplosiveKnockback blind: run judge-1"),
         ("fresh reader", "You are ONE fresh reader. You made none of this version's evidence writes."),
         ("fresh reader", "- You are the one fresh reader of each mod fix made in the sitting."),
         ("fresh reader", "You are a detached Opus reader for the Conductor."),
         ("fresh reader", "Work list item X.\n\nTitle: One fresh reader reads the file"),
         ("examiner", "You are the Designer's Examiner, a different agent."),
         ("challenger", "You are the Challenger, a second fresh agent."),
         ("coverage judge", "You are the coverage judge for the RimMandrake concept at X."))


def t_blind_roles_get_none():
    import card_capture
    import control
    import coverage_judge
    import detached_helper as DH
    import left_open_continue as LOC
    import maturation as M
    import maturation_autonomy as MA
    for role, text in BLIND:
        m = DH.brief_message("# Work\n\n%s\n" % text, IT, "BENCH", REPO)
        chk(lambda: IP.role_of(text) == role, "blind-roles-get-none: %s: %s" % (role, text[:40]))
        chk(lambda: "ITEM PACKET" not in m and "cli.py show" not in m and "You start fresh (%s)" % role in m and text in m,
            "blind-roles-get-none: the brief of a %s holds no packet" % role)
    # a resume or a continuation has another text: the first launch leaves the role on the run's env, which they carry
    for role, text in BLIND[4:6] + (("blind judge", "Judge it."),):
        rec = {"env": {"RM_CONTROL_STAGE": "blind_challenge"} if text == "Judge it." else {"RM_CONTROL_MOD": "X"}}
        DH.mark_fresh(rec, text)
        chk(lambda: rec["env"].get(IP.ROLE_ENV) == role and "ITEM PACKET" not in DH.brief_message(
            "You were stopped by a fleet stop; carry on.", IT, "BENCH", "/c", env=rec["env"]),
            "blind-roles-get-none: the resume of a %s" % role)
    with tempfile.TemporaryDirectory() as d:        # `launch --resume SESSION` by hand, with a short brief and no --env
        src = os.path.join(d, "b.md")
        with open(src, "w", encoding="utf-8") as f:
            f.write("You are the blind judge.")
        os.makedirs(os.path.join(d, "detached"))
        for unit, item, k in (("rm-detached-u1", IT, {"brief_src": src}), ("rm-detached-u2", IT, {"env": {
                IP.ROLE_ENV: "challenger"}}), ("rm-detached-u3", IT, {"brief_src": os.path.join(d, "gone.md")})):
            DH.write_record(dict({"unit": unit, "item": item, "session": "sess-" + unit, "at": 5.0, "seat": "BENCH"}, **k), d)
        for unit, item, role in (("rm-detached-u1", IT, "blind judge"), ("rm-detached-u2", IT, "challenger"),
                                 ("rm-detached-u3", IT, None), ("rm-detached-u1", IT + "_TWO", None), ("none", IT, None)):
            rec = {"item": item}
            DH.mark_fresh(rec, "carry on", "sess-" + unit, d)
            chk(lambda: (rec.get("env") or {}).get(IP.ROLE_ENV) == role, "blind-roles-get-none: --resume of %s: %s" % (
                unit, role))
    with tempfile.TemporaryDirectory() as d:
        c = make_clone(os.path.join(d, "c"), EVENTS)
        state, projects = os.path.join(d, "state"), os.path.join(d, "projects")
        sid, unit = "examiner-session", "rm-detached-examiner"
        project = os.path.join(projects, "c")
        os.makedirs(project)
        with open(os.path.join(project, sid + ".jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "assistant", "message": {"usage": {"input_tokens": 150000}}}) + "\n")
        src = os.path.join(d, "exam.md")
        with open(src, "w", encoding="utf-8") as f:
            f.write("Read the design.")
        DH.write_record({"unit": unit, "item": IT, "session": sid, "at": 5.0, "seat": "BENCH",
                         "brief_src": src, "env": {IP.ROLE_ENV: "examiner"}}, state)
        progress = ev("note", 7, text="PROGRESS: the first part is read")

        def launch(seat, item, brief, model, max_s, budget, clone, skip_launch_checks, env, resume_session, extra):
            return DH._launch_locked(seat, item, brief, model, max_s, budget, 10.0, None, clone, clone,
                                     skip_launch_checks=skip_launch_checks, env=env, resume=(resume_session, projects),
                                     extra=extra)

        with patch.dict(os.environ, RM_DISPATCHER_STATE=state), patch.object(LOC, "CONDUCTOR_PROJECTS", projects), \
                patch.object(DH, "read_item", return_value={"notes": [progress]}), patch.object(DH, "launch", launch), \
                patch.object(DH, "clone_holders", return_value=[]), patch.object(DH, "launch_argv", return_value=[]), \
                patch.object(control, "launch_unit", return_value=subprocess.CompletedProcess([], 0)):
            rc = DH.main(["launch", "--seat", "BENCH", "--item", IT, "--brief", "Carry on.", "--resume", sid,
                          "--clone", c, "--skip-launch-checks", "selftest", "--budget-usd", "0"])
        rec = DH.read_record(DH.unit_name("BENCH", IT, 10.0), state)
        with open(rec["brief_file"], encoding="utf-8") as f:
            msg = f.read()
        chk(lambda: rc == 0 and rec.get("resume_converted_from") == sid and not rec.get("resume_session")
            and progress["text"] in msg and "150000 tokens" in msg, "blind-roles-get-none: manual resume converts at 150000")
        chk(lambda: (rec.get("env") or {}).get(IP.ROLE_ENV) == "examiner" and "You start fresh (examiner)" in msg
            and "ITEM PACKET" not in msg and "cli.py show" not in msg,
            "blind-roles-get-none: a converted manual resume keeps the examiner role and no packet or show command")
    with tempfile.TemporaryDirectory() as d:
        unit = "rm-detached-blind-judge"
        at = DH._epoch(EVENTS[2]["ts"])
        rec = {"unit": unit, "item": IT, "seat": "BENCH", "at": at, "result": "success (exited 0)",
               "env": {"RM_CONTROL_STAGE": "blind_challenge"}}
        opened = {"state": "doing", "notes": [ev("note", 7, text="LEFT OPEN: finish the remaining checks")]}
        gates = dict.fromkeys(LOC.GATES, lambda _: None)
        rec["continue_plan"] = LOC.plan(rec, opened, {}, now=at + 8, gates=gates, root=d)
        DH.write_record(rec, d)
        launched = {}

        def capture(seat, item, brief, model, max_s, budget, **kw):
            launched.update(kw)
            launched["brief"] = DH.brief_message(brief, item, seat, d, env=kw["env"])
            return 0, "DETACHED rm-detached-blind-continued"

        with patch.object(card_capture, "item_cards", return_value=[]):
            r = LOC.run(unit, now=at + 9, launch_fn=capture, gates=gates, root=d, reader=lambda _: opened,
                        log_path=os.path.join(d, "conductor.md"), projects=os.path.join(d, "projects"),
                        plan_dir=os.path.join(d, "no_account_notice"))     # never the live account's drain
        msg = launched.get("brief", "")
        chk(lambda: r["act"] == "continued" and not launched.get("resume_session")
            and launched["extra"]["continue_how"] == "fresh" and opened["notes"][0]["text"] in msg,
            "blind-roles-get-none: a blind_challenge with a LEFT OPEN note continues fresh")
        chk(lambda: "You start fresh (blind judge)" in msg and "ITEM PACKET" not in msg and "cli.py show" not in msg,
            "blind-roles-get-none: a blind_challenge continuation has no item packet or show command")
    maker = {}
    DH.mark_fresh(maker, "Build it.")
    chk(lambda: maker == {}, "blind-roles-get-none: a maker's record gets no role")
    lk = inspect.getsource(DH._launch_locked)
    chk(lambda: lk.index("mark_fresh(rec, brief, resume_session, root)") < lk.index("reserve_record(") < lk.index("brief_message("),
        "blind-roles-get-none: _launch_locked marks the record before it is written")
    for stage in ("blind_challenge", "pre_human"):
        chk(lambda: "ITEM PACKET" not in DH.brief_message("Fix it.", IT, "BENCH", "/c", env={"RM_CONTROL_STAGE": stage}),
            "blind-roles-get-none: the stage %s" % stage)
    chk(lambda: IP.role_of("Read this.", {IP.ROLE_ENV: "examiner"}) == "examiner", "blind-roles-get-none: said on the launch")
    # the texts that the pipeline itself writes for these roles
    chk(lambda: IP.role_of(inspect.getsource(M.judge_resumed_text)) == "blind judge", "blind-roles-get-none: the resumed judge")
    chk(lambda: IP.role_of(M.blind_brief_text(REPO, "Pyrelands")[0]) == "blind judge",
        "blind-roles-get-none: maturation.blind_brief_text")
    chk(lambda: "You are the one fresh reader of each mod fix" in inspect.getsource(MA), "blind-roles-get-none: the steward's text")
    with open(os.path.join(HERE, "roles", "walk_brief.md"), encoding="utf-8") as f:
        walk = f.read()
    chk(lambda: IP.role_of(walk) == "fresh reader", "blind-roles-get-none: roles/walk_brief.md")
    chk(lambda: "You are the coverage judge" in inspect.getsource(coverage_judge) and "brief_message" not in
        inspect.getsource(coverage_judge) and "item_packet" not in inspect.getsource(coverage_judge),
        "blind-roles-get-none: coverage_judge launches its own run, with no packet")
    for text in ("You are a detached Opus helper of the Conductor. One fresh reader who did not make it reads the file.",
                 "Do not start a blind judge; you are the builder. The coverage judge reads later.", "Title: fix the reader"):
        chk(lambda: IP.role_of(text, {"RM_CONTROL_STAGE": "offline_build"}) is None,
            "blind-roles-get-none: a maker is not one: %s" % text[:36])


def t_every_detached_launch_carries_the_packet():
    import detached_helper as DH
    import list_dispatch as LD
    with tempfile.TemporaryDirectory() as d:
        c = make_clone(os.path.join(d, "c"), EVENTS, prose="## spec\nthe prose of it")
        m = DH.brief_message("Do the work.", IT, "BENCH", c, 60, {"RM_CONTROL_STAGE": "offline_build"})
        chk(lambda: m.startswith("Do the work.") and "ITEM PACKET of " + IT in m and "the newest note" in m
            and m.index("the newest note") < m.index("You are a DETACHED helper"),
            "every-detached-launch-carries-the-packet: between the brief and the footer")
    src = inspect.getsource(DH._launch_locked)
    chk(lambda: re.search(r"brief_message\(brief, item, seat, clone, max_s, rec\.get\(\"env\"\)\)", src),
        "every-detached-launch-carries-the-packet: _launch_locked, with the run's env")
    chk(lambda: src.index('rec["brief_src"]') < src.index("brief_message("),
        "every-detached-launch-carries-the-packet: the kept brief holds none, so a relaunch carries one, not two")
    chk(lambda: "ITEM PACKET" in LD.brief_text(IT, {"title": "t", "effect": "cmd:x"}, {"run_n": 1}),
        "every-detached-launch-carries-the-packet: the Workshop Pipeline's Work brief reads it")


def t_a_launch_never_fails_on_the_packet():
    import detached_helper as DH
    for name in ("gather", "packet", "role_of"):
        real = getattr(IP, name)
        setattr(IP, name, lambda *a, **k: 1 / 0)
        try:
            m = DH.brief_message("Do the work.", IT, "BENCH", "/tmp/clone")
        finally:
            setattr(IP, name, real)
        chk(lambda: m.startswith("Do the work.") and "could not look (ZeroDivisionError" in m and "cli.py show " + IT in m
            and "You are a DETACHED helper" in m, "a-launch-never-fails-on-the-packet: %s raised" % name)


def main():
    for t in (t_holds_the_item, t_decisive_notes_are_kept, t_oldest_routine_notes_go_first, t_a_note_is_whole_or_left_out,
              t_left_out_is_counted, t_could_not_look_is_said, t_an_unknown_item_is_said,
              t_a_stale_ledger_is_said, t_no_spend_in_the_text, t_blind_roles_get_none,
              t_every_detached_launch_carries_the_packet, t_a_launch_never_fails_on_the_packet):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            chk(lambda: False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
