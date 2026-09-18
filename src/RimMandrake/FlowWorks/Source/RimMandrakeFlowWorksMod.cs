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

        // ══════════════════════════════════════════════════════════════════
        // PHASE 4 — STOCK, DISPLACEMENT, RECESSION, REFILL, SINKS.
        //
        // ⚠️ DELIBERATELY ITS OWN SECTION, top to bottom: fields, ExposeData
        // lines and the screen block below all sit together and touch nothing
        // above them. A second lane was adding unrelated toggles to this file
        // in the same window; keeping Phase 4 in one contiguous run is what
        // makes both changes land without either rewriting the other's lines.
        //
        // Defaults = the behaviour this phase ships, per the standing rule
        // (owner, 2026-09-12). ALL-OFF degrades exactly to the pre-Phase-4
        // engine: dry digging, the sort-and-overflow pulse, limitless sources,
        // nothing receding, nothing refilling, nothing draining off-map.
        //  11. fillInEnabled              — the fill-in designator exists at all
        //  12. fillInDisplacementEnabled  — displaced liquid is credited back
        //  13. sourceBudgetEnabled        — the 5:1 budget; off = limitless all
        //  14. stickyLimitlessEnabled     — edge + size classification
        //  15. recessionEnabled           — a spent body gives up cells
        //  16. refillEnabled              — seepage, rain and season
        //  17. rainFillsExcavationsEnabled— ruling 25, roof grid consulted
        //  18. edgeSinksEnabled           — map-edge drainage
        public static bool fillInEnabled = true;
        public static bool fillInDisplacementEnabled = true;
        public static bool sourceBudgetEnabled = true;
        public static bool stickyLimitlessEnabled = true;
        public static bool recessionEnabled = true;
        public static bool refillEnabled = true;
        public static bool rainFillsExcavationsEnabled = true;
        public static bool edgeSinksEnabled = true;
        public static float sourceBudgetMultiplier = 1f;
        public static float minLimitlessBodyCells = 50f;
        public static float refillRateMultiplier = 1f;
        public static float rainFillPerPulse = 0.1f;

        // ══════════════════════════════════════════════════════════════════
        // PHASE 5 — CAPTURE, LADDERS, AND THE ONE SHOOTING RULE.
        //
        // ⚠️ ITS OWN CONTIGUOUS SECTION, same discipline as Phase 4 above:
        // fields, ExposeData lines and the screen block are each kept whole and
        // touch nothing around them, so a concurrent lane editing this file
        // does not have to rewrite these lines to land its own.
        //
        // Defaults = what this phase ships. All three OFF degrades to the
        // pre-Phase-5 engine: nothing captures, nothing is stranded, and every
        // verb's line of fire is vanilla's again.
        //  19. superdeepCaptureEnabled     — ruling 26, fall-in at D = 4
        //  20. superdeepCapturesOwnFaction — whether your own hole takes you too
        //  21. ladderRequiredToExitEnabled — the jailer mechanic
        //  22. superdeepShootingRuleEnabled— ruling 23, 8-way adjacency only
        //
        // 🔴 ONE DISCLOSED DEVIATION from "all-off = exactly as before". Before
        // this phase RM_Channel_Superdeep was <passability>Impassable</passability>,
        // a placeholder whose own def comment says "until fall-in capture and
        // ladders exist". They exist now, so it is passable, and passability is a
        // per-Def field that no runtime toggle can move. With capture off a
        // SUPERDEEP cell is therefore a very costly hole (pathCost 300) rather
        // than a wall. That is the placeholder retiring, not a mechanic hiding.
        public static bool superdeepCaptureEnabled = true;
        public static bool superdeepCapturesOwnFaction = false;
        public static bool ladderRequiredToExitEnabled = true;
        public static bool superdeepShootingRuleEnabled = true;

        // ══════════════════════════════════════════════════════════════════
        // LIQUID_BOTTLE_LOOP_1 — FILL / USE / DIRTY / WASH.
        //
        // ⚠️ ITS OWN CONTIGUOUS SECTION, same discipline as Phases 4/5 above.
        //
        // Both default ON -- that is the shipped campaign behaviour (design
        // "Dirty-bottle stage is a Mod Settings toggle; default ON in the
        // campaign"). Off degrades gracefully at two different joints:
        //  23. bottleLoopEnabled       — the whole fill/wash WorkGiver pair.
        //      Off: RM_BottleEmpty/RM_BottleDirty just sit there like any
        //      other item; a colonist can still hand-carry and drink a
        //      filled bottle, only the automatic fill/wash labour stops.
        //  24. bottleDirtyStageEnabled — whether "use" leaves a dirty bottle
        //      to wash at all. Off: drinking a filled bottle returns a clean
        //      empty bottle directly and RM_BottleDirty is never minted —
        //      any dirty bottle a save already holds from before the switch
        //      is still washable, since WorkGiver_WashBottle does not gate
        //      on this toggle.
        public static bool bottleLoopEnabled = true;
        public static bool bottleDirtyStageEnabled = true;

        public static int MinLimitlessBodyCells => Mathf.Max(1, Mathf.RoundToInt(minLimitlessBodyCells));

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
            // ── Phase 4 (see the block above; kept contiguous on purpose) ──
            Scribe_Values.Look(ref fillInEnabled, "fillInEnabled", true);
            Scribe_Values.Look(ref fillInDisplacementEnabled, "fillInDisplacementEnabled", true);
            Scribe_Values.Look(ref sourceBudgetEnabled, "sourceBudgetEnabled", true);
            Scribe_Values.Look(ref stickyLimitlessEnabled, "stickyLimitlessEnabled", true);
            Scribe_Values.Look(ref recessionEnabled, "recessionEnabled", true);
            Scribe_Values.Look(ref refillEnabled, "refillEnabled", true);
            Scribe_Values.Look(ref rainFillsExcavationsEnabled, "rainFillsExcavationsEnabled", true);
            Scribe_Values.Look(ref edgeSinksEnabled, "edgeSinksEnabled", true);
            Scribe_Values.Look(ref sourceBudgetMultiplier, "sourceBudgetMultiplier", 1f);
            Scribe_Values.Look(ref minLimitlessBodyCells, "minLimitlessBodyCells", 50f);
            Scribe_Values.Look(ref refillRateMultiplier, "refillRateMultiplier", 1f);
            Scribe_Values.Look(ref rainFillPerPulse, "rainFillPerPulse", 0.1f);
            // ── Phase 5 (see the block above; kept contiguous on purpose) ──
            Scribe_Values.Look(ref superdeepCaptureEnabled, "superdeepCaptureEnabled", true);
            Scribe_Values.Look(ref superdeepCapturesOwnFaction, "superdeepCapturesOwnFaction", false);
            Scribe_Values.Look(ref ladderRequiredToExitEnabled, "ladderRequiredToExitEnabled", true);
            Scribe_Values.Look(ref superdeepShootingRuleEnabled, "superdeepShootingRuleEnabled", true);
            // ── LIQUID_BOTTLE_LOOP_1 (see the block above; kept contiguous) ─
            Scribe_Values.Look(ref bottleLoopEnabled, "bottleLoopEnabled", true);
            Scribe_Values.Look(ref bottleDirtyStageEnabled, "bottleDirtyStageEnabled", true);
        }

        private static Vector2 scrollPosition = Vector2.zero;

        public void DoWindowContents(Rect inRect)
        {
            // Raised from 900 when the unproven-mechanics section landed, and
            // from 1400 when Phase 4's stock section did, and from 3000 when
            // Phase 5's capture/ladder/shooting section did: this is a FIXED view
            // height, so content taller than it is clipped rather than scrolled
            // to. Anyone adding a block here raises this number in the same
            // edit or their block is invisible.
            Rect view = new Rect(0f, 0f, inRect.width - 24f, 4200f);
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

            // ══════════════════════════════════════════════════════════════
            // PHASE 4 SECTION — kept whole and kept last, see the field block.
            // ══════════════════════════════════════════════════════════════
            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("Stock, recession and drainage");
            Text.Font = GameFont.Small;
            list.Label("How much liquid a natural body actually has, what happens when a canal "
                     + "drinks it dry, and where liquid goes when you fill a channel back in. "
                     + "Everything here is on by default; turn it all off and sources are "
                     + "bottomless, nothing recedes and nothing drains, which is how the mod "
                     + "behaved before this.");

            list.CheckboxLabeled("Fill in channels", ref fillInEnabled,
                "Adds the 'fill in canal' order — the opposite of digging. Each application "
              + "raises a cell one level; taking it all the way back to the surface restores "
              + "the terrain that was there before you dug. Off: the order refuses and the "
              + "tool is inert.");

            list.CheckboxLabeled("Filling in displaces liquid", ref fillInDisplacementEnabled,
                "Liquid pushed out of a cell you are filling flows into the rest of the "
              + "channel and back into the body it came from, so the rest of the canal gets "
              + "deeper. Only what finds no room anywhere is lost, and you are told when that "
              + "happens. Off: displaced liquid is simply lost — still reported, never silent.");

            list.CheckboxLabeled("Sources have a stock", ref sourceBudgetEnabled,
                "A natural body supplies a limited amount: each of its cells is worth a few "
              + "canal cells and no more, however big the pond looks. Run it down and the "
              + "canal stops filling. Off: every source is bottomless.");

            list.Gap();
            list.Label("Source budget: " + (5f * sourceBudgetMultiplier).ToString("F1")
                     + " canal cells per source cell");
            sourceBudgetMultiplier = list.Slider(sourceBudgetMultiplier, 0.2f, 5f);
            list.Label("The trade the whole stock model turns on. Lower makes water precious and "
                     + "a canal a real commitment; higher makes ponds generous.");

            list.CheckboxLabeled("Big bodies are limitless", ref stickyLimitlessEnabled,
                "A body that touches the map edge and is large enough is treated as fed from "
              + "off-map: it never runs down and never recedes. This is decided ONCE, the first "
              + "time you draw from it, and never revisited — so a lake cannot flicker between "
              + "limitless and limited. Off: every body is limited, including the ocean.");

            list.Gap();
            list.Label("Smallest limitless body: " + MinLimitlessBodyCells + " cells");
            minLimitlessBodyCells = list.Slider(minLimitlessBodyCells, 1f, 400f);
            list.Label("A body must touch the map edge AND be at least this big to count as "
                     + "limitless. Raise it to make even edge-clipping ponds exhaustible.");

            list.CheckboxLabeled("Bodies recede when drawn down", ref recessionEnabled,
                "A limited body that has been spent gives up cells from its outer edge inward, "
              + "so you can see it shrinking. The original terrain of every cell it gives up is "
              + "recorded and handed back when the water returns — a receding pond never "
              + "permanently changes your map. Off: the stock runs down invisibly.");

            list.CheckboxLabeled("Bodies refill", ref refillEnabled,
                "Seepage, rain and the season slowly put liquid back into a limited body, and "
              + "its cells come back in the order it gave them up. A very small seep takes "
              + "multiple seasons. Off: what you spend is gone for good.");

            list.Gap();
            list.Label("Refill speed: " + refillRateMultiplier.ToString("F2") + "x");
            refillRateMultiplier = list.Slider(refillRateMultiplier, 0.1f, 5f);
            list.Label("Slow and certain is the intent, not random. At 1x a one-cell seep needs "
                     + "the better part of a year to refill what it can support.");

            list.CheckboxLabeled("Rain fills open excavations", ref rainFillsExcavationsEnabled,
                "Rain falls into any excavated cell that is NOT roofed. Roof a pit and it stays "
              + "dry in a downpour — that is the point, and it makes roofing a real decision. "
              + "Off: weather never touches a channel.");

            list.Gap();
            list.Label("Rain fill speed: " + rainFillPerPulse.ToString("F2") + " level(s) per pulse");
            rainFillPerPulse = list.Slider(rainFillPerPulse, 0.01f, 1f);
            list.Label("How fast heavy rain fills an open trench. At the default a downpour takes "
                     + "roughly an in-game hour to add one level.");

            list.CheckboxLabeled("Map-edge sinks drain", ref edgeSinksEnabled,
                "A channel dug into the strip along the map edge is a drain: liquid reaching it "
              + "leaves the map. It is not destroyed — it goes where an edge-touching lake's "
              + "water comes from. This also lets you dig in that strip at all, which the game "
              + "normally refuses. Off: the edge strip is undiggable again and nothing drains.");

            // ══════════════════════════════════════════════════════════════
            // PHASE 5 SECTION — kept whole and kept last, see the field block.
            // ══════════════════════════════════════════════════════════════
            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("Falling in, ladders and shooting");
            Text.Font = GameFont.Small;
            list.Label("A superdeep excavation is the trapping level — the only depth that takes "
                     + "anyone. Everything shallower is wadeable however full it is: a brimming "
                     + "deep canal is a tax on crossing it, never a barrier, so stopping power "
                     + "comes from superdeep holes and nothing else.");

            list.CheckboxLabeled("Superdeep cells capture", ref superdeepCaptureEnabled,
                "Anyone who walks into a superdeep excavation falls in and is held there, whether "
              + "it is dry or brimming. They take a fall, and whatever liquid is down there then "
              + "goes to work on them. They struggle to climb out on the same clock a pit trap "
              + "uses. Off: a superdeep cell is just a very slow hole to cross.");

            list.CheckboxLabeled("Your own hole takes your own people", ref superdeepCapturesOwnFaction,
                "Off (the default), a superdeep excavation you dug ignores your own colonists, the "
              + "same way your own armed pit traps do — otherwise nobody could ever get down there "
              + "to build the ladder. On, the ground does not care whose side you are on.");

            list.CheckboxLabeled("A ladder is needed to get out", ref ladderRequiredToExitEnabled,
                "Without a ladder standing in it, a superdeep hole holds whoever is in it "
              + "indefinitely — pull the ladder and they are stranded, which is a jailer as much "
              + "as a trap. With a ladder, they can climb, and the ladder beats deep liquid that "
              + "would otherwise make climbing impossible. Off: no ladder is needed and the "
              + "struggle roll is the only thing between an occupant and the surface.");

            list.CheckboxLabeled("Superdeep limits who can shoot whom", ref superdeepShootingRuleEnabled,
                "Someone standing in a superdeep hole can only trade fire with whoever is in one "
              + "of the eight cells touching theirs, and that cuts both ways: a turret cannot "
              + "shoot into the hole unless it is right at the lip, and whoever is down there can "
              + "still shoot anyone who comes to the edge. It is a restriction only — nothing here "
              + "changes accuracy, cover or sight. Off: depth never affects shooting at all.");

            // ══════════════════════════════════════════════════════════════
            // LIQUID_BOTTLE_LOOP_1 SECTION — kept whole and kept last.
            // ══════════════════════════════════════════════════════════════
            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("Bottles: fill, use, wash");
            Text.Font = GameFont.Small;
            list.Label("An empty bottle filled at a matching liquid's shore becomes a filled bottle; "
                     + "drinking or otherwise using one leaves a bottle behind to deal with. Bottles are "
                     + "loot, not free.");

            list.CheckboxLabeled("Bottle fill/wash labour", ref bottleLoopEnabled,
                "Colonists automatically carry an empty bottle to a matching liquid's edge to fill it, "
              + "and a dirty bottle to fresh water to wash it — no order needed, the same way an empty "
              + "fuel tank is a standing invitation to refuel. Off: bottles still fill and empty by hand "
              + "if you carry and drink them yourself, but nothing does the fetching for you.");

            list.CheckboxLabeled("Using a bottle leaves it dirty", ref bottleDirtyStageEnabled,
                "Drinking a filled bottle leaves a dirty bottle that needs washing before it can be "
              + "filled again — the shipped campaign behaviour. Off: drinking returns a clean empty "
              + "bottle directly and no dirty bottles are minted; any a save already holds are still "
              + "washable.");

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
