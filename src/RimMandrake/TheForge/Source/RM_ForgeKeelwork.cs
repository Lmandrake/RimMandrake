using System.Text;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.TheForge
{
    // ════════════════════════════════════════════════════════════════════
    // FORGE_GPT_ENRICHMENT_1 §1 — floatstone keelwork.
    //
    // MEASURED (RimSage, decompiled 1.6, 2026-10-01): Odyssey's gravship has
    // no mass or payload term at all. Launch cost is fuel, and the one knob
    // is Building_GravEngine.FuelSavingsPercent, the clamped sum of every
    // linked CompGravshipFacility's Props.fuelSavingsPercent; FuelPerTile is
    // 10 * (1 - that). Vanilla's fuel optimizer is exactly such a facility.
    // So the keel brace needs NO Harmony hook into the calculation: it is a
    // gravship facility carrying fuelSavingsPercent, linked to the grav
    // engine by Patches/RM_TheForge_KeelBraceLink.xml. "Mass saved" is
    // therefore shown as fuel saved, the only quantity the engine has.
    //
    // This file adds the inspect string (what this brace saves, what the
    // ship now burns) and the settings toggle, which rewrites the brace's
    // fuelSavingsPercent between its shipped value and 0 (0 is what the
    // engine's own "> 0f" test skips).
    // ════════════════════════════════════════════════════════════════════
    public class CompProperties_KeelBrace : CompProperties
    {
        public CompProperties_KeelBrace()
        {
            compClass = typeof(RM_CompKeelBrace);
        }
    }

    public class RM_CompKeelBrace : ThingComp
    {
        public override string CompInspectStringExtra()
        {
            if (!parent.Spawned || !ModsConfig.OdysseyActive)
            {
                return null;
            }
            if (!RM_TheForgeSettings.Active(RM_TheForgeSettings.keelworkEnabled))
            {
                return "Floatstone keelwork is switched off in Mod Settings.";
            }
            CompGravshipFacility facility = parent.TryGetComp<CompGravshipFacility>();
            Building_GravEngine engine = facility?.engine;
            if (facility == null || engine == null || !facility.CanBeActive)
            {
                return null;
            }
            float braces = 0f;
            foreach (CompGravshipFacility comp in engine.GravshipComponents)
            {
                if (comp.parent.Spawned && comp.CanBeActive && comp.parent.TryGetComp<RM_CompKeelBrace>() != null)
                {
                    braces += comp.Props.fuelSavingsPercent;
                }
            }
            float total = engine.FuelSavingsPercent;
            float without = Mathf.Clamp01(total - braces);
            StringBuilder sb = new StringBuilder();
            sb.Append("Keelwork: this brace saves ").Append(facility.Props.fuelSavingsPercent.ToStringPercent("F0"))
              .Append(" fuel; all braces ").Append(braces.ToStringPercent("F0")).Append('.');
            sb.AppendLine();
            sb.Append("Ship burns ").Append(engine.FuelPerTile.ToString("0.##"))
              .Append(" fuel per tile (").Append((10f * (1f - without)).ToString("0.##")).Append(" without keelwork).");
            return sb.ToString();
        }
    }

    public static class RM_KeelworkUtility
    {
        private static float shippedSavings = -1f;

        /// <summary>Puts the brace's fuel savings at its shipped value, or 0
        /// with the toggle off. Called at startup and on every settings save.</summary>
        public static void ApplySetting()
        {
            ThingDef brace = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FloatstoneKeelBrace");
            CompProperties_GravshipFacility props = brace?.GetCompProperties<CompProperties_GravshipFacility>();
            if (props == null)
            {
                return;
            }
            if (shippedSavings < 0f)
            {
                shippedSavings = props.fuelSavingsPercent;
            }
            props.fuelSavingsPercent = RM_TheForgeSettings.Active(RM_TheForgeSettings.keelworkEnabled) ? shippedSavings : 0f;
        }
    }

    // Glassy ring at launch. GravshipUtility.GenerateGravship(engine) is the launch
    // entry point (RimSage 1.6): it runs once per launch, before anything is despawned,
    // so the braces still stand on the departing map. One ring per linked, active brace,
    // each a little higher so four braces chord instead of stacking into one hit.
    [HarmonyPatch(typeof(GravshipUtility), nameof(GravshipUtility.GenerateGravship))]
    public static class RM_Patch_KeelRing
    {
        public static void Prefix(Building_GravEngine engine)
        {
            if (!RM_TheForgeSettings.Active(RM_TheForgeSettings.keelworkEnabled)
                || !RM_TheForgeSettings.Active(RM_TheForgeSettings.keelRingEnabled)
                || engine == null || !engine.Spawned)
            {
                return;
            }
            SoundDef ring = RM_TheForgeDefOf.RM_ForgeVoice_KeelRing;
            if (ring == null)
            {
                return;
            }
            int n = 0;
            foreach (CompGravshipFacility comp in engine.GravshipComponents)
            {
                if (comp.parent.Spawned && comp.CanBeActive && comp.parent.TryGetComp<RM_CompKeelBrace>() != null)
                {
                    SoundInfo info = SoundInfo.InMap(new TargetInfo(comp.parent.Position, comp.parent.Map));
                    info.pitchFactor = 1f + 0.12f * n;
                    ring.PlayOneShot(info);
                    n++;
                }
            }
        }
    }
}
