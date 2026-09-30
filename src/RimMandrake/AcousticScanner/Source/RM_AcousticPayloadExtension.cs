using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.AcousticScanner
{
    // GRAVSHIP_ACOUSTIC_SCANNER_1 — "What it finds depends on the biome. Each biome
    // supplies its own payload through a def extension on the BiomeDef, so adding a
    // biome is XML."
    //
    // A biome with no extension gives the plain "nothing unusual" reading
    // (RM_Acoustic_NothingUnusual). Every reference to another mod's content is a
    // defName STRING resolved with GetNamedSilentFail at pulse time, never a Def
    // cross-reference, so a payload naming a def from an inactive mod loads clean
    // and simply hears nothing of that kind.
    //
    // Shipped payloads are PATCHES in each biome's own mod, guarded by
    // PatchOperationFindMod on mandrake.rm.acousticscanner (so this class is never
    // named in a def while its assembly is absent):
    //   src/RimMandrake/FloodedCanyon/Patches/RM_AcousticPayload_FloodedCanyon.xml
    //   src/RimMandrake/Stillsand/Patches/RM_AcousticPayload_Stillsand.xml
    //   src/RimUtinni/UtinniPatches/Patches/AcousticPayload_CrackedLands.xml
    public class RM_AcousticPayloadExtension : DefModExtension
    {
        public List<RM_AcousticTarget> targets = new List<RM_AcousticTarget>();

        /// <summary>Optional biome-flavoured line for a pulse that hears none of its targets.</summary>
        [MustTranslate]
        public string quietText;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (targets.NullOrEmpty())
            {
                yield return "RM_AcousticPayloadExtension has no targets";
                yield break;
            }
            for (int i = 0; i < targets.Count; i++)
            {
                RM_AcousticTarget t = targets[i];
                if (t == null) { yield return "null target at index " + i; continue; }
                if (t.label.NullOrEmpty()) yield return "target " + i + " has no label";
                if (!t.HasAnyMatcher) yield return "target '" + t.label + "' matches nothing (no thingDefs/pawnRaces/terrainDefs/hiddenCaves)";
            }
        }
    }

    /// <summary>One kind of thing a biome's ground can give back to a sounding pulse.
    /// Subclass (XML Class attribute) and override CollectCells for a matcher the
    /// generic fields cannot express; everything the shipped payloads need is here.</summary>
    public class RM_AcousticTarget
    {
        [MustTranslate] public string label;
        /// <summary>Line appended to the reading letter when this target is heard.</summary>
        [MustTranslate] public string reading;
        public Color color = new Color(0.55f, 0.8f, 1f);
        /// <summary>Per-hit weight; a band's tier is its summed weight against the pulse's strongest band.</summary>
        public float weight = 1f;

        /// <summary>ThingDef defNames (spawned things, buildings, plants).</summary>
        public List<string> thingDefs = new List<string>();
        /// <summary>Race ThingDef defNames of living pawns (swimmers, sleepers).</summary>
        public List<string> pawnRaces = new List<string>();
        /// <summary>TerrainDef defNames.</summary>
        public List<string> terrainDefs = new List<string>();
        /// <summary>Standable cells under a natural rock roof that are still fogged — unopened caverns.</summary>
        public bool hiddenCaves;
        /// <summary>Only count terrain/thing cells that are still fogged (the player cannot already see them).</summary>
        public bool onlyFogged;
        /// <summary>Sample 1 in N matching terrain/cave cells, so a large pool does not drown point targets.</summary>
        public int cellSampleStride = 3;

        public bool HasAnyMatcher => !thingDefs.NullOrEmpty() || !pawnRaces.NullOrEmpty()
            || !terrainDefs.NullOrEmpty() || hiddenCaves;

        public virtual void CollectCells(Map map, IntVec3 origin, float range, List<IntVec3> into)
        {
            float rangeSq = range * range;
            bool InRange(IntVec3 c) => (c - origin).LengthHorizontalSquared <= rangeSq;

            if (!thingDefs.NullOrEmpty())
            {
                for (int i = 0; i < thingDefs.Count; i++)
                {
                    ThingDef td = DefDatabase<ThingDef>.GetNamedSilentFail(thingDefs[i]);
                    if (td == null) continue;
                    List<Thing> things = map.listerThings.ThingsOfDef(td);
                    for (int j = 0; j < things.Count; j++)
                    {
                        IntVec3 c = things[j].Position;
                        if (!c.InBounds(map) || !InRange(c)) continue;
                        if (onlyFogged && !c.Fogged(map)) continue;
                        into.Add(c);
                    }
                }
            }

            if (!pawnRaces.NullOrEmpty())
            {
                var races = new HashSet<ThingDef>();
                for (int i = 0; i < pawnRaces.Count; i++)
                {
                    ThingDef rd = DefDatabase<ThingDef>.GetNamedSilentFail(pawnRaces[i]);
                    if (rd != null) races.Add(rd);
                }
                if (races.Count > 0)
                {
                    IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
                    for (int i = 0; i < pawns.Count; i++)
                    {
                        Pawn p = pawns[i];
                        if (p.Dead || !races.Contains(p.def)) continue;
                        if (p.Faction != null && p.Faction.IsPlayer) continue;
                        if (!InRange(p.Position)) continue;
                        into.Add(p.Position);
                    }
                }
            }

            bool wantTerrain = !terrainDefs.NullOrEmpty();
            if (!wantTerrain && !hiddenCaves) return;

            var terrains = new HashSet<TerrainDef>();
            if (wantTerrain)
            {
                for (int i = 0; i < terrainDefs.Count; i++)
                {
                    TerrainDef t = DefDatabase<TerrainDef>.GetNamedSilentFail(terrainDefs[i]);
                    if (t != null) terrains.Add(t);
                }
            }
            if (terrains.Count == 0 && !hiddenCaves) return;

            int stride = Mathf.Max(1, cellSampleStride);
            int n = 0;
            // A clipped rect, not GenRadial: the radial pattern table is shorter
            // than the settings' range ceiling.
            foreach (IntVec3 c in CellRect.CenteredOn(origin, Mathf.CeilToInt(range)).ClipInsideMap(map))
            {
                if (!InRange(c)) continue;
                bool hit = false;
                if (terrains.Count > 0 && terrains.Contains(c.GetTerrain(map)))
                {
                    hit = !onlyFogged || c.Fogged(map);
                }
                if (!hit && hiddenCaves && c.Fogged(map))
                {
                    RoofDef roof = c.GetRoof(map);
                    hit = roof != null && roof.isNatural && c.Standable(map);
                }
                if (hit && (n++ % stride) == 0)
                {
                    into.Add(c);
                }
            }
        }
    }
}
