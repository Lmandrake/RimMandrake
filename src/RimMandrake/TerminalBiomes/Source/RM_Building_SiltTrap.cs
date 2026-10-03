using System.Collections.Generic;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_CHANNEL_CURRENT_1 §4. "Slows the margin water; over days it
    // raises the fertility of adjacent RM_BankSilt cells... the engine
    // route is a terrain swap to RM_BankSilt_Rich, the shipped idiom." Both
    // terrain defs are content drop §8.2's own job (not this item's — see
    // report), so every terrain lookup here is GetNamedSilentFail: absent,
    // the trap still stands, still clogs/unclogs, and simply has nothing to
    // paint yet.
    //
    // "Job: dredge (periodic, or the trap clogs and the bonus stalls)" is
    // folded into the same HP/repair mechanism the weir uses (see that
    // class's header) rather than a new WorkGiver: a clogged trap is one
    // whose HitPoints have fallen below the working threshold, and vanilla
    // WorkGiver_Repair already sends a colonist to bring it back up. This
    // is a build-time simplification of the spec's own "periodic" dredge,
    // not a ruling — the spec leaves the dredge's own mechanism unspecified.
    public class RM_Building_SiltTrap : Building
    {
        private const int RichenIntervalTicks = 30000; // "over days" — once every half a day
        private const int WearIntervalTicks = 3000;
        private const float WorkingHpFraction = 0.4f;
        private const float RichenRadius = 3.5f;

        private List<IntVec3> richened = new List<IntVec3>();

        protected override void Tick()
        {
            base.Tick();
            if (!RM_TerminalBiomesSettings.BankWorksActive)
            {
                return;
            }

            if (this.IsHashIntervalTick(WearIntervalTicks) && HitPoints > 1)
            {
                HitPoints = System.Math.Max(1, HitPoints - 1); // slow siltation, same "ordinary gnaw" shape as the weir
            }

            bool clogged = HitPoints < MaxHitPoints * WorkingHpFraction;
            if (!clogged && this.IsHashIntervalTick(RichenIntervalTicks))
            {
                RichenNearbyBankSilt();
            }
        }

        private void RichenNearbyBankSilt()
        {
            if (Map == null)
            {
                return;
            }
            TerrainDef plain = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_BankSilt");
            TerrainDef rich = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_BankSilt_Rich");
            if (plain == null || rich == null)
            {
                return;
            }
            foreach (IntVec3 c in GenRadial.RadialCellsAround(Position, RichenRadius, useCenter: false))
            {
                if (!c.InBounds(Map) || c.GetTerrain(Map) != plain)
                {
                    continue;
                }
                Map.terrainGrid.SetTerrain(c, rich);
                if (!richened.Contains(c))
                {
                    richened.Add(c);
                }
            }
        }

        // §4's breach effect (d): "the silt-trap's terrain bonus reverts."
        // Called by RM_Building_BankWeir on breach. Also usable directly as
        // this trap's own clog consequence if a future pass wants the
        // revert to happen locally rather than only via a nearby weir's
        // breach — kept public and idempotent for that reason.
        public void Clog()
        {
            if (Map == null || richened.Count == 0)
            {
                return;
            }
            TerrainDef plain = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_BankSilt");
            TerrainDef rich = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_BankSilt_Rich");
            if (plain == null)
            {
                return;
            }
            for (int i = 0; i < richened.Count; i++)
            {
                IntVec3 c = richened[i];
                // Only revert a cell still carrying the richened terrain we
                // painted — a floor (or anything else) the player built over
                // it since is not ours to overwrite.
                if (c.InBounds(Map) && (rich == null || c.GetTerrain(Map) == rich))
                {
                    Map.terrainGrid.SetTerrain(c, plain);
                }
            }
            richened.Clear();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref richened, "richened", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && richened == null)
            {
                richened = new List<IntVec3>();
            }
        }
    }
}
