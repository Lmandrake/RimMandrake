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
    //  34b. reactionDetectionEnabled — RM_CompReactionSource's proximity
    //      trigger (REACTION_MECHANISM_GENERALISE_1 step 3, the ant hive). Off:
    //      a sentry never rings on SIGHT, only when damaged.
    //  34c. reactionSuppressionEnabled / reactionSuppressionDurationMultiplier
    //      — RM_ReactionSuppression (step 5). Off: no zone is laid and every
    //      IsSuppressed reads false. The dial scales how long a zone lasts
    //      (never its radius, which the caller sets).
    //  34d. homeTetherEnabled — RM_CompHomeTether. Off: a tethered calm
    //      pawn wanders like any wild animal.
    //  35. adhesiveSlickEnabled / adhesiveSlickSeverityMultiplier —
    //      RM_CompAdhesiveSlick (WEBWORK_WEB_STRUCTURES_1, kit §3's deferred
    //      "commandable adhesive slick/locked" mechanism — v1). Off: a
    //      tagged structure's adhesive stops refreshing its slick hediff on
    //      anyone standing on/near it — a carried hediff still decays and
    //      still tends normally, it just never gets topped up again, same
    //      "degrades cleanly" posture as every other toggle here. The dial
    //      scales only the severity added per scan (never the hediff's own
    //      stage thresholds, decay rate or tend rate, which stay whatever
    //      RM_Webwork_Slick says); a structure also carrying CompFlickable
    //      is the player's own on/off command regardless of this setting.
    //  36. shadowFollowEnabled — RM_JobGiver_FollowShadowCaster
    //      (DESERT_GLITTER_BIRDS_COMMENSALS_1). Off: a shadow-follower-
    //      tagged commensal stops tracking the nearest shadow-caster host
    //      and falls through to ordinary vanilla wander — it never seeks
    //      the host out, but nothing stops it standing near one by chance.
    //      movingShadeEnabled — LONGSHADE_GPT_ENRICHMENT_1 §2: a host whose
    //      RM_CompProperties_ShadowCaster sets castShadeHeight (the gloomcast)
    //      casts real moving shade into the grid. Off: the layer is cleared and
    //      the host is a follow-only host again.
    //      heatSoundscapeEnabled / heatSoundscapeVolume — LONGSHADE_GPT_
    //      ENRICHMENT_1 §3 (RM_HeatSoundscape.cs): on a biome carrying
    //      RM_HeatSoundscapeExtension, a lit bed or a shade bed by the
    //      exposure at the CAMERA's cell. Off (or volume 0): no bed.
    //      creatureHeatSoundsEnabled — a herd animal's call at the rim before
    //      a dash, and a giant's far-carrying footfalls (RM_CompFootfalls).
    //      Off: both silent.
    //  37. pinnedSunEnabled / pinnedSunSkyStrength — RM_MapComponent_PinnedSun
    //      + RM_PinnedSunPatches (LONGSHADE_BEDAZZLE_MECHANICS_1 part 1, the
    //      golden hour). Only a biome carrying RM_PinnedSunExtension is
    //      affected. Off: the sky turns day-to-night like anywhere else and
    //      shadows swing with the real sun again (the live event expires on
    //      the next check). The dial scales how strongly the pinned sky paints
    //      over the weather's own; at 0 the colours are vanilla but the
    //      shadow vector stays pinned.
    //  38. falseShadeAmbushEnabled — RM_CompFalseShadeAmbusher +
    //      RM_MapComponent_FalseShade (LONGSHADE_BEDAZZLE_MECHANICS_1 part 2,
    //      the mirrak). Off: a false-shade ambusher never strikes and no
    //      longer reads as shade to shade-seekers — it is a slow, flat
    //      carrion-eater from then on.
    //  39. Sun heat (SOLAR_HEAT_EXPOSURE_1) — only a biome carrying
    //      RM_SunHeatExtension is affected; every other map is untouched.
    //      sunHeatEnabled (master) / sunHeatStrength — standing in the sun
    //      adds degrees to what a pawn feels, feeding vanilla comfort and
    //      Heatstroke. Off: no sun heat, no sun pathing, no bar anywhere.
    //      directionalShadeEnabled — shadows are cast along the sun vector
    //      (pinned sun, else the heat biome's own geometry). Off: the grid
    //      falls back to the old radius-2 ring round every caster.
    //      sunPathingEnabled / sunPathCostMultiplier — undrafted pawns
    //      route shade-to-shade. sunLoadBarEnabled — the inspect bar.
    //  40. Shade gear (SHADE_GEAR_FAMILY_1, RM_ShadeGear.cs) — one toggle
    //      per piece: parasolShadeEnabled / shadeTentEnabled /
    //      sunShieldEnabled. Off: that piece casts no shade into the grid
    //      and is ordinary gear (still craftable, still wearable/buildable).
    //  41. Shade hopping (SOLAR_HEAT_EXPOSURE_1 §5/§6, RM_ShadeHop.cs) —
    //      sun-heat maps only, and never where shade does not help (steam,
    //      volcanic). shadeHopEnabled — wild animals rest in shade, pause at
    //      its edge and sprint to the next patch instead of ambling in the
    //      sun. Off: they wander as vanilla does (sun pathing still applies).
    //      shadeHopRangeMultiplier — how far they will dash (the strictness
    //      dial). dashRingEnabled — the drafted-pawn "back to shade" ring.
    //  42. Sand swimming (STILLSAND_SAND_SWIM_KIT_1, RM_CompSandSwim.cs) — only a
    //      race carrying RM_SandSwimExtension. sandSwimEnabled — off: swimmers walk
    //      the surface like any animal (no submerge, no wake, no rumble).  sandSwim-
    //      DroidImmunity — off: a submerged swimmer will press an attack on a
    //      mechanoid or droid too. sandSwimRumbleVolume — the rumble slider.
    //  43. Sun from latitude (STILLSAND_SUN_FROM_LATITUDE_1) — only a biome
    //      whose RM_SunHeatExtension opts in. kindFromElevationEnabled — the
    //      cover that counts follows the sun angle (overhead above the
    //      biome's threshold, low sun below). Off: the biome's fixed heat
    //      kind. sandGlareEnabled / sandGlareStrength — open natural sand
    //      keeps a floor of exposure even in shade; paved floors do not glare.
    //      Off: shade on sand works as anywhere else. The heat-by-angle
    //      offset rides the existing sunHeatStrength dial.
    //  44. Glare-blind (STILLSAND_GLARE_BLIND_GOGGLES_1, RM_GlareBlind.cs) — only
    //      a biome whose RM_SunHeatExtension names a glareBlindHediff.
    //      glareBlindEnabled — off: nobody gains it; one already carried still
    //      decays away. glareBlindRateMultiplier — how fast full glare blinds.
    //      Immunity (a gene, or eye protection) is never a setting.
    //  45. The mirage (STILLSAND_MIRAGE_CONDITION_1, RM_Mirage.cs) — only a biome
    //      whose RM_SunHeatExtension names a mirageCondition, under a high sun.
    //      mirageEnabled — off: the condition ends on the next recompute, no
    //      shimmer band, no accuracy cut, no new "chasing the water" breaks (one
    //      already running ends on its own). mirageBreakChanceMultiplier — how
    //      often a heat-struck pawn breaks (0 = never; band and shimmer stay).
    //  46. Footprints (FOOTPRINT_TRACK_GRID_1, RM_MapComponent_TrackGrid) — only
    //      where a terrain or filth carries RM_TrackSurfaceExtension (the Warscar's
    //      settled film, the Stillsand's sand). tracksEnabled — THE performance
    //      switch: off, no step is recorded and the layer draws nothing (records
    //      already laid stay saved and reappear when it is turned back on).
    //      trackPoolCap — records kept per map (eviction: small animals first,
    //      then oldest; recent humanlike and large prints kept). trackPrintOpacity.
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
        public static bool sunScaldReadsShade = true;
        public static float sunScaldShadeThreshold = 0.5f;
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
        public static bool reactionDetectionEnabled = true;
        public static bool reactionSuppressionEnabled = true;
        public static float reactionSuppressionDurationMultiplier = 1f;
        public static bool homeTetherEnabled = true;
        public static bool adhesiveSlickEnabled = true;
        public static float adhesiveSlickSeverityMultiplier = 1f;
        // GREENTIDE_PLANT_SIGHT_BLOCK_ENGINE_1 (RM_SightBlockPatches). Defaults =
        // shipped behaviour: a grown blocker plant hides what is behind it from
        // sight AND from ranged fire, one plant deep.
        public static bool sightBlockEnabled = true;
        public static bool sightBlockRangedFire = true;
        public static int sightBlockCellsNeeded = 1;
        public static bool shadowFollowEnabled = true;
        public static bool movingShadeEnabled = true;
        public static bool heatSoundscapeEnabled = true;
        public static float heatSoundscapeVolume = 1f;
        public static bool creatureHeatSoundsEnabled = true;
        public static bool pinnedSunEnabled = true;
        public static float pinnedSunSkyStrength = 1f;
        public static bool falseShadeAmbushEnabled = true;
        public static bool sunHeatEnabled = true;
        public static float sunHeatStrength = 1f;
        public static bool directionalShadeEnabled = true;
        public static bool sunPathingEnabled = true;
        public static float sunPathCostMultiplier = 1f;
        public static bool sunLoadBarEnabled = true;
        public static bool parasolShadeEnabled = true;
        public static bool shadeTentEnabled = true;
        public static bool sunShieldEnabled = true;
        public static bool shadeHopEnabled = true;
        public static float shadeHopRangeMultiplier = 1f;
        public static bool dashRingEnabled = true;
        public static bool sandSwimEnabled = true;
        public static bool sandSwimDroidImmunity = true;
        public static float sandSwimRumbleVolume = 1f;
        public static bool kindFromElevationEnabled = true;
        public static bool sandGlareEnabled = true;
        public static float sandGlareStrength = 1f;
        public static bool glareBlindEnabled = true;
        public static float glareBlindRateMultiplier = 1f;
        public static bool mirageEnabled = true;
        public static float mirageBreakChanceMultiplier = 1f;
        public static bool tracksEnabled = true;
        public static int trackPoolCap = RM_TrackPool.DefaultCapacity;
        public static float trackPrintOpacity = 0.7f;

        private static Vector2 scrollPosition;
        private static float lastContentHeight = 2400f;

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
            Scribe_Values.Look(ref sunScaldReadsShade, "sunScaldReadsShade", true);
            Scribe_Values.Look(ref sunScaldShadeThreshold, "sunScaldShadeThreshold", 0.5f);
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
            Scribe_Values.Look(ref reactionDetectionEnabled, "reactionDetectionEnabled", true);
            Scribe_Values.Look(ref reactionSuppressionEnabled, "reactionSuppressionEnabled", true);
            Scribe_Values.Look(ref reactionSuppressionDurationMultiplier, "reactionSuppressionDurationMultiplier", 1f);
            Scribe_Values.Look(ref homeTetherEnabled, "homeTetherEnabled", true);
            Scribe_Values.Look(ref adhesiveSlickEnabled, "adhesiveSlickEnabled", true);
            Scribe_Values.Look(ref adhesiveSlickSeverityMultiplier, "adhesiveSlickSeverityMultiplier", 1f);
            Scribe_Values.Look(ref sightBlockEnabled, "sightBlockEnabled", true);
            Scribe_Values.Look(ref sightBlockRangedFire, "sightBlockRangedFire", true);
            Scribe_Values.Look(ref sightBlockCellsNeeded, "sightBlockCellsNeeded", 1);
            Scribe_Values.Look(ref shadowFollowEnabled, "shadowFollowEnabled", true);
            Scribe_Values.Look(ref movingShadeEnabled, "movingShadeEnabled", true);
            Scribe_Values.Look(ref heatSoundscapeEnabled, "heatSoundscapeEnabled", true);
            Scribe_Values.Look(ref heatSoundscapeVolume, "heatSoundscapeVolume", 1f);
            Scribe_Values.Look(ref creatureHeatSoundsEnabled, "creatureHeatSoundsEnabled", true);
            Scribe_Values.Look(ref pinnedSunEnabled, "pinnedSunEnabled", true);
            Scribe_Values.Look(ref pinnedSunSkyStrength, "pinnedSunSkyStrength", 1f);
            Scribe_Values.Look(ref falseShadeAmbushEnabled, "falseShadeAmbushEnabled", true);
            Scribe_Values.Look(ref sunHeatEnabled, "sunHeatEnabled", true);
            Scribe_Values.Look(ref sunHeatStrength, "sunHeatStrength", 1f);
            Scribe_Values.Look(ref directionalShadeEnabled, "directionalShadeEnabled", true);
            Scribe_Values.Look(ref sunPathingEnabled, "sunPathingEnabled", true);
            Scribe_Values.Look(ref sunPathCostMultiplier, "sunPathCostMultiplier", 1f);
            Scribe_Values.Look(ref sunLoadBarEnabled, "sunLoadBarEnabled", true);
            Scribe_Values.Look(ref parasolShadeEnabled, "parasolShadeEnabled", true);
            Scribe_Values.Look(ref shadeTentEnabled, "shadeTentEnabled", true);
            Scribe_Values.Look(ref sunShieldEnabled, "sunShieldEnabled", true);
            Scribe_Values.Look(ref shadeHopEnabled, "shadeHopEnabled", true);
            Scribe_Values.Look(ref shadeHopRangeMultiplier, "shadeHopRangeMultiplier", 1f);
            Scribe_Values.Look(ref dashRingEnabled, "dashRingEnabled", true);
            Scribe_Values.Look(ref sandSwimEnabled, "sandSwimEnabled", true);
            Scribe_Values.Look(ref sandSwimDroidImmunity, "sandSwimDroidImmunity", true);
            Scribe_Values.Look(ref sandSwimRumbleVolume, "sandSwimRumbleVolume", 1f);
            Scribe_Values.Look(ref kindFromElevationEnabled, "kindFromElevationEnabled", true);
            Scribe_Values.Look(ref sandGlareEnabled, "sandGlareEnabled", true);
            Scribe_Values.Look(ref sandGlareStrength, "sandGlareStrength", 1f);
            Scribe_Values.Look(ref glareBlindEnabled, "glareBlindEnabled", true);
            Scribe_Values.Look(ref glareBlindRateMultiplier, "glareBlindRateMultiplier", 1f);
            Scribe_Values.Look(ref mirageEnabled, "mirageEnabled", true);
            Scribe_Values.Look(ref mirageBreakChanceMultiplier, "mirageBreakChanceMultiplier", 1f);
            Scribe_Values.Look(ref tracksEnabled, "tracksEnabled", true);
            Scribe_Values.Look(ref trackPoolCap, "trackPoolCap", RM_TrackPool.DefaultCapacity);
            Scribe_Values.Look(ref trackPrintOpacity, "trackPrintOpacity", 0.7f);
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls: the screen outgrew one window height (38 mechanisms).
            Rect viewRect = new Rect(0f, 0f, inRect.width - 20f, Mathf.Max(lastContentHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPosition, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width };
            list.Begin(viewRect);

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
            list.CheckboxLabeled("Sun-scald reads tree shade", ref sunScaldReadsShade,
                "On a sun-heat map, trees, parasols and cast shade protect from sun-scald as well as roofs "
              + "(off: only a roof does, as in vanilla's own light-sensitivity).");
            list.Label("Sun-scald shade threshold: " + sunScaldShadeThreshold.ToString("0.00"));
            sunScaldShadeThreshold = list.Slider(sunScaldShadeThreshold, 0.1f, 1f);
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
            list.CheckboxLabeled("Hive sentries notice intruders", ref reactionDetectionEnabled,
                "On: a reaction source built to watch (an ant hive's sentries) rings its alarm when it "
              + "SEES an intruder nearby — a colonist, a tamed animal, a raider — and the hive rallies "
              + "after them. Off: it only rings when hurt, so you can walk a hive until you strike first.");
            list.CheckboxLabeled("Reaction suppression (stench smoke)", ref reactionSuppressionEnabled,
                "On: a suppressing counter-tool (the stench grenade) marks an area where no reaction "
              + "source rings, no alarm spreads, no responder answers, and swarming or rallied creatures "
              + "give up. Off: the smoke still does whatever else it does, but reactions ignore it.");
            list.Label("Suppression duration: " + reactionSuppressionDurationMultiplier.ToString("0.00") + "x");
            reactionSuppressionDurationMultiplier = list.Slider(reactionSuppressionDurationMultiplier, 0f, 3f);
            list.CheckboxLabeled("Hive residents stay home", ref homeTetherEnabled,
                "On: a calm creature tethered to a home (an ant hive's residents) drifts back when it "
              + "wanders too far, so a hive is still occupied when you find it. Off: they wander the "
              + "map like any wild animal.");
            list.GapLine();

            list.CheckboxLabeled("Adhesive slick surfaces", ref adhesiveSlickEnabled,
                "On: a tagged structure's adhesive keeps refreshing its slick hediff on anyone "
              + "standing on or near it, so lingering climbs from a slow-down toward a near-full "
              + "stick; a doctor's tend still frees them faster than waiting it out. Off: a hediff "
              + "already caught still decays and still tends normally, it just never tops back up.");
            list.Label("Adhesive slick strength: " + adhesiveSlickSeverityMultiplier.ToString("0.00") + "x");
            adhesiveSlickSeverityMultiplier = list.Slider(adhesiveSlickSeverityMultiplier, 0f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Sight-blocking plants", ref sightBlockEnabled,
                "On: a plant tagged as a sight blocker (the Greentide's brakkel, tumbel and the rest of "
              + "its understory), once grown, stops pawns seeing past it — they cannot target, witness "
              + "or notice what is on the other side. Pathing, fire, explosions and YOUR view of the map "
              + "are never affected. Off: those plants are ordinary cover again.");
            if (sightBlockEnabled)
            {
                list.CheckboxLabeled("  Also blocks ranged fire", ref sightBlockRangedFire,
                    "On: nobody can shoot at what the thicket hides (fights in dense jungle become close-"
                  + "quarters). Off: guns and turrets see through it; it still hides things from "
                  + "witnessing and from animals noticing you.");
                list.Label("  Thicket depth needed to hide something: " + sightBlockCellsNeeded
                    + (sightBlockCellsNeeded == 1 ? " plant" : " plants")
                    + " (higher = more of the jungle stays readable)");
                sightBlockCellsNeeded = Mathf.RoundToInt(list.Slider(sightBlockCellsNeeded, 1f, 4f));
                if (sightBlockCellsNeeded < 1) { sightBlockCellsNeeded = 1; }
            }
            list.GapLine();

            list.CheckboxLabeled("Shadow-following commensals", ref shadowFollowEnabled,
                "On: a tagged small commensal actively tracks and follows the nearest large "
              + "shadow-casting host creature, staying in its moving shadow. Off: it stops seeking "
              + "one out and just wanders normally — nothing stops it standing near a host by chance.");
            list.CheckboxLabeled("Giants cast moving shade", ref movingShadeEnabled,
                "On: a giant built to cast shade (the Long Shade's gloomcast) throws a real shadow that "
              + "moves with it. Anything looking for shade can shelter in it, and it cools whoever stands "
              + "in it like the shadow of a rock. Off: its shadow is only something its riders follow.");
            list.GapLine();

            list.CheckboxLabeled("Pinned sun (golden hour)", ref pinnedSunEnabled,
                "On: a biome built with a pinned sun (the Long Shade) keeps one fixed sunset sky "
              + "forever — no night — and every shadow on the map points the same way and never "
              + "moves. Off: the sky turns from day to night like anywhere else and shadows swing "
              + "with the real sun again.");
            list.Label("Golden-hour sky strength: " + pinnedSunSkyStrength.ToStringPercent());
            pinnedSunSkyStrength = list.Slider(pinnedSunSkyStrength, 0f, 1f);
            list.CheckboxLabeled("False-shade ambush (the mirrak)", ref falseShadeAmbushEnabled,
                "On: a flat ambusher lying in the open looks like shade to animals looking for "
              + "shade, and seizes whatever lies down in it. Off: it never strikes and nothing "
              + "mistakes it for shade — it just scavenges the dead.");
            list.GapLine();

            list.Label("Sun heat — only on biomes built with it (the Long Shade, the deep desert, "
                     + "and the steam and volcanic lands). Everywhere else nothing changes.");
            list.CheckboxLabeled("Sun heat", ref sunHeatEnabled,
                "On: standing in the open sun adds to the temperature a creature feels, so it gets hot, "
              + "then heatstroke, exactly as it would in a heat wave. Clothing, comfort range and "
              + "heatstroke work as normal. Smaller creatures heat faster. Off: none of the sun-heat "
              + "features below run.");
            if (sunHeatEnabled)
            {
                list.Label("  Sun heat strength: " + sunHeatStrength.ToStringPercent());
                sunHeatStrength = list.Slider(sunHeatStrength, 0f, 3f);
                list.CheckboxLabeled("  Shadows fall one way", ref directionalShadeEnabled,
                    "On: every rock, wall and big tree throws its shadow along the sun, longer the lower "
                  + "the sun is — the shade you see is the shade that counts. Off: shade is a small ring "
                  + "around each object instead.");
                list.CheckboxLabeled("  Walk shade to shade", ref sunPathingEnabled,
                    "On: creatures and colonists (unless drafted) prefer routes through shade, even if longer. "
                  + "Does nothing where shade does not help (steam and volcanic lands).");
                list.Label("  How much they avoid the sun: " + sunPathCostMultiplier.ToStringPercent());
                sunPathCostMultiplier = list.Slider(sunPathCostMultiplier, 0f, 3f);
                list.CheckboxLabeled("  Sun load bar", ref sunLoadBarEnabled,
                    "Shows a bar when you select one creature on a sun-heat map: how close it is to "
                  + "heatstroke, and how much the sun is adding where it stands.");
                list.CheckboxLabeled("  Animals hop shade to shade", ref shadeHopEnabled,
                    "On: wild animals do not stroll in the open sun. They rest in shade, stop at its edge, "
                  + "then sprint to the next patch of shade they can reach before the heat gets to them. "
                  + "Big animals dash further than small ones. Off: they wander as normal.");
                if (shadeHopEnabled)
                {
                    list.Label("    How far they will dash: " + shadeHopRangeMultiplier.ToStringPercent()
                             + " (lower is stricter)");
                    shadeHopRangeMultiplier = list.Slider(shadeHopRangeMultiplier, 0.25f, 2f);
                }
                list.CheckboxLabeled("  Back-to-shade ring", ref dashRingEnabled,
                    "Draws a line on the ground around a selected drafted colonist, showing how far they "
                  + "can go and still get back into shade before heatstroke sets in.");
                list.CheckboxLabeled("  Heat you can hear", ref heatSoundscapeEnabled,
                    "On a land built with it (the Long Shade): sunlit ground and shade sound different, "
                  + "keyed to where the camera is looking, not to your people. Off: no heat sound bed.");
                if (heatSoundscapeEnabled)
                {
                    list.Label("    Heat sound volume: " + heatSoundscapeVolume.ToStringPercent());
                    heatSoundscapeVolume = list.Slider(heatSoundscapeVolume, 0f, 2f);
                }
                list.CheckboxLabeled("  Herd calls and giant footfalls", ref creatureHeatSoundsEnabled,
                    "On a land built with it: a herd animal may call out at the edge of shade before it "
                  + "sprints, and a giant's footfalls (the gloomcast's) carry further than you can see. "
                  + "Off: both are silent.");
                list.CheckboxLabeled("  Cover follows the sun's height", ref kindFromElevationEnabled,
                    "On a land whose sun height comes from where it sits on the planet (the Stillsand): "
                  + "On: where the sun stands high, roofs and parasols protect; where it stands low, only "
                  + "the shade behind a wall or rock does. Off: the land's one fixed rule applies everywhere.");
                list.CheckboxLabeled("  Sand glare", ref sandGlareEnabled,
                    "On: open sand throws the sun back up, so standing on it in shade still heats you a "
                  + "little. Paved floors do not glare, so a paved patch of shade is fully cool. "
                  + "Off: shade on sand works as anywhere else.");
                if (sandGlareEnabled)
                {
                    list.Label("    Sand glare strength: " + sandGlareStrength.ToStringPercent());
                    sandGlareStrength = list.Slider(sandGlareStrength, 0f, 2f);
                }
                list.CheckboxLabeled("  Glare-blind", ref glareBlindEnabled,
                    "On a land built with it (the Stillsand): people standing in full glare slowly lose "
                  + "sight, and get it back in shade or indoors. Sun goggles (or any goggles that keep "
                  + "out glare) stop it, and some peoples are born with eyes that never need them. "
                  + "Animals are not affected. Off: nobody is glare-blinded.");
                if (glareBlindEnabled)
                {
                    list.Label("    How fast glare blinds: " + glareBlindRateMultiplier.ToStringPercent());
                    glareBlindRateMultiplier = list.Slider(glareBlindRateMultiplier, 0f, 3f);
                }
                list.CheckboxLabeled("  The mirage", ref mirageEnabled,
                    "On a land built with it (the Stillsand), under a high sun: the far edge of the map "
                  + "shimmers with water that is not there, the shimmer spoils long shots taken from full "
                  + "sun, and someone suffering heatstroke may set off walking for the water. They stay on "
                  + "the map: they come to, collapse, or stop when a drafted friend reaches them, and you "
                  + "get a letter either way. Off: none of it.");
                if (mirageEnabled)
                {
                    list.Label("    How often the heat-struck chase the water: " + mirageBreakChanceMultiplier.ToStringPercent());
                    mirageBreakChanceMultiplier = list.Slider(mirageBreakChanceMultiplier, 0f, 3f);
                }
            }
            list.GapLine();

            list.Label("Shade gear — how well each piece works depends on the land's kind of heat: "
                     + "overhead sun, low sun, or steam and volcanic heat (where no shade helps).");
            list.CheckboxLabeled("Parasols cast shade", ref parasolShadeEnabled,
                "On: a parasol shades the colonist carrying it, and a little of the cell beside them. "
                + "Strong under an overhead sun, weak under a low one. Off: it is just something to carry.");
            list.CheckboxLabeled("Shade tents cast shade", ref shadeTentEnabled,
                "On: a pitched shade tent shades the ground under it. Strong under an overhead sun, "
                + "weak under a low one. Off: it casts no shade.");
            list.CheckboxLabeled("Sun shields cast shade", ref sunShieldEnabled,
                "On: a standing sun shield throws shade on its far side from the sun. The one piece "
                + "that works under a low sun; only modest under an overhead one. Off: it casts no shade.");
            list.GapLine();

            list.CheckboxLabeled("Sand swimmers go under the sand", ref sandSwimEnabled,
                "On: creatures built to swim through loose sand (the vekka, the sand stalker, the krayt) "
              + "sink out of sight on sand, leaving a dust wake and a rumble, and burst up when they "
              + "strike, reach rock or are hit. Hard ground stops them. Off: they walk the surface "
              + "like any animal.");
            if (sandSwimEnabled)
            {
                list.CheckboxLabeled("  Droids are invisible to swimmers", ref sandSwimDroidImmunity,
                    "On: nothing under the sand goes after a pawn with no water in it, so droids and "
                  + "mechanoids can cross, fish and haul where nothing alive can. Off: swimmers attack them too.");
                list.Label("  Rumble volume: " + sandSwimRumbleVolume.ToStringPercent());
                sandSwimRumbleVolume = list.Slider(sandSwimRumbleVolume, 0f, 2f);
            }
            list.GapLine();

            list.CheckboxLabeled("Footprints (performance switch)", ref tracksEnabled,
                "On ground built to take prints (the Warscar's settled film, the Stillsand's sand), "
              + "everything that walks leaves prints pointing the way it went, invisible things "
              + "included. They stay until that land's own wind or dunes wipe them. Off: no prints "
              + "are recorded or drawn. This is the switch to flip if a big map runs slow.");
            if (tracksEnabled)
            {
                list.Label("  Prints kept per map: " + trackPoolCap
                         + " (when full, small animals' prints go first, then the oldest)");
                trackPoolCap = Mathf.RoundToInt(list.Slider(trackPoolCap, 1000f, 20000f) / 500f) * 500;
                if (trackPoolCap < 1000) { trackPoolCap = 1000; }
                list.Label("  Print opacity: " + trackPrintOpacity.ToStringPercent());
                trackPrintOpacity = list.Slider(trackPrintOpacity, 0.1f, 1f);
            }

            list.End();
            lastContentHeight = list.CurHeight + 12f;
            Widgets.EndScrollView();
        }
    }

    public class RM_CreatureBehaviorsMod : Mod
    {
        public static RM_CreatureBehaviorsSettings settings;

        public RM_CreatureBehaviorsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_CreatureBehaviorsSettings>();
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            // Footprints: apply a new cap and redraw with the new opacity / on-off now.
            if (Current.ProgramState != ProgramState.Playing || Find.Maps == null) return;
            foreach (Map map in Find.Maps)
            {
                RM_MapComponent_TrackGrid grid = RM_MapComponent_TrackGrid.For(map);
                grid?.ApplyCapacitySetting();
                map.mapDrawer.WholeMapChanged(RM_TrackDefOf.RM_TrackPrints);
            }
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
