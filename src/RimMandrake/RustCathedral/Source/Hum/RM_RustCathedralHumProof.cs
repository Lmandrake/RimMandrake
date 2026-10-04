using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.RustCathedral.Hum
{
    /// <summary>
    /// RUSTCATHEDRAL_COVERAGE_GAPS_1. Deterministic reads/triggers for jawa/static_call on the CURRENT map. A
    /// quicktest map has no attitude def (only RM_RustCathedral does), so each proof binds the map's attitude
    /// component to RM_RustCathedralAttitude for the call and resets it afterwards (unless the map IS the
    /// Cathedral, where the binding is already what the game would do).
    /// </summary>
    public static class RM_RustCathedralHumProof
    {
        private const string AttitudeDefName = "RM_RustCathedralAttitude";

        private static RM_MapComponent_BiomeAttitude Bind(Map map, out string refusal)
        {
            refusal = null;
            if (map == null) { refusal = "REFUSED: no current map"; return null; }
            RM_MapComponent_BiomeAttitude comp = map.GetComponent<RM_MapComponent_BiomeAttitude>();
            RM_BiomeAttitudeDef def = DefDatabase<RM_BiomeAttitudeDef>.GetNamedSilentFail(AttitudeDefName);
            if (comp == null || def == null) { refusal = "REFUSED: no attitude component or def"; return null; }
            comp.ProofUseDef(def);
            return comp;
        }

        private static int Goodwill() => Faction.OfMechanoids?.GoodwillWith(Faction.OfPlayer) ?? 0;

        /// <summary>The value ladder, climbing then falling through the hysteresis margin.
        /// "LADDER goodwill G | weight W | up i:b/l,... | down i:b/l,...", i = irritation, b = band, l = hum layers.</summary>
        public static string ProofLadder()
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_BiomeAttitude comp = Bind(map, out string refusal);
            if (comp == null) return refusal;
            RM_BiomeAttitudeDef def = DefDatabase<RM_BiomeAttitudeDef>.GetNamed(AttitudeDefName);
            bool was = RustCathedralHumSettings.humMechanicEnabled;
            try
            {
                RustCathedralHumSettings.humMechanicEnabled = true;
                // Irritation is chosen so the COMPOSITE (irritation - goodwill x weight) lands on each threshold; a
                // composite the goodwill floor already exceeds cannot be reached and reads as the floor band.
                float offset = -Goodwill() * def.goodwillCompositeWeight;
                var up = new List<string>();
                comp.ProofBandAt(0f);
                foreach (float composite in new[] { 0f, 10f, 30f, 55f, 80f })
                {
                    float irr = composite - offset;
                    int b = comp.ProofBandAt(irr);
                    up.Add(composite.ToString("0", CultureInfo.InvariantCulture) + ":" + b + "/" + comp.ProofLayers);
                }
                var down = new List<string>();
                foreach (float composite in new[] { 77f, 73f, 52f, 48f })
                {
                    int b = comp.ProofBandAt(composite - offset);
                    down.Add(composite.ToString("0", CultureInfo.InvariantCulture) + ":" + b + "/" + comp.ProofLayers);
                }
                return "LADDER goodwill " + Goodwill() + " | weight " + def.goodwillCompositeWeight.ToString("0.00", CultureInfo.InvariantCulture)
                    + " | up " + string.Join(",", up) + " | down " + string.Join(",", down);
            }
            finally
            {
                RustCathedralHumSettings.humMechanicEnabled = was;
                if (map.Biome?.defName != def.targetBiome) comp.ProofReset();
            }
        }

        /// <summary>"enabled": boltWatchedPricingEnabled for the call. A player colonist picks up a shed curiosity
        /// twice and kills a living bolt. "WATCHED pickup +A | again +B | kill +C".</summary>
        public static string ProofWatched(string args)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_BiomeAttitude comp = Bind(map, out string refusal);
            if (comp == null) return refusal;
            bool enabled = (args ?? "true").Trim().ToLowerInvariant() != "false";
            bool wasHum = RustCathedralHumSettings.humMechanicEnabled, wasWatch = RustCathedralHumSettings.boltWatchedPricingEnabled;
            ThingDef curio = DefDatabase<ThingDef>.GetNamedSilentFail(RM_WatchedBolts.CuriosityDefName);
            PawnKindDef boltKind = DefDatabase<PawnKindDef>.GetNamedSilentFail(RM_WatchedBolts.LivingBoltDefName);
            if (curio == null || boltKind == null) return "REFUSED: curiosity or living bolt def missing";
            var made = new List<Thing>();
            try
            {
                RustCathedralHumSettings.humMechanicEnabled = true;
                RustCathedralHumSettings.boltWatchedPricingEnabled = enabled;
                IntVec3 at = CellFinder.RandomClosewalkCellNear(map.Center, map, 20);
                Pawn colonist = PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDefOf.Colonist, Faction.OfPlayer,
                    fixedBiologicalAge: 30f, fixedChronologicalAge: 30f));
                GenSpawn.Spawn(colonist, at, map);
                made.Add(colonist);
                comp.ProofBandAt(0f);
                float i0 = comp.ProofIrritation;
                Thing item = GenSpawn.Spawn(ThingMaker.MakeThing(curio), at, map);
                made.Add(item);
                colonist.carryTracker.TryStartCarry(item);
                float i1 = comp.ProofIrritation;
                if (colonist.carryTracker.CarriedThing != null)
                {
                    colonist.carryTracker.TryDropCarriedThing(at, ThingPlaceMode.Near, out Thing dropped);
                    if (dropped != null) { made.Add(dropped); colonist.carryTracker.TryStartCarry(dropped); }
                }
                float i2 = comp.ProofIrritation;
                Pawn bolt = (Pawn)GenSpawn.Spawn(PawnGenerator.GeneratePawn(boltKind), CellFinder.RandomClosewalkCellNear(at, map, 4), map);
                made.Add(bolt);
                bolt.Kill(new DamageInfo(DamageDefOf.Cut, 9999f, 0f, -1f, colonist));
                float i3 = comp.ProofIrritation;
                return "WATCHED pickup +" + (i1 - i0).ToString("0.0", CultureInfo.InvariantCulture)
                    + " | again +" + (i2 - i1).ToString("0.0", CultureInfo.InvariantCulture)
                    + " | kill +" + (i3 - i2).ToString("0.0", CultureInfo.InvariantCulture);
            }
            finally
            {
                RustCathedralHumSettings.humMechanicEnabled = wasHum;
                RustCathedralHumSettings.boltWatchedPricingEnabled = wasWatch;
                foreach (Thing t in made)
                {
                    if (t is Pawn p && p.Corpse != null && !p.Corpse.Destroyed) p.Corpse.Destroy();
                    if (t is Pawn cp && cp.carryTracker?.CarriedThing != null) cp.carryTracker.DestroyCarriedThing();
                    if (!t.Destroyed && t.Spawned) t.Destroy();
                }
                if (map.Biome?.defName != DefDatabase<RM_BiomeAttitudeDef>.GetNamed(AttitudeDefName).targetBiome) comp.ProofReset();
            }
        }
    }
}
