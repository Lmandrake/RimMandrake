# Bars whose sentence holds long play, for the Conductor's call

Written 2026-11-24 for `RIMMANDRAKE_ENACT_SEASON_PLAY_IS_PLAYTEST_NOT_ACCEPTANCE_NOR_HIS_WALK`. The rule: `design/RimMandrake/standing_rulings.md`
§Season-long play is play testing. No bar's sentence was changed, loosened or deleted. Which class a bar is in: [guess ~85%].

## The sentence is nothing but long play

| mod | bar | sentence |
|---|---|---|
| Contagion (held) | `walk_red_lid` | The player walks a lived-in Contagion colony through a Bloom day, a natural Burn with a dash, a Repulsor Burn and a gestation, and the sky and the body tell one story. |
| Graffiti (held, locked) | `stories_not_tax` | Across three in-game weeks of an ordinary colony, the player sees graffiti make occasional stories, never a permanent mood tax or a stream of messages. |
| Graffiti (held, locked) | `walk_lived_in` | The player walks a lived-in colony: a spree, recreation tagging, a raid's exit tags and a trader visit, and sees the wall tell the colony's story. |

## The sentence holds long play beside claims that a short scene decides

| mod | bar | the long-play part | what stays |
|---|---|---|---|
| Pyrelands (locked) | `walk_season_on_the_pyre` | "plays a fresh Pyrelands colony through about two weeks on the full list" | the reload; the step away from fire; the meal first; the full list; fruit, sowing, shelter |
| FlowWorks (locked) | `walk_moat_season` | "playing a colony through a season on the full list" | the moat sequence, the save and the reload |
| Gimme Some Slack (locked) | `walk_scavenger_base` | "on his full list for about a week"; its deciders still hold `LOOK_STAGE8` | the cut, the re-string, the save and the reload |
| PyrelandsMechanics (held) | `walk_tribes_season` | "In ordinary play a rite party comes on its own, lights the grass and picks behind the front." Nothing decides this sentence now | the saved and reloaded rite |
| Cauldron (held) | `cauldron_walk` | "Returning still offers dependable work and risky expeditions." | the reload, the repeat, the second order |
| GelatinousSlime (held) | `repeat_walk` | "carry on with a prepared colony. The body stays useful" | the reload, the rescue, legible costs |
| Stillsand (held) | `stillsand_walk` | "carry out the expedition and resupply loop", played whole | the reload, the repeat, the second order |

## What the ruling implies for Pyrelands `walk_season_on_the_pyre`

- The words "through about two weeks on the full list" are play testing. No script and no walk can pass them.
- The rest of the sentence stays a bar. `sc_reload_keeps_the_burn`, `sc_fire_sense` and `sc_full_list_smoke` decide the rest.
- `LOOK_STAGE8` was a decider (077f18f8b0). `LOOK_STAGE8` is a support again, without the two weeks, and the bar proves at
  stage 6. The Conductor's recorded act of 2:08 AM PST on 2026-11-24 named his walk as a decider, so the Conductor records this
  change.
- A change of the sentence, of the leaf's `scenario` (it still asks for a repeat and a second order in play) or of the bar's
  name is the Conductor's. A change of `tree.json` voids the Cold Reader exam (`design/concepts/Pyrelands/version/polish.md`).
- `exam_control/` and `sheet.md` carry the same sentence.

## The cleanse proposals: the whole bar of 23 held biome mods

The Designer's brief told each cleanse to run the whole bar for a season on a full map. The brief is corrected. The proposals stay
as written. In 20 of 23 the sentence of the whole bar names a season. In the other three (Greentide `B8`, LeaningScrub
`whole_season`, TheSump `B7`) only the range does [measured].

The 20: Abyss `B8`, BlueDesert `B8`, Cauldron `whole`, Contagion `season`, CrackedLands `B8`, FeverWood `whole`, GelatinousSlime
`whole`, LanternDeeps `B8`, LongShade `B8`, Miasma `B9`, RustCathedral `B7`, SleepingIce `B8`, Stillsand `B_WHOLE`, TerminalBiomes
`B8`, TheForge `B8`, TheRot `B7`, Warscar `W9`, Wastes `B8`, Webwork `B8`, WeepingStones `B9`. Each is in
`design/concepts/<Mod>/cleanse/bars.json`.

## The Conductor's rulings

The Conductor rules each bar above by name: cut the long-play words from the sentence (in `tree.json` or `cleanse/bars.json`),
delete the bar, or keep it with its reason in a row `| <mod> | <bar> | kept: <why> |` here. The check of item
`RIMMANDRAKE_RULE_LONG_PLAY_BARS_TWENTY_ARE_CLEANSED` is `python3 design/specs/2026-11-24-oversized-scenes/check_long_play_bars.py`:
exit 0 when no bar here still asks for long play, 1 when one does (each is named), 2 when it could not look.

| mod | bar | ruling |
|---|---|---|
