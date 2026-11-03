#!/usr/bin/env python3
"""selftest_tidal_lock_guard.py -- offline proof for TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING.

    python3 src/RimMandrake/Utils/selftest_tidal_lock_guard.py

No game, no bridge. Checks:
  1. the guard is wired: both C# files in the mod csproj, the kernel in the C# SelfTest csproj (which compiles the
     REAL RM_TidalLockPresetKernel.cs and sweeps its truth table), the setting
     tidalLockPresetGuard defaults on, is saved, and has a checkbox; the guard writes the line the readers parse.
  1b. the truth table is RUN: selftest_sun_heat.py builds and runs the C# SelfTest, and its tidal lock preset guard
     case must print PASS (no dotnet, no build, or no such line is a FAIL here, never a pass).
  2. harvest_log.py's `tidallock` check fires on a MOVING SUN line and on nothing else.
  3. tidal_lock_readback.py parses and judges the guard's line (locked, restored, unlocked, absent).
  4. the remake runbook's S13/G12 name the dev start save of record (canon.yml planet.start_savegame), and the
     PAINT-made originals that loaded unlocked are named only as gone.
  5. the live proof file can measure A1: a live-site line loads a fixture save (that save, when the Saves folder is
     readable, reads TidallyLocked with NO worldPresetName), live-mods names CreatureBehaviors, the stager is told the
     three workshop packageIds A1 reads, and the proof line runs the readback with --expect-restored. Without these the
     round ran A1 20 times on a game with no Alien Worlds and no save loaded and measured nothing (2026-11-03).
"""
import os
import re
import subprocess
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


KERNEL_CASE = "tidal lock preset guard: restores only a locked save with no preset on Worldbuilder"


def kernel():
    """Build and run the C# SelfTest (it compiles the real RM_TidalLockPresetKernel.cs) and require its sweep to pass."""
    try:
        res = subprocess.run([sys.executable, os.path.join(HERE, "selftest_sun_heat.py")],
                             capture_output=True, text=True, timeout=480)
        out = res.stdout + "\n" + res.stderr
    except subprocess.TimeoutExpired:
        out = ""
    passed = [l for l in out.splitlines() if l.startswith("PASS ") and KERNEL_CASE in l]
    failed = [l for l in out.splitlines() if l.startswith("FAIL ") and KERNEL_CASE in l]
    for l in failed:
        print("      " + l[:400])
    check(len(passed) == 1 and not failed, "C# SelfTest RAN the PresetToRestore truth table and it passed")
    if not passed and not failed:
        print("      (no tidal lock case in the C# SelfTest output; tail: %r)" % out.strip()[-400:])


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
        live_def_check._bridge = lambda tool, params, timeout, read_only_static=False: (
            answers[params["method"]] if read_only_static else (None, "exit 3: REFUSING 'jawa/static_call'"))
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
    # RELENTLESS_LIVE_FIX_GAME_UP_NOTHING_MEASURED: the stub refuses an undeclared static call as the client does, so a
    # pass above also proves every read declares itself read-only (else the client's guard refused it, exit 3)


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


SAVES = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves"
WORKSHOP_NEEDS = ("7f.alienworlds", "7f.alienworlds.tidallylocked", "ferny.Worldbuilder")


def live_proof_file(text=None, saves=SAVES):
    """The live_proofs file -> list of what is missing for A1 to measure (empty = measurable)."""
    # the round's OWN parsers, so this reads the file exactly as the live round does
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
    import relentless_live_round as R
    if text is None:
        text = read(REPO, "infrastructure", "state", "live_proofs", "TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING.txt")
    gaps = []
    lines = text.splitlines()
    proofs = [m for m in (R.PROOF_LINE.match(l) for l in lines) if m]
    sites = [m for m in (R.SITE_LINE.match(l) for l in lines) if m]
    cmd = lambda m: m.group("cmd1") or m.group("cmd2")
    cid = lambda m: m.group("cid1") or m.group("cid2")
    a1 = [cmd(m) for m in proofs if cid(m) == "A1"]
    if not (len(a1) == 1 and "tidal_lock_readback.py" in a1[0] and "--expect-restored" in a1[0]):
        gaps.append("proof: one live-proof A1 running tidal_lock_readback.py --expect-restored")
    site = [cmd(m) for m in sites if cid(m) == "A1"]
    save = re.search(r"live_site\.py\s+--save\s+(\S+)", site[0]) if len(site) == 1 else None
    if not save:
        gaps.append("site: one live-site A1 that loads a save (live_site.py --save NAME)")
    elif os.path.isdir(saves):
        path = os.path.join(saves, save.group(1) + ".rws")
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                head = fh.read()  # whole file: worldPresetName sits past 6 MB in the canon start save
        except OSError:
            head = None
        if head is None:
            gaps.append("site: the save %s is not in the Saves folder" % save.group(1))
        else:
            t = re.search(r"<alienWorldsFrameworkPlanetType>\s*([^<\s]*)", head)
            if not (t and t.group(1) == "TidallyLocked"):
                gaps.append("site: %s does not read alienWorldsFrameworkPlanetType TidallyLocked" % save.group(1))
            if re.search(r"<worldPresetName>\s*[^<\s]", head):
                gaps.append("site: %s carries a worldPresetName, so the guard has nothing to restore" % save.group(1))
    else:
        print("NOTE  Saves folder unreadable here: the fixture's shape is not checked")
    if "CreatureBehaviors" not in R.live_mods(text):
        gaps.append("mods: live-mods names CreatureBehaviors")
    comments = "\n".join(l for l in lines if l.lstrip().startswith("#"))
    for pid in WORKSHOP_NEEDS:
        if not re.search(r"(?<![\w.])%s(?![\w.])" % re.escape(pid), comments):
            gaps.append("stager: the load note names %s" % pid)
    return gaps


def live_proofs():
    gaps = live_proof_file()
    check(not gaps, "live proof file can measure A1%s" % ("" if not gaps else ": missing " + "; ".join(gaps)))
    good = read(REPO, "infrastructure", "state", "live_proofs", "TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING.txt")
    # the instrument sees: each mutant of the real file must be caught
    mutants = {
        "no live-site": "\n".join(l for l in good.splitlines() if not l.startswith("live-site")),
        "site loads a quicktest": good.replace("--save rm_proof_atmosphere", "--biome TemperateForest"),
        "site loads a save with a preset": good.replace("rm_proof_atmosphere", "ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3"),
        "site loads a missing save": good.replace("rm_proof_atmosphere", "rm_no_such_save_xyz"),
        "no live-mods": "\n".join(l for l in good.splitlines() if not l.startswith("live-mods")),
        "no Worldbuilder in the note": good.replace("ferny.Worldbuilder", "ferny.Other"),
        "no tidallylocked in the note": good.replace("7f.alienworlds.tidallylocked", "7f.other"),
        "proof without --expect-restored": good.replace(" --expect-restored", ""),
    }
    for name, text in mutants.items():
        g = live_proof_file(text)
        if name in ("site loads a save with a preset", "site loads a missing save") and not os.path.isdir(SAVES):
            print("NOTE  mutant not checkable without the Saves folder: %s" % name)
            continue
        check(bool(g), "live proof mutant caught: %s" % name)


def main():
    wiring()
    kernel()
    harvest()
    readback()
    runbook()
    live_proofs()
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
