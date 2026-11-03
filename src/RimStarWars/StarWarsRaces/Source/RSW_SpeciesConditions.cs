using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Races
{
    // SPECIES_TRAITS_OVER_APTITUDES_1: species character that no skill aptitude can carry, expressed as a gene's
    // stat bonus that holds only in a situation. Vanilla's StatWorker reads GeneDef.conditionalStatAffecters
    // (offsets and factors, plus a "<gene> (<Label>)" line in the stat explanation), so no Harmony is needed.
    // Each class is chosen in XML (Defs/GeneDefs/RSW_SpeciesCharacter.xml) and switched by one Mod Setting;
    // a switched-off condition never applies, which leaves the gene inert.
    //
    // Applies() runs for EVERY stat of every pawn carrying the gene, so each check must be cheap: the two
    // map scans below are cached per pawn for RecheckTicks.

    public abstract class RSW_SpeciesCondition : ConditionalStatAffecter
    {
        /// <summary>The stat-explanation text, "<gene> (label): +x". Def text, so the player reads it.</summary>
        public string label;

        /// <summary>Which Mod Setting switches this condition (RSW_StarWarsRacesSettings.SpeciesMechanicOn).</summary>
        public string setting;

        public override string Label => label ?? GetType().Name;

        public override bool Applies(StatRequest req)
        {
            if (!RSW_StarWarsRacesSettings.SpeciesMechanicOn(setting)) return false;
            if (!req.HasThing || !(req.Thing is Pawn pawn)) return false;
            if (NeedsMap && (!pawn.Spawned || pawn.Map == null)) return false;
            return AppliesTo(pawn);
        }

        /// <summary>True for conditions that read the pawn's map. MoodBand does not: a Bothan trading from a
        /// caravan (unspawned) still shows its fur.</summary>
        protected virtual bool NeedsMap => true;

        protected abstract bool AppliesTo(Pawn pawn);
    }

    /// <summary>Counts, per pawn, the OTHER living spawned carriers of kinGene on its map and within radius.
    /// Shared by the near-kin and no-kin conditions so one scan serves both.</summary>
    public static class RSW_KinCensus
    {
        public const int RecheckTicks = 250;

        private struct Entry
        {
            public int tick;
            public int mapId;
            public float radius;
            public int near;
            public int onMap;
        }

        private static readonly Dictionary<(int pawn, ushort gene), Entry> cache = new Dictionary<(int, ushort), Entry>();

        public static void Count(Pawn pawn, GeneDef kinGene, float radius, out int near, out int onMap)
        {
            int now = Find.TickManager?.TicksGame ?? 0;
            var key = (pawn.thingIDNumber, kinGene.shortHash);
            if (cache.TryGetValue(key, out Entry e) && e.mapId == pawn.Map.uniqueID && e.radius == radius
                && now - e.tick < RecheckTicks && now >= e.tick)
            {
                near = e.near;
                onMap = e.onMap;
                return;
            }
            near = 0;
            onMap = 0;
            float r2 = radius * radius;
            IReadOnlyList<Pawn> all = pawn.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn other = all[i];
                if (other == pawn || other.Dead || other.genes == null || !other.genes.HasActiveGene(kinGene)) continue;
                onMap++;
                if ((other.Position - pawn.Position).LengthHorizontalSquared <= r2) near++;
            }
            if (cache.Count > 4096) cache.Clear();
            cache[key] = new Entry { tick = now, mapId = pawn.Map.uniqueID, radius = radius, near = near, onMap = onMap };
        }
    }

    /// <summary>Holds while at least minKin other carriers of kinGene stand within radius cells.</summary>
    public class ConditionalStatAffecter_NearKin : RSW_SpeciesCondition
    {
        public GeneDef kinGene;
        public float radius = 15f;
        public int minKin = 2;

        protected override bool AppliesTo(Pawn pawn)
        {
            if (kinGene == null) return false;
            RSW_KinCensus.Count(pawn, kinGene, radius, out int near, out _);
            return near >= minKin;
        }
    }

    /// <summary>Holds while no other carrier of kinGene is anywhere on the pawn's map: cut off from the hive.</summary>
    public class ConditionalStatAffecter_NoKinOnMap : RSW_SpeciesCondition
    {
        public GeneDef kinGene;
        public float radius = 15f;

        protected override bool AppliesTo(Pawn pawn)
        {
            if (kinGene == null) return false;
            RSW_KinCensus.Count(pawn, kinGene, radius, out _, out int onMap);
            return onMap == 0;
        }
    }

    /// <summary>Holds while the pawn's mood (0..1) is in [minMood, maxMood). A pawn with no mood need never matches.</summary>
    public class ConditionalStatAffecter_MoodBand : RSW_SpeciesCondition
    {
        public float minMood = 0f;
        public float maxMood = 1.01f;

        protected override bool NeedsMap => false;

        protected override bool AppliesTo(Pawn pawn)
        {
            Need_Mood mood = pawn.needs?.mood;
            if (mood == null) return false;
            float m = mood.CurLevelPercentage;
            return m >= minMood && m < maxMood;
        }
    }

    /// <summary>Holds while the pawn stands under a thick (overhead-mountain) roof: underground.</summary>
    public class ConditionalStatAffecter_UnderThickRoof : RSW_SpeciesCondition
    {
        protected override bool AppliesTo(Pawn pawn)
        {
            RoofDef roof = pawn.Position.GetRoof(pawn.Map);
            return roof != null && roof.isThickRoof;
        }
    }
}
