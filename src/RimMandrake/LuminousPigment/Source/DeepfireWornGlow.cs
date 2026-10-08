using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_WORN_GLOW_1, spec §3.4: what a pawn's worn/equipped Deepfire
    // gear adds up to. One light per glowing pawn (never per item):
    //  - radius   = the pawn's highest coat's radius;
    //  - colour   = the coat-weighted blend of every glowing item's hue,
    //               lit at the brightest coat's intensity ("the brightest
    //               coat's colour blended across the pawn's glowing items").
    public static class WornGlowUtility
    {
        // Apparel.Wearer for apparel; Pawn_EquipmentTracker.pawn (public
        // field, RimSage Verse/Pawn_EquipmentTracker.cs) for equipment.
        public static Pawn WearerOf(Thing thing)
        {
            if (thing is Apparel ap && ap.Wearer != null) return ap.Wearer;
            if (thing?.ParentHolder is Pawn_EquipmentTracker eq) return eq.pawn;
            return null;
        }

        public static IEnumerable<ThingWithComps> WornAndEquipped(Pawn pawn)
        {
            if (pawn?.apparel != null)
            {
                List<Apparel> worn = pawn.apparel.WornApparel;
                for (int i = 0; i < worn.Count; i++) yield return worn[i];
            }
            if (pawn?.equipment != null)
            {
                List<ThingWithComps> eq = pawn.equipment.AllEquipmentListForReading;
                for (int i = 0; i < eq.Count; i++) yield return eq[i];
            }
        }

        // Gizmo list: worn apparel + equipped weapons that can take a coat.
        public static List<ThingWithComps> Lacquerable(Pawn pawn)
        {
            var list = new List<ThingWithComps>();
            foreach (ThingWithComps t in WornAndEquipped(pawn))
            {
                CompDeepfire comp = t.GetComp<CompDeepfire>();
                if (comp != null && comp.CanAddCoat) list.Add(t);
            }
            return list;
        }

        public static bool TryComputeLight(Pawn pawn, out Color color, out float radius)
        {
            color = Color.black;
            radius = 0f;
            var coats = new List<int>();
            var rs = new List<float>();
            var gs = new List<float>();
            var bs = new List<float>();
            foreach (ThingWithComps t in WornAndEquipped(pawn))
            {
                CompDeepfire comp = t.GetComp<CompDeepfire>();
                if (comp == null || comp.coats <= 0) continue;
                // Full-intensity hue of this item, weighted by its coats.
                Color c = DeepfireColorUtility.GlowColorFor(t.DrawColor, CompDeepfire.MaxCoats);
                coats.Add(comp.coats); rs.Add(c.r); gs.Add(c.g); bs.Add(c.b);
            }
            if (!RM_DeepfireRules.WornBlend(coats, rs, gs, bs, LuminousPigmentSettings.coatIntensity, CompDeepfire.MaxCoats,
                    out float r, out float g, out float b, out int maxCoats)) return false;
            color = new Color(r, g, b, 1f);
            radius = DeepfireColorUtility.RadiusForCoats(maxCoats);
            return true;
        }
    }

    // Spec §3.4 "Easier to hit in the dark": the target has an active worn
    // Deepfire glow AND its surroundings are dark WITHOUT our light.
    public static class DeepfireDarkness
    {
        public static bool IsGlowingInDark(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned) return false;
            MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(pawn.Map);
            if (mc == null || !mc.TryGetWornLight(pawn, out ColorInt ownColor, out float ownRadius)) return false;
            return OtherLightAt(pawn.Map, pawn.Position, ownColor, ownRadius) < DeepfirePaintDefaults.DarkGroundGlowMax
                && SkyIsDark(pawn.Map, pawn.Position);
        }

        private static bool SkyIsDark(Map map, IntVec3 c)
        {
            if (map.roofGrid.Roofed(c)) return true; // indoors: only the ground test counts
            return map.skyManager.CurSkyGlow <= DeepfirePaintDefaults.DarkSkyGlowMax;
        }

        // GroundGlowAt(c, ignoreSky: true) re-derived from the public
        // accumulated colour (GlowGrid.VisualGlowAt) with OUR proxy's own
        // centre-cell contribution taken off first. Lights accumulate
        // additively (GlowGrid.CombineColorsJob.AddColors), and a light's
        // centre cell receives glowColor * Lerp(1 - 1/radius, 1, 0.4)
        // (ComputeGlowGridsJob.SetGlowFromDist at intDist 100). The pawn
        // stands on its proxy's cell whenever this is asked between polls
        // closer than WornLightTickInterval; in between it is off by at most
        // one cell, which only makes the subtraction slightly generous.
        public static float OtherLightAt(Map map, IntVec3 c, ColorInt own, float ownRadius)
        {
            Color32 acc = map.glowGrid.VisualGlowAt(c);
            return RM_DeepfireRules.OtherLightAt(acc.a == 1, acc.r, acc.g, acc.b, own.r, own.g, own.b, ownRadius,
                DeepfirePaintDefaults.GlowFalloffLerp, DeepfirePaintDefaults.GroundGlowFactor, DeepfirePaintDefaults.MaxNonOverlitGroundGlow);
        }
    }
}
