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
    //   8. senseWebEnabled — RM_MapComponent_SenseWeb. Off: registered web
    //      nodes still track (cheap bookkeeping), but the map stops scanning
    //      for and marking intruding pawns.
    //   9. chewAnchorsBehaviorEnabled — RM_JobGiver_ChewAnchors. Off: a
    //      beetle-like race built to chew anchors never seeks one out.
    //  10. frontCreepEnabled / frontCreepRateMultiplier —
    //      RM_MapComponent_FrontCreep. Off: a border map's advancing front
    //      freezes wherever it currently sits. The dial scales how much of
    //      each band actually spawns (never the advance interval or depth
    //      cap, which stay whatever the biome's own extension says).
    //  11. aquaticAmbushEnabled — RM_CompAquaticAmbusher / RM_JobDriver_
    //      LungeAttack (GREENTIDE_MECHANICS_2 M7). Off: a tagged pawn never
    //      goes invisible while submerged and never lunges — a hediff it
    //      already carries when this is toggled off is removed on the next
    //      check, so nothing stays invisible forever; the pawn hunts
    //      exactly like a normal vanilla predator from then on.
    //  12. woundLinkEnabled / woundLinkShareMultiplier — RM_CompWoundLink
    //      (ROT_HEALTH_SHARING_1). Off: a fresh wound on a tagged pawn never
    //      mirrors onto same-tag kin, and the victim keeps 100% of it — the
    //      dial scales only the SHARED fraction (never the severity gate or
    //      radius, which stay whatever the race's own extension says).
    //  13. kinMendingEnabled / kinMendingBoostMultiplier —
    //      RM_HediffComp_KinMending (ROT_HEALTH_SHARING_1). Off: kin nearby
    //      never speeds up a tagged pawn's own natural healing. The dial
    //      scales only the extra heal amount (never the kin-count threshold
    //      or radius, which stay whatever the race's own extension says).
    //  14. guardianAlarmEnabled — RM_CompPlantAlarm / RUT_Plant_FalseFruit
    //      (ROT_GUARDIAN_GROVES_1, RimUtinni RotSporeKit). Off: a guardian
    //      plant's network alarm never wakes nearby tagged fauna and
    //      harvesting the false-fruit lure never grips the harvester's
    //      ankle — the Rot's tea sources become plain, undefended
    //      harvestables. Card 6 RULED 2026-09-17: this is deliberately
    //      framed as a CONFESSION in its own label, not a neutral
    //      accessibility switch — turning the grove's guardians off is the
    //      player's own conscience talking, not just an easier game. The
    //      spore-gas guardian pattern (RUT_AgelessCap) is a separate,
    //      pre-existing switch — RM_EnvironmentalHazardsSettings'
    //      "Gas emitters"/"Gas damage and transmuting" toggles, which
    //      already cover it kit-wide.
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
        public static bool senseWebEnabled = true;
        public static bool chewAnchorsBehaviorEnabled = true;
        public static bool frontCreepEnabled = true;
        public static float frontCreepRateMultiplier = 1f;
        public static bool aquaticAmbushEnabled = true;
        public static bool woundLinkEnabled = true;
        public static float woundLinkShareMultiplier = 1f;
        public static bool kinMendingEnabled = true;
        public static float kinMendingBoostMultiplier = 1f;
        public static bool guardianAlarmEnabled = true;

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
            Scribe_Values.Look(ref senseWebEnabled, "senseWebEnabled", true);
            Scribe_Values.Look(ref chewAnchorsBehaviorEnabled, "chewAnchorsBehaviorEnabled", true);
            Scribe_Values.Look(ref frontCreepEnabled, "frontCreepEnabled", true);
            Scribe_Values.Look(ref frontCreepRateMultiplier, "frontCreepRateMultiplier", 1f);
            Scribe_Values.Look(ref aquaticAmbushEnabled, "aquaticAmbushEnabled", true);
            Scribe_Values.Look(ref woundLinkEnabled, "woundLinkEnabled", true);
            Scribe_Values.Look(ref woundLinkShareMultiplier, "woundLinkShareMultiplier", 1f);
            Scribe_Values.Look(ref kinMendingEnabled, "kinMendingEnabled", true);
            Scribe_Values.Look(ref kinMendingBoostMultiplier, "kinMendingBoostMultiplier", 1f);
            Scribe_Values.Look(ref guardianAlarmEnabled, "guardianAlarmEnabled", true);
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
            list.GapLine();

            list.CheckboxLabeled("Web-sense network", ref senseWebEnabled,
                "A registered web/anchor/gutter network stops sensing and marking intruders "
              + "(nodes still track, but nothing gets felt).");
            list.CheckboxLabeled("Anchor-chewing behavior", ref chewAnchorsBehaviorEnabled,
                "A beetle-like animal stops seeking out web anchors to chew through.");
            list.CheckboxLabeled("Border margin creep", ref frontCreepEnabled,
                "A map bordering a creeping biome stops advancing that biome's web/anchor/gutter line inward.");
            list.Label("Margin creep density: " + frontCreepRateMultiplier.ToString("0.00") + "x");
            frontCreepRateMultiplier = list.Slider(frontCreepRateMultiplier, 0f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Aquatic ambush (submerge + lunge)", ref aquaticAmbushEnabled,
                "A tagged animal stops going invisible while submerged in deep water and stops "
              + "lunging at targets that come into range; any lingering invisibility clears "
              + "immediately, and the animal hunts like a normal predator from then on.");
            list.GapLine();

            list.CheckboxLabeled("Wound sharing", ref woundLinkEnabled,
                "A serious fresh wound on a tagged animal stops partly mirroring onto same-tag "
              + "kin nearby; the original victim keeps the full wound instead.");
            list.Label("Wound-sharing amount: " + woundLinkShareMultiplier.ToString("0.00") + "x");
            woundLinkShareMultiplier = list.Slider(woundLinkShareMultiplier, 0f, 2f);
            list.CheckboxLabeled("Kin mending", ref kinMendingEnabled,
                "A tagged animal stops healing its own wounds faster just because same-tag kin "
              + "are nearby.");
            list.Label("Kin-mending boost: " + kinMendingBoostMultiplier.ToString("0.00") + "x");
            kinMendingBoostMultiplier = list.Slider(kinMendingBoostMultiplier, 0f, 2f);
            list.GapLine();

            list.CheckboxLabeled("Guardian defenses (unchecking this is you deciding the grove's "
              + "own law doesn't apply to you)",
                ref guardianAlarmEnabled,
                "Unchecked: you have chosen to strip the Rot's tea sources of what protects them, "
              + "for your own convenience. The network alarm stops waking nearby guardians and a "
              + "false-fruit lure stops gripping the hand that picks it — the grove simply lets "
              + "you take what it would otherwise defend. Not a neutral accessibility setting: "
              + "it is your own conscience being asked, every time you open this menu.");

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
