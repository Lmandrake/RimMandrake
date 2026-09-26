using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SCALD water review, owner ruling 2026-09-25 (SCALD_REVIEW live walk):
    // "some rippling animation from bubbles emerging from the surface ...
    // just the disturbances themselves would be welcome to show how
    // agitated the water is. That could be used to distinguish margin vs
    // shallow vs deep: margin is calm, shallow has a bit of agitation, deep
    // has constant agitation." Generic, terrain-tag-gated like every other
    // mechanism in this kit — not Scald-hardcoded, so any future biome's
    // boiling/roiling/agitated water opts in with two tags and zero new C#.
    //
    // Reuses the vanilla engine's own disturbance mote outright rather than
    // inventing one: RimWorld already spawns FleckDefOf.WaterRipple every
    // time a pawn steps through water (Verse.PawnWaterRippleMaker, on every
    // Pawn's own Pawn_DrawTracker) via the public
    // RimWorld.FleckMaker.WaterRipple(Vector3, Map, float) call. This
    // MapComponent just calls the same engine method itself, from cells the
    // water has no pawn standing in — no new art, no new FleckDef, no new
    // shader; MEASURED against the decompiled engine
    // (Source/Verse/PawnWaterRippleMaker.cs, Source/RimWorld/FleckMaker.cs)
    // before writing this.
    //
    // Two tags, not a shared one with the wreck-scatter tag
    // (RUT_ScaldShallow) — same "each purpose gets its own tag" convention
    // this kit already follows elsewhere (RUT_ScaldMarginMat vs the generic
    // Water tag): RM_WaterAgitationLight (occasional ripples) and
    // RM_WaterAgitationHeavy (near-constant ripples). The Scald's margin
    // ring (RUT_ScaldMargin) carries neither, staying calm per the owner's
    // own three-way split.
    //
    // ── 2026-09-26 REWRITE (SCALD_WATER_AGITATION_FLECKS_1) ───────────────
    // Owner's walk verdict: "the boiling should have WAY MORE ripples" — the
    // effect read nearly flat. The cause was structural, not a timid
    // constant, and it is worth stating so nobody re-tunes the old shape:
    //
    //   The first version fired ONE ripple per interval MAP-WIDE, picked
    //   from a pool of every tagged cell on the map. At its fastest (one
    //   per 40-100 ticks) that is ~0.014 spawns/tick over an entire map. A
    //   camera sees on the order of 3% of a map, and FleckDef WaterRipple
    //   lives ~4.1 s (fadeOutTime 4, solidTime 0, alpha 0.2 — MEASURED from
    //   the def) — so the expected number of ripples VISIBLE AT ANY MOMENT
    //   was about one tenth of one. The mechanism was working exactly as
    //   written and could never be seen.
    //
    // The fix is to spawn where the camera is looking and to scale with how
    // much of the view is actually agitated water, rather than with map
    // area. Each tick a few cells are sampled from Find.CameraDriver's own
    // CurrentViewRect; a sample that lands on tagged water rolls for a
    // ripple. Cost is bounded by the sample count regardless of map size
    // (at most ~0.5 fleck spawns/tick at default density), and the density
    // is proportional to the fraction of the VIEW that is agitated — a
    // shoreline half-full of water ripples half as hard as open boil, which
    // is the correct read.
    //
    // At the shipped defaults a view filled with heavy water settles at
    // roughly 120 concurrent ripples (0.49 spawns/tick x 246 ticks of
    // lifetime) — about one ripple per 16 visible cells, a surface that
    // never settles. Light water settles near 25, read as occasional. Both
    // are INVENTED: the owner gave a direction ("WAY MORE"), not a figure,
    // which is exactly why the density multiplier below is a Mod Settings
    // slider rather than a constant.
    public class RM_MapComponent_WaterAgitation : MapComponent
    {
        private const int RescanIntervalTicks = 2500; // 1 in-game hour, same cadence as RM_MapComponent_VaporColumns

        // How many cells of the current camera view to test per tick. Four
        // array lookups a tick is free; this is the hard ceiling on the
        // whole mechanism's cost, independent of map size.
        private const int SamplesPerTick = 4;

        // Chance a sample that landed on tagged water actually throws a
        // ripple, before the settings multiplier. INVENTED — see the header
        // for what they settle to on screen.
        private const float HeavyRippleChance = 0.123f;
        private const float LightRippleChance = 0.026f;

        // Ripple size, randomized a little so a field of them does not read
        // as one stamp repeated.
        private const float LightRippleSizeMin = 0.35f;
        private const float LightRippleSizeMax = 0.6f;
        private const float HeavyRippleSizeMin = 0.5f;
        private const float HeavyRippleSizeMax = 0.95f;

        // Per-cell agitation grade, indexed by CellIndicesUtility index.
        // 0 = none, 1 = light, 2 = heavy. A byte per cell is ~62 KB on a
        // 250x250 map and costs one array read per sample, where the old
        // List<IntVec3> pools cost a random index into a list that could
        // hold tens of thousands of entries and still only ever yielded one
        // cell per interval.
        private byte[] grade;
        private bool anyAgitated;

        private int ticksUntilRescan = 1;

        public RM_MapComponent_WaterAgitation(Map map)
            : base(map)
        {
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            Rebuild();
            ticksUntilRescan = RescanIntervalTicks;
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (--ticksUntilRescan <= 0)
            {
                ticksUntilRescan = RescanIntervalTicks;
                Rebuild();
            }

            if (!anyAgitated)
            {
                return; // this map carries neither tag — quiet no-op, matches the kit's posture elsewhere
            }

            if (!RM_EnvironmentalHazardsSettings.waterAgitationEnabled)
            {
                return; // grid stays built (cheap, terrain-only) so re-enabling resumes with no rescan delay
            }

            // Purely cosmetic, and a fleck the player cannot see is pure
            // waste: only the map actually on screen spawns anything.
            if (map != Find.CurrentMap)
            {
                return;
            }

            CameraDriver camera = Find.CameraDriver;
            if (camera == null)
            {
                return;
            }

            CellRect view = camera.CurrentViewRect;
            view.ClipInsideMap(map);
            if (view.Width <= 0 || view.Height <= 0)
            {
                return;
            }

            float density = Mathf.Clamp(RM_EnvironmentalHazardsSettings.waterAgitationDensity, 0f, 8f);
            if (density <= 0f)
            {
                return;
            }

            for (int i = 0; i < SamplesPerTick; i++)
            {
                IntVec3 cell = new IntVec3(
                    Rand.RangeInclusive(view.minX, view.maxX),
                    0,
                    Rand.RangeInclusive(view.minZ, view.maxZ));

                byte g = grade[map.cellIndices.CellToIndex(cell)];
                if (g == 0)
                {
                    continue;
                }

                bool heavy = g == 2;
                if (!Rand.Chance((heavy ? HeavyRippleChance : LightRippleChance) * density))
                {
                    continue;
                }

                float size = heavy
                    ? Rand.Range(HeavyRippleSizeMin, HeavyRippleSizeMax)
                    : Rand.Range(LightRippleSizeMin, LightRippleSizeMax);

                // Jitter inside the cell so the ripples do not sit on the
                // square grid the way a pawn's own wake never does.
                Vector3 loc = cell.ToVector3Shifted();
                loc.x += Rand.Range(-0.4f, 0.4f);
                loc.z += Rand.Range(-0.4f, 0.4f);
                FleckMaker.WaterRipple(loc.WithY(AltitudeLayer.MoteLow.AltitudeFor()), map, size);
            }
        }

        private void Rebuild()
        {
            int area = map.Area;
            if (grade == null || grade.Length != area)
            {
                grade = new byte[area];
            }

            anyAgitated = false;
            CellIndices indices = map.cellIndices;

            foreach (IntVec3 cell in map.AllCells)
            {
                int idx = indices.CellToIndex(cell);
                TerrainDef terrain = map.terrainGrid.TerrainAt(cell);
                byte g = 0;

                if (terrain?.tags != null)
                {
                    if (terrain.tags.Contains("RM_WaterAgitationHeavy"))
                    {
                        g = 2;
                    }
                    else if (terrain.tags.Contains("RM_WaterAgitationLight"))
                    {
                        g = 1;
                    }
                }

                grade[idx] = g;
                if (g != 0)
                {
                    anyAgitated = true;
                }
            }
        }
    }
}
