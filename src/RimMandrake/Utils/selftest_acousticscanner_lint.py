#!/usr/bin/env python3
"""Planted-defect selftest for lint_acousticscanner_defs.py: clean on the real mod and the real payloads, then one planted
defect at a time (in a copy of the mod, or in a copy of a real payload patch) is caught.

    python3 src/RimMandrake/Utils/selftest_acousticscanner_lint.py
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_acousticscanner_defs as L  # noqa: E402
import modpack_lint_harness as H  # noqa: E402

M = "Source/RM_AcousticScannerMod.cs"
K = "Source/Kernel/RM_AcousticKernel.cs"
PLANTS = [
    ("banding floor lowered below 7", K, "public const int MinBandSize = 7;", "public const int MinBandSize = 3;", "as-banding-floor"),
    ("settings floor no longer the kernel's", M, "MinBandSize = RM_AcousticKernel.MinBandSize;", "MinBandSize = 7;", "as-banding-floor"),
    ("band slider not bounded by the floor", M, "list.Slider(BandSizeClamped, MinBandSize, MaxBandSize)", "list.Slider(BandSizeClamped, 3, MaxBandSize)", "as-banding-floor"),
    ("slider excludes the default", M, "list.Slider(overlayHours, 1f, 48f)", "list.Slider(overlayHours, 10f, 48f)", "as-setting-ranges"),
    ("reset snapshot removed", M, "shippedDefaults = SnapshotDefaults()", "shippedDefaultz = SnapshotDefaults()", "as-setting-ranges"),
    ("settings key differs from field", M, 'Scribe_Values.Look(ref rangeCells, "rangeCells", 60f)', 'Scribe_Values.Look(ref rangeCells, "range", 60f)', "settings-scribed"),
    ("kernel missing from the csproj", "Source/RM_AcousticScanner.csproj", '<Compile Include="Kernel\\RM_AcousticKernel.cs" />', "", "compile-listed"),
    ("kernel imports Verse", K, "using System.Collections.Generic;", "using System.Collections.Generic;\nusing Verse;", "as-kernel-pure"),
    ("a translated key deleted", "Languages/English/Keyed/RM_AcousticScanner_Keys.xml", "<RM_Acoustic_NoPower>", "<RM_Acoustic_NoPowr>", "as-keyed"),
    ("a placeholder the call does not fill", "Languages/English/Keyed/RM_AcousticScanner_Keys.xml", "<RM_Acoustic_Disabled>", "<RM_Acoustic_Disabled>{0} ", "as-keyed"),
    ("a def class typo", "Defs/ThingDefs_Buildings/RM_AcousticSounder.xml", "RimMandrake.AcousticScanner.RM_Building_AcousticSounder", "RimMandrake.AcousticScanner.RM_Building_AcousticSounde", "class-resolves"),
]

PAYLOAD_SRC = os.path.join(L.REPO, "src", "RimMandrake", "Stillsand", "Patches", "RM_AcousticPayload_Stillsand.xml")
PAYLOAD_PLANTS = [
    ("payload: zero weight", "<weight>2</weight>", "<weight>0</weight>", "non-positive weight"),
    ("payload: negative stride", "<cellSampleStride>4</cellSampleStride>", "<cellSampleStride>0</cellSampleStride>", "cellSampleStride"),
    ("payload: colour channel above 1", "<color>(1, 0.4, 0.3)</color>", "<color>(1, 4, 0.3)</color>", "within 0..1"),
    ("payload: label removed", "<label>buried cache</label>", "<label></label>", "has no label"),
    ("payload: thing def typo", "<li>RM_SandBusterMound</li>", "<li>RM_SandBusterMoun</li>", "RM_SandBusterMoun"),
    ("payload: pawn race typo", "<li>RM_Vekka</li>", "<li>RM_Vekkaa</li>", "RM_Vekkaa"),
    ("payload: FindMod names another mod", "<li>RimMandrake: Acoustic Scanner</li>", "<li>RimMandrake: Acoustic Scanne</li>", "FindMod"),
    ("payload: biome typo", 'BiomeDef[defName="RM_Stillsand"]', 'BiomeDef[defName="RM_Stilsand"]', "RM_Stilsand"),
    ("payload: target matches nothing", "<hiddenCaves>true</hiddenCaves>", "", "matches nothing"),
    ("payload: no targets", "<targets>", "<targets></targets><unused>", "no targets"),
]


def payload_selftest():
    bad = 0
    known = L.defnames(os.path.join(L.REPO, "src"))
    name = L.about_name()
    text = open(PAYLOAD_SRC, encoding="utf-8").read()
    clean = L.check_payloads([PAYLOAD_SRC], known, name)
    print(("ok   " if not clean else "FAIL ") + "real Stillsand payload is clean" + ("" if not clean else " | " + clean[0][:140]))
    bad += bool(clean)
    tmp = tempfile.mkdtemp(prefix="acpayload_")
    try:
        for label, old, new, want in PAYLOAD_PLANTS:
            if text.count(old) < 1:
                print("FAIL %s: pattern not found" % label)
                bad += 1
                continue
            d = os.path.join(tmp, "Mod", "Patches")
            os.makedirs(d, exist_ok=True)
            p = os.path.join(d, "p.xml")
            body = text.replace(old, new, 1)
            if label == "payload: no targets":
                body = body.replace("</targets>", "</unused></targets>", 1) if False else text.replace(text[text.index("<targets>"):text.index("</targets>") + 10], "<targets></targets>", 1)
            open(p, "w", encoding="utf-8").write(body)
            errs = L.check_payloads([p], known, name)
            hit = any(want in e for e in errs)
            print(("ok   " if hit else "FAIL ") + label + ("" if hit else " | got %s" % (errs[:1] or "no errors")))
            bad += not hit
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return bad


if __name__ == "__main__":
    rc = H.run("AcousticScanner", "lint_acousticscanner_defs.py", PLANTS, keep=("Languages",))
    bad = payload_selftest()
    n = len(PAYLOAD_PLANTS) + 1
    print("acousticscanner payload planted-defect selftest: %d/%d ok" % (n - bad, n))
    sys.exit(1 if (rc or bad) else 0)
