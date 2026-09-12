using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Creature Behaviors.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // Like EnvironmentalHazards, this assembly is a generic BEHAVIOR KIT:
    // every JobGiver/comp/hediff here reads a DefModExtension off the
    // pawn's race and no-ops instantly for any race that doesn't carry one
    // — this assembly names no race of its own. A master switch per
    // mechanism plus the two rate dials below cover the whole surface.
    //
    //   1. verminBreedingEnabled / breedRateMultiplier — RM_CompVerminBreeder.
    //      Off: a breeder-carrying pawn never spawns offspring. The rate
    //      dial scales how OFTEN it fires (never the population caps, which
    //      stay whatever the race's own extension says).
    //   2. gnawBehaviorEnabled — RM_JobGiver_GnawTargets /
    //      RM_JobDriver_Gnaw. Off: a race built to gnaw buildings/floors
    //      never seeks or starts that job.
    //   3. eatCleanableBehaviorEnabled — RM_ThinkNode_EatCleanable /
    //      RM_JobDriver_EatCleanable. Off: a race built to forage named
    //      items/filth never seeks or starts that job.
    //   4. seekShadeBehaviorEnabled — RM_JobGiver_SeekShade. Off: a race
    //      built to duck under roof in the heat never does.
    //   5. seekMarkedTerrainBehaviorEnabled — RM_JobGiver_SeekMarkedTerrain.
    //      Off: a race built to walk toward tagged terrain never does.
    //   6. silenceCueEnabled — RM_MapComponent_SilenceCue. Off: a predator
    //      hunt never hushes the map's ambient sound (a hush already in
    //      progress still ends normally rather than getting stuck on).
    //   7. sunScaldEnabled / sunScaldSeverityMultiplier — RM_Hediff_SunScald.
    //      Off: the hediff stops climbing or decaying at all (frozen in
    //      place, never removed — a content mod's own stages decide what a
    //      frozen severity means). The dial scales both the climb and the
    //      decay rate together.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CreatureBehaviorsSettings : ModSettings
    {
        public static bool verminBreedingEnabled = true;
        public static float breedRateMultiplier = 1f;
        public static bool gnawBehaviorEnabled = true;
        public static bool eatCleanableBehaviorEnabled = true;
        public static bool seekShadeBehaviorEnabled = true;
        public static bool seekMarkedTerrainBehaviorEnabled = true;
        public static bool silenceCueEnabled = true;
        public static bool sunScaldEnabled = true;
        public static float sunScaldSeverityMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref verminBreedingEnabled, "verminBreedingEnabled", true);
            Scribe_Values.Look(ref breedRateMultiplier, "breedRateMultiplier", 1f);
            Scribe_Values.Look(ref gnawBehaviorEnabled, "gnawBehaviorEnabled", true);
            Scribe_Values.Look(ref eatCleanableBehaviorEnabled, "eatCleanableBehaviorEnabled", true);
            Scribe_Values.Look(ref seekShadeBehaviorEnabled, "seekShadeBehaviorEnabled", true);
            Scribe_Values.Look(ref seekMarkedTerrainBehaviorEnabled, "seekMarkedTerrainBehaviorEnabled", true);
            Scribe_Values.Look(ref silenceCueEnabled, "silenceCueEnabled", true);
            Scribe_Values.Look(ref sunScaldEnabled, "sunScaldEnabled", true);
            Scribe_Values.Look(ref sunScaldSeverityMultiplier, "sunScaldSeverityMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("This is a toolkit other creatures use for behavior. Turning a piece "
                     + "off only matters for a race that actually uses it.");
            list.GapLine();

            list.CheckboxLabeled("Vermin breeding", ref verminBreedingEnabled,
                "A breeder-tagged animal stops spawning offspring near itself.");
            list.Label("Breeding rate: " + breedRateMultiplier.ToString("0.00") + "x");
            breedRateMultiplier = list.Slider(breedRateMultiplier, 0.25f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Gnawing behavior", ref gnawBehaviorEnabled,
                "A gnaw-tagged animal stops seeking out buildings or floors to chew.");
            list.CheckboxLabeled("Foraging/eating cleanable items", ref eatCleanableBehaviorEnabled,
                "A tagged animal stops seeking out named items or filth to eat.");
            list.CheckboxLabeled("Seeking shade", ref seekShadeBehaviorEnabled,
                "A shade-seeking animal stops ducking under roof once it gets hot.");
            list.CheckboxLabeled("Seeking marked terrain", ref seekMarkedTerrainBehaviorEnabled,
                "A tagged animal stops walking toward terrain it's built to seek out.");
            list.CheckboxLabeled("Predator-hunt silence cue", ref silenceCueEnabled,
                "A tagged predator's hunt near a colonist stops hushing the map's ambient sound.");
            list.GapLine();

            list.CheckboxLabeled("Sun-scald buildup", ref sunScaldEnabled,
                "A sun-sensitive pawn's exposure severity stops rising in sun or falling in shade "
              + "(frozen wherever it currently sits).");
            list.Label("Sun-scald rate: " + sunScaldSeverityMultiplier.ToString("0.00") + "x");
            sunScaldSeverityMultiplier = list.Slider(sunScaldSeverityMultiplier, 0.25f, 3f);

            list.End();
        }
    }

    public class RM_CreatureBehaviorsMod : Mod
    {
        public static RM_CreatureBehaviorsSettings settings;

        public RM_CreatureBehaviorsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_CreatureBehaviorsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Creature Behaviors";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
