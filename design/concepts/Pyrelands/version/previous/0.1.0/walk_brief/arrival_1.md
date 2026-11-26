# Pyrelands 0.1.0: walk brief, arrival 1
written_by: rm-detached-bench-rimmandrake-steward-pyrelands-pre-human-1795523659

Written 2026-11-24, 4:50 AM PST, by a fresh reader. This reader made none of this version's evidence writes (no stage
move, no in-game row). Sources: `D:\Luke\dev\RimMandrake\design\concepts\Pyrelands\version\stage_record.json`, the summary,
rows, strange things and pictures of visit 8 (`D:\Luke\dev\RimMandrake\design\concepts\Pyrelands\version\in_game\visit_8\`),
`build_match.py check --mod Pyrelands`, `D:\Luke\dev\RimMandrake\design\concepts\Pyrelands\journal.md`, `git log` on
`src\RimMandrake\Pyrelands`, the open items, and the walk save file itself.

## What to open

- **Savegame:**
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\PYRELANDS_0.1.0_VISIT8_WALK_FULL.rws`
  (36,322,960 bytes, saved 2026-11-24 2:19 AM PST) [measured]. **It needs a small restage first**
  (`RIMMANDRAKE_FREE_PYRE_WALK_SAVE_SKY_TUTOR_PINS_CLEAR`), for two reasons read from the file:
  - Its storyteller is Tutor, and under Tutor the sky stays clear for good. You would never see ash fall, cinderfall or
    black rain. If you open this save as it is, change the storyteller to Cassandra first.
  - The creatures left their station before the save was made (below).
- **Mod list:** your full list, 314 mods in the save, Camera+ among them [measured]. ArchBig now runs another mod's test and
  its `ModsConfig.xml` is a 12-mod list [measured 4:38 AM]. The seat that stages the walk restores the full list.
- **Build:** the newest mod code is `4a9d62cae0` (2026-11-23 8:50 PM PST). ArchBig's Mods folder is in sync with it
  (4769 files) [measured 4:48 AM]. All 40 in-game checks count on that build [measured].
- **The map:** a hot test map (57 C outdoors when the site loaded), 250 x 250, with three colonists, a few survival meals and
  no base. It is not a colony with a history. The game is paused, the camera opens on station 5.
- **Signs:** five signs stand at the stations. They draw only after one bridge call in that game session.

| station | where (x, z) | what it shows | as saved |
|---|---|---|---|
| 1 burn front | 26 to 46, 20 to 36 | a fire line in fresh ember grass | 32 burning cells at the left edge; unpause and watch |
| 2 creatures | 68 to 88, 20 to 36 | ullai herd, furnace-beast, ashwallows | 5 of 6 ullai and 2 ashwallows in one cell at (68, 27); the other ullai at (68, 30); the furnace-beast is at (21, 33), left of station 1 |
| 3 scorch-fruit | 178 to 182, 26 to 30 | pods standing in ash | 16 pods |
| 4 roofed grass | 26 to 46, 62 to 78 | left patch roofed (withers within a day), right patch open | as labelled |
| 5 charred ruin | about 22, 98 | blackened walls on deep ash | as labelled |

- **Look first** at station 1, unpaused, for a day or two at speed 3: the fire walking, the scar behind it, the fruit in the
  scar. That is the mod's flagship. Then the natives: 5 fire-hawks, 2 flamefangs and 9 zeer are on the map.
- No bar waits on your judgement of long play: a season of play is play testing (your words of 2026-11-24). The long
  scripted walk is gone on your words of the same day ("what's the MINIMUM test necessary to show it?"). Three small scenes replaced it and pass: the burn
  survives a reload, colonists step away from fire and eat first, and the fire runs on your full list with no error of ours.

## What changed since his last look

The record has no `his_walk` move, so this covers the whole version. **Your informal look was on 2026-11-22 at about 6 PM
PST, on the visit 5 save.** You said: *"Charred ruins look GREAT"*, *"Scorch fruit patch look FANTASTIC"*, and asked for a
black outline on the ullai.

Since that look:
- **Ullai outline.** First thin (`f8003374bc`), then medium, your pick B (`99cede2bfa`). You: *"I will see it next walk of
  Pyrelands just to be sure, but enough."* This walk is that look.
- **Fire-hawk flight pictures, flip-book S** (`10bc0e7cca`). You: *"Yes, S is superior. Authorized pick."*
- **A lone fire fans out and burns with ragged edges**; before, it left a one-cell lane (`510d96f7b8`).
- **A furnace-beast no longer tears the roof off the barn it heats**; Huge Things spares it (`aca7464fe3`).
- **A fire-hawk already carrying an ember drops it no more once the mod or its switch is off** (`4a9d62cae0`).
- **The wind and master switch texts and the fire-front letter now say what the fire does** (`454764adbe`).
- Char on ruins stays paint. You: *"Char as paint is ok."* The flamefang danger stays: one bite survivable, two can kill.

Earlier in this version (from 2026-11-13):
- **The fire walks with the wind and no longer floods the map** (`49e11870b4`); burned lanes close up (`2910619418`). Your
  bar: *"I just wanted a natural grassfire feel."* Wind-off burned 84% of the map in the four-day test, wind-on 24%.
- **Black rain puts fires out, with a switch for it** (`24a2069d18`). Rain that another source forces becomes black rain,
  and herds never settle on fresh ash (`de0aae4a1b`).
- **Grasses grow at full speed on old dry ash**; before, at a tenth (`e63595716c`).
- **A sprayer carrier foams the fire in the way** (`3acf1ad82b`).
- **One untended flamefang bite is thrown off** (`11fca75b4b`).
- **An ashwallow beside a fire dives first**, before any dash for shade or water (`675ab57651`).
- **The fire-hawk**: carries its ember anywhere on the map to the biggest fuel (`82d9247595`), a first-sighting letter
  (`8bd38615e3`, its blanks filled in `fa5e6df8cb`), a crestfeather trophy (`6b30bbf55d`).
- **Furnace-beast** at body size 9, twice the zeer, with new art (`6120bb02aa`, `99507bc992`). Your cards.
- **Texts stop promising world generation and paving as a firebreak** (`4a7c450d6b`, `f71693d77a`); world placement ships
  off (`e36d2374af`). Your cards.

## Known, not fixed: you need not report these

No raid bar is open, and no bar moved to the next version [measured: `maturation.py next`, `VERSION.json`].

Current version, open:
- **After heavy ash fall the grass can vanish from view** under the ash (seen on 2026-11-16, day 7 of a free-sky week: bare
  grey while 81% of open ground held grass). No later commit names a fix and nobody has looked again, so whether it still
  happens is UNMEASURED [guess ~70% it does]. Your card of 2026-11-17 makes it a defect against
  `grass_carpets_and_regreens`. `RIMMANDRAKE_SHOW_PYRE_GRASS_UNDER_ASH_COVER_COUNTED_UNSEEN`.
- **"Richer ground ringing standing water" has no live check** that decides it.
  `RIMMANDRAKE_STAGE_PYRE_POND_SO_SHORE_RING_CLAUSE_GETS_A_READING`.
- **Four long readings are owed**: foreign animals on your full list (9 zhakka seen in visit 1), a one-second stall every
  250 ticks, the giant-passage dump, how much scorch-fruit a ready colony can store.
  `RIMMANDRAKE_READ_PYRE_LONG_RUN_FOUR_OWED_ZHAKKA_FIRST`.
- **Footprints in ash and the hover text "Ash"**: fixed offline, promised to you for a look on 2026-11-08, and no station
  shows them. Walk a colonist over bare ash. `RIMMANDRAKE_SHOW_PYRE_HIS_WALK_FOUR_PICKS_ULLAI_FIRST` (part 3).
- **The crestfeather still wears vanilla's thrumbo horn picture**, and the 17 art and text entries added after your
  2026-10-16 sheet have no judge verdict. `RIMMANDRAKE_JUDGE_PYRE_POST_SHEET_ART_CRESTFEATHER_A_HORN`.
- **One visit 7 burn stamp on a control pad**: classed a fault of the test scene, not of the mod, which had its fire mechanics
  switched off. Who lit that pad is unknown. The same check passed in visits 8 and 9. `RIMMANDRAKE_CLASS_PYRE_CONTROL_PAD_BURN_NOBODY_LIT`.
- **The tree item** stays open until the version passes: `RIMMANDRAKE_FINISH_PYRELANDS_AGAINST_TREE_FURNACE_GREW_TO_NINE`.

Not this mod, but on your list:
- **The Deep Desert Tribes mod is in the save.** Its fire rite can turn wild animals on your colony for a fire you did not
  set. It is a separate mod, worked after this one passes. `RIMMANDRAKE_SPARE_COLONY_BEAST_REVENGE_FOR_TRIBES_RITE_FIRE`.
- River steam (FlowWorks) waits on its own look: `RIVER_STEAM_ANIMATION_1`. The Struck Glass rite is campaign work:
  `PYRELANDS_STRUCK_GLASS_RITE_BUILD_1`.

Next version, by your words or cards:
- Black rain fills the moat and the tanks: `RIMMANDRAKE_BUILD_BLACK_RAIN_FILLS_MOATS_TANKS_STAY_DRY`.
- Choking smoke as its own weather: `RIMMANDRAKE_BUILD_PYRE_SMOKE_WEATHER_ONLY_LONGSHADE_HAS_ONE`.
- Wind-driven fire in every biome: `RIMMANDRAKE_GENERALIZE_WIND_FIRE_ALL_BAROQUE_BIOMES_NEXT_VERSION`.

Recorded and left, no ticket (`D:\Luke\dev\RimMandrake\design\concepts\Pyrelands\version\polish.md` and
`D:\Luke\dev\RimMandrake\design\concepts\Pyrelands\version\in_game\visit_8\polish.md`): a front on never-burned ground
shows as a square block about 5 cells deep, and a front about 10 cells wide as a flat one-cell line; a sprayer carrier who wears a
shield belt never foams; a week-old scar is about 60% green; wild animals kill one another in plain sight.

## What I noticed first

- **The sky cannot change on this save** (storyteller Tutor), and the sky is part of the vision.
  `RIMMANDRAKE_FREE_PYRE_WALK_SAVE_SKY_TUTOR_PINS_CLEAR`.
- **The herd is a heap.** Animals that run from the sun all pick the same shade cell: 5 ullai and 2 ashwallows on one cell,
  4 ashwallows on another. It is the shade dash of Creature Behaviors, not the ullai, so it would hide the outline you came
  to see. The restage spawns the herd last; the dash itself is
  `RIMMANDRAKE_SPREAD_SHADE_DASH_SEVEN_ANIMALS_ON_ONE_CELL`.
- **With the wind the burn is narrow.** In the four-day pictures it leaves a few long strips that all run the same way; most
  of the map keeps its grass. The wind-off row is round and floods. Whether the strips feel like a grassfire is yours:
  `D:\Luke\dev\RimMandrake\design\concepts\Pyrelands\version\in_game\visit_8\screenshots\burn_line2_dayend_sheet.jpg`
  (top row wind on, bottom row wind off).
- **"Green again" is orange.** Ember grass regrows in its own orange-red, and fire on it is orange on orange when zoomed
  out. The check counts grass, not colour.
- **The About text still says a smoulder relights "far from anything you have built".** The code does keep that distance,
  so the line is true. You took the same words out of the bar on 2026-11-16; say if you want them out here too.
- **The sign texts are ours, not a player's** ("VISIT8", "walls painted RM_FE_Charred"). The restage item carries it.
- **One of the three colonists came with an addiction and a heart blockage** (the test list generated them). What happens to
  that colonist is not the biome.
