using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ManyWaters
{
    // ════════════════════════════════════════════════════════════════════
    // WHICH BIOMES STEAM — the data hook.
    //
    // TRIGGERED BY: a <modExtensions><li Class="RimMandrake.ManyWaters.RiverSteamBiomeExtension">
    // block on a BiomeDef. A biome that does not carry this extension gets
    // no river steam at all; this assembly names no biome of its own.
    //
    // The campaign's own wiring (the Pyrelands, ZBiome_Grasslands) lives in
    // the RimUtinni tier — src/RimUtinni/UtinniPatches/Patches/
    // ManyWaters_RiverSteam_Ashkarr.xml — not here, because ManyWaters is a
    // RimMandrake-tier engine and must run on any game, any biome.
    //
    // ⚠️ Every default below is the value this engine shipped with while the
    // biome was hardcoded. A biome that declares the extension and overrides
    // nothing therefore gets byte-identical behaviour to the old build.
    // ════════════════════════════════════════════════════════════════════
    public class RiverSteamBiomeExtension : DefModExtension
    {
        // Present-but-off, so a biome can be listed and muted without the
        // patch that added it having to be removed.
        public bool riverSteam = true;

        // Vanilla's own "Steam" FleckDef (Defs/Ideology/Effects/Fleck_Visual.xml,
        // ParentName="FleckBase_Thrown"). Overridable so a biome can steam in
        // its own colour once ManyWaters ships flecks of its own.
        public string fleckDef = "Steam";

        public IntRange ticksBetweenPuffs = new IntRange(90, 260);
        public FloatRange puffScale = new FloatRange(1f, 1.8f);
        public IntRange velocityAngle = new IntRange(60, 120);
        public FloatRange velocitySpeed = new FloatRange(0.15f, 0.3f);
    }

    // Ambient visual only: rivers on any biome that opts in (see the
    // extension above) throw periodic steam puffs, per the owner's ask
    // (RIVER_STEAM_ANIMATION_1). Reuses the exact river-cell test
    // RimWorld.SeasonalFlood already uses (TerrainDef.IsRiver) -- no new art,
    // no heat push, no gameplay effect. MapComponent subclasses are
    // auto-instantiated per map by Map.FillComponents(), so no Harmony/XML
    // registration is needed.
    public class MapComponent_RiverSteam : MapComponent
    {
        private List<IntVec3> riverCells;
        private int nextPuffTick = -1;
        private FleckDef steamFleck;
        private RiverSteamBiomeExtension settings;

        public MapComponent_RiverSteam(Map map) : base(map)
        {
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            riverCells = new List<IntVec3>();

            // Data-driven, not a biome defName in C#: this component exists on
            // EVERY map in every save, so the not-my-biome path stays a single
            // extension lookup and an early return.
            if (map.Biome == null)
            {
                return;
            }
            settings = map.Biome.GetModExtension<RiverSteamBiomeExtension>();
            if (settings == null || !settings.riverSteam)
            {
                return;
            }

            steamFleck = DefDatabase<FleckDef>.GetNamedSilentFail(
                settings.fleckDef.NullOrEmpty() ? "Steam" : settings.fleckDef);
            if (steamFleck == null)
            {
                return;
            }

            foreach (IntVec3 c in map.AllCells)
            {
                if (c.GetTerrain(map).IsRiver)
                {
                    riverCells.Add(c);
                }
            }

            ScheduleNext();
        }

        public override void MapComponentTick()
        {
            if (steamFleck == null || riverCells == null || riverCells.Count == 0)
            {
                return;
            }

            if (Find.TickManager.TicksGame < nextPuffTick)
            {
                return;
            }

            IntVec3 cell = riverCells[Rand.Range(0, riverCells.Count)];
            if (!cell.Fogged(map))
            {
                Vector3 loc = cell.ToVector3Shifted();
                FleckCreationData data = FleckMaker.GetDataStatic(
                    loc, map, steamFleck, Rand.Range(settings.puffScale.min, settings.puffScale.max));
                // IntRange.RandomInRange (Rand.RangeInclusive) is inclusive of max; the
                // plain int overload Rand.Range(int,int) is NOT (maxExclusive) and was
                // silently dropping the top of the configured angle range.
                data.velocityAngle = settings.velocityAngle.RandomInRange;
                data.velocitySpeed = Rand.Range(settings.velocitySpeed.min, settings.velocitySpeed.max);
                map.flecks.CreateFleck(data);
            }

            ScheduleNext();
        }

        private void ScheduleNext()
        {
            nextPuffTick = Find.TickManager.TicksGame + settings.ticksBetweenPuffs.RandomInRange;
        }
    }
}
