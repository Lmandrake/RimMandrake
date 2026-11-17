#!/usr/bin/env python3
"""The proof rows the owner's ruling of 2026-11-16 changed ("simply not show sparking ends that are inside walls"; "Rock and wall should
act the same"): RIMMANDRAKE_RETIRE_SLACK_ROWS_WANTING_SPARKING_WALL_ENDS.

  M1_node_census                         asked for a live wall terminal; now refuses one (planted below)
  B4d_spark_budget_shared_visible_first  asked for three live ends, the third being the scene's wall end; two tell the same thing
  B4_downed_wire_bursts                  retired with the feature it read (a live wire hanging out of a wall), its setting and its code

    python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_wall_end_rows.py      # exit 0 = every check passes
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(MOD, "..", "Utils"))
import validation  # noqa: E402


def main():
    fails = []

    def check(ok, msg):
        print(("ok   " if ok else "FAIL ") + msg)
        if not ok:
            fails.append(msg)

    nt = {"battery": 1, "consumer": 1, "junction": 2, "stub_wall": 1, "terminal": 2, "hidden_end": 1}
    floor = [{"wall": False, "netLive": True}, {"wall": False, "netLive": False}]
    check(validation.node_census_verdict(nt, floor)[0] == "PASS", "the scene as the mod draws it today passes: no end on a wall")
    check(validation.node_census_verdict(nt, floor + [{"wall": True, "netLive": True}])[0] == "FAIL", "planted: a live (sparking) wall end is refused")
    check(validation.node_census_verdict(nt, floor + [{"wall": True, "netLive": False}])[0] == "PASS", "a dead end on a wall is not this row's (the end-kind rule has it)")
    check(validation.node_census_verdict(dict(nt, terminal=1), floor)[0] == "FAIL", "planted: one far run end only is refused")
    check(validation.node_census_verdict({k: v for k, v in nt.items() if k != "junction"}, floor)[0] == "FAIL", "planted: no junction is refused")

    def bud(all_, stub_on, stub_set, stub_set_on, scene_on, scene_set, scene_set_on, cap_set):
        return {"stub": {"liveEndsAll": all_, "liveEndsOnScreen": stub_on, "sparkSet": stub_set, "sparkSetOnScreen": stub_set_on},
                "scene": {"liveEndsAll": all_, "liveEndsOnScreen": scene_on, "sparkSet": scene_set, "sparkSetOnScreen": scene_set_on},
                "cap24": {"liveEndsAll": all_, "sparkSet": cap_set}}
    check(validation.spark_budget_verdict(bud(2, 1, 1, 1, 1, 1, 1, 2)), "two live ends, the one on screen sparking in each frame, both at cap 24: passes")
    check(validation.spark_budget_verdict(bud(3, 1, 1, 1, 1, 1, 1, 3)), "three live ends pass as before")
    check(not validation.spark_budget_verdict(bud(2, 1, 1, 0, 1, 1, 1, 2)), "planted: the sparking end is the one off screen: refused")
    check(not validation.spark_budget_verdict(bud(2, 1, 2, 1, 1, 1, 1, 2)), "planted: two ends spark with the cap at 1: refused")
    check(not validation.spark_budget_verdict(bud(1, 1, 1, 1, 1, 1, 1, 1)), "planted: one live end in all cannot tell which is chosen: refused")
    check(not validation.spark_budget_verdict(bud(2, 1, 1, 1, 1, 1, 1, 1)), "planted: at cap 24 one of two live ends does not spark: refused")
    src = open(os.path.join(MOD, "validation.py"), encoding="utf-8").read()
    check('row(rows, "B4_downed_wire_bursts"' not in src, "the downed-wire row is gone from the script")
    cs = "".join(open(os.path.join(MOD, "Source", f), encoding="utf-8").read() for f in ("GimmeSomeSlackMod.cs", "RM_MapComponent_CordGraph.cs"))
    check("downedWire" not in cs and "DownedWireSchedule" not in cs, "the setting and its schedule are gone from the mod")
    print("PASS" if not fails else "FAIL: %d" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
