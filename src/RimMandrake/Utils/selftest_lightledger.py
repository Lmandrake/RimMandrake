#!/usr/bin/env python3
"""Light ledger selftest (LIGHT_LEDGER_ONE_1): a static guard, then the kernel's offline test.

1. Lint: no C# under src/RimMandrake writes `GlowRadius =` outside src/RimMandrake/_Shared/LightLedger/.
   A direct write is how ten files in five mods kept undoing each other's dimming
   (design/RimMandrake/light_ledger_design.md). Sanity probe: the ledger's own write must be found,
   so a lint that can see nothing cannot pass.
2. Every consumer that writes through LightLedger links BOTH shared files in its .csproj
   (EnableDefaultCompileItems is off in several, so a missing link compiles into nothing).
3. Builds and runs _Shared/LightLedger/SelfTest (net8.0, the production kernel file) through winbuild.

    python3 src/RimMandrake/Utils/selftest_lightledger.py [--lint-only]
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)                                   # src/RimMandrake
SHARED = os.path.join(SRC, "_Shared", "LightLedger")
WRITE = re.compile(r"\bGlowRadius\s*=(?!=)")
# Writers not yet migrated (LIGHT_LEDGER_ONE_1 lands one commit per writer). Shrinks to empty; a file
# listed here that no longer writes directly is itself a failure, so the list cannot rot.
NOT_YET_MIGRATED = {
    "LanternDeeps/Source/RM_AuroraCollapse.cs",
    "LanternDeeps/Source/RM_HydrocarbonWave3.cs",
    "Abyss/Source/RM_MapComponentDark.cs",
    "Abyss/Source/RM_CompKrizzak.cs",
    "LuminousPigment/Source/MapComponent_DeepfireLights.cs",
    "LuminousPigment/Source/MapComponent_DeepfireLights.Worn.cs",
}


def lint():
    bad, ledger_hits, consumers = [], 0, set()
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in ("obj", "bin", ".git", "__pycache__")]
        for f in files:
            if not f.endswith(".cs"):
                continue
            p = os.path.join(root, f)
            text = open(p, encoding="utf-8", errors="replace").read()
            rel = os.path.relpath(p, SRC)
            if "LightLedger." in text and not p.startswith(SHARED):
                consumers.add(rel.split(os.sep)[0])
            for i, line in enumerate(text.splitlines(), 1):
                code = line.split("//", 1)[0]
                if WRITE.search(code):
                    if p.startswith(SHARED):
                        ledger_hits += 1
                    else:
                        bad.append("%s:%d: %s" % (rel, i, line.strip()))
    ok = True
    still = {b.split(":", 1)[0] for b in bad}
    bad = [b for b in bad if b.split(":", 1)[0] not in NOT_YET_MIGRATED]
    for gone in sorted(NOT_YET_MIGRATED - still):
        print("FAIL %s is listed NOT_YET_MIGRATED but no longer writes directly - remove it from the list" % gone)
        ok = False
    if ledger_hits == 0:
        print("FAIL sanity probe: the ledger's own GlowRadius write was not found - the lint sees nothing")
        ok = False
    for b in bad:
        print("FAIL direct GlowRadius write outside the light ledger: " + b)
        ok = False
    for mod in sorted(consumers):
        projs = [os.path.join(SRC, mod, "Source", f) for f in os.listdir(os.path.join(SRC, mod, "Source"))
                 if f.endswith(".csproj")] if os.path.isdir(os.path.join(SRC, mod, "Source")) else []
        text = "".join(open(p).read() for p in projs)
        for need in ("LightLedger.cs", "LightLedgerKernel.cs"):
            if need not in text:
                print("FAIL %s uses LightLedger but its .csproj does not link %s" % (mod, need))
                ok = False
    print("lightledger lint: %d ledger write(s) seen, %d unlisted direct write(s), %d file(s) awaiting migration, consumers: %s"
          % (ledger_hits, len(bad), len(still & NOT_YET_MIGRATED), ", ".join(sorted(consumers)) or "none"))
    return ok


def kernel():
    sys.path.insert(0, HERE)
    import winbuild  # noqa: E402
    selftest = os.path.join(SHARED, "SelfTest")
    csproj = os.path.join(selftest, "RimMandrakeLightLedger.SelfTest.csproj")
    rc, rec = winbuild.stage_build(csproj, stage_name="LightLedgerSelfTest")
    if rc:
        print("selftest build FAILED")
        return False
    dll = winbuild.staged_win(rec, selftest) + "\\bin\\Release\\net8.0\\RimMandrakeLightLedger.SelfTest.dll"
    return subprocess.run([winbuild.dotnet_exe(), dll], cwd="/mnt/d/Luke/dev").returncode == 0


def main(argv):
    ok = lint()
    if "--lint-only" not in argv:
        ok = kernel() and ok
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
