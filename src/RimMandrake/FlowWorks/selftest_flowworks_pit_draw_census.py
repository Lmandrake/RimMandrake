#!/usr/bin/env python3
"""Census of everything drawn outside the map-mesh print, against FlowWorks' one under-liquid law.

RIMMANDRAKE_SINK_HOSES_AND_OVERLAYS_TORCHES_BURN_IN_TAR (owner 2026-11-12, ~20:30: "a GSS connector unfortunately showing up
through the battery it should be beneath in a pit. This appears to be a common problem for the cooler and the Glowtank. The
wires are also above the items and furniture otherwise, likely all the same problem."). The law (RM_UnderLiquid) used to reach
only what SectionLayer_ThingsGeneral prints. Round 2 applies it by LAYER:
  * print      SectionLayer_ThingsGeneral.TakePrintFrom -> Printer_Plane split (unchanged);
  * realtime   Thing.DynamicDrawPhase gate: hidden under an opaque liquid, Graphic.DrawMeshInt drawn cut and faded, a
               Graphic_Flicker flame under the line is out (RM_SubmergeDraw.BeginRealtime / DrawRealtime / FlameShows);
  * overlays   OverlayDrawer.DrawOverlay (hidden) and every Render*(Thing ...) (depth set) with DrawBatch.DrawMesh (material
               faded after vanilla's own pulse fade) are seen as their thing's middle is (owner 2026-11-13 ~10:15 PM: "the Cooler
               still keeps its little red arrow icon above the surface"; ~10:25 PM: "put the yellow power disconnect icons under
               the water too when the item is under water");
  * order      a drowned part is its own colour whole under a liquid-coloured Silhouette cover (owner 2026-11-13 ~10 PM: "the
               vent looks on top of the water"); the cover is drawn in DrawOrder.DrownedQueue, above every ground-level cord /
               hose / clamp queue: what lies under a drowned thing stays under it. Flat things (vent, filth) print under the
               sheet, tinted as the floor; a sprite bigger than its cell is clipped to the pit's rim (~10:10 PM: "the chunks don't
               honor the pit, they overlap its edges unphysically");
  * cords      Gimme Some Slack's floor cords on a pit floor are faded by RM_SubmergeDraw.FloorSeen (found by name) and do
               not ripple per frame under liquid.
Every C# file in our mods that draws per frame (Graphics.DrawMesh, DrawMeshNow, a draw batch, or a Thing / comp / Graphic draw
override) must be in SITES below, ROUTED (which layer covers it) or LISTED (why the law does not apply, or the open gap). A new
draw site fails this test until it is classified; a classified file that no longer draws fails as stale. Vanilla's per-frame
drawers (RimSage census, decompiled 1.6) are pinned in VANILLA the same way.

Can-fail: --base REV reads the route pins from git REV (before round 2 they are absent: red); the built-in plants (an
unclassified site, a removed route) must go red every run.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, ".."))          # src/RimMandrake
REPO = os.path.normpath(os.path.join(SRC, "..", ".."))

DRAW = re.compile(r"Graphics\.DrawMesh|DrawMeshNow|drawBatch\.DrawMesh|DrawMeshNowOrLater|"
                  r"override void (DrawAt|PostDraw|DynamicDrawPhaseAt|DrawWorker)\(")
SKIP = ("/SelfTest/", "/obj/", "/bridgetools/", "/Tools/")

GATE = "ROUTED realtime gate: drawn inside its thing's DynamicDrawPhase (hidden under an opaque liquid; its Graphic draws " \
       "cut and faded; its own direct Graphics.DrawMesh is NOT faded in a clear liquid)"
SITES = {
    # the law and its own drawers
    "FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs": "ROUTED: the law itself (prints, pawns, realtime gate, overlays)",
    "FlowWorks/Source/Superdeep/RM_FlowDoors.cs": "ROUTED: DrawUnder (gates draw their own cut)",
    "FlowWorks/Source/Superdeep/RM_Spikes.cs": "ROUTED: DrawUnder (stakes draw their own cut)",
    "GimmeSomeSlack/Source/RM_MapComponent_CordGraph.cs": "ROUTED in part: a floor cord under liquid does not ripple, so it is "
        "printed and faded (CordUnderLiquid). LISTED gap: a lifted cord swaying per frame, the live glow, highlight and sparks",
    # above the liquid by design
    "FlowWorks/Source/RM_LiquidSurface.cs": "LISTED: the liquid's own surface (ripples, bubbles); it is the liquid",
    "FlowWorks/Source/Superdeep/RM_PitLipOcclusion.cs": "LISTED: the near bank drawn over the pit; it stands above the liquid",
    "FlowWorks/Source/Pits/Drawbridge/RM_DrawbridgeArt.cs": "LISTED: a drawbridge spans the pit at bank height (dry, like a deck)",
    "FlowWorks/Source/Pits/Suspension/RM_MapComponent_SuspensionBridges.cs": "LISTED: a suspension bridge spans the pit at "
        "bank height (dry)",
    "GimmeSomeSlack/Source/Aerial/RM_MapComponent_Aerial.cs": "LISTED: overhead span cables, above everything (OverheadQueue > DrownedQueue)",
    "Stillsand/Source/RM_StillsandWater.cs": "LISTED: a biome's own water surface, not a thing in a pit",
    "BiomesShell/Source/RM_WorldDecals.cs": "LISTED: the world map, not a local map",
    "CreatureBehaviors/Source/RM_Mirage.cs": "LISTED: an air effect (mirage), not a thing standing on a floor",
    "SolarMirrors/Source/RM_MapComponent_MirrorLight.cs": "LISTED: reflected light, a lighting effect",
    "AcousticScanner/Source/RM_MapComponent_AcousticReading.cs": "LISTED: a scanner reading overlay (player information)",
    "FlowWorks/Source/Superdeep/RM_PitDepthDraw.cs": "LISTED: the drafted-move destination ghost and circle (MetaOverlays), "
        "player information drawn over everything",
    # open gaps, each filed
    "FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs": "LISTED gap: a laid FlowWorks hose on a pit floor draws crisp "
        "(RIMMANDRAKE_FADE_LAID_HOSE_ON_PIT_FLOOR_LIKE_CORDS)",
    "FlowWorks/Source/Machinery/RM_LiquidJoins.cs": "LISTED gap: pipe joins drawn per frame by a map component; not routed "
        "(RIMMANDRAKE_FADE_LAID_HOSE_ON_PIT_FLOOR_LIKE_CORDS)",
    "FlowWorks/Source/Machinery/RM_UnderCouplers.cs": "LISTED gap: couplers drawn per frame; not routed "
        "(RIMMANDRAKE_FADE_LAID_HOSE_ON_PIT_FLOOR_LIKE_CORDS)",
    "RustCathedral/Source/Hum/RM_HullBolts.cs": "LISTED gap: drawn per frame by a map component; not routed (not a pit content mod)",
}
for f in ("BlueDesert/Source/RM_AblationSalvage.cs", "Contagion/Source/CompCloudRepulsor.cs", "Contagion/Source/RM_ContagionTellRender.cs",
          "CreatureBehaviors/Source/RM_Building_TractionLance.cs", "CreatureBehaviors/Source/RM_CompSalvageWinch.cs",
          "CreatureBehaviors/Source/RM_CompTetherPull.cs", "FlameStatues/Source/RM_FlamePoints.cs",
          "FlowWorks/Source/Drilling/Building_LiquidDrill.cs", "FlowWorks/Source/Hose/Graphic_HoseReel.cs",
          "FlowWorks/Source/Rivers/RM_FerryAndLevee.cs", "FlowWorks/Source/Rivers/RM_Weir.cs", "Scarlands/Source/RM_AerosolScreen.cs",
          "Scarlands/Source/RM_CompTurretAim.cs", "Scarlands/Source/RM_ReactionPools.cs", "TheSump/Source/RM_CapstanTurret.cs",
          "ExplosiveKnockback/Source/RM_ThingFlyer_Knockback.cs", "FlowWorks/Source/Pits/Drawbridge/RM_DrawbridgeControl.cs"):
    SITES[f] = GATE

VANILLA = {
    "Thing.DynamicDrawPhase (every realtime thing)": "ROUTED: the realtime gate",
    "Graphic.DrawWorker -> DrawMeshInt (Single, Multi, StackCount, Random, ...)": "ROUTED: DrawRealtime",
    "Graphic_Flicker.DrawWorker (torch, campfire, brazier, darklight flames)": "ROUTED: a flame under the line is out",
    "Book (RealtimeOnly by the ThingDef default)": "ROUTED: the realtime gate (item, 0.3 m)",
    "Corpse / Pawn DynamicDrawPhaseAt": "ROUTED: gate (hidden under opaque) + CoverPawn (LayingFacing, body position)",
    "Building_HoldingPlatform / GrowthVat / GeneExtractor / GibbetCage / SubcoreScanner DynamicDrawPhaseAt": GATE,
    "OverlayDrawer (power off, needs power, broken down, out of fuel, forbidden, ...)": "ROUTED: DrawOverlay + every Render*(Thing) + "
        "DrawBatch.DrawMesh (OVERLAY_PATHS)",
    "Building_SteamGeyser (the vent print)": "ROUTED: flat, printed under the sheet (UnderSheetMat), tinted as the floor",
    "PawnFlyer DynamicDrawPhaseAt": "LISTED: in flight, above any liquid",
    "Motes, flecks, gas (Graphic_Mote*, Graphic_Fleck, Graphic_Gas)": "LISTED: air effects, not standing things",
    "SilhouetteUtility (zoomed-out silhouettes)": "LISTED: a zoom-out aid drawn over everything, like a label backdrop",
    "MinifiedThing (MapMeshOnly)": "ROUTED: the print split (crate and content planes)",
}

# Every icon OverlayDrawer can put on a thing (RimWorld 1.6 decompile, OverlayDrawer: each Render* takes the Thing first) and
# DrawBatch.DrawMesh, where each lands. Patch_RM_SubmergeOverlayRender takes them by reflection (every Render* whose first
# parameter is a Thing), so one added by a later version is covered too; this list names them (owner ~10:25 PM).
OVERLAY_PATHS = {
    "RenderNeedsPowerOverlay": "yellow bolt: needs power (owner ~10:25 PM)",
    "RenderPowerOffOverlay": "yellow bolt crossed: power off (owner ~10:25 PM)",
    "RenderBrokenDownOverlay": "broken down",
    "RenderRechargineOverlay": "recharging",
    "RenderOutOfFuelOverlay": "out of fuel",
    "RenderPulsingOverlay": "the pulsing icons' entry (two overloads)",
    "RenderPulsingOverlayInternal": "the pulse fade (vanilla re-fades after ours: hence the DrawBatch swap)",
    "RenderForbiddenRefuelOverlay": "forbidden to refuel",
    "RenderForbiddenAtomizerOverlay": "forbidden atomizer",
    "RenderForbiddenOverlay": "forbidden",
    "RenderForbiddenBigOverlay": "forbidden (big)",
    "RenderBurningWick": "a lit wick",
    "RenderQuestionMarkOverlay": "question mark",
    "DrawBatch.DrawMesh": "where every one above lands: the material faded with its thing",
    "Building_Cooler / Building_Vent texture arrow": "part of the sprite: a wall slot, drawn 1 m high (WallSlotMetres)",
    "GSS unplugged marker": "none exists in Gimme Some Slack (grep, 2026-11-13)",
}

# Thing classes in a liquid cell: ROUTED (the one tint) or LISTED (why not). Owner ~10:10 PM: "The ancient shopping Cart isn't
# shown as under the water. Not sure if the chunks are either."
THING_CLASSES = {
    "Item (chunks, stacks, books)": "ROUTED: print split, own whole + liquid cover; rim-clipped",
    "Building (carts, furniture, machines)": "ROUTED: print split, own whole + liquid cover; rim-clipped south/east/west",
    "Building_Cooler, Building_Vent": "ROUTED: wall slot, 1 m",
    "Filth, Building_SteamGeyser": "ROUTED: flat, under the sheet",
    "Plant wholly under": "ROUTED: print split by its drawn height",
    "Plant partly under": "LISTED: drawn as vanilla draws it above its cut",
    "Pawn, Corpse": "ROUTED: CoverPawn",
    "realtime things": "ROUTED: gate + DrawRealtime cover; LISTED: not rim-clipped",
    "Projectile, Gas, Attachment, Mote, Ethereal, PsychicEmitter": "LISTED: in the air or not a standing thing",
    "GSS floor cords": "LISTED gap: CordUnderLiquid.Faded keeps the own-alpha fade (no liquid colour)",
}

ROUTES = [  # (file, pattern, what)
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"\[HarmonyPatch\(typeof\(Thing\), nameof\(Thing\.DynamicDrawPhase\)\)\]", "realtime gate patch"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"return RM_SubmergeDraw\.BeginRealtime\(__instance, phase\)", "gate decides"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"phase != DrawPhase\.Draw", "gate stays off the parallel pre-draw"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"\[HarmonyPatch\(typeof\(Graphic\), \"DrawMeshInt\"\)\]", "realtime mesh fade"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"\[HarmonyPatch\(typeof\(Graphic_Flicker\), nameof\(Graphic_Flicker\.DrawWorker\)\)\]", "flame out"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"\[HarmonyPatch\(typeof\(OverlayDrawer\), nameof\(OverlayDrawer\.DrawOverlay\)\)\]", "overlay hide"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"m\.Name\.StartsWith\(\"Render\"\) && !m\.IsStatic && ps\.Length > 0 && ps\[0\]\.ParameterType == typeof\(Thing\)",
     "every OverlayDrawer.Render*(Thing) sets the depth"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"m\.Name == nameof\(DrawBatch\.DrawMesh\) && ps\.Length > 2 && ps\[2\]\.ParameterType == typeof\(Material\)",
     "every DrawBatch.DrawMesh fades the icon after vanilla's pulse"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"RM_UnderLiquid\.OverlayAlpha\(", "an icon is seen as its thing's middle"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"ShaderDatabase\.Silhouette,", "the drowned cover is a Silhouette"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"RM_UnderLiquid\.CoverAlpha\(q\)", "cover alpha 1 - Seen"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"RM_FaceMaterial\.UnderSheetQueue", "flat things under the sheet"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"ctxClip \? RM_UnderLiquid\.ClipQuad\(", "the rim clip"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"t is Building_Cooler \|\| t is Building_Vent", "the wall slot"),
    ("FlowWorks/Source/Superdeep/RM_GeyserPit.cs", r"GetNamedSilentFail\(\"RM_Fleck_VentBubble\"\)", "the plume throws the vent bubble"),
    ("FlowWorks/Source/Superdeep/RM_GeyserPit.cs", r"RM_GeyserTubMath\.PlumeRate\(RM_GeyserPitSettings\.geyserPlumeEnabled,", "the plume switch"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"\{ renderQueue = DrownedQueue \}", "drowned parts in the drowned queue"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"r\.LayingFacing\(\)", "corpse cover faces as the body does"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"Vector3 body = r\.SilhouettePos;", "corpse cover sits where the body is"),
    ("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"public static float FloorSeen\(Map map, int x, int z\)", "the cord hook"),
    ("_Shared/SlackGeometry/DrawOrder.cs", r"DrownedQueue\(int strandQueue\) => Math\.Max\(HoseQueue\(strandQueue\), TapClampQueue\(strandQueue\)\) \+ 1",
     "drowned queue above every ground rope queue"),
    ("_Shared/SlackGeometry/DrawOrder.cs", r"OverheadQueue\(int strandQueue\) => DrownedQueue\(strandQueue\) \+ 1", "spans above drowned parts"),
    ("GimmeSomeSlack/Source/CordUnderLiquid.cs", r"\"RimMandrake\.FlowWorks\.RM_SubmergeDraw:FloorSeen\", new\[\] \{ typeof\(Map\), typeof\(int\), typeof\(int\) \}",
     "GSS finds the hook by its exact name and signature"),
    ("GimmeSomeSlack/Source/SectionLayer_RM_MessyCords.cs", r"int rn = WetRibbon\(", "the cord strand is faded"),
    ("GimmeSomeSlack/Source/SectionLayer_RM_MessyCords.cs", r"verts \+= WetRibbon\(CordMaterials\.Shadow", "its shadow is faded"),
    ("GimmeSomeSlack/Source/SectionLayer_RM_MessyCords.cs", r"m = CordUnderLiquid\.Faded\(m, CordUnderLiquid\.StepAt\(Map, d\.Pos\.X, d\.Pos\.Z\)\)",
     "plugs and connectors are faded"),
    ("GimmeSomeSlack/Source/RM_MapComponent_CordGraph.cs", r"CordUnderLiquid\.SeenAt\(map, c\.x, c\.z\) >= 1f", "a cord under liquid does not ripple"),
]


def read(rel, rev=None):
    if rev:
        r = subprocess.run(["git", "-C", REPO, "show", rev + ":src/RimMandrake/" + rel], capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else ""
    p = os.path.join(SRC, rel)
    return open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else ""


def hits():
    out = []
    for root, _, files in os.walk(SRC):
        for f in files:
            if not f.endswith(".cs"):
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, SRC).replace(os.sep, "/")
            if any(s in "/" + rel for s in SKIP):
                continue
            if DRAW.search(open(p, encoding="utf-8", errors="replace").read()):
                out.append(rel)
    return sorted(out)


def check(found, sites, routes, rev=None):
    bad = []
    if len(found) < 10:
        bad.append("the census saw only %d draw sites (blind instrument?)" % len(found))
    for f in found:
        if f not in sites:
            bad.append("UNCLASSIFIED draw site: %s (route it through the law or list it with a reason)" % f)
    for f in sites:
        if f not in found:
            bad.append("STALE: %s no longer draws per frame (drop its row)" % f)
    for f, pat, what in routes:
        if not re.search(pat, read(f, rev)):
            bad.append("ROUTE MISSING (%s): %s  [%s]" % (what, f, pat))
    for k, v in VANILLA.items():
        if not (v.startswith("ROUTED") or v.startswith("LISTED")):
            bad.append("vanilla row without a class: " + k)
    return bad


def bubble_art():
    """RM_Fleck_VentBubble and its art (owner 2026-11-13: "too large and too transparent"): small, short-lived, opaque."""
    bad = []
    xml = read("FlowWorks/Defs/LiquidTypes/FleckDefs/RM_LiquidBubble.xml")
    m = re.search(r"<defName>RM_Fleck_VentBubble</defName>(.*?)</FleckDef>", xml, re.S)
    if not m:
        return ["RM_Fleck_VentBubble is not defined"]
    body = m.group(1)
    def num(tag):
        g = re.search(r"<%s>([0-9.]+)</%s>" % (tag, tag), body)
        return float(g.group(1)) if g else None
    life = sum(num(t) or 0.0 for t in ("fadeInTime", "solidTime", "fadeOutTime"))
    size = num("drawSize")
    if not (0.3 <= life <= 0.8):
        bad.append("vent bubble life %.2f s outside 0.3..0.8" % life)
    if size is None or not (0.08 <= size <= 0.15):
        bad.append("vent bubble drawSize %s outside 0.08..0.15 (before 0.18 x 1.5..2.2)" % size)
    if "Graphic_FleckPulse" in body:
        bad.append("vent bubble pulses its alpha (Graphic_FleckPulse): it must stay solid")
    tex = re.search(r"<texPath>([^<]+)</texPath>", body)
    png = os.path.join(SRC, "FlowWorks", "Textures", (tex.group(1) if tex else "") + ".png")
    if not os.path.exists(png):
        return bad + ["vent bubble art missing: " + png]
    from PIL import Image
    a = list(Image.open(png).convert("RGBA").getchannel("A").tobytes())
    cov = [v for v in a if v > 0]
    mean = sum(cov) / len(cov) / 255.0 if cov else 0.0
    if mean < 0.75:
        bad.append("vent bubble art mean alpha %.2f < 0.75 (vanilla VatBubble ~0.29: ghost bubbles)" % mean)
    if max(a) < 250:
        bad.append("vent bubble art has no opaque rim")
    return bad + sunk_vent_art()


def sunk_vent_art():
    """Round 7 (owner: "the vent looks on top of the water"): the sunk vent is a soft dark hole with no pale ring, and the
    froth ring a soft white ring about a square across."""
    bad = []
    from PIL import Image
    png = os.path.join(SRC, "FlowWorks", "Textures", "Things", "Building", "RM_SunkVent.png")
    if not os.path.exists(png):
        return ["sunk vent art missing: " + png]
    im = Image.open(png).convert("RGBA")
    w, h = im.size
    px = im.load()
    if px[w // 2, h // 2][3] < 216:
        bad.append("sunk vent: the hole's centre is not dark and solid")
    if max(px[0, 0][3], px[w - 1, 0][3], px[0, h - 1][3], px[w - 1, h - 1][3]) > 0:
        bad.append("sunk vent: hard square edge (corners not clear)")
    bright = max((max(p[:3]) for p in im.getdata() if p[3] > 10), default=0)
    if bright > 70:
        bad.append("sunk vent: a pale ring (a visible pixel at %d/255)" % bright)
    xml = read("FlowWorks/Defs/LiquidTypes/FleckDefs/RM_LiquidBubble.xml")
    if "<defName>RM_Fleck_VentFroth</defName>" not in xml:
        bad.append("RM_Fleck_VentFroth is not defined")
    if not os.path.exists(os.path.join(SRC, "FlowWorks", "Textures", "Things", "Mote", "RM_VentFroth.png")):
        bad.append("froth art missing")
    return bad


def main(argv):
    rev = argv[argv.index("--base") + 1] if "--base" in argv else None
    found = hits()
    bad = check(found, SITES, ROUTES, rev)
    bad += [] if rev else bubble_art()
    for k, v in list(OVERLAY_PATHS.items()) + list(THING_CLASSES.items()):
        if not v:
            bad.append("unnamed path: " + k)
    # plants: each must go red
    plants = {
        "an unclassified draw site": check(found + ["Planted/Source/RM_NewOverlay.cs"], SITES, ROUTES),
        "a removed route": check(found, SITES, ROUTES + [("FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs", r"NO_SUCH_ROUTE_PLANTED", "planted")]),
        "a stale row": check(found, dict(SITES, **{"Gone/Source/RM_Gone.cs": GATE}), ROUTES),
    }
    for name, res in plants.items():
        if not res:
            bad.append("CAN-FAIL: the plant (%s) stayed green" % name)
    routed = sum(1 for v in list(SITES.values()) + list(VANILLA.values()) if v.startswith("ROUTED"))
    listed = sum(1 for v in list(SITES.values()) + list(VANILLA.values()) if not v.startswith("ROUTED"))
    print("pit draw census: %d draw sites in our mods, %d vanilla rows; %d routed, %d listed; %d route pins; %d overlay paths; "
          "%d thing classes%s" % (len(found), len(VANILLA), routed, listed, len(ROUTES), len(OVERLAY_PATHS), len(THING_CLASSES),
                                  " (base " + rev + ")" if rev else ""))
    for k, v in THING_CLASSES.items():
        if not v.startswith("ROUTED: ") or "LISTED" in v:
            print("  listed: %s -- %s" % (k, v))
    for b in bad:
        print("FAIL " + b)
    print("PASS" if not bad else "FAILED (%d)" % len(bad))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
