using System;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // SOLAR_HEAT_EXPOSURE_1 — the pure arithmetic of Direct Sun.
    //
    // DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES (owner, 2026-10-19: "a pure
    // function of geometry, NOT biome"): one model on every map. No heat
    // kind, no per-biome number. Felt offset = zenith C × sin(E) × exposure
    // × weather sun factor × body-size factor × strength dial. A roof, a
    // parasol and a cast shadow cover at every sun elevation E; a shadow is
    // height / tan E cells long, so a low sun is weak and throws long shade,
    // a high sun is strong and throws almost none. Ambient heat (steam,
    // volcanic) is vanilla air temperature, never this pipeline.
    //
    // No Verse/Unity dependency on purpose (System.Math only): the offline
    // selftest (Source/SelfTest, run by Utils/selftest_sun_heat.py) compiles
    // this exact file. Every live caller (RM_MapComponent_ShadeGrid,
    // RM_SunHeatPatches) routes through these functions, so what the
    // selftest checks is what the game runs.
    // ════════════════════════════════════════════════════════════════════

    /// <summary>The planet constants of Direct Sun: the same on every map.
    /// No BiomeDef field changes them (DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES).
    /// The zenith value is a Mod Setting whose default is ZenithDefaultC.</summary>
    public static class RM_DirectSun
    {
        /// <summary>°C of Direct Sun on a size-1 pawn in full sun at E = 90 (owner card 2026-10-19: "55 C everywhere").</summary>
        public const float ZenithDefaultC = 55f;

        /// <summary>Body-size term: (1 / bodySize)^exponent, clamped. INVENTED first values (SOLAR_HEAT_EXPOSURE_1).</summary>
        public const float BodySizeExponent = 0.5f;
        public const float MinBodySizeFactor = 0.25f;
        public const float MaxBodySizeFactor = 2.5f;

        /// <summary>Cap on the felt offset (°C), so a tiny creature at the zenith does not read absurd numbers.</summary>
        public const float MaxOffsetC = 70f;

        /// <summary>Path cost of one fully sunlit cell for an undrafted pawn (before the pathing dial).</summary>
        public const float SunPathCostPerCell = 20f;

        /// <summary>Open natural sand never reads below this exposure (the light comes up from the ground). Owner card
        /// 2026-09-30, once the Stillsand's figure; by his card of 2026-10-19 (D5) any natural sand under the sun.</summary>
        public const float SandGlareExposureFloor = 0.35f;

        /// <summary>The body-size factor by the planet constants.</summary>
        public static float BodyFactor(float bodySize)
        {
            return RM_SunHeatMath.BodySizeFactor(bodySize, BodySizeExponent, MinBodySizeFactor, MaxBodySizeFactor);
        }

        /// <summary>°C of Direct Sun a creature of this size feels at this exposure (weather already in it), with
        /// offsetAtFullC = zenith × sin E (RM_SunHeatMath.DirectSunOffsetC) and the strength dial.</summary>
        public static float FeltOffsetC(float exposure, float offsetAtFullC, float strength, float bodySize)
        {
            return RM_SunHeatMath.HeatOffset(exposure, offsetAtFullC, strength, BodyFactor(bodySize), MaxOffsetC);
        }
    }

    public static class RM_SunHeatMath
    {
        /// <summary>A PathGridJob custom cost at or above this makes the cell
        /// impassable (decompiled 1.6 PathGridJob: custom[index] >= 10000).
        /// Sun cost is always kept well under it.</summary>
        public const int ImpassableCustomCost = 10000;

        public const int MaxSunPathCost = 2000;

        /// <summary>0 (fully sheltered) .. 1 (full sun) for one cell, the same at every sun elevation.
        /// outdoors: the cell's room uses outdoor temperature — an enclosed room is never exposed (vanilla's own
        /// "leaving" the open air). roofShade: 1 under any roof (a tent, a building, overhead rock), else 0.
        /// castShade: 0..1 from the directional grid. Covers combine by the deepest.</summary>
        public static float Exposure(bool outdoors, float roofShade, float castShade)
        {
            if (!outdoors)
            {
                return 0f;
            }
            return Clamp01(1f - Clamp01(Math.Max(roofShade, castShade)));
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
        // Parasol, tent and standing lee casters all feed the SAME exposure rule above: their shade is one more cover
        // term, at every sun elevation (DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES spec 4-5).

        /// <summary>The shade (0..1) a gear piece casts: its own depth + its stuff's shade-cloth bonus, clamped to 1.
        /// Mirrak hide carries the biggest bonus, so it casts the deepest shade.</summary>
        public static float GearDepth(float baseDepth, float stuffBonus)
        {
            return Clamp01(baseDepth + stuffBonus);
        }

        /// <summary>Exposure with a gear cover term.</summary>
        public static float Exposure(bool outdoors, float roofShade, float castShade, float gearShade)
        {
            return WithCover(Exposure(outdoors, roofShade, castShade), gearShade);
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

        // ── Direct Sun by the sun's height (DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES spec 1-3) ──
        // The sun elevation E comes from the map tile's arc to the substellar point, one clamp [0, 90] on every map.

        /// <summary>The one clamp on a sun elevation: [0, 90] degrees. NaN (no sun known) stays NaN.</summary>
        public static float ClampElevation(float elevationDeg)
        {
            if (float.IsNaN(elevationDeg))
            {
                return elevationDeg;
            }
            return elevationDeg < 0f ? 0f : (elevationDeg > 90f ? 90f : elevationDeg);
        }

        /// <summary>Direct Sun at full exposure on a size-1 pawn before weather and the strength dial:
        /// zenithC × sin(E). 0 at E ≤ 0 (the sun is at or below the horizon) and for an unknown (NaN) sun.
        /// No floor, no per-biome number.</summary>
        public static float DirectSunOffsetC(float zenithC, float elevationDeg)
        {
            if (float.IsNaN(elevationDeg) || elevationDeg <= 0f || zenithC <= 0f)
            {
                return 0f;
            }
            double e = Math.Min(90.0, elevationDeg) * Math.PI / 180.0;
            return zenithC * (float)Math.Sin(e);
        }

        /// <summary>Cells of ground shadow per unit of caster height at this sun elevation: 1 / tan E (cot E).
        /// E is floored at 0.5 degrees so the value stays finite; the caller caps the length. 0 for an unknown sun.</summary>
        public static float ShadowLengthPerHeight(float elevationDeg)
        {
            if (float.IsNaN(elevationDeg))
            {
                return 0f;
            }
            double e = Math.Max(0.5, Math.Min(90.0, elevationDeg)) * Math.PI / 180.0;
            return (float)(Math.Cos(e) / Math.Sin(e));
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

        // ── TREE_SHADE_BUILD_CROWNS_ON_STILTS: a tree is a parasol on a pole ──
        // design/RimMandrake/tree_shade_model_2026-10-19.md §4. The crown is a disc of radius r held at height hc;
        // the sun projects it onto the ground hc / tan E cells down-sun (capped like every other shadow). A horizontal
        // disc projected by parallel rays onto flat ground is the same disc, moved. The trunk keeps its strip.

        /// <summary>The plant's drawn size in cells at this growth: drawSize.x × visualSizeRange lerped by growth
        /// (0..1), by the one ruler Plant.Print uses (RimMandrake.Shared.DrawnExtent.Side, which Huge Things' hitboxes
        /// also use). Growth-aware: a seedling is drawn small and casts small.</summary>
        public static float DrawnSize(float drawSizeX, float visualMin, float visualMax, float growth)
        {
            float g = Clamp01(growth);
            return RimMandrake.Shared.DrawnExtent.Side(drawSizeX, visualMin + (visualMax - visualMin) * g);
        }

        /// <summary>The ground centre of a crown's shadow: the caster cell moved min(cap, hc × cotE) cells along the
        /// shadow direction. No direction (or cotE 0, the sun at the zenith): the disc lies under the crown.</summary>
        public static void CrownFootprint(int cx, int cz, float crownHeight, float dirX, float dirZ, float cotE,
            float cap, out float ox, out float oz)
        {
            ox = cx;
            oz = cz;
            float norm = (float)Math.Sqrt(dirX * dirX + dirZ * dirZ);
            if (norm < 1e-4f || crownHeight <= 0f || cotE <= 0f)
            {
                return;
            }
            float off = crownHeight * cotE;
            if (off > cap) { off = cap; }
            ox = cx + dirX / norm * off;
            oz = cz + dirZ / norm * off;
        }

        /// <summary>A crown's opacity: its base (1 = full shade, owner card 2026-10-19 Q2) × the leafless factor while
        /// leafless × the strength dial, clamped to 0..1.</summary>
        public static float CrownOpacity(float baseOpacity, bool leafless, float leaflessFactor, float strength)
        {
            return Clamp01(baseOpacity * (leafless ? leaflessFactor : 1f) * strength);
        }

        /// <summary>Writes `value` into every cell whose centre lies within `radius` of (ox, oz), keeping the max of
        /// what is there; the cell holding the centre is always written, so a crown is never smaller than one cell.
        /// When `owner` is given, a cell this disc raised records `id` there (who shades it, for the readout).
        /// Returns the number of cells raised. Row-major grid, index = z * width + x.</summary>
        public static int RasterDisc(float[] grid, int width, int height, float ox, float oz, float radius,
            float value, int[] owner, int id)
        {
            if (value <= 0f)
            {
                return 0;
            }
            float v = Clamp01(value);
            float r = radius < 0f ? 0f : radius;
            float r2 = r * r;
            int raised = 0;
            int ccx = (int)Math.Round(ox);
            int ccz = (int)Math.Round(oz);
            int minX = Math.Max(0, (int)Math.Floor(ox - r));
            int maxX = Math.Min(width - 1, (int)Math.Ceiling(ox + r));
            int minZ = Math.Max(0, (int)Math.Floor(oz - r));
            int maxZ = Math.Min(height - 1, (int)Math.Ceiling(oz + r));
            for (int z = minZ; z <= maxZ; z++)
            {
                float dz = z - oz;
                for (int x = minX; x <= maxX; x++)
                {
                    float dx = x - ox;
                    if (dx * dx + dz * dz > r2 && !(x == ccx && z == ccz))
                    {
                        continue;
                    }
                    int i = z * width + x;
                    if (v > grid[i])
                    {
                        grid[i] = v;
                        if (owner != null)
                        {
                            owner[i] = id;
                        }
                        raised++;
                    }
                }
            }
            return raised;
        }

        /// <summary>One tree's crown shadow into `grid`: the disc of radius r (cells) moved by CrownFootprint.
        /// Returns the cells raised.</summary>
        public static int CastCrown(float[] grid, int width, int height, int cx, int cz, float radius, float crownHeight,
            float dirX, float dirZ, float cotE, float cap, float opacity, int[] owner, int id)
        {
            CrownFootprint(cx, cz, crownHeight, dirX, dirZ, cotE, cap, out float ox, out float oz);
            return RasterDisc(grid, width, height, ox, oz, radius, opacity, owner, id);
        }

        /// <summary>RIMMANDRAKE_TRY_RENDERED_CROWN_SHADOW_ON_ONE_GIANT_TREE: whether a crown's shadow is DRAWN (the owner's
        /// experiment, card 2026-10-19 Q3 option 3): tree crowns on, a sun vector to follow (no vector, no drawn shadow:
        /// the ground tint shows those maps' crowns), the species flagged by RM_TreeCrownExtension.renderedShadow, and a
        /// crown that casts at all.</summary>
        public static bool DrawsCrownShadow(bool settingOn, bool directional, bool speciesFlagged, float opacity)
        {
            return settingOn && directional && speciesFlagged && opacity > 0f;
        }

        /// <summary>The drawn crown shadow's square, in world units: centred on the crown's footprint (CrownFootprint;
        /// a grid cell x has its world centre at x + 0.5), half side = radius + CrownShadowPenumbra, so the soft disc's
        /// full-dark core covers every cell RasterDisc raises and its edge fades over one cell outside them.</summary>
        public static void CrownShadowQuad(int cx, int cz, float radius, float crownHeight, float dirX, float dirZ,
            float cotE, float cap, out float centreX, out float centreZ, out float halfSide)
        {
            CrownFootprint(cx, cz, crownHeight, dirX, dirZ, cotE, cap, out float ox, out float oz);
            centreX = ox + 0.5f;
            centreZ = oz + 0.5f;
            halfSide = (radius < 0f ? 0f : radius) + CrownShadowPenumbra;
        }

        /// <summary>The width in cells of the drawn shadow's soft edge (INVENTED: one cell reads as soft at the
        /// default zoom and is still inside the next cell).</summary>
        public const float CrownShadowPenumbra = 1f;

        /// <summary>The drawn disc's full-dark core as a fraction of its half side. A shaded cell's centre lies within r
        /// of the disc's centre, so the core must reach r: core >= r / (r + penumbra 1). A greatbole grown is drawn 12 to
        /// 16 cells, r = 0.97 x drawn / 2 = 5.8 to 7.8 cells, r / (r + 1) = 0.853 to 0.886; 0.9 covers them all with a
        /// fade of about 0.7 to 0.9 cells (the selftest checks drawn 12 and 16).</summary>
        public const float CrownShadowCore = 0.9f;

        /// <summary>The drawn shadow's alpha at distance d from its centre, as a fraction of the half side (0 centre, 1
        /// the square's inscribed circle): 1 inside `core`, a smoothstep down to 0 at 1, 0 beyond.</summary>
        public static float CrownShadowAlpha(float d, float core)
        {
            if (d <= core)
            {
                return 1f;
            }
            if (d >= 1f || core >= 1f)
            {
                return 0f;
            }
            float t = (d - core) / (1f - core);
            return 1f - t * t * (3f - 2f * t);
        }

        public static float Clamp01(float v)
        {
            return v < 0f ? 0f : (v > 1f ? 1f : v);
        }
    }

    /// <summary>TREE_SHADE_BUILD_CROWNS_ON_STILTS: the planet constants of tree crowns (design
    /// tree_shade_model_2026-10-19.md §4.2). The same for every biome; a species whose sprite misleads overrides them on
    /// its own ThingDef with RM_TreeCrownExtension, never on a BiomeDef.</summary>
    public static class RM_TreeCrown
    {
        /// <summary>A plant drawn at least this many cells at full growth is a tree for shade (owner card 2026-10-19
        /// Q4: "anything drawn >=1.5 cells").</summary>
        public const float CasterDrawnSize = 1.5f;

        /// <summary>Crown radius = factor × drawn size / 2. INVENTED default (the crown covers most of the sprite's
        /// width, less trunk and gaps).</summary>
        public const float RadiusFactorDefault = 0.8f;

        /// <summary>Crown height = factor × drawn size; also the trunk strip's height (today's 0.5).</summary>
        public const float HeightFactorDefault = 0.5f;

        /// <summary>Full shade (owner card 2026-10-19 Q2: "Full shade").</summary>
        public const float OpacityDefault = 1f;

        /// <summary>While Plant.LeaflessNow the crown lets most light through. INVENTED.</summary>
        public const float LeaflessFactor = 0.3f;

        /// <summary>The crown radius in cells for a tree of this drawn size.</summary>
        public static float Radius(float drawnSize, float radiusFactor)
        {
            return radiusFactor * drawnSize * 0.5f;
        }

        /// <summary>The crown height (shadow-height scale, a wall is 1) for a tree of this drawn size.</summary>
        public static float Height(float drawnSize, float heightFactor)
        {
            return heightFactor * drawnSize;
        }
    }
}
