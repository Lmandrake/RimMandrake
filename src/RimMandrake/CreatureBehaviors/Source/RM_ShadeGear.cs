using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // SHADE_GEAR_FAMILY_1 — carried and pitched shade, cross-biome.
    //
    // Three pieces, one comp, and NO parallel system: each piece writes into
    // RM_MapComponent_ShadeGrid (the same grid every shade consumer reads)
    // and its shade reaches sun heat through RM_SunHeatMath.Exposure, the
    // same rule roofs and cast shadows go through.
    //
    //   wearer    — the parasol (utility-layer apparel). Shades its wearer
    //               (read live off the worn apparel, so it moves with the
    //               pawn) and, at adjacentFactor, the one cell its shadow
    //               falls on (the grid's parasol layer, refreshed often).
    //   footprint — the shade tent (a minifiable building). Shades every
    //               cell it occupies.
    //   lee       — the sun shield (a standing panel). Throws a shadow
    //               along the sun vector from each cell it occupies, of
    //               length leeHeight × the sun's cells-per-height.
    //
    // How much of a piece's shade counts is set by the biome's heat kind
    // (RM_SunHeatExtension; a biome without one is treated as overhead):
    // overheadFactor / lowSunFactor, and ALWAYS zero under ambient heat —
    // steam and volcanic lands, where the answer is insulation or leaving.
    //
    // Depth = shadeDepth + the stuff's RM_ShadeClothExtension.shadeBonus
    // (mirrak hide carries the biggest), clamped to 1.
    //
    // Each mode has its own Mod Settings toggle (Creature Behaviors, entry
    // 40); off, that piece casts nothing and is ordinary gear.
    // ════════════════════════════════════════════════════════════════════
    public enum RM_ShadeGearMode
    {
        wearer,
        footprint,
        lee,
    }

    public class RM_CompProperties_ShadeGear : CompProperties
    {
        public RM_ShadeGearMode mode = RM_ShadeGearMode.footprint;

        /// <summary>Shade 0..1 before the stuff bonus and the kind factor.</summary>
        public float shadeDepth = 0.8f;

        public float overheadFactor = 1f;
        public float lowSunFactor = 0.3f;

        /// <summary>wearer only: the adjacent cell gets this fraction of the
        /// wearer's shade.</summary>
        public float adjacentFactor = 0.4f;

        /// <summary>lee only: the panel's shadow height (a wall is 1.0).</summary>
        public float leeHeight = 1.5f;

        /// <summary>lee only: shadow length, in cells, on a map with no sun
        /// direction at all (thrown away from the panel's face).</summary>
        public float fallbackLeeCells = 2f;

        public RM_CompProperties_ShadeGear()
        {
            compClass = typeof(RM_CompShadeGear);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (mode == RM_ShadeGearMode.wearer && parentDef.apparel == null)
            {
                yield return "RM_CompProperties_ShadeGear mode wearer on a non-apparel def";
            }
            if (mode != RM_ShadeGearMode.wearer && !typeof(Building).IsAssignableFrom(parentDef.thingClass))
            {
                yield return "RM_CompProperties_ShadeGear mode " + mode + " on a non-building def";
            }
        }
    }

    /// <summary>A pitched piece (tent, shield) asks the grid for a prompt
    /// recompute when it appears or goes, so its shade does not wait for the
    /// grid's coarse interval.</summary>
    public class RM_CompShadeGear : ThingComp
    {
        public RM_CompProperties_ShadeGear Props => (RM_CompProperties_ShadeGear)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (Props.mode != RM_ShadeGearMode.wearer)
            {
                RM_MapComponent_ShadeGrid.For(parent.Map)?.RegisterGear(parent);
            }
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            RM_MapComponent_ShadeGrid.For(map)?.UnregisterGear(parent);
        }
    }

    public static class RM_ShadeGear
    {
        public static bool ModeEnabled(RM_ShadeGearMode mode)
        {
            switch (mode)
            {
                case RM_ShadeGearMode.wearer:
                    return RM_CreatureBehaviorsSettings.parasolShadeEnabled;
                case RM_ShadeGearMode.footprint:
                    return RM_CreatureBehaviorsSettings.shadeTentEnabled;
                default:
                    return RM_CreatureBehaviorsSettings.sunShieldEnabled;
            }
        }

        public static float StuffBonus(Thing t)
        {
            return t?.Stuff?.GetModExtension<RM_ShadeClothExtension>()?.shadeBonus ?? 0f;
        }

        /// <summary>This piece's kind-resolved shade depth, or 0 when its
        /// toggle is off.</summary>
        public static float DepthOf(Thing t, RM_CompProperties_ShadeGear p, RM_HeatKind kind)
        {
            if (p == null || !ModeEnabled(p.mode))
            {
                return 0f;
            }
            return RM_SunHeatMath.GearDepth(kind, p.shadeDepth, StuffBonus(t), p.overheadFactor, p.lowSunFactor);
        }

        /// <summary>The deepest shade the pawn's worn parasol(s) give it
        /// under this heat kind, and the parasol that gives it.</summary>
        public static float WornCover(Pawn pawn, RM_HeatKind kind, out Apparel best)
        {
            best = null;
            List<Apparel> worn = pawn?.apparel?.WornApparel;
            if (worn == null || worn.Count == 0 || !RM_CreatureBehaviorsSettings.parasolShadeEnabled)
            {
                return 0f;
            }
            float cover = 0f;
            for (int i = 0; i < worn.Count; i++)
            {
                RM_CompProperties_ShadeGear p = worn[i].def.GetCompProperties<RM_CompProperties_ShadeGear>();
                if (p == null || p.mode != RM_ShadeGearMode.wearer)
                {
                    continue;
                }
                float d = DepthOf(worn[i], p, kind);
                if (d > cover)
                {
                    cover = d;
                    best = worn[i];
                }
            }
            return cover;
        }
    }
}
