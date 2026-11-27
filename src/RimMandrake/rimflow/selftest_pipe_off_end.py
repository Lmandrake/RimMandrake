#!/usr/bin/env python3
"""selftest_pipe_off_end.py: the promises of design/specs/2026-11-26-pipe-off-end/boundary.md (each t_ function is one
promise, by name). Offline: a temp control store, a temp concepts root, fake ledger items. Written before
pipe_off_end.py; seen failing on the base (the module absent, `pipe off` without --end).

    python3 src/RimMandrake/rimflow/selftest_pipe_off_end.py
"""
import json
import os
import re
import sys
import tempfile
from types import SimpleNamespace as NS

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils"), os.path.join(REPO, "src", "RimMandrake")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
NOW = 1_800_000_000.0


def fresh():
    d = tempfile.mkdtemp(prefix="poe_")
    os.environ["RM_CONTROL_DB"] = os.path.join(d, "control.db")
    import control as C
    C.init(os.environ["RM_CONTROL_DB"])
    return C, d


def E():
    import pipe_off_end
    return pipe_off_end


def concepts(mod, verdict):
    root = tempfile.mkdtemp(prefix="poe_concepts_")
    d = os.path.join(root, mod, "version", "in_game")
    os.makedirs(d)
    with open(os.path.join(d, "readiness_visit_3_20261120.md"), "w") as f:
        f.write("# readiness\n\nNOT READY. A BLOCKS ticket.\n")
    with open(os.path.join(d, "readiness_visit_12_20261124.md"), "w") as f:
        f.write("# readiness\n\n%s\n" % verdict)
    return root


def items(**states):
    return {k: NS(state=v) for k, v in states.items()}


def t_an_end_is_parsed_or_refused():
    e = E()
    assert e.parse("closed:RIMMANDRAKE_X_Y_Z") == {"kind": "closed", "item": "RIMMANDRAKE_X_Y_Z"}
    assert e.parse("ready:GimmeSomeSlack") == {"kind": "ready", "mod": "GimmeSomeSlack"}
    assert e.parse("cmd:true") == {"kind": "cmd", "cmd": "true"}
    for bad in ("", "soon", "closed:", "ready:", "cmd:"):
        try:
            e.parse(bad)
        except e.Refused as x:
            assert "closed:<ITEM>" in str(x), str(x)
        else:
            raise AssertionError("%r was accepted" % bad)
    C, _ = fresh()
    import argparse
    o = argparse.Namespace(target="item:B_ITEM", why="w", owner_said=None, per_ruling=None, idem=None, end="soon")
    try:
        C.cmd_switch(o, True)
    except Exception as x:      # noqa: BLE001
        assert "closed:<ITEM>" in str(x), str(x)
    else:
        raise AssertionError("a bad --end was written")
    assert not C.switches(), "a refused --end wrote a switch"
    o.end = "closed:A_ITEM"
    C.cmd_switch(o, True)
    row = C.switches()[0]
    assert json.loads(row["extra"])["end"] == {"kind": "closed", "item": "A_ITEM"}, dict(row)


def t_a_true_end_lifts_the_off():
    C, _ = fresh()
    C.switch("mod:GSS", True, "its readiness list is not READY", extra={"end": {"kind": "ready", "mod": "GSS"}})
    C.switch("item:B_ITEM", True, "until A closes", extra={"end": {"kind": "closed", "item": "A_ITEM"}})
    C.switch("stage:6", True, "no end given")
    root = concepts("GSS", "READY. No BLOCKS ticket is open on this path.")
    out = E().sweep(apply=True, now=NOW, root=root, items=items(A_ITEM="done"))
    lifted = sorted(r["scope"] for r in out if r.get("lifted"))
    assert lifted == ["item:B_ITEM", "mod:GSS"], out
    assert sorted(s["scope"] for s in C.switches()) == ["stage:6"], [dict(s) for s in C.switches()]
    r = [x for x in out if x["scope"] == "mod:GSS"][0]
    assert "undo: pipe off" in r["undo"] and "--end" in r["undo"], r
    acts = [a for a in C._q("SELECT * FROM acts WHERE kind='on'")]
    assert acts and all("program lift" in a["why"] for a in acts), [dict(a) for a in acts]
    dry = E().sweep(apply=False, now=NOW, root=root, items=items(A_ITEM="done"))
    assert not any(x.get("lifted") for x in dry)


def t_an_unread_end_lifts_nothing():
    C, _ = fresh()
    C.switch("mod:GSS", True, "x", extra={"end": {"kind": "ready", "mod": "GSS"}})
    C.switch("item:B", True, "x", extra={"end": {"kind": "closed", "item": "NOT_FILED"}})
    C.switch("item:C", True, "x", extra={"end": {"kind": "cmd", "cmd": "exit 2"}})
    C.switch("item:D", True, "x", extra={"end": {"kind": "closed", "item": "A"}})
    out = E().sweep(apply=True, now=NOW, root=tempfile.mkdtemp(), items=items(A="doing"))
    by = {r["scope"]: r for r in out}
    assert len(C.switches()) == 4, "an unread condition lifted an off"
    for s in ("mod:GSS", "item:B", "item:C"):
        assert by[s]["reading"].startswith("could not look"), by[s]
    assert by["item:D"]["reading"].startswith("false"), by["item:D"]
    C.switch("item:F", True, "x", extra=None)
    C._q  # the store stays readable
    bad = E().check(E()._end_of({"extra": "{not json"}))
    assert bad[0] is None and bad[1].startswith("could not look"), bad
    out = E().sweep(apply=True, now=NOW, root=tempfile.mkdtemp(), items=None)
    assert all(r["reading"].startswith("could not look") for r in out if r["end"] and r["end"]["kind"] == "closed")


def t_his_holds_are_never_touched():
    C, _ = fresh()
    C.switch("mod:GSS", True, "his hold: x", layer="owner", said="hold it", extra={"end": {"kind": "cmd", "cmd": "true"}})
    C.switch("mod:FW", True, "he ordered it", owner_said="switch FlowWorks off", extra={"end": {"kind": "cmd", "cmd": "true"}})
    out = E().sweep(apply=True, now=NOW, root=tempfile.mkdtemp(), items={})
    assert len(C.switches()) == 2 and not any(r.get("lifted") for r in out), out
    assert all("his" in r["reading"] for r in out), out


def t_every_off_shows_its_reason_age_and_end():
    C, _ = fresh()
    C.switch("mod:GSS", True, "readiness is not READY", now=NOW - 50 * 3600, extra={"end": {"kind": "ready", "mod": "GSS"}})
    C.switch("stage:6", True, "a broken stage", now=NOW - 3 * 3600)
    rows = E().rows(now=NOW, root=tempfile.mkdtemp(), items={})
    by = {r["scope"]: r for r in rows}
    assert by["mod:GSS"]["age"] == "2d" and by["mod:GSS"]["why"] == "readiness is not READY", by
    assert by["stage:6"]["end_text"] == "none set" and by["stage:6"]["age"] == "3h", by
    text = "\n".join(E().page_lines(rows))
    assert "mod:GSS" in text and "ready:GSS" in text and "none set" in text and "could not look" in text, text


def t_the_tick_and_the_page_read_it():
    """Wiring: the Maturation tick sweeps before it reads the holds; MATURATION_NOW prints the block."""
    src = open(os.path.join(HERE, "maturation_dispatch.py")).read()
    i, j = src.find("POE.safe_sweep(True, now)"), src.find("holds = OH.load()")
    assert 0 < i < j, "the tick does not sweep the end conditions before it reads the holds"
    import maturation_now as MN
    md = "\n".join(MN.offs_md({"offs": [{"scope": "mod:GSS", "why": "w", "age": "2d", "end_text": "ready:GSS",
                                         "reading": "false: x"}]}))
    assert "## Switched off (1)" in md and "ready:GSS" in md, md
    assert "could not look" in "\n".join(MN.offs_md({"offs": None}))
    assert "boom" in "\n".join(MN.offs_md({"offs": {"could_not_look": "boom"}}))


def t_each_limit_names_its_danger():
    src = open(os.path.join(HERE, "pipe_off_end.py")).read()
    m = re.search(r"^# budget: .*\n(?:# budget: .*\n)*CMD_DEADLINE_S = ", src, re.M)
    assert m and "danger=" in m.group(0), "CMD_DEADLINE_S has no danger line above it"


def main():
    failed = 0
    tests = [t_an_end_is_parsed_or_refused, t_a_true_end_lifts_the_off, t_an_unread_end_lifts_nothing,
             t_his_holds_are_never_touched, t_every_off_shows_its_reason_age_and_end, t_the_tick_and_the_page_read_it,
             t_each_limit_names_its_danger]
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001 - a promise whose test cannot run is a FAIL, never a crash
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, str(e)[:400]))
    print("FAILED %d of %d" % (failed, len(tests)) if failed else "ALL PASS (%d)" % len(tests))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
