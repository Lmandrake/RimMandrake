using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Miasma
{
    /// <summary>
    /// MIASMA_COVERAGE_GAPS_1: jawa/static_call proofs for mechanics the suite could only describe. Each drives the
    /// real code path on the CURRENT map (no worldgen, no long tick runs) and reports key=value text for
    /// validation.py to assert on. Each restores any setting it flips.
    /// </summary>
    public static class RM_MiasmaProof
    {
        /// <summary>Decay cell: full feed beats low feed beats empty (0), the switch off makes 0, and feeding it its
        /// lifetime through the real digestion check turns it into a rotting bed.</summary>
        public static string ProofDecayCell(Map map)
        {
            map = map ?? Find.CurrentMap;
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_DecayCell");
            if (map == null || def == null)
            {
                return "UNMEASURED no map or no RM_DecayCell";
            }
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 30,
                    c => GenAdj.OccupiedRect(c, Rot4.North, def.size).All(x => x.InBounds(map) && x.Standable(map)
                         && x.GetFirstBuilding(map) == null && x.GetFirstItem(map) == null), out IntVec3 cell))
            {
                return "UNMEASURED no clear cell";
            }
            Thing t = GenSpawn.Spawn(ThingMaker.MakeThing(def, def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null), cell, map);
            t.SetFaction(Faction.OfPlayer);
            var power = t.TryGetComp<RM_CompPowerPlantDecay>();
            var fuel = t.TryGetComp<CompRefuelable>();
            if (power == null || fuel == null)
            {
                t.Destroy();
                return "FAIL decay cell lacks its power or refuelable comp";
            }
            float cap = fuel.Props.fuelCapacity;
            fuel.Refuel(cap);
            power.UpdateDesiredPowerOutput();
            float full = power.PowerOutput;
            fuel.ConsumeFuel(cap * 0.9f);
            power.UpdateDesiredPowerOutput();
            float low = power.PowerOutput;
            bool was = RM_MiasmaSettings.decayCellsEnabled;
            float off;
            try
            {
                RM_MiasmaSettings.decayCellsEnabled = false;
                power.UpdateDesiredPowerOutput();
                off = power.PowerOutput;
            }
            finally
            {
                RM_MiasmaSettings.decayCellsEnabled = was;
            }
            fuel.ConsumeFuel(fuel.Fuel);
            power.UpdateDesiredPowerOutput();
            float empty = power.PowerOutput;

            int feeds = 0;
            power.ObserveFuel();
            while (!t.Destroyed && feeds < 1000)
            {
                fuel.Refuel(cap);
                power.ObserveFuel();
                fuel.ConsumeFuel(cap);
                power.ObserveFuel();
                feeds++;
            }
            Building bed = cell.GetFirstBuilding(map);
            bool becameBed = t.Destroyed && bed != null && bed.def.defName == "RM_RottingBed";
            string res = "full=" + full.ToString("0") + " low=" + low.ToString("0") + " off=" + off.ToString("0")
                         + " empty=" + empty.ToString("0") + " feeds=" + feeds + " becameBed=" + becameBed;
            if (!t.Destroyed)
            {
                t.Destroy();
            }
            bed?.Destroy();
            return res;
        }

        /// <summary>Attar glaze: a sculpture's Beauty rises by the glaze bonus once glazed, and not with attar
        /// switched off.</summary>
        public static string ProofGlaze(Map map)
        {
            map = map ?? Find.CurrentMap;
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("SculptureSmall");
            if (map == null || def == null || RM_GlazedRegistry.Instance == null)
            {
                return "UNMEASURED no map, no SculptureSmall or no glaze registry";
            }
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 30,
                    c => c.Standable(map) && c.GetFirstBuilding(map) == null && c.GetFirstItem(map) == null, out IntVec3 cell))
            {
                return "UNMEASURED no clear cell";
            }
            Thing art = ThingMaker.MakeThing(def, GenStuff.DefaultStuffFor(def));
            art.TryGetComp<CompArt>()?.InitializeArt(ArtGenerationContext.Colony);
            GenSpawn.Spawn(art, cell, map);
            bool glazable = RM_AttarUtil.IsGlazable(art);
            float before = art.GetStatValue(StatDefOf.Beauty);
            RM_GlazedRegistry.Instance.Add(art);
            float after = art.GetStatValue(StatDefOf.Beauty);
            bool was = RM_MiasmaSettings.attarEnabled;
            float off;
            try
            {
                RM_MiasmaSettings.attarEnabled = false;
                off = art.GetStatValue(StatDefOf.Beauty);
            }
            finally
            {
                RM_MiasmaSettings.attarEnabled = was;
            }
            bool glazableAgain = RM_AttarUtil.IsGlazable(art);
            art.Destroy();
            return "glazable=" + glazable + " before=" + before.ToString("0.0") + " after=" + after.ToString("0.0")
                   + " off=" + off.ToString("0.0") + " glazableAgain=" + glazableAgain;
        }

        /// <summary>Attar balm: a pawn's permanent scar loses severity (or goes), a fresh wound beside it is
        /// untouched.</summary>
        public static string ProofBalm(Map map)
        {
            Pawn p = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
            foreach (Hediff_Injury old in p.health.hediffSet.hediffs.OfType<Hediff_Injury>().ToList())
            {
                p.health.RemoveHediff(old);
            }
            var parts = p.health.hediffSet.GetNotMissingParts().Where(x => x.depth == BodyPartDepth.Outside && x.def.hitPoints >= 20).ToList();
            if (parts.Count < 2)
            {
                return "UNMEASURED no two outside parts on a generated colonist";
            }
            var scar = (Hediff_Injury)HediffMaker.MakeHediff(HediffDefOf.Cut, p, parts[0]);
            scar.Severity = 5f;
            var perm = scar.TryGetComp<HediffComp_GetsPermanent>();
            if (perm == null)
            {
                return "UNMEASURED Cut has no HediffComp_GetsPermanent";
            }
            perm.IsPermanent = true;
            p.health.AddHediff(scar, parts[0]);
            var fresh = (Hediff_Injury)HediffMaker.MakeHediff(HediffDefOf.Cut, p, parts[1]);
            fresh.Severity = 2f;
            p.health.AddHediff(fresh, parts[1]);
            float scarBefore = scar.Severity;
            float freshBefore = fresh.Severity;
            RM_AttarUtil.Balm(p);
            bool scarGone = !p.health.hediffSet.hediffs.Contains(scar);
            string res = "scarBefore=" + scarBefore.ToString("0.0") + " scarAfter=" + (scarGone ? "gone" : scar.Severity.ToString("0.0"))
                         + " freshBefore=" + freshBefore.ToString("0.0") + " freshAfter=" + fresh.Severity.ToString("0.0")
                         + " freshStillThere=" + p.health.hediffSet.hediffs.Contains(fresh);
            p.Discard(true);
            return res;
        }
    }
}
