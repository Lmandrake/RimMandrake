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
