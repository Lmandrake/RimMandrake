#!/usr/bin/env python3
"""Planted faults for the polish watch of work_bundle_monitor.py (item
RIMMANDRAKE_WATCH_POLISH_FOR_NEW_BUGS_HE_FEARS_THE_OLD_NOISE). Run from the clone root.
Each fault: (file, before, after, the promise that must go red). The file is mutated in place, the selftest run
with no bytecode, the file restored and byte-compared. A fault whose anchor is missing fails by name."""
import os
import subprocess
import sys

MON = "src/RimMandrake/rimflow/work_bundle_monitor.py"
BL = "src/RimMandrake/contracts/blind.py"
TEST = "src/RimMandrake/rimflow/selftest_work_bundle_monitor.py"
F = [
    ("polish column lost", MON, '("polish" if any(is_polish(c["subject"]) for c in cs)', '("polish" if False', "polish-then-fix-one-regression"),
    ("no-polish fixes unseen", MON, 'fixes = [c["sha"][:10] for c in later if is_fix(c["subject"])]', 'fixes = [c["sha"][:10] for c in later if is_fix(c["subject"])] if col == "polish" else []', "no-polish-fix-counts-no-polish"),
    ("window five days", MON, "hi = tch + REGRESS_DAYS * DAY", "hi = tch + 5 * DAY", "regression-kinds-and-window"),
    ("revert ignored", MON, 'return bool(re.match(r"\\s*Revert\\b", subject or "")) or any(w in REVERT_WORDS for w in _lead_words(subject))', "return False", "regression-kinds-and-window"),
    ("selftest red unmatched", MON, 'return test == path or os.path.basename(test) == "selftest_%s.py" % stem', "return test == path", "regression-kinds-and-window"),
    ("reopen ignored", MON, '"reopened": sorted(named & reopened_members)', '"reopened": []', "regression-kinds-and-window"),
    ("pending read as ripe", MON, '"state": "ripe" if now >= hi else "pending"', '"state": "ripe"', "regression-kinds-and-window"),
    ("fix word anywhere", MON, "return not is_polish(subject) and not is_revert(subject) and any(w in FIX_WORDS for w in _lead_words(subject))", "return not is_polish(subject) and not is_revert(subject) and any(w.lower() in FIX_WORDS for w in re.findall(r'[A-Za-z]+', subject.replace('_', ' ')))", "regression-kinds-and-window"),
    ("run record is a file", MON, "return path.startswith(RECORD_PATHS) or bool(RECORD_NAMES.search(path))", "return path.startswith(RECORD_PATHS)", "regression-kinds-and-window"),
    ("published sha ignored", MON, 'and (c["sha"] in shas or (rx', 'and (False or (rx', "regression-kinds-and-window"),
    ("before-rule into no_polish", MON, 'col = "before_rule" if first < rule_t else', 'col = "before_rule" if False else', "before-rule-not-measured"),
    ("pre-rule day read as 0", MON, "    if t_hi <= rule_t:\n        return {\"state\": \"not measured\"", "    if False:\n        return {\"state\": \"not measured\"", "before-rule-not-measured"),
    ("probe skipped", MON, "    if not probe or not probe[0]:\n        return {\"state\": CNL", "    if False:\n        return {\"state\": CNL", "polish-zero-needs-probe"),
    ("probe accepts a blind reader", MON, 'if len(cs) != 2 or len(pol) != 1 or pol[0]["files"] != ["b.py"]:', "if False:", "polish-zero-needs-probe"),
    ("reader flag ignored", MON, 'flags = [x for x in rv["flags"] if x["path"] in files and c["t"] < x["t"] <= hi] if rv is not None else []', "flags = []", "polish-findings-from-reader"),
    ("a mark before the change counts", MON, 'if x["path"] in files and c["t"] < x["t"] <= hi and x.get("verdict") == "clean"]', 'if x["path"] in files and x.get("verdict") == "clean"]', "polish-findings-from-reader"),
    ("no close read as 0", MON, 'return round(born / closed, 2) if closed else "no close"', "return round(born / closed, 2) if closed else 0", "born-per-closed-per-bundle-and-day"),
    ("bundle born = the day's born", MON, 'b = set().union(*[by_unit.get(r["unit"], set()) for r in rs]) if rs else set()', "b = born if rs else set()", "born-per-closed-per-bundle-and-day"),
    ("born line on one day", MON, "crossed=over(g) and over(p))", "crossed=over(g))", "born-line-two-days"),
    ("lines section not owed", MON, "for s in SECTIONS + ((LINES_SECTION,) if crossed_lines(R) else ()):", "for s in SECTIONS:", "lines-crossed-section"),
    ("page drops the watch", MON, "return out + _watch_md(L.get(\"polish_watch\")) + [\"\"]", "return out + [\"\"]", "polish-watch-on-page-and-digest"),
    ("digest drops born", MON, "out.update(born=(b.get(\"day\") or {}).get(\"born\"),", "out.update(", "polish-watch-on-page-and-digest"),
    ("digest line drops the crossed line", BL, "    if m.born_line_crossed:\n", "    if False:\n", "polish-watch-on-page-and-digest"),
]


def run():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-B", TEST], capture_output=True, text=True, env=env, timeout=600)  # hang guard: the selftest takes ~1 s
    return r.returncode, r.stdout + r.stderr


def main():
    rc, out = run()
    if rc != 0:
        print("CONTROL RED: the unmutated selftest fails; no mutant can be read\n" + out[-2000:])
        return 2
    print("control: green")
    bad = 0
    for name, path, a, b, promise in F:
        orig = open(path, "rb").read()
        text = orig.decode()
        if text.count(a) != 1:
            print("NOT APPLIED  %-38s anchor found %d times" % (name, text.count(a)))
            bad += 1
            continue
        try:
            open(path, "w").write(text.replace(a, b))
            assert open(path, "rb").read() != orig
            rc, out = run()
        finally:
            open(path, "wb").write(orig)
        assert open(path, "rb").read() == orig, "restore failed: " + path
        fails = [ln for ln in out.splitlines() if ln.startswith("FAIL ")]
        hit = [ln for ln in fails if ln.startswith("FAIL " + promise)]
        verdict = "RED" if rc == 1 and hit else ("CRASH" if rc not in (0, 1) else "NOT CAUGHT" if rc == 0 else "RED ELSEWHERE")
        bad += verdict != "RED"
        print("%-13s %-38s want %-36s %d FAIL lines; first: %s" % (verdict, name, promise, len(fails),
                                                                   (hit or fails or ["-"])[0][5:110]))
    rc, out = run()
    print("control after: %s" % ("green" if rc == 0 else "RED"))
    print("MUTANTS: %d of %d red on their promise" % (len(F) - bad, len(F)))
    return 0 if bad == 0 and rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
