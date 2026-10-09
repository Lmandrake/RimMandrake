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
                if (comp != null && comp.CanAddCoat && LacquerAllowed(t)) list.Add(t);
            }
            return list;
        }

        // GPT review #7: the worn paths obey the same Mod Settings gates as
        // the designator (paintingEnabled + the per-class toggle).
        public static bool LacquerAllowed(Thing t)
        {
            return t != null && LuminousPigmentSettings.paintingEnabled && DeepfireTargetClassUtility.IsPaintable(t);
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
                // Unscaled hue of this item, weighted by its coats; WornBlend applies intensity once.
                Color c = DeepfireColorUtility.GlowHueFor(t.DrawColor);
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
    // Deepfire glow (or, HEDIFF_GLOW_TARGETING_PULSE_1, a lit glow-hediff)
    // AND its surroundings are dark WITHOUT our light.
    public static class DeepfireDarkness
    {
        public static bool IsGlowingInDark(Pawn pawn) => TargetFactorInDark(pawn) > 0f;

        private static readonly List<float> tmpR = new List<float>(), tmpG = new List<float>(), tmpB = new List<float>(), tmpRad = new List<float>();

        /// <summary>The ranged target-size factor this pawn's own light earns in the dark, or 0 when it is not
        /// glowing in the dark. Worn gear earns glowTargetFactor; a glow-hediff earns its glowTargetFactorOverride
        /// when that is set (hair-glow, vermilion: 1.5), else glowTargetFactor; the largest wins.</summary>
        public static float TargetFactorInDark(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned) return 0f;
            MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(pawn.Map);
            if (mc == null) return 0f;
            tmpR.Clear(); tmpG.Clear(); tmpB.Clear(); tmpRad.Clear();
            float factor = 0f;
            // WORN_DARKNESS_PROXY_POSITION_1: evaluate at the proxy's ACTUAL cell (its centre-cell contribution is
            // exact there), not pawn.Position, which can be one poll ahead of it.
            IntVec3 at = IntVec3.Invalid;
            if (mc.TryGetWornLight(pawn, out ColorInt wc, out float wr) && Emits(wc, wr)
                && mc.TryGetWornProxyCell(pawn, out IntVec3 wcell))
            {
                at = wcell;
                factor = LuminousPigmentSettings.glowTargetFactor;
                Add(wc, wr);
            }
            // PROVISIONAL (auto-decided 2026-10-09, HEDIFF_GLOW_TARGETING_PULSE_1): glow-hediff lights feed the
            // same darkness model, carrying their override.
            if (LuminousPigmentSettings.hediffGlowInCombat && pawn.health?.hediffSet != null)
            {
                List<Hediff> hs = pawn.health.hediffSet.hediffs;
                for (int i = 0; i < hs.Count; i++)
                {
                    HediffComp_DeepfireGlow comp = hs[i].TryGetComp<HediffComp_DeepfireGlow>();
                    if (comp == null || !mc.TryGetHediffLight(pawn, hs[i].def, out ColorInt hc, out float hr, out IntVec3 hcell)
                        || !Emits(hc, hr)) continue;
                    if (!at.IsValid) at = hcell;
                    if (hcell == at) Add(hc, hr); // a light centred elsewhere is not subtracted as centre-cell glow
                    float o = comp.Props.glowTargetFactorOverride;
                    factor = Mathf.Max(factor, o != 1f ? o : LuminousPigmentSettings.glowTargetFactor);
                }
            }
            if (factor <= 0f || !at.IsValid || !at.InBounds(pawn.Map)) return 0f;
            Color32 acc = pawn.Map.glowGrid.VisualGlowAt(at);
            float other = RM_DeepfireRules.OtherLightAtMany(acc.a == 1, acc.r, acc.g, acc.b, tmpR, tmpG, tmpB, tmpRad,
                DeepfirePaintDefaults.GlowFalloffLerp, DeepfirePaintDefaults.GroundGlowFactor, DeepfirePaintDefaults.MaxNonOverlitGroundGlow);
            return other < DeepfirePaintDefaults.DarkGroundGlowMax && SkyIsDark(pawn.Map, at) ? factor : 0f;
        }

        // GPT review #13: a black light (glowMinValue 0 on dark dye) emits nothing and is no beacon.
        private static bool Emits(ColorInt c, float radius) => radius > 0f && (c.r > 0 || c.g > 0 || c.b > 0);

        private static void Add(ColorInt c, float radius)
        {
            tmpR.Add(c.r); tmpG.Add(c.g); tmpB.Add(c.b); tmpRad.Add(radius);
        }

        private static bool SkyIsDark(Map map, IntVec3 c)
        {
            if (map.roofGrid.Roofed(c)) return true; // indoors: only the ground test counts
            return map.skyManager.CurSkyGlow <= DeepfirePaintDefaults.DarkSkyGlowMax;
        }

        // GroundGlowAt(c, ignoreSky: true) re-derived from the public
        // accumulated colour (GlowGrid.VisualGlowAt) with OUR lights' own
        // centre-cell contributions taken off first (RM_DeepfireRules.OtherLightAtMany).
        // Lights accumulate additively (GlowGrid.CombineColorsJob.AddColors), and a
        // light's centre cell receives glowColor * Lerp(1 - 1/radius, 1, 0.4)
        // (ComputeGlowGridsJob.SetGlowFromDist at intDist 100) -- exact only AT the
        // proxy's cell, which is why TargetFactorInDark evaluates there.
    }
}
