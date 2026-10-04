using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Sarlacc
{
    // ════════════════════════════════════════════════════════════════════
    // SARLACC_HABITAT_BUILD_1 — Mod Settings, per CLAUDE.md's standing rule
    // ("Every mod ships superb Mod Settings") and the draft's own §8 ruling
    // ("Mod Settings per MOD_OPTIONS_RETROFIT_1 (feature toggles incl.
    // rooting-in-play, changed-return hediffs, breach consequences)").
    //
    // STATIC fields, read from comps that have no Mod instance handy — same
    // shape as RSW_JawaIonWeaponsSettings (src/RimStarWars/JawaIonWeapons).
    //
    // ALL-OFF DEGRADES GRACEFULLY: with rootingInPlayEnabled off, a swimmer
    // just never roots (an ordinary, if unusual, wild predator forever). With
    // anchoredTitheEnabled off, an anchored sarlacc is inert scenery. With
    // changedReturnHediffsEnabled off, swallow-and-survive works exactly as
    // vanilla CompDevourer already does, with no hediff granted. Nothing NREs
    // and no def fails to resolve with every toggle off.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_SarlaccSettings : ModSettings
    {
        /// <summary>Fork 1: a swimmer that finds a seep or runs dry anchors visibly on the map.</summary>
        public static bool rootingInPlayEnabled = true;

        /// <summary>Multiplier on how fast a swimmer's water reserve drains (lower = swimmers live longer before rooting).</summary>
        public static float reserveDrainMultiplier = 1f;

        /// <summary>Show a message when a swimmer roots.</summary>
        public static bool rootingMessagesEnabled = true;

        /// <summary>Stage II: the anchored sarlacc's rare mouth-strike ("it strikes rarely, and only to tithe").</summary>
        public static bool anchoredTitheEnabled = true;

        /// <summary>Grant one of the seven changed-return hediffs (draft §4.5) to a pawn that survives being swallowed.</summary>
        public static bool changedReturnHediffsEnabled = true;

        /// <summary>Chance a survivor is granted a SECOND hediff on top of the first ("usually one, sometimes two").</summary>
        public static float secondHediffChance = 0.2f;

        /// <summary>Stage III: the breach flood's real (DBH-thirst-fillable, self-reverting)
        /// water terrain around a breached cistern. See MapComponent_SarlaccBreachFlood.</summary>
        public static bool breachFloodVisualEnabled = true;

        /// <summary>LONGSHADE_BEDAZZLE_MECHANICS_1 part 3 (tranche 1): every swallow leaves a
        /// readable sign — a disturbed patch of sand where the prey went under, and a
        /// message naming what was taken (vanilla already messages for the player's own).</summary>
        public static bool takeSignsEnabled = true;

        /// <summary>LONGSHADE_BEDAZZLE_MECHANICS_1 tranche 2, the swimmer's road: the
        /// once-per-map incident (Long Shade maps) in which one young swimmer swims rim
        /// to rim toward the biggest dew ring and roots there. Needs Creature Behaviors'
        /// shade-patch graph.</summary>
        public static bool swimmerRoadEnabled = true;

        /// <summary>When a road swimmer roots, every wild animal sheltering in that
        /// patch of shade breaks from it at once.</summary>
        public static bool rootingEvacuatesPatch = true;

        /// <summary>The road/seep swimmer's under-sand grinding (vanilla FleshbeastDigging) while it moves.</summary>
        public static bool swimmerGrindSoundEnabled = true;

        /// <summary>STILLSAND_EVENT_CREATURES_REMAINDER_1: the once-per-map incident (Stillsand maps)
        /// in which one swimmer swims for the largest buried seep and roots there.</summary>
        public static bool swimmerSeepEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref rootingInPlayEnabled, "rootingInPlayEnabled", true);
            Scribe_Values.Look(ref reserveDrainMultiplier, "reserveDrainMultiplier", 1f);
            Scribe_Values.Look(ref rootingMessagesEnabled, "rootingMessagesEnabled", true);
            Scribe_Values.Look(ref anchoredTitheEnabled, "anchoredTitheEnabled", true);
            Scribe_Values.Look(ref changedReturnHediffsEnabled, "changedReturnHediffsEnabled", true);
            Scribe_Values.Look(ref secondHediffChance, "secondHediffChance", 0.2f);
            Scribe_Values.Look(ref breachFloodVisualEnabled, "breachFloodVisualEnabled", true);
            Scribe_Values.Look(ref takeSignsEnabled, "takeSignsEnabled", true);
            Scribe_Values.Look(ref swimmerRoadEnabled, "swimmerRoadEnabled", true);
            Scribe_Values.Look(ref rootingEvacuatesPatch, "rootingEvacuatesPatch", true);
            Scribe_Values.Look(ref swimmerGrindSoundEnabled, "swimmerGrindSoundEnabled", true);
            Scribe_Values.Look(ref swimmerSeepEnabled, "swimmerSeepEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Stage I to II — rooting in play");
            list.CheckboxLabeled("Swimmers root in play", ref rootingInPlayEnabled,
                "A sarlacc swimmer that finds a buried seep, or spends its whole birth-water "
              + "reserve, anchors on the spot and becomes Stage II (the anchored sarlacc). Off: "
              + "swimmers never root and behave as an ordinary wild predator forever.");
            list.Label("Reserve drain speed: " + reserveDrainMultiplier.ToString("0.00") + "x");
            list.Label("Higher means swimmers root sooner; lower lets them roam longer before "
              + "running dry.");
            reserveDrainMultiplier = list.Slider(reserveDrainMultiplier, 0.25f, 4f);
            list.CheckboxLabeled("Announce rooting", ref rootingMessagesEnabled,
                "Show a message the moment a swimmer roots.");
            list.GapLine();

            list.Label("Stage II — the anchored sarlacc's tithe");
            list.CheckboxLabeled("Anchored sarlaccs strike", ref anchoredTitheEnabled,
                "An anchored sarlacc rarely strikes whatever stands beside its mouth. Off: it is "
              + "inert scenery.");
            list.GapLine();

            list.CheckboxLabeled("Swallows leave a sign", ref takeSignsEnabled,
                "When a swimmer swallows anything, the sand where it went under is left churned "
              + "and a message names what was taken, so nothing on the map simply vanishes. Off: "
              + "only your own colonists' and animals' swallows are announced (the base game's "
              + "own message), and wild prey goes under without a trace until it is spat out.");
            list.GapLine();

            list.Label("The swimmer's road (Long Shade)");
            list.CheckboxLabeled("Swimmer's road incident", ref swimmerRoadEnabled,
                "Once per map, ever, on a Long Shade map: one young swimmer comes up at the map edge "
              + "and swims shade to shade toward the biggest dew ring on soft ground, usually your "
              + "walls, leaping at whatever stands on a dew line it passes. If it gets there it roots "
              + "for good. Needs Creature Behaviors (its shade-patch graph and sun heat). Off: the "
              + "incident never fires, and a swimmer already on the road wanders like any other.");
            list.CheckboxLabeled("Rooting empties the patch", ref rootingEvacuatesPatch,
                "When the road swimmer roots, every wild animal sheltering in that shade breaks from "
              + "it at once. Off: they stay until the mouth takes one.");
            list.CheckboxLabeled("Swimmer grinds under the sand", ref swimmerGrindSoundEnabled,
                "While the road or seep swimmer is moving you hear it grinding under the sand. Off: it "
              + "moves silently. Sound only; no effect on play.");
            list.GapLine();

            list.Label("The swimmer comes to root (Stillsand)");
            list.CheckboxLabeled("Seep-rooting incident", ref swimmerSeepEnabled,
                "Once per map, ever, on a Stillsand map with a sarlacc seep: one swimmer comes up at the map "
              + "edge and swims for the largest buried seep, then roots over it for good. Needs no other mod. "
              + "Off: the incident never fires, and a swimmer already on its way wanders like any other.");
            list.GapLine();

            list.Label("Changed on return");
            list.CheckboxLabeled("Grant changed-return hediffs", ref changedReturnHediffsEnabled,
                "A pawn who is swallowed by a sarlacc and survives to be spat free is permanently "
              + "changed by it (one of seven effects). Off: swallow-and-survive works exactly as "
              + "the underlying swallow mechanic already does, with no lasting effect.");
            list.Label("Chance of a second effect: " + (secondHediffChance * 100f).ToString("0") + "%");
            secondHediffChance = list.Slider(secondHediffChance, 0f, 1f);
            list.GapLine();

            list.Label("Stage III — breaching a cistern");
            list.CheckboxLabeled("Flood the surface on breach", ref breachFloodVisualEnabled,
                "Breaching a cistern turns the surrounding sand into real shallow water for a few "
              + "days — a genuine, drinkable source while it lasts, then dry again. Off: the "
              + "breach still ends the cistern, without the flood.");

            list.End();
        }
    }

    public class RSW_SarlaccMod : Mod
    {
        public static RSW_SarlaccSettings settings;

        public RSW_SarlaccMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_SarlaccSettings>();
        }

        public override string SettingsCategory()
        {
            return "Sarlacc — Native Habitat";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
