// MOD_OPTIONS_RETROFIT_1 — Mod Settings for the Long Hunger.
//
// House style: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs (static fields
// read from everywhere, Scribe_Values in ExposeData, DoWindowContents helper
// called from the Mod subclass).
//
// What is real here: a single quest-gated VAST creature (LongHungerThing) whose
// eruption/tremor/submerge numbers are hardcoded consts, fired by
// IncidentWorker_LongHungerSurfaces only from Quest_LongHunger.xml. Disabling the
// encounter does NOT fail the quest — the quest's own Delay/reward chain runs off
// its own timer signal (ContractDue), independent of whether the incident ever
// fires (see Quest_LongHunger.xml: QuestNode_CreateIncidents and QuestNode_Delay
// are parallel nodes, not sequenced on one another) — so "no encounter, contract
// still resolves" is a safe, graceful off-switch.
using RimWorld;
using UnityEngine;
using Verse;

namespace LongHunger
{
    public class LongHungerSettings : ModSettings
    {
        // Master switch for the creature itself. Off: the incident never spawns
        // RUT_LongHunger, but the quest's own contract fee still pays out on its
        // timer — nothing else in the quest depends on the encounter firing.
        public static bool encounterEnabled = true;

        // Scales EruptionDamage (90) and PulseDamage (45) together.
        public static float damageMultiplier = 1f;

        // Scales SurfacedDurationTicks (2500 = 1 in-game hour) and
        // PulseIntervalTicks (600 = 14 in-game minutes) together, so the pulse
        // cadence stays proportional to how long the creature stays surfaced.
        public static float durationMultiplier = 1f;

        // Scales the salvage value range (600-1400) dropped on submerging.
        public static float lootValueMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref encounterEnabled, "encounterEnabled", true);
            Scribe_Values.Look(ref damageMultiplier, "damageMultiplier", 1f);
            Scribe_Values.Look(ref durationMultiplier, "durationMultiplier", 1f);
            Scribe_Values.Look(ref lootValueMultiplier, "lootValueMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("The Long Hunger can surface", ref encounterEnabled,
                "Off: the quest's salvage contract still pays out on its timer, but the "
              + "creature never erupts onto your map. On by default.");
            list.Gap();

            list.Label("Damage: " + damageMultiplier.ToString("0.00") + "x");
            list.Label("Scales both the initial eruption (90 damage, radius 4.5) and each "
              + "tremor pulse (45 damage, radius 3) that follows.");
            damageMultiplier = list.Slider(damageMultiplier, 0.25f, 3f);
            list.Gap();

            list.Label("Surfaced duration: " + durationMultiplier.ToString("0.00") + "x");
            list.Label("Scales how long it stays up (default 1 in-game hour) and the gap "
              + "between tremor pulses (default 14 in-game minutes) together.");
            durationMultiplier = list.Slider(durationMultiplier, 0.25f, 3f);
            list.Gap();

            list.Label("Salvage value: " + lootValueMultiplier.ToString("0.00") + "x");
            list.Label("Scales the value of the loot dropped when it submerges "
              + "(default 600-1400 silver-equivalent).");
            lootValueMultiplier = list.Slider(lootValueMultiplier, 0f, 3f);

            list.End();
        }
    }

    public class LongHungerMod : Mod
    {
        public static LongHungerSettings settings;

        public LongHungerMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<LongHungerSettings>();
        }

        public override string SettingsCategory()
        {
            return "The Long Hunger";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
