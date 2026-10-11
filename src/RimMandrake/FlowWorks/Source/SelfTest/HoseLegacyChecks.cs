// Hose port step 2 gates (design v2 §6, FINAL §3.8-3.9): the type-name alias table and the one-time settings import, over
// RM_HoseLegacyMath.cs (the PRODUCTION file, compiled in directly). Each alias / import rule has a can-fail beside it.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.Hose;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseLegacyChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "hoselegacy: " + msg);

        private static string File(string cls, params (string k, string v)[] kv) =>
            "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<SettingsBlock>\n  <ModSettings Class=\"" + cls + "\">\n" +
            string.Concat(kv.Select(p => "    <" + p.k + ">" + p.v + "</" + p.k + ">\n")) + "  </ModSettings>\n</SettingsBlock>\n";

        public static void Run()
        {
            // ---- type alias (6.1): both old prefixes, the job-driver pair, unknown names untouched
            Check(RM_HoseLegacyMath.MapTypeName("RimMandrake.GimmeSomeSlack.Hose.Jobs.JobDriver_CarryHoseEnd") == "RimMandrake.FlowWorks.Hose.Jobs.JobDriver_CarryHoseEnd",
                  "alias: a GSS-era mid-carry driver resolves to FlowWorks'");
            Check(RM_HoseLegacyMath.MapTypeName("RimMandrake.GimmeSomeSlack.Hose.Jobs.JobDriver_RetractHose") == "RimMandrake.FlowWorks.Hose.Jobs.JobDriver_RetractHose",
                  "alias: a GSS-era mid-wind driver resolves to FlowWorks'");
            Check(RM_HoseLegacyMath.MapTypeName("RimMandrake.MessyConduit.Hose.Jobs.JobDriver_CarryHoseEnd") == "RimMandrake.FlowWorks.Hose.Jobs.JobDriver_CarryHoseEnd",
                  "alias: a MessyConduit-era driver resolves directly (works with GSS absent)");
            Check(RM_HoseLegacyMath.MapTypeName("RimMandrake.GimmeSomeSlack.RM_MapComponent_CordGraph") == null &&
                  RM_HoseLegacyMath.MapTypeName("RimMandrake.GimmeSomeSlack.Aerial.CompAerialAnchor") == null &&
                  RM_HoseLegacyMath.MapTypeName("RimMandrake.FlowWorks.Hose.CompHoseReel") == null &&
                  RM_HoseLegacyMath.MapTypeName("RimMandrake.GimmeSomeSlack.Hose.") == null && RM_HoseLegacyMath.MapTypeName(null) == null,
                  "alias: GSS's own cable/aerial types, already-new names, a bare prefix and null are untouched");
            // commutes with GSS's own MessyConduit -> GimmeSomeSlack rename: either order ends on the FlowWorks type
            string gssFirst = RM_HoseLegacyMath.MapTypeName("RimMandrake.GimmeSomeSlack.Hose.CompHoseReel");
            string fwFirst = RM_HoseLegacyMath.MapTypeName("RimMandrake.MessyConduit.Hose.CompHoseReel");
            Check(gssFirst == fwFirst && fwFirst == "RimMandrake.FlowWorks.Hose.CompHoseReel", "alias: the two renames commute");
            Check("RimMandrake.GimmeSomeSlack.Hose.CompHoseReel" != "RimMandrake.FlowWorks.Hose.CompHoseReel", "alias can-fail: without the map the old name does not resolve");

            // ---- def alias (6.2, step 4): the renamed pipe and its derived blueprint/frame, ThingDef only
            Check(RM_HoseLegacyMath.MapDefName("ThingDef", "RM_LiquidHose") == "RM_UniversalPipe" &&
                  RM_HoseLegacyMath.MapDefName("ThingDef", "Blueprint_RM_LiquidHose") == "Blueprint_RM_UniversalPipe" &&
                  RM_HoseLegacyMath.MapDefName("ThingDef", "Frame_RM_LiquidHose") == "Frame_RM_UniversalPipe",
                  "def alias: RM_LiquidHose and its blueprint/frame resolve to the universal pipe");
            Check(RM_HoseLegacyMath.MapDefName("TerrainDef", "RM_LiquidHose") == null && RM_HoseLegacyMath.MapDefName("ThingDef", "RM_HoseReel") == null &&
                  RM_HoseLegacyMath.MapDefName("ThingDef", "RM_UniversalPipe") == null && RM_HoseLegacyMath.MapDefName("ThingDef", null) == null,
                  "def alias: another def type, an unrenamed def, the new name and null are untouched");
            Check("RM_LiquidHose" != "RM_UniversalPipe", "def alias can-fail: without the table the saved name names no def");

            // ---- settings import (6.3): three file-name families, key copy, ignored Class=, missing file
            var now = new DateTime(2026, 10, 11, 12, 0, 0, DateTimeKind.Utc);
            var cands = new List<(string, DateTime)>
            {
                ("C:/cfg/Mod_GimmeSomeSlack_FireHosesMod.xml", now.AddDays(-1)),
                ("C:/cfg/Mod_MessyConduit_FireHosesMod.xml", now.AddDays(-9)),
                ("C:/cfg/Mod_3402011111_FireHosesMod.xml", now),
            };
            Check(RM_HoseLegacyMath.PickFile(cands, "GimmeSomeSlack", RM_HoseLegacyMath.HoseFileSuffix).EndsWith("Mod_GimmeSomeSlack_FireHosesMod.xml"),
                  "import: GSS loaded from folder GimmeSomeSlack picks that file even when another is newer");
            Check(RM_HoseLegacyMath.PickFile(cands, "3402011111", RM_HoseLegacyMath.HoseFileSuffix).EndsWith("Mod_3402011111_FireHosesMod.xml"),
                  "import: a Workshop install picks its id's file");
            Check(RM_HoseLegacyMath.PickFile(cands.Skip(1).Take(1).ToList(), null, RM_HoseLegacyMath.HoseFileSuffix).EndsWith("Mod_MessyConduit_FireHosesMod.xml"),
                  "import: GSS absent, a MessyConduit-era file alone is found");
            Check(RM_HoseLegacyMath.PickFile(cands, null, RM_HoseLegacyMath.HoseFileSuffix).EndsWith("Mod_3402011111_FireHosesMod.xml"),
                  "import: GSS absent, the newest file wins");
            Check(RM_HoseLegacyMath.PickFile(new List<(string, DateTime)>(), "GimmeSomeSlack", RM_HoseLegacyMath.HoseFileSuffix) == null,
                  "import: no file -> nothing to import (defaults kept)");

            string full = File("RimMandrake.GimmeSomeSlack.Hose.HoseSettings",
                ("enabled", "False"), ("minBendRadius", "1.8"), ("plumpAmount", "0.5"), ("transitionTicks", "60"), ("releaseTicks", "700"),
                ("minPlumpDwell", "300"), ("maxLength", "52"), ("maxLengthDefaults", "1"), ("couplingSpacing", "10"), ("handlingTime", "2"),
                ("windCellsPerSecond", "5"), ("autoResumeDroppedHose", "False"), ("slack", "1.5"), ("tintByContents", "False"),
                ("fillWobble", "False"), ("useFlowWorksPumps", "False"), ("defaultFluid", "RM_Fluid_Tar"));
            Dictionary<string, string> got = RM_HoseLegacyMath.HoseImport(full);
            Check(got.Count == 15 && RM_HoseLegacyMath.ImportedKeys.Length == 15 && RM_HoseLegacyMath.ImportedKeys.All(got.ContainsKey),
                  "import: the 15 surviving keys are copied (" + got.Count + ")");
            Check(!got.ContainsKey("useFlowWorksPumps") && !got.ContainsKey("defaultFluid"), "import: useFlowWorksPumps and defaultFluid are not imported");
            Check(got["maxLength"] == "52" && got["enabled"] == "False" && got["minBendRadius"] == "1.8", "import: values copied verbatim");
            string messy = File("RimMandrake.MessyConduit.Hose.HoseSettings", ("maxLength", "30"));
            Check(RM_HoseLegacyMath.HoseImport(messy).Count == 1 && RM_HoseLegacyMath.HoseImport(messy)["maxLength"] == "30",
                  "import: the Class= value is ignored (a MessyConduit-era file reads the same way)");
            Check(RM_HoseLegacyMath.HoseImport("not xml <").Count == 0 && RM_HoseLegacyMath.HoseImport("<a/>").Count == 0,
                  "import: a damaged or foreign file imports nothing");
            int all = RM_HoseLegacyMath.ReadKeys(full).Count;
            Check(all == 17, "import can-fail: a copy-everything import would carry " + all + " keys, two of them dead");

            // ---- look import (G2.2): GSS's global style seeds the reel default look by the 4-row LookOf table
            Check(RM_HoseLegacyMath.LookFromCordSettings(File("RimMandrake.GimmeSomeSlack.GimmeSomeSlackSettings", ("style", "ExtensionCord"))) == "Modern" &&
                  RM_HoseLegacyMath.LookFromCordSettings(File("x", ("style", "Cybertek"))) == "Futuristic" &&
                  RM_HoseLegacyMath.LookFromCordSettings(File("x", ("style", "StarWars"))) == "Industrial" &&
                  RM_HoseLegacyMath.LookFromCordSettings(File("x", ("style", "StarWarsJawa"))) == "Scrapper",
                  "look import: the four GSS styles map to the four looks");
            Check(RM_HoseLegacyMath.LookFromCordSettings(File("x", ("enabled", "True"))) == "Scrapper" && RM_HoseLegacyMath.LookFromCordSettings(null) == "Scrapper" &&
                  RM_HoseLegacyMath.LookFromCordSettings(File("x", ("style", "Gold"))) == "Scrapper",
                  "look import: no style key, no file, or an unknown style -> Scrapper (GSS's own default)");
            Check(RM_HoseLegacyMath.LookOfCordStyle("StarWars") != "Scrapper", "look import can-fail: 'always Scrapper' would change an Industrial player's reels");
            Check(HoseStyles.Looks.All(l => HoseStyles.IsLook(l)) && HoseStyles.Looks.Length == 4 &&
                  new[] { "StarWarsJawa", "StarWars", "ExtensionCord", "Cybertek" }.Select(RM_HoseLegacyMath.LookOfCordStyle).Distinct().Count() == 4,
                  "look import: every mapped look is one of FlowWorks' four, all four reachable");
        }
    }
}
