using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // SEA_DIVE_MAPS_BUILD_1 — Mod Settings, rewritten wholesale.
    // The shore-terrain "dive to hunt/commune" mechanic (SCALD_DIVING_MOD_1)
    // is RETIRED per the SHIP-ONLY ACCESS ruling (owner, 2026-09-26): this
    // mod is now the ship-hatch pocket-map mechanism. Precedent for the
    // pattern: src/RimStarWars/Shokk/Source/RSW_ShokkSettings.cs.
    //
    // MOD_OPTIONS_RETROFIT_1 doctrine (CLAUDE.md "Every mod ships superb Mod
    // Settings"): defaults = shipped, all-off degrades gracefully
    // (masterEnabled false makes every RM_SeaDiveHatch un-enterable
    // everywhere, on any sea, in any biome).
    // ════════════════════════════════════════════════════════════════════
    public class RM_DivingSettings : ModSettings
    {
        public static bool masterEnabled = true;

        // SHIP-ONLY ACCESS RULING enforcement toggle. Default true matches
        // the ruling; off exists purely so a franchise-free/no-DLC install,
        // a modded ruleset, or a debug session can build+test the hatch
        // without also owning a completed gravship — degrades gracefully
        // per MOD_OPTIONS_RETROFIT_1, it does not remove the ruling from
        // About.xml's description of shipped default behavior.
        public static bool requireGravEngine = true;

        // GREYSEA_BRINE_POOL_DEFENCE_1, 2026-09-26. The Grey Sea floor's
        // crystallisation defence: touch a brine pool (or stand in a salt
        // chimney's plume) and you are encased as an object that must be
        // mined out — the owner's ruling Q1(b), 2026-09-26.
        //
        // It gets its own toggle rather than riding masterEnabled because it
        // is the one mechanic in this mod that can take a colonist out of the
        // player's hands without a fight, and MOD_OPTIONS_RETROFIT_1's rule
        // is a toggle per major mechanic. Default ON = shipped behaviour.
        // Off: the pools are merely slow water, and any jacket already on a
        // saved map still exists and can still be mined out — turning the
        // mechanic off never strands a pawn inside one.
        public static bool greyPoolDefenceEnabled = true;

        // GREYSEA_RULED_CONTENT_1, Q13 (question card 2026-09-27). The
        // orruhmu (RM_Orruhmu / RM_CompPoolSentinelSquirt): a pool-shore
        // sentinel that squirts and encases the nearest of 2+ crowding
        // intruders, the third trigger on the same consequence as the pool/
        // chimney defence above. Own toggle for the same reason: it can take
        // a colonist out of the player's hands with no fight. Default ON.
        // Off: the orruhmu never squirts — it is just a strange dome.
        public static bool greyPoolSentinelEnabled = true;

        // GREYSEA_BRINE_ELDERS_1, 2026-09-26. The Brine Elder's blinding EMP
        // discharge — both the rare unprompted event and the defensive
        // reaction to disturbance (RM_Building_BrineElder). Its own toggle
        // because, like the pool defence above, it can stun a colonist (and
        // any mech) with no warning beyond the charge tell. Off: the Elder
        // never discharges; the trade below is unaffected.
        public static bool greyElderDischargeEnabled = true;

        // The novelty trade (Dialog_OfferToElder / RM_ElderTradeUtility).
        // Off: the Elder's gizmo disappears and nothing can be offered —
        // the seen-set already recorded stays recorded (it costs nothing to
        // leave it), so re-enabling later never un-values anything.
        public static bool greyElderTradeEnabled = true;

        // CHILL_FIRE_BAN_1, 2026-09-27. "There's no oxygen down in the sea
        // floor so it's not explosive" — no flame works on the Chill
        // seabed pocket map (fire spawns, campfires/torches, fuel-burning
        // heat) unless a future mechanism marks a zone oxygenated, or the
        // igniting Thing carries its own oxidizer (Fuselight). Own toggle:
        // off restores plain vanilla fire behaviour on that one map, for
        // testing or a different ruleset — every other map is unaffected
        // either way, on or off.
        public static bool chillFireBanEnabled = true;

        // CHILL_THERMAL_ENGINE_1, 2026-09-27/28. The boil shroud: liquid-
        // adjacent bubble/boil flecks near a warm hull and a smaller shimmer
        // around any warm thing (pawn, powered device) standing outdoors on
        // the Chill seabed. Purely cosmetic — see
        // RM_MapComponent_ChillBoilShroud.cs — so its own toggle exists only
        // because every mechanic in this kit gets one per
        // MOD_OPTIONS_RETROFIT_1; off changes nothing mechanical either way.
        // The cryogenic ambient temperature itself (the actual cooling
        // load) is NOT gated by a toggle here — it rides masterEnabled/
        // requireGravEngine like the rest of the map's identity, because it
        // is vanilla's own MapTemperature/Room machinery reading a
        // MapGeneratorDef field, not a mechanic this mod can switch off
        // without switching off the whole pocket map.
        public static bool chillBoilShroudEnabled = true;

        // CHILL_HEATED_SUIT_1, 2026-09-28. The heated dive suit's battery
        // gauge — drains outdoors on the Chill seabed, recharges near a
        // powered RM_HeatedSuitCharger. Own toggle per MOD_OPTIONS_
        // RETROFIT_1: off degrades gracefully to "always full," i.e. the
        // suit's charge-gated cold protection is simply always on and the
        // charger building becomes inert decoration — off never strands a
        // colonist on a dead battery mid-dive.
        public static bool chillHeatedSuitEnabled = true;

        // CHILL_GARDEN_DEFENSE_1, 2026-09-28. The garden's tiered immune
        // system: harvesting/killing floor life/directed heat draws an
        // Iliss arc (stinging, survivable), sustained destruction wakes a
        // bounded skirmish of dormant RM_Tarnn. Own toggle per MOD_OPTIONS_
        // RETROFIT_1: off degrades to "the garden never fights back" — no
        // arcs, no wake, floor life is simply passive/huntable like any
        // other wildlife. Never strands anyone: RM_Tarnn's dormancy comp
        // just never gets its WakeUp() call, so a toggled-off Tarnn is
        // identical to an ordinary sessile floor-life creature.
        public static bool chillGardenDefenseEnabled = true;

        // CHILL_THERMAL_FOOTPRINTS_1, 2026-09-28. "Everything warm marks
        // the Chill's ice floor" — a walking pawn's melt-prints and a
        // parked powered device's polished shadow, both a permanent-ish
        // RM_Filth_ChillFrostGlaze deposit
        // (RM_MapComponent_ChillFootprints.cs). Own toggle per MOD_
        // OPTIONS_RETROFIT_1: off means nothing new is ever deposited and
        // RM_MapComponent_ChillFootprints.TrailDensityAt always reads 0
        // (so CHILL_GARDEN_DEFENSE_1's trail-density threshold discount
        // simply never applies) — frost glaze already on a saved map
        // stays exactly as visible and cleanable as any other filth
        // either way, so toggling this off never erases history, only
        // stops writing more of it.
        public static bool chillThermalFootprintsEnabled = true;

        // CHILL_FLOOR_LIGHT_1, 2026-09-28. The drowned aurora: a map-wide
        // violet-teal glow on the Chill seabed that rises and falls with
        // whichever aurora GameCondition is active on the SURFACE map above
        // (Patch_ChillDrownedAurora.cs + RM_MapComponent_ChillDrownedAurora.cs).
        // Own toggle per MOD_OPTIONS_RETROFIT_1: off degrades to "no layer-1
        // light" — the seabed keeps whatever baseline glow vanilla's own
        // weather/GameCondition blend already produces for it (this toggle
        // never darkens anything below that), and layer 2 (Fuselight/
        // Ghostpane's ordinary CompGlower point light) is completely
        // unaffected either way, so the floor never goes fully black from
        // toggling this off.
        public static bool chillDrownedAuroraEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref requireGravEngine, "requireGravEngine", true);
            Scribe_Values.Look(ref greyPoolDefenceEnabled, "greyPoolDefenceEnabled", true);
            Scribe_Values.Look(ref greyPoolSentinelEnabled, "greyPoolSentinelEnabled", true);
            Scribe_Values.Look(ref greyElderDischargeEnabled, "greyElderDischargeEnabled", true);
            Scribe_Values.Look(ref greyElderTradeEnabled, "greyElderTradeEnabled", true);
            Scribe_Values.Look(ref chillFireBanEnabled, "chillFireBanEnabled", true);
            Scribe_Values.Look(ref chillBoilShroudEnabled, "chillBoilShroudEnabled", true);
            Scribe_Values.Look(ref chillHeatedSuitEnabled, "chillHeatedSuitEnabled", true);
            Scribe_Values.Look(ref chillGardenDefenseEnabled, "chillGardenDefenseEnabled", true);
            Scribe_Values.Look(ref chillThermalFootprintsEnabled, "chillThermalFootprintsEnabled", true);
            Scribe_Values.Look(ref chillDrownedAuroraEnabled, "chillDrownedAuroraEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Sea diving enabled", ref masterEnabled,
                "Master switch. Off: no RM_SeaDiveHatch anywhere can be entered — the mod is "
              + "fully inert (existing hatches stay buildable but never open a pocket map).");

            if (masterEnabled)
            {
                list.Gap();
                list.CheckboxLabeled("Require a grav engine to build a dive hatch", ref requireGravEngine,
                    "Shipped default: ON. The owner's ruling is that a gravship is the sole way "
                  + "to reach a sea floor — turning this off lets the hatch be built anywhere, for "
                  + "testing or a different ruleset, but that is not the shipped experience.");

                list.Gap();
                list.CheckboxLabeled("Grey Sea: brine pools crystallise intruders", ref greyPoolDefenceEnabled,
                    "Shipped default: ON. On the Grey Sea's floor, touching a brine pool — or "
                  + "standing in a salt chimney's plume — encases a colonist in salt. They are "
                  + "not downed; they are an object, and another colonist has to MINE them out "
                  + "before they smother. Off: the pools are merely slow water. Jackets already "
                  + "on a saved map keep working either way, so switching this off never leaves "
                  + "anyone sealed in.");

                list.Gap();
                list.CheckboxLabeled("Grey Sea: orruhmu pool sentinels squirt intruders", ref greyPoolSentinelEnabled,
                    "Shipped default: ON. An orruhmu (a salt-dome-mimic creature stationed on brine "
                  + "pool shores) swells as a warning, then squirts and encases the nearest colonist "
                  + "if 2 or more crowd within 5 cells — a lone worker is always safe. Off: orruhmu "
                  + "never squirt; they remain harmless, mineral-mimicking dressing.");

                list.Gap();
                list.CheckboxLabeled("Grey Sea: Brine Elders can discharge", ref greyElderDischargeEnabled,
                    "Shipped default: ON. Each Grey Sea floor's Brine Elder builds a visible charge "
                  + "and, once full, releases a blinding EMP burst on its own — or immediately if "
                  + "its pool is disturbed (attacked, or a nearby jacket mined). Stuns anyone "
                  + "nearby and breaks active shields. Off: the Elder never discharges; the trade "
                  + "below is unaffected either way.");

                list.Gap();
                list.CheckboxLabeled("Grey Sea: Brine Elders trade on novelty", ref greyElderTradeEnabled,
                    "Shipped default: ON. Offer a specimen and the Elder pays well for the first "
                  + "of its kind it has ever seen at THIS pool, and almost nothing for a repeat — "
                  + "every Grey Sea tile keeps its own memory, so travelling to another tile finds "
                  + "a market that has never seen your find. Off: the Elder's trade gizmo "
                  + "disappears; nothing already recorded is lost.");

                list.Gap();
                list.CheckboxLabeled("The Chill: no fire on the seabed", ref chillFireBanEnabled,
                    "Shipped default: ON. \"There's no oxygen down in the sea floor so it's not "
                  + "explosive\" — on the Chill's seabed pocket map, campfires and torches never "
                  + "light (or go dark if already burning), fuel-burning heat stops working, and "
                  + "molotovs/incendiaries splash inert. Heat there is electric-only. A creature or "
                  + "plant that carries its own oxidizer (built under a separate item) is exempt. "
                  + "Off: fire behaves normally down there, for testing or a different ruleset. "
                  + "Every other map is unaffected either way.");

                list.Gap();
                list.CheckboxLabeled("The Chill: boil shroud visuals", ref chillBoilShroudEnabled,
                    "Shipped default: ON. Purely cosmetic. Liquid near any heated room's walls "
                  + "bubbles as the warm hull boils the cryogenic lake beside it, and a smaller "
                  + "shimmer follows any live colonist or powered device standing outdoors down "
                  + "there. Off: no flecks, nothing mechanical changes — the cold and the room "
                  + "freezing it fights are unaffected either way.");

                list.Gap();
                list.CheckboxLabeled("The Chill: heated suit battery drains", ref chillHeatedSuitEnabled,
                    "Shipped default: ON. The heated dive suit's battery drains while worn "
                  + "outdoors on the Chill's seabed, and recharges near a powered suit charging "
                  + "rack. An empty suit gives no cold protection at all, only vanilla's own "
                  + "hypothermia to fight on the walk back. Off: the suit's cold protection is "
                  + "simply always on, and the charging rack becomes inert decoration — never "
                  + "strands anyone on a dead battery.");

                list.Gap();
                list.CheckboxLabeled("The Chill: the garden defends itself", ref chillGardenDefenseEnabled,
                    "Shipped default: ON. Harvesting past a threshold, killing floor life, or hitting "
                  + "it with directed heat draws a survivable electric arc from the Iliss. Sustained "
                  + "destruction wakes a bounded group of dormant Tarnn into one hard, winnable fight "
                  + "— never a raid, never repeating. Off: the floor garden never fights back; floor "
                  + "life is simply passive wildlife.");

                list.Gap();
                list.CheckboxLabeled("The Chill: thermal footprints", ref chillThermalFootprintsEnabled,
                    "Shipped default: ON. Everything warm marks the seabed's ice: a walking colonist "
                  + "leaves a thin trail of refrozen glossy melt-prints, and a parked powered device "
                  + "saturates a denser \"polished shadow\" under itself. Permanent-ish — it does not "
                  + "melt back on its own, only ordinary filth-cleaning removes it. A heavily-trailed "
                  + "site also makes the garden's own defenses escalate faster on a return visit. Off: "
                  + "nothing new is deposited and that escalation bonus never applies; frost glaze "
                  + "already on a saved map is unaffected either way.");

                list.Gap();
                list.CheckboxLabeled("The Chill: drowned aurora floor light", ref chillDrownedAuroraEnabled,
                    "Shipped default: ON. The seabed's ambient light rises and falls with whichever "
                  + "aurora is active on the surface far above — a slow violet-teal glow that "
                  + "ripples, never a fixed brightness. Off: the seabed loses this layer entirely "
                  + "(whatever baseline light it would otherwise have is unaffected, never darkened "
                  + "further); Fuselight and Ghostpane's own steady point-glow is unaffected either "
                  + "way, so the floor never goes fully black from toggling this off.");
            }

            list.End();
        }
    }

    public class RM_DivingInteractionMod : Mod
    {
        public static RM_DivingSettings settings;

        public RM_DivingInteractionMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_DivingSettings>();
            // CHILL_FIRE_BAN_1: the first Harmony patches this assembly has
            // ever needed (Patch_ChillFireBan.cs) — every other mechanism
            // here rides a vanilla extension point (ThingComp/MapComponent/
            // GenStep) and needs no patch, same rule PropaneLakeMechanics'
            // own csproj documents for its one Harmony patch.
            new Harmony("mandrake.rm.divinginteraction").PatchAll();
        }

        public override string SettingsCategory()
        {
            return "Deep Diving";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
