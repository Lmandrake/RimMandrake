using UnityEngine;
using Verse;

namespace RimMandrake.FluidCanals
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Fluid Canals.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // The one mechanism this mod runs at play time is CompFluidReservoir's
    // drip/re-flood cadence (owner ruling 2026-09-04, canon_reintegration_
    // plan.md sec G8): once a canal opens next to a reservoir, it primes and
    // starts a steady drip plus periodic big re-floods, forever. Everything
    // else (Designator_DigCanal, WorkGiver_DigCanal, JobDriver_DigCanal) is
    // the labor to dig the channel in the first place and needs no gate —
    // an inert reservoir still lets a player dig a (dry) canal.
    //   1. canalFlowEnabled — master switch. Off: a dug canal never primes
    //      any reservoir, so nothing ever floods — the terrain itself
    //      (RM_Channel_Empty) is unaffected and still diggable/undiggable
    //      normally.
    //   2. flowRateMultiplier — scales how OFTEN both the drip and the
    //      re-flood fire (does not change per-fire volume).
    //   3. floodVolumeMultiplier — scales how MUCH volume each drip and
    //      re-flood releases (does not change cadence).
    // ════════════════════════════════════════════════════════════════════
    public class RimMandrakeFluidCanalsSettings : ModSettings
    {
        public static bool canalFlowEnabled = true;
        public static float flowRateMultiplier = 1f;
        public static float floodVolumeMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref canalFlowEnabled, "canalFlowEnabled", true);
            Scribe_Values.Look(ref flowRateMultiplier, "flowRateMultiplier", 1f);
            Scribe_Values.Look(ref floodVolumeMultiplier, "floodVolumeMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Fed reservoirs flow", ref canalFlowEnabled,
                "A reservoir starts flowing the moment a dug canal opens next to it. Off: "
              + "canals can still be dug, but no reservoir ever floods one.");
            list.Label("Flow speed: " + flowRateMultiplier.ToString("0.00") + "x");
            flowRateMultiplier = list.Slider(flowRateMultiplier, 0.25f, 3f);
            list.Label("How often a reservoir drips or re-floods. Does not change how much "
                     + "water each release carries.");
            list.Gap();
            list.Label("Flood size: " + floodVolumeMultiplier.ToString("0.00") + "x");
            floodVolumeMultiplier = list.Slider(floodVolumeMultiplier, 0.25f, 3f);
            list.Label("How much water each drip or re-flood releases. Does not change how "
                     + "often a reservoir fires.");

            list.End();
        }
    }

    public class RimMandrakeFluidCanalsMod : Mod
    {
        public static RimMandrakeFluidCanalsSettings settings;

        public RimMandrakeFluidCanalsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RimMandrakeFluidCanalsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Fluid Canals";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
