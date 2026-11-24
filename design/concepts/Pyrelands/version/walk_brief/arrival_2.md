# Pyrelands 0.1.0: walk brief, arrival 2
written_by: rm-detached-bench-rimmandrake-steward-pyrelands-pre-human-1795561517

Written 2026-11-24, 3:25 PM PST, by a fresh reader. This reader made none of this version's evidence writes (no stage
move, no in-game row). Sources: the stage record, the summary, rows, strange things and pictures of visit 9
(`D:\Luke\dev\RimMandrake\design\concepts\Pyrelands\version\in_game\visit_9\`), `build_match.py check --mod Pyrelands`,
`D:\Luke\dev\RimMandrake\design\concepts\Pyrelands\journal.md`, `git log` on `src\RimMandrake\Pyrelands`, the open items,
and the walk save file itself. It replaces `D:\Luke\dev\RimMandrake\design\concepts\Pyrelands\version\walk_brief\arrival_1.md`:
that arrival went back to the game the same morning, for the checks that the last code change touched.

## What to open

- **Savegame:** `D:\ClaudeWork\rimmandrake\instances\b\Saves\PYRELANDS_0.1.0_VISIT9_WALK.rws` (27,660,888 bytes, saved
  2026-11-24 12:59 PM PST) [measured]. It opens on **ArchSmall**. A seat stages it: ArchSmall is now in use for your Explosive
  Knockback walk [measured 3:10 PM]. **It needs a small restage first** (`RIMMANDRAKE_FREE_PYRE_WALK_SAVE_SKY_TUTOR_PINS_CLEAR`):
  - Its storyteller is Tutor [measured], and under Tutor the sky stays clear for good. If you open it as it is, change the
    storyteller to Cassandra (game options) to see ash fall, cinderfall or black rain.
  - The five station signs are not in the save [measured]: a plain load shows no sign. Use the table below.
- **Mod list:** the Pyrelands small list, 18 mods: all five DLC, the zoom mod (`ray1203.simplecamerasetting`), the biomes, the
  bestiary and the Utinni patches that supply the cast [measured from the save]. Full-list testing is retired on your word.
- **Build:** the newest mod code is `a6f05380df` (2026-11-24 4:45 AM PST). All 39 in-game checks count on it [measured]. No
  Pyrelands game file of ArchSmall or ArchBig differs from it [measured 3:18 PM].
- **The map:** a hot test map (52 C in a picture of the session), 250 x 250, three colonists, a few survival meals, no base and no
  history. The camera opens on station 5.

| station | where (x, z) | what it shows | as saved |
|---|---|---|---|
| 1 burn front | 20 to 39, 20 to 35 | a fire line at the edge of fresh ember grass | 32 burning cells on the left edge [measured]; unpause and watch |
| 2 creatures | 74 to 93, 20 to 35 | ullai herd, furnace-beast, ashwallows | 6 ullai in a row at z 24 (x 76 to 86), the furnace-beast at (82, 30), 2 ashwallows at (89, 30) and (91, 30) [measured]; look **before you unpause**, they run for shade |
| 3 scorch-fruit | 136 to 139, 26 to 29 | pods in bare ash | 16 pods set by hand; real ones come at station 1 |
| 4 roofed grass | 173 to 177 and 182 to 186, 37 to 41 | left patch roofed (withers within a day), right patch open | as labelled |
| 5 charred ruin | about (159, 105) | blackened walls on deep ash | made with the map, no event behind it |

- **Look first** at station 2, paused: the outlined ullai. Then station 1, unpaused, for a day or two at speed 3: the fire walking,
  the scar behind it, the fruit in the scar. That is the mod's flagship.
- **Natives on the map:** 8 more ashwallows, 2 fire-hawks, 1 flamefang, 3 sytheclaws, 12 gizka [measured].
- No bar waits on your judgement of long play: season-long play is play testing (your words of 2026-11-24).
- No station shows an aftermath that owes a START twin: station 5 came with the map, station 3's cause is watchable at station 1.

## What changed since his last look

The record's last `his_walk` move is 2026-11-24 4:50 AM PST, and no walk is recorded after it. **Your last recorded look at the
walk stations was 2026-11-22, about 6 PM PST, on the visit 5 save.** You said: *"Charred ruins look GREAT"*, *"Scorch fruit
patch look FANTASTIC"*, and asked for a black outline on the ullai. On 2026-11-24 at about 11:18 AM you also looked at ArchBig
during visit 9 and saw no large grazing; the count agreed (16 of 16 plants at every read over 4,000 ticks).

New since arrival 1 of this brief (`a6f05380df`, from a Codex review, read sound by a fresh reader):
- **"Reset all" works**: shown live, it put back four changed fields.
- **Scorch-fruit comes only on ground that burned within a day.**
- **Each switch stops what it names**: the opening scar's ash and bonus, the share of Ash Drift in the sky, the ashwallow's
  burrow, the furnace-beast's bed fire. Read in code and checked offline; these were not each staged live.

Between your 2026-11-22 look and arrival 1:
- **Ullai outline**: thin (`f8003374bc`), then medium, your pick B (`99cede2bfa`). You: *"I will see it next walk of Pyrelands
  just to be sure, but enough."* This walk is that look.
- **Fire-hawk flight pictures, flip-book S** (`10bc0e7cca`). You: *"Yes, S is superior. Authorized pick."*
- **A lone fire fans out and burns with ragged edges**; before, it left a one-cell lane (`510d96f7b8`).
- **A furnace-beast no longer tears the roof off the barn it heats** (`aca7464fe3`).
- **A fire-hawk already carrying an ember drops it no more once the mod or its switch is off** (`4a9d62cae0`).
- **The wind and master switch texts and the fire-front letter say what the fire does** (`454764adbe`).
- Char on ruins stays paint. You: *"Char as paint is ok."* The flamefang danger stays as you accepted it.

Earlier in this version (from 2026-11-13):
- **The fire walks with the wind and no longer floods the map** (`49e11870b4`); burned lanes close up (`2910619418`). Your bar:
  *"I just wanted a natural grassfire feel."* Visit 9, four days: 31% burned at worst with the wind on, 84% with it off.
- **Black rain puts fires out, with a switch** (`24a2069d18`); rain that another source forces becomes black rain, and herds never
  settle on fresh ash (`de0aae4a1b`).
- **Grasses grow at full speed on old dry ash** (`e63595716c`). **A sprayer carrier foams the fire in the way** (`3acf1ad82b`).
- **One untended flamefang bite is thrown off** (`11fca75b4b`). **An ashwallow beside a fire dives first** (`675ab57651`).
- **The fire-hawk** carries its ember to the biggest fuel (`82d9247595`), a first-sighting letter (`8bd38615e3`,
  `fa5e6df8cb`), a crestfeather trophy (`6b30bbf55d`).
- **Furnace-beast** at body size 9 with new art (`6120bb02aa`, `99507bc992`), and **texts that stop promising world generation and
  paving as a firebreak** (`4a7c450d6b`, `f71693d77a`, `e36d2374af`). Your cards.

## Known, not fixed: you need not report these

No raid bar is open, and no bar moved to the next version [measured: `maturation.py next`, `VERSION.json`].

Current version, open:
- **After heavy ash fall the grass can vanish from view** (seen 2026-11-16: bare grey while 81% of open ground held grass). No
  commit names a fix and no later look is recorded, so whether it still happens is UNMEASURED [guess ~70% it does]. Your card of
  2026-11-17 makes it a defect. `RIMMANDRAKE_SHOW_PYRE_GRASS_UNDER_ASH_COVER_COUNTED_UNSEEN`.
- **"Richer ground ringing standing water" has no live check.**
  `RIMMANDRAKE_STAGE_PYRE_POND_SO_SHORE_RING_CLAUSE_GETS_A_READING`.
- **Two long readings are owed**: the giant-passage dump, and how much scorch-fruit a ready colony stores. Two more (foreign
  animals, a one-second stall every 250 ticks) wait for the integration phase, as they need the full list.
  `RIMMANDRAKE_READ_PYRE_LONG_RUN_FOUR_OWED_ZHAKKA_FIRST`.
- **Footprints in ash and the hover text "Ash"**: fixed offline, promised to you on 2026-11-08, and no station shows them. Walk a
  colonist over bare ash. `RIMMANDRAKE_SHOW_PYRE_HIS_WALK_FOUR_PICKS_ULLAI_FIRST` (part 3).
- **The crestfeather wears vanilla's thrumbo horn picture**, and the 17 art and text entries added after your 2026-10-16 sheet
  have no judge verdict. `RIMMANDRAKE_JUDGE_PYRE_POST_SHEET_ART_CRESTFEATHER_A_HORN`.
- **The wind and master tooltips were not hovered live** in visit 9 (the settings window opened; the letter's new text was read).
- **Animals in the sun all run to one shade cell**: Creature Behaviors, `RIMMANDRAKE_SPREAD_SHADE_DASH_SEVEN_ANIMALS_ON_ONE_CELL`.
- **The tree item** stays open until the version passes: `RIMMANDRAKE_FINISH_PYRELANDS_AGAINST_TREE_FURNACE_GREW_TO_NINE`.
- **The words of bar `walk_season_on_the_pyre`** still describe a season; the Conductor rules on them:
  `RIMMANDRAKE_RULE_LONG_PLAY_BARS_TWENTY_ARE_CLEANSED`. Two small scenes decide the bar (reload keeps the burn, colonists step
  away from fire) and pass.

Closed since arrival 1: the visit 7 control-pad burn is a fault of the test scene, not the mod
(`RIMMANDRAKE_CLASS_PYRE_CONTROL_PAD_BURN_NOBODY_LIT`).

Other mods and lanes:
- The Deep Desert Tribes mod is **not** on this list. Its rite fire can turn animals on your colony:
  `RIMMANDRAKE_SPARE_COLONY_BEAST_REVENGE_FOR_TRIBES_RITE_FIRE`, worked after this mod passes.
- River steam (FlowWorks) waits on its own look: `RIVER_STEAM_ANIMATION_1`. The Struck Glass rite is campaign work:
  `PYRELANDS_STRUCK_GLASS_RITE_BUILD_1`.

Next version, by your words or cards:
- Black rain fills the moat and the tanks: `RIMMANDRAKE_BUILD_BLACK_RAIN_FILLS_MOATS_TANKS_STAY_DRY`.
- Choking smoke as its own weather: `RIMMANDRAKE_BUILD_PYRE_SMOKE_WEATHER_ONLY_LONGSHADE_HAS_ONE`.
- Wind-driven fire in every biome: `RIMMANDRAKE_GENERALIZE_WIND_FIRE_ALL_BAROQUE_BIOMES_NEXT_VERSION`.

Recorded and left, no ticket (`D:\Luke\dev\RimMandrake\design\concepts\Pyrelands\version\polish.md` and the visit 8 and 9 polish
lists): a front on never-burned ground shows as a square block; a shield-belt wearer never foams, and a foam shot already
aimed still fires after its switch goes off; a fire-hawk passes over a fuel patch whose middle cell is foamed; natural water
never sets off the gentle burst; the giant switch's tooltip is wrong about animals already on the map; a week-old scar is
about 60% green; wild animals kill one another in plain sight.

## What I noticed first

- **From far out the burns are long straight lanes, 8 to 10 cells wide, all running one way, with squared ends.** Close up the
  front is ragged and looks natural. The GPT judge said the same: passes, *"but the straight lanes weaken the natural appearance"*.
  Whether that is your *"natural grassfire feel"* is yours to say:
  `D:\Luke\dev\RimMandrake\design\concepts\Pyrelands\version\in_game\visit_9\screenshots\burn_share_on_sheet.jpg` (far) and
  `D:\Luke\dev\RimMandrake\design\concepts\Pyrelands\version\in_game\visit_9\screenshots\walk_small_hourly_sheet.jpg` (close).
- **The ullai stand in a row facing away, so each shows as a thin dark upright stroke with a pale tip.** Their outline reads best from
  the side: unpause for a moment and catch one turning. Soon after, the herd is one heap at the left edge
  (`D:\Luke\dev\RimMandrake\design\concepts\Pyrelands\version\in_game\visit_9\screenshots\walk_small_closeups.jpg`).
- **The sky cannot change on this save, and the signs are gone** (the restage ticket above carries both).
- **The sign words are ours, not a player's** ("VISIT9", "walls painted RM_FE_Charred"). Same ticket.
- **"Green again" is orange**: ember grass regrows orange-red, and fire on it is orange on orange when zoomed out.
- **The hand-set fruit is a tidy 4 x 4 grid**; the real seeding is scattered, as station 1's scar shows.
- **One colonist has a psychite addiction and another carries a bite and frailty** (the test list made them). What happens to them
  is not the biome.
