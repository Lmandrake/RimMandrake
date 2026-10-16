# Standard biome review savegame — specification

spec-version: **1** (2026-10-15, BENCH)

**Owner, 2026-10-15 ~20:10 PDT:** *"Let's define a standard savegame for the biomes like this, so we can start improving
the specification, ok?"* "Like this" means the Pyrelands review save `RM_pyre_review_20261015`, built by
`src/RimMandrake/Pyrelands/human_review.py` (`review/COVERAGE.md`, `review/KEYSHEET.md`), plus the corrections from
his walk that night. Earlier, the same day: *"Not just a "hey look it's the Pyrelands" but a nice, orderly
station-by-station demonstration of the mechanics to test, the art to examine, etc. That showed more hidden bugs than
anything."*

This file is the contract every biome's review save is built to. It is versioned: a change bumps `spec-version`, and
every builder stamps the version it was built to into its key sheet and its sign sidecar. A save built to an older version
is not wrong. It shows which rules it predates.

Related: the method `design/RimMandrake/northstar_human_review.md` (the calm world and the build discipline, which still
hold); the review ladder `infrastructure/VALIDATION_LADDER.md`; the skills `rimworld-live-review` and
`rimworld-review-sheets`; worked examples `src/RimMandrake/GimmeSomeSlack/human_review.py` and
`src/RimMandrake/FlowWorks/review_map.py`.

---

## 1. Purpose

- **One paused map per biome that he walks with the UI on.** Each station shows one key look or state. Its sign says what
  to LOOK at, what to DO, and what to DECIDE. He walks it at the biome's S2 sitting to accept or reject the visual bars
  (kickoff packet §1, O2).
- **It is a review environment, not a test.** It has no verdicts and no pass bars, and it records no result. The north-star
  matrix owns the combinations. The save owns the looks that only a human can judge.
- **It comes last on the ladder** (owner, 2026-09-01: *"don't use humans where a screenshot will do"*). Everything
  mechanical has passed the machine gates (§8) and an agent screenshot pass before he loads it. Nothing he finds on the
  walk should be a missing texture, a stale file or an orphan station.
- **It is a deliverable.** *"Options he must LOOK at ship as a savegame."* The keeper save is kept until he says delete.

## 2. The map

- **It is the biome's own map.** It is built on a saved site fixture of the biome (`NS_<Biome>_site_<n>_<fingerprint>_<r>`,
  made by the biome's `northstar_site.py`). A quicktest map is not the biome. The builder refuses a map whose BiomeDef is
  not the biome's, or whose fixture fingerprint does not match the live def set.
- **Calm world**, set by the builder and re-checked by every `--goto`:
  - weather Clear and locked;
  - the clock pinned to daylight (noon, or the biome's brightest hour when its sun never reaches noon light);
  - Peaceful storyteller and the incident queue cleared;
  - every non-colonist swept before the pens are filled, and every hostile killed;
  - every fire out unless a station stages one;
  - research finished, god mode on, game paused;
  - screenshot mode off, and the game never fullscreened or focused.
- **Mod Settings at the shipped defaults.** Board S names each setting and the station that shows it.
- **One restart.** Everything the save needs is deployed before the single launch (gate PW6). If a fix needs another
  restart, the build is redone after it. Nothing is patched into a running game.
- **Colonists** stand drafted in a sheltered room in the free area, and the shelter is climate-controlled when the biome is
  hostile outdoors. No station needs a colonist. A DO line that needs one says so ("draft a god-mode colonist").

## 3. Required station kinds

Each biome supplies stations of the kinds below. A kind the biome has nothing for is marked `none: <reason>` in COVERAGE,
never silently dropped.

| row | kind | what a station of this kind must show |
|---|---|---|
| **A** | Ground / terrain | Each terrain the biome ships, on a pad big enough to judge the tiling (8x8 or larger), with its edge against the biome's common ground. Each terrain transition the biome causes (a burn, a wash, a freeze) shows as a BEFORE pad and an AFTER pad. |
| **B** | Mechanics demos | Each mechanic a player can SEE, staged in its working state. Every comparative claim (X heats, Y grows faster, Z protects) has a **control** beside it (§6). A mechanic that runs over days shows a staged state (for example "burned 2 days ago"), never a clock. |
| **C** | Flora | Each wild plant the biome ships, at **every growth stage it draws differently**. The minimum is 5 strips at 5/25/50/75/100%, and a plant with staged graphics shows each stage. Every random variant (A/B/C), the leafless or burnt drawing, and the harvest product (on the ground beside the plant) are shown too. A ground-cover mix station shows the biome's density. |
| **D** | Items and buildings | Each item, building, floor and order the biome adds: the item on the floor, the building built (and powered or lit when that changes its look), and an order designated and complete. |
| **E** | Biome fauna pens | One pen per wild animal the biome owns (§5). |
| **F** | Campaign cast | One pen per patch-added animal on the biome's roster (`UtinniPatches/Patches/WildAnimals_<Biome>.xml`), so the whole roster stands in one place. |
| **N0** | Natural window | A rectangle of the fixture's own ground that the builder never touches: natural cover, density and ponds as mapgen made them. |
| **G** | Weather switch board | Every WeatherDef the biome adds, and every vanilla weather its table keeps. The builder's `--weather <def>` switch is named on the sign. Visual effects without a weather (glows, gas clouds, overlays) get a B station each. |
| **S, W, V, L, R** | Boards | S Mod Settings · W world map (the biome's world texture and any world objects) · V events and incidents (what fires and how to trigger it) · L clocks (map timers the calm world stops, and how they restart) · R set-pieces (ruins or structures that mapgen places, found on the site and pointed at). A board is a sign with no build. |
| **F** (area) | Free area | Open biome ground stocked with the biome's buildables and materials, for him to try things. It sits away from the gallery and any hazard. |

**North-star index.** Every line under `### must show` in the biome's walk file
(`design/validation_walks/RimMandrake/<Biome>.md`) maps to at least one station or board, or to a stated reason it is not a
look ("a mapgen census: the matrix's row"). COVERAGE prints this table, generated by parsing the walk file and never
hand-written. A line with no mapping fails gate PW2. The same table exists for the kickoff packet's visual bars (§1.x
*Must show*) while they are still draft.

**No orphan stations.** A station shows only content that is wired into play: content a roster, patch, recipe, research,
GenStep, incident or setting can actually put into a player's game. Content that is built but not wired, or wired but not
built, gets a COVERAGE row with `none: not wired (<item ID>)` and no station. (The lesson came from fulgurite: a station was
staged for content that never reached play, and he excised it, 5d8609cc8b.)

## 4. Layout and grid key

- **Rows run north to south in the fixed order A B C D E F.** A row letter means the same thing on every biome's map, so
  he learns the layout once. Stations are numbered 1..n continuously across the rows. Boards sit in a line along the
  gallery's south edge, and the free area sits clear of the gallery.
- **Pitch.** Each station has a fixed footprint (12x12 in v1). There are at least 4 empty cells between stations, and
  the title and sign book sit in that gap. Each station is visible as a whole at one zoom level.
- **Hazard separation.** A station that stages a hazard (fire, gas, acid, explosion) sits at least
  `hazard_gap` cells from every pen and from the free area. `hazard_gap` is set per biome from the largest scan or spread
  radius of that biome (Pyrelands: 30, because the fire-hawk scans 18 cells). The pad's ground cannot carry the hazard
  anywhere the station does not intend (Pyrelands: bare deep ash, which does not burn).
- **The whole gallery is floored with the biome's common ground**, so every station is judged on the right ground.
- **Navigation.** `--goto <n|letter|N0|F|0>` frames a station, a board, the free area or the overview, and re-sweeps
  hostiles on the way.
- **Key sheet.** `review/KEYSHEET.md` (and `Transient/<biome>_human_review/keysheet.html`) lists the rows, then every
  station in order: its full sign, then *Look for*, *Poke it* and *If you unpause*. It ends with a "This build" block
  (what verified, what was refused). The sheet repeats the save. It does not replace it.

## 5. Pen rules

Owner, 2026-10-15: *"You should put many creatures in each pen so they will have different facings to study."*

- **One species per pen.** The pen is walled and roofed with a door and floored with the biome's common ground. Flyers
  always get a roofed pen and are shown STANDING (*"do not do live testing of flyers without a human present"*).
- **Specimen matrix.** Each pen holds one specimen for every graphic the game can draw for that kind:
  every life stage with its own graphic (baby, juvenile, adult) × each sex with a distinct graphic (female, male) × every
  alternate graphic (`alternateGraphics`, xenotype or variant comps, and modExtension graphics). The builder expands
  the matrix from the def, so nobody writes it by hand. The **floor is 4 specimens**, even when the def draws one graphic.
- **All four facings show while paused.** Specimens are placed in a ring and given rotations South, East, North and West,
  so each graphic in the matrix is seen from all four sides across the pen. West is the mirrored East and is still shown,
  because a mirror defect is visible only there. The builder reads the rotations back after the spawn (gate PL2). If
  the bridge cannot set a pawn's rotation, that is a companion tool owed (`rimbridge-companion`), not a pen with one facing.
  UNMEASURED: whether today's spawn call accepts a rotation.
- **Size.** The pen interior grows with the matrix: about 2.5 cells per specimen, 10x10 minimum. A matrix over 16
  specimens splits into a main pen (adults, both sexes) and an alternates pen beside it.
- **The sign names the matrix**: "6: adult F/M, juvenile, baby, variant B ×2; four facings each". The key sheet lists which
  specimen stands where.
- **Corpses and rotted drawings** are not staged by default (they need days of sim). The pen's DO line says how to see
  them by hand.

## 6. Mechanics demos and controls

- **Every comparison has a control station** beside it (adjacent number, same row). The control's title begins with
  `CONTROL:`, and its sign says what it is a control for and the ONE thing it changes ("CONTROL: NO BEAST — same room,
  same chill, no furnace-beast").
- **Both start where the mechanic visibly works.** The control must be a working comparison, not a second copy of the
  ambient. Pyrelands: both furnace-beast rooms are chilled to 10 C, because the heat pusher only works below 24 C and
  the outdoors is about 50 C. A per-station `climate` op sets this, and the verify reads it.
- **A staged state is named for its age** ("burned 8000 ticks ago"). It is staged by the builder through the mechanic's
  own route (a real fire, a real weather), never by writing the end state, unless a sign says so.
- **What unpausing does** is written on every station ("If you unpause"), including the bad things ("the fire front can
  light this grass").

## 7. Sign format

Owner, 2026-10-15: *"I need text signs added to the savegame to tell me what to DO at each station."*

Every station and board carries the same sign in three places:

1. **In the save itself, with no agent needed:** one vanilla book (Novel) on the gap cell just north of the station's
   west corner. Its **title is the DO line**, so mousing over it shows what to do. Its **info card (press i)** holds the
   whole sign: number, name, clause, LOOK, DO, DECIDE, and "Key sheet: station n".
2. **Floating labels** from the JawaBench labeller (title, clause, then LOOK / DO / DECIDE when zoomed in), saved in a sidecar
   beside the save and re-pinned by `--labels`. They are a convenience. The book is the sign of record.
3. **The key sheet**, word for word.

Text rules:

- The title has at most 24 characters and the clause at most 56.
- LOOK names the thing to look at. DO is one imperative with the exact menu path. DECIDE is the question he answers,
  ending in "?".
- Plain words only, with no defName unless the DO needs it.
- The sign fits in 5 lines of the sign width, and the DO line fits the book title.
- A suspected weak spot goes on the sign as the DECIDE ("does young grass read as young, or just small?"), so he is
  pointed at it rather than left to find it.

## 8. Pre-walk gates (machine-checkable)

All of these run before he is told the save exists. Offline gates run in `--plan`. Live gates run in `--build` and at
`--save`. Each writes a row to `review/AUDIT.md` and to the build state JSON, and the key sheet's "This build" block
prints any row that is not PASS. A gate that cannot see answers UNMEASURED, and UNMEASURED blocks the walk the same way
FAIL does.

**Offline (`--plan`, no game):**

| id | gate | passes when |
|---|---|---|
| PW1 | site fixture | The named fixture exists, its BiomeDef is the biome's, and its fingerprint equals the live def set's. |
| PW2 | coverage | Every feature in the inventory has a station or a `none: <reason>`. Every `### must show` line in the walk file maps to a station or a reason. |
| PW3 | reachability | Every def a station names is wired into play (roster, patch, recipe, research, GenStep, incident or setting), checked against the deployed composite. An unwired def makes an orphan station: FAIL. |
| PW4 | layout | `layout_check` returns empty: every station inside the map and its own footprint, the pitch kept, no overlaps, hazards at least `hazard_gap` from pens and the free area, flyers roofed, animals penned, every station has something to verify, and every def named is known. |
| PW5 | signs | Every station and board has LOOK/DO/DECIDE within the §7 limits, and every comparison has a `CONTROL:` partner. |
| PW6 | deploy currency | `deploy_custom_mods.py` dry run shows zero pending lines for every mod in the review tier. Every DLL's `.srchash` matches. Nothing retired is still deployed (a file removed from the repo but still in the game's Mods folder is a FAIL). |
| PW7 | graphics audit | Every picture the GAME will load for every station's subjects resolves, read from the DEPLOYED Mods folders in the live load order (later mods win). This covers all facings, life stages, sexes, `alternateGraphics`, plant growth stages and random variants, leafless drawings, rotted-corpse drawings, projectiles, and every texPath inside a modExtension or comp (the gap `texture_gap_lint` cannot see). Result: 0 missing, plus a contact sheet `Transient/<biome>_review_audit_<date>/sheet.png` at true scale beside a vanilla human. |
| PW8 | defects disposed | Every PW7 defect is FIXED AND DEPLOYED (counted under PW6), or it is a row on ONE pick sheet (`art_sheet.py`, served gated) with an id, and its station's sign names the open pick. There is no third state. |
| PW9 | pen matrix | Every pen's planned specimens cover the def's matrix (§5), with at least 4 specimens and 4 rotations each. |

**Live (`--build`, `--save`):**

| id | gate | passes when |
|---|---|---|
| PL1 | stations verified | Every station verifies "as built": the terrain, things and kinds it wanted are read back from the map. |
| PL2 | pens | The specimen count and lifestage/sex/graphic of each pen match its plan, and each pawn's rotation reads back as planned. |
| PL3 | controls | Each control pair reads its declared starting condition (for example both rooms at 10 C ± 2). |
| PL4 | calm world | Hostiles 0, incident queue empty, weather Clear and locked, hour in daylight, paused, god mode on, screenshot mode off, Peaceful, not fullscreen. |
| PL5 | signs in save | The number of sign books on the map equals the number of stations plus boards, and each book's title equals its DO line. The label sidecar is written. |
| PL6 | agent look | An OS screenshot of every station is taken and read by the building agent (the L3 rung). Each one is filed as `looked: ok` or a defect, and a defect returns to PW8. |
| PL7 | save | The Saves folder is backed up first. The save stat-diff shows exactly one new or updated keeper. The owner's ModsConfig backup path is printed for restore after the walk. |

## 9. Build tool contract

**Generalize `human_review.py`; do not copy it.** Pyrelands' 1472 lines split into one generic builder and one data file
per biome.

**Extract into `src/RimMandrake/Utils/modcheck/biome_review.py`** (beside `reviewmap.py`, which already holds
`LiveBridge`, `sweep_pawns`, `label_line`, `sign_sub`, `sign_book`, `place_signs`, `write_signs` and `save_keeper`):

- The `Review` class verbs: `load`, `require_site`, `calm`, `clear`, `ticks`, `shelter`, `colonists_in`, `draft_in`,
  `build`, `plant` (with the fixed "clear only on the station's first planting" rule from L2b, 2aedbdc9b2), `pawns`,
  `put_out`, `keep_rects`, `verify_all`, `labels`, `goto`. `chill` becomes a generic `climate(station, celsius)`, and
  `burn`/`find_ruin` become biome hooks (below).
- The layout: `footprint`, `region_rect`, `_overlap`, `_dist`, and the generic half of `layout_check`, with
  `CREATURE_FIRE_GAP` generalized to `hazard_gap` and `fire_stations` to `hazard_stations`.
- The writers: `sign_of`/`sign_ops`, `keysheet`, `coverage_md`, `write_coverage`, `station_verdict`, `build_exit`,
  `ops_counts`, `read_state`/`write_state`.
- The CLI (`--plan --build --load --goto --labels --signs --signs-for --weather --clear --save --name --log`), driven
  by the biome module.
- **New:** the pen planner (def → specimen matrix → ring placement with rotations), the north-star parser (walk file →
  must-show ids), the reachability check (PW3), and the graphics audit (PW7). The audit generalizes whatever produced
  `Transient/review_graphics_audit_2026-10-15/` and closes the modExtension gap in
  `src/RimMandrake/Utils/art/texture_gap_lint.py`.

**Per biome, `src/RimMandrake/<Biome>/review/stations.py`** holds data plus small hooks only:

- `BIOME` (the defName, the short tag used in save names, the fixture name, map size, common ground def, wall stuff,
  `hazard_gap`, and the daylight hour);
- `STATIONS` (row, short, sub, look, poke, unpause, setup) and `SIGNS`;
- `BOARDS` and `BOARD_SIGNS`, the `FEATURES` inventory, `WEATHERS`;
- `hooks`: optional `stage(review, station, phase)` for biome-specific staging (Pyrelands: the burn phases),
  `find_setpiece` (Pyrelands: the ruin), and `extra_layout_checks`.

`src/RimMandrake/<Biome>/human_review.py` shrinks to a few lines that call `biome_review.main(stations)`. Pyrelands
migrates first, and its save must rebuild with the same 41/41 verify before any other biome uses the builder. GSS and
FlowWorks are not biomes and keep their own builders.

**Invariants carried over:**

- `--build` is idempotent (it clears the region first).
- `--plan` needs no game.
- Every refusal lands in the notes and the key sheet.
- Exit 0 only when every station verifies.
- The builder is excluded from `modcheck.status.mod_hash`, and `review/` is in `.hashignore`.
- An offline selftest `review/selftest_review.py` exists.
- No MapComponent or GameComponent is written, because it would end up in the save.

## 10. Naming and files

| thing | name |
|---|---|
| keeper save | `RM_<tag>_review_<YYYYMMDD>`, where `<tag>` is the biome's short tag (`pyre` for Pyrelands, kept as is) |
| site fixture | `NS_<Biome>_site_<n>_<fingerprint>_<r>` |
| per-biome data | `src/RimMandrake/<Biome>/review/stations.py` |
| generated, committed | `src/RimMandrake/<Biome>/review/{KEYSHEET.md, COVERAGE.md, AUDIT.md}` |
| read-once output | `Transient/<tag>_human_review/keysheet.html`, `Transient/<tag>_review_audit_<date>/sheet.png` |
| build state | `Transient/<tag>_review_map_state.json` (a program reads it: never cited by a doc) |
| saves backup | `D:\Luke\dev\_rmscratch\<round>\saves_backup_pre_review` before every `--save` |

The event board in v1 is **V**, not E (Pyrelands used E for both the creature row and the event board). Pyrelands keeps
its letters until it migrates to the generic builder.

## 11. Open questions for the owner (card-ready)

Each goes through the `question-card` skill. The options are real, and the recommendation comes first.

**Q1. How many animals in each pen?**
- *Every look, all four facings (recommended).* One animal for every drawing the game has (young, adult, female, male,
  each alternate), turned four ways. A species with many variants gets a second pen beside it. Complete, but some pens
  hold 12-16 animals.
- *Capped at 8 per pen.* Smaller pens and a quicker walk. Rare alternates go to one shared "alternates" pen at the end of
  the row, away from their species.
- *Adults only, four facings.* The fastest walk. Young and alternate drawings go on the art sheet instead, so they are
  never seen in the game.

**Q2. Should every biome's map use the same layout?**
- *Same rows, same letters, every biome (recommended).* A is always ground, E is always the biome's animals. You learn
  the map once, but a biome with no items still has an empty-marked row D.
- *Same order, rows a biome lacks are skipped.* Tighter maps, but the letters shift between biomes.
- *Free layout per biome.* Each map is shaped to its biome, and every map is new to you.

**Q3. Where do the art defects found before your walk go?**
- *One pick sheet before the walk, then the save (recommended).* You settle the pictures first. The walk then shows only
  the art you chose, but it costs one extra short sitting and possibly one more rebuild.
- *Into the save, as a "picks" board.* One sitting: the open picks stand in a pen beside each other in the game. Only
  options that already exist as deployable art can be shown this way.
- *On the walk's key sheet only.* Fastest, but you judge those pictures on a page, not in the game.

**Q4. Fights, bites and other action (venom, tail guns, a burrow) — how are they shown?**
- *A DO line on the pen's sign (recommended for v1).* "Draft a god-mode colonist and let it bite." Nothing extra is built,
  but you do the staging yourself.
- *An "action" row staged by the builder.* A paused moment mid-fight (projectile in the air, venom on a colonist). It
  shows more, but it is fragile to stage and costs build time.
- *Leave action to the matrix.* The save stays about looks only, and action is never judged by eye.

**Q5. What should happen if you unpause?**
- *Paused-only, and every sign says what unpausing breaks (recommended, today's rule).* Simple, but one unpause can
  spoil stations (animals turn, grass burns), and a rebuild takes about 1 minute plus a reload.
- *Safe for about a day at 3x.* Pens fed, hazards fenced, clocks off. You can watch things move, but the build costs more
  and the hazard stations must be self-contained.
- *A second save at a later moment.* The same map saved again after N hours of sim, so you can compare before and after.
  Two saves to keep current.
