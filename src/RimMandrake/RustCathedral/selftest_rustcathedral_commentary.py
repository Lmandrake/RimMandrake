"""selftest_rustcathedral_commentary.py -- cathedral_arc_lint.py is clean on the shipped commentary pools and reddens
on each defect it exists to catch, planted in a temp copy of Defs/ (never the shipped files); its string rules are
checked on poisoned fixture lines, with a control that a post-reveal aliveness line is allowed.
CATHEDRAL_STAGE_COMMENTARY_POOLS_1."""
import importlib.util
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []
RAN = []


def check(name, cond, detail=""):
    RAN.append(name)
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    lint = _load("rc_arc_lint", "cathedral_arc_lint.py")
    v = _load("rc_v", "validation.py")
    check("shipped: pools clean", lint.pool_problems() == [], lint.pool_problems())
    check("shipped: validation.commentary_problems clean", v.commentary_problems() == [], v.commentary_problems())

    xml = os.path.join(lint.ATTITUDE_XML)

    def planted(label, old, new, expect):
        tmp = tempfile.mkdtemp()
        try:
            shutil.copytree(os.path.join(HERE, "Defs"), os.path.join(tmp, "Defs"))
            p = os.path.join(tmp, xml)
            with open(p, encoding="utf-8") as fh:
                text = fh.read()
            assert old in text, old
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(text.replace(old, new, 1))
            got = lint.pool_problems(tmp)
            check(label, any(expect in g for g in got), got)
        finally:
            shutil.rmtree(tmp)

    w0 = "<li>The drone has not changed. The droid keeps turning its head toward it anyway.</li>"   # band 1 stage 0
    r3 = "<li>The droid stops talking mid-word, the way you stop when something enormous turns to look.</li>"  # band 3 stage 3
    planted("place named before the reveal", w0, "<li>The Cathedral has not changed its drone.</li>", "names-the-place")
    planted("agency before the reveal", w0, "<li>The droid is sure it is watching us.</li>", "agency before the reveal")
    planted("the Kindled named after the reveal", r3, "<li>The droid speaks of the Kindled.</li>", "kindled")
    planted("mercy explained after the reveal", r3, "<li>It spared us because we came in reverence.</li>", "mercy (ban 2)")
    planted("the drill described", r3, "<li>Something answers the drill far below.</li>", "drill (ban 6)")
    planted("§GM truth leaked", r3, "<li>The hum is the crystals thinking.</li>", "§GM truth")
    planted("a mechanic named", w0, "<li>The droid can tell the irritation is rising.</li>", "mechanic named")
    planted("a pool emptied", w0, "", "band 1 stage 0 has 2 lines")
    planted("a line repeated", w0, "<li>The drone here is flat as a dead battery. The droid says it has never heard a "
            "place sound so empty.</li>", "line repeated")
    planted("a band out of range", "<band>4</band>\n        <stage>3</stage>", "<band>9</band>\n        <stage>3</stage>",
            "out of range")
    planted("a stage pool dropped", "<band>4</band>\n        <stage>3</stage>", "<band>4</band>\n        <stage>2</stage>",
            "duplicate pool key band 4 stage 2")

    # string rules on fixture lines: an any-stage (-1) line is held to the pre-reveal rules
    check("fixture: alive at stage 1 caught", lint.findings("It is alive under us.", 1) != [])
    check("fixture: alive at any-stage caught", lint.findings("It is alive under us.", -1) != [])
    check("control: alive at stage 3 allowed", lint.findings("It is alive under us.", 3) == [],
          lint.findings("It is alive under us.", 3))
    check("fixture: hunting Sentinels caught", lint.findings("The guardians hunt the trespassers.", 3) != [])
    check("control: the sheet's own verbatim line passes", lint.findings(
        "Why have you angered this place? We know what it feels. So will you if you just listen.", 0) == [])

    tmp = tempfile.mkdtemp()
    try:
        p = os.path.join(tmp, "quest.xml")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("<Defs><QuestScriptDef><defName>X</defName><rulesStrings><li>questDescription->The Cathedral asks "
                     "a favour.</li></rulesStrings><description>The enclaves ask a favour.</description></QuestScriptDef></Defs>")
        got = lint.xml_findings(p, 1)
        check("--xml: quest-giver named pre-reveal caught (rulesStrings)", len(got) == 1 and "names-the-place" in got[0], got)
    finally:
        shutil.rmtree(tmp)

    print("%d/%d checks passed" % (len(RAN) - len(FAILS), len(RAN)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
