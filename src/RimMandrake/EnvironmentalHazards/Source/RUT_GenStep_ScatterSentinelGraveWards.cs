using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SCARLANDS_MECHANICS_2 build pass continuation (2026-09-26). Closes the
    // gap RUT_SentinelGraveWard.xml's own header flagged as "OWED, NOT
    // BUILT: faction assignment" — CompSpawnerPawn.TrySpawnPawn spawns with
    // parent.Faction (decompile-confirmed), so without this GenStep the
    // grave-ward is never even placed on a map, and if debug-spawned by hand
    // it produces faction-less ("wild") Sentinels: not hostile, not the
    // scoped defend-only behavior the sheet describes.
    //
    // Same shape as RustCathedral's own GenStep_ScatterSacredWalls (same
    // "Forgotten"/Cathedral lore family, src/RimMandrake/RustCathedral/
    // Source/Walls/GenStep_ScatterSacredWalls.cs) — a plain GenStep rather
    // than a GenStep_ScatterGroup subclass, because the vanilla scatter
    // classes have no hook to call SetFaction on what they place.
    // Faction.OfMechanoids is the SAME faction that precedent already uses
    // (vanilla Mechanoid, hidden/permanentEnemy, reskinned "the Forgotten
    // Arsenal" per src/RimUtinni/UtinniPatches/Patches/ForgottenArsenal.xml)
    // — not a new faction, exactly as the grave-ward's own header called
    // "very likely the correct one for this building too."
    //
    // Density per scarlands_kit_spec.md §4 (owner, legends sitting
    // 2026-09-11): SPARSE — "most strongpoints are bones, the manned one is
    // the exception... the repair alcove reads as SELF-REPAIR." chancePerMap/
    // countRange below copy GenStep_ScatterSacredWalls' own figures verbatim
    // (same sparse-density intent, same lore family, no new number invented).
    //
    // Targets RUT_Scarlands only (the frozen campaign twin), never
    // RM_Warscar (SCARLANDS_STANDALONE_MOD_1's franchise-free mod) — that
    // mod's own header states outright that this kit's campaign-mechanic
    // content ("the frozen twin's scaria-mark mechanic and pre-sprung ruin
    // dressing") stays UtinniPatches-only, and the Sentinel grave-ward is
    // the same class of content, never carried into RM_Warscar's extraGenSteps.
    public class RUT_GenStep_ScatterSentinelGraveWards : GenStep
    {
        public const string ScarlandsBiomeDefName = "RUT_Scarlands";

        public ThingDef thingDef;

        public float chancePerMap = 0.15f;

        public IntRange countRange = new IntRange(1, 1);

        public int minEdgeDistance = 8;

        public override int SeedPart => 1926604817;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_EnvironmentalHazardsSettings.sentinelGraveWardsEnabled)
            {
                return;
            }
            if (map.Biome == null || map.Biome.defName != ScarlandsBiomeDefName)
            {
                return;
            }
            if (thingDef == null)
            {
                Log.Error("[RM EnvironmentalHazards] RUT_GenStep_ScatterSentinelGraveWards has no thingDef configured.");
                return;
            }
            if (!Rand.Chance(chancePerMap))
            {
                return;
            }

            Faction sentinelOwner = Faction.OfMechanoids;
            int count = countRange.RandomInRange;
            for (int i = 0; i < count; i++)
            {
                if (!CellFinderLoose.TryFindRandomNotEdgeCellWith(minEdgeDistance,
                        (IntVec3 c) => CanPlaceAt(c, map), map, out IntVec3 cell))
                {
                    continue;
                }

                Thing ward = ThingMaker.MakeThing(thingDef);
                GenSpawn.Spawn(ward, cell, map, WipeMode.Vanish);
                // Faction ownership is what lets CompSpawnerPawn's spawned
                // Sentinels inherit a real, hostile-to-nobody-until-provoked
                // faction (parent.Faction, decompile-confirmed) instead of
                // spawning wild — same mechanism note as
                // GenStep_ScatterSacredWalls.
                if (sentinelOwner != null)
                {
                    ward.SetFaction(sentinelOwner);
                }
            }
        }

        private bool CanPlaceAt(IntVec3 c, Map map)
        {
            if (!c.Standable(map))
            {
                return false;
            }
            if (!c.GetAffordances(map).Contains(thingDef.terrainAffordanceNeeded))
            {
                return false;
            }
            foreach (Thing t in c.GetThingList(map))
            {
                if (t.def.category == ThingCategory.Building)
                {
                    return false;
                }
            }
            return true;
        }
    }
}
