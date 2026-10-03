# LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1 -- choices (FOUNDRY, 2026-10-03)  OWNER VETO OPEN

Item cites no spec. Words used: RM_Vissler description ("everything hungry comes to the twitch"; "regrows the arm in a season"),
RM_VisslerArm comment ("hunter's lure" is MECHANICS_BUILD_1), item questions 1-3.
Existing: arms exist (RM_VisslerArm in RM_LeaningScrubItems.xml, shed by RM_RunwayBloomExtension, art wired). Roster read as XML nodes:
fuzzrunner, thornhold, shokka, zellik, fuzzviper, surrik, ribbonwhip, vissler, dustflutter, shirrel, crustweevil, rollbug, tikkit.
Artpipe: only RM_Vissler creature art; no arm-specific job. No new art owed.

## Choices (owner veto open)
1. SPECIES: no species list; whoever the engine's hunger AI lets eat Meat: rollbug (foodType Meat), all predators
   (shokka, zellik, fuzzviper, surrik, ribbonwhip) and omnivores (thornhold, shirrel, vissler). Herbivores (fuzzrunner,
   dustflutter, crustweevil, tikkit) will not. Rollbug and the four named predators are all covered. Veto: restrict.
2. MECHANISM: FOOD, not a lure job. RM_VisslerArm now has `<ingestible>` (foodType Meat, RawTasty, Nutrition 0.05).
   Reason: vissler description says "everything hungry comes to the twitch"; vanilla AI, no new job code. A hunger-blind
   lure stays MECHANICS_BUILD_1 ("hunter's lure").
3. ROT: yes, CompProperties_Rottable daysToRotStart 6, rotDestroys (+ tickerType Rare, required). Hunters-buy-them trade
   window is therefore ~6 days.
4. TOGGLE: `visslerArmFoodEnabled` (Mod Settings) via Harmony postfix on Thing.IngestibleNow (src/.../Source/RM_VisslerArm.cs,
   in csproj). Off = arm inedible (rot comp stays).
5. Humans: RawTasty raw meat with optimalityOffsetHumanlikes -30 (vanilla value), AteRawFood thought.
6. ART: none owed (arm art wired, artpipe has only creature art).
## Proof
selftest_leaningscrub.py exit 0 (46 components, 35 breaks incl. arm_not_rotting). validate_patch OK. winbuild BUILT.
UNMEASURED live: that a hungry wild rollbug/predator actually takes the job for an arm (needs a hungry wild animal;
validation covers def comps + Harmony rule only). Not deployed.
