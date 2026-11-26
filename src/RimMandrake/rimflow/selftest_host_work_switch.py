#!/usr/bin/env python3
"""selftest_host_work_switch.py - the host work switch, and the owner's age filter on every bundle.

Item RIMMANDRAKE_VET_WORK_BOUND_FOR_STEVEDESKTOP_HE_SAW_FIREHAWK_AGAIN. Failures that happened on 2026-11-25:
- the owner's order (SteveDesktop works pipeline improvements only) had no switch that a program reads; the filler,
  the list launcher and the bundles could each put mod work on SteveDesktop;
- four bundles took 60 tickets, many filed before the Maturation Pipeline, with no test that was red that day; the
  reality sort closed only the green ones and admitted the rest. The owner, 2026-11-25: "We must ALWAYS Filter old
  tickets into any process, yes. The older, the more grinding required to prove they're not harmful."

  python3 selftest_host_work_switch.py      every check; exit 1 on any failure

A temp switch file stands in for the real one; no ledger, ssh, git or game is touched.
"""
import json
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="hws_")
SW = os.path.join(TMP, "host_work_switch.json")
os.environ["RM_HOST_SWITCH_FILE"] = SW
os.environ["RM_WORK_BUNDLE_DIR"] = os.path.join(TMP, "wb")

import host_work_switch as H  # noqa: E402
import work_bundle as W  # noqa: E402
import list_dispatch as L  # noqa: E402

FAILS = []
NOW = W._ts("2026-11-25T22:00:00Z")
SAID = "I'd like to have SteveDesktop working 100% on closing out non-mod work today please."
NOT_CONDUCTOR = {"RM_ROLE_UNIT": "rm-detached-bench-x", "AGENT_SEAT": "BENCH"}


def check(ok, what):
    print("%s  %s" % ("PASS" if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


def raises(fn, kind):
    try:
        fn()
    except kind:
        return True
    except Exception:  # noqa: BLE001 - the wrong kind is a failure of the check
        return False
    return False


def t_switch():
    with open(SW, "w") as f:
        json.dump({"switches": []}, f)
    check(H.switched("SteveDesktop") is None, "no row: SteveDesktop is not switched")
    check(raises(lambda: H.set_switch("SteveDesktop"), ValueError), "set without authority is refused")
    H.set_switch("SteveDesktop", said=SAID, today="2026-11-24")
    sw = H.switched("Steve2")
    check(bool(sw) and SAID in sw and "lift SteveDesktop" in sw,
          "set with his words: Steve1/Steve2 read it, with his words and the lift command (%s)" % sw)
    check(H.switched("ArchBig") is None, "the other machine is not switched")
    check(raises(lambda: H.lift("SteveDesktop", per_ruling=H.CONDUCTOR_ACT, why="x", env=NOT_CONDUCTOR), ValueError),
          "a helper (RM_ROLE_UNIT set) cannot lift it by the Conductor's ruling")
    check(raises(lambda: H.lift("SteveDesktop"), ValueError), "a lift without authority is refused")
    gone = H.lift("SteveDesktop", said="Lift it.", today="2026-11-26")
    check(H.switched("SteveDesktop") is None and gone.get("lifted_said") == "Lift it.",
          "his lift removes it and keeps the lifted row with his words")
    check(raises(lambda: H.lift("SteveDesktop", said="again"), KeyError), "lifting an unswitched host says so")
    with open(SW, "w") as f:
        f.write("{not json")
    check(bool(H.switched("SteveDesktop")), "an unreadable file reads as switched (could not look)")


def t_age_filter():
    it = lambda **kw: types.SimpleNamespace(**dict({"created_at": "2026-11-24T10:00:00Z", "runs": [], "findings": [],  # noqa: E731
                                                    "raised": None, "spawned_by": None, "live_broken": None,
                                                    "kind": "task"}, **kw))
    old = it(created_at="2026-10-10T10:00:00Z")
    check(W.age_refusal(old, "fails", NOW) is None, "an old ticket with a test red today is admitted")
    for v in (None, "no_test", "holds_unproven", "unmeasured"):
        y = W.age_refusal(old, v, NOW)
        check(bool(y) and "before the Maturation Pipeline" in y, "an old ticket whose test reads %s is refused" % v)
    check(bool(W.age_refusal(it(), "no_test", NOW)), "a new ticket with no red test and no recorded failure is refused")
    for kw in ({"spawned_by": "RUNNER"}, {"raised": "2026-11-24T10:00:00Z"}, {"kind": "bug"},
               {"findings": ["F1"]}, {"runs": [types.SimpleNamespace(result="fail")]}):
        check(W.age_refusal(it(**kw), "no_test", NOW) is None, "a new ticket with a recorded failure %s is admitted" % kw)
    check(bool(W.age_refusal(old, None, NOW)) and bool(W.age_refusal(it(created_at=None), None, NOW)),
          "an old joiner, and one with no filing date, are refused")


def t_bundle_command_filters():
    items = {i: {"id": i, "created_at": c, "kind": "task", "state": "proposed", "home": {"home": "pipeline:test-lane"}}
             for i, c in (("OLD_RED", "2026-10-01T00:00:00Z"), ("OLD_NOTEST", "2026-10-01T00:00:00Z"),
                          ("NEW_BUG", "2026-11-24T00:00:00Z"), ("NEW_NOTEST", "2026-11-24T00:00:00Z"))}
    items["OLD_RED"]["effect"] = "cmd:false"
    items["NEW_BUG"]["kind"] = "bug"
    launched = []

    def launcher(rec, text):
        launched.append(list(rec["members"]))
        return 0, "ok", "unit-1"
    got = W.bundle_command("pipeline:test-lane", list(items), items, "test", NOW, prose_of=lambda i: "",
                           run_effect=lambda what, root: ("fails", "red"), run_script_fn=lambda p, r: ("fails", ""),
                           sha="abc", refused=lambda i: None, held=lambda i: None, leased=lambda it: False,
                           launcher=launcher, closer=lambda *a: (0, ""), dry=True)
    check(sorted(got["ready"]) == ["NEW_BUG", "OLD_RED"],
          "the bundle takes the old ticket with a red test and the new bug, nothing else (%s)" % got["ready"])
    check(all(str(got["out"].get(i, "")).startswith("UNVETTED") for i in ("OLD_NOTEST", "NEW_NOTEST")),
          "the unvetted members are left out with their reason (%s)" % {i: got["out"].get(i, "")[:60] for i in got["out"]})


def t_mod_work_not_sent_to_a_switched_host():
    with open(SW, "w") as f:
        json.dump({"switches": [{"host": "SteveDesktop", "mode": "pipeline", "date": "2026-11-24", "said": SAID}]}, f)
    called = []
    rc, rec = W.launch_remote("SteveDesktop", "mod:DivingInteraction", ["X"], "test", "maturation", now=NOW,
                              runner=lambda *a, **k: called.append(a))
    check(rc == 3 and rec.get("decision") == "host_refused" and not called,
          "a mod bundle is not sent to a switched host, and no ssh runs (%s, %s)" % (rc, rec))
    check(W.switch_refusal("SteveDesktop", "pipeline:bridge") is None, "a pipeline bundle still goes there")
    no = L.switch_refuses("SteveDesktop", {"mod_work": {"mod": "Pyrelands"}})
    check(bool(no) and "no mod work" in no, "the list launcher gives a mod ticket no room on it (%s)" % no)
    check(bool(L.switch_refuses("SteveDesktop", {"mod_work": {"unreadable": "x"}})),
          "a ticket whose mod cannot be read gets no room there either")
    check(L.switch_refuses("SteveDesktop", {"mod_work": {"mod": None}}) is None, "a pipeline ticket gets room")


def t_status_page_shows_it():
    import importlib.util
    mp = os.path.join(HERE, "..", "Utils", "maturation_now.py")
    sys.path.insert(0, os.path.abspath(os.path.dirname(mp)))
    spec = importlib.util.spec_from_file_location("maturation_now", os.path.abspath(mp))
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    with open(SW, "w") as f:
        json.dump({"switches": [{"host": "SteveDesktop", "mode": "pipeline", "date": "2026-11-24", "said": SAID}]}, f)
    line = M.switch_line()
    check("SteveDesktop: Claude work is pipeline improvements only" in line and "lift SteveDesktop" in line,
          "the status page names the switch and its lift: %s" % line)
    with open(SW, "w") as f:
        json.dump({"switches": []}, f)
    check("no machine is switched" in M.switch_line(), "and says when no machine is switched")


def main():
    t_switch()
    t_status_page_shows_it()
    t_age_filter()
    t_bundle_command_filters()
    t_mod_work_not_sent_to_a_switched_host()
    print("FAILED %d" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
