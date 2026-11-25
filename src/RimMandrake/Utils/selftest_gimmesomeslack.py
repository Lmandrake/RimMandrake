#!/usr/bin/env python3
"""Offline selftest of the Gimme Some Slack core (graph reduction, planner, slack laying) against the
Python oracle (src/RimMandrake/Utils/mockups/messy_conduit/).

    python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py [--probe] [--no-export] [--dump <dir on /mnt/...>] [--geometry | --geometry-only] [--no-slacken] [--slice-only] [--slice-repeat] [--lay-profile] [--switchlight-only | --switchlight-plant | --kinks-only | --holes-only] [--no-unkink] [--reach-only]

1. Re-exports the oracle's scenes and answers (export_oracle.py) unless --no-export.
2. Builds src/RimMandrake/GimmeSomeSlack/Source/SelfTest/ (net8.0, compiles ../Core/*.cs, the
   production files) through winbuild.stage_build: dotnet.exe is Windows-native and cannot build
   from the ext4 clone, so the project is staged on D:.
3. Runs it. --probe plants one wrong expectation per scene; the run must then report every scene
   as FAILING (a selftest that cannot fail proves nothing).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeGimmeSomeSlack.SelfTest.csproj")
SOURCE = os.path.dirname(SELFTEST)


def selftest_cwd():
    """Working directory for dotnet.exe: agent scratch on D:, a drive path Windows can use. It was the read-only mirror
    /mnt/d/Luke/dev (review 9.7), which an agent must never write and which the run could litter."""
    d = os.path.join("/mnt/d/ClaudeWork/rimmandrake/scratch", "gss_selftest_cwd")
    os.makedirs(d, exist_ok=True)
    return d


def sliced_rebuild_callers():
    """GSS round 3 review (2026-10-26): a budgeted Rebuild lays only ~8 ms of edges and leaves the rest to later frames, so a
    scripted caller that reads Pieces right after it (cstyles probe, JawaBench gss staging) saw a half-laid set. The public
    Rebuild() must be the complete build; only the component's own frame paths may ask for a slice (Rebuild(false))."""
    comp = os.path.join(SOURCE, "RM_MapComponent_CordGraph.cs")
    with open(comp, encoding="utf-8") as f:
        text = f.read()
    import re
    bad = []
    if not re.search(r"public void Rebuild\(\)\s*=>\s*Rebuild\(true\);", text):
        bad.append("RM_MapComponent_CordGraph.Rebuild() is not the complete build (Rebuild(true))")
    if text.count("Rebuild(false)") < 2:
        bad.append("the frame paths (PiecesForSection, MapComponentUpdate) do not ask for a budgeted slice")
    for root, dirs, files in os.walk(SOURCE):
        dirs[:] = [d for d in dirs if d not in ("SelfTest", "bin", "obj")]
        for n in files:
            p = os.path.join(root, n)
            if n.endswith(".cs") and p != comp:
                with open(p, encoding="utf-8") as f:
                    if "Rebuild(false)" in f.read():
                        bad.append(os.path.relpath(p, SOURCE) + " asks for a budgeted slice outside the component")
    for b in bad:
        print("FAIL sliced rebuild: " + b)
    print("sliced rebuild callers: " + ("FAIL" if bad else "ok"))
    return 1 if bad else 0


def probe_read_wiring(probe_text=None, comp_text=None):
    """RIMMANDRAKE_SETTLE_SLACK_CUT_CENSUS_DEAD_END_POLL_LATE (visit 2: M8 read the published pieces while the workers still owed the
    cut's edges). The offline SelfTest proves the read decision (Core/ProbeRead.cs, ProbeReadChecks); this proves the Verse side
    calls it: the probe's dispatcher settles a laid-set read first, the component settles with the complete Rebuild, and the
    census reports the pending count the save/load triplet's read requires (validation.py run_triplet reads "pending" == "0")."""
    import re
    if probe_text is None:
        with open(os.path.join(SOURCE, "GimmeSomeSlackProbe.cs"), encoding="utf-8") as f:
            probe_text = f.read()
    if comp_text is None:
        with open(os.path.join(SOURCE, "RM_MapComponent_CordGraph.cs"), encoding="utf-8") as f:
            comp_text = f.read()
    bad = []
    run = re.search(r"private static string Run\(Map map, RM_MapComponent_CordGraph comp, string cmd\)\s*\{(.*?)if \(cmd == \"census\"\)", probe_text, re.S)
    if not run or not re.search(r"ProbeRead\.ReadsLaidSet\(cmd\)\s*&&\s*comp\.SettleForRead\(\)", run.group(1)):
        bad.append("the probe's Run does not settle a laid-set read (ProbeRead.ReadsLaidSet + SettleForRead) before it dispatches")
    census = re.search(r"private static string Census\(Map map, RM_MapComponent_CordGraph comp\)(.*?)\n        \}\n", probe_text, re.S)
    if not census or 'F("pending", comp.LastPending' not in census.group(1):
        bad.append("the census does not report pending (the triplet's read is then never taken)")
    settle = re.search(r"internal bool SettleForRead\(\)\s*\{(.*?)\n        \}", comp_text, re.S)
    if not settle or "ProbeRead.OwesBuild(" not in settle.group(1) or "Rebuild(true)" not in settle.group(1):
        bad.append("RM_MapComponent_CordGraph.SettleForRead does not finish an owed build with the complete Rebuild(true)")
    for b in bad:
        print("FAIL probe read wiring: " + b)
    print("probe read wiring: " + ("FAIL" if bad else "ok"))
    return 1 if bad else 0


def main(argv):
    if sliced_rebuild_callers():
        return 1
    if probe_read_wiring():
        return 1
    if "--no-export" not in argv:
        r = subprocess.run([sys.executable, os.path.join(HERE, "mockups", "messy_conduit", "export_oracle.py")])
        if r.returncode:
            return r.returncode
    # every clone stages this test in the same D: folder: hold it from build through run (another clone's run held the
    # DLL while this one rebuilt it, MSB3027, 2026-11-16; RIMMANDRAKE_LOCK_GSS_SELFTEST_STAGE_SHARED_BY_EVERY_CLONE)
    with winbuild.exclusive("GimmeSomeSlackSelfTest"):
        rc, rec = winbuild.stage_build(CSPROJ, stage_name="GimmeSomeSlackSelfTest",
                                       extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", d)
                                                   # Defs, Patches: read by LookIconChecks / WallLampLookChecks (0.2.0)
                                                   for d in ("Source/Core", "Defs", "Patches")])
        if rc:
            print("selftest build FAILED")
            return rc
        dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeGimmeSomeSlack.SelfTest.dll"
        args = [winbuild.dotnet_exe(), dll] + (["--probe"] if "--probe" in argv else []) + (["--perdig-only"] if "--perdig-only" in argv else []) + (["--slice-repeat"] if "--slice-repeat" in argv else []) + (["--slice-only"] if "--slice-only" in argv else []) + (["--old-form"] if "--old-form" in argv else []) + (["--lay-profile"] if "--lay-profile" in argv else []) + (["--shape-diag"] if "--shape-diag" in argv else []) + (["--endkind-only"] if "--endkind-only" in argv else []) + (["--joins-only"] if "--joins-only" in argv else []) + (["--holes-only"] if "--holes-only" in argv else []) + (["--wallplugs-only"] if "--wallplugs-only" in argv else []) + (["--reach-only"] if "--reach-only" in argv else []) + (["--looks-only"] if "--looks-only" in argv else []) + (["--aerial-only"] if "--aerial-only" in argv else []) + (["--switchoff-only"] if "--switchoff-only" in argv else []) + [f for f in ("--switchlight-only", "--switchlight-plant", "--kinks-only") if f in argv] + (["--live-sweep-only"] if "--live-sweep-only" in argv else []) + (["--geometry"] if "--geometry" in argv else []) + (["--geometry-only"] if "--geometry-only" in argv else []) + (["--no-slacken"] if "--no-slacken" in argv else []) + (["--no-unkink"] if "--no-unkink" in argv else []) + [f for f in ("--probe-read-only", "--probe-read-old") if f in argv]
        # the stage holds no PNGs (winbuild.RSYNC_EXCLUDES): LookIconChecks / WallLampLookChecks read the clone's Textures/
        args += ["--textures", winbuild.win(os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "Textures"))]
        for i, a in enumerate(argv):   # approach B fuzz knobs (GssFuzz.cs): --fuzz-scale F, --fuzz-only NAME, --fuzz-seed N
            if a.startswith("--fuzz") and i + 1 < len(argv):
                args += [a, argv[i + 1]]
        if "--scale-bench" in argv:   # CordScaleBench.cs: --scale-bench [K,K,...] (frame cost and per-frame allocation vs lattices)
            i = argv.index("--scale-bench")
            args += ["--scale-bench"] + [a for a in argv[i + 1:i + 2] if not a.startswith("--")]
        if "--unroutable-census" in argv:   # A7 census (UnroutableCensus.cs): --unroutable-census OUT.json [SEEDS]
            i = argv.index("--unroutable-census")
            args += ["--unroutable-census", winbuild.win(os.path.abspath(argv[i + 1]))] + argv[i + 2:i + 3]
        if "--live-census" in argv:   # LiveEndCensus.cs: --live-census OUT.jsonl [FUZZ_SEEDS [FAMILY_SEEDS]], every live cut end read by the three bars
            i = argv.index("--live-census")
            args += ["--live-census", winbuild.win(os.path.abspath(argv[i + 1]))] + [a for a in argv[i + 2:i + 4] if not a.startswith("--")] + (["--placed-only"] if "--placed-only" in argv else [])
        if "--scene-dump" in argv:   # SceneDump.cs: --scene-dump OUT.json fuzz:SEED[:STEP] | placed:N | family:N, a built scene for scene_picture.py
            i = argv.index("--scene-dump")
            args += ["--scene-dump", winbuild.win(os.path.abspath(argv[i + 1])), argv[i + 2]]
        if "--slope-census" in argv:   # SceneDump.Census: every slope and stub-join refusal of the first N random worlds, one line each
            i = argv.index("--slope-census")
            args += ["--slope-census", winbuild.win(os.path.abspath(argv[i + 1]))] + argv[i + 2:i + 3]
        if "--lab" in argv:   # LabWorld.cs: --lab WORLD.json OUT.json, the shape lab on a world the live probe dumped
            i = argv.index("--lab")
            args += ["--lab", winbuild.win(os.path.abspath(argv[i + 1])), winbuild.win(os.path.abspath(argv[i + 2]))]
        if "--switchlamp-dump" in argv:   # SwitchLampArt pixels for GimmeSomeSlack/tools/switch_lamp_mock.py
            i = argv.index("--switchlamp-dump")
            args += ["--switchlamp-dump", winbuild.win(os.path.abspath(argv[i + 1]))]
        if "--wallplug-seeds" in argv:   # WallPlugChecks.cs on N other seeds (the sweep beyond the check's own two)
            args += ["--wallplug-seeds", argv[argv.index("--wallplug-seeds") + 1]]
        if "--wallplug-dump" in argv:   # WallPlugChecks.cs: every wall plug cord of the sweep, one JSON line each (tools/wall_plug_sweep.py)
            i = argv.index("--wallplug-dump")
            args += ["--wallplugs-only", "--wallplug-dump", winbuild.win(os.path.abspath(argv[i + 1]))]
        if "--dump" in argv:
            args += ["--dump", winbuild.win(os.path.abspath(argv[argv.index("--dump") + 1]))]
        return winbuild.run_interop(args, cwd=selftest_cwd(), timeout=None)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
