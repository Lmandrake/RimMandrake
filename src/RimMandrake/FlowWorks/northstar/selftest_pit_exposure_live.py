#!/usr/bin/env python3
"""Offline test of pit_exposure_live.py's judges (PIT_TEMPERATURE_SOFTENING_1): no bridge, no game. The samples are the
shapes the live runs of 2026-11-11 wrote: run 4 (all three rows PASS) and run 2 (the open-pit prisoner walked out of an
unevenly dug pit at 10:30: A3 must read SITE, never PASS)."""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pit_exposure_live as L  # noqa: E402


def sample(h, out, ta, tb, tc, ra, rb, rc, hurt_a):
    def p(r, hurt, t, outdoor, exposed):
        return {"resistance": "%.3f" % r, "hurting": str(hurt), "ambient": "%.2f" % t, "safeMax": "38.0", "prisoner": "True",
                "heatstroke": "0.010", "outdoorRoom": str(outdoor), "exposed": str(exposed), "hour": "%.2f" % h}
    return {"hour": h, "out": out, "TA": ta, "TB": tb, "TC": tc, "depthA": [8, 8], "depthB": [8, 8],
            "PA": p(ra, hurt_a, ta, True, True), "PB": p(rb, False, tb, False, False), "PC": p(rc, False, tc, False, False)}


HOT = ["EnvironmentHot", -8.0, "Hot"]


def base():
    s = [sample(6.0 + k, 36.7 + k, 36.68 + k, 40.0 + 0.1 * k, 37.2 + 0.9 * k, 12.0 - 0.5 * k, 14.0, 12.0, True)
         for k in range(10)]
    return {"args": {"from_hour": 6.0}, "samples": s, "prisoners": {"PA": "a", "PB": "b", "PC": "c"},
            "colonists": {"ids": ["k", "p", "h"], "psychopath": "p", "psycho_trait": True, "charity": {"Kind": ["Charity_Important"], "Hard": []},
                          "ideos": {"k": "Kind", "p": "Kind", "h": "Hard"}},
            "noon_thoughts": {"k": [["RM_ExposedPrisoner", -3.0, "Prisoner left exposed in a pit"], HOT],
                              "p": [HOT], "h": [HOT]}}


def judge(res):
    got = {}
    L.verdicts(res, lambda rid, st, cls, det: got.__setitem__(rid, (st, cls)))
    return got


def main():
    fails, count = [], [0]

    def check(ok, msg):
        count[0] += 1
        if not ok:
            fails.append(msg)

    g = judge(base())
    check(g["PEX_A2_open_pit_tracks_noon"][0] == "PASS", "run-4 shape: the open pit tracks, the twin trails -> A2 PASS")
    check(g["PEX_A3_pit_wears_resistance"][0] == "PASS", "run-4 shape: only the pit prisoner loses resistance -> A3 PASS")
    check(g["PEX_A4_compassion_not_psycho"][0] == "PASS", "run-4 shape: kind yes, psychopath no, hard ideo no -> A4 PASS")

    r = base()   # a twin that tracks outdoors as closely as the open pit: nothing moves faster
    for s in r["samples"]:
        s["TB"] = s["out"] + 0.05
    check(judge(r)["PEX_A2_open_pit_tracks_noon"][0] == "FAIL", "a roofed twin that tracks too is an A2 FAIL")
    r = base()   # the open pit lagging outdoors: not 'outdoor temperature'
    r["samples"][5]["TA"] = r["samples"][5]["out"] - 3.0
    check(judge(r)["PEX_A2_open_pit_tracks_noon"][0] == "FAIL", "an open pit 3 C off outdoors is an A2 FAIL")
    r = base()
    r["samples"] = [s for s in r["samples"] if s["hour"] != 12.0]
    check(judge(r)["PEX_A2_open_pit_tracks_noon"][0] == "UNMEASURED", "no 12:00 sample is UNMEASURED, never PASS")

    r = base()   # review 2026-11-11: pit A never dug (the drive refused): flat ground also tracks outdoors
    for x in r["samples"]:
        x["depthA"] = None
    check(judge(r)["PEX_A2_open_pit_tracks_noon"] == ("UNMEASURED", "SITE"), "an undug pit A is UNMEASURED SITE")
    r = base()   # run 3: the pit got shallower under the prisoner
    r["samples"][4]["depthA"] = [3, 8]
    check(judge(r)["PEX_A2_open_pit_tracks_noon"][0] == "UNMEASURED", "a pit not full depth all day is UNMEASURED")
    r = base()
    r["samples"][6]["PB"]["outdoorRoom"] = "True"
    check(judge(r)["PEX_A2_open_pit_tracks_noon"][0] == "UNMEASURED", "a 'roofed' twin reading outdoors is UNMEASURED")
    r = base()   # run 8: rain filled the open pit
    r["samples"][3]["fillA"] = 5
    check(judge(r)["PEX_A2_open_pit_tracks_noon"][0] == "UNMEASURED", "a flooded open pit is UNMEASURED")
    r = base()   # the normal cell's prisoner loses as much: the pit is not what wore it down
    for k, s in enumerate(r["samples"]):
        s["PC"]["resistance"] = "%.3f" % (12.0 - 0.5 * k)
    check(judge(r)["PEX_A3_pit_wears_resistance"][0] == "FAIL", "a cell prisoner losing as much is an A3 FAIL")
    r = base()   # nothing hurt: a loss with no heat is not this mechanism
    for s in r["samples"]:
        s["PA"]["hurting"] = "False"
    check(judge(r)["PEX_A3_pit_wears_resistance"][0] == "FAIL", "a pit prisoner never hurting is an A3 FAIL")
    r = base()   # run 2: PA walked out at 10:30 and off the map
    r["lost"] = {"PA": {"hour": 14.0}}
    for s in r["samples"][8:]:
        s["PA"] = {"raw": "REFUSED: no spawned pawn a"}
    check(judge(r)["PEX_A3_pit_wears_resistance"] == ("UNMEASURED", "SITE"), "a lost prisoner is UNMEASURED SITE")

    r = base()
    r["noon_thoughts"]["p"] = [["RM_ExposedPrisoner", -3.0, "x"]]
    check(judge(r)["PEX_A4_compassion_not_psycho"][0] == "FAIL", "a psychopath with the thought is an A4 FAIL")
    r = base()
    r["noon_thoughts"]["h"] = [["RM_ExposedPrisoner", -3.0, "x"]]
    check(judge(r)["PEX_A4_compassion_not_psycho"][0] == "FAIL", "a hard-morality colonist with the thought is an A4 FAIL")
    r = base()
    r["noon_thoughts"]["k"] = [HOT]
    check(judge(r)["PEX_A4_compassion_not_psycho"][0] == "FAIL", "a compassionate colonist without it is an A4 FAIL")
    r = base()
    r["colonists"]["charity"] = {"Kind": [], "Hard": []}
    r["noon_thoughts"]["k"] = [HOT]
    check(judge(r)["PEX_A4_compassion_not_psycho"][0] != "PASS", "no compassionate colonist at all is never a PASS")
    r = base()   # review 2026-11-11: PA recruited/released before the end reads resistance -1
    r["samples"][-1]["PA"]["resistance"], r["samples"][-1]["PA"]["prisoner"] = "-1.000", "False"
    check(judge(r)["PEX_A3_pit_wears_resistance"][0] == "UNMEASURED", "a prisoner no longer a prisoner is UNMEASURED")
    r = base()   # review 2026-11-11: a failed thought read for the psychopath is not 'no thought'
    r["noon_thoughts"]["p"] = []
    check(judge(r)["PEX_A4_compassion_not_psycho"][0] == "UNMEASURED", "an empty thought read is UNMEASURED")
    r = base()   # no compassionate colonist: the kind one moved to the hard ideo
    r["colonists"]["ideos"]["k"] = "Hard"
    check(judge(r)["PEX_A4_compassion_not_psycho"][0] == "FAIL", "no compassionate colonist is a FAIL")
    r = base()   # run 6: the 'psychopath' was a pawn of no ideoligion: his missing thought proves nothing
    r["colonists"]["ideos"]["p"] = None
    check(judge(r)["PEX_A4_compassion_not_psycho"][0] == "UNMEASURED", "a psychopath outside a Charity ideo is UNMEASURED")
    r = base()
    r["colonists"]["psycho_trait"] = False
    check(judge(r)["PEX_A4_compassion_not_psycho"][0] == "UNMEASURED", "a trait that did not take is UNMEASURED")
    r = copy.deepcopy(base())
    r.pop("noon_thoughts")
    check(judge(r)["PEX_A4_compassion_not_psycho"][0] == "UNMEASURED", "no thought read is UNMEASURED")

    r = base()   # review 2026-11-12: a blank outdoor read mid-day used to drop out of the lag test (or crash max([]))
    r["samples"][3]["out"] = None
    check(judge(r)["PEX_A2_open_pit_tracks_noon"][0] == "UNMEASURED", "a sample with no outdoor read is A2 UNMEASURED")
    r = base()   # review 2026-11-12: a failed step leaves the labels on the wrong game hours
    r["samples"][5]["PA"]["hour"] = "13.00"
    check(judge(r)["PEX_A2_open_pit_tracks_noon"][0] == "UNMEASURED", "a sample off the game clock is A2 UNMEASURED")
    r = base()   # the real runs read the game hour 0.23 h behind the label (a whole-hour zone): a fixed offset is fine
    for s in r["samples"]:
        s["PA"]["hour"] = "%.2f" % (s["hour"] - 0.23)
    check(judge(r)["PEX_A2_open_pit_tracks_noon"][0] == "PASS", "a fixed zone offset between label and game hour still passes")

    r = base(); r["args"]["interaction"] = "ReduceResistance"
    for sm in r["samples"]:
        for n in ("PA", "PB", "PC"):
            sm[n]["chatsToday"] = "2"
    check(judge(r)["PEX_A3_pit_wears_resistance"][0] == "PASS", "wardened (ReduceResistance), chats to all: the pit still wins -> PASS")
    for sm in r["samples"]:
        sm["PC"]["chatsToday"] = "0"
    check(judge(r)["PEX_A3_pit_wears_resistance"] == ("UNMEASURED", "HARNESS"),
          "wardened, but no warden ever chatted with the cell prisoner: UNMEASURED, never PASS")
    r = base()
    check(judge(r)["PEX_A3_pit_wears_resistance"][0] == "PASS", "no interaction set (older runs): no chat read is needed")
    r = base(); r["placed"] = {"PA": {"resistance": "12.000"}, "PB": {"resistance": "15.000"}, "PC": {"resistance": "17.000"}}
    check(judge(r)["PEX_A3_pit_wears_resistance"][0] == "FAIL",
          "a cell prisoner chatted down 5 before the first sample counts: the pit no longer wins -> FAIL")
    check(L.kv("REFUSED: no spawned pawn x") == {"raw": "REFUSED: no spawned pawn x"}, "a refusal parses to raw, no fields")
    check(L.kv("EXPOSURE exposed=True resistance=4.500")["resistance"] == "4.500", "kv reads the proof line")
    check(L.tick_for(22, 0.0, 0.0) == 22 * 60000, "local midnight at longitude 0")
    check(L.tick_for(22, 6.0, 15.0) == 22 * 60000 + 5 * 2500, "longitude 15 E is one hour ahead")
    check(L.tick_for(22, 6.0, 11.47) == 22 * 60000 + 5 * 2500, "a fractional zone rounds to a whole hour (TimeZoneAt)")
    n = count[0]
    for f in fails:
        print("FAIL", f)
    print("%s %d/%d" % ("PASS" if not fails else "FAIL", n - len(fails), n))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
