#!/usr/bin/env python3
"""Offline check of the five proof scenes Stage 3 owed Explosive Knockback 0.1.0
(RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN, 2026-11-14): sc_hose_drop, sc_closed_containers, sc_settings_sweep,
sc_frame_probe_check and sc_barrage_perf in design/concepts/ExplosiveKnockback/scenes.json. The scenes run only in a game
(their live commands are in version/test_table.json, UNRUN); this proves what can be read without one:
  N  every entry point and its control lane is in RM_KnockbackProof.SceneNames and reaches its builder from Build
  G  each builder carries the start assertions its scene names (INVALID guards) and its control lane
  F  the sweep's field list equals the settings' saved Scribe keys, and every saved key but enabled and shieldsAbsorbThrow
     is named in the scene's action text (a saved field in none of the three fails the scene, offline too)
  R  every builder that changes a setting or a def sets s.restore
  T  the runner can wait in real time (--real-seconds): a frame scene stepped by ticks inside one frame measures nothing
The frame probe's arithmetic is K-22 in Source/SelfTest/Program.cs (selftest_explosiveknockback_kernel.py).

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_stage3_scenes.py [--src DIR]
--src reads the mod's files from DIR (laid out like this folder) instead: the way it was watched red on the base commit.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCENES = os.path.join(REPO, "design", "concepts", "ExplosiveKnockback", "scenes.json")

LANES = {
    "sc_hose_drop": ("hose_carry_drop", ["hose_carry_drop_off"], "HoseCarryDrop",
                     ["FlowWorks hose reels not hooked", "RM_CarryHoseEnd", "TryTakeOrderedJob", "hoseDropped", "enabled = false",
                      "IntVec3.South, 2.9f", "Cheb(lt, to) == 3"]),
    "sc_closed_containers": ("closed_containers", ["closed_containers_control"], "ClosedContainers",
                             ["LWM_WeaponsLocker", "LWM_Safe", "SealedCrate", "AncientSecurityCrate",
                              "guy762_SecretFloorPanel_darkwhiteoutlines", "RM_KnockbackClosedStorage", "ClearClosedCache",
                              "76f", "249f", "closedContainerMassLimit", "\"jolt\"", "drawnOffset=UNMEASURED"]),
    "sc_settings_sweep": ("settings_sweep", ["settings_sweep_after"], "SettingsSweep",
                          ["the Cauldron (mandrake.rm.cauldron) not loaded", "LWM's Deep Storage (lwm.deepstorage) not loaded",
                           "maxThrowsPerExplosion", "maxItemThrowsPerMapTick", "immuneBodySize", "KernelReadBack", "sweepFieldDefaults"]),
    "sc_frame_probe_check": ("frame_probe_selfcheck", ["frame_probe_selfcheck_paused"], "FrameProbeSelfCheck",
                             ["SleepNextMs = 100", "KbFrameStats.SelfCheck(g, 100f", "TimeSpeed.Normal", "TimeSpeed.Paused", "maxInAir > 0"]),
    "sc_barrage_perf": ("barrage_perf", ["barrage_perf_off"], "BarragePerf",
                        ["probeSelfCheckPassed", "WithinBudget(g, 50f", "the Cauldron not loaded", "Zone_Stockpile",
                         "CellRect(s.o.x - 11, s.o.z - 5, 10, 10)", "SeedCloud", "enabled = false", "ActiveModsInLoadOrder"]),
}
# the game-side sweep lanes the table names (sc_settings_sweep's why_game); kernel-side lines are T_SETTINGS_SWEEP_OFFLINE
GAME_LANES = ["throwAnimals", "throwMechanoids", "throwDowned", "throwItems", "throwCorpses", "landingStun", "doorsTakeDamage",
              "debugDrawVectors", "vanillaCratesClosed", "heavyGoodsMinMass", "flyingGoods", "closedGuard", "heavyGoodsKnock",
              "gasChain", "fireHalf"]

fails = []


def check(code, ok, what):
    print(("PASS " if ok else "FAIL ") + code + " " + what)
    if not ok:
        fails.append(code + " " + what)


def body_of(src, name):
    """The text of `private static string <name>(Scene s)` up to the next private static string method."""
    m = re.search(r"private static string %s\(Scene s\)(.*?)(?=\n        (?:private|internal|public) static )" % re.escape(name), src, re.S)
    return m.group(1) if m else ""


def main():
    root = HERE
    if "--src" in sys.argv:
        root = os.path.abspath(sys.argv[sys.argv.index("--src") + 1])
    rd = lambda *p: open(os.path.join(root, *p), encoding="utf-8").read() if os.path.exists(os.path.join(root, *p)) else ""
    proof = rd("Source", "RM_KnockbackProof.cs")
    three = rd("Source", "RM_KnockbackProof_StageThree.cs")
    mod = rd("Source", "RM_KnockbackMod.cs")
    runner = rd("knockback_runner.py")
    csproj = rd("Source", "RimMandrake_ExplosiveKnockback.csproj")
    if not proof or not mod:
        print("UNMEASURED: RM_KnockbackProof.cs or RM_KnockbackMod.cs not found under %s" % root)
        return 2
    scenes = {s["id"]: s for s in json.load(open(SCENES, encoding="utf-8"))["scenes"]}
    names_m = re.search(r"SceneNames\s*=\s*\{(.*?)\};", proof, re.S)
    names = set(re.findall(r'"([a-z0-9_]+)"', names_m.group(1))) if names_m else set()
    check("N0", len(names) > 20 and "calibration" in names, "SceneNames parsed (%d names)" % len(names))
    check("N0b", 'Include="RM_KnockbackProof_StageThree.cs"' in csproj, "the csproj compiles RM_KnockbackProof_StageThree.cs")
    both = proof + "\n" + three
    for sid, (entry, controls, builder, needles) in LANES.items():
        ep = scenes.get(sid, {}).get("entry_point", "")
        check("N1 " + sid, ep.endswith("::" + entry), "scenes.json entry point is %s (%s)" % (entry, ep or "missing"))
        for n in [entry] + controls:
            check("N2 " + n, n in names, "%s is in SceneNames" % n)
        if entry == "settings_sweep":
            routed = 'StartsWith("settings_sweep_")' in proof and "return SettingsSweep(s);" in proof
        else:
            routed = all(('case "%s":' % n) in proof for n in [entry] + controls) and ("return %s(s);" % builder) in proof
        check("N3 " + sid, routed, "Build routes %s to %s" % (entry, builder))
        body = body_of(three, builder)
        check("G0 " + sid, len(body) > 200, "builder %s found" % builder)
        missing = [x for x in needles if x not in body and x not in three]
        check("G1 " + sid, not missing, "start assertions and control present" + (": missing %s" % missing if missing else ""))
        sets = re.search(r"RimMandrakeExplosiveKnockbackSettings\.\w+\s*=[^=]|modExtensions\.Remove|CurTimeSpeed\s*=|\.SetValue\(null", body)
        check("R1 " + sid, not sets or "s.restore =" in body, "changes a setting or a def only with s.restore set")
    # F: the sweep list, the saved keys, the scene's action text
    saved = re.findall(r'Scribe_Values\.Look\(ref (\w+), "(\w+)"', mod)
    keys = {k for _, k in saved}
    lst = re.search(r"SweepFields\s*=\s*\{(.*?)\};", three, re.S)
    sweep = set(re.findall(r'"(\w+)"', lst.group(1))) if lst else set()
    check("F0", len(keys) >= 40, "Scribe keys parsed (%d)" % len(keys))
    check("F1", sweep == keys, "SweepFields equals the saved Scribe keys" + ("" if sweep == keys else ": extra %s missing %s"
          % (sorted(sweep - keys), sorted(keys - sweep))))
    action = scenes.get("sc_settings_sweep", {}).get("action", "")
    # the two sheet switches the locked action names in words, not by field (blind cycle 2 built them: steward's decision 6)
    words = {"closedContainerGuard": "closed guard", "fireAtHalf": "fire at half"}
    unnamed = sorted(k for k in keys - {"enabled", "shieldsAbsorbThrow"}
                     if not re.search(r"\b%s\b" % k, action) and not (k in words and words[k] in action))
    check("F2", not unnamed, "every saved key but enabled and shieldsAbsorbThrow is named in sc_settings_sweep's action"
          + (": unnamed %s" % unnamed if unnamed else ""))
    banned = [b for b in ("maxThrowsPerExplosion", "maxItemThrowsPerMapTick", "immuneBodySize") if b in keys]
    check("F3", not banned, "no cap or body-size field is saved" + (": %s" % banned if banned else ""))
    lanes_m = re.search(r"SweepLanes\s*=.*?\{(.*?)\n        \};", three, re.S)
    lanes = set(re.findall(r'\["(\w+)"\]', lanes_m.group(1))) if lanes_m else set()
    gone = [l for l in GAME_LANES if l not in lanes]
    check("F4", not gone, "every game-side sweep lane has a lane" + (": missing %s" % gone if gone else ""))
    check("T1", "--real-seconds" in runner and "time.sleep(a.real_seconds)" in runner and "if a.ticks > 0:" in runner,
          "knockback_runner.py waits in real time and can skip tick stepping")
    print("%s stage3 scenes: %d failed" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
