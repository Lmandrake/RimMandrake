using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // LEANINGSCRUB_MECHANICS_BUILD_1 part 2 — the Lean (v1).
    //
    // Each map whose biome carries RM_LeanExtension has one wind heading: from
    // its tile toward the substellar point (owner card 2026-10-20, "Point it at
    // the sun, snap to a side"), derived from planet geometry, never rolled or
    // saved. v1 scope, per the item: two local patches, no hunting-AI rewrite.
    //
    //   Scent  JobGiver_AnimalFlee.TryGiveJob postfix. Vanilla wild animals
    //          flee only fire and alwaysFlee things (RimSage, decompiled
    //          JobGiver_AnimalFlee); here a wild non-predator also bolts from a
    //          humanlike standing UPWIND of it within scent range — its scent
    //          is carried down onto the animal. Approach from downwind and the
    //          prey never knows.
    //   Fire   Fire.TrySpread prefix. Part of the time the spread picks only
    //          among the adjacent cells that lie downwind, then runs vanilla's
    //          own ChanceToStartFireIn / TryStartFireIn; otherwise vanilla's
    //          own omnidirectional roll runs untouched. Net: fire races
    //          downwind and creeps upwind.
    //
    // Windbreak calm wakes live with the ripple (RM_Ripple.cs InWindbreakLee,
    // setting leanWakesEnabled): in a wall's lee the ripple acts as in the Stall.
    // Not in v1: the fog harvest (no such system) and predators hunting by scent
    // (the spec's v1 scope rules out a hunting-AI rewrite).
    // ════════════════════════════════════════════════════════════════════
    public class RM_LeanExtension : DefModExtension
    {
        // SCRUB_WIND_BUILD_LEAN_ON_PURPOSE (owner card 2026-10-20, biome_bars_sitting §5.1): the plants that face the wind
        // on this biome's maps instead of mirroring at random (RM_PlantLean.cs). Data, never hardcoded defNames.
        public List<ThingDef> leanPlants = new List<ThingDef>();

        // Texture names (file name, no extension) of the variants whose own art leans WEST (screen left). Every other
        // variant of a listed plant is taken to lean east. selftest_scrub_wind.py measures the PNGs against this list.
        public List<string> westLeaningTextures = new List<string>();

        // Owner, by card 2026-10-20 17:28 ("Wind dir → Point it at the sun, snap to a side"): the wind blows from the
        // map's tile toward this substellar point. Ash'karr's is (0, 0), the same point RM_PinnedSunExtension and the
        // WeatherSuite use.
        public float substellarLatitude = 0f;
        public float substellarLongitude = 0f;

        [Unsaved(false)] private bool[] leansByIndex;
        [Unsaved(false)] private HashSet<string> westSet;

        public bool Leans(ThingDef def)
        {
            if (leansByIndex == null)
            {
                leansByIndex = new bool[DefDatabase<ThingDef>.DefCount];
                foreach (ThingDef d in leanPlants)
                {
                    if (d != null && d.index < leansByIndex.Length)
                    {
                        leansByIndex[d.index] = true;
                    }
                }
            }
            return def != null && def.index < leansByIndex.Length && leansByIndex[def.index];
        }

        public HashSet<string> WestSet => westSet ?? (westSet = new HashSet<string>(westLeaningTextures ?? new List<string>()));

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            foreach (ThingDef d in leanPlants)
            {
                if (d != null && d.plant == null)
                {
                    yield return "RM_LeanExtension.leanPlants lists " + d.defName + ", which is not a plant";
                }
            }
            foreach (string n in westLeaningTextures)
            {
                if (n.NullOrEmpty() || n.Contains("/"))
                {
                    yield return "RM_LeanExtension.westLeaningTextures entry '" + n + "' must be a bare texture name";
                }
            }
        }
    }

    public class RM_MapComponent_Lean : MapComponent
    {
        private bool? applies;
        private bool resolved;
        private float headingDegrees;
        private float sunBearingDegrees;
        private Vector2 cachedDir;

        public RM_MapComponent_Lean(Map map) : base(map)
        {
        }

        public bool Applies
        {
            get
            {
                if (!applies.HasValue)
                {
                    applies = map.Biome?.GetModExtension<RM_LeanExtension>() != null;
                }
                return applies.Value;
            }
        }

        // Unit vector the wind blows TOWARD, in map x/z. SCRUB_WIND_BUILD_LEAN_ON_PURPOSE (owner card 2026-10-20 17:28,
        // "Point it at the sun, snap to a side"): toward the substellar point, a pure function of the tile, so it needs
        // no save and every consumer (scent, fire, ripple, creep, the plant lean, the Gale dust) shares one wind. The
        // bearing is CreatureBehaviors' own RM_MapComponent_PinnedSun.SunGeometry, never new maths.
        public Vector2 Downwind
        {
            get
            {
                if (!resolved)
                {
                    Resolve();
                }
                return cachedDir;
            }
        }

        public float HeadingDegrees { get { if (!resolved) Resolve(); return headingDegrees; } }
        public float SunBearingDegrees { get { if (!resolved) Resolve(); return sunBearingDegrees; } }

        private void Resolve()
        {
            resolved = true;
            float bearing = 0f;   // no world tile (never a Scrub map in practice): due north, documented tie -> east lean
            RM_LeanExtension ext = map.Biome?.GetModExtension<RM_LeanExtension>();
            if (ext != null && Find.WorldGrid != null && map.Tile.Valid)
            {
                Vector2 longLat = Find.WorldGrid.LongLatOf(map.Tile);
                RimMandrake.CreatureBehaviors.RM_MapComponent_PinnedSun.SunGeometry(longLat.y, longLat.x,
                    ext.substellarLatitude, ext.substellarLongitude, out bearing, out float _);
            }
            sunBearingDegrees = bearing;
            headingDegrees = RM_LeanKernel.HeadingFromSunBearing(bearing);
            RM_LeanKernel.Direction(headingDegrees, out float dirX, out float dirZ);
            cachedDir = new Vector2(dirX, dirZ);
        }

        public static RM_MapComponent_Lean For(Map map)
        {
            if (map == null || !RM_WindCalendar.On(RM_LeaningScrubSettings.leanEnabled))
            {
                return null;
            }
            RM_MapComponent_Lean lean = map.GetComponent<RM_MapComponent_Lean>();
            return lean != null && lean.Applies ? lean : null;
        }

        // Cosine between "from → to" and the downwind heading: 1 = straight downwind.
        public float Alignment(IntVec3 from, IntVec3 to)
        {
            Vector2 dir = Downwind;
            return RM_LeanKernel.Alignment(to.x - from.x, to.z - from.z, dir.x, dir.y);
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_TheLeanPatches
    {
        private const int FleeDistance = 24;

        static RM_TheLeanPatches()
        {
            Harmony harmony = new Harmony("mandrake.rm.leaningscrub");
            Patch(harmony, "lean-scent", AccessTools.Method(typeof(JobGiver_AnimalFlee), "TryGiveJob"),
                null, nameof(AnimalFlee_Postfix));
            Patch(harmony, "lean-fire", AccessTools.Method(typeof(Fire), "TrySpread"),
                nameof(TrySpread_Prefix), null);
        }

        private static void Patch(Harmony harmony, string rule, System.Reflection.MethodBase target, string prefix, string postfix)
        {
            if (target == null)
            {
                Log.Error("[RM LeaningScrub] " + rule + ": target method not found — rule NOT armed.");
                return;
            }
            try
            {
                harmony.Patch(target,
                    prefix: prefix == null ? null : new HarmonyMethod(typeof(RM_TheLeanPatches), prefix),
                    postfix: postfix == null ? null : new HarmonyMethod(typeof(RM_TheLeanPatches), postfix));
            }
            catch (Exception e)
            {
                Log.Error("[RM LeaningScrub] " + rule + ": patch failed, rule NOT armed. " + e);
            }
        }

        public static void AnimalFlee_Postfix(Pawn pawn, ref Job __result)
        {
            if (__result != null || pawn == null || pawn.Faction != null || !pawn.RaceProps.Animal
                || pawn.RaceProps.predator || pawn.Downed || !pawn.Spawned
                || !RM_LeaningScrubSettings.leanScentEnabled)
            {
                return;
            }
            RM_MapComponent_Lean lean = RM_MapComponent_Lean.For(pawn.Map);
            if (lean == null)
            {
                return;
            }
            float range = RM_LeaningScrubSettings.leanScentRange;
            IReadOnlyList<Pawn> people = pawn.Map.mapPawns.AllHumanlikeSpawned;
            int n = people.Count;
            int[] dx = new int[n], dz = new int[n];
            bool[] gone = new bool[n];
            for (int i = 0; i < n; i++)
            {
                Pawn h = people[i];
                // Scent runs from the person toward the animal along the wind.
                dx[i] = pawn.Position.x - h.Position.x;
                dz[i] = pawn.Position.z - h.Position.z;
                gone[i] = h.Dead || h.Downed;
            }
            Vector2 wind = lean.Downwind;
            Job found = null;
            RM_LeanKernel.FirstScentThreat(n, dx, dz, gone, range, wind.x, wind.y, i =>
            {
                Job flee = FleeUtility.FleeJob(pawn, people[i], FleeDistance);
                if (flee == null)
                {
                    return false;
                }
                found = flee;
                return true;
            });
            if (found != null)
            {
                __result = found;
            }
        }

        public static bool TrySpread_Prefix(Fire __instance)
        {
            if (!RM_LeaningScrubSettings.leanFireEnabled)
            {
                return true;
            }
            Map map = __instance.Map;
            RM_MapComponent_Lean lean = RM_MapComponent_Lean.For(map);
            if (lean == null)
            {
                return true;
            }
            IntVec3 pos = __instance.Position;
            Vector2 wind = lean.Downwind;
            int pick = RM_LeanKernel.FireSpreadPick(true, RM_LeaningScrubSettings.leanFireBias, Rand.Value, wind.x, wind.y, Rand.Value);
            if (pick < 0)
            {
                return true;
            }
            IntVec3 target = new IntVec3(pos.x + RM_LeanKernel.NeighbourDx[pick], 0, pos.z + RM_LeanKernel.NeighbourDz[pick]);
            if (target.InBounds(map) && Rand.Chance(FireUtility.ChanceToStartFireIn(target, map)))
            {
                FireUtility.TryStartFireIn(target, map, 0.1f, __instance.instigator);
            }
            return false;
        }
    }
}
