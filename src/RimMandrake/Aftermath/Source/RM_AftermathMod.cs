using UnityEngine;
using Verse;

namespace RimMandrake.Aftermath
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Aftermath.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields
    // read from everywhere, Scribe_Values in ExposeData).
    //
    // What this mod actually DOES at runtime: MapComponent_BattleRecorder
    // opens/closes BattleRecords (battle tracking + the ChronicleEvents.Raise
    // "battle.closed" publish other mods, e.g. Ninefold, subscribe to) and
    // AftermathRuleRunner turns a closed battle / a nearby mental break / a
    // long-held prisoner into a QUEUED follow-up incident (a forced raid-like
    // payload) against a target faction, subject to discipline caps.
    //
    // GATING CHOICE: the master switch below turns off only the QUEUEING of
    // aftermath incidents (AftermathRuleRunner's three trigger entry points).
    // It deliberately does NOT stop MapComponent_BattleRecorder itself —
    // that recorder is also the sole source of the "battle.closed"
    // ChronicleEvent other mods (Ninefold's ChronicleSubscriber) depend on
    // for their own, unrelated mechanics; killing it would silently break
    // a different mod's feature. All-off for Aftermath's OWN mechanic still
    // degrades cleanly: OnBattleClosed/OnMentalBreakNearBattle/
    // OnPrisonerHeldTooLong become no-ops, nothing is queued, no NREs.
    // ════════════════════════════════════════════════════════════════════
    public class RM_AftermathSettings : ModSettings
    {
        // Master switch for AftermathRuleRunner's queued follow-up incidents.
        public static bool aftermathEnabled = true;

        // AftermathRuleRunner.PassesDiscipline's two shipped caps
        // (MaxPerFaction = 1, MaxTotal = 2 in the original hardcoded consts).
        public static int maxQueuedPerFaction = 1;
        public static int maxQueuedTotal = 2;

        // Rule 6's own window: "a mental break WITHIN 2 DAYS after a battle."
        public static float mentalBreakWindowDays = 2f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref aftermathEnabled, "aftermathEnabled", true);
            Scribe_Values.Look(ref maxQueuedPerFaction, "maxQueuedPerFaction", 1);
            Scribe_Values.Look(ref maxQueuedTotal, "maxQueuedTotal", 2);
            Scribe_Values.Look(ref mentalBreakWindowDays, "mentalBreakWindowDays", 2f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Battle aftermath enabled", ref aftermathEnabled,
                "After a battle ends badly, a colonist has a mental break near one, or a prisoner "
              + "is held too long, this can queue a follow-up raid-like event against the faction "
              + "involved. Off: nothing is ever queued — battles are still tracked for other mods, "
              + "but this mod's own follow-up events never fire.");
            list.GapLine();

            list.Label("Max queued follow-ups for the same faction at once: " + maxQueuedPerFaction);
            maxQueuedPerFaction = System.Convert.ToInt32(list.Slider(maxQueuedPerFaction, 1, 5));

            list.Label("Max queued follow-ups total, any faction: " + maxQueuedTotal);
            maxQueuedTotal = System.Convert.ToInt32(list.Slider(maxQueuedTotal, 1, 8));

            list.Label("Mental-break window after a battle: " + mentalBreakWindowDays.ToString("0.0") + " days");
            list.Label("A colonist mental break this soon after a battle closes can also count as an aftermath trigger.");
            mentalBreakWindowDays = list.Slider(mentalBreakWindowDays, 0.5f, 7f);

            list.End();
        }
    }

    public class RM_AftermathMod : Mod
    {
        public static RM_AftermathSettings settings;

        public RM_AftermathMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_AftermathSettings>();
        }

        public override string SettingsCategory()
        {
            return "Battle Aftermath";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
