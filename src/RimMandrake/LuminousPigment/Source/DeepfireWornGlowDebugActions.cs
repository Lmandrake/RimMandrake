using System.Collections.Generic;
using System.Globalization;
using System.Text;
using LudeonTK;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_WORN_GLOW_1: dev-menu tools for this item's quicktest
    // (src/RimMandrake/bridgetools/prove_deepfire_worn_glow.py), same shape
    // as DeepfireFloorDebugActions / DeepfireFirstCoatDebugActions -- every
    // action is a ToolMap action (rimworld/execute_debug_action with x/z;
    // the report actions ignore the cell) and writes exactly one
    // "[DeepfireWorn] {json}" log line. Coats go through CompDeepfire.AddCoat
    // and wearing through Pawn_ApparelTracker.Wear, i.e. the real
    // Notify_Equipped path; the styling test queues the real job via
    // StylingStationLacquer.QueueLacquer (the dialog's own Accept entry point).
    // In 1.6 these show flat under Actions as "T: WornGlow: ...".
    public static class DeepfireWornGlowDebugActions
    {
        private const string Tag = "[DeepfireWorn] ";
        private const int StripLength = 34;       // the walk is 30 cells; margin for the light
        private const int StripHalfWidth = 3;
        private const int WalkCells = 30;
        private const int TestCoats = 3;          // brightest: glow stays > 0.3 one cell off the proxy
        private const int HitPairs = 20;          // spawn-many-for-bridge-tests
        private const int HitTwinOffset = 8;      // twins sit symmetric about the shooter
        private const int HitAreaHalf = 10;

        private static Pawn walker;
        private static Pawn styler;
        private static Apparel stylerParka;
        private static Thing styleStation;

        // ---- setup ----

        [DebugAction("Deepfire", "WornGlow: roof dark strip east of cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void RoofStrip()
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            CellRect rect = new CellRect(c.x - 2, c.z - StripHalfWidth, StripLength + 2, 2 * StripHalfWidth + 1).ClipInsideMap(map);
            Roof(map, rect);
            map.glowGrid.GlowGridUpdate_First();
            Log.Message(Tag + "{\"action\":\"roofStrip\",\"cells\":" + rect.Area
                + ",\"baselineGlow\":" + F(map.glowGrid.GroundGlowAt(c)) + "}");
        }

        [DebugAction("Deepfire", "WornGlow: spawn coated walker at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void SpawnWalker()
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            if (walker != null && !walker.Destroyed) walker.Destroy();
            walker = SpawnColonist(map, c, TestCoats);
            Log.Message(Tag + ReportPawn(walker, "spawnWalker"));
        }

        [DebugAction("Deepfire", "WornGlow: walker walk 30 east", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void WalkEast()
        {
            if (walker == null || !walker.Spawned) { Log.Message(Tag + "{\"action\":\"walk\",\"found\":false}"); return; }
            IntVec3 dest = walker.Position + new IntVec3(WalkCells, 0, 0);
            if (walker.drafter != null) walker.drafter.Drafted = true;
            bool ok = walker.jobs.TryTakeOrderedJob(JobMaker.MakeJob(JobDefOf.Goto, dest), JobTag.Misc);
            Log.Message(Tag + "{\"action\":\"walk\",\"found\":true,\"ordered\":" + B(ok)
                + ",\"destX\":" + dest.x + ",\"destZ\":" + dest.z + "}");
        }

        [DebugAction("Deepfire", "WornGlow: report walker", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void ReportWalker()
        {
            if (walker == null) { Log.Message(Tag + "{\"action\":\"reportWalker\",\"found\":false}"); return; }
            if (walker.Spawned) walker.Map.glowGrid.GlowGridUpdate_First();
            Log.Message(Tag + ReportPawn(walker, "reportWalker"));
        }

        [DebugAction("Deepfire", "WornGlow: strip walker's coats", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void StripWalker()
        {
            if (walker == null) { Log.Message(Tag + "{\"action\":\"stripWalker\",\"found\":false}"); return; }
            foreach (ThingWithComps t in WornGlowUtility.WornAndEquipped(walker)) t.GetComp<CompDeepfire>()?.RemoveAllCoats();
            if (walker.Spawned) walker.Map.glowGrid.GlowGridUpdate_First();
            Log.Message(Tag + ReportPawn(walker, "stripWalker"));
        }

        // ---- combat: 20 fresh pairs, HitReportFor compared directly ----

        [DebugAction("Deepfire", "WornGlow: 20 hit-report pairs at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void HitPairsAtCell()
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            Roof(map, CellRect.CenteredOn(c, HitAreaHalf).ClipInsideMap(map));

            Pawn shooter = SpawnColonist(map, c, 0);
            ThingWithComps rifle = (ThingWithComps)ThingMaker.MakeThing(ThingDef.Named("Gun_AssaultRifle"));
            shooter.equipment.AddEquipment(rifle);
            Verb verb = shooter.equipment.PrimaryEq.PrimaryVerb;

            IntVec3 coatedCell = c + new IntVec3(HitTwinOffset, 0, 0);
            IntVec3 plainCell = c - new IntVec3(HitTwinOffset, 0, 0);
            CultureInfo inv = CultureInfo.InvariantCulture;
            var rows = new List<string>();
            int coatedHigher = 0, readoutLines = 0, darkCount = 0, dodgeLower = 0, dodgeExplained = 0;
            for (int i = 0; i < HitPairs; i++)
            {
                Pawn coated = SpawnColonist(map, coatedCell, TestCoats);
                Pawn plain = SpawnColonist(map, plainCell, 0);
                map.glowGrid.GlowGridUpdate_First();

                ShotReport rc = ShotReport.HitReportFor(shooter, verb, coated);
                ShotReport rp = ShotReport.HitReportFor(shooter, verb, plain);
                bool dark = DeepfireDarkness.IsGlowingInDark(coated);
                string readout = rc.GetTextReadout();
                bool line = readout.Contains(Patch_ShotReport_GetTextReadout.LineLabel.CapitalizeFirst());

                // DEEPFIRE_DODGE_PROOF_TWINS_1: compare the SAME pawn's
                // MeleeDodgeChance coated vs stripped, not two independently
                // generated twins. `coated` and `plain` are both random
                // colonists (PawnGenerator) -- their Melee skill level,
                // passion and traits (Nimble etc.) are NOT matched, so the
                // "plain" twin's base dodge can legitimately sit above the
                // coated twin's regardless of the coat. Live 2026-09-30: 1/20
                // pairs read dodgeCoated 0.02 > dodgePlain 0, which is a
                // skill mismatch, not the -0.08 penalty failing to apply (it
                // applied and was explained in 20/20). Reading the coat's
                // effect off ONE pawn, before and after stripping it, makes
                // every other factor (skill, passion, traits, body size,
                // apparel, health) identical by construction.
                float dodgeC = coated.GetStatValue(StatDefOf.MeleeDodgeChance);
                string expl = StatDefOf.MeleeDodgeChance.Worker.GetExplanationFull(
                    StatRequest.For(coated), ToStringNumberSense.Absolute, dodgeC) ?? "";
                bool explained = expl.Contains(Patch_ShotReport_GetTextReadout.LineLabel.CapitalizeFirst());
                // GetStatValue is cached per-thing and nothing else dirties
                // that cache mid-tick (see jawa/stat_cache_bust's own
                // comment on why TryClearCache/ClearCacheForThing exist), so
                // stripping the coat and re-reading without clearing the
                // cache would silently hand back the pre-strip value.
                ParkaOf(coated)?.GetComp<CompDeepfire>()?.RemoveAllCoats();
                StatDefOf.MeleeDodgeChance.Worker.ClearCacheForThing(coated);
                float dodgeStripped = coated.GetStatValue(StatDefOf.MeleeDodgeChance);

                // DEEPFIRE_LIVE_FAILURES_1: vanilla factorFromTargetSize is
                // Clamp(target.BodySize, 0.5, 2) (RimSage Verse/ShotReport.cs),
                // and the twins are random colonists -- live 2026-09-30 a plain
                // twin at body size 0.8 read 0.3258 against 0.4072 for size 1.0,
                // and 2 of 20 pairs had a smaller coated twin. The x1.25 was
                // applied in every row (coated/plain = 1.25 exactly at equal
                // size); what differed was the pawns. Twins are now baseliner
                // adults, and the tally compares aim PER UNIT of each twin's own
                // clamped size, so a body-size gap cannot flip it.
                float sizeC = Mathf.Clamp(coated.BodySize, DeepfirePaintDefaults.TargetSizeFactorMin, DeepfirePaintDefaults.TargetSizeFactorMax);
                float sizeP = Mathf.Clamp(plain.BodySize, DeepfirePaintDefaults.TargetSizeFactorMin, DeepfirePaintDefaults.TargetSizeFactorMax);
                if (rc.AimOnTargetChance / sizeC > rp.AimOnTargetChance / sizeP) coatedHigher++;
                if (line) readoutLines++;
                if (dark) darkCount++;
                if (dodgeC < dodgeStripped || dodgeStripped <= 0f) dodgeLower++;
                if (explained) dodgeExplained++;
                rows.Add(string.Format(inv,
                    "{{\"coatedAim\":{0:0.####},\"plainAim\":{1:0.####},\"coatedTotal\":{2:0.####},\"plainTotal\":{3:0.####},\"dark\":{4},\"line\":{5},\"dodgeCoated\":{6:0.####},\"dodgeStripped\":{7:0.####},\"dodgeExplained\":{8},\"coatedSize\":{9:0.##},\"plainSize\":{10:0.##},\"coatedSizeFactor\":{11:0.####}}}",
                    rc.AimOnTargetChance, rp.AimOnTargetChance, rc.TotalEstimatedHitChance, rp.TotalEstimatedHitChance,
                    B(dark), B(line), dodgeC, dodgeStripped, B(explained), coated.BodySize, plain.BodySize,
                    Patch_ShotReport_HitReportFor.FactorFromTargetSize(ref rc)));

                coated.Destroy();
                plain.Destroy();
                // Drop the proxy now rather than at the next 15-tick poll, or
                // the next pair's coated twin stands in this one's light.
                MapComponent_DeepfireLights.MarkWornDirty(coated);
            }
            shooter.Destroy();

            var sb = new StringBuilder();
            sb.Append("{\"action\":\"hitPairs\",\"pairs\":").Append(HitPairs)
              .Append(",\"coatedHigher\":").Append(coatedHigher)
              .Append(",\"readoutLines\":").Append(readoutLines)
              .Append(",\"darkCount\":").Append(darkCount)
              .Append(",\"dodgeLowerOrZero\":").Append(dodgeLower)
              .Append(",\"dodgeExplained\":").Append(dodgeExplained)
              .Append(",\"rows\":[").Append(string.Join(",", rows)).Append("]}");
            Log.Message(Tag + sb);
        }

        // ---- styling station (spec §3.4 path 3) ----

        [DebugAction("Deepfire", "WornGlow: styling lacquer setup at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void StylingSetup()
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            if (styler != null && !styler.Destroyed) styler.Destroy();
            if (styleStation != null && !styleStation.Destroyed) styleStation.Destroy();

            ThingDef stationDef = ThingDef.Named(LacquerWornItemUtility.StylingStationDefName);
            styleStation = GenSpawn.Spawn(ThingMaker.MakeThing(stationDef, GenStuff.DefaultStuffFor(stationDef)), c, map, WipeMode.Vanish);
            styleStation.SetFaction(Faction.OfPlayer);

            Thing deepfire = ThingMaker.MakeThing(ThingDef.Named("RM_Deepfire"));
            deepfire.stackCount = LacquerWornItemUtility.CostFor(ThingMaker.MakeThing(ThingDef.Named("Apparel_Parka"), ThingDefOf.Cloth));
            GenPlace.TryPlaceThing(deepfire, c + new IntVec3(0, 0, -4), map, ThingPlaceMode.Near);

            styler = SpawnColonist(map, c + new IntVec3(3, 0, -3), 0);
            stylerParka = ParkaOf(styler);
            bool queued = StylingStationLacquer.QueueLacquer(styler, styleStation, stylerParka);
            Log.Message(Tag + ReportStyler("stylingSetup", queued));
        }

        [DebugAction("Deepfire", "WornGlow: report styler", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void StylingReport() => Log.Message(Tag + ReportStyler("reportStyler", true));

        [DebugAction("Deepfire", "WornGlow: cleanup test pawns", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void Cleanup()
        {
            if (walker != null && !walker.Destroyed) walker.Destroy();
            if (styler != null && !styler.Destroyed) styler.Destroy();
            if (styleStation != null && !styleStation.Destroyed) styleStation.Destroy();
            walker = styler = null;
            styleStation = null;
            stylerParka = null;
            Log.Message(Tag + "{\"action\":\"cleanup\"}");
        }

        // ---- helpers ----

        private static void Roof(Map map, CellRect rect)
        {
            foreach (IntVec3 cell in rect) map.roofGrid.SetRoof(cell, RoofDefOf.RoofConstructed);
        }

        private static Pawn SpawnColonist(Map map, IntVec3 c, int coats)
        {
            // Baseliner adults: every proof pawn the same body size (see HitPairsAtCell).
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDefOf.Colonist, Faction.OfPlayer,
                forcedXenotype: XenotypeDefOf.Baseliner, developmentalStages: DevelopmentalStage.Adult));
            GenSpawn.Spawn(p, c, map, WipeMode.Vanish);
            Apparel parka = (Apparel)ThingMaker.MakeThing(ThingDef.Named("Apparel_Parka"), ThingDefOf.Cloth);
            p.apparel.Wear(parka, dropReplacedApparel: false);
            CompDeepfire comp = parka.GetComp<CompDeepfire>();
            for (int i = 0; i < coats && comp != null; i++) comp.AddCoat();
            return p;
        }

        private static Apparel ParkaOf(Pawn p)
        {
            foreach (Apparel a in p.apparel.WornApparel) if (a.def.defName == "Apparel_Parka") return a;
            return null;
        }

        private static string ReportPawn(Pawn p, string action)
        {
            CultureInfo inv = CultureInfo.InvariantCulture;
            var sb = new StringBuilder();
            sb.Append("{\"action\":\"").Append(action).Append("\",\"found\":true");
            sb.Append(",\"spawned\":").Append(B(p.Spawned));
            sb.Append(",\"ticks\":").Append(Find.TickManager.TicksGame);
            if (p.Spawned)
            {
                Map map = p.Map;
                MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(map);
                IntVec3 pc = IntVec3.Invalid;
                bool tracked = mc != null && mc.TryGetWornProxyCell(p, out pc);
                sb.AppendFormat(inv, ",\"x\":{0},\"z\":{1},\"tracked\":{2},\"proxyX\":{3},\"proxyZ\":{4}",
                    p.Position.x, p.Position.z, B(tracked), pc.x, pc.z);
                sb.AppendFormat(inv, ",\"groundGlow\":{0:0.####},\"skyGlow\":{1:0.####},\"roofed\":{2},\"glowingInDark\":{3},\"wornLights\":{4}",
                    map.glowGrid.GroundGlowAt(p.Position), map.skyManager.CurSkyGlow, B(p.Position.Roofed(map)),
                    B(DeepfireDarkness.IsGlowingInDark(p)), mc != null ? mc.WornLightCount : -1);
                sb.AppendFormat(inv, ",\"job\":\"{0}\",\"moveSpeed\":{1:0.##}", p.CurJobDef?.defName ?? "",
                    p.GetStatValue(StatDefOf.MoveSpeed));
            }
            Apparel parka = ParkaOf(p);
            sb.AppendFormat(inv, ",\"coats\":{0}", parka?.GetComp<CompDeepfire>()?.coats ?? -1);
            sb.Append('}');
            return sb.ToString();
        }

        private static string ReportStyler(string action, bool queued)
        {
            if (styler == null) return "{\"action\":\"" + action + "\",\"found\":false}";
            Map map = styler.MapHeld;
            var sb = new StringBuilder();
            sb.Append("{\"action\":\"").Append(action).Append("\",\"found\":true,\"queued\":").Append(B(queued));
            sb.Append(",\"coats\":").Append(stylerParka?.GetComp<CompDeepfire>()?.coats ?? -1);
            sb.Append(",\"deepfireOnMap\":").Append(map != null ? StylingStationLacquer.AvailableDeepfire(map) : -1);
            sb.Append(",\"job\":\"").Append(styler.CurJobDef?.defName ?? "").Append('"');
            sb.Append(",\"queuedJobs\":").Append(styler.jobs?.jobQueue?.Count ?? 0);
            sb.Append(",\"ticks\":").Append(Find.TickManager.TicksGame);
            sb.Append('}');
            return sb.ToString();
        }

        private static string B(bool v) => v ? "true" : "false";
        private static string F(float v) => v.ToString("0.####", CultureInfo.InvariantCulture);
    }
}
