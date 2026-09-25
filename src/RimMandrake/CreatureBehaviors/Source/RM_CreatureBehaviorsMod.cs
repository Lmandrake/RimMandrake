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
    //   9. proximitySoundscapeEnabled — RM_MapComponent_ProximitySoundscape.
    //      Off: a tagged def stops contributing hum layers as the camera
    //      moves near it, and any playing layers end.
    //  10. chewAnchorsBehaviorEnabled — RM_JobGiver_ChewAnchors. Off: a
    //      beetle-like race built to chew anchors never seeks one out.
    //  11. frontCreepEnabled / frontCreepRateMultiplier —
    //      RM_MapComponent_FrontCreep. Off: a border map's advancing front
    //      freezes wherever it currently sits. The dial scales how much of
    //      each band actually spawns (never the advance interval or depth
    //      cap, which stay whatever the biome's own extension says).
    //  12. aquaticAmbushEnabled — RM_CompAquaticAmbusher / RM_JobDriver_
    //      LungeAttack (GREENTIDE_MECHANICS_2 M7). Off: a tagged pawn never
    //      goes invisible while submerged and never lunges — a hediff it
    //      already carries when this is toggled off is removed on the next
    //      check, so nothing stays invisible forever; the pawn hunts
    //      exactly like a normal vanilla predator from then on.
    //  13. woundLinkEnabled / woundLinkShareMultiplier — RM_CompWoundLink
    //      (ROT_HEALTH_SHARING_1). Off: a fresh wound on a tagged pawn never
    //      mirrors onto same-tag kin, and the victim keeps 100% of it — the
    //      dial scales only the SHARED fraction (never the severity gate or
    //      radius, which stay whatever the race's own extension says).
    //  14. kinMendingEnabled / kinMendingBoostMultiplier —
    //      RM_HediffComp_KinMending (ROT_HEALTH_SHARING_1). Off: kin nearby
    //      never speeds up a tagged pawn's own natural healing. The dial
    //      scales only the extra heal amount (never the kin-count threshold
    //      or radius, which stay whatever the race's own extension says).
    //  15. guardianAlarmEnabled — RM_CompPlantAlarm / RUT_Plant_FalseFruit
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
    //  16. grapplerHoldEnabled / grapplerCrushMultiplier — RM_Hediff_Grappled
    //      + RM_CompGrappler (DEEPS_FAUNA_MECHANICS_1, Grabber). Off: any
    //      active hold releases immediately, a fresh pincer hit never starts
    //      a new one, no crush damage is dealt and hurting the grabber no
    //      longer rolls to break a hold (there is none). The dial scales the
    //      per-round crush damage and the hold's tightening rate together
    //      (never the escape chance, rescue chance, round interval or
    //      release radius, which stay whatever the defs say).
    //  17. drinkerFluidSacsEnabled / drinkerPoisonMultiplier —
    //      RM_CompFluidSacs (DEEPS_FAUNA_MECHANICS_1, Drinker). Off: a bite
    //      never restores the drinker's hunger and never poisons it either
    //      — a bite is just a bite. The dial scales only the poison
    //      severity applied on a bad bite (0 = a bad bite is simply never
    //      fed, same as any other unwanted meal, never the hunger restored
    //      from a good one).
    //  18. soulchimePsychicStunEnabled — RM_CompProximityPsychicStun
    //      (DEEPS_FAUNA_MECHANICS_1, Soulchime). Off: nobody gets
    //      psychically stunned for standing too close, wild or tamed.
    //  19. soulchimeShardArmorEnabled / soulchimeShardArmorRateMultiplier —
    //      RM_CompShardArmor (DEEPS_FAUNA_MECHANICS_1, Soulchime). Off: its
    //      shard armor stops growing (never shrinks what's already grown).
    //  20. soulchimeTameSootheEnabled — RM_CompTameSootheAura
    //      (DEEPS_FAUNA_MECHANICS_1, Soulchime). Off: a tamed carrier stops
    //      handing out its soothing memory to nearby colonists.
    //  21. shadeGridEnabled — RM_MapComponent_ShadeGrid (DESERT_SHADE_GRID_
    //      KEYSTONE_1). Off: ShadeAt reports full sun everywhere and the map
    //      stops recomputing the grid at all — every consumer below degrades
    //      to its "no shade found" behaviour, never a stale or wrong read.
    //  22. shadeSeekingWanderEnabled — RM_JobGiver_WanderInShadeGrid. Off: a
    //      shade-wander-tagged animal's idle wandering stops steering toward
    //      shaded cells and falls through to ordinary vanilla wander.
    //  23. heatDrivenBurstEnabled / heatDrivenBurstDecayMultiplier —
    //      RM_HediffComp_ShadeDrivenSeverity (RM_HeatDrivenBurst). Off: the
    //      hediff's severity freezes wherever it currently sits (never
    //      climbs or decays) — a content mod's own trigger and stages decide
    //      what a frozen severity means. The dial scales the decay rate in
    //      both sun and shade together (never the stage thresholds or the
    //      stat offsets, which stay whatever the def says).
    //  24. drumLureEnabled / drumLureChanceMultiplier — RM_CompDrumLure
    //      (DRUM_LURE_PREDATOR_BUILD_1). Off: a lure predator drops any
    //      in-progress compulsion immediately (the victim keeps walking
    //      wherever it was already headed, it just stops being steered) and
    //      never starts a new one; any lingering submersion clears and the
    //      pawn hunts like a normal vanilla predator from then on. The dial
    //      scales only the per-scan appraisal chance (never the radius or
    //      ambush range, which stay whatever the race's own comp says).
    //  25. shadeStaggerEnabled / shadeStaggerGerminationMultiplier —
    //      RM_HediffComp_ShadeStagger (DESERT_STAGGERSEED_BUILD_1). Off: a
    //      creature carrying a corpse-dispersal brood still sickens and still
    //      dies on exactly the same schedule — this switch never touches the
    //      hediff's severity — it simply stops being steered toward shade on
    //      the way down, and nothing germinates at its corpse. The dial scales
    //      only the germination CHANCE (never the stagger, the search radius,
    //      the seedling count or the lethality, which stay whatever the def
    //      says); at 0 the dying still walk for the shadows and the plant
    //      simply never spreads that way.
    //  26. filterFeedingEnabled / filterFeedNutritionMultiplier —
    //      RM_JobGiver_FilterFeedTerrain + RM_JobDriver_FilterFeedTerrain
    //      (DESERT_SHADE_WHALE_FILTERFEED_1). Off: a terrain filter-feeder
    //      never strains the ground for a meal and falls straight through to
    //      ordinary vanilla eating, which its declared foodType still governs
    //      — so it gets hungrier and has to find real food, it never starves
    //      for want of a mechanic. The dial scales only how much one completed
    //      bout restores (never the bout duration, search radius or hunger
    //      threshold, which stay whatever the race's own extension says).
    //  27. dungSeedingEnabled / dungSeedingMultiplier — RM_CompDungSeeder
    //      (DESERT_SHADE_WHALE_FILTERFEED_1). Off: a carrier still drops no
    //      dung from this comp and fertilises nothing (its ordinary vanilla
    //      FilthRate is untouched and still dirties the ground). The dial
    //      scales the growth boost, the seedling count and the wildlife chance
    //      together; at 0 the dung still falls and simply seeds nothing. Never
    //      the shade gate or the radius, which stay whatever the def says.
    //  28. parentalEnrageEnabled — RM_CompParentalEnrage +
    //      RM_MentalState_ParentalEnrage (SHRUBLAND_GIANT_ENRAGE_1). Off: the
    //      young of a "giant with young" race stop being guarded — walking up
    //      to a calf rouses nothing, and the herd is exactly as dangerous as
    //      its stats say and no more. Never touches the adults' own stats,
    //      tools or manhunterOnDamageChance, which still answer for hurting
    //      one. A rage already running ends on its own timer; this switch
    //      only stops new ones starting.
    //  29. directedAssaultBehaviorEnabled — RM_JobGiver_DirectedAssault
    //      (THEY_MOD_REPLICATION_1). Off: a tagged race stops marching on the
    //      colony when nothing is in sight — it still fights back at whatever
    //      it happens to run into, it just never goes looking.
    //  30. seedPassageEnabled / seedPassageGerminationMultiplier —
    //      RM_HediffComp_SeedPassage (GREENTIDE_YEARNING_FRUIT_FILTH_1). Off:
    //      a digestive-accelerant hediff still digests fast and still ends on
    //      exactly the same schedule — this switch never touches the
    //      hediff's severity — it simply leaves no filth and germinates
    //      nothing when it ends. The dial scales only the germination CHANCE
    //      (never the filth drop, the search radius or the seedling count,
    //      which stay whatever the def says); at 0 the filth still falls and
    //      the plant simply never spreads that way.
    //  31. brineBatteryDischargeEnabled / brineBatteryDischargeMultiplier —
    //      RM_CompDefensiveDischarge (WASTELAND_BRINE_BATTERY_DISCHARGE_1,
    //      RUT_BrineBattery). Off: hurting a tagged pawn at close range never
    //      shocks the attacker back. The dial scales only the discharge
    //      strength (never the range or cooldown, which stay whatever the
    //      def says); at 0 a hit is simply never returned.
    //  32. ambientHeatPusherEnabled — RM_CompHeatPusherGated
    //      (WASTELAND_RADIOTHERMAL_SOLITARY_1). Off: a tagged pawn stops
    //      pushing ambient heat into whatever cell/room it currently
    //      occupies — a plain animal from then on, wild or tamed.
    //  33. speciesSpacingEnabled / speciesSpacingCookDamageMultiplier —
    //      RM_JobGiver_AvoidOwnKind + RM_CompHeatCook
    //      (WASTELAND_RADIOTHERMAL_SOLITARY_1). Off: a tagged pawn stops
    //      steering away from other members of its own kind and stops taking
    //      cook-damage for standing too close to one — exactly as sociable
    //      (or not) as any other animal. The dial scales only the cook-tick
    //      damage amount (never the avoid/cook radii or the check interval,
    //      which stay whatever the race's own extension says).
    //  34. reactionSourceSpawnEnabled / reactionSourceBudgetMultiplier —
    //      RM_CompReactionSource + RM_ReactionResponseRule_SpawnPawns
    //      (REACTION_MECHANISM_GENERALISE_1 step 1, GREENTIDE_WASP_SWARM_1)
    //      and, since step 2 (HOSTILE_MOBILE_PLANTS_1),
    //      RM_ReactionPropagationRule_SameKindWithinRadius +
    //      RM_ReactionResponseRule_ActivateSelf (a gallowroot). Off: a
    //      disturbed reaction source (a skerrel gall, a gallowroot, and any
    //      future consumer wired the same way) never builds a reaction event
    //      at all — nothing spawns and nothing wakes its own kind nearby,
    //      same as guardianAlarmEnabled for the shipped alarm. The dial
    //      scales the SHARED event budget only — the one total every
    //      propagation hop and every response spends from — never a
    //      response's own per-map population ceiling or a propagation rule's
    //      own radius/per-neighbour cost, which stay whatever that rule's own
    //      config says. 0 disables the whole family (spawning AND
    //      propagation) without touching the toggle, the same "a number is
    //      the experience" shape as breedRateMultiplier. No new setting is
    //      owed for the plant swarm specifically: it shares this exact dial
    //      because it shares the exact mechanism.
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
        public static bool proximitySoundscapeEnabled = true;
        public static bool chewAnchorsBehaviorEnabled = true;
        public static bool frontCreepEnabled = true;
        public static float frontCreepRateMultiplier = 1f;
        public static bool aquaticAmbushEnabled = true;
        public static bool woundLinkEnabled = true;
        public static float woundLinkShareMultiplier = 1f;
        public static bool kinMendingEnabled = true;
        public static float kinMendingBoostMultiplier = 1f;
        public static bool guardianAlarmEnabled = true;
        public static bool grapplerHoldEnabled = true;
        public static float grapplerCrushMultiplier = 1f;
        public static bool drinkerFluidSacsEnabled = true;
        public static float drinkerPoisonMultiplier = 1f;
        public static bool soulchimePsychicStunEnabled = true;
        public static bool soulchimeShardArmorEnabled = true;
        public static float soulchimeShardArmorRateMultiplier = 1f;
        public static bool soulchimeTameSootheEnabled = true;
        public static bool shadeGridEnabled = true;
        public static bool shadeSeekingWanderEnabled = true;
        public static bool heatDrivenBurstEnabled = true;
        public static float heatDrivenBurstDecayMultiplier = 1f;
        public static bool drumLureEnabled = true;
        public static float drumLureChanceMultiplier = 1f;
        public static bool shadeStaggerEnabled = true;
        public static float shadeStaggerGerminationMultiplier = 1f;
        public static bool filterFeedingEnabled = true;
        public static float filterFeedNutritionMultiplier = 1f;
        public static bool dungSeedingEnabled = true;
        public static float dungSeedingMultiplier = 1f;
        public static bool parentalEnrageEnabled = true;
        public static bool directedAssaultBehaviorEnabled = true;
        public static bool seedPassageEnabled = true;
        public static float seedPassageGerminationMultiplier = 1f;
        public static bool brineBatteryDischargeEnabled = true;
        public static float brineBatteryDischargeMultiplier = 1f;
        public static bool ambientHeatPusherEnabled = true;
        public static bool speciesSpacingEnabled = true;
        public static float speciesSpacingCookDamageMultiplier = 1f;
        public static bool reactionSourceSpawnEnabled = true;
        public static float reactionSourceBudgetMultiplier = 1f;

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
            Scribe_Values.Look(ref proximitySoundscapeEnabled, "proximitySoundscapeEnabled", true);
            Scribe_Values.Look(ref chewAnchorsBehaviorEnabled, "chewAnchorsBehaviorEnabled", true);
            Scribe_Values.Look(ref frontCreepEnabled, "frontCreepEnabled", true);
            Scribe_Values.Look(ref frontCreepRateMultiplier, "frontCreepRateMultiplier", 1f);
            Scribe_Values.Look(ref aquaticAmbushEnabled, "aquaticAmbushEnabled", true);
            Scribe_Values.Look(ref woundLinkEnabled, "woundLinkEnabled", true);
            Scribe_Values.Look(ref woundLinkShareMultiplier, "woundLinkShareMultiplier", 1f);
            Scribe_Values.Look(ref kinMendingEnabled, "kinMendingEnabled", true);
            Scribe_Values.Look(ref kinMendingBoostMultiplier, "kinMendingBoostMultiplier", 1f);
            Scribe_Values.Look(ref guardianAlarmEnabled, "guardianAlarmEnabled", true);
            Scribe_Values.Look(ref grapplerHoldEnabled, "grapplerHoldEnabled", true);
            Scribe_Values.Look(ref grapplerCrushMultiplier, "grapplerCrushMultiplier", 1f);
            Scribe_Values.Look(ref drinkerFluidSacsEnabled, "drinkerFluidSacsEnabled", true);
            Scribe_Values.Look(ref drinkerPoisonMultiplier, "drinkerPoisonMultiplier", 1f);
            Scribe_Values.Look(ref soulchimePsychicStunEnabled, "soulchimePsychicStunEnabled", true);
            Scribe_Values.Look(ref soulchimeShardArmorEnabled, "soulchimeShardArmorEnabled", true);
            Scribe_Values.Look(ref soulchimeShardArmorRateMultiplier, "soulchimeShardArmorRateMultiplier", 1f);
            Scribe_Values.Look(ref soulchimeTameSootheEnabled, "soulchimeTameSootheEnabled", true);
            Scribe_Values.Look(ref shadeGridEnabled, "shadeGridEnabled", true);
            Scribe_Values.Look(ref shadeSeekingWanderEnabled, "shadeSeekingWanderEnabled", true);
            Scribe_Values.Look(ref heatDrivenBurstEnabled, "heatDrivenBurstEnabled", true);
            Scribe_Values.Look(ref heatDrivenBurstDecayMultiplier, "heatDrivenBurstDecayMultiplier", 1f);
            Scribe_Values.Look(ref drumLureEnabled, "drumLureEnabled", true);
            Scribe_Values.Look(ref drumLureChanceMultiplier, "drumLureChanceMultiplier", 1f);
            Scribe_Values.Look(ref shadeStaggerEnabled, "shadeStaggerEnabled", true);
            Scribe_Values.Look(ref shadeStaggerGerminationMultiplier, "shadeStaggerGerminationMultiplier", 1f);
            Scribe_Values.Look(ref filterFeedingEnabled, "filterFeedingEnabled", true);
            Scribe_Values.Look(ref filterFeedNutritionMultiplier, "filterFeedNutritionMultiplier", 1f);
            Scribe_Values.Look(ref dungSeedingEnabled, "dungSeedingEnabled", true);
            Scribe_Values.Look(ref dungSeedingMultiplier, "dungSeedingMultiplier", 1f);
            Scribe_Values.Look(ref parentalEnrageEnabled, "parentalEnrageEnabled", true);
            Scribe_Values.Look(ref directedAssaultBehaviorEnabled, "directedAssaultBehaviorEnabled", true);
            Scribe_Values.Look(ref seedPassageEnabled, "seedPassageEnabled", true);
            Scribe_Values.Look(ref seedPassageGerminationMultiplier, "seedPassageGerminationMultiplier", 1f);
            Scribe_Values.Look(ref brineBatteryDischargeEnabled, "brineBatteryDischargeEnabled", true);
            Scribe_Values.Look(ref brineBatteryDischargeMultiplier, "brineBatteryDischargeMultiplier", 1f);
            Scribe_Values.Look(ref ambientHeatPusherEnabled, "ambientHeatPusherEnabled", true);
            Scribe_Values.Look(ref speciesSpacingEnabled, "speciesSpacingEnabled", true);
            Scribe_Values.Look(ref speciesSpacingCookDamageMultiplier, "speciesSpacingCookDamageMultiplier", 1f);
            Scribe_Values.Look(ref reactionSourceSpawnEnabled, "reactionSourceSpawnEnabled", true);
            Scribe_Values.Look(ref reactionSourceBudgetMultiplier, "reactionSourceBudgetMultiplier", 1f);
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
            list.CheckboxLabeled("Proximity soundscapes", ref proximitySoundscapeEnabled,
                "A tagged plant or building stops adding its hum layer as the view moves near it "
              + "(the grove falls silent; nothing else changes).");
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
            list.GapLine();

            list.CheckboxLabeled("Grabber hold-and-crush", ref grapplerHoldEnabled,
                "On: a pawn caught in a grabber's pincer cannot move and takes crush damage every "
              + "few seconds; break the hold by hurting the grabber (each hit from someone else has "
              + "a chance to free them). Off: any hold releases immediately and a pincer hit is just a hit.");
            list.Label("Hold crush rate: " + grapplerCrushMultiplier.ToString("0.00") + "x");
            grapplerCrushMultiplier = list.Slider(grapplerCrushMultiplier, 0f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Drinker fluid sacs", ref drinkerFluidSacsEnabled,
                "On: a drinker's bite feeds it and fills its fluid sacs (more drained fluids from the carcass), "
              + "but warm iron blood poisons it and it dies within a day. Off: a bite is just a bite, and its "
              + "sacs never yield anything.");
            list.Label("Bad-blood poison severity: " + drinkerPoisonMultiplier.ToString("0.00") + "x");
            drinkerPoisonMultiplier = list.Slider(drinkerPoisonMultiplier, 0f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Soulchime psychic stun", ref soulchimePsychicStunEnabled,
                "On: a Soulchime psychically stuns anyone not of its own faction who gets too close in its "
              + "line of sight, or who hurts it; psychically deaf pawns are immune. Off: nobody is ever stunned.");
            list.CheckboxLabeled("Soulchime shard armor", ref soulchimeShardArmorEnabled,
                "A Soulchime's shard armor stops growing (whatever it's already grown stays).");
            list.Label("Shard armor growth rate: " + soulchimeShardArmorRateMultiplier.ToString("0.00") + "x");
            soulchimeShardArmorRateMultiplier = list.Slider(soulchimeShardArmorRateMultiplier, 0f, 3f);
            list.CheckboxLabeled("Soulchime tamed soothing", ref soulchimeTameSootheEnabled,
                "A tamed Soulchime stops handing out its soothing calm to nearby colonists.");
            list.GapLine();

            list.CheckboxLabeled("Shade grid", ref shadeGridEnabled,
                "The per-cell shade grid stops computing entirely; every shade-reading behavior "
              + "below acts as if the whole map were in full sun.");
            list.CheckboxLabeled("Shade-seeking wander", ref shadeSeekingWanderEnabled,
                "A shade-wander-tagged animal stops steering its idle wandering toward shaded cells.");
            list.CheckboxLabeled("Heat-driven burst/retreat hediff", ref heatDrivenBurstEnabled,
                "A heat-driven-burst hediff's severity stops climbing or decaying at all (frozen "
              + "wherever it currently sits).");
            list.Label("Heat-driven burst decay rate: " + heatDrivenBurstDecayMultiplier.ToString("0.00") + "x");
            heatDrivenBurstDecayMultiplier = list.Slider(heatDrivenBurstDecayMultiplier, 0.25f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Drum-lure ambush", ref drumLureEnabled,
                "A lure predator stops calling victims closer with a false vibration signal; any "
              + "victim already mid-compulsion is released immediately (they just keep walking "
              + "wherever they were headed) and the predator hunts like a normal vanilla predator "
              + "from then on.");
            list.Label("Drum-lure appraisal chance: " + drumLureChanceMultiplier.ToString("0.00") + "x");
            drumLureChanceMultiplier = list.Slider(drumLureChanceMultiplier, 0f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Corpse-dispersal seeding (stagger for shade)", ref shadeStaggerEnabled,
                "On: a creature dying of a seed-brood walks for the nearest shadow while it still "
              + "can, and the plant grows from wherever the body falls. Off: it dies exactly as fast "
              + "and exactly as surely, it just dies where it happens to be standing and leaves "
              + "nothing growing behind it. This never changes how deadly the fruit is.");
            list.Label("Corpse germination chance: " + shadeStaggerGerminationMultiplier.ToString("0.00") + "x");
            shadeStaggerGerminationMultiplier = list.Slider(shadeStaggerGerminationMultiplier, 0f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Filter-feeding from the ground", ref filterFeedingEnabled,
                "On: an animal built to strain its food out of the ground (sand, silt) stops on "
              + "terrain it can feed from and eats there, with no plant or food item involved. "
              + "Off: it never does, and simply eats like any other animal of its diet — hungrier, "
              + "but never stuck.");
            list.Label("Filter-feed meal size: " + filterFeedNutritionMultiplier.ToString("0.00") + "x");
            filterFeedNutritionMultiplier = list.Slider(filterFeedNutritionMultiplier, 0.25f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Dung seeding at shade patches", ref dungSeedingEnabled,
                "On: a big grazer resting in shade leaves dung that fertilises the plants around "
              + "it, sprouts young ones, and now and then brings a small creature with it — the "
              + "way seeds and passengers travel between patches that are otherwise cut off from "
              + "each other. Dung dropped out in the open fertilises nothing. Off: it leaves "
              + "nothing behind and nothing grows from it.");
            list.Label("Dung seeding strength: " + dungSeedingMultiplier.ToString("0.00") + "x");
            dungSeedingMultiplier = list.Slider(dungSeedingMultiplier, 0f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Giants defend their young", ref parentalEnrageEnabled,
                "On: getting close to the calf of a giant-with-young animal makes the nearest "
              + "adult charge you, with no warning at all. It goes after whoever came close and "
              + "nobody else, and it calms down again once you back off. Off: their young are "
              + "not guarded, and you can walk right up to one.");
            list.GapLine();

            list.CheckboxLabeled("Directed assault (march on the colony)", ref directedAssaultBehaviorEnabled,
                "On: a tagged animal that has nothing to fight marches toward the colony instead of "
              + "idling at the map edge. Off: it still fights back at whatever it happens to run into, "
              + "it just never goes looking.");
            list.GapLine();

            list.CheckboxLabeled("Seed passage (filth + germination)", ref seedPassageEnabled,
                "On: when a digestive-accelerant hediff runs its course, the carrier leaves filth "
              + "behind and may germinate a seedling nearby — free calories with a tax, and the tax "
              + "is the ground sprouting. Off: the hediff still digests just as fast and ends on the "
              + "same schedule, it just leaves nothing behind.");
            list.Label("Seed passage germination chance: " + seedPassageGerminationMultiplier.ToString("0.00") + "x");
            seedPassageGerminationMultiplier = list.Slider(seedPassageGerminationMultiplier, 0f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Brine battery defensive discharge", ref brineBatteryDischargeEnabled,
                "On: hurting a brine battery at close range shocks the attacker back (a stun, not a "
              + "wound). Off: a hit is simply never returned.");
            list.Label("Discharge strength: " + brineBatteryDischargeMultiplier.ToString("0.00") + "x");
            brineBatteryDischargeMultiplier = list.Slider(brineBatteryDischargeMultiplier, 0f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Ambient heat pushing", ref ambientHeatPusherEnabled,
                "A tagged animal stops pushing ambient heat into whatever cell or room it currently "
              + "occupies, wild or tamed.");
            list.CheckboxLabeled("Species-spacing law", ref speciesSpacingEnabled,
                "On: a tagged animal steers away from other members of its own kind, and takes heat "
              + "damage every so often if it fails to keep even that much distance. Off: it neither "
              + "avoids nor cooks its own kind, same as any other animal.");
            list.Label("Cook-damage rate: " + speciesSpacingCookDamageMultiplier.ToString("0.00") + "x");
            speciesSpacingCookDamageMultiplier = list.Slider(speciesSpacingCookDamageMultiplier, 0f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Reaction sources (hive/gall spawn, plant swarm)", ref reactionSourceSpawnEnabled,
                "On: disturbing a reaction source (a skerrel gall, a gallowroot, and any future consumer "
              + "wired the same way) spawns a bounded batch of hostile creatures nearby and/or wakes its "
              + "own kind within range. Off: disturbing it does nothing at all — no spawn, no swarm, no "
              + "budget spent.");
            list.Label("Reaction spawn budget: " + reactionSourceBudgetMultiplier.ToString("0.00") + "x");
            reactionSourceBudgetMultiplier = list.Slider(reactionSourceBudgetMultiplier, 0f, 3f);

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
