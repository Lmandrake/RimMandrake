#!/usr/bin/env python3
"""selftest_coldstorage.py -- build and run the C# selftest of the cold storage engine (mandrake.rm.coldstorage).

    python3 src/RimMandrake/ColdStorage/selftest_coldstorage.py   (exit 0 = clean)

Source/SelfTest/Program.cs compiles the REAL Source/Kernel/ColdStorageKernel.cs and checks it against the shipped
Assembly-CSharp's GenTemperature.RotRateAtTemperature: rot per tick for each unit type, the temperature an item
on a unit reads, and every engine switch off giving vanilla rot at room temperature
(COLD_STORAGE_ENGINE_BUILD_CLIMATE_COMP). dotnet.exe is Windows-native, so the project is staged on D: by
Utils/winbuild.stage_build and run with `dotnet run --no-build`. No dotnet.exe -> exit 2, UNMEASURED.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
CSPROJ = os.path.join(HERE, "Source", "SelfTest", "RimMandrakeColdStorage.SelfTest.csproj")
DOTNET = ("/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe")


def static_checks():
    """Source-level pins the C# selftest cannot see. Returns a list of failure strings."""
    import re
    import xml.etree.ElementTree as ET
    fails = []
    # A class holding a static Texture2D/Material loaded at class init must be [StaticConstructorOnStartup], else
    # its cctor may run off the main thread (map load/gen are async long events) and DevMode warns every startup.
    src = os.path.join(HERE, "Source")
    for dirpath, dirnames, files in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in ("SelfTest", "obj", "bin")]
        for f in files:
            if not f.endswith(".cs"):
                continue
            path = os.path.join(dirpath, f)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            if re.search(r"static\s+readonly\s+(Texture2D|Material)\b", text) and "[StaticConstructorOnStartup]" not in text:
                fails.append("%s: static Texture2D/Material field without [StaticConstructorOnStartup]" % os.path.relpath(path, HERE))
    # LWM.DeepStorage.Properties is a CompProperties (LWM's own Deep_Storage.xml puts it under <comps>);
    # under <modExtensions> it is a load error and the unit gets no deep storage.
    lwm = os.path.join(HERE, "Patches", "ColdStorage_LWMDeepStorage.xml")
    root = ET.parse(lwm).getroot()
    found = 0
    for parent in root.iter():
        for li in parent.findall("li"):
            if li.get("Class") == "LWM.DeepStorage.Properties":
                found += 1
                if parent.tag != "comps":
                    fails.append("%s: LWM.DeepStorage.Properties under <%s>, must be <comps>" % (os.path.basename(lwm), parent.tag))
    if found == 0:
        fails.append("%s: no LWM.DeepStorage.Properties found (instrument blind?)" % os.path.basename(lwm))
    fails += seal_static_checks(ET, re)
    return fails


def seal_static_checks(ET, re):
    """COLD_STORAGE_SEALS_BUILD_RESIN_SAND_BRINE / COLD_STORAGE_TARSEAL_BUILD_SUMP_VAT pins. An external "Type:field"
    setting that names no public static field reads as unreadable, and GateOpen then treats it as ON: a typo would
    silently ignore the player's switch. The Sump's tar defs ride Cold Storage parents, so each must be MayRequire'd."""
    fails = []
    mods = os.path.dirname(HERE)
    files = [os.path.join(HERE, "Defs", "Seals", f) for f in sorted(os.listdir(os.path.join(HERE, "Defs", "Seals")))]
    tar = os.path.join(mods, "TheSump", "Defs", "ThingDefs_Buildings", "RM_TarSealing.xml")
    files.append(tar)
    refs = 0
    for path in files:
        root = ET.parse(path).getroot()
        for tag in ("settingField", "chanceSettingField"):
            for el in root.iter(tag):
                refs += 1
                typ, _, field = (el.text or "").strip().rpartition(":")
                cls = typ.rpartition(".")[2]
                src = None
                for d in (HERE, os.path.join(mods, "TheSump")):
                    for dp, dn, fs in os.walk(os.path.join(d, "Source")):
                        dn[:] = [x for x in dn if x not in ("SelfTest", "obj", "bin")]
                        for f in fs:
                            if f.endswith(".cs"):
                                t = open(os.path.join(dp, f), encoding="utf-8").read()
                                if re.search(r"class\s+%s\b" % re.escape(cls), t):
                                    src = t
                if src is None or not re.search(r"public\s+static\s+\w+\s+%s\s*=" % re.escape(field), src):
                    fails.append("%s: %s %r names no public static field" % (os.path.basename(path), tag, el.text))
        if path == tar:
            for d in root:
                if d.get("MayRequire") != "mandrake.rm.coldstorage":
                    fails.append("RM_TarSealing.xml: %s %s lacks MayRequire mandrake.rm.coldstorage" % (d.tag, d.findtext("defName")))
    if refs < 5:
        fails.append("seal settings refs: only %d found (instrument blind?)" % refs)
    return fails


def main():
    fails = static_checks()
    for f in fails:
        print("FAIL static: " + f)
    print("coldstorage static checks: %d failed" % len(fails))
    dotnet = next((c for c in DOTNET if os.path.exists(c)), None)
    if dotnet is None:
        print("UNMEASURED: dotnet.exe not found; the C# selftest needs the Windows-side .NET SDK")
        return 2
    import winbuild
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="SelfTest_coldstorage")
    if rc:
        print("selftest build FAILED")
        return rc
    r = subprocess.run([dotnet, "run", "--project", winbuild.staged_win(rec, CSPROJ), "-c", "Release", "--no-build"],
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout.replace("\r\n", "\n"))
    if r.stderr.strip():
        sys.stderr.write(r.stderr)
    return r.returncode or (1 if fails else 0)


if __name__ == "__main__":
    sys.exit(main())
