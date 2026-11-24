#!/usr/bin/env python3
"""An aftermath station of a walk save has a START twin (owner, 2026-11-23; page design/specs/2026-11-24-walk-save-start-twin/
boundary.md). Offline: planted saves in a temp root, no game."""
import contextlib
import html
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.join(HERE, "..", "Utils")):
    sys.path.insert(0, os.path.abspath(p))
import selftest_wrong_check_fixed_in_sitting as S  # noqa: E402  its temp roots, rows and stubbed build match
import walk_twins as WT  # noqa: E402
from modcheck import reviewmap as RM  # noqa: E402

M, MOD = S.M, S.MOD
BAD, N = [], [0]


def check(ok, name):
    N[0] += 1
    if not ok:
        BAD.append(name)
    print("%s  %s" % ("ok   " if ok else "FAIL ", name))


# as on EK_VISIT4_WALK_20261123, which he could not judge
OLD = [RM.sign_book(12, 9, "01", "calibration PASS", look="the colonist thrown 3 cells", do="read its health", more="visit 4 proof verdict PASS"),
       RM.sign_book(207, 9, "14", "storeroom_bomb_pit PASS", look="goods in the pit", more="visit 4 proof verdict PASS")]
# as on EK_VISIT6_WALK_20261124_C, its rebuild
AFTER = RM.sign_book(12, 9, "01", "calibration AFTER", look="thrown > three cells", do="compare", more="proof verdict PASS")
START = RM.sign_book(12, 39, "01", "calibration START", look="as it stood before the blast")
ACT = RM.sign_book(50, 9, "3", "GROUND CORDS: MODERN", do="flick the switch")


def rws(ops):
    """A save with each sign as a book, its fields in the order the game writes them, other things between."""
    out = ['<?xml version="1.0"?>\n<savegame><meta/><things><thing Class="Building"><def>Wall</def><pos>(1, 0, 1)</pos></thing>']
    for o in ops:
        x, z, title, body = o.split("|", 3)
        t, b = html.escape(title, quote=False), html.escape(body.replace(RM.SIGN_BREAK, "\n"), quote=False)
        out.append('<thing Class="Book"><def>RM_StationSign</def><map>0</map><pos>(%s, 0, %s)</pos><title>%s</title>'
                   '<descriptionFlavor>%s</descriptionFlavor></thing><thing Class="Pawn"><pos>(9, 0, 9)</pos></thing>' % (x, z, t, b))
    return "\n".join(out) + "</things></savegame>"


def put_save(ops, name="w"):
    p = os.path.join(tempfile.mkdtemp(dir=S.TMP), name + ".rws")
    with open(p, "w", encoding="utf-8") as f:
        f.write(rws(ops))
    return p


def run(*a):
    with contextlib.redirect_stdout(io.StringIO()) as o, contextlib.redirect_stderr(io.StringIO()):
        rc = WT.main(list(a))
    return rc, o.getvalue()


def t_an_aftermath_with_no_twin_is_refused():
    w = WT.why(WT.of_ops([AFTER, ACT])) or ""
    check("01 calibration" in w and "1 aftermath" in w and "START" in w and "GROUND" not in w, "an-aftermath-with-no-twin-is-refused (%s)" % w[:80])
    check(run("check", put_save([AFTER]))[0] == 1, "...and check exits 1")


def t_an_aftermath_with_its_twin_passes():
    check(WT.why(WT.of_ops([AFTER, START])) is None and run("check", put_save([AFTER, START]))[0] == 0, "an-aftermath-with-its-twin-passes")


def t_a_finished_scene_is_an_aftermath_without_the_tag():
    w = WT.why(WT.of_ops(OLD)) or ""
    check("2 aftermath" in w and "14 storeroom_bomb_pit" in w, "a-finished-scene-is-an-aftermath-without-the-tag (%s)" % w[:120])


def t_a_station_he_acts_on_needs_no_twin():
    check(WT.why(WT.of_ops([ACT])) is None, "a-station-he-acts-on-needs-no-twin")


def t_a_twin_of_another_station_does_not_count():
    for what, twin in (("another name", RM.sign_book(12, 39, "01", "wall_stop START")), ("another key", RM.sign_book(12, 39, "02", "calibration START")),
                       ("the same cell", RM.sign_book(12, 9, "01", "calibration START")),
                       ("START not as the tag", RM.sign_book(12, 39, "01", "START calibration"))):
        check(bool(WT.why(WT.of_ops([AFTER, twin]))), "a-twin-of-another-station-does-not-count: %s" % what)


def t_the_save_itself_is_read():
    ops = [AFTER, START, ACT] + OLD
    check(WT.of_save(put_save(ops)) == WT.of_ops(ops) and len(WT.of_ops(ops)) == 5, "the-save-itself-is-read")
    check(WT.of_ops(["1|2|a label|x", "", "# map ?"]) == [] and WT.of_ops(None) == [], "...and a line that is no sign book is no station")


class FakeB:
    def __init__(self, saves, name):
        self.saves, self.name, self.calls = saves, name, []

    def call(self, tool, **kw):
        self.calls.append(tool)
        self.saves[self.name + ".rws"] = (1, 1)
        return {"success": True}


def keep(signs):
    saves, d = {}, tempfile.mkdtemp(dir=S.TMP)
    b = FakeB(saves, "K")
    return RM.save_keeper(b, "K", saves=os.path.join(d, "Saves"), stat=lambda _: dict(saves), sleep=lambda s: None, wait_s=0, signs=signs), b


def t_save_keeper_refuses_before_the_save():
    r, b = keep([AFTER])
    check(not r["ok"] and "start-state twin" in (r.get("refused") or "") and not b.calls, "save-keeper-refuses-before-the-save (%s)" % r)
    for signs in ([AFTER, START], [ACT], None, "1|2|a label|sub|#fff|medium|t"):
        r, b = keep(signs)
        check(r["ok"] and b.calls == ["rimworld/save_game"], "...and a save with nothing lacking is made: %s" % str(signs)[:40])


def exit_of(ops, name):
    root = S.visit(name, S.ALL_PASS)
    with open(os.path.join(root, "saves", "w.rws"), "w", encoding="utf-8") as f:
        f.write(rws(ops))
    return M.read_ingame_exit(root, MOD, 1)


def t_the_exit_refuses_it():
    ex = exit_of(OLD, "twins_old")
    check(ex["state"] == "not_met" and any("start-state twin" in w for w in ex["why"]), "the-exit-refuses-it (%s)" % ex["why"])
    for ops, what in (([AFTER, START], "twins"), ([ACT], "no aftermath"), ([], "no sign")):
        ex = exit_of(ops, "twins_ok")
        check(ex["state"] == "met", "...and is met with %s (%s)" % (what, ex["state"] if ex["state"] == "met" else ex["why"]))


def t_a_save_that_cannot_be_read_is_said():
    p = os.path.join(S.TMP, "empty.rws")
    open(p, "w").close()
    for q in (p, os.path.join(S.TMP, "absent.rws")):
        check("could not be read" in (WT.save_why(q) or ""), "a-save-that-cannot-be-read-is-said: %s" % os.path.basename(q))


def t_could_not_look_exits_two():
    for q in (os.path.join(S.TMP, "absent.rws"), put_save([])):
        rc, out = run("check", q)
        check(rc == 2 and out.startswith("COULD NOT LOOK"), "could-not-look-exits-two (%s: %s)" % (rc, out[:60]))


def t_the_driver_brief_says_the_rule():
    root = S.visit("twins_brief", S.ALL_PASS)
    r = M.ingame_brief_text(root, MOD)
    txt = r[0] if isinstance(r, tuple) else r
    check("START twin beside it" in txt and "walk_twins.py check" in txt, "the-driver-brief-says-the-rule")


def main():
    for t in (t_an_aftermath_with_no_twin_is_refused, t_an_aftermath_with_its_twin_passes,
              t_a_finished_scene_is_an_aftermath_without_the_tag, t_a_station_he_acts_on_needs_no_twin,
              t_a_twin_of_another_station_does_not_count, t_the_save_itself_is_read, t_save_keeper_refuses_before_the_save,
              t_the_exit_refuses_it, t_a_save_that_cannot_be_read_is_said, t_could_not_look_exits_two, t_the_driver_brief_says_the_rule):
        t()
    print("%s  walk_twins: %d of %d" % ("FAIL" if BAD else "ok  ", N[0] - len(BAD), N[0]))
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
