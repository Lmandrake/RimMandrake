#!/usr/bin/env python3
"""selftest_tidal_lock_guard.py -- offline proof for TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING.

    python3 src/RimMandrake/Utils/selftest_tidal_lock_guard.py

No game, no bridge. Checks:
  1. the guard is wired: both C# files in the mod csproj, the kernel in the C# SelfTest csproj (which compiles the
     REAL RM_TidalLockPresetKernel.cs and sweeps its truth table: selftest_sun_heat.py runs it), the setting
     tidalLockPresetGuard defaults on, is saved, and has a checkbox; the guard writes the line the readers parse.
  2. harvest_log.py's `tidallock` check fires on a MOVING SUN line and on nothing else.
  3. tidal_lock_readback.py parses and judges the guard's line (locked, restored, unlocked, absent).
  4. the remake runbook's S13/G12 name the dev start save of record (canon.yml planet.start_savegame), and the
     PAINT-made originals that loaded unlocked are named only as gone.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
SRC = os.path.join(REPO, "src", "RimMandrake", "CreatureBehaviors", "Source")
FAILS = []


def check(ok, what):
    print(("PASS  " if ok else "FAIL  ") + what)
    if not ok:
        FAILS.append(what)


def read(*p):
    with open(os.path.join(*p), encoding="utf-8-sig") as fh:
        return fh.read()


def wiring():
    proj = read(SRC, "RM_CreatureBehaviors.csproj")
    check('<Compile Include="RM_TidalLockPresetKernel.cs" />' in proj and '<Compile Include="RM_TidalLockPresetGuard.cs" />' in proj,
          "mod csproj compiles the kernel and the guard")
    st = read(SRC, "SelfTest", "RimMandrakeCreatureBehaviors.SunHeat.SelfTest.csproj")
    check('<Compile Include="..\\RM_TidalLockPresetKernel.cs" />' in st, "C# SelfTest compiles the real kernel")
    prog = read(SRC, "SelfTest", "Program.cs")
    check("RM_TidalLockPresetKernel.PresetToRestore" in prog, "C# SelfTest sweeps PresetToRestore")
    mod = read(SRC, "RM_CreatureBehaviorsMod.cs")
    check("public static bool tidalLockPresetGuard = true;" in mod, "setting tidalLockPresetGuard defaults on")
    check('Scribe_Values.Look(ref tidalLockPresetGuard, "tidalLockPresetGuard", true);' in mod, "setting is saved, default on")
    check("ref tidalLockPresetGuard," in mod, "setting has a checkbox")
    check('"tidalLockPresetGuard"' in mod.split("Group(list, \"Pinned sun and false shade\"")[1].split("\n")[0],
          "setting is in its settings group (reset/search)")
    guard = read(SRC, "RM_TidalLockPresetGuard.cs")
    check('LinePrefix = "[RM CreatureBehaviors] planet lock at load: "' in guard, "guard writes the parsed line prefix")
    for field in ('"saved="', '" preset="', '" backend="', '" current="', '" lockPatches="', '" action="', "MOVING SUN"):
        check(field in guard, "guard line carries %s" % field)
    check("priority = Priority.Last" in guard, "load postfix runs after Alien Worlds' PostSaveLoadHook")
    check("LoadSaveMode.LoadingVars" in guard, "saved planet type captured while loading vars")


LOCKED_OK = ("[RM CreatureBehaviors] planet lock at load: saved=TidallyLocked preset=(none) backend=Worldbuilder "
             "current=TidallyLocked lockPatches=True action=restored")
LOCKED_PRESET = ("[RM CreatureBehaviors] planet lock at load: saved=TidallyLocked preset=TidallyLocked backend=Worldbuilder "
                 "current=TidallyLocked lockPatches=True action=none")
MOVING = ("[RM CreatureBehaviors] planet lock at load: saved=TidallyLocked preset=(none) backend=Worldbuilder "
          "current=Default lockPatches=False action=off -- MOVING SUN: the save is tidally locked, the loaded planet is not")
QUICKTEST = ("[RM CreatureBehaviors] planet lock at load: saved=(none) preset=(none) backend=Worldbuilder "
             "current=Default lockPatches=False action=none")


def harvest():
    import harvest_log
    rows = [c for c in harvest_log.CHECKS if c[0] == "tidallock"]
    check(len(rows) == 1 and rows[0][3] == 0, "harvest_log has one tidallock check, baseline 0")
    if not rows:
        return
    rx = re.compile(rows[0][2])
    lines = [LOCKED_OK, LOCKED_PRESET, MOVING, QUICKTEST, "Loading game from file X with mods:", "sun rises"]
    check(harvest_log.count(lines, rx) == 1, "tidallock counts the MOVING SUN line only (1 of 6 synthetic lines)")
    check(harvest_log.count([MOVING], rx) == 1 and harvest_log.count([LOCKED_OK, QUICKTEST], rx) == 0,
          "tidallock: unlocked locked-save is red, a restored load and a quicktest world are not")


def readback():
    import tidal_lock_readback as r
    d = r.parse_line(LOCKED_OK)
    check(d == {"saved": "TidallyLocked", "preset": "(none)", "backend": "Worldbuilder", "current": "TidallyLocked",
                "lockPatches": "True", "action": "restored"}, "readback parses every field of the guard line")
    check(r.parse_line("Loading game from file X") is None, "readback ignores other lines")
    check(r.judge_line(d, expect_restored=True)[0] == r.PASS, "restored + locked passes --expect-restored")
    check(r.judge_line(r.parse_line(LOCKED_PRESET), expect_restored=False)[0] == r.PASS, "locked save with preset passes")
    check(r.judge_line(r.parse_line(LOCKED_PRESET), expect_restored=True)[0] == r.FAIL,
          "--expect-restored fails a load the guard did not have to fix (wrong fixture loaded)")
    check(r.judge_line(r.parse_line(MOVING))[0] == r.FAIL, "unlocked load fails")
    check(r.judge_line(r.parse_line(QUICKTEST))[0] == r.FAIL, "a Default planet fails (not locked)")
    check(r.judge_line(None)[0] == r.UNMEASURED, "no guard line is UNMEASURED, not a pass")
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False, encoding="utf-8") as fh:
        fh.write(MOVING + "\nnoise\n" + LOCKED_OK + "\nmore noise\n")
    try:
        check(r.last_load_line(fh.name) == d, "readback takes the LAST load line in the log")
        check(r.main(["--log", fh.name, "--no-bridge", "--expect-restored"]) == r.PASS, "main --no-bridge exits 0 on a locked log")
    finally:
        os.unlink(fh.name)
    bridge(r)


def bridge(r):
    """bridge_reads() against a stubbed client: the three answers decide the verdict, a failed read is never a pass."""
    import live_def_check
    real = live_def_check._bridge
    ok = lambda v: ({"success": True, "result": v}, None)
    absent = ({"success": False, "message": "Type not found: Worldbuilder.World_ExposeData_Patch"}, None)

    def run(cur, patched, preset):
        answers = {"get_Current": cur, "HasAnyPatches": patched, "get_WorldPresetName": preset}
        live_def_check._bridge = lambda tool, params, timeout: answers[params["method"]]
        try:
            return r.bridge_reads()[0]
        finally:
            live_def_check._bridge = real
    check(run(ok("TidallyLocked"), ok(True), ok("TidallyLocked")) == r.PASS, "bridge: locked + patched + preset passes")
    check(run(ok("TidallyLocked"), ok(True), absent) == r.PASS, "bridge: no Worldbuilder (type not found) passes on Current alone")
    check(run(ok("Default"), ok(False), ok("null")) == r.FAIL, "bridge: Default planet fails")
    check(run(ok("TidallyLocked"), ok(True), ok("null")) == r.FAIL, "bridge: locked now but no preset name (next save loses it) fails")
    check(run(ok("TidallyLocked"), ok(True), (None, "timeout")) == r.UNMEASURED, "bridge: a preset read that did not finish is UNMEASURED")
    check(run(ok("TidallyLocked"), ok(True), ({"success": False, "message": "Invoke threw"}, None)) == r.UNMEASURED,
          "bridge: a preset read that failed for another reason is UNMEASURED, not 'no Worldbuilder'")
    check(run((None, "no bridge"), ok(True), ok("TidallyLocked")) == r.UNMEASURED, "bridge: no answer is UNMEASURED")


def runbook():
    import yaml  # noqa: canon.yml is YAML
    canon = yaml.safe_load(read(REPO, "infrastructure", "state", "canon.yml"))
    start = canon["planet"]["start_savegame"]
    start = start if isinstance(start, str) else (start.get("file") or start.get("name") or str(start))
    stem = os.path.basename(start).replace(".rws", "")
    rb = read(REPO, "design", "RimMandrake", "world_remake_2026-10-19", "06_remake_runbook.md")
    rows = {m.group(1): m.group(0) for m in re.finditer(r"^\| (S13|G12) \|.*$", rb, re.M)}
    check(set(rows) == {"S13", "G12"}, "runbook has rows S13 and G12")
    for k, row in rows.items():
        check(stem in row, "runbook %s names the dev start save of record %s" % (k, stem))
        check("TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING" in row, "runbook %s cites the item" % k)


def main():
    wiring()
    harvest()
    readback()
    runbook()
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
