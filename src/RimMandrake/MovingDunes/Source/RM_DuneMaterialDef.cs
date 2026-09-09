using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.MovingDunes
{
    /// <summary>How a skinned map's sand layer carries its material's colour.</summary>
    /// <remarks>
    /// MOVING_DUNES_DESIGN.md §2 "Rendering" names ONE honest unknown: whether the
    /// vanilla sand shader (Misc/Sand, <see cref="MatBases.Sand"/>) respects material
    /// <c>color</c>. Both routes are implemented in
    /// <see cref="SectionLayer_DuneSand"/>; the design's shader-tint quicktest decides
    /// which becomes the shipped default. Until that gate runs the default is
    /// <see cref="MaterialColor"/> — the design's primary route.
    /// </remarks>
    public enum DuneTintMode
    {
        /// <summary>Tint applied to a per-map <c>new Material(MatBases.Sand)</c> instance.
        /// Vertex RGB keeps its vanilla meaning (red = pollution mask).</summary>
        MaterialColor,

        /// <summary>Tint folded into our own vertex RGB. We own the layer on a skinned
        /// map, so the pollution mask is surrendered — the fallback the design names.</summary>
        VertexColor,
    }

    /// <summary>
    /// The whole knob panel for one map's drifting material. MOVING_DUNES_DESIGN.md §2
    /// "The tunable surface" is RULED no-constants: everything a designer might retune
    /// is a field here, and <see cref="MapComponent_DuneField"/> hardcodes nothing.
    ///
    /// "Particle mass" (the owner's phrase) has no engine counterpart — Odyssey's sand
    /// channel is one float per cell with no mass concept. Mass IS this parameter
    /// cluster: a heavier material sets a higher <see cref="windSpeedThreshold"/>, a
    /// shorter <see cref="hopRange"/> and a larger <see cref="slabSize"/>.
    ///
    /// A biome binds one material with <see cref="DuneFieldExtension"/>; the map
    /// resolves its single material once at init.
    /// </summary>
    public class RM_DuneMaterialDef : Def
    {
        // ---------------------------------------------------------------- rendering

        /// <summary>Display colour of drifted sand on a map skinned with this material.
        /// White = vanilla appearance.</summary>
        public Color tint = Color.white;

        /// <summary>Which of the two tint routes this material uses. See
        /// <see cref="DuneTintMode"/> — gate-pending, default is the design's primary.</summary>
        public DuneTintMode tintMode = DuneTintMode.MaterialColor;

        /// <summary>Relief shading strength on the downwind depth gradient: windward
        /// erosion faces read lighter, leeward slip faces darker. Applied to layer
        /// OPACITY in both tint modes (alpha is the documented channel of the vanilla
        /// sand shader, so this reads correctly whichever way the gate falls) and
        /// additionally to vertex RGB in <see cref="DuneTintMode.VertexColor"/>.
        /// 0 disables. This is the fix for sand-on-sand contrast — the reason vanilla
        /// excluded sand terrain from holding sand at all.</summary>
        public float crestShading = 0.18f;

        // ---------------------------------------------------------------- transport

        /// <summary>Depth moved by one slab hop (Werner's q). The design sizes this
        /// under SandGrid's own 0.15 mesh-dirty threshold on purpose: q = 0.05 rides
        /// the built-in rate limiter instead of fighting it.</summary>
        public float slabSize = 0.05f;

        /// <summary>How far downwind a slab may travel before it must land.</summary>
        public IntRange hopRange = new IntRange(2, 6);

        /// <summary>A cell below this depth has nothing loose to give up.</summary>
        public float erodeMinDepth = 0.1f;

        /// <summary>Map wind speed (<c>WindManager.WindSpeed</c>, vanilla range
        /// 0.04–2.0) below which no transport happens at all. Heavier material,
        /// higher number.</summary>
        public float windSpeedThreshold = 0.6f;

        /// <summary>How many cells upwind are scanned for a wind shadow (a full-fillage
        /// edifice, or a meaningfully deeper cell) that protects a cell from eroding.</summary>
        public int shadowRange = 4;

        /// <summary>Transport attempts per map cell per in-game day, before the storm
        /// multiplier. The engine converts to a per-batch K: <c>K = value × cells /
        /// 240</c> (240 batches/day at one batch per 250 ticks). The design's budget
        /// arithmetic — K = 2,000 on a 250×250 map — is this value at 7.7.</summary>
        public float attemptsPerCellPerDay = 7.7f;

        /// <summary>K multiplier while a sand-bearing weather is running
        /// (<c>WeatherManager.SandRate &gt; 0.001</c>). A WeatherDef may override this
        /// with <see cref="DuneWeatherExtension"/>. This is the knob that makes a
        /// windstorm visibly reshape the field.</summary>
        public float stormTransportFactor = 4f;

        /// <summary>Scale applied to vanilla's ambient sand decay (the exact
        /// <c>-1f/180f</c> per cell-visit in <c>SteadyEnvironmentEffects</c>).
        /// 0 = fully suppressed, which is what persistent dunes need; 1 = vanilla.</summary>
        public float ambientDecayFactor = 0f;

        // ------------------------------------------------------------ source / sink

        /// <summary>RULED §2: the map is a window onto an endless desert, not a torus.
        /// Slabs leaving the leeward edge are gone; this is the fraction of that loss
        /// the windward edge gives back. 1.0 = steady dune field, &lt;1 = isolated
        /// migrating banks, &gt;1 = a map that slowly buries (capped — see
        /// <see cref="maxTotalMassFraction"/>).</summary>
        public float influxLossRatio = 1f;

        /// <summary>Absolute windward supply, in depth-units per in-game day,
        /// independent of loss. This is the "per-biome base" the design names, and the
        /// cold-start seed: without it a map holding no sand can never lose any and so
        /// could never be given any.</summary>
        public float influxPerDay = 25f;

        /// <summary>Influx multiplier while a sand-bearing weather is running.
        /// Overridable per weather via <see cref="DuneWeatherExtension"/>.</summary>
        public float weatherInfluxFactor = 4f;

        /// <summary>Hard guard: influx stops once total grid mass reaches this fraction
        /// of (cells × MaxDepth). A mis-tuned supply cannot drown a map unboundedly.
        /// MOVING_DUNES_DESIGN.md §7.3 (may a material legitimately bury a map for
        /// good?) is owner-level and UNRULED — until it is ruled, the cap is binding.</summary>
        public float maxTotalMassFraction = 0.35f;

        // ---------------------------------------------------------------- gameplay

        /// <summary>Depth at or above which qualifying loose haulables on a cell are
        /// swallowed into a buried cache.</summary>
        public float burialDepth = 0.6f;

        /// <summary>Depth below which a buried cache erodes back out and returns its
        /// contents. The wind-shift reveal is the scavenger campaign's hook.</summary>
        public float revealDepth = 0.25f;

        /// <summary>Lowest market value of a stack worth burying. Keeps the save from
        /// filling with one-pebble caches (design §6.3).</summary>
        public float minBurialMarketValue = 5f;

        /// <summary>Hard per-map cache count. At the cap no NEW cache cell is opened;
        /// existing caches still merge, so a drifting front keeps working.</summary>
        public int maxCachesPerMap = 400;

        /// <summary>Depth above which standing plants start to choke. Vanilla already
        /// blocks sowing and wild spawns at 0.2 (<c>PlantUtility.SandAllowsPlanting</c>);
        /// this adds the kill.</summary>
        public float plantChokeDepth = 0.5f;

        /// <summary>In-game days a fully-buried plant takes to die. The engine sizes
        /// each damage tick from this and the sampled visit rate, so the answer holds
        /// whatever <see cref="attemptsPerCellPerDay"/> is set to.</summary>
        public float plantChokeDays = 3f;

        /// <summary>Fraction of transport attempts also spent on the plant-choke pass.</summary>
        public float plantChokeSampleFraction = 0.125f;

        /// <summary>Optional filth laid down by deposition — an ash material drifts grey
        /// AND leaves grey dust. Null = none.</summary>
        public ThingDef depositFilthDef;

        /// <summary>Chance per deposition of laying <see cref="depositFilthDef"/>.</summary>
        public float depositFilthChance = 0.01f;

        // -------------------------------------------------------------------- wind

        /// <summary>Mean in-game days between prevailing-wind shifts. Vanilla has wind
        /// SPEED only — no direction exists anywhere in the engine — so the MapComponent
        /// owns an 8-way direction and random-walks it on this timescale. Wind shifts
        /// are the reveal-mechanic driver.</summary>
        public float windShiftMeanDays = 6f;

        /// <summary>Chance that a shift jumps two compass points instead of one.</summary>
        public float windShiftBigChance = 0.25f;

        // ------------------------------------------------------------------ derived

        /// <summary>Transport attempts per 250-tick batch on a map of this many cells.</summary>
        public int AttemptsPerBatch(int numCells)
        {
            return Mathf.Max(1, Mathf.RoundToInt(attemptsPerCellPerDay * numCells / 240f));
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors())
            {
                yield return error;
            }

            if (slabSize <= 0f || slabSize > 0.5f)
            {
                yield return "slabSize must be in (0, 0.5]. It is a depth quantum on a grid "
                    + "capped at 1.0; above 0.15 it also defeats SandGrid's own mesh-dirty limiter.";
            }
            if (hopRange.min < 1 || hopRange.max < hopRange.min)
            {
                yield return "hopRange must be a valid range with min >= 1 (a slab that hops 0 cells "
                    + "erodes and re-deposits in place, which is a no-op that still costs a mesh dirty).";
            }
            if (erodeMinDepth < slabSize)
            {
                yield return "erodeMinDepth (" + erodeMinDepth + ") is below slabSize (" + slabSize
                    + "): a cell could be eroded to a negative depth and get clamped, quietly losing mass.";
            }
            if (shadowRange < 0)
            {
                yield return "shadowRange must be >= 0.";
            }
            if (attemptsPerCellPerDay <= 0f)
            {
                yield return "attemptsPerCellPerDay must be > 0 or nothing ever moves.";
            }
            if (ambientDecayFactor < 0f || ambientDecayFactor > 1f)
            {
                yield return "ambientDecayFactor must be in [0,1] (it scales vanilla's own decay, "
                    + "it does not replace it).";
            }
            if (maxTotalMassFraction <= 0f || maxTotalMassFraction > 1f)
            {
                yield return "maxTotalMassFraction must be in (0,1].";
            }
            if (revealDepth >= burialDepth)
            {
                yield return "revealDepth (" + revealDepth + ") must be below burialDepth ("
                    + burialDepth + ") or a cache reveals itself on the tick it is created.";
            }
            if (plantChokeDays <= 0f)
            {
                yield return "plantChokeDays must be > 0.";
            }
            if (plantChokeSampleFraction < 0f || plantChokeSampleFraction > 1f)
            {
                yield return "plantChokeSampleFraction must be in [0,1].";
            }
            if (windShiftMeanDays <= 0f)
            {
                yield return "windShiftMeanDays must be > 0.";
            }
            if (depositFilthChance > 0f && depositFilthDef == null)
            {
                yield return "depositFilthChance is set but depositFilthDef is null — no filth can be laid.";
            }
        }
    }

    /// <summary>
    /// The three depths at which the game stops DRAWING a thing that sand has covered.
    /// These are global, not per-map: <c>ThingDef.hideAtSnowOrSandDepth</c> lives on the
    /// shared def database, so one map's material cannot own them. Single instance,
    /// <c>RM_Dunes_Globals</c>.
    /// </summary>
    public class RM_DuneGlobalsDef : Def
    {
        /// <summary>Applied to every item-category ThingDef still carrying the vanilla
        /// 99999 default.</summary>
        public float itemHideDepth = 0.45f;

        /// <summary>Applied to plants still carrying the vanilla default.</summary>
        public float plantHideDepth = 0.55f;

        /// <summary>Applied to filth still carrying the vanilla default.</summary>
        public float filthHideDepth = 0.2f;

        /// <summary>Set false to leave the def database entirely alone (debugging).</summary>
        public bool applyHideDepths = true;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors())
            {
                yield return error;
            }
            if (itemHideDepth <= 0f || itemHideDepth >= 1f
                || plantHideDepth <= 0f || plantHideDepth >= 1f
                || filthHideDepth <= 0f || filthHideDepth >= 1f)
            {
                yield return "hide depths must be in (0,1) — the sand grid is capped at 1.0, "
                    + "so a value of 1 or more can never be reached and hides nothing.";
            }
        }
    }
}
