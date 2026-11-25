#!/usr/bin/env python3
"""selftest_scene_accept_ledger: a judged scene.py accept run appends its run line to scene_runs.jsonl, copied from its
receipt (scene_judge.ledger_append; Bridge v2 decision 12). No game; every file is in a temp root.

    python3 selftest_scene_accept_ledger.py"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RIMFLOW = HERE.parent / "rimflow"
for p in (str(HERE), str(RIMFLOW)):
    sys.path.insert(0, p)
import scene_judge as J  # noqa: E402
import scene_verdicts as SV  # noqa: E402
import selftest_scene_judge as T  # noqa: E402

MOD = "WMod"
MARKS = {"overlay": "none", "tainted": False, "arm": "reference", "build_kind": "RELEASE", "map_kind": "settlement"}


def kept(root, marks=None, mode="accept", script="design/concepts/WMod/version/s1.py"):
    folder = Path(tempfile.mkdtemp(dir=root))
    data = T.fixture()
    data[2][0].update(marks or {})
    T.keep(folder, data)
    run = json.loads((folder / "run.json").read_text())
    run.update(mode=mode, script=script)
    (folder / "run.json").write_text(json.dumps(run))
    return folder, data


def ledger(root):
    return SV.read(root, MOD)[0]


def t_success_adds_one_line_with_every_mark():
    with tempfile.TemporaryDirectory() as root:
        folder, _ = kept(root, MARKS)
        assert J.judge(folder, ledger_root=root).outcome == "SUCCESS"
        J.judge(folder, ledger_root=root)       # a second plain judge reads the kept verdict: no second line
        lines = ledger(root)
        assert len(lines) == 1 and lines[0]["rec"] == "run" and lines[0]["outcome"] == "SUCCESS", lines
        for k, v in MARKS.items():
            assert lines[0][k] == v, (k, lines[0])
        assert SV.bar_refusal(lines[0]) is None, SV.bar_refusal(lines[0])


def t_receipt_without_a_mark_reads_not_counted():
    with tempfile.TemporaryDirectory() as root:
        folder, _ = kept(root)
        J.judge(folder, ledger_root=root)
        lines = ledger(root)
        assert len(lines) == 1 and "overlay" not in lines[0]
        assert SV.bar_refusal(lines[0]).startswith("NOT COUNTED"), SV.bar_refusal(lines[0])
        for drop in MARKS:
            f2, _ = kept(root, {k: v for k, v in MARKS.items() if k != drop})
            J.judge(f2, ledger_root=root)
            last = ledger(root)[-1]
            assert drop not in last and SV.bar_refusal(last) is not None, (drop, last)


def t_rejudge_adds_a_class_line_never_a_second_run_line():
    with tempfile.TemporaryDirectory() as root:
        folder, data = kept(root, MARKS)
        J.judge(folder, ledger_root=root)
        plan = data[0]
        plan.update(success=T.cmp("job", "==", "Rescue"), version="changed")
        T.write(folder / "contract.json", plan)
        assert J.judge(folder, rejudge=True, ledger_root=root).outcome == "MOD FAILURE"
        lines = ledger(root)
        assert [x["rec"] for x in lines] == ["run", "class"], lines
        assert lines[1]["how"] == "rejudged" and lines[1]["outcome"] == "MOD FAILURE" and lines[1]["run"] == lines[0]["run"]


def t_explore_run_adds_nothing():
    with tempfile.TemporaryDirectory() as root:
        for mode, script in (("explore", None), ("accept", "elsewhere/s1.py")):
            folder, _ = kept(root, MARKS, mode=mode, script=script)
            J.judge(folder, ledger_root=root)
        assert not os.path.exists(SV.path(root, MOD)), "a ledger was written"


def main():
    names = [n for n in sorted(globals()) if n.startswith("t_")]
    bad = 0
    for n in names:
        try:
            globals()[n]()
            print("PASS", n)
        except Exception as e:  # noqa: BLE001
            bad += 1
            print("FAIL", n, repr(e))
    print("RESULT %d/%d passed" % (len(names) - bad, len(names)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
