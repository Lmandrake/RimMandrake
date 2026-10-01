using System.Collections.Generic;
using Verse;

namespace RimMandrake.MovingDunes
{
    /// <summary>
    /// Biome opt-in. A BiomeDef carrying this extension makes every map generated in it
    /// a dune field, skinned with the named material. This is the whole binding surface
    /// — MOVING_DUNES_DESIGN.md §4: the engine mod ships the machinery plus one generic
    /// sand material and binds vanilla Desert/ExtremeDesert; data packs (RUT, a
    /// Pyrelands ash-dune biome) add materials and their own bindings.
    /// </summary>
    public class DuneFieldExtension : DefModExtension
    {
        /// <summary>The material this biome's maps drift. Required.</summary>
        public RM_DuneMaterialDef material;

        /// <summary>STILLSAND_WIND_SUN_BEARING_1: pin this biome's wind to the
        /// tile-to-substellar bearing (DuneWindBearing) instead of letting it shift,
        /// so crests, lees, shadows and the wind all point one way. The substellar
        /// point must match the biome's pinned sun (Ash'karr's is 0, 0). Gated by
        /// the Moving Dunes setting windLockEnabled.</summary>
        public bool lockBearingToSubstellar;
        public float substellarLatitude;
        public float substellarLongitude;

        /// <summary>Default false: the locked wind blows along the shadows (away
        /// from the sun), so dune lees fall on the shadow side.</summary>
        public bool windBlowsTowardSubstellar;

        /// <summary>STILLSAND_GLASS_LENS_CHAIN_1 §1: what a pawn shovelling drift off this
        /// biome's maps gets for it, or null for nothing (the sand simply leaves the field).
        /// Full yield, no loss factor (ruled by card 2026-09-30): every drift is stock.</summary>
        public ThingDef clearYield;

        /// <summary>Items of <see cref="clearYield"/> per unit of sand depth removed (a cell
        /// at full depth is 1.0). Fractions round randomly. Scaled by the Mod Settings slider.</summary>
        public float clearYieldPerDepth = 6f;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors())
            {
                yield return error;
            }
            if (material == null)
            {
                yield return "DuneFieldExtension.material is null — this biome would be marked a "
                    + "dune field with nothing to drift, which is worse than not opting in at all.";
            }
            if (clearYield != null && clearYieldPerDepth <= 0f)
            {
                yield return "DuneFieldExtension.clearYield is set but clearYieldPerDepth <= 0, so "
                    + "shovelling would never yield it.";
            }
        }
    }

    /// <summary>
    /// Per-weather override of the two storm multipliers. Attach to a WeatherDef
    /// (a violent windstorm) to make it move more sand than the material's own
    /// <c>stormTransportFactor</c> / <c>weatherInfluxFactor</c> would.
    /// A weather with no extension uses the material's values whenever its
    /// <c>sandRate</c> is live.
    /// </summary>
    public class DuneWeatherExtension : DefModExtension
    {
        /// <summary>K multiplier while this weather runs. Negative = use the material's.</summary>
        public float transportFactor = -1f;

        /// <summary>Windward influx multiplier while this weather runs. Negative = use
        /// the material's.</summary>
        public float influxFactor = -1f;

        /// <summary>Run the storm multipliers even if this weather's own
        /// <c>sandRate</c> is zero — for a dry, sand-free gale that still shifts a
        /// field that is already there.</summary>
        public bool forceStormTransport;
    }
}
