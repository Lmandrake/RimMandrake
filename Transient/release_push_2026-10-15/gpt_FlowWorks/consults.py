#!/usr/bin/env python3
"""FlowWorks pre-release GPT consults: slice manifest + parallel runner (BENCH, 2026-10-15).

    python3 consults.py sizes            # chars per slice
    python3 consults.py run C1 C2 ...    # run those slices in parallel (gpt_consult.py, --timeout 585)
"""
import glob, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
FW = "src/RimMandrake/FlowWorks/"
S = FW + "Source/"
DS = "design/RimMandrake/"
COMMON = [str(HERE.relative_to(ROOT) / "dossier/00_brief.md"), str(HERE.relative_to(ROOT) / "dossier/known_behaviours.md"),
          DS + "gss_flowworks_rulings_2026-10-11.md", S + "RimMandrakeFlowWorks_DefOf.cs"]

def g(*pats):
    out = []
    for p in pats:
        hits = sorted(glob.glob(str(ROOT / p), recursive=True))
        if not hits:
            sys.exit("no match: " + p)
        out += [str(Path(h).relative_to(ROOT)) for h in hits if "/obj/" not in h and "/SelfTest/" not in h]
    return out

M = S + "Machinery/"
SLICES = {
 "C1": ("liquid network core: pipes, liquid net + kernel, transfer service, spill, theft, adapters, converters, kits, sluice gate, ruins",
        [DS + "liquid_network_semantics_design_2026-10-11.md"],
        g(M + "*.cs", M + "Kits/*.cs", M + "Logistics/*.cs", S + "RM_PumpMath.cs", S + "RM_Volume.cs", S + "FluidDef.cs", S + "RM_FluidIdentity.cs")),
 "C2": ("liquids, tanks (incl. tall tank), pumps, bottles/containers, the source stock model, drilling",
        [DS + "liquids_framework_design.md"],
        g(S + "LiquidTypes/*.cs", S + "RM_LiquidStock.cs", S + "RM_StockMath.cs", S + "Drilling/*.cs")),
 "C3": ("superdeep pits: cliff masks, pocket grid, pit pathing/step cost, ladders, pit rooms, flow doors, traps, walls, lip occlusion",
        ["infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md"],
        g(S + "Superdeep/*.cs")),
 "C4": ("pit math + covers + exposure + superdeep shooting + liquid fire/heat",
        [DS + "flowworks_pits_unified_model_2026-10-02.md", DS + "pit_exposure_to_the_elements_2026-10-11.md"],
        g(S + "Pits/**/*.cs", S + "RM_PocketGridMath.cs", S + "RM_PitRoomMath.cs", S + "RM_PitTrapMath.cs", S + "RM_PitDrawMath.cs",
          S + "RM_PitExposure.cs", S + "RM_PitExposureMath.cs", S + "RM_PitFillEffects.cs", S + "RM_Patch_SuperdeepShooting.cs",
          S + "RM_WallFaceMath.cs", S + "RM_CliffMaskMath.cs", S + "RM_LiquidFire.cs", S + "RM_LiquidHeat.cs", S + "RM_FireMath.cs",
          S + "RM_LiquidHeatMath.cs")),
 "C5": ("excavation map component (depth/fill grid, dig/fill-in, displacement), flow kernel, canals, ponds/lakebeds as bodies, liquid surface/looks, swale, taken-by-land, quarry/placer, flood",
        [DS + "natural_bodies_as_canals_design_2026-10-11.md"],
        g(S + "RM_MapComponent_Excavation.cs", S + "RM_FlowKernel.cs", S + "*Canal*.cs", S + "RM_DigDiscovery*.cs", S + "RM_FillEffectMath.cs",
          S + "RM_ExcavationDepth.cs", S + "RM_ExcavationSanityMath.cs", S + "RM_LiquidBody.cs", S + "RM_LiquidSurface.cs", S + "RM_WakeMath.cs",
          S + "Swale/*.cs", S + "TakenByLand/*.cs", S + "Quarry/*.cs", S + "Flood_FlowWorks.cs")),
 "C6": ("rivers (weir, ferry rope + levee, river current/swept away, silt, river works), many waters (river steam, swim), and the main Mod Settings class",
        [DS + "surface_river_weirs_design_2026-10-02.md", DS + "river_works_mod_design_2026-10-03.md"],
        g(S + "Rivers/*.cs", S + "ManyWaters/*.cs", S + "RimMandrakeFlowWorksMod.cs")),
 "C7": ("hoses A: hose map component, reel comp, carry, jobs, relay/live/flow/ends/ports, hose settings",
        [DS + "hose_port_to_flowworks_design_FINAL_2026-10-10.md"],
        g(S + "Hose/RM_MapComponent_Hoses.cs", S + "Hose/CompHoseReel.cs", S + "Hose/HoseCarry.cs", S + "Hose/Jobs/*.cs",
          S + "Hose/HoseRelay.cs", S + "Hose/HoseLive.cs", S + "Hose/HoseFlow.cs", S + "Hose/HoseEnds.cs", S + "Hose/HosePorts.cs",
          S + "Hose/RM_HoseSettings.cs")),
 "C8": ("hoses B (hose math, probes, legacy migration, styles/looks) + debug actions + in-game proof hooks + liquid looks",
        [],
        g(S + "Hose/HoseMath.cs", S + "Hose/HoseProbe.cs", S + "Hose/RM_HoseLegacy*.cs", S + "Hose/HoseNetProbe.cs", S + "Hose/HoseStyle*.cs",
          S + "Hose/HoseLook.cs", S + "Hose/Graphic_HoseReel.cs", S + "Hose/ReelIntakeGeometry.cs", S + "Debug/*.cs",
          S + "RM_NorthstarProofs.cs", S + "RM_PromotionProofs.cs", S + "RM_LiquidLooks.cs")),
 "C9": ("XML: About, all Patches, all Defs except the generated liquid/canal TerrainDefs (one sample of each kept), plus the csproj",
        [],
        g(FW + "About/About.xml", FW + "Patches/**/*.xml", S + "RimMandrake_FlowWorks.csproj")
        + [p for p in g(FW + "Defs/**/*.xml") if "LiquidTypes/TerrainDefs" not in p and "Canals/TerrainDefs" not in p]
        + g(FW + "Defs/LiquidTypes/TerrainDefs/*.xml")[:1] + g(FW + "Defs/Canals/TerrainDefs/*.xml")[:1]),
}

# C7/C8 timed out at 585 s on 2026-10-15; split.
SLICES["C7a"] = ("hoses A1: hose map component, relay/live/flow/ends/ports", [DS + "hose_port_to_flowworks_design_FINAL_2026-10-10.md"],
        g(S + "Hose/RM_MapComponent_Hoses.cs", S + "Hose/HoseRelay.cs", S + "Hose/HoseLive.cs", S + "Hose/HoseFlow.cs", S + "Hose/HoseEnds.cs", S + "Hose/HosePorts.cs"))
SLICES["C7b"] = ("hoses A2: reel comp, carry, hose jobs/work giver/float menu, hose settings", [DS + "hose_port_to_flowworks_design_FINAL_2026-10-10.md"],
        g(S + "Hose/CompHoseReel.cs", S + "Hose/HoseCarry.cs", S + "Hose/Jobs/*.cs", S + "Hose/RM_HoseSettings.cs"))
SLICES["C8a"] = ("hoses B1: hose math and legacy save migration", [],
        g(S + "Hose/HoseMath.cs", S + "Hose/RM_HoseLegacy*.cs"))
SLICES["C8b"] = ("hoses B2: hose probes, styles/looks, debug actions, in-game proof hooks, liquid looks", [],
        g(S + "Hose/HoseProbe.cs", S + "Hose/HoseNetProbe.cs", S + "Hose/HoseStyle*.cs", S + "Hose/HoseLook.cs", S + "Hose/Graphic_HoseReel.cs",
          S + "Hose/ReelIntakeGeometry.cs", S + "Debug/*.cs", S + "RM_NorthstarProofs.cs", S + "RM_PromotionProofs.cs", S + "RM_LiquidLooks.cs"))

def files(k):
    title, design, src = SLICES[k]
    return title, COMMON + design + src

def size(k):
    return sum((ROOT / f).stat().st_size for f in files(k)[1])

def main(a):
    if a[0] == "sizes":
        for k in SLICES:
            print(k, size(k), len(files(k)[1]))
        return
    tmpl = (HERE / "q_common.md").read_text()
    procs = []
    for k in a[1:]:
        title, fs = files(k)
        q = HERE / ("q_%s.md" % k)
        q.write_text(tmpl.replace("{SLICE}", title))
        cmd = ["python3", "src/RimMandrake/Utils/gpt_consult.py", "--prompt-file", str(q), "--out", str(HERE / ("answer_%s.md" % k)),
               "--timeout", "585"] + sum((["-f", f] for f in fs), [])
        procs.append((k, subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)))
    for k, p in procs:
        _, err = p.communicate()
        print(k, "rc", p.returncode, (err or "").strip().splitlines()[-1:] )

if __name__ == "__main__":
    main(sys.argv[1:])
