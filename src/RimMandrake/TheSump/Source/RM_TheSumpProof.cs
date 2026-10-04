using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.TheSump
{
    /// <summary>
    /// THESUMP_COVERAGE_GAPS_1: jawa/static_call proofs on the CURRENT map. Each drives the real comp methods and
    /// reports key=value text for validation.py; each removes what it spawned.
    /// </summary>
    public static class RM_TheSumpProof
    {
        private static bool TryCell(Map map, IntVec2 size, out IntVec3 cell)
        {
            return CellFinder.TryFindRandomCellNear(map.Center, map, 30,
                c => GenAdj.OccupiedRect(c, Rot4.North, size).All(x => x.InBounds(map) && x.Standable(map)
                     && x.GetFirstBuilding(map) == null && x.GetFirstItem(map) == null && x.GetFirstPawn(map) == null), out cell);
        }

        /// <summary>Tar vault: a stored meal is sealed (rot frozen, forbidden); taken out with no solvent it comes
        /// out as tar-ruined goods; with a weak solvent on the map it comes out clean and the solvent is spent.</summary>
        public static string ProofVault(Map map)
        {
            map = map ?? Find.CurrentMap;
            ThingDef vaultDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_TarVault");
            ThingDef solventDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_WeakTarSolvent");
            if (map == null || vaultDef == null || solventDef == null)
            {
                return "UNMEASURED no map, RM_TarVault or RM_WeakTarSolvent";
            }
            ThingDef strongDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_StrongTarSolvent");
            if (map.listerThings.ThingsOfDef(solventDef).Any() || (strongDef != null && map.listerThings.ThingsOfDef(strongDef).Any()))
            {
                return "UNMEASURED this map already holds tar solvent (the ruined arm needs none)";
            }
            if (!TryCell(map, vaultDef.size, out IntVec3 cell))
            {
                return "UNMEASURED no clear cell";
            }
            Thing vault = GenSpawn.Spawn(ThingMaker.MakeThing(vaultDef, vaultDef.MadeFromStuff ? GenStuff.DefaultStuffFor(vaultDef) : null), cell, map);
            vault.SetFaction(Faction.OfPlayer);
            var seal = vault.TryGetComp<RM_Comp_TarVaultSeal>();
            if (seal == null)
            {
                vault.Destroy();
                return "FAIL RM_TarVault carries no RM_Comp_TarVaultSeal";
            }
            Thing meal1 = GenSpawn.Spawn(ThingMaker.MakeThing(ThingDefOf.MealSimple), cell, map);
            seal.ScanNow();
            bool sealed1 = seal.IsSealed(meal1);
            bool rotFrozen = meal1.TryGetComp<CompRottable>()?.disabled == true;
            bool forbidden = meal1.IsForbidden(Faction.OfPlayer);
            IntVec3 pos = meal1.Position;
            seal.ExtractOne(meal1);
            ThingDef ruinedDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_TarRuinedGoods");
            Thing ruined = ruinedDef == null ? null : GenRadial.RadialDistinctThingsAround(pos, map, 4f, true).FirstOrDefault(t => t.def == ruinedDef);
            bool ruinedOut = meal1.Destroyed && ruined != null;
            ruined?.Destroy();

            Thing meal2 = GenSpawn.Spawn(ThingMaker.MakeThing(ThingDefOf.MealSimple), cell, map);
            Thing solvent = ThingMaker.MakeThing(solventDef);
            solvent.stackCount = 2;
            IntVec3 sc = cell + new IntVec3(0, 0, -2);
            if (!sc.InBounds(map) || !sc.Standable(map))
            {
                sc = CellFinder.StandableCellNear(cell, map, 6f);
            }
            GenPlace.TryPlaceThing(solvent, sc, map, ThingPlaceMode.Near);
            seal.ScanNow();
            seal.ExtractOne(meal2);
            bool cleanOut = !meal2.Destroyed && meal2.TryGetComp<CompRottable>()?.disabled == false && !meal2.IsForbidden(Faction.OfPlayer);
            int solventLeft = map.listerThings.ThingsOfDef(solventDef).Sum(t => t.stackCount);

            foreach (Thing t in map.listerThings.ThingsOfDef(solventDef).ToList())
            {
                t.Destroy();
            }
            if (!meal2.Destroyed)
            {
                meal2.Destroy();
            }
            vault.Destroy();
            return "sealed=" + sealed1 + " rotFrozen=" + rotFrozen + " forbidden=" + forbidden + " ruinedOut=" + ruinedOut
                   + " cleanOut=" + cleanOut + " solventLeft=" + solventLeft;
        }

        /// <summary>Kethrel: carried metal steps its shell stage (and the shell hediff) by load; a molt drops it all
        /// and returns it to stage 0.</summary>
        public static string ProofKethrel(Map map)
        {
            map = map ?? Find.CurrentMap;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Kethrel");
            if (map == null || kind == null)
            {
                return "UNMEASURED no map or no RM_Kethrel kind";
            }
            if (!TryCell(map, new IntVec2(1, 1), out IntVec3 cell))
            {
                return "UNMEASURED no clear cell";
            }
            Pawn k = (Pawn)GenSpawn.Spawn(PawnGenerator.GeneratePawn(kind), cell, map);
            var shell = k.TryGetComp<RM_CompKethrelShell>();
            if (shell == null)
            {
                k.Destroy();
                return "FAIL RM_Kethrel carries no RM_CompKethrelShell";
            }
            int s0 = shell.Stage;
            Thing steel = ThingMaker.MakeThing(ThingDefOf.Steel);
            steel.stackCount = 30;   // 15 kg
            GenSpawn.Spawn(steel, cell, map);
            shell.PickUp(steel);
            int s1 = shell.Stage;
            float kg1 = shell.LoadKg;
            Hediff h1 = k.health.hediffSet.GetFirstHediffOfDef(KethrelDefOf.RM_KethrelShell);
            Thing more = ThingMaker.MakeThing(ThingDefOf.Steel);
            more.stackCount = 30;    // 30 kg total
            GenSpawn.Spawn(more, cell, map);
            shell.PickUp(more);
            int s2 = shell.Stage;
            int dropped = shell.Molt(null);
            int sAfter = shell.Stage;
            bool hediffGone = k.health.hediffSet.GetFirstHediffOfDef(KethrelDefOf.RM_KethrelShell) == null;
            int steelOnMap = GenRadial.RadialDistinctThingsAround(cell, map, 5f, true).Where(t => t.def == ThingDefOf.Steel).Sum(t => t.stackCount);
            foreach (Thing t in GenRadial.RadialDistinctThingsAround(cell, map, 5f, true).Where(t => t.def == ThingDefOf.Steel).ToList())
            {
                t.Destroy();
            }
            k.Destroy();
            return "s0=" + s0 + " kg1=" + kg1.ToString("0") + " s1=" + s1 + " hediff1=" + (h1 != null ? h1.Severity.ToString("0.00") : "none")
                   + " s2=" + s2 + " dropped=" + dropped + " sAfter=" + sAfter + " hediffGone=" + hediffGone + " steelOnMap=" + steelOnMap;
        }
    }
}
