using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.ManyWaters
{
    // ════════════════════════════════════════════════════════════════════
    // WHICH BIOMES STEAM — the data hook.
    //
    // TRIGGERED BY: a <modExtensions><li Class="RimMandrake.FlowWorks.ManyWaters.RiverSteamBiomeExtension">
    // block on a BiomeDef. A biome that does not carry this extension gets
    // no river steam at all; this assembly names no biome of its own.
    //
    // The campaign's own wiring (the Pyrelands — RM_Pyrelands, our own
    // biome def) lives in the RimUtinni tier — src/RimUtinni/UtinniPatches/Patches/
    // (CORRECTED 2026-09-20, PYRELANDS_WRONG_BIOME_DEF_1: this comment's own
    // "RM_Pyrelands carries 222 tiles" claim, dated 2026-09-19, does not match
    // the canonical `world/ASHKARR_WORLDMAP_tiles.csv` — independently reparsed
    // today: RM_Pyrelands 0 tiles, ZBiome_Grasslands 222. Whether a live
    // `jawa/world_tile_set` switch on 2026-09-19 ever landed in that frozen CSV
    // is unreconciled; treat the CSV as authoritative until BENCH says otherwise.)
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

        // REVISED 2026-09-25 (owner, live look at the v1 build): a single
        // round "Steam" puff every 90-260 ticks read as "little choo-choo
        // train round clouds" — too rare, too opaque, wrong shape.
        // "SmokeGrowing" swells in over 6s instead of Steam's snappy 1.2s
        // reveal, which is a softer, less puff-like entrance for the same
        // underlying texture (Defs/Ideology/Effects/Fleck_Visual.xml,
        // ParentName="FleckBase_Thrown" — both use Things/Mote/Smoke).
        // Overridable so a biome can steam in its own colour/def once
        // ManyWaters ships flecks of its own.
        public string fleckDef = "SmokeGrowing";

        // PER-VENT interval now (see maxVents below), not per-map: tightened
        // from 90-260 so each vent column reads as a continuous, wavering
        // rise rather than a rare discrete event. INVENTED, tuned by eye.
        public IntRange ticksBetweenPuffs = new IntRange(20, 50);
        public FloatRange puffScale = new FloatRange(1f, 1.8f);
        public IntRange velocityAngle = new IntRange(70, 110);

        // Slowed from 0.15-0.3: a gentle standing rise reads more like heat
        // haze than a thrown puff.
        public FloatRange velocitySpeed = new FloatRange(0.05f, 0.15f);

        // NEW 2026-09-25. `FleckCreationData.exactScale` lets a fleck be
        // stretched non-uniformly (Verse/FleckCreationData.cs) — a thin,
        // tall sliver out of the same round Smoke texture reads as a rising
        // wisp/ribbon instead of a round cloud. Width and height are
        // independent ranges so each instance varies a little.
        public FloatRange ribbonWidth = new FloatRange(0.12f, 0.22f);
        public FloatRange ribbonHeight = new FloatRange(1.0f, 1.7f);

        // Lower per-instance opacity so several overlapping ribbons at
        // different ages/heights blend into a soft haze rather than
        // stacking as a series of visible discrete blobs — the "wavering
        // distortion" read the owner asked for is an emergent effect of
        // MANY faint overlapping instances, not one strong one.
        public FloatRange alpha = new FloatRange(0.30f, 0.50f);

        // Gentle side-to-side sway as each ribbon rises — the "oscillating"
        // half of the ask. Degrees/second, sign randomized per instance.
        public FloatRange wobbleDegreesPerSec = new FloatRange(4f, 10f);

        // How many persistent vent columns a river gets, spaced evenly
        // along its cells, instead of one puff hopping to a random river
        // cell each time. A handful of standing columns is what the
        // reference photo actually shows — mist rising from a few points
        // along the water, not scattered randomly across its whole length.
        // INVENTED — no figure was given, chosen so a modest river (a few
        // dozen cells) gets visibly separated columns rather than a solid
        // wall or a single lonely one.
        public int maxVents = 6;
    }

    // Ambient visual only: rivers on any biome that opts in (see the
    // extension above) throw periodic steam wisps from a handful of
    // persistent vent cells, per the owner's ask (RIVER_STEAM_ANIMATION_1).
    // Reuses the exact river-cell test RimWorld.SeasonalFlood already uses
    // (TerrainDef.IsRiver) -- no new art, no heat push, no gameplay effect.
    // MapComponent subclasses are auto-instantiated per map by
    // Map.FillComponents(), so no Harmony/XML registration is needed.
    public class MapComponent_RiverSteam : MapComponent
    {
        private List<IntVec3> vents;
        private int[] nextPuffTick;
        private FleckDef steamFleck;
        private RiverSteamBiomeExtension settings;

        public MapComponent_RiverSteam(Map map) : base(map)
        {
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            vents = new List<IntVec3>();

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
                settings.fleckDef.NullOrEmpty() ? "SmokeGrowing" : settings.fleckDef);
            if (steamFleck == null)
            {
                return;
            }

            List<IntVec3> riverCells = new List<IntVec3>();
            foreach (IntVec3 c in map.AllCells)
            {
                if (c.GetTerrain(map).IsRiver)
                {
                    riverCells.Add(c);
                }
            }

            if (riverCells.Count == 0)
            {
                return;
            }

            int ventCount = Mathf.Min(Mathf.Max(1, settings.maxVents), riverCells.Count);
            int stride = Mathf.Max(1, riverCells.Count / ventCount);
            for (int i = 0; i < riverCells.Count && vents.Count < ventCount; i += stride)
            {
                vents.Add(riverCells[i]);
            }

            nextPuffTick = new int[vents.Count];
            for (int i = 0; i < nextPuffTick.Length; i++)
            {
                // Staggered start so every vent doesn't puff on the same tick.
                nextPuffTick[i] = Find.TickManager.TicksGame + Rand.Range(0, settings.ticksBetweenPuffs.max);
            }
        }

        public override void MapComponentTick()
        {
            if (!RiverSteamSettings.riverSteamEnabled)
            {
                return; // mod option: river steam disabled
            }
            if (steamFleck == null || vents == null || vents.Count == 0)
            {
                return;
            }

            int now = Find.TickManager.TicksGame;
            for (int i = 0; i < vents.Count; i++)
            {
                if (now < nextPuffTick[i])
                {
                    continue;
                }

                IntVec3 cell = vents[i];
                if (!cell.Fogged(map))
                {
                    ThrowRibbon(cell);
                }

                float mult = Mathf.Max(0.01f, RiverSteamSettings.puffRateMultiplier);
                int interval = Mathf.Max(1, Mathf.RoundToInt(settings.ticksBetweenPuffs.RandomInRange / mult));
                nextPuffTick[i] = now + interval;
            }
        }

        private void ThrowRibbon(IntVec3 cell)
        {
            Vector3 loc = cell.ToVector3Shifted();
            FleckCreationData data = FleckMaker.GetDataStatic(
                loc, map, steamFleck, Rand.Range(settings.puffScale.min, settings.puffScale.max));

            // IntRange.RandomInRange (Rand.RangeInclusive) is inclusive of max; the
            // plain int overload Rand.Range(int,int) is NOT (maxExclusive) and was
            // silently dropping the top of the configured angle range.
            data.velocityAngle = settings.velocityAngle.RandomInRange;
            data.velocitySpeed = Rand.Range(settings.velocitySpeed.min, settings.velocitySpeed.max);
            data.rotationRate = Rand.Range(settings.wobbleDegreesPerSec.min, settings.wobbleDegreesPerSec.max)
                                 * (Rand.Bool ? 1f : -1f);

            float width = Rand.Range(settings.ribbonWidth.min, settings.ribbonWidth.max);
            float height = Rand.Range(settings.ribbonHeight.min, settings.ribbonHeight.max);
            data.exactScale = new Vector3(width, 1f, height);

            float a = Rand.Range(settings.alpha.min, settings.alpha.max);
            data.instanceColor = new Color(1f, 1f, 1f, a);

            map.flecks.CreateFleck(data);
        }
    }
}
