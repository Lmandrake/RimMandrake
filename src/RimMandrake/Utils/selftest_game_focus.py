"""selftest_game_focus.py - nothing brings RimWorld forward or minimises a window unless explicitly opted in.

FOCUS_HEAL_TAME_HANDS_OFF_HIS_WINDOWS (owner ruling 2026-10-04: never fullscreen or focus the game). Written
failing-first. PowerShell is faked: every script is captured, and a script that calls SetForegroundWindow,
ShowWindow or AppActivate counts as a focus/minimise act.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import game_focus as G  # noqa: E402
import focus_heal as H  # noqa: E402

ACTS = ("SetForegroundWindow", "ShowWindow", "AppActivate", "SendKeys")
SCRIPTS = []


def fake_ps(script):
    SCRIPTS.append(script)
    if "(Get-Fg).title" in script:
        return "Google Chrome"
    return "0|0|Google Chrome"


def acted():
    return any(a in s for s in SCRIPTS for a in ACTS)


def prefs(value):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "Prefs.xml")
    with open(p, "w") as fh:
        fh.write("<PrefsData>\n  <volumeGame>0.8</volumeGame>\n%s</PrefsData>\n" % (
            "" if value is None else "  <runInBackground>%s</runInBackground>\n" % value))
    return p


def case(name, cond, detail=""):
    print("%-4s %s %s" % ("ok" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    G._ps = fake_ps
    os.environ.pop(G.OPT_IN_ENV, None)
    good = []

    good.append(case("pref read: True", G.run_in_background(prefs("True")) is True))
    good.append(case("pref read: False", G.run_in_background(prefs("False")) is False))
    good.append(case("pref read: absent is False (RimWorld ships it off)", G.run_in_background(prefs(None)) is False))
    good.append(case("pref read: unreadable is None, never True", G.run_in_background("/nope/Prefs.xml") is None))

    SCRIPTS.clear()
    r = G.preflight(prefs_path=prefs("True"))
    good.append(case("preflight with Run in background ON touches no window", r is None and not acted()))

    SCRIPTS.clear()
    try:
        G.preflight(prefs_path=prefs("False"))
        ok = False
    except G.FocusRefused as e:
        ok = "Run in background" in str(e)
    good.append(case("preflight with the pref OFF refuses loudly, no window touched", ok and not acted()))

    SCRIPTS.clear()
    try:
        G.focus_game(attempts=1, pause_s=0)
        ok = False
    except G.FocusRefused:
        ok = True
    good.append(case("focus_game without opt-in refuses and touches no window", ok and not acted()))

    SCRIPTS.clear()
    try:
        H.heal(RuntimeError("Chrome kept focus"))
        ok = False
    except H.FocusLost:
        ok = True
    good.append(case("heal without opt-in raises FocusLost and minimises nothing", ok and not acted()))

    SCRIPTS.clear()
    os.environ[G.OPT_IN_ENV] = "focus"
    try:
        G.focus_game(attempts=1, pause_s=0)
    except Exception:
        pass
    good.append(case("opt-in 'focus' does try to focus", any("SetForegroundWindow" in s for s in SCRIPTS)))
    minimised = any("ShowWindow($fgH, 6)" in s for s in SCRIPTS)
    good.append(case("opt-in 'focus' never minimises another window", not minimised))
    os.environ.pop(G.OPT_IN_ENV, None)

    print("%d/%d" % (sum(good), len(good)))
    return 0 if all(good) else 1


if __name__ == "__main__":
    sys.exit(main())
