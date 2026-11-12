#!/usr/bin/env python3
"""cathedral_offer_letters.py -- a gm_blackboard_shadow.py JSONL log, read the way the player would meet it.

CATHEDRAL_MISSION_BOON_OFFERS_1. Prints, in game-day order, every letter the Cathedral's favours would put in front
of the player had the blackboard not been in shadow mode: each request as its "Quest available" letter, the pack's
arrival once the request is accepted, the success letter when it ends well, and each gravtech gift. Lines in
[brackets] are what the player does NOT see (stage changes, a gift withheld for Heat, a request lapsing or
withdrawn), so the transcript can be checked against the rule that the player only ever reads the world, never the
mechanism. Text comes from the shipped defs, through the log's own would_fire entries.

    python3 cathedral_offer_letters.py <shadow_log.jsonl> [--out <file>]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gm_blackboard_shadow as G  # noqa: E402


def transcript(records, catalogue):
    missions = {m["quest_def"]: m for m in catalogue["missions"]}
    out, prev_boon_state, prev_stage, accepted = [], {}, None, set()

    def day(r):
        return "Day %5.2f" % ((r.get("ticksGame") or 0) / 60000.0)

    def letter(r, label, text, name=None):
        out.append("%s  LETTER  %s%s" % (day(r), label, ("  --  " + name) if name else ""))
        out.extend("            " + ln for ln in text.split("\n"))
        out.append("")

    for r in records:
        stage = r.get("conduct_posture_label")
        if stage != prev_stage:
            out.append("%s  [stage %s -> %s, Regard %.1f, Heat %.1f]" % (day(r), prev_stage, stage,
                                                                    r["cathedral_regard_after"], r["heat_after"]))
            prev_stage = stage
        for q in r.get("mission_quests", []):
            if q["state"] == "Ongoing" and q["id"] not in accepted:
                accepted.add(q["id"])
                m = missions[q["quest_def"]]
                out.append("%s  [the player accepts quest %s]" % (day(r), q["id"]))
                letter(r, m["arrival_letter"]["label"], m["arrival_letter"]["text"])
        for e in r["would_fire"]:
            t = e["type"]
            if t == "cathedral_mission_offer":
                letter(r, e["letter"]["label"], e["letter"]["text"], e["letter"]["quest_name"])
            elif t == "cathedral_mission_completed":
                m = missions[e["quest_def"]]
                letter(r, m["success_letter"]["label"], m["success_letter"]["text"])
                out.append("%s  [Regard +%.1f this poll from the completion; Heat %.2f]" % (
                    day(r), r["mission_completion_regard_gain_this_poll"], r["heat_after"]))
            elif t == "cathedral_boon_offer":
                letter(r, e["letter"]["label"], e["letter"]["text"])
                out.append("%s  [gift: %s; Heat %.1f, ceiling %.0f]" % (day(r), e["gifts"], e["heat_at_offer"],
                                                                     e["heat_ceiling"]))
            elif t in ("cathedral_mission_offer_lapsed", "cathedral_mission_offer_withdrawn"):
                out.append("%s  [%s: %s%s -- no letter]" % (day(r), t.replace("cathedral_", ""), e["quest_def"],
                                                           (" (%s)" % e["reason"]) if e.get("reason") else ""))
            elif t == "cathedral_mission_resolved" and "EndedFailed" in e["detail"]:
                out.append("%s  [quest %s failed: no Regard]" % (day(r), e["quest_id"]))
            elif t == "cathedral_mission_resolved" and "EndedOfferExpired" in e["detail"]:
                out.append("%s  [quest %s lapsed unanswered -- no letter]" % (day(r), e["quest_id"]))
            elif t == "cathedral_go_dark":
                out.append("%s  [GO-DARK: favours closed, held shut until tick %s]" % (
                    day(r), r["cathedral_offers"].get("dark_hold_until_tick")))
        for b in r["cathedral_offers"]["boons"]:
            was = prev_boon_state.get(b["incident_def"])
            if was is not None and was != b["state"] and "withheld_heat" in (was, b["state"]):
                out.append("%s  [%s: %s -> %s at Heat %.1f]" % (day(r), b["incident_def"], was, b["state"],
                                                               r["heat_after"]))
            prev_boon_state[b["incident_def"]] = b["state"]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("log")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    with open(a.log, encoding="utf-8") as f:
        records = [json.loads(ln) for ln in f if ln.strip()]
    lines = transcript(records, G.load_cathedral_offer_catalogue())
    text = "\n".join(lines) + "\n"
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
        print("cathedral_offer_letters: %d lines -> %s" % (len(lines), a.out))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
