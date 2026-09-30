using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // LONGSHADE_BEDAZZLE_MECHANICS_1 part 1 — "Golden hour" (owner, turn 2:
    // "I like the golden hour concept. A perpetual beautiful sunset.").
    // Design: design/Jawa/worldbuilding/biomes/longshade_shade_ideation_2026-09-29.md
    // §3.1–3.2 and §1.3.
    //
    // A BiomeDef-side extension. A biome that carries it gets, on every map of
    // that biome, a PINNED SUN: one fixed sky (glow + colour set) that never
    // turns to night, and one fixed shadow vector that every building, rock
    // and tree with staticSunShadowHeight renders along, forever.
    //
    // The pinned vector is ALSO the mechanical one. RM_MapComponent_PinnedSun
    // exposes ShadowDirection / ShadowLengthPerHeight for the directional
    // shade grid (SOLAR_HEAT_EXPOSURE_1 spec 3) to cast along, so the shade the
    // player sees and the shade animals use are the same cells. This file and
    // its map component build only the sky + the vector; the directional grid
    // itself is that item's scope, not this one's.
    //
    // Kit mechanic, not a Long Shade hard-code: any biome can carry it (the
    // Deep Desert's low sun is the obvious second consumer), and it is gated
    // in this assembly's own Mod Settings (pinnedSunEnabled).
    //
    // Every number here is XML-tunable and INVENTED as a first value — the
    // owner tunes the look by watching it in game.
    // ════════════════════════════════════════════════════════════════════
    public class RM_PinnedSunExtension : DefModExtension
    {
        // ── where the sun is ────────────────────────────────────────────
        /// <summary>The sunward point on the planet, degrees. The sun's
        /// bearing on a map is the great-circle bearing from the map's tile
        /// toward this point, and its elevation is 90° minus the arc between
        /// them — so on a tidally locked world every map's shadows point away
        /// from the substellar point, consistent planet-wide (§3.1 "per-map
        /// orientation"). Ash'karr's substellar point is (0, 0)
        /// (the_one_map.md reconciliation; the WeatherSuite's PlanetGeometryDef
        /// carries the same numbers for the Star Wars tier).</summary>
        public float substellarLatitude = 0f;
        public float substellarLongitude = 0f;

        /// <summary>Sun elevation clamp, degrees. A Long Shade tile sits at
        /// arc ~60–88° (§3.1), i.e. elevation 2–30°.</summary>
        public float minElevationDegrees = 2f;
        public float maxElevationDegrees = 30f;

        // ── the rendered shadow ─────────────────────────────────────────
        /// <summary>Rendered shadow-vector length = cot(elevation) ×
        /// renderLengthScale, clamped to [minRenderLength, maxRenderLength].
        /// Vanilla's own dusk vector is ~16.6 long (GenCelestial,
        /// ShadowMaxLengthDay 15 on its horizontal axis).</summary>
        public float renderLengthScale = 1f;
        public float minRenderLength = 1.5f;
        public float maxRenderLength = 15f;

        /// <summary>Shadow opacity pinned for the whole day (vanilla drives
        /// it from the real sun glow, which would fade the shadows to nothing
        /// at the engine's own "dusk" 0.6 threshold).</summary>
        public float shadowStrength = 1f;

        // ── the sky ─────────────────────────────────────────────────────
        /// <summary>Fixed sky glow. Plant growth reads it through GlowGrid
        /// (vanilla growMinGlow 0.51 → optimal 1.0), so this is the growth
        /// dial as much as the light dial — tune by looking and by crops.</summary>
        public float glow = 0.8f;

        /// <summary>Apricot-rose sky light (the sheet's warm half).</summary>
        public Color skyColor = new Color(1f, 0.80f, 0.62f);

        /// <summary>Cool violet-blue shadows (the sheet's cool half —
        /// "amber, ochre and rust against long cool blue shadows").</summary>
        public Color shadowColor = new Color(0.52f, 0.48f, 0.72f);

        /// <summary>Warm overlay tint applied to weather overlays.</summary>
        public Color overlayColor = new Color(1f, 0.86f, 0.70f);

        public float saturation = 1.1f;

        /// <summary>Sun-shine draw on the horizon: large and soft reads as a
        /// sun sitting on the horizon (§3.2).</summary>
        public float lightsourceShineSize = 2.5f;
        public float lightsourceShineIntensity = 0.8f;

        /// <summary>How strongly the pinned sky overrides the weather's own
        /// sky, 0..1, before the Mod Settings strength dial.</summary>
        public float lerpFactor = 1f;
    }
}
