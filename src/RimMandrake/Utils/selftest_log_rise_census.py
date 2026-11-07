#!/usr/bin/env python3
"""Selftest of log_rise_census.py: a synthetic session whose true sources are known, and each way the join can lie."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import log_rise_census as lrc

MCR = "[MCR][MoodChain] Pat: Scan finished. NewlyAddedMemories=0"
LOV = "IntimacyGiver_Sex: Pat cannot currently do lovin'"
ERR = "Could not load reference to Verse.ThingDef named Gone"
PLAIN = "Some mod says hello"
UNITY = "Unloading 3 unused Assets to reduce memory usage."
fails = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ((": " + str(detail)) if detail and not cond else ""))
    if not cond:
        fails.append(name)


def ctx(sec, count, err=0, warn=0):
    return {"kind": "context", "utc": "2026-11-06T20:%02d:%02d.000Z" % (sec // 60, sec % 60), "logMsgs": count,
            "logErr": err, "logWarn": warn}


def fixture(d, lines, rows):
    log = os.path.join(d, "Player.log")
    with open(log, "w", newline="\n") as f:
        f.write("\r\n".join(lines) + "\r\n")     # the game writes CRLF: the startswith and regex reads must survive it
    with open(os.path.join(d, "tps_x_abcd_0_000.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return log


def capped_session():
    """Cold load, then a Log.Clear; 0-4000 Mood Chain, 4000-6000 mixed, 6000-10000 plain, then the cap; a rise of each."""
    lines = [UNITY] * 50 + [PLAIN] * 10000 + [lrc.CAP_LINE + ". Stopping logging to avoid spam."]
    lines += [MCR] * 4000 + [UNITY] * 7 + [MCR, LOV] * 1000 + [PLAIN] * 4000
    lines += [lrc.CAP_LINE + ". Stopping logging to avoid spam."] + [PLAIN] * 5
    rows = [ctx(0, 100), ctx(60, 10000, warn=9900), ctx(120, 1, warn=9900), ctx(180, 4000, warn=9900),
            ctx(240, 6000, warn=9900), ctx(300, 10000)]
    rows[5]["logWarn"] = 13900
    return lines, rows


def main():
    with tempfile.TemporaryDirectory() as d:
        lines, rows = capped_session()
        log = fixture(d, lines, rows)
        code, out = lrc.run(log, d, "abcd")
        check("a session of known sources passes", code == lrc.PASS, out)
        crlf = [x.rstrip("\r") for x in open(log, errors="replace", newline="\n").read().split("\n")]
        rises, problems = lrc.analyse(crlf, *lrc.read_rows(d, "abcd"))
        check("no alignment problem", not problems, problems)
        by = {(r["before"], r["after"]): r for r in rises}
        spam = by[(1, 4000)]
        check("the Mood Chain rise is that source and nothing else",
              spam["verdict"] == "SPAM" and spam["census"][lrc.MOODCHAIN] == 3999 and spam["after_spam"] == 0, spam)
        mix = by[(4000, 6000)]
        check("a mixed rise counts both sources",
              mix["census"][lrc.MOODCHAIN] == 1000 and mix["census"][lrc.INTIMACY] == 1000, mix)
        check("Unity's own lines never count as messages", lrc.source_of(UNITY) not in mix["census"], mix["census"])
        check("the plain rise is not called spam", by[(6000, 10000)]["spam"] == 0)
        check("a plain rise the record's warnings explain is ERRORS", by[(6000, 10000)]["verdict"] == "ERRORS")

    with tempfile.TemporaryDirectory() as d:
        lines, rows = capped_session()
        rows[5]["logWarn"] = 9900
        code, out = lrc.run(fixture(d, lines, rows), d, "abcd")
        check("a rise no source explains fails", code == lrc.FAIL and any("explained by no source" in x for x in out), out)

    with tempfile.TemporaryDirectory() as d:
        lines, rows = capped_session()
        lines = lines[:-6] + lines[-5:]      # the second cap line gone: record and log disagree about the caps
        code, out = lrc.run(fixture(d, lines, rows), d, "abcd")
        check("a cap line missing is UNMEASURED, never a guess", code == lrc.UNMEASURED and "cap lines" in out[-2], out)

    with tempfile.TemporaryDirectory() as d:
        lines, rows = capped_session()
        at = len(lines) - 6
        lines = lines[:at - 500] + lines[at:]    # 500 messages short: the walk misses 10000 by more than 1%
        code, out = lrc.run(fixture(d, lines, rows), d, "abcd")
        check("a walk that misses the cap is UNMEASURED", code == lrc.UNMEASURED and "walks to" in out[-2], out)

    with tempfile.TemporaryDirectory() as d:
        lines = [lrc.LOAD_LINE % "Saved" + "with mods:"] + [ERR] * 1100 + [PLAIN] * 5
        rows = [ctx(0, 10), ctx(60, 1110, err=1100)]
        games = {"kind": "game", "utc": "2026-11-06T20:00:30.000Z", "save": "Saved"}
        code, out = lrc.run(fixture(d, lines, rows + [games]), d, "abcd")
        check("a load inside an uncapped rise anchors it and errors explain it", code == lrc.PASS, out)
        check("that rise is ERRORS with its census", any("ERRORS" in x and "anchor load" in x for x in out)
              and any(lrc.SAVE_LOAD in x for x in out), out)

    with tempfile.TemporaryDirectory() as d:
        lines = [MCR] * 1200
        rows = [ctx(0, 10), ctx(60, 1110)]
        code, out = lrc.run(fixture(d, lines, rows), d, "abcd")
        check("an uncapped rise with no load and no errors is UNMEASURED", code == lrc.UNMEASURED and "no line anchor" in " ".join(out), out)

    with tempfile.TemporaryDirectory() as d:
        code, out = lrc.run(fixture(d, [PLAIN] * 100, [ctx(0, 10), ctx(60, 100)]), d, "abcd")
        check("no big rise is UNMEASURED, not a clean pass", code == lrc.UNMEASURED and "no scan-to-scan" in out[-2], out)
        code, out = lrc.run(os.path.join(d, "absent.log"), d, "abcd")
        check("a missing log is UNMEASURED", code == lrc.UNMEASURED, out)
        code, out = lrc.run(os.path.join(d, "Player.log"), d, "nosuchsession")
        check("a missing record is UNMEASURED", code == lrc.UNMEASURED, out)

    with tempfile.TemporaryDirectory() as d:
        # a rise spam-dominated by half yet still at the queue size without it: the fix would not have helped
        lines2 = [UNITY] * 50 + [PLAIN] * 10000 + [lrc.CAP_LINE] + [MCR] * 4000 + [MCR] * 1500 + [PLAIN] * 1500 + [PLAIN] * 3000 + [lrc.CAP_LINE]
        rows2 = [ctx(0, 100), ctx(60, 10000, warn=9900), ctx(120, 1, warn=9900), ctx(180, 4000, warn=9900),
                 ctx(240, 7000, warn=9900), ctx(300, 10000, warn=12900)]
        code, out = lrc.run(fixture(d, lines2, rows2), d, "abcd")
        check("a spam rise still at the queue size without the spam fails", code == lrc.FAIL and any("stays at" in x for x in out), out)
        check("the replay says where the epoch would have stopped", any("without the spam it reaches 4501" in x for x in out), out)

    print("%d failed" % len(fails) if fails else "ALL PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
