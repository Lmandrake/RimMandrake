using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using LudeonTK;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // GREENTIDE_PLANT_SIGHT_BLOCK_ENGINE_1 — deterministic STATE-READ proof.
    //
    // No screenshots, no watching: this stages two pawns six cells apart on
    // the current map, calls the ACTUAL engine functions a pawn uses to see and
    // shoot (AttackTargetFinder.CanSee, Verb.CanHitTarget with a real revolver,
    // ThoughtUtility.Witnessed, ShootLeanUtility.CellCanSeeCell), then puts one
    // sight-blocking plant between them and asks again. It also asserts the
    // things that must NOT change (plain LineOfSight, the explosion cell set,
    // walkability) and the settings toggles, then removes everything it made.
    //
    // Dev menu: RimMandrake > "Sight-block probe" / "Sight-block stress".
    // Result goes to the log AND to lastReport (readable by reflection).
    // ════════════════════════════════════════════════════════════════════
    public static class RM_SightBlockProbe
    {
        public static string lastReport = "";

        [DebugAction("RimMandrake", "Sight-block probe", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        public static void ProbeAction()
        {
            string r = Run(Find.CurrentMap);
            if (r.StartsWith("RM sight-block probe: PASS"))
            {
                Log.Message(r);
            }
            else
            {
                Log.Warning(r);
            }
        }

        [DebugAction("RimMandrake", "Sight-block stress", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        public static void StressAction()
        {
            Log.Message(Stress(Find.CurrentMap, 20000));
        }

        private static ThingDef FindBlockerDef()
        {
            ThingDef named = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Brakkel");
            if (named != null && named.HasComp(typeof(RM_CompSightBlocker)))
            {
                return named;
            }
            return DefDatabase<ThingDef>.AllDefs.FirstOrDefault(d => d.category == ThingCategory.Plant && d.HasComp(typeof(RM_CompSightBlocker)));
        }

        private static bool CellClear(IntVec3 c, Map map)
        {
            if (!c.InBounds(map) || !c.Standable(map) || c.GetEdifice(map) != null || c.GetPlant(map) != null || c.GetFirstPawn(map) != null)
            {
                return false;
            }
            return !c.Fogged(map);
        }

        private static bool TryFindStrip(Map map, out IntVec3 a)
        {
            IntVec3 center = map.Center;
            int n = GenRadial.NumCellsInRadius(Math.Min(50f, GenRadial.MaxRadialPatternRadius - 1f));
            for (int i = 0; i < n; i++)
            {
                IntVec3 c = center + GenRadial.RadialPattern[i];
                bool ok = true;
                for (int dx = -1; dx <= 7 && ok; dx++)
                {
                    ok = CellClear(c + new IntVec3(dx, 0, 0), map);
                }
                if (ok)
                {
                    a = c;
                    return true;
                }
            }
            a = IntVec3.Invalid;
            return false;
        }

        public static string Run(Map map)
        {
            StringBuilder sb = new StringBuilder();
            int pass = 0, fail = 0;
            void Check(string what, bool actual, bool expected)
            {
                bool ok = actual == expected;
                if (ok) { pass++; } else { fail++; }
                sb.AppendLine((ok ? "  ok   " : "  FAIL ") + what + " = " + actual + " (expected " + expected + ")");
            }

            if (map == null)
            {
                return "RM sight-block probe: UNMEASURED — no current map.";
            }
            ThingDef blockerDef = FindBlockerDef();
            if (blockerDef == null)
            {
                return "RM sight-block probe: UNMEASURED — no Plant ThingDef carries RM_CompProperties_SightBlocker in this mod set.";
            }
            if (!TryFindStrip(map, out IntVec3 a))
            {
                return "RM sight-block probe: UNMEASURED — no clear 9-cell standable strip near map centre.";
            }
            ThingDef gunDef = DefDatabase<ThingDef>.GetNamedSilentFail("Gun_Revolver");
            RM_MapComponent_SightBlockGrid grid = RM_MapComponent_SightBlockGrid.For(map);

            bool sEnabled = RM_CreatureBehaviorsSettings.sightBlockEnabled;
            bool sRanged = RM_CreatureBehaviorsSettings.sightBlockRangedFire;
            int sNeeded = RM_CreatureBehaviorsSettings.sightBlockCellsNeeded;
            RM_CreatureBehaviorsSettings.sightBlockEnabled = true;
            RM_CreatureBehaviorsSettings.sightBlockRangedFire = true;
            RM_CreatureBehaviorsSettings.sightBlockCellsNeeded = 1;

            IntVec3 plantCell = a + new IntVec3(3, 0, 0);
            IntVec3 b = a + new IntVec3(6, 0, 0);
            List<Thing> made = new List<Thing>();
            sb.AppendLine("  blocker def " + blockerDef.defName + ", A " + a + ", plant " + plantCell + ", B " + b
                + ", map " + map + " (" + map.Biome?.defName + "), blocked cells before " + (grid?.BlockedCellCount ?? -1));
            try
            {
                Pawn pa = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
                Pawn pb = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
                GenSpawn.Spawn(pa, a, map);
                made.Add(pa);
                GenSpawn.Spawn(pb, b, map);
                made.Add(pb);
                Verb verb = null;
                if (gunDef != null)
                {
                    ThingWithComps gun = (ThingWithComps)ThingMaker.MakeThing(gunDef);
                    pa.equipment.AddEquipment(gun);
                    verb = pa.equipment.PrimaryEq?.PrimaryVerb;
                }
                if (verb == null)
                {
                    sb.AppendLine("  note: no Gun_Revolver verb — ranged-shot checks skipped");
                }

                // Baseline, nothing between them.
                Check("baseline CanSee(A,B)", pa.CanSee(pb), true);
                if (verb != null) { Check("baseline revolver CanHitTarget(B)", verb.CanHitTarget(pb), true); }
                Check("baseline Witnessed(B sees A)", ThoughtUtility.Witnessed(pb, pa), true);
                Check("baseline CellCanSeeCell(A,B)", ShootLeanUtility.CellCanSeeCell(a, b, map), true);
                List<IntVec3> blastBefore = DamageDefOf.Bomb.Worker.ExplosionCellsToHit(a, map, 7.9f).ToList();

                // One mature blocker between them.
                Plant plant = (Plant)ThingMaker.MakeThing(blockerDef);
                plant.Growth = 1f;
                GenSpawn.Spawn(plant, plantCell, map);
                made.Add(plant);
                RM_CompSightBlocker comp = plant.GetComp<RM_CompSightBlocker>();
                Check("grid marks the plant cell", grid != null && grid.IsBlocked(plantCell), true);
                Check("blocked CanSee(A,B)", pa.CanSee(pb), false);
                Check("blocked CanSee(B,A)", pb.CanSee(pa), false);
                if (verb != null) { Check("blocked revolver CanHitTarget(B)", verb.CanHitTarget(pb), false); }
                Check("blocked Witnessed(B sees A)", ThoughtUtility.Witnessed(pb, pa), false);
                Check("blocked CellCanSeeCell(A,B)", ShootLeanUtility.CellCanSeeCell(a, b, map), false);

                // Must NOT change: physics and pathing.
                Check("plain GenSight.LineOfSight(A,B) outside a sight scope", GenSight.LineOfSight(a, b, map), true);
                List<IntVec3> blastAfter = DamageDefOf.Bomb.Worker.ExplosionCellsToHit(a, map, 7.9f).ToList();
                Check("explosion cell set unchanged (" + blastBefore.Count + " vs " + blastAfter.Count + ")",
                    blastBefore.Count == blastAfter.Count && blastAfter.Contains(b) == blastBefore.Contains(b), true);
                Check("plant cell still walkable", plantCell.Walkable(map), true);
                Check("plant cell still standable", plantCell.Standable(map), true);

                // A pawn standing IN the thicket cell is seen, and sees out.
                Pawn pc = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
                GenSpawn.Spawn(pc, plantCell, map);
                made.Add(pc);
                Check("A sees C standing in the plant cell", pa.CanSee(pc), true);
                Check("C in the plant cell sees A", pc.CanSee(pa), true);
                pc.DeSpawn();
                made.Remove(pc);
                pc.Destroy();

                // Growth threshold.
                plant.Growth = Math.Max(0f, comp.Props.minGrowth - 0.3f);
                comp.Refresh();
                Check("young plant (growth " + plant.Growth.ToString("0.00") + " < " + comp.Props.minGrowth + ") does not block", pa.CanSee(pb), true);
                plant.Growth = 1f;
                comp.Refresh();
                Check("regrown plant blocks again", pa.CanSee(pb), false);

                // Settings.
                RM_CreatureBehaviorsSettings.sightBlockRangedFire = false;
                if (verb != null) { Check("rangedFire OFF: revolver CanHitTarget(B)", verb.CanHitTarget(pb), true); }
                Check("rangedFire OFF: CanSee(A,B)", pa.CanSee(pb), true);
                Check("rangedFire OFF: Witnessed still blocked", ThoughtUtility.Witnessed(pb, pa), false);
                RM_CreatureBehaviorsSettings.sightBlockRangedFire = true;
                RM_CreatureBehaviorsSettings.sightBlockCellsNeeded = 2;
                Check("cellsNeeded 2: one plant does not block", pa.CanSee(pb), true);
                RM_CreatureBehaviorsSettings.sightBlockCellsNeeded = 1;
                RM_CreatureBehaviorsSettings.sightBlockEnabled = false;
                Check("master OFF: CanSee(A,B)", pa.CanSee(pb), true);
                Check("master OFF: Witnessed", ThoughtUtility.Witnessed(pb, pa), true);
                RM_CreatureBehaviorsSettings.sightBlockEnabled = true;

                Check("sight scope depth back to 0", RM_SightContext.depth == 0, true);

                // Despawn clears the grid.
                plant.Destroy();
                made.Remove(plant);
                Check("grid clears on despawn", grid != null && grid.IsBlocked(plantCell), false);
                Check("after removal CanSee(A,B)", pa.CanSee(pb), true);
            }
            catch (Exception e)
            {
                fail++;
                sb.AppendLine("  FAIL exception: " + e);
            }
            finally
            {
                foreach (Thing t in made)
                {
                    if (!t.Destroyed)
                    {
                        t.Destroy();
                    }
                }
                RM_CreatureBehaviorsSettings.sightBlockEnabled = sEnabled;
                RM_CreatureBehaviorsSettings.sightBlockRangedFire = sRanged;
                RM_CreatureBehaviorsSettings.sightBlockCellsNeeded = sNeeded;
                RM_SightContext.depth = 0;
            }
            string head = "RM sight-block probe: " + (fail == 0 ? "PASS " : "FAIL ") + pass + "/" + (pass + fail)
                + " (hooks patched " + RM_SightBlockPatches.patchedCount + "/9)";
            lastReport = head + "\n" + sb;
            return lastReport;
        }

        /// <summary>Times GenSight.LineOfSight over random pairs, outside and inside a sight scope, on this map as it stands.</summary>
        public static string Stress(Map map, int calls)
        {
            if (map == null)
            {
                return "RM sight-block stress: UNMEASURED — no current map.";
            }
            RM_MapComponent_SightBlockGrid grid = RM_MapComponent_SightBlockGrid.For(map);
            Rand.PushState(1234);
            IntVec3[] from = new IntVec3[calls];
            IntVec3[] to = new IntVec3[calls];
            for (int i = 0; i < calls; i++)
            {
                from[i] = CellFinder.RandomCell(map);
                to[i] = from[i] + GenRadial.RadialPattern[Rand.Range(0, GenRadial.NumCellsInRadius(30f))];
            }
            Rand.PopState();

            int prev = RM_SightContext.depth;
            long vanillaTicks, scopedTicks;
            int vanillaTrue = 0, scopedTrue = 0;
            Stopwatch sw = Stopwatch.StartNew();
            RM_SightContext.depth = 0;
            for (int i = 0; i < calls; i++)
            {
                if (GenSight.LineOfSight(from[i], to[i], map, skipFirstCell: true)) { vanillaTrue++; }
            }
            vanillaTicks = sw.ElapsedTicks;
            sw.Restart();
            RM_SightContext.depth = 1;
            for (int i = 0; i < calls; i++)
            {
                if (GenSight.LineOfSight(from[i], to[i], map, skipFirstCell: true)) { scopedTrue++; }
            }
            scopedTicks = sw.ElapsedTicks;
            RM_SightContext.depth = prev;
            double usV = vanillaTicks * 1e6 / Stopwatch.Frequency / calls;
            double usS = scopedTicks * 1e6 / Stopwatch.Frequency / calls;
            return "RM sight-block stress on " + map + " (" + map.Biome?.defName + ", " + map.Size.x + "x" + map.Size.z
                + "): blocked cells " + (grid?.BlockedCellCount ?? -1) + "; " + calls + " LineOfSight calls (<=30 cells): "
                + "unscoped " + usV.ToString("0.000") + " us/call (" + vanillaTrue + " clear), "
                + "in sight scope " + usS.ToString("0.000") + " us/call (" + scopedTrue + " clear).";
        }
    }
}
