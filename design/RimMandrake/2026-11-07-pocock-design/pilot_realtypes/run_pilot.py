"""Real-types pilot (06-mined-live-bugs.md): the real ThinkNode_ConditionalPyrelandsColonist against the real Assembly-CSharp.dll,
outside the game. Built through winbuild.stage_build (dotnet.exe is Windows-native), run as a .NET Framework exe; exit 0 = every
scenario holds, 1 = a scenario failed, 3 = staging aborted.

    python3 design/RimMandrake/2026-11-07-pocock-design/pilot_realtypes/run_pilot.py            # the scenarios
    python3 design/RimMandrake/2026-11-07-pocock-design/pilot_realtypes/run_pilot.py --mutants  # each planted mutant must go red
    python3 design/RimMandrake/2026-11-07-pocock-design/pilot_realtypes/run_pilot.py --probe-map  # how far a real Map gets
    ... --net8                                                   # the same on .NET 8 (PyreGateScenario.net8.csproj)

Each run copies the current caller into caller/ (from src/ on main once it is there, else from origin/ralph/pyrelands), so the
build always compiles today's production file and a mutant is planted in the copy, never in src/.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import winbuild  # noqa: E402

NET8 = "--net8" in sys.argv
CSPROJ = os.path.join(HERE, "PyreGateScenario.net8.csproj" if NET8 else "PyreGateScenario.csproj")
PYRE = os.path.join(REPO, "src", "RimMandrake", "Pyrelands")
CALLER = "src/RimMandrake/Pyrelands/Source/ThinkNode_ConditionalPyrelandsColonist.cs"
BRANCH = "ralph/pyrelands"
COPY = os.path.join(HERE, "caller", os.path.basename(CALLER))

# (old, new) on the caller's text: each must turn at least one scenario red.
MUTANTS = [
    ("!pawn.Drafted && ", ""),
    ("pawn.IsColonist && ", ""),
    ('"RM_Pyrelands"', '"RM_Pyreland"'),
    ("PyrelandsMechanicsGate.On && ", ""),
    ("&& pawn.Map.Biome.defName", "|| pawn.Map.Biome.defName"),
    ("!pawn.Drafted", "pawn.Drafted"),
]


def caller_text():
    if os.path.exists(os.path.join(REPO, CALLER)):
        with open(os.path.join(REPO, CALLER)) as f:
            return f.read(), "main"
    subprocess.run(["git", "-C", REPO, "fetch", "-q", "origin", BRANCH], check=True)
    text = subprocess.run(["git", "-C", REPO, "show", "FETCH_HEAD:" + CALLER], check=True, capture_output=True, text=True).stdout
    return text, "origin/" + BRANCH


def build_and_run(text, extra=()):
    os.makedirs(os.path.dirname(COPY), exist_ok=True)
    with open(COPY, "w") as f:
        f.write(text)
    rc, rec = winbuild.stage_build(CSPROJ, extra=extra, stage_name="PyreGateRealTypesPilot",
                                   extra_dirs=[os.path.join(PYRE, "Source"), os.path.join(PYRE, "Assemblies")])
    if rc:
        print("pilot build FAILED")
        return rc
    asm = winbuild.staged_win(rec, os.path.join(PYRE, "Assemblies"))
    probe = ["--probe-map"] if "--probe-map" in sys.argv else []
    if NET8:
        cmd = [winbuild.dotnet_exe(), winbuild.staged_win(rec, HERE) + "\\bin8\\Release\\net8.0\\PyreGateScenario.dll"]
    else:
        exe = winbuild.staged_win(rec, HERE) + "\\bin\\Release\\net472\\PyreGateScenario.exe"
        cmd = [subprocess.run(["wslpath", "-u", exe], check=True, capture_output=True, text=True).stdout.strip()]
    return winbuild.run_interop(cmd + [asm] + probe, cwd="/mnt/d/Luke/dev", timeout=300)


def main():
    text, source = caller_text()
    print("caller from " + source)
    if "--mutants" not in sys.argv:
        return build_and_run(text)
    survivors = 0
    for old, new in MUTANTS:
        if old not in text:
            print("MUTANT STALE  %r is no longer in the caller" % old)
            survivors += 1
            continue
        # --no-incremental: a mutant run straight after another once reported the previous mutant's result (stale build).
        rc = build_and_run(text.replace(old, new, 1), extra=("--no-incremental",))
        verdict = "KILLED" if rc == 1 else ("SURVIVED" if rc == 0 else "BROKE rc=%d" % rc)
        survivors += verdict != "KILLED"
        print("MUTANT %-8s %r -> %r" % (verdict, old, new))
    build_and_run(text)
    print("%d of %d mutants killed" % (len(MUTANTS) - survivors, len(MUTANTS)))
    return 0 if survivors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
