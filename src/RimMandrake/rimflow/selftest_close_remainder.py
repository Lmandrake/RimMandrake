#!/usr/bin/env python3
"""selftest_close_remainder.py: a close whose words name unbuilt spec parts files them first.

Page design/specs/2026-11-24-close-files-its-remainder/boundary.md. The close tests run the real cli.py on a throwaway
ledger; the run-end test calls detached_helper's own function and its real ledger reader text.

    python3 src/RimMandrake/rimflow/selftest_close_remainder.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="selftest_close_remainder_")
os.environ.setdefault("RM_CONDUCTOR_LOG", os.path.join(TMP, "conductor.log"))
import close_remainder as CR    # noqa: E402

FAILS = []
RUN, TICK = "rm-detached-bench-some-item-1795529016", "rm-list-effect.service"
ITEM = "RIMMANDRAKE_ASK_LANE_IN_ONE_LINE"
# the words of the two runs of 2026-11-24
ASK_EVIDENCE = ("ask_lane_accept.py PASS 11/11; selftest_ask_lane 8 promises, planted faults caught. Untested: live ssh refresh "
                "(host_facts.py refresh), filler/visit-feed wiring, companion hold, login alarm timer")
ASK_SPEC = ("## spec\n\n- `host_facts.py`: one ssh read each hour of installed package ids.\n- It holds the job until its "
            "companion is staged.\n- The filler, the visit feed and `submit` read the same facts.\n- A login with under 3 days "
            "left raises one alarm that names the account.\n\n## verify\n\nx\n")
LANE_NOTE = ("Partial scope: not built — wait-instead-of-drop retire, ingest.repair 3-in-24h rule, boundary page. Check holds "
             "(8/8) on lane_ticket + steward cause-named mint + ops_watch incident clock.")
ASK_REPORT = ("The item is closed at `3b6525ea42ea`.\n\n- **Built:** `host_facts.py`\n- **Not tested:**\n  - **Filler and visit "
              "feed:** they do not read the facts yet.\n- **Left unbuilt:** the spec's fresh-reader read of the changed files.\n")


def check(cond, what):
    print(("ok    " if cond else "FAIL  ") + what)
    if not cond:
        FAILS.append(what)


class Led:
    """One throwaway ledger with ITEM started, and the real cli on it."""
    n = 0

    def __init__(self, spec=""):
        Led.n += 1
        self.dir = os.path.join(TMP, "l%d" % Led.n)
        self.items = os.path.join(self.dir, "items")
        os.makedirs(os.path.join(self.items, "closed"))
        self.path = os.path.join(self.dir, "events.jsonl")
        self.sha = subprocess.run(["git", "log", "origin/main", "-1", "--format=%H", "--", "src/RimMandrake/Utils/boundary_check.py"],
                                  cwd=REPO, capture_output=True, text=True, timeout=60).stdout.strip()
        self.ok("file", ITEM, "--for", "BENCH", "--title", "the lane")
        self.ok("start", ITEM)
        if spec:
            with open(os.path.join(self.items, ITEM + ".md"), "w") as f:
                f.write(spec)

    def cli(self, *args, unit=RUN, seat="BENCH"):
        env = {k: v for k, v in os.environ.items()
               if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RM_ROLE_UNIT", "RIMFLOW_GITINDEX")}
        env.update(RIMFLOW_LEDGER=self.path, RIMFLOW_ITEMS=self.items, RIMFLOW_SEAT=seat, AGENT_SEAT=seat)
        if unit:
            env["RM_ROLE_UNIT"] = unit
        r = subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), *args, "--why", "selftest"], cwd=REPO, env=env,
                           capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout + r.stderr

    def ok(self, *args, **kw):
        rc, out = self.cli(*args, **kw)
        if rc:
            raise AssertionError("%s -> %d: %s" % (" ".join(args), rc, out[-600:]))
        return out

    def close(self, *more, **kw):
        base = ["close", ITEM] + ([] if "--no-code" in more else ["--sha", self.sha]) + ["--live", "once: selftest"]
        return self.cli(*base, *more, **kw)

    def events(self, verb=None, iid=None):
        import model
        model.EVENTS = self.path
        evs = model.read()
        return [e for e in evs if (not verb or e["event"] == verb) and (not iid or e.get("id") == iid)]

    def closed(self):
        return bool(self.events("close", ITEM))


def t_a_run_whose_evidence_names_unbuilt_parts_is_answered_with_the_repair():
    led = Led()
    n = len(led.events())
    rc, out = led.close("--evidence", "PASS 8/8; the boundary page is not built")
    check(rc != 0 and not led.closed() and len(led.events()) == n, "evidence: the close is refused and writes nothing (rc %d)" % rc)
    check("cli.py file RIMMANDRAKE_FINISH_" in out and "--caused-by " + ITEM in out and "close again" in out
          and "the boundary page is not built" in out, "evidence: the answer holds the repair and the part (%s)" % out[-300:])
    for words in (("--no-code", "study done; the second table is unbuilt"), ("--reason", "done but for the login alarm, not wired")):
        rc, out = Led().close(*words)
        check(rc != 0 and "cli.py file" in out, "evidence: %s is read too" % words[0])


def t_a_run_whose_last_note_names_unbuilt_parts_is_answered():
    led = Led()
    led.ok("note", ITEM, "--text", LANE_NOTE)
    rc, out = led.close("--evidence", "lane_cause_once_accept PASS 8/8")
    check(rc != 0 and not led.closed() and "wait-instead-of-drop" in out, "note: the run of 6:32 AM is answered (rc %d)" % rc)
    led.ok("note", ITEM, "--text", "All three are built at abc1234")
    check(led.close("--evidence", "PASS 8/8")[0] == 0, "note: an older note is not read once a later one stands")
    led = Led()
    led.ok("note", ITEM, "--text", LANE_NOTE)
    led.ok("note", ITEM, "--text", "DETACHED run x ended success. Result: closed.")
    check(led.close()[0] != 0, "note: a run-ended note does not hide the run's own last note")
    led = Led()
    led.ok("note", ITEM, "--text", LANE_NOTE)
    led.ok("note", ITEM, "--text", "DETACHED run x ended success. Result: part x is not built.")
    led.ok("start", ITEM)
    check(led.close("--evidence", "PASS 8/8")[0] == 0, "note: a note before the last start is another run's")


def t_an_untested_spec_part_is_answered():
    led = Led(ASK_SPEC)
    rc, out = led.close("--evidence", ASK_EVIDENCE)
    check(rc != 0 and not led.closed() and "filler/visit-feed wiring" in out and "companion hold" in out,
          "untested: the run of 6:18 AM is answered (rc %d %s)" % (rc, out[-300:]))
    check(Led(ASK_SPEC).close("--evidence", "PASS 11/11. Untested: a Mac browser, the colour of the page")[0] == 0,
          "untested: what the spec does not name is not asked")
    check(Led().close("--evidence", ASK_EVIDENCE)[0] == 0, "untested: an item with no spec is not asked")


def t_the_same_close_passes_after_the_remainder_is_filed():
    words = ("--evidence", "PASS 8/8; the boundary page is not built")
    led = Led()
    led.ok("file", "RIMMANDRAKE_FIX_OTHER_FAULT_SEEN", "--for", "BENCH", "--title", "another fault", "--caused-by", ITEM)
    check(led.close(*words)[0] != 0, "filed: another ticket that the item caused is not its remainder")
    led.ok("file", "RIMMANDRAKE_WRITE_PAGE_FOR_THE_LANE", "--for", "BENCH", "--title", "Remainder of %s: the page" % ITEM,
           "--caused-by", ITEM)
    rc, out = led.close(*words)
    check(rc == 0 and led.events("close", ITEM)[0].get("remainder") == "RIMMANDRAKE_WRITE_PAGE_FOR_THE_LANE",
          "filed: the same close passes and names it (rc %d %s)" % (rc, out[-200:]))
    led = Led()
    led.ok("file", "RIMMANDRAKE_WRITE_PAGE_FOR_THE_LANE", "--for", "BENCH", "--title", "the page")
    check(led.close(*words, "--remainder", "RIMMANDRAKE_NO_SUCH_ITEM_HERE")[0] != 0, "filed: --remainder with no such item is refused")
    check(led.close(*words, "--remainder", ITEM)[0] != 0, "filed: --remainder with the item itself is refused")
    check(not led.closed(), "filed: and the item is open")
    check(led.close(*words, "--remainder", "RIMMANDRAKE_WRITE_PAGE_FOR_THE_LANE")[0] == 0, "filed: --remainder lets it close")
    led = Led()
    led.ok("file", "RIMMANDRAKE_WRITE_PAGE_FOR_THE_LANE", "--for", "BENCH", "--title", "the page")
    check(led.close("--evidence", "PASS; the page is not built (RIMMANDRAKE_WRITE_PAGE_FOR_THE_LANE). The alarm is unwired.")[0] != 0,
          "filed: an id in one sentence does not hold the part of another")
    check(led.close("--evidence", "PASS; the page is not built (RIMMANDRAKE_WRITE_PAGE_FOR_THE_LANE)")[0] == 0,
          "filed: an id beside the part lets it close")
    led = Led()
    led.ok("file", "RIMMANDRAKE_WRITE_PAGE_FOR_THE_LANE", "--for", "BENCH", "--title", "Remainder of it", "--caused-by", ITEM)
    led.ok("drop", "RIMMANDRAKE_WRITE_PAGE_FOR_THE_LANE", "--reason", "not worth the touch: test")
    check(led.close(*words)[0] != 0, "filed: a dropped ticket is not a remainder")
    check(led.close(*words, "--remainder", "RIMMANDRAKE_WRITE_PAGE_FOR_THE_LANE")[0] != 0, "filed: --remainder with a dropped item is refused")


def t_no_remainder_closes_with_its_reason_recorded():
    led = Led()
    words = ("--evidence", "PASS; not wired into visit code, as the brief says")
    check(led.close(*words, "--no-remainder", " ")[0] != 0 and not led.closed(), "no-remainder: an empty reason is refused")
    rc, out = led.close(*words, "--no-remainder", "the brief leaves the wiring to another item")
    check(rc == 0 and led.events("close", ITEM)[0].get("noRemainder") == "the brief leaves the wiring to another item",
          "no-remainder: closes with the reason on the event (rc %d %s)" % (rc, out[-200:]))


def t_words_that_name_nothing_unbuilt_close_as_before():
    for words in ("PASS 8/8; no part is unbuilt", "all built, nothing left unbuilt", "0 spec parts not built", "Not built: none.",
                  "selftest green; live: UNRUN, `python3 x.py`", "rebuilt the page; the built page opens"):
        led = Led()
        rc, out = led.close("--evidence", words)
        ev = led.events("close", ITEM)
        check(rc == 0 and ev and "remainder" not in ev[0] and "noRemainder" not in ev[0] and len(led.events("file")) == 1,
              "plain: %r closes with no extra step (rc %d %s)" % (words, rc, out[-200:] if rc else ""))
    check(CR.named("Not built: none of the three parts") == [] and CR.named("Nothing is done: the alarm is not built")
          and CR.named("the page is not built, 0 tests red"),
          "plain: a denial does not hide a later part")


def t_a_program_close_files_the_remainder_itself_and_closes():
    led = Led()
    led.ok("note", ITEM, "--text", LANE_NOTE)
    rc, out = led.close("--no-code", "outcome check cmd:x holds at abc1234. Output: PASS", unit=TICK)
    filed = [e for e in led.events("file") if e.get("caused_by") == ITEM]
    order = [e["event"] for e in led.events()][-3:]
    check(rc == 0 and led.closed() and len(filed) == 1 and order == ["file", "note", "close"],
          "program: one remainder filed, then the close (rc %d %s %s)" % (rc, order, out[-200:]))
    if filed:
        check(led.events("close", ITEM)[0].get("remainder") == filed[0]["id"] and "wait-instead-of-drop" in filed[0]["title"]
              and "wait-instead-of-drop" in led.events("note", filed[0]["id"])[0]["text"], "program: linked, with the words")
    led = Led()
    rc, out = led.close("--no-code", "outcome check cmd:x holds. Output: FAIL-list: page not built, 0 left", unit=TICK)
    check(rc == 0 and len(led.events("file")) == 1, "program: its check's output is not read as a statement about the work")


def t_the_owner_and_the_conductor_window_are_never_refused():
    led = Led()
    rc, out = led.close("--evidence", "PASS; the page is not built", unit=None)
    ev = (led.events("close", ITEM) or [{}])[0]
    check(rc == 0 and any("the page is not built" in n for n in ev.get("form_notes") or []) and len(led.events("file")) == 1,
          "principal: the Conductor window's close goes on, noted (rc %d %s)" % (rc, out[-200:]))
    led = Led()
    rc, out = led.close("--reason", "the page is not built, close it", "--owner-said", "close it, the page is not built", unit=None)
    check(rc == 0 and led.closed(), "principal: the owner's close goes on (rc %d %s)" % (rc, out[-200:]))


def t_a_run_end_files_the_remainder_its_report_declares_once():
    import detached_helper as DH
    led = Led()
    led.ok("close", ITEM, "--sha", led.sha, "--live", "once: selftest", "--evidence", "PASS 11/11")
    prog = DH.READ_ITEM
    rec = {"unit": RUN, "item": ITEM, "seat": "BENCH", "clone": REPO}

    def read(item=ITEM):
        bound = prog.replace("import model\n", "import model\nmodel.EVENTS = %r\n" % led.path, 1)
        r = subprocess.run([sys.executable, "-c", bound, item], cwd=REPO, capture_output=True, text=True, timeout=120)
        return json.loads(r.stdout)

    def runner(argv, **kw):
        rc, out = led.cli(*argv[2:argv.index("--seat")], unit=RUN)
        return subprocess.CompletedProcess(argv, rc, out, "")
    boom = []
    trap = lambda argv, **kw: boom.append(argv) or subprocess.CompletedProcess(argv, 0, '', '')     # noqa: E731
    got = read()
    check(got["state"] == "done" and got["rest"].get("unit") == RUN, "run end: the reader sees the run's own close (%s)" % got["rest"].get("blind"))
    check(DH.file_remainder(rec, got, "All parts of the spec are built; the old page was not built by us.", trap) == "" and not boom,
          "run end: a report that only mentions the word files nothing")
    check(DH.file_remainder(rec, dict(got, state="doing"), ASK_REPORT, trap) == "" and not boom,
          "run end: an item still open files nothing")
    check(DH.file_remainder(dict(rec, unit="rm-detached-other"), got, ASK_REPORT, trap) == "" and not boom,
          "run end: an item that another run closed files nothing")
    bad = lambda argv, **kw: subprocess.CompletedProcess(argv, 4, "", "no disk")     # noqa: E731
    check("remainder FAILED" in DH.file_remainder(rec, got, ASK_REPORT, bad), "run end: a failed filing is named")
    check("could not look" in DH.file_remainder(rec, {"state": "done", "rest": {"blind": "X"}}, ASK_REPORT, trap),
          "run end: a ledger that could not be read is said")
    step = DH.file_remainder(rec, got, ASK_REPORT, runner)
    filed = [e for e in led.events("file") if e.get("caused_by") == ITEM]
    check("remainder filed" in step and len(filed) == 1 and "fresh-reader" in filed[0]["title"],
          "run end: the run of 6:18 AM files one ticket (%s)" % step)
    notes = led.events("note", filed[0]["id"]) if filed else []
    check(bool(notes) and "do not read the facts yet" in notes[0]["text"], "run end: the note holds the whole report")
    check(DH.file_remainder(rec, read(), ASK_REPORT, runner) == "" and len(led.events("file")) == 2, "run end: a second end files nothing")
    led = Led()
    led.ok("close", ITEM, "--sha", led.sha, "--live", "once: selftest", "--no-remainder", "out of the spec")
    check(DH.file_remainder(rec, read(), ASK_REPORT, trap) == "" and not boom, "run end: noRemainder on the close files nothing")
    check(len(CR.declared("- **Not built:**\n  - the timer\n  - the alarm\n\nDone.")) == 1
          and "the alarm" in CR.declared("- **Not built:**\n  - the timer\n  - the alarm\n\nDone.")[0], "run end: sub-bullets are kept")
    # that finish calls it: selftest_detached_helper, `remainder:` lines


def main():
    tests = [t_a_run_whose_evidence_names_unbuilt_parts_is_answered_with_the_repair,
             t_a_run_whose_last_note_names_unbuilt_parts_is_answered,
             t_an_untested_spec_part_is_answered,
             t_the_same_close_passes_after_the_remainder_is_filed,
             t_no_remainder_closes_with_its_reason_recorded,
             t_words_that_name_nothing_unbuilt_close_as_before,
             t_a_program_close_files_the_remainder_itself_and_closes,
             t_the_owner_and_the_conductor_window_are_never_refused,
             t_a_run_end_files_the_remainder_its_report_declares_once]
    try:
        for t in tests:
            t()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("selftest_close_remainder: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
