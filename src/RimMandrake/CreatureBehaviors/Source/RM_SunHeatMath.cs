using System;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // SOLAR_HEAT_EXPOSURE_1 — the pure arithmetic of sun heat.
    //
    // No Verse/Unity dependency on purpose (System.Math only): the offline
    // selftest (Source/SelfTest, run by Utils/selftest_sun_heat.py) compiles
    // this exact file and checks sun vs shade vs roofed, the three heat
    // kinds, the body-size term, the path cost and the directional cast.
    // Every live caller (RM_MapComponent_ShadeGrid, RM_SunHeatPatches)
    // routes through these functions, so what the selftest checks is what
    // the game runs.
    // ════════════════════════════════════════════════════════════════════
    public enum RM_HeatKind
    {
        /// <summary>The Long Shade: roofs AND cast (lee) shade both protect.</summary>
        overhead,

        /// <summary>The Deep Desert: only a vertical caster's lee shadow
        /// protects. A constructed roof overhead gives nothing; being inside
        /// rock (a thick natural roof) still counts, because that is walls,
        /// not overhead shade.</summary>
        lowSun,

        /// <summary>Steam and volcanic heat: shade does nothing. Only
        /// insulation (vanilla comfortable range) or leaving the open air —
        /// an enclosed room — helps.</summary>
        ambient,
    }

    public static class RM_SunHeatMath
    {
        /// <summary>A PathGridJob custom cost at or above this makes the cell
        /// impassable (decompiled 1.6 PathGridJob: custom[index] >= 10000).
        /// Sun cost is always kept well under it.</summary>
        public const int ImpassableCustomCost = 10000;

        public const int MaxSunPathCost = 2000;

        /// <summary>0 (fully sheltered) .. 1 (full sun) for one cell.
        /// outdoors: the cell's room uses outdoor temperature — an enclosed
        /// room is never exposed, whatever the kind (that is vanilla's own
        /// "leaving" the open air). roofShade: 1 under any roof, else 0.
        /// thickRoof: the roof is natural overhead rock. castShade: 0..1 from
        /// the directional grid.</summary>
        public static float Exposure(RM_HeatKind kind, bool outdoors, float roofShade, bool thickRoof, float castShade)
        {
            if (!outdoors)
            {
                return 0f;
            }
            float cover;
            switch (kind)
            {
                case RM_HeatKind.ambient:
                    cover = 0f;
                    break;
                case RM_HeatKind.lowSun:
                    cover = Math.Max(thickRoof ? 1f : 0f, castShade);
                    break;
                default:
                    cover = Math.Max(roofShade, castShade);
                    break;
            }
            return Clamp01(1f - Clamp01(cover));
        }

        /// <summary>Body-size factor on sun heat: (1 / bodySize)^exponent,
        /// clamped to [minFactor, maxFactor]. Size 1 = 1×; a small animal
        /// heats faster, a megafauna slower — the whole of "dash range is a
        /// function of size" (§1.2).</summary>
        public static float BodySizeFactor(float bodySize, float exponent, float minFactor, float maxFactor)
        {
            if (bodySize <= 0.01f)
            {
                bodySize = 0.01f;
            }
            float f = (float)Math.Pow(1.0 / bodySize, exponent);
            if (f < minFactor) { f = minFactor; }
            if (f > maxFactor) { f = maxFactor; }
            return f;
        }

        /// <summary>Degrees C added to what the pawn feels (its
        /// AmbientTemperature), which is the ONLY input the vanilla
        /// comfort/Heatstroke path reads. exposure × baseOffset × strength ×
        /// body-size factor, capped at maxOffset.</summary>
        public static float HeatOffset(float exposure, float baseOffsetC, float strength, float bodySizeFactor, float maxOffsetC)
        {
            if (exposure <= 0f || baseOffsetC <= 0f || strength <= 0f)
            {
                return 0f;
            }
            float off = Clamp01(exposure) * baseOffsetC * strength * bodySizeFactor;
            return off > maxOffsetC ? maxOffsetC : off;
        }

        /// <summary>Per-cell path cost offset (PathGridJob adds it to the
        /// cell's move cost; vanilla cardinal step is 13). exposure ×
        /// costPerCell × strength, rounded, clamped to [0, MaxSunPathCost].</summary>
        public static ushort PathCost(float exposure, float costPerCell, float strength)
        {
            float c = Clamp01(exposure) * costPerCell * strength;
            if (c <= 0f)
            {
                return 0;
            }
            int i = (int)Math.Round(c);
            if (i > MaxSunPathCost) { i = MaxSunPathCost; }
            return (ushort)i;
        }

        /// <summary>Shadow length in cells for a caster of the given height
        /// (staticSunShadowHeight scale: a rock or wall is 1.0) under a sun
        /// whose ground shadow is lengthPerHeight cells per unit height.</summary>
        public static float ShadowLength(float casterHeight, float lengthPerHeight, float maxCells)
        {
            float l = casterHeight * lengthPerHeight;
            if (l < 0f) { l = 0f; }
            return l > maxCells ? maxCells : l;
        }

        /// <summary>
        /// Casts one caster's shadow into a row-major grid (index = z * width
        /// + x, the same layout as CellIndices), marching from the caster
        /// along (dirX, dirZ) — the way shadows fall, away from the sun — for
        /// `length` cells. Full shade (1) along the body of the shadow, easing
        /// to tipShade at the far end. Keeps the max of what is already
        /// there, so overlapping shadows never lighten each other. The caster
        /// cell itself is not written (a rock is not standing room).
        /// </summary>
        public static void CastInto(float[] grid, int width, int height, int cx, int cz,
            float dirX, float dirZ, float length, float tipShade)
        {
            // Half-cell steps so a diagonal shadow leaves no gaps (the depth
            // overload below holds the one implementation).
            CastInto(grid, width, height, cx, cz, dirX, dirZ, length, tipShade, 1f);
        }

        // ── SHADE_GEAR_FAMILY_1: carried and pitched shade ──────────────
        // Parasol, shade tent and sun shield all feed the SAME exposure rule
        // above: their shade is one more cover term. What differs per biome
        // is only how much of each piece's shade counts, by heat kind.

        /// <summary>How much of a gear piece's shade counts under this heat
        /// kind: overheadFactor under overhead sun, lowSunFactor under a low
        /// sun, and always 0 under ambient heat (steam, volcanic), where no
        /// shade of any kind helps.</summary>
        public static float GearKindFactor(RM_HeatKind kind, float overheadFactor, float lowSunFactor)
        {
            switch (kind)
            {
                case RM_HeatKind.ambient:
                    return 0f;
                case RM_HeatKind.lowSun:
                    return Clamp01(lowSunFactor);
                default:
                    return Clamp01(overheadFactor);
            }
        }

        /// <summary>The shade (0..1) a gear piece casts under this heat kind:
        /// (its own depth + its stuff's shade-cloth bonus, clamped to 1) ×
        /// the kind factor. Mirrak hide carries the biggest bonus, so it casts
        /// the deepest shade.</summary>
        public static float GearDepth(RM_HeatKind kind, float baseDepth, float stuffBonus,
            float overheadFactor, float lowSunFactor)
        {
            return Clamp01(baseDepth + stuffBonus) * GearKindFactor(kind, overheadFactor, lowSunFactor);
        }

        /// <summary>Exposure with a gear cover term (already kind-resolved by
        /// GearDepth). Under ambient heat the gear term is ignored, exactly as
        /// roofs and cast shade are.</summary>
        public static float Exposure(RM_HeatKind kind, bool outdoors, float roofShade, bool thickRoof,
            float castShade, float gearShade)
        {
            float ex = Exposure(kind, outdoors, roofShade, thickRoof, castShade);
            return kind == RM_HeatKind.ambient ? ex : WithCover(ex, gearShade);
        }

        /// <summary>Exposure after one more cover (0..1): covers combine by
        /// the deepest, never by sum — two parasols are not better than one.</summary>
        public static float WithCover(float exposure, float cover)
        {
            float cap = 1f - Clamp01(cover);
            return exposure < cap ? exposure : cap;
        }

        /// <summary>Writes `depth` into every cell of an inclusive rectangle
        /// (a shade tent's footprint), keeping the max of what is there.</summary>
        public static void FillRect(float[] grid, int width, int height, int minX, int minZ, int maxX, int maxZ, float depth)
        {
            if (depth <= 0f)
            {
                return;
            }
            for (int z = Math.Max(0, minZ); z <= Math.Min(height - 1, maxZ); z++)
            {
                for (int x = Math.Max(0, minX); x <= Math.Min(width - 1, maxX); x++)
                {
                    int i = z * width + x;
                    if (depth > grid[i])
                    {
                        grid[i] = depth;
                    }
                }
            }
        }

        /// <summary>A shadow cast along the sun (CastInto's shape) whose full
        /// body is `depth` rather than 1 — a sun shield's lee.</summary>
        public static void CastInto(float[] grid, int width, int height, int cx, int cz,
            float dirX, float dirZ, float length, float tipShade, float depth)
        {
            if (depth <= 0f || length <= 0f)
            {
                return;
            }
            float norm = (float)Math.Sqrt(dirX * dirX + dirZ * dirZ);
            if (norm < 1e-4f)
            {
                return;
            }
            dirX /= norm;
            dirZ /= norm;
            float d = Clamp01(depth);
            int steps = (int)Math.Ceiling(length * 2f);
            int lastIdx = -1;
            for (int s = 1; s <= steps; s++)
            {
                float t = s * 0.5f;
                int x = (int)Math.Round(cx + dirX * t);
                int z = (int)Math.Round(cz + dirZ * t);
                if (x < 0 || z < 0 || x >= width || z >= height)
                {
                    return;
                }
                if (x == cx && z == cz)
                {
                    continue;
                }
                int idx = z * width + x;
                if (idx == lastIdx)
                {
                    continue;
                }
                lastIdx = idx;
                float frac = t / length;
                float v = frac <= 0.75f ? 1f : 1f - (1f - tipShade) * ((frac - 0.75f) / 0.25f);
                v = Clamp01(v) * d;
                if (v > grid[idx])
                {
                    grid[idx] = v;
                }
            }
        }

        /// <summary>The one cell a parasol weakly shades besides its wearer:
        /// one step along the shadow direction (rounded to the 8-neighbour
        /// grid). Returns false when there is no direction.</summary>
        public static bool AdjacentShadowCell(int cx, int cz, float dirX, float dirZ, out int x, out int z)
        {
            float norm = (float)Math.Sqrt(dirX * dirX + dirZ * dirZ);
            x = cx;
            z = cz;
            if (norm < 1e-4f)
            {
                return false;
            }
            x = cx + (int)Math.Round(dirX / norm);
            z = cz + (int)Math.Round(dirZ / norm);
            return x != cx || z != cz;
        }

        // ── STILLSAND_SUN_FROM_LATITUDE_1: the sun's height decides ──────
        // Owner rulings: "The biome takes its sun angle from its latitude"
        // (the tile's planet latitude, never a region's prose), and "the cover
        // that counts follows the sun angle". Still ONE kind of heat: these
        // pick which cover counts and how strong the sun is, nothing else.

        /// <summary>The heat kind a biome's sun resolves to at this elevation:
        /// overhead at or above overheadAboveDeg, lowSun below it. Ambient is
        /// never changed (shade does not help there at any angle). A negative
        /// threshold, or an unknown (NaN) elevation, keeps the biome's own
        /// kind.</summary>
        public static RM_HeatKind KindFromElevation(RM_HeatKind baseKind, float elevationDeg, float overheadAboveDeg)
        {
            if (baseKind == RM_HeatKind.ambient || overheadAboveDeg < 0f || float.IsNaN(elevationDeg))
            {
                return baseKind;
            }
            return elevationDeg >= overheadAboveDeg ? RM_HeatKind.overhead : RM_HeatKind.lowSun;
        }

        /// <summary>Irradiance by angle: zenithOffsetC × sin(elevation), never
        /// below floorC (the far ring's own figure). An unknown (NaN)
        /// elevation returns zenithOffsetC unchanged.</summary>
        public static float ElevationHeatOffset(float zenithOffsetC, float elevationDeg, float floorC)
        {
            if (float.IsNaN(elevationDeg))
            {
                return zenithOffsetC;
            }
            double e = Math.Max(0.0, Math.Min(90.0, elevationDeg)) * Math.PI / 180.0;
            float off = zenithOffsetC * (float)Math.Sin(e);
            return off < floorC ? floorC : off;
        }

        /// <summary>Sand glare: exposure on open natural sand never drops
        /// below the floor, whatever shade or cover is over it (the light
        /// comes up from the ground). An enclosed room is handled before this
        /// (exposure 0 there, never floored).</summary>
        public static float WithGlareFloor(float exposure, float glareFloor)
        {
            float f = Clamp01(glareFloor);
            return exposure > f ? exposure : f;
        }

        /// <summary>SOLAR_MIRRORS_MOD_DESIGN_1 §2.3: exposure where a light
        /// provider (RM_MapComponent_ShadeGrid.RegisterLightSource) lands
        /// `light` (0..N, N &gt; 1 = concentration): light un-shades, up to
        /// full sun and never past it — max(exposure, min(1, light)). 0 light
        /// returns the exposure unchanged.</summary>
        public static float WithLight(float exposure, float light)
        {
            float l = Clamp01(light);
            return exposure > l ? exposure : l;
        }

        /// <summary>Shade (0..1) after light: cut to 1 - min(1, light), never
        /// raised. The ShadeAt counterpart of WithLight.</summary>
        public static float ShadeWithLight(float shade, float light)
        {
            float cap = 1f - Clamp01(light);
            return shade < cap ? shade : cap;
        }

        /// <summary>STILLSAND_GLARE_BLIND_GOGGLES_1: the glare-blind severity a
        /// pawn gains over one check interval. Nothing below the full-glare
        /// threshold (shade on sand, which the glare floor holds at about
        /// 0.35, does not blind), nothing for protected eyes (a gene or eye
        /// cover), and above the threshold perDay × the interval's share of a
        /// day × the strength dial. Recovery is the hediff's own
        /// SeverityPerDay decay, never this.</summary>
        public static float GlareBlindGain(float exposure, float fullGlareMin, float severityPerDay,
            float strength, int intervalTicks, bool eyesProtected)
        {
            if (eyesProtected || exposure < fullGlareMin || severityPerDay <= 0f || strength <= 0f || intervalTicks <= 0)
            {
                return 0f;
            }
            return severityPerDay * strength * intervalTicks / 60000f;
        }

        // ── STILLSAND_MIRAGE_CONDITION_1 ────────────────────────────────

        /// <summary>The mirage runs only on a map whose sun stands at or above
        /// the threshold. Unknown (NaN) elevation or a negative threshold: no
        /// mirage.</summary>
        public static bool MirageActive(float elevationDeg, float minElevationDeg)
        {
            return minElevationDeg >= 0f && !float.IsNaN(elevationDeg) && elevationDeg >= minElevationDeg;
        }

        /// <summary>The map edge the mirage lies on: the sun-ward one, opposite
        /// the shadow direction. 0 north (+z), 1 east (+x), 2 south, 3 west
        /// (Rot4's numbering). No direction: north.</summary>
        public static int MirageEdge(float shadowDirX, float shadowDirZ)
        {
            float x = -shadowDirX;
            float z = -shadowDirZ;
            if (Math.Abs(x) < 1e-4f && Math.Abs(z) < 1e-4f)
            {
                return 0;
            }
            if (Math.Abs(x) >= Math.Abs(z))
            {
                return x > 0f ? 1 : 3;
            }
            return z > 0f ? 0 : 2;
        }

        /// <summary>Heat shimmer on a long-range accuracy factor: the shipped
        /// factor for a shooter standing in full sun (exposure at or above
        /// the threshold), 1 otherwise.</summary>
        public static float MirageShimmerFactor(float exposure, float fullSunMin, float factor)
        {
            return exposure >= fullSunMin ? Clamp01(factor) : 1f;
        }

        /// <summary>WEBWORK_HEAT_SHADE_BUILD_1: is a sun-sensitive pawn exposed to light?
        /// When the shade grid is usable and the setting reads it, exposed means the cell's shade is below
        /// the threshold AND it is not under a roof (a roof is shade 1, so the roof case falls out);
        /// otherwise the vanilla primitive (inSunlight) decides, which is today's behaviour.</summary>
        public static bool ScaldExposed(bool readsShade, bool gridUsable, float shadeAt, float threshold, bool inSunlight)
        {
            if (readsShade && gridUsable)
            {
                return inSunlight && shadeAt < threshold;
            }
            return inSunlight;
        }

        public static float Clamp01(float v)
        {
            return v < 0f ? 0f : (v > 1f ? 1f : v);
        }
    }
}
