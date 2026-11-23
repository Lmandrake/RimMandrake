# MachineLooks: admission at intake, and a PROPOSED split of Design Version 0.1.0

Admitted 2026-11-23 by a Conductor act (item RIMMANDRAKE_ADMIT_MACHINE_LOOKS_MOD_WITH_FRIDGE_AND_BATTERY, per ruling
RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS). Everything below the "What exists" section is a **proposal** for
the Designer and the owner. Nothing here locks a bar; the Designer's Lock step does.

## His words

- 2026-11-20, 3:30 PM PST (`D:\ClaudeWork\rimmandrake\conductor\gss_walk_20261120_his_words.md`, Message 2): "Go ahead
  and commission different looks for the battery at this time for the various styles too, like we did for the lamp
  already." In the same message: "Generate art for the heater too, and other vanilla basegame electrical objects that
  we commonly test with like production desks and research benches and things and turrets. [...] Wall coolers. That sort
  of thing. Televisions. Vanilla things that consume electricity. Generators. Solar panels. Do a design pass to see
  whether that belongs in this mod or in a RimMandrake existing or new mod: design and decide and advise, then present
  me with arguments why/where/whynot."
- 2026-11-20 (`conversations/2026-11-20-2350-97f0c93f.md` line 116): "I wonder if RimFridge should be part of the same
  RimMandrake mod that holds all of our reskinning of vanilla electrical devices and workbenches etc. Might even already
  be something there, or if that should be merged with some other mod all together, your call. But we should decide now
  so it can become an item that's worked and the art gathered out of the main pool." The Conductor's call (same file,
  lines 177-180): the fridge art goes in the reskin mod; the cold-storage function stays parked for Cuisine.
- The design pass he asked for: `design/specs/2026-11-20-vanilla-electrical-art-home/design.md` (item
  RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART): a new mod, Machine Looks, takes the appliances; Gimme Some Slack
  keeps the installation.

## What exists (measured 2026-11-23)

- **Mod folder:** none. `src/RimMandrake/MachineLooks` does not exist; no About.xml, no packageId in any mod list.
- **Art:** 7 battery pictures KEEP and 4 look icons KEEP, all in the art store, none installed; the Modern battery north
  is owed (REDO three times); 13 cold-storage renders of 2026-10-26 in the art store, never judged. Every sha, size and
  verdict: `kept_art.md`.
- **Shared code it would use:** the picker core `src/RimMandrake/_Shared/StylePicker/StylePickerCore.cs` (exists;
  consumers today Gimme Some Slack and FlowWorks); GSS's `ThingStyleDef`-per-look pattern (`<Def>_<Look>`).
- **Scope measured by the design pass:** 106 power defs on the 2026-08-29 dump, 97 buildable; the Core set his words
  name is 28 defs, about 252 pictures for four looks; the DLC add 10 buildable defs, about 72 pictures
  (`design.md` §"The wider set", from `power_census.json`; turret tops estimated).
- **Tests, Mod Settings, live proof:** none (no mod).
- **Art route:** the artpipe daemon's Codex worker homes hold a dead refresh token (`commissions.md` §"How the art was
  made"); the 2026-11-20 art was rendered with `art/gen_direct.py`. Daemon state on 2026-11-23: UNMEASURED.

## The 0.1.0 vision (PROPOSAL)

A player who loads Machine Looks can pick one of the four looks (Scrapper, Industrial, Modern, Futuristic) for each
vanilla battery he builds, through the same picker as Gimme Some Slack; the default look follows GSS when GSS is
loaded; an ideoligion's style is not silently overwritten and does not silently overwrite a picked look; with the mod's
switches off the game is vanilla. The battery leads because its art is ready (less the Modern north).

## Proposed split (PROPOSAL for the Designer and the owner)

| part | version | reason |
|---|---|---|
| mod skeleton: About (`mandrake.rm.machinelooks`), settings with a switch per group, the picker as a third consumer, `ThingStyleDef` `<Def>_<Look>`, a `CompStyleable` patch where a def lacks it | 0.1.0 | every later def needs it; the battery cannot ship without it |
| battery, four looks, three facings | 0.1.0 | art KEEP except Modern north; the owner asked for it first |
| Modern battery north | 0.1.0 | owed (RIMMANDRAKE_REDO_MODERN_BATTERY_NORTH_VIEW_FAILED_JUDGE_THRICE); 0.1.0 cannot ship three looks of four |
| the ideoligion-style rule (no silent overwrite either way) | 0.1.0 | the style field is contested (Ideology, Alpha Memes, VME) on the battery's neighbours; the rule is cheapest set once |
| stable defNames and a "clear this mod's looks" action, tested save/load | 0.1.0 (proposed) | design.md places it before 1.0.0; removing the mod mid-save is the run-voiding case |
| the look icons, own copy at `RimMandrake/MachineLooks/UI/Looks/<Look>.png` | 0.1.0 | KEEP already; a third put record row |
| the fridge pictures (see below) | 0.1.0 decision, art later | the owner asked that it be decided now; the art is unjudged and drawn for other mods' defs |
| battery charge bar over each look's gauge window | 0.1.0 live look | UNMEASURED (`commissions.md`) |
| heater, cooler, benches, research benches, televisions, generators, solar, sun lamp, flood light | later (0.2.0 onward, group by group) | about 250 pictures not yet drawn; one group per version keeps each judged before install |
| turrets | later, after a turret-top prototype | design.md step 4 |
| the 10 DLC defs | later | after the Core set |

## The fridge (a Designer question, not settled here)

Vanilla RimWorld has no fridge. The 13 cold-storage pictures were drawn for `RM_EvaporativeCrock` (ColdStorage, RM
tier) and four `RSW_*` cooling buildings in `mandrake.rsw.cuisine` (Star Wars tier,
`src/RimStarWars/Cuisine/Defs/RSW_CoolingUnits.xml`); the cold-storage function stays parked (ColdStorage was parked on
his word of 2026-11-20 as too small to be a mod alone). The Designer decides, with each limit tagged bar or our own rule:
(a) whether Machine Looks styles cold-storage buildings in the four looks when their mod is loaded (a PatchOperationFindMod
seam), (b) whether the RSW pictures stay with Cuisine and only RM-tier or generic fridge art comes here, (c) whether
any fridge picture fits one of the four looks at all. A fridge building with its own function is not this mod's: that
is the parked function.

## Old items mapped onto the mod (2026-11-23)

| item | state | version | reason |
|---|---|---|---|
| RIMMANDRAKE_REDO_MODERN_BATTERY_NORTH_VIEW_FAILED_JUDGE_THRICE | proposed | 0.1.0 | the one missing battery picture |
| RIMMANDRAKE_ADD_FRIDGE_ART_TO_ELECTRICAL_RESKIN_HOME | proposed | 0.1.0 decision | the fridge-art item the Conductor promised; Machine Looks is the home |
| COLD_STORAGE_LADDER_ART_JUDGE_SHEET | proposed | 0.1.0 decision (fridge pictures only) | judging the 13 renders; also mapped onto ColdStorage 0.1.0 on 2026-11-20 |
| COLD_STORAGE_ART_BUILD_SPRITE_BATCH | proposed | later (cooling-unit pictures only) | its stasis, item icons and motes stay with ColdStorage/Cuisine |

## What must happen before it runs

The mod is admitted at intake and switched OFF (`./pipe off MachineLooks`); all three live slots are full
(`maturation_dispatch.json` max_live 3: Pyrelands, FlowWorks, GimmeSomeSlack live on 2026-11-23). Before it may move,
its readiness list (`design/RimMandrake/standing_rulings.md` §No mod runs forward on a broken pipeline) must read
READY, with every component on its path looked at and each open pipeline ticket classed BLOCKS, RARE or NOT ON PATH:
- the move from intake (`maturation.py advance --to designer`, clause `intake_closed`), the Designer role launch on
  `stage.json` (already initialised), its exam, coverage judge and `lock-bars`;
- creating a mod that does not exist: About.xml and packageId, the folder, its place in the live mod list and in
  `infrastructure/state/modlists/manifest.FULL.json`; whether preflight accepts a mod with no prior build: UNMEASURED,
  a likely BLOCKS row;
- the offline build (`winbuild.py`) with `StylePickerCore.cs` linked as a third consumer, and deploy;
- the art route: the Modern battery north render and judge (gen_direct or a re-signed artpipe), installing kept art
  with the put record;
- the tests-first stage (no selftest exists yet);
- the in-game stage: a mod list with Machine Looks, Gimme Some Slack, Ideology and the bridge; the battery charge-bar
  look;
- the walk brief and the road back;
- a free slot.

Then a word moves it from intake (spec §4 "Intake", exit row) and `./pipe on MachineLooks` cites the READY list.
