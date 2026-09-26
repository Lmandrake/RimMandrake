using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Sarlacc
{
    /// <summary>
    /// SARLACC_HABITAT_BUILD_1, Fork 6 (draft §8, sarlacc_native_habitat_draft.md):
    /// "DBH thirst is in the shipped list, so the breach flood is fillable at launch."
    ///
    /// Verified mechanism (not guessed): `dubwise.dubsbadhygiene.lite` +
    /// `.thirst` ship a real `NeedDef` (`defName="DBHThirst"`, `needClass=
    /// "DubsBadHygiene.Need_Thirst"`, `Defs/NeedDefs/Needs_Misc.xml`) and a
    /// `DubsBadHygiene.JobDriver_DrinkFromGround` driven by
    /// `DubsBadHygiene.JobGiver_DrinkWater`. Both are decompiled-confirmed to key off
    /// `Verse.TerrainDef.IsWater` (`=> HasTag("Water")`, vanilla, `Source/Verse/TerrainDef.cs`)
    /// rather than any DBH-specific terrain list — so painting real `WaterShallow`
    /// (tags: Water/WaterFreshShallow/WaterFreshShallowStill) makes the flood a genuine,
    /// autonomously-found drink source with **no assembly reference to DBH at all**: this
    /// mod never needs DBH loaded to be correct, and never breaks if it isn't.
    ///
    /// This replaces the earlier cosmetic-only `Filth_Water` spread
    /// (`CompSarlaccCisternBreach`) with real, temporary terrain — legal under
    /// `deep_desert.md` §6 ban 5's own sarlacc carve-out ("the breach flood (transient...)").
    /// Reverts each cell to what it was before, on the draft's own clock: §4.4's "the
    /// ground blooms within hours and is dead again within days," concretely the
    /// draft's own worked number, "a three-day garden" (§4.4 point 2).
    /// </summary>
    public class MapComponent_SarlaccBreachFlood : MapComponent
    {
        private const int FloodLifetimeTicks = GenDate.TicksPerDay * 3; // "a three-day garden"
        private const int RevertCheckInterval = 250;

        // Not readonly: Scribe_Collections.Look reassigns these on load.
        private List<IntVec3> floodedCells = new List<IntVec3>();
        private List<TerrainDef> originalTerrain = new List<TerrainDef>();
        private List<int> revertAtTick = new List<int>();

        public MapComponent_SarlaccBreachFlood(Map map) : base(map)
        {
        }

        /// <summary>Paint <paramref name="floodTerrain"/> over standable cells in radius, remembering
        /// what was there so it can be restored once the flood dies on its own clock.</summary>
        public void Flood(IntVec3 center, float radius, TerrainDef floodTerrain)
        {
            if (map?.terrainGrid == null)
            {
                return;
            }
            int revertTick = Find.TickManager.TicksGame + FloodLifetimeTicks;
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(center, radius, useCenter: true))
            {
                if (!cell.InBounds(map) || !cell.Standable(map))
                {
                    continue;
                }
                TerrainDef existing = cell.GetTerrain(map);
                if (existing == floodTerrain)
                {
                    continue;
                }
                floodedCells.Add(cell);
                originalTerrain.Add(existing);
                revertAtTick.Add(revertTick);
                map.terrainGrid.SetTerrain(cell, floodTerrain);
            }
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (floodedCells.Count == 0 || Find.TickManager.TicksGame % RevertCheckInterval != 0)
            {
                return;
            }
            for (int i = floodedCells.Count - 1; i >= 0; i--)
            {
                if (Find.TickManager.TicksGame < revertAtTick[i])
                {
                    continue;
                }
                IntVec3 cell = floodedCells[i];
                // v1 simplification: revert unconditionally on expiry, even if the player
                // has since built or terraformed over it — the flood's own clock always wins.
                if (cell.InBounds(map))
                {
                    map.terrainGrid.SetTerrain(cell, originalTerrain[i]);
                }
                floodedCells.RemoveAt(i);
                originalTerrain.RemoveAt(i);
                revertAtTick.RemoveAt(i);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref floodedCells, "rswFloodedCells", LookMode.Value);
            Scribe_Collections.Look(ref originalTerrain, "rswFloodOriginalTerrain", LookMode.Def);
            Scribe_Collections.Look(ref revertAtTick, "rswFloodRevertAtTick", LookMode.Value);
        }
    }
}
