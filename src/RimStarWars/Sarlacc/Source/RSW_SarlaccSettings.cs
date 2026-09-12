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

        /// <summary>Stage III: the breach flood's cosmetic puddle radius around a breached cistern.</summary>
        public static bool breachFloodVisualEnabled = true;

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

            list.Label("Changed on return");
            list.CheckboxLabeled("Grant changed-return hediffs", ref changedReturnHediffsEnabled,
                "A pawn who is swallowed by a sarlacc and survives to be spat free is permanently "
              + "changed by it (one of seven effects). Off: swallow-and-survive works exactly as "
              + "the underlying swallow mechanic already does, with no lasting effect.");
            list.Label("Chance of a second effect: " + (secondHediffChance * 100f).ToString("0") + "%");
            secondHediffChance = list.Slider(secondHediffChance, 0f, 1f);
            list.GapLine();

            list.Label("Stage III — breaching a cistern");
            list.CheckboxLabeled("Show the breach flood puddle", ref breachFloodVisualEnabled,
                "Breaching a cistern leaves a temporary spread of water puddles at the surface. "
              + "Off: the breach still ends the cistern, without the cosmetic flood.");

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
