using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // SOLAR_HEAT_EXPOSURE_1 §2 — the per-biome heat kind.
    //
    // Owner ruling (longshade_shade_ideation_2026-09-29.md, "Rulings —
    // volley turn 4"): heat is ONE kind, planet-wide. Sun exposure feeds the
    // game's EXISTING heat — it raises what a pawn feels (AmbientTemperature),
    // so the vanilla comfortable range, apparel insulation and Heatstroke
    // keep their vanilla meaning. There is no sun hediff. What differs per
    // biome is only what PROTECTS you:
    //   overhead — the Long Shade: roofs and cast shade.
    //   lowSun   — the Deep Desert: only a vertical caster's lee shadow.
    //   ambient  — steam / volcanic: shade does nothing; insulation or an
    //              enclosed room.
    //
    // A BiomeDef that carries this extension IS a sun-heat biome. Every
    // map-wide effect (heat, sun-cost pathing, the sun-load readout) is gated
    // on it, and on the Creature Behaviors settings. Wire it with
    // MayRequire="mandrake.rm.creaturebehaviors" on the <li>, as the Long
    // Shade does for RM_PinnedSunExtension.
    //
    // All numbers are INVENTED first values; the owner-watched sitting in
    // the item's criteria rules on the strictness.
    // ════════════════════════════════════════════════════════════════════
    public class RM_SunHeatExtension : DefModExtension
    {
        public RM_HeatKind heatKind = RM_HeatKind.overhead;

        /// <summary>°C added to a size-1 pawn's felt temperature at full
        /// exposure, before the Mod Settings strength dial.</summary>
        public float heatOffsetC = 30f;

        /// <summary>Hard cap on the offset after the body-size term.</summary>
        public float maxHeatOffsetC = 70f;

        /// <summary>Offset × (1 / bodySize)^this. 0 = size does not matter.</summary>
        public float bodySizeExponent = 0.5f;
        public float minBodySizeFactor = 0.25f;
        public float maxBodySizeFactor = 2.5f;

        /// <summary>Extra path cost per fully exposed cell (a cardinal step
        /// costs 13), before the Mod Settings path dial. Ignored for
        /// ambient heat, where shade is not worth a detour.</summary>
        public float sunPathCostPerCell = 20f;

        // ── the sun, when the biome has no pinned sun ───────────────────
        /// <summary>Used ONLY when the map has no active RM_PinnedSunExtension
        /// (which is preferred, because then the rendered shadows and the
        /// mechanical shade are the same cells). Same geometry as the pinned
        /// sun: bearing and arc from the map's tile to the substellar point.</summary>
        public float substellarLatitude = 0f;
        public float substellarLongitude = 0f;
        public float minElevationDegrees = 5f;
        public float maxElevationDegrees = 60f;
    }
}
