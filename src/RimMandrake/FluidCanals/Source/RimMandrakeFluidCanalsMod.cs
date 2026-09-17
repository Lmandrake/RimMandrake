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

        // ── the depth engine (rulings 17-19, 21, 26) ──────────────────────
        //   4. depthEngineEnabled — master switch for the depth/fill grid and
        //      its pulse. Off: nothing pours, nothing overflows, and a dug
        //      channel is inert earthworks. Digging and the depth-derived
        //      movement cost are UNAFFECTED, because those are properties of
        //      terrain the player already paid labour for.
        //   5. pulseIntervalTicks — how often the sort-and-overflow runs.
        //      Never per tick; pillar 2 forbids a fluid simulation outright.
        //   6. flowPerPulse — how many fill levels one cell may take in from
        //      its neighbours per pulse. The viscosity dial, effectively.
        //   7. channelConfinementEnabled — the legacy release path may only
        //      enter excavated cells. Off restores the pre-2026-09-16
        //      behaviour where a release leaked across open ground.
        //   8. digToDepthEnabled — deepening. Off: one level only, the way
        //      the mod shipped before the four-depth ruling.
        public static bool depthEngineEnabled = true;
        public static float pulseIntervalTicks = 250f;
        public static float flowPerPulse = 1f;
        public static bool channelConfinementEnabled = true;
        public static bool digToDepthEnabled = true;

        public static int PulseIntervalTicks => Mathf.Max(60, Mathf.RoundToInt(pulseIntervalTicks));

        public static int FlowPerPulse => Mathf.Clamp(Mathf.RoundToInt(flowPerPulse), 1, 4);

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref canalFlowEnabled, "canalFlowEnabled", true);
            Scribe_Values.Look(ref flowRateMultiplier, "flowRateMultiplier", 1f);
            Scribe_Values.Look(ref floodVolumeMultiplier, "floodVolumeMultiplier", 1f);
            Scribe_Values.Look(ref depthEngineEnabled, "depthEngineEnabled", true);
            Scribe_Values.Look(ref pulseIntervalTicks, "pulseIntervalTicks", 250f);
            Scribe_Values.Look(ref flowPerPulse, "flowPerPulse", 1f);
            Scribe_Values.Look(ref channelConfinementEnabled, "channelConfinementEnabled", true);
            Scribe_Values.Look(ref digToDepthEnabled, "digToDepthEnabled", true);
        }

        private static Vector2 scrollPosition = Vector2.zero;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 24f, 900f);
            Widgets.BeginScrollView(inRect, ref scrollPosition, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width };
            list.Begin(view);

            Text.Font = GameFont.Medium;
            list.Label("Excavation and flow");
            Text.Font = GameFont.Small;

            list.CheckboxLabeled("Depth engine", ref depthEngineEnabled,
                "The depth/fill engine: liquid pours into the deepest excavated cells first "
              + "and overflows from a full cell into any neighbour with room. Off: nothing "
              + "pours and a dug channel is inert earthworks. Digging still works, and a "
              + "channel still costs what it costs to cross.");

            list.CheckboxLabeled("Dig deeper", ref digToDepthEnabled,
                "Digging a channel that is already dug cuts it one level further down — "
              + "shallow, mid, deep, then SUPERDEEP. Each level costs more labour than the "
              + "last. Off: channels are one level only.");

            list.CheckboxLabeled("Liquid stays in the channel", ref channelConfinementEnabled,
                "Liquid may only enter cells that have been excavated, or cells that are "
              + "already part of a liquid body. Off restores the old behaviour, where a "
              + "release spread across any open ground it could reach.");

            list.Gap();
            list.Label("Flow pulse: every " + PulseIntervalTicks + " ticks");
            pulseIntervalTicks = list.Slider(pulseIntervalTicks, 60f, 2500f);
            list.Label("How often liquid levels itself out. There is no per-tick fluid "
                     + "simulation here and there will not be one — flow happens on this "
                     + "pulse and nowhere else. A shorter pulse means livelier water and "
                     + "more work per second.");

            list.Gap();
            list.Label("Flow per pulse: " + FlowPerPulse + " level(s) per cell");
            flowPerPulse = list.Slider(flowPerPulse, 1f, 4f);
            list.Label("How many fill levels one cell can take in from its neighbours each "
                     + "pulse. Low reads as thick and slow; high reads as water.");

            list.GapLine();
            list.Label("A channel holds three visible levels of liquid, and depth decides "
                     + "how much a cell can hold. Those levels are also the unit burning "
                     + "consumes, so anything that changes the depth ladder changes how "
                     + "long a burning channel lasts. They are one number wearing two hats, "
                     + "on purpose.");
            list.GapLine();

            Text.Font = GameFont.Medium;
            list.Label("Sources (legacy)");
            Text.Font = GameFont.Small;
            list.Label("The test spring building is being replaced by a simpler rule — a "
                     + "natural liquid body IS the source, with no building involved. These "
                     + "three settings drive the old building and will retire with it.");

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
            Widgets.EndScrollView();
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
