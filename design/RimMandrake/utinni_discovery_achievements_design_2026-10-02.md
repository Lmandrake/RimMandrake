# Utinni discovery achievements — design pass (2026-10-02)

Item: `UTINNI_DISCOVERY_ACHIEVEMENTS_1`. DESIGN ONLY — build pause in force; nothing here is built.

## 1. Brief

Owner, typed 2026-10-02 (the whole brief, from the item): *"Make a ticket to create an achievement mod
unique to the utinni scenario that makes all of the discoverable content and unique mod capabilities
clear so you know to discover it and play with it. Doesn't give you any rewards it's just a helper for
players to have more fun. Could put options for players to add small rewards tied to them in options if
we want. But that's not the point."*

So the product is a **map of the unseen**, not a score: its job is to tell a player that a thing exists
and roughly where to look, then to light up when they have done it. Rewards are optional and off.
Constraints from the standing rules: tier grammar (`RM_`/`RSW_`/`RUT_`), superb Mod Settings, all DLCs
assumed, build pause (design only).

## 2. What already exists (read before inventing)

Searched `design/` and `src/` for achievement, codex, journal, discover and first-time mechanisms, and
every installed `About.xml` (1,412 files across the game `Mods` folder and workshop `294100`) for
achievement frameworks. The scan's sanity probe: it found 24 About.xml files mentioning "achievement", so
it can see.

**No achievement mod of ours exists.** But four pieces of discovery machinery do, and the design should
stand on them rather than beside them:

| Piece | Where | What it does | How this mod uses it |
|---|---|---|---|
| **LoreStages** | `mandrake.rm.lorestages` (`src/RimMandrake/LoreStages/`), BUILT | `GameComponent_LoreStage` + `RM_LoreStageTableDef`: a def's description/label is rewritten as a reveal ladder advances, scribed per save | the **spoiler engine**: an entry's text can be staged (riddle → hint → truth) with no new code |
| **Antiquities** | `mandrake.rut.antiquities`, BUILT | five lore stages (LANGUAGE, RELIGION, CULTURE, CARTOGRAPHY, VOICE) read out of the world urn by urn | a category of entries, and a source of "stage advanced" events |
| **Rites tab, found rites** | `mandrake.rut.rites`; `design/Jawa/salvation_rites_2026-10-01.md` §(d) | a found rite is a greyed research row ("A rite the dark keeps.") that lights when its inscription is studied | already a discovery list for one category; the achievement entry should POINT at it, not duplicate it |
| **The nine unveilings** | `design/Jawa/first_contact_chains.md` (veiled-discovery onboarding, F4) | each god introduces itself by a scripted chain; "after all nine unveil, the veiled-discovery layer retires" | nine entries; the chain's trigger is the detection hook |
| **Hidden items** | `RUT_ShipMemory_Containment` (`mandrake.rut.shipmemory`) | uses vanilla `Find.HiddenItemsManager.SetDiscovered` + `discoveryPrerequisites` to reveal buildables | proof the vanilla discovery flag is already in use; a detection source |
| **Bedazzle scorecards** | `design/Jawa/worldbuilding/biomes/*_bedazzle_review_*.md` §2 | every biome is graded on the same nine marks: unique mechanic, discoverable technology, unique resources, surprising creatures, GIANT beast, gravship touch, soundscape, weather, relationship to the gods | **the catalogue's spine** (§3): the marks are exactly "things worth discovering here" |

Engine precedent (vanilla 1.6, all DLCs): Anomaly's **entity codex** (`EntityCodexEntryDef`, discovered
entries with greyed undiscovered silhouettes) is Ludeon's own discovery journal, and Ideology's
**relic/ancient** discoveries and Odyssey's landmarks are the other reveal surfaces. None is a general
achievement system.

**External framework.** *Vanilla Achievements Expanded* (`vanillaexpanded.achievements`) is **not
installed**: it appears only as a `loadAfter` in 21 Vanilla Expanded mods. Its def shape (read from
`Vanilla Weapons Expanded` 1814383360, `1.5/Defs/Achievements/Achievements.xml`) is
`AchievementsExpanded.AchievementDef` with `tab`, `tracker Class="AchievementsExpanded.ItemCraftTracker"`
(and Research, Kill, Hediff, ... trackers), `texPath`, `points`, plus `Reward_*` defs bought with points.
VWE's `1.6/Defs/` carries no `Achievements` folder while `1.5/` does, but VAE itself **does** ship a
`1.6` folder (its GitHub repo root, checked 2026-10-02); see §5.6.

## 3. The catalogue: what counts as discoverable

**Rule: an entry is anything the player could go a whole campaign without knowing exists, that is
fun once known.** Vanilla content does not qualify; a recolour does not qualify; a mechanic that fires on
the player unasked (a raid) qualifies only for its *counter-play* ("the deep can be driven off").

### Categories

The **nine bedazzle marks are the spine**, because every biome is already graded on them and they are
exactly the list of "things worth finding here". Four cross-biome categories sit beside them for
content that belongs to no single place.

| Category | Source of truth today | Typical evidence |
|---|---|---|
| 1. Unique mechanic (per biome) | bedazzle §2 mark 1; the biome mod's comps/map components | first successful use |
| 2. Discoverable technology | mark 2; `ResearchProjectDef`s with `hiddenPrerequisites`, techprints | studied / researched |
| 3. Unique resources | mark 3; the biome's plant and animal products | first harvested |
| 4. Surprising creatures | mark 4; the biome roster (patch-added rows included) | first seen, then tamed/studied |
| 5. Giant beast | mark 5 | first seen; survived/driven off |
| 6. Gravship touch | mark 6; `RM_SeabedLayer`, ground refusal | landed / launched under the condition |
| 7. Soundscape | mark 7; `soundsAmbient`, silence cues | present on the map while the cue plays (text equivalent) |
| 8. Weather | mark 8; the biome's own `WeatherDef`/`GameConditionDef` | lived through it on a home map |
| 9. The gods | mark 9; found rites (`mandrake.rut.rites`) | rite found, rite learned, rite performed |
| 10. The Nine | `first_contact_chains.md` unveilings | the chain's own completion |
| 11. Antiquities | `mandrake.rut.antiquities` stages | stage reached |
| 12. Clan crafts (cross-biome mechanics) | FlowWorks, Graffiti/SacredGraffiti, MessyConduit, Webwork, vermin breeding, Warcasket, Droidworks... | first meaningful use (not construction) |
| 13. The ship | `mandrake.rut.shipmemory`, ShipShields, gravship layers | the mod's own reveal |

### How the catalogue is generated so it cannot rot

1. **Entries are defs** (`RM_DiscoveryEntryDef`), authored **beside the content they describe**, in the
   content's own mod, never in one central list. A biome mod ships its entries in its own `Defs/`.
2. **The biome gets a `DefModExtension`** (`RM_DiscoveryMarksExtension`) mapping each of the nine marks
   to entry defNames, or to an explicit `none: <reason>`. A mark with neither is a lint failure.
3. **A coverage lint** (offline, python, beside `run_selftests.py`) reads the def dump and reports:
   biome marks with no entry and no exclusion; research projects and found-rite rows with no entry;
   entries pointing at defs that do not exist; entries with no hint text at the active spoiler level;
   entries whose trigger kind has no detector. It is the bedazzle scorecard's "built" column, made
   mechanical: a HIT mark with no entry is visible debt.
4. **Generic entries are generated, not authored**, where the def already says it: every creature on a
   biome's own roster can get an auto "first seen" entry from the roster itself (read as XML elements,
   patch-added rows included). Hand-authored entries are only for mechanics and story.
5. **Availability is computed, not assumed**: an entry whose subject def is absent (mod not loaded,
   biome not on the map) is shown as unavailable in this world, never as an unfinished task.

## 4. Worked examples

Illustrative; every defName below that is not already in `src/` is a proposal. Hint text is placeholder
wording, to be authored at a sitting. "Hint" is what the Guided level shows before discovery.

| # | Entry | Category | Hint (Guided) | Detection |
|---|---|---|---|---|
| 1 | The greatbole that will not die | 1 Greentide mechanic | "Some roots refuse a final harvest." | `RM_MapComponent_LivingRegrowth` emits on first regrowth tick the player witnessed |
| 2 | Sealing the wound | 2 technology | "A bitter oil makes wood forget how to grow." | first `RM_ToxinSealant` terrain placed on a `RUT_GreatboleHeartwood` cut |
| 3 | The sekkulaath | 5 giant (Fever Wood) | "Something under the pools is listening." | first limb or eye unfogged on a player map |
| 4 | Driving off the deep | 1 Fever Wood mechanic | "Even the deep can be made to leave." | `RM_MapComponent_TentacleWatch` reports retreat |
| 5 | Mirror pools | 1 Fever Wood mechanic | "Still water shows more than your face." | first use of a mirror pool |
| 6 | The sea floor | 6 gravship | "The ship can go lower than the shore." | gravship lands on `RM_SeabedLayer` |
| 7 | A catch that swims | 3 resource (seas) | "What you pull from the water also walks the floor." | catch a `fishTypes` species, then see its floor twin |
| 8 | Canals | 12 crafts (FlowWorks) | "Water goes where the clan tells it." | FlowWorks reports first fluid moved through a player-dug canal (not merely built) |
| 9 | A pit | 12 crafts (FlowWorks) | "Some holes are rooms." | first superdeep cell enclosed (per `PIT_SUPERDEEP_COLLAPSE_1` when built) |
| 10 | Marking the wall | 12 crafts (Graffiti) | "The clan can leave its words on the world." | first graffiti completed |
| 11 | Grubs that breed | 12 crafts (vermin) | "Even vermin have uses for a patient scavenger." | `RM_CompVerminBreeder` first brood |
| 12 | The Dark Vigil | 9 gods (Abyss) | "A rite the dark keeps." (the Rites row's own text) | the rite's inscription studied; links to the Rites tab row |
| 13 | Ozzik the Shamed | 10 the Nine | "One god loves what you make. Fear him." | the unveiling chain's completion signal |
| 14 | Cartography | 11 Antiquities | "The urns remember the shape of the land." | Antiquities stage CARTOGRAPHY reached |
| 15 | She remembers | 13 ship | "The ship has held things before." | `RUT_ShipMemory_Containment` set discovered (observed, never called by us) |
| 16 | The pilgrims' end | world (Scarlands) | "Someone walked here to die on purpose." | `RUT_ScarlandsLadder` reaches rung 5 |
| 17 | Gizka aboard | 4 creatures (RSW) | "Something is breeding in the hold." | first `GizkaStowaway` sighting |

Note on 12 and 15: rites, unveilings, Antiquities and hidden items **are their own authority**; the
achievement observes them and links to them, and never advances them.

## 5. Design questions, options and trade-offs

### 5.1 Tier placement
| Option | For | Against |
|---|---|---|
| **A. `RM_` framework + `RUT_` content** (`mandrake.rm.discoveries` + `mandrake.rut.atlas`) | free biome mods ship their own entries so a non-campaign player gets the atlas too; matches LoreStages/Ninefold precedent (engine RM, content RUT) | two mods; the RM engine must stay faith-free and campaign-free |
| B. `RUT_`-only | fastest; can name gods and rites freely | the brief says "unique mod capabilities", most of which live in `RM_` mods; a free-mod player gets nothing |
| C. Build on VAE | trackers, UI and save code exist | see 5.6 |

Recommend **A**. The nine-mark taxonomy, god/rite/Antiquities entries and the clan's voice live in RUT;
the schema, tracking, UI, lint and settings live in RM. RSW entries only for Star Wars content reused
outside Utinni.

### 5.2 Knowing an entry exists without being spoiled
Three states per entry, independent (from the consult): **awareness** (unlisted, hinted, identified),
**evidence** (encountered, studied), **participation** (untried, used). Spoiler levels pick what is shown
before discovery:

| Level | Before discovery the player sees | Cost |
|---|---|---|
| Mystery | a count per category ("4 things unfound in the Fever Wood") and riddle text only after a rumour (urn, trader, proximity) | capabilities can be missed entirely, defeating the brief |
| **Guided** (recommended default) | every entry as a one-line hint in plain words, no icon, no name | mild spoil that something exists, which is the point |
| Explicit | name, icon and how to trigger it | a checklist; mystery gone |

Riddle and hint text is **staged by LoreStages**, so the same def can say riddle, then hint, then truth.
Spoiler protection must cover the whole surface: title, icon, tooltip, search, links.
**Proximity** upgrades a hint to "identified" when the subject is on a player map and unfogged, which is
how a creature or giant becomes visible without a letter.

### 5.3 Detection
| Option | For | Against |
|---|---|---|
| **Direct emit from our own mechanics** (`RM_Discoveries.Notify("entry")`) | exact, cheap, attributes a real success | every mechanic owes one line; a soft dependency (reflection or a tiny shared static) so mods load without the framework |
| Harmony on vanilla success points (research done, ritual done, techprint applied, landing) | covers vanilla-shaped content | brittle across updates; must hook success, not job start |
| Polling (`GameComponent` every ~2,000 ticks, staggered) | catches durable states (stage reached, thing exists, terrain placed) and backfills old saves | cannot see transient events |

Recommend **all three, by kind**: defs declare a trigger kind; our mechanics emit; Harmony covers vanilla
events; polling reconciles durable facts on load and periodically. Save safety: a `GameComponent`
scribes entry IDs (strings) to states; unknown IDs are kept as archived, never dropped; repeated
notifications are idempotent; adding the mod mid-game backfills only durable facts.

### 5.4 UI
| Surface | Use |
|---|---|
| **Main tab** ("Atlas", `MainButtonDef`) | biome pages with the nine marks, plus the cross-biome pages; filters; pins ("things to try here") |
| Toast (`Messages.Message`) | ordinary discoveries; quiet |
| Letter | reserved; most big moments already have their own letter (unveilings, rites), so the atlas adds none there |
| Inspect-pane link | "In the Atlas" on an entry's subject once identified |
| World-map tile tooltip | "3 unfound here" on a visited biome (Guided and Explicit only) |

### 5.5 Mod Settings
- Spoiler level: Mystery / Guided / Explicit (default Guided).
- Per-category off (each of the 13 categories), and hide completed.
- Notifications: toast / silent.
- **Lore rewards** (§5.7): off / Jawa lore / Jawa and world lore.
- **Small rewards**: off by default; when on, future discoveries only, no backlog grant.
- Counters (x of y) on/off; a counter is a spoiler at Mystery.

### 5.6 VAE or our own
The consult reports that VAE now ships 1.6; **verified 2026-10-02**: the GitHub repo
`Vanilla-Expanded/VanillaAchievementsExpanded` root lists a `1.6` folder. It is still not installed here.
VAE is a points-and-cards system: trackers for vanilla actions, a points shop for rewards. What this
brief needs (staged hints, LoreStages text, links to existing authorities, our own mechanics' success
signals, lore leaves) is mostly what VAE does not do, and its custom-tracker contract is officially
unsupported since 1.5 (consult, citing the maintainer). **Recommend our own small framework**, with an
optional later bridge that mirrors our entries into VAE cards for players who run it.

### 5.7 Lore rewards (owner addition, typed 2026-10-02)
Owner: *"Add to the design pass that achievements can be rewarded with Jawa lore or world lore should
the player seek that."*

**What it is.** An unlocked entry may carry a **lore leaf**: a short in-world fragment (a clan saying, a
trader's tale, an urn's line, a Salvation teaching, a fact about Ash'karr) that the player reads only if
they opted in. It deepens the thing just discovered, so the reward is understanding, not loot.

**Where the text comes from.**
- **The canon is `design/Jawa/reconciled_lore/`** (13 files, ~1,400 lines: world, deep history, factions,
  the clan, the ship, droids). It is **authors' knowledge**, so leaves are **written from** it, never
  quoted from it.
- **R25 binds every leaf** (`_freeze_rulings_2026-09-07.md`): *"The player may INFER it; the player is
  never TOLD it."* A leaf speaks in a voice inside the world (a Jawa, a trader, an inscription) and may
  be wrong, partial or devout; it never states the Assailants' authorship, the Rakata or the Cathedral's
  nature. The Scarlands ladder (`RUT_ScarlandsLadder`) is the model: its rungs name a place's story,
  and the truths come only as the Ancients' own words in quest text.
- **Ladder-gated depth.** A leaf may name a LoreStages ladder and rung (or an Antiquities stage); it is
  withheld (shown as "the clan does not yet understand this") until the story reaches that rung, so an
  achievement can never leak ahead of the campaign.
- **No lore text exists yet.** Like the Scarlands ladder's placeholders, leaves are authored at a
  sitting; the text-lore census (`design/Jawa/text_lore_load_report.md`) is where that debt is counted.

**How it is shown and kept.** On unlock (lore on), the toast says "A memory was kept"; the entry's card
gains the leaf. All kept leaves gather on an Atlas page, **"The Telling"**, grouped by theme (the clan,
the gods, the world, the ship, the old ones), ordered by the canon's own sequence, not by unlock order,
so the collection reads as a growing book with visible gaps. Scribed per save in the same
`GameComponent`.

**Gating.** Mod Settings: Lore rewards Off / Jawa lore / Jawa and world lore, chosen once; a one-time
ask on the first unlock if still at default (§8 Q4). Switching it on later reveals leaves for entries
already unlocked (lore is not a balance reward, so backlog is fine here, unlike material rewards).

### 5.8 How new content registers itself
Every new feature's mod ships its `RM_DiscoveryEntryDef`(s) and, for a biome, its marks extension; the
coverage lint fails a feature with neither an entry nor an exclusion. Add one line to the biome sitting
template: *"Atlas entries: which marks, what hint, what evidence."* A biome is not finished until its
atlas row is.

## 6. GPT consult

One consult, run alone, `gpt_consult.py -m gpt-6.1-sol --effort high`, 2026-10-02; full answer saved at
`design/RimMandrake/utinni_discovery_achievements_gpt_consult_2026-10-02.md`. Subject guard held: the
answer opens "SUBJECT: Utinni discovery achievements" and is about this subject throughout. (The lore
addition arrived after the consult ran; §5.7 is BENCH's design, not GPT's.)

Its five ideas:
1. **Scavenger's Atlas**: organized by place, the nine marks per biome. *Picked.* Risk: 225 slots
   becoming chores; marks are navigation, not quotas.
2. **Rumour net** (Outer Wilds ship log): clues link to clues. Risk: one missed source hides a capability.
3. **Field codex** (Subnautica, Hollow Knight): encounter makes a partial record, study fills it.
   Risk: a study chore bolted onto everything.
4. **Apprenticeship** (Minecraft advancements): a tree of concrete experiments. Best at "go use this",
   worst at mystery.
5. **Inquiry dossiers** (Obra Dinn): evidence toward a conclusion. Risk: a second puzzle game beside the
   unveilings; weakest fit for plain capabilities.

Taken from it: the awareness/evidence/participation split (§5.2); hook success, not job start; never
call `HiddenItemsManager.SetDiscovered` to tick a box; destinations keyed by planet layer and tile;
spoiler protection must cover icons and search; future-only material rewards; Mystery/Guided/Explicit
presets. Its correction that VAE ships 1.6 was checked and holds (§5.6).

## 7. Recommended design

**"RimUtinni: Scavenger's Atlas"** (`mandrake.rut.atlas`, `src/RimUtinni/Atlas/`) on a small engine,
**`mandrake.rm.discoveries`** (`src/RimMandrake/Discoveries/`), names proposed.

- Engine (RM): `RM_DiscoveryEntryDef`, `RM_DiscoveryMarksExtension`, `GameComponent_RM_Discoveries`
  (scribed states, backfill, idempotent notify), detectors by trigger kind, the Atlas tab, settings,
  the coverage lint. Names no faith, no campaign.
- Content (RUT): the nine-mark taxonomy and clan voice, entries for gods, rites, Antiquities, ship,
  Scarlands ladder, the lore leaves and The Telling.
- Free biome mods ship their own entries, so the atlas works in any game that runs them.
- Default: Guided, toasts, lore off until asked, small rewards off.
- First slice when the build pause lifts: one biome (the Fever Wood, most mechanics built) plus FlowWorks
  and Graffiti, to prove emit, poll and lint end to end before authoring 25 biomes of hints.
- Not built before the owner rules §8.

## 8. Final questions for the owner

**Q1. Before a player finds something, how much does the Atlas show?**
- **Guided (recommended):** every entry as a one-line plain hint, no name or picture. Players reliably
  learn things exist; the surprise of *what* stays. Costs a little mystery.
- Mystery: only counts and riddles that appear after a rumour. Most atmospheric, but players miss
  capabilities, which is what the mod is for.
- Explicit: name, picture and how-to. Nothing is missed, nothing is a surprise; it becomes a checklist.

**Q2. Where should it live?**
- **A free engine plus a campaign layer (recommended):** our free biome and craft mods carry their own
  entries, so anyone running them gets the Atlas; the gods, rites and clan voice stay campaign-only.
  Two mods to keep.
- Campaign-only: one mod, faster, but players of the free mods get nothing.
- On top of Vanilla Achievements Expanded: its tracking exists already, but it is a points-and-cards
  system, it cannot stage hints or lore, and adds a dependency we do not control.

**Q3. What does the catalogue cover?**
- **Our own content in the campaign, every tier (recommended):** biomes, creatures, crafts, gods, rites,
  ship. Manageable, and every entry is something we wrote.
- Also notable donor mods' features: more complete, but we maintain entries for mods we do not own.
- Campaign-tier content only: smallest, but leaves out most of the "unique mod capabilities".

**Q4. Lore as a reward: how does a player opt in?**
- **Ask once on the first discovery (recommended):** "Keep the clan's memories as you discover? (Jawa
  lore / Jawa and world lore / no)". Everyone learns it exists; one interruption.
- Off, found only in Mod Settings: zero interruption, but few players will ever find it.
- On by default: everyone gets the lore, including players who wanted the story kept for later.

**Q5. Optional small material rewards: ship them in the first version?**
- **Not in the first version (recommended):** keeps it a pure guide; add later if wanted.
- Ship them off by default, future discoveries only: choice from day one; each reward needs balancing
  and a save-safe hand-off.
- A points shop like VAE's: flexible, but turns discovery into earning, against your brief.

**Q6. When does an entry count as done?**
- **It depends on the thing (recommended):** creatures and weather when encountered, crafts when used
  successfully (not just built), technology and rites when studied. Means what it says; more to build.
- One rule for all (first encounter): simple, but "you built a canal" would count without water ever
  moving through it.

## Rulings — 2026-10-02 sitting (21:50 PDT; typed answers quoted, clicks recorded as "decision taken by question card")

| Q | Ruling |
|---|---|
| 1 Before discovery | Owner, typed: *"Cryptic riddles that you can click on for flip over hints. And they are arranged in a beautiful graphical display that looks like the utinni vessel."* Riddles first, a click flips each to its hint; the Atlas is a graphical layout shaped like the Utinni herself (the ship), not a list. |
| 2 Placement | Owner, typed: *"Utinni scenario only. But content is added from free tier mods too. Anything required by the scenario."* One Utinni-tier mod; its entries cover free-tier mods the scenario requires. No free-tier engine. |
| 3 Coverage | All our content (card), within the scenario's required mods. |
| 4 Lore | Owner, typed: *"It's all optional lore, no spoilers, and you can "click" through to it once you unlock it. Nothing gets in your way, ignorable if undesired."* No prompt, no setting needed: an unlocked entry offers a click-through to its lore, never pushed. |
| 5 Rewards | Optional small material rewards, off by default, in Mod Settings (card). |
| 6 Done rule | Depends on the thing: seen, used or performed per entry (card). |
