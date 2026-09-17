using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for FlowWorks.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // This screen covers the EXCAVATION AND FLOW half of FlowWorks. The pit
    // family and the water-effects engine came in with the 2026-09-16 merge
    // and keep their own screens, listed beside this one under the FlowWorks
    // name (Source/Pits/PitsMod.cs, Source/ManyWaters/RiverSteamSettings.cs).
    //
    // ⚠️ `canalFlowEnabled`, `flowRateMultiplier` and `floodVolumeMultiplier`
    // are GONE. They existed only to scale CompFluidReservoir's drip and
    // re-flood cadence, and ruling 24 (owner, 2026-09-16) deleted that comp
    // outright — a source is not a building. A slider that moves nothing is
    // worse than an absent one, so they are removed rather than left inert.
    // ════════════════════════════════════════════════════════════════════
    public class RimMandrakeFlowWorksSettings : ModSettings
    {
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

        // ── UNPROVEN MECHANICS, OFF BY DEFAULT ───────────────────────────
        // The standing rule is "defaults = shipped behavior". These two came
        // in with the 2026-09-16 LiquidTypes merge, and LiquidTypes was never
        // in the live ModsConfig — so their shipped behavior is that they have
        // never run at all. LIQUID_TYPES_SPIKES_1 says it plainly of the
        // ignition prototype: "has never ticked inside a running game".
        // Faithful to that, both default OFF. Turning them ON is the owner's
        // call AFTER a live proof, not a default an agent quietly chose for
        // him — a merge must not smuggle unproven damage into a campaign.
        //
        // Gated at the top of each MapComponentTick rather than by dropping
        // the component: a MapComponent is scribed per map, and removing one
        // that a save already carries is a save-compat problem. Off means it
        // ticks and returns; the component still exists, still loads, and
        // flipping the toggle needs no new game.
        //   9. liquidCorrosionEnabled  — LiquidCorrosionMapComponent
        //  10. liquidIgnitionEnabled   — LiquidIgnitionMapComponent
        public static bool liquidCorrosionEnabled = false;
        public static bool liquidIgnitionEnabled = false;

        public static int PulseIntervalTicks => Mathf.Max(60, Mathf.RoundToInt(pulseIntervalTicks));

        public static int FlowPerPulse => Mathf.Clamp(Mathf.RoundToInt(flowPerPulse), 1, 4);

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref depthEngineEnabled, "depthEngineEnabled", true);
            Scribe_Values.Look(ref pulseIntervalTicks, "pulseIntervalTicks", 250f);
            Scribe_Values.Look(ref flowPerPulse, "flowPerPulse", 1f);
            Scribe_Values.Look(ref channelConfinementEnabled, "channelConfinementEnabled", true);
            Scribe_Values.Look(ref digToDepthEnabled, "digToDepthEnabled", true);
            Scribe_Values.Look(ref liquidCorrosionEnabled, "liquidCorrosionEnabled", false);
            Scribe_Values.Look(ref liquidIgnitionEnabled, "liquidIgnitionEnabled", false);
        }

        private static Vector2 scrollPosition = Vector2.zero;

        public void DoWindowContents(Rect inRect)
        {
            // Raised from 900 when the unproven-mechanics section landed: this
            // is a FIXED view height, so content taller than it is clipped
            // rather than scrolled to.
            Rect view = new Rect(0f, 0f, inRect.width - 24f, 1400f);
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
            list.Label("Sources are terrain, not buildings: a natural liquid body is itself "
                     + "the source — a superdeep cell that is already full, which is why it "
                     + "spills into any shallower channel dug at its edge. There is nothing "
                     + "to place and nothing to tune.");

            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("Unproven mechanics — OFF by default");
            Text.Font = GameFont.Small;
            list.Label("These came in with the liquid-types merge and have never run inside a "
                     + "live game. They are off because that is what has actually shipped, not "
                     + "because they are broken. Turn one on when you want to test it, and "
                     + "expect it to be rough.");

            list.CheckboxLabeled("Liquid corrosion", ref liquidCorrosionEnabled,
                "Standing in an acidic or caustic liquid damages a pawn and eats the apparel "
              + "it is wearing, per that liquid's registry row. UNTESTED in a running game: "
              + "it can destroy worn gear, and it acts on colonists exactly as it acts on "
              + "raiders. Off: the rule is inert and liquids are just terrain.");

            list.CheckboxLabeled("Liquid ignition", ref liquidIgnitionEnabled,
                "A flammable liquid catches fire when something hot or electrical touches it — "
              + "never spontaneously. UNTESTED in a running game, and it is a prototype rather "
              + "than the finished burn model FlowWorks owes. Off: flammable liquids sit there.");

            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RimMandrakeFlowWorksMod : Mod
    {
        public static RimMandrakeFlowWorksSettings settings;

        public RimMandrakeFlowWorksMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RimMandrakeFlowWorksSettings>();
        }

        public override string SettingsCategory()
        {
            // Grouped by origin: three Mod classes ship in this one assembly
            // (RimWorld instantiates every Mod subclass it finds, one screen
            // each — LoadedModManager.CreateModClasses), so they are named to
            // sort together in the settings list.
            return "FlowWorks: Excavation & Flow";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
