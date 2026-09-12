using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.BrainWorms
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Geonosian Brain Worms.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields read
    // from everywhere, Scribe_Values in ExposeData, a DoWindowContents helper
    // called from the Mod subclass).
    //
    // Gates two of the three runtime infection vectors named in About.xml —
    // the salvaged-cargo incident and the weaponized-egg mortar shell. The
    // third vector (ruin dungeon egg clusters) is loot-table/def placement,
    // not a runtime mechanism this assembly can gate.
    //
    // 🔴 OWNER RULING, PERMANENT, VERBATIM: "Never corpse-walker. Too gross."
    // This file adds NO setting that could let a dead host be puppeted, and
    // does not touch the living-host refusal in CompRSWWormBurrow.IsValidHost
    // or the death guards in HediffComp_BrainWormPuppeteer. Whoever edits this
    // settings screen next: do not add one either.
    //
    // The cold-kill slider deliberately has no zero/off value (floor 0.25x) —
    // per the item spec, an on/off here would strand the intended "escape via
    // cold" design; only the RATE may be tuned, never disabled outright.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_BrainWormsSettings : ModSettings
    {
        public static bool cargoIncidentEnabled = true;
        public static bool eggProjectileEnabled = true;

        // 1.0 = shipped default (severityPerDay 0.14, ~2.5d latent + ~3d influenced).
        public static float progressionSpeedMultiplier = 1f;

        // 1.0 = shipped default (dies after ticksBelowBeforeDeath, ~1 hour below
        // freezing). Never allowed to reach "never dies" — see class comment.
        public static float coldKillRateMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref cargoIncidentEnabled, "cargoIncidentEnabled", true);
            Scribe_Values.Look(ref eggProjectileEnabled, "eggProjectileEnabled", true);
            Scribe_Values.Look(ref progressionSpeedMultiplier, "progressionSpeedMultiplier", 1f);
            Scribe_Values.Look(ref coldKillRateMultiplier, "coldKillRateMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Infection vectors");
            list.CheckboxLabeled("Salvaged cargo pod incident", ref cargoIncidentEnabled,
                "A crashed cargo pod incident can carry a hidden egg cluster. Off: this "
              + "incident never fires. The ruin dungeon egg clusters (a loot table, not "
              + "runtime code) are unaffected by any setting here.");
            list.CheckboxLabeled("Weaponized egg mortar shells spawn worms", ref eggProjectileEnabled,
                "A brain worm egg shell fired from a mortar bursts into loose worms on "
              + "impact. Off: the shell still exists and can still be loaded and fired — "
              + "it just lands inert, no worms.");
            list.GapLine();

            list.Label("Infection progression speed: " + progressionSpeedMultiplier.ToString("0.00") + "x");
            list.Label("Multiplies how fast a latent infection advances toward influenced "
              + "and then puppeted while the host stays warm. Does not change the cold cure.");
            progressionSpeedMultiplier = list.Slider(progressionSpeedMultiplier, 0.1f, 4f);
            list.Gap();

            list.Label("Cold-kill rate (loose worms and eggs): " + coldKillRateMultiplier.ToString("0.00") + "x");
            list.Label("Multiplies how fast a below-freezing worm or egg item dies of cold. "
              + "Floored above zero by design — cold is the intended way to deal with a "
              + "loose worm or a carried egg, and this mod will not let that be switched off.");
            coldKillRateMultiplier = list.Slider(coldKillRateMultiplier, 0.25f, 4f);

            list.End();
        }
    }

    public class RSW_BrainWormsMod : Mod
    {
        public static RSW_BrainWormsSettings settings;

        public RSW_BrainWormsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_BrainWormsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Geonosian Brain Worms";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
