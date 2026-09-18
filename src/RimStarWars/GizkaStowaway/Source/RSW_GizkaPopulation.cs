using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.GizkaStowaway
{
    /// <summary>
    /// GIZKA_TRIBBLE_ADAPTATION_1 — the one place that knows what a stowaway
    /// gizka IS, so that no other file has to guess.
    ///
    /// The donor's defNames are resolved by silent lookup, never by DefOf: this
    /// mod must load and run cleanly with Star Wars Animal Collection absent,
    /// and a DefOf field for a def that does not exist is a red error on every
    /// startup. Donor absent => `Kind` is null => every entry point here
    /// returns without doing anything, which is the whole of the graceful
    /// no-op the draft's "Mod home" paragraph asks for.
    /// </summary>
    public static class RSW_GizkaPopulation
    {
        // Two gizka are live at once: SWBestiary's ported `RSW_Gizka`
        // (MLIE_FAUNA_ABSORPTION_1 Pass 12, a defName-only rename of the
        // donor) and the donor's own `Gizka`. Ours is preferred so that the
        // feature keeps working on the day Star Wars Animal Collection is
        // retired; the donor is the fallback for as long as it is the one
        // actually in the biome rosters.
        private static readonly string[] GizkaDefNames = { "RSW_Gizka", "Gizka" };

        private static bool resolved;
        private static PawnKindDef kind;
        private static HediffDef fecundity;

        public static PawnKindDef Kind
        {
            get { Resolve(); return kind; }
        }

        public static HediffDef Fecundity
        {
            get { Resolve(); return fecundity; }
        }

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;
            for (int i = 0; i < GizkaDefNames.Length && kind == null; i++)
            {
                kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(GizkaDefNames[i]);
            }
            fecundity = DefDatabase<HediffDef>.GetNamedSilentFail("RSW_GizkaFecundity");
        }

        public static bool IsStowawayGizka(Pawn p)
        {
            if (p == null || p.Dead) return false;
            if (Fecundity == null) return false;
            return p.health?.hediffSet?.GetFirstHediffOfDef(Fecundity) != null;
        }

        /// <summary>
        /// Stowaway-lineage gizka currently on this map. Deliberately counts
        /// lineage only, not every gizka present: a caravan of bought gizka
        /// passing through must not push the pest population over its cap, and
        /// the player's own farmed stock must not be able to stall the pest by
        /// filling the cap for it.
        /// </summary>
        public static int CountOnMap(Map map)
        {
            if (map == null) return 0;
            int n = 0;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                if (IsStowawayGizka(pawns[i])) n++;
            }
            return n;
        }

        public static List<Pawn> ListOnMap(Map map)
        {
            List<Pawn> result = new List<Pawn>();
            if (map == null) return result;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                if (IsStowawayGizka(pawns[i])) result.Add(pawns[i]);
            }
            return result;
        }

        /// <summary>
        /// Makes one stowaway-lineage gizka and puts it on the map.
        /// `faction` is the faction it belongs to — the player's, for a tame
        /// discovery and for everything descended from one.
        /// </summary>
        public static Pawn SpawnStowaway(Map map, IntVec3 cell, Faction faction, bool newborn)
        {
            if (map == null || Kind == null || Fecundity == null) return null;

            Pawn p = PawnGenerator.GeneratePawn(Kind, faction);
            if (p == null) return null;

            if (newborn && p.ageTracker != null)
            {
                p.ageTracker.AgeBiologicalTicks = 0L;
                p.ageTracker.AgeChronologicalTicks = 0L;
            }

            p.health.AddHediff(Fecundity);

            if (!GenPlace.TryPlaceThing(p, cell, map, ThingPlaceMode.Near))
            {
                p.Destroy();
                return null;
            }

            // Faction is set by PawnGenerator from the request above. Passing
            // the player's faction is what makes the discovery ARRIVE tame:
            // no taming roll, no handler job, no chance of it wandering off
            // before the colony has met it. The draft's endearment beats
            // (nuzzles, naming, bonding) are all vanilla behaviour that only
            // happens to a tame animal.
            return p;
        }
    }
}
