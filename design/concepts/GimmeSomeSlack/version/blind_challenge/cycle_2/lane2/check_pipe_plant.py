#!/usr/bin/env python3
"""Does T_NO_HOSE's scan, as it stood at <sha>, see a pipe that GSS ships? (bar no_hose_in_gss: "No hose, reel or pipe is
drawn by this mod"; T_NO_HOSE observes "no hose, reel or pipe def, texture or class").
    python3 check_pipe_plant.py <sha>
Loads northstar/selftest_gss_no_hose.py from git at <sha>, copies the mod's Defs/Patches/Textures/Source (this checkout)
into a temp folder, and plants one pipe at a time: a ThingDef RM_WaterPipe, a texture Things/RM_WaterPipe_south.png, a C#
class Building_WaterPipe. The clean copy must scan green. Exit 0 when the scan names every plant, 1 when it misses one,
2 when the instrument broke (the clean copy read red)."""
import importlib.util, os, shutil, subprocess, sys, tempfile
from pathlib import Path
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = Path(REPO) / "src/RimMandrake/GimmeSomeSlack"
sha = sys.argv[1]
txt = subprocess.run(["git", "show", "%s:src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py" % sha], cwd=REPO,
                     capture_output=True, text=True, check=True).stdout
tmp = tempfile.mkdtemp(prefix="gss_pipe_plant_")
try:
    p = Path(tmp) / "nohose_at_sha.py"; p.write_text(txt, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("nohose_at_sha", p); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    def copy(dst):
        for top in ("Defs", "Patches", "Textures", "Source"):
            if (MOD / top).is_dir(): shutil.copytree(MOD / top, Path(dst) / top, ignore=shutil.ignore_patterns("bin", "obj"))
        return Path(dst)
    def p_def(m):
        (m / "Defs" / "RM_PlantedPipe.xml").write_text('<?xml version="1.0" encoding="utf-8"?>\n<Defs><ThingDef><defName>RM_WaterPipe</defName>'
                                                       '<thingClass>Building</thingClass></ThingDef></Defs>\n', encoding="utf-8"); return "RM_WaterPipe"
    def p_tex(m):
        d = m / "Textures" / "Things"; d.mkdir(parents=True, exist_ok=True); (d / "RM_WaterPipe_south.png").write_bytes(b"\x89PNG\r\n\x1a\n"); return "RM_WaterPipe_south"
    def p_type(m):
        (m / "Source" / "PlantedPipe.cs").write_text("namespace X { public class Building_WaterPipe : object { } }\n", encoding="utf-8"); return "Building_WaterPipe"
    bad = 0
    for name, plant in (("pipe_def", p_def), ("pipe_texture", p_tex), ("pipe_class", p_type)):
        d = tempfile.mkdtemp(dir=tmp); m = copy(d)
        if mod.scan(m): print("UNMEASURED clean copy read red:", mod.scan(m)); sys.exit(2)
        want = plant(m); got = mod.scan(m); ok = any(want in h for h in got)
        print("%s  %s  want=%s got=%s" % ("CAUGHT" if ok else "MISSED", name, want, got)); bad += not ok
    print("scan at %s: %d of 3 pipe plants caught" % (sha[:10], 3 - bad))
    sys.exit(1 if bad else 0)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
