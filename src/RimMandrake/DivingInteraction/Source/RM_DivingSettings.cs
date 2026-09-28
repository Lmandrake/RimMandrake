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

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref requireGravEngine, "requireGravEngine", true);
            Scribe_Values.Look(ref greyPoolDefenceEnabled, "greyPoolDefenceEnabled", true);
            Scribe_Values.Look(ref greyPoolSentinelEnabled, "greyPoolSentinelEnabled", true);
            Scribe_Values.Look(ref greyElderDischargeEnabled, "greyElderDischargeEnabled", true);
            Scribe_Values.Look(ref greyElderTradeEnabled, "greyElderTradeEnabled", true);
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
