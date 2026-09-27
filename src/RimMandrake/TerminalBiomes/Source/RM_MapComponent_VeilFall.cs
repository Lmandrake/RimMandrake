using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_PANE_STRIKE_1 — "floor and deck are ONE pane system" (danger
    // pass §4). Two cheap, independent per-map tickers sharing one
    // MapComponent (auto-added to every Map by the engine; no def/registration
    // needed) so neither needs its own GameComponent:
    //
    //   (a) THE ORDINARY SHED CADENCE (D1a): "Most veil-fall is flakes and
    //       litter." Harmless RM_Filth_VeilFlakes, ambient dressing only —
    //       never damage, never a letter.
    //
    //   (b) THE LADEN DECK (D8): "panes are things landing on ship-footprint
    //       cells (D1's skyfaller, unmodified)" — the SAME lethal
    //       RM_VeilFallIncoming as the floor strike (RM_IncidentWorker_
    //       PaneStrike.cs), targeted at a gravship's own ValidSubstructure
    //       instead of a random floor cell. Purely additive to the
    //       Storyteller-scheduled RM_VeilFallPaneStrike IncidentDef, which
    //       can also happen to land on the ship on its own.
    //
    // NEVER A STRANDING (D8, binding bar): this class only ever SPAWNS a
    // pane on the deck. It never touches fuel, cooldown, substructure or the
    // engine in any way, and the clearing job the panes create (Deconstruct)
    // is a job the colony can always do. The actual launch DELAY lives
    // entirely in RM_Patch_GravEngineLaunchGate.cs's postfix, which only
    // ever downgrades an already-Accepted report — see that file's own
    // header for the full argument.
    //
    // Both halves no-op instantly off a non-Twilight-Sea map (the biome
    // check is the very first thing MapComponentTick does) or with their own
    // Mod Settings toggle off.
    public class RM_MapComponent_VeilFall : MapComponent
    {
        private const int TickInterval = 2500; // ~1 in-game hour.
        private const int MaxSubstructureAttempts = 20;

        private int nextShedTick = -1;
        private int nextDeckTick = -1;

        public RM_MapComponent_VeilFall(Map map) : base(map)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref nextShedTick, "nextShedTick", -1);
            Scribe_Values.Look(ref nextDeckTick, "nextDeckTick", -1);
        }

        public override void MapComponentTick()
        {
            // Cheapest possible early-out: string compare against the map's
            // OWN biome, no scan of anything. RM_TwilightSea only —
            // TERMINAL_SEAS_FLOOR_DRESSING_1's own biome, not any land tile.
            if (map.Biome == null || map.Biome.defName != "RM_TwilightSea")
            {
                return;
            }

            int now = Find.TickManager.TicksGame;
            if (nextShedTick < 0)
            {
                // First tick after map creation/load: stagger both timers
                // so every Twilight floor map doesn't roll on the exact
                // same absolute tick.
                nextShedTick = now + TickInterval + Rand.Range(0, TickInterval);
                nextDeckTick = now + TickInterval + Rand.Range(0, TickInterval);
                return;
            }

            if (now >= nextShedTick)
            {
                nextShedTick = now + TickInterval;
                TrySpawnLightShed();
            }
            if (now >= nextDeckTick)
            {
                nextDeckTick = now + TickInterval;
                TrySpawnDeckPane();
            }
        }

        // ── (a) the ordinary shed cadence ───────────────────────────────
        private void TrySpawnLightShed()
        {
            if (!RM_TerminalBiomesSettings.TwilightPaneStrikeActive)
            {
                return;
            }
            if (!Rand.Chance(0.35f * RM_TerminalBiomesSettings.twilightPaneStrikeFrequency))
            {
                return;
            }
            for (int i = 0; i < 6; i++)
            {
                IntVec3 cell = CellFinder.RandomCell(map);
                if (!cell.Standable(map) || cell.Fogged(map))
                {
                    continue;
                }
                FilthMaker.TryMakeFilth(cell, map, RM_VeilFallDefOf.RM_Filth_VeilFlakes);
                return;
            }
        }

        // ── (b) the laden deck ───────────────────────────────────────────
        private void TrySpawnDeckPane()
        {
            if (!RM_TerminalBiomesSettings.TwilightDeckAccumulationActive)
            {
                return;
            }
            ThingDef gravEngineDef = DefDatabase<ThingDef>.GetNamedSilentFail("GravEngine");
            if (gravEngineDef == null)
            {
                return; // Odyssey not installed -- nothing to accumulate on.
            }
            Building_GravEngine engine = map.listerThings.ThingsOfDef(gravEngineDef)
                .FirstOrDefault() as Building_GravEngine;
            if (engine == null || engine.ValidSubstructure.Count == 0)
            {
                return;
            }
            if (!Rand.Chance(0.25f * RM_TerminalBiomesSettings.twilightDeckAccumulationRate))
            {
                return;
            }
            if (!TryFindClearSubstructureCell(engine, out IntVec3 cell))
            {
                return;
            }
            SkyfallerMaker.SpawnSkyfaller(RM_VeilFallDefOf.RM_VeilFallIncoming, cell, map);
            Letter letter = LetterMaker.MakeLetter(
                "RM_VeilFallDeckLabel".Translate(),
                "RM_VeilFallDeckText".Translate(),
                LetterDefOf.ThreatBig,
                new TargetInfo(cell, map));
            Find.LetterStack.ReceiveLetter(letter);
        }

        private bool TryFindClearSubstructureCell(Building_GravEngine engine, out IntVec3 result)
        {
            List<IntVec3> candidates = engine.ValidSubstructure.ToList();
            int attempts = System.Math.Min(MaxSubstructureAttempts, candidates.Count);
            for (int i = 0; i < attempts; i++)
            {
                IntVec3 candidate = candidates[Rand.Range(0, candidates.Count)];
                if (IsClearFootprint(candidate, engine))
                {
                    result = candidate;
                    return true;
                }
            }
            result = IntVec3.Invalid;
            return false;
        }

        // Same footprint shape TryFindSkyfallerCell checks for the floor
        // strike (RM_VeilFallIncoming.size), restricted to cells the engine
        // itself counts as valid substructure — so a pane can never be
        // "accumulated" half off the ship's own deck.
        private bool IsClearFootprint(IntVec3 center, Building_GravEngine engine)
        {
            foreach (IntVec3 cell in GenAdj.OccupiedRect(center, Rot4.North, RM_VeilFallDefOf.RM_VeilFallIncoming.size))
            {
                if (!cell.InBounds(map) || !engine.ValidSubstructureAt(cell) || !cell.Standable(map))
                {
                    return false;
                }
                if (cell.GetFirstBuilding(map) != null || cell.GetFirstItem(map) != null || cell.GetFirstSkyfaller(map) != null)
                {
                    return false;
                }
            }
            return true;
        }
    }
}
