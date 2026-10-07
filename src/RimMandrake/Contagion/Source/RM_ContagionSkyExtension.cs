using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_MECHANICS_BUILD_1 Part 1 — the Burn and the Bloom.
    //
    // The whole sky engine is gated on THIS extension sitting on the map's
    // BiomeDef (the Undersurge lesson, TWILIGHT_REVIEW_FIXES_1 #3: every
    // map-wide roll gates on the biome, never on settings alone). RM_Contagion
    // carries it; any other biome that wants the Burn/Bloom kit can carry it
    // too, which is the "biome-kit mechanics are feature-gated so they can be
    // enabled in other biomes" law. A biome without it never schedules a
    // Burn, whatever the settings say.
    public class RM_ContagionSkyExtension : DefModExtension
    {
        // Mean gap between Burns, in days, before the Mod Settings frequency
        // multiplier. Each gap is rolled uniformly in [0.5x, 1.5x] of this.
        public float meanDaysBetweenBurns = 3f;

        // How long one Burn holds the sky, in ticks. "Raw UV lances the valley
        // floor for minutes" (sheet §3) — well under two in-game hours.
        public IntRange burnDurationTicks = new IntRange(1500, 4000);

        // How far ahead of the tear the tells begin. The sheet's "seconds
        // before a Burn": 1250 ticks is half an in-game hour, ~20 s real time
        // at 1x speed.
        public int tellLeadTicks = 1250;

        // Natives are every race in this biome's own wildAnimals roster plus
        // these (things the goo buds that are not rostered — the Unfinished).
        public List<ThingDef> extraNatives = new List<ThingDef>();

        // UV-armored natives (sheet §4's carve-outs): take no Burn damage and
        // do not dive — they come OUT in the Burn.
        public List<ThingDef> armoredNatives = new List<ThingDef>();

        // Natives that walk into the light and cook: take Burn damage but are
        // never ordered to dive (the Scorchpod, "the leaker").
        public List<ThingDef> leakerNatives = new List<ThingDef>();

        // Tell 1: these sink (stop, settle, throw a puff) when a Burn is near.
        public List<ThingDef> tellSinkers = new List<ThingDef>();

        // Tell 2: these plants rattle when a Burn is near (RM_Rattlegrope).
        public List<ThingDef> tellRattlers = new List<ThingDef>();
        // The rattle's sound: one one-shot per tell pulse at a rattling plant.
        // Vanilla by the 2026-10-03 audio ruling (Ideology LeavesRustle, a
        // non-sustained plant-rustle folder); null = silent.
        public SoundDef tellRattleSound;

        // Burn damage to a UV-shy native caught in the open, per 250 ticks,
        // before the Mod Settings damage factor.
        public float nativeBurnDamagePerInterval = 3f;

        // RM_BurnDose severity added to a non-native caught in the open, per
        // 250 ticks, before the Mod Settings damage factor.
        public float visitorDosePerInterval = 0.02f;

        // Part 2 — the Coalescence. Null = this biome never grows one.
        public ThingDef coalescenceDef;
        // A "long Bloom": ticks since the last Burn ended before one can form.
        public int coalescenceLongBloomTicks = 90000;
        // Mean days to form once the Bloom is long enough.
        public float coalescenceMtbDays = 0.5f;
    }

    public static class RM_ContagionSky
    {
        public const int Interval = RM_SkyKernel.Interval;

        public static RM_ContagionSkyExtension ExtFor(Map map)
        {
            if (map == null) return null;
            if (map.generatorDef != null && map.generatorDef.isUnderground) return null;
            return map.Biome?.GetModExtension<RM_ContagionSkyExtension>();
        }

        // Is the sky engine live on this map right now (setting AND biome)?
        public static bool Active(Map map)
        {
            return RM_ContagionSettings.burnEnabled && ExtFor(map) != null;
        }

        // Out under the open sky: unroofed, not under a tree's canopy, not in
        // water. The three shelters the natives dive for (sheet §3: "into the
        // red water, under the canopy, into the goo" — the goo itself is not a
        // cell property, so it is not counted).
        public static bool Exposed(IntVec3 c, Map map)
        {
            if (!c.InBounds(map)) return false;
            TerrainDef t = c.GetTerrain(map);
            Plant p = c.GetPlant(map);
            return RM_SkyKernel.Exposed(true, c.Roofed(map), t != null && t.IsWater, p != null && p.def.plant != null && p.def.plant.IsTree);
        }

        private static readonly Dictionary<BiomeDef, HashSet<ThingDef>> nativeCache =
            new Dictionary<BiomeDef, HashSet<ThingDef>>();

        public static HashSet<ThingDef> NativesOf(BiomeDef biome, RM_ContagionSkyExtension ext)
        {
            if (nativeCache.TryGetValue(biome, out HashSet<ThingDef> set)) return set;
            set = new HashSet<ThingDef>();
            foreach (PawnKindDef k in biome.AllWildAnimals)
            {
                if (k?.race != null) set.Add(k.race);
            }
            if (ext.extraNatives != null) set.UnionWith(ext.extraNatives);
            nativeCache[biome] = set;
            return set;
        }

        // A Contagion native anywhere: its race is native to ANY biome that
        // carries the sky extension. Used by the Sunbeam's multiplier, which
        // must work on a native that wandered (or was hauled) off its biome.
        private static HashSet<ThingDef> allNatives;

        public static bool IsNative(Thing t)
        {
            if (t?.def == null) return false;
            if (allNatives == null)
            {
                allNatives = new HashSet<ThingDef>();
                foreach (BiomeDef b in DefDatabase<BiomeDef>.AllDefsListForReading)
                {
                    RM_ContagionSkyExtension ext = b.GetModExtension<RM_ContagionSkyExtension>();
                    if (ext != null) allNatives.UnionWith(NativesOf(b, ext));
                }
            }
            return allNatives.Contains(t.def);
        }
    }
}
