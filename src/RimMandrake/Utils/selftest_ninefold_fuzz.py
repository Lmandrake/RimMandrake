#!/usr/bin/env python3
"""Offline selftest of the Ninefold engine inside Salvation Rites (src/RimUtinni/Rites/Source), no game. Two parts:

1. SAVE TYPE ALIAS. Ninefold was its own mod (mandrake.rm.ninefold, namespace RimMandrake.Ninefold) until the
   owner folded it into Salvation Rites on 2026-10-22, and saves name its scribed classes by the old full name.
   Source/SelfTest/fixtures/ninefold_save_blocks_*.xml holds the two blocks copied verbatim from a canonical save.
   Every saved Class is run through the PRODUCTION map (NinefoldLegacyTypesKernel.MapTypeName, via the selftest exe's
   --legacy-map), and the result must be a class Rites declares, with every saved field still a Scribe label in that
   class's source. Also checked: nothing still declares the old namespace, and the Mod constructor registers the
   converter. `--saves` also scans the live CANONICAL_ASHKARR_START_* saves (read only) for every old class name.
2. FUZZ. Seeded action sequences (events, hourly mood walk + rooted erosion, launches, landings, violent deaths,
   first-contact triggers and the one-a-day queue) over the production kernel (RM_NinefoldKernel.cs), with design
   invariants checked after every step. A failing case is shrunk and printed as `family seed N: message | actions`;
   --fuzz-seed N replays it.

    python3 src/RimMandrake/Utils/selftest_ninefold_fuzz.py [--legacy-only] [--saves]
                                                            [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only seq|band|rank|mood]

The project is built through winbuild.stage_build (dotnet.exe is Windows-native), then run.
"""
import glob
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SOURCE = os.path.join(REPO, "src", "RimUtinni", "Rites", "Source")
SELFTEST = os.path.join(SOURCE, "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrake.Utinni.Rites.SelfTest.csproj")
FIXTURES = sorted(glob.glob(os.path.join(SELFTEST, "fixtures", "ninefold_save_blocks_*.xml")))
SAVES = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves"
OLD_NS = "RimMandrake.Ninefold"
NEW_NS = "RimMandrake.Utinni.Rites"
# Names that must NOT map: a near-miss namespace, the bare namespace, and an unrelated game type.
NEGATIVE = ["RimMandrake.NinefoldX.GameComponent_Ninefold", "RimMandrake.Ninefold.", "Verse.GameComponent",
            "RimMandrake.Utinni.Rites.GameComponent_Ninefold"]

fails = []


def check(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)[:300]))
    if not ok:
        fails.append(name)


def sources():
    out = {}
    for p in glob.glob(os.path.join(SOURCE, "*.cs")):
        with open(p, encoding="utf-8") as fh:
            out[os.path.basename(p)] = fh.read()
    return out


def class_source(srcs, ns, cls):
    """The file text declaring `class <cls>` inside `namespace <ns>`, or None."""
    for text in srcs.values():
        if re.search(r"^namespace\s+" + re.escape(ns) + r"\s*$", text, re.M) and \
           re.search(r"\bclass\s+" + re.escape(cls) + r"\b", text):
            return text
    return None


def legacy_map(exe_args, names):
    r = subprocess.run(exe_args + ["--legacy-map"] + names, cwd="/mnt/d/Luke/dev",
                       capture_output=True, text=True)
    rows = {}
    for line in r.stdout.splitlines():
        if "\t" in line:
            k, v = line.rstrip("\r").split("\t", 1)
            rows[k] = None if v == "-" else v
    return r.returncode, rows


def saved_classes():
    """Every RimMandrake.Ninefold.* Class in the live canonical saves (read only): {name: count of saves}."""
    seen = {}
    files = sorted(glob.glob(os.path.join(SAVES, "CANONICAL_ASHKARR_START_*.rws")))
    pat = re.compile(r'Class="(' + re.escape(OLD_NS) + r'\.[A-Za-z0-9_.]+)"')
    for f in files:
        with open(f, encoding="utf-8", errors="replace") as fh:
            for n in set(pat.findall(fh.read())):
                seen[n] = seen.get(n, 0) + 1
    return len(files), seen


def run_legacy(exe_args, with_saves):
    srcs = sources()
    stale = [n for n, t in srcs.items() if re.search(r"^namespace\s+" + re.escape(OLD_NS) + r"\b", t, re.M)]
    check("no Rites source still declares namespace " + OLD_NS, not stale, stale)
    mod = srcs.get("RM_NinefoldMod.cs", "")
    ctor = re.search(r"public RM_NinefoldMod\(ModContentPack content\)[^{]*\{(.*?)\n        \}", mod, re.S)
    check("the Mod constructor registers NinefoldLegacyTypeConverter",
          bool(ctor) and "NinefoldLegacyTypeConverter.Register()" in ctor.group(1))

    check("a save-block fixture exists", bool(FIXTURES), SELFTEST)
    blocks = []
    for fx in FIXTURES:
        blocks += list(ET.parse(fx).getroot())
    check("SANITY: the fixtures hold the GameComponent and MapComponent blocks",
          {b.get("Class") for b in blocks} >= {OLD_NS + ".GameComponent_Ninefold", OLD_NS + ".MapComponent_NinefoldOfferings"},
          [b.get("Class") for b in blocks])

    names = sorted({b.get("Class") for b in blocks})
    extra = {}
    if with_saves:
        n_files, extra = saved_classes()
        check("SANITY: canonical saves found and read", n_files > 0, SAVES)
        print("      canonical .rws saves read: %d; saves naming each old class: %s" % (n_files, extra))
        names = sorted(set(names) | set(extra))
    rc, rows = legacy_map(exe_args, names + NEGATIVE)
    check("the --legacy-map run exits 0 and answers every name", rc == 0 and len(rows) == len(names + NEGATIVE),
          (rc, rows))
    for n in NEGATIVE:
        check("not mapped: " + n, n in rows and rows[n] is None, rows.get(n))
    for n in names:
        mapped = rows.get(n)
        check("mapped: %s -> %s" % (n, mapped), mapped == NEW_NS + n[len(OLD_NS):], mapped)
        if not mapped:
            continue
        cls = mapped.rsplit(".", 1)[1]
        text = class_source(srcs, NEW_NS, cls)
        check("Rites declares " + mapped, text is not None)
    for b in blocks:
        mapped = rows.get(b.get("Class"))
        text = class_source(srcs, NEW_NS, mapped.rsplit(".", 1)[1]) if mapped else None
        labels = set(re.findall(r'\.Look\(\s*ref\s+[A-Za-z_][A-Za-z0-9_]*\s*,\s*"([A-Za-z0-9_]+)"', text or ""))
        fields = [c.tag for c in b]
        missing = [f for f in fields if f not in labels]
        check("every saved field of %s is still read (%d fields)" % (b.get("Class"), len(fields)),
              text is not None and not missing, missing)
    gc = next((b for b in blocks if b.get("Class", "").endswith(".GameComponent_Ninefold")), None)
    if gc is not None:
        sat = [float(li.text) for li in gc.find("ninefoldSatiation")]
        check("SANITY: the fixture's favour is real state (9 gods, not all zero)",
              len(sat) == 9 and any(abs(v) > 0 for v in sat), sat)


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="NinefoldFuzzSelfTest", extra_dirs=[SOURCE])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrake.Utinni.Rites.SelfTest.dll"
    exe_args = [winbuild.dotnet_exe(), dll]
    run_legacy(exe_args, "--saves" in argv)
    if "--legacy-only" in argv:
        print("%s (legacy only)" % ("FAIL" if fails else "PASS"))
        return 1 if fails else 0
    args = list(exe_args)
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    frc = subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode
    if fails:
        print("FAIL: %d legacy-type check(s): %s" % (len(fails), fails))
    return 1 if (fails or frc) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
