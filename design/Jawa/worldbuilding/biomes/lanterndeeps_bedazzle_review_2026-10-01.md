# Lantern Deeps: bedazzle review (grandfathered sitting, turn 1 ruled, ticketed)

Item: `LANTERNDEEPS_BEDAZZLE_SITTING_1` (BENCH). Program: `BEDAZZLE_TOP_SHAPE_PROGRAM_1`, track (a), worst-first, sitting 2.

_BENCH design pass, 2026-10-01. Second sitting of the grandfathered track, worst-first by
`grandfathered_bedazzle_scores_2026-10-01.md` (§ Lantern Deeps; sitting order row 2). The sheet
`the_lantern_deeps.md` is frozen (`BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07); its fauna was ruled
in the frozen review sheet `Transient/deeps_flora_fauna_review_2026-09-18.decisions.json`
(7 cut, 8 regen, flora kept; owner: *"Accept Lantern Deeps ruling and follow its regeneration
request."*). **Nothing ruled there is re-argued here.** Its cuts are scoped to this biome only._

Sources read, all on `origin/main`: `src/RimMandrake/LanternDeeps/` (defs, C#, `ART_JOBS.md`),
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_LanternDeeps.xml` and the `RUT_LanternDeep*` /
`RUT_Lanternstone*` patches, `src/RimStarWars/SWBestiary/.../RSW_BiomesTeamPort_Races.xml`,
`src/RimStarWars/Droidworks/Defs/ThingDefs/Heads_Droidworks.xml`,
`design/Jawa/worldbuilding/biomes/rosters/the_lantern_deeps.json` and
`lantern_deeps_repopulation_proposals.md`, the items `DEEPS_FAUNA_MECHANICS_1/_2`,
`DEEPS_FAUNA_REPOPULATION_1`, `MECHANOID_ORIGIN_CANON_1`, `KYBER_TRADE_PLOT_1`. The Deeps is a
pocket map with no worldmap route at all, so no tile count applies.

## 1. What is there: ruled vs built

### The mod is a whole cavern, and nothing lives in it on the free tier

`src/RimMandrake/LanternDeeps/` is a real build: `RM_LanternDeeps` (no worldgen route,
`generatesNaturally false`, a steady 17 °C), the pocket-map generator `RM_LanternDeepGenerator`, two
entrances scattered on ≤ −40 °C hosts (`RM_LanternDeepEmergence`, the geode mouth;
`RM_LanternDeepMineshaft`, the ruined shaft), lanternstone as rock, wall, floor, chunk, item and
four volatile glowing formations (small to huge, blast radius 1.5 to 3.9), a sowable lanternstone,
12 owned cave plants with in-play regrowth (`MapComponent_DeepFloraRegrowth`), the weather
`RM_DeepCalm` with the hum (`RUT_DeepHum`, `RM_DeepChorus`, Anomaly clips), the darkness mechanic
(`MapComponent_LanternDeepDarkness`), incident suppression, and Mod Settings. The campaign adds the
kyber, stygium and pyrinth scatters.

### Fauna, merged (inline + patch-added), read as XML elements

The free def's `<wildAnimals>` is **empty** by design (`LANTERNDEEPS_RM_MOD_BUILD_1`). All eight
residents arrive by `WildAnimals_LanternDeeps.xml`, gated on `mandrake.rsw.swbestiary`.

| def | label as shipped | bs | commonality | origin | state |
|---|---|---|---|---|---|
| `RSW_BloodropMoth` | **drinker** | 0.77 | 0.25 | Biomes! Team, regenned on owner brief | built; mechanic built, unproven live |
| `RSW_GlowSlug` | **glowbulb** | 0.4 | 0.2 | same | built |
| `RSW_BovineBeetle` | **grabber** | 4 | 0.1 | same | built; hold-and-crush built, unproven live |
| `RSW_FacetMothLarvae` | **soulchime** | 0.7 | 0.05 | same | built; stun and soothe built, unproven live |
| `RSW_Gembug` | gembug | 0.335 | 0.1 | same | built |
| `RSW_Megapleura` | megapleura | 2.4 | 0.1 | same | built |
| `RSW_MossBeetleLarvae` | moss grub | 0.7 | 0.1 | same | built |
| `RSW_ShatterjawBeetle` | shatterjaw beetle | 1.0 | 0.1 | same | built |

None of the eight is Star Wars canon. They are Biomes! Team inventions the owner remade on
2026-09-18 into the Deep's own pale-blue, yellow-blooded hydrocarbon register. Their `RSW_` prefix
is the old port's, not an IP fact.

🔴 **Finding 1: on the free tier the biome's own law does nothing.** The darkness mechanic draws a
predator to the brightest colonist by name, and the only names it knows are `RSW_BloodropMoth` and
`RSW_ShatterjawBeetle` (`DeepPredatorKindNames`). Without SWBestiary it finds neither and returns
silently. So the free Deep is an empty, silent-tempered cave: no animals, and light draws nothing.
Q11a (*"rich enough to stand alone"*) fails twice. The remedy is already ruled:
`biome_mod_architecture.md` §7 **Q12**, *invented-name `RSW_` creatures move to the RM tier per biome,
at that biome's review sitting*. This is that sitting (§4 row 0).

⚠️ **Multi-homed, noted as a review-sheet row, not evicted:** `RSW_GlowSlug` is also wired into the
Fever Wood (`WildAnimals_FeverWood.xml`, 0.5). The glowbulb's look and name were ruled for the Deeps;
the Fever Wood's sitting decides its own row (Q13's duplicate-then-regenerate is the shape if both
keep it).

### The repopulation he asked for is still waiting on him

On 2026-09-18 he cut or remade 15 of 16 animals and asked for *"more truly alien hydrocarbon-based
life forms that are utterly different than anything on the dayside... we need to repopulate this
biome's fauna significantly with surprising life forms."* `DEEPS_FAUNA_REPOPULATION_1` answered
with twelve concepts (`rosters/lantern_deeps_repopulation_proposals.md`: sipper, drifter, candler,
hush, knocker, tapper, pooler, blinker, galuush, chiller, slick, shoal). 🔴 **Finding 2.** Its keep/cut sheet was ruled to
be served *"NOW"* on 2026-09-19, and no picks were recorded until this sitting. Turn 1 admitted all
twelve (§3, §7).

### Ruled cast: the crystal life, all unbuilt

| ruled (sheet §4) | what it is | in `src/` |
|---|---|---|
| **the Lantern** | glowing colony crystal; *"the only safe light that does not draw the others"*; light now vs light later, sold | no. Every lanternstone glow counts toward the light-draw the same as a lamp |
| **the Creep** | slow accretive predator; grows over what sleeps near it | no |
| **the Cleavers** | fragment-life that moves by fracturing; the caverns' true danger | no |
| **the Chorus** | resonant masses whose hum has a psychological effect | sound only (`RM_DeepChorus`); no effect |
| ⭐ **the Shard-minds** | sentient, immobile crystals that animate the dead droids and suits | no |
| ⭐ **the mindstone** | the aware crystal; a droid mind made of it is a new race, the Kindled | `RSW_DW_Head_Mindstone` exists as a standalone Droidworks item, *"no donor pawn carries this head"*, no source anywhere |

The 2026-09-20 strange-life sheet (`Transient/lantern_deeps_strange_life_2026-09-20.decisions.json`)
proposed filing six of these next. It is **agent prefill, never reviewed** (`reviewStatus: prefill`),
so it rules nothing.

### The signature image is not on the map

🔴 **Finding 3.** The sheet's image is *"a blue lantern burning under the mountain, and a dead
miner's suit walking toward it"*, and its access ruling is *"the dead are well-equipped, and some of
them walk"*. `RM_LanternDeepGenerator`'s genSteps place rock, terrain, lanternstone, pyrinth, plants
and the exit. **No corpse, no gear, no ruin, no dead droid is ever placed in a Deep.** The mineshaft
mouth's description promises the well-provisioned dead; nothing delivers them. The legends sitting's
**Working Dead** (dead chassis that stand up and work in the mindstone galleries) is likewise
unbuilt.

### Ruled mechanics, built and unbuilt

- **Built:** persistence (pocket map), the two mouths, light-draws-predators (campaign only, see
  finding 1), deep-flora regrowth, the hum.
- **Unbuilt:** collapse with its dust-trail and sand-pile warnings and the grumble (ruled v1,
  2026-09-02; only vanilla roof collapse exists); the reconnection storm as *"a feast day"* for the
  piezo lattices; the Lantern's safe light; the mindstone's source; the cousins who talk; the
  facility trickle (`MECHANOID_ORIGIN_CANON_1` is closed as canon, not as a build).
- **Campaign, blocked elsewhere:** the kyber trade (`KYBER_TRADE_PLOT_1`, `doing`, blocked on the GM
  blackboard's live-injection flip).

### Mechanisms already in `src/` that the slate can reuse (searched before proposing)

- `RM_CompWoundLink` + `RM_HediffComp_KinMending`, `RM_CompPlantAlarm`, `RM_CompVerminBreeder`,
  `RM_SeekTargetExtension`, `RM_JobGiver_GnawTargets`, `RM_CompAquaticAmbusher`
  (`CreatureBehaviors`): the repopulation doc already maps its twelve onto these.
- The grapple, soulchime stun and drinker sacs (`DEEPS_FAUNA_MECHANICS_1/_2`), built and deployed.
- `RSW_DW_Head_Mindstone` and Droidworks assembly: the Kindled's body already exists as a recipe
  path that deliberately excludes the mindstone head, waiting for a source.
- Anomaly's shamblers and Biotech's mechanitor control: vanilla prior art for a dead body made to
  move by something else (the Shard-minds).

### Weather, sound, ship, gods

- **Weather:** `RM_DeepCalm` at 100, *"No penalties or modifiers."* Unique because there is no sky;
  inert because nothing happens.
- **Sound:** the hum and the chorus loop, built. The servo click and the shatter (§9) are not.
- **Ship:** nothing. A gravship cannot enter a pocket map.
- **Gods:** nothing. The aware mindstone is the obvious seat, and it has no source.

## 2. Scorecard

Ruled counts as HIT; built is reported beside it. Marks come from the scores doc, re-read against
the sheet and the source.

| # | Mark | Free (ruled) | Campaign (ruled) | Built today | Note |
|---|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | free: half; campaign: yes | light draws the Deep; on free it draws nothing (finding 1) |
| 2 | Discoverable technology | PARTIAL | **HIT** | sowable lanternstone; mindstone head with no source | the Kindled are ruled (campaign) but unmakeable; nothing is *learned* on free |
| 3 | Unique resources | **HIT** | **HIT** | yes | lanternstone, puffer tendrils; kyber, stygium, pyrinth |
| 4 | Surprising creatures | **HIT** | **HIT** | free 0; campaign 8 | the crystal cast is ruled and free-tier; none built |
| 5 | GIANT beast | MISS | PARTIAL | grabber, bs 4 | the galuush (bs 6) is now ruled in (§3) |
| 6 | Gravship touch | MISS | MISS | 0 | a ship cannot go down; nothing down here reaches up to it |
| 7 | Soundscape | **HIT** | **HIT** | hum + chorus | servo click and shatter unbuilt |
| 8 | Interesting weather | PARTIAL | PARTIAL | `RM_DeepCalm`, inert | collapse (ruled v1) and the storm feast day (one line) are unbuilt |
| 9 | Relationship to the gods | MISS | MISS | 0 | the aware mindstone has no god and no rite |

**Free 5 / 2 / 2 ruled (3 / 2 / 4 built). Campaign 6 / 2 / 1 ruled (4 / 3 / 2 built).**

Two HITs are thinner than they look:
- **Mark 1** on the free tier is a no-op until row 0 ports the predators.
- **Mark 4** is the best-written crystal cast on the planet with no defs: five forms and the
  mindstone, all prose.

## 3. Roster fill

### The gaps, read from the sheet and the ruled review only

| hole | why it is a hole | fill |
|---|---|---|
| The free tier has no animals | Q11a; the light-draw has no one to draw | **port the eight** (Q12, ruled; §4 row 0) |
| The repopulation he asked for | *"repopulate this biome's fauna significantly"*, 2026-09-18 | **all twelve** (ruled, turn 1) |
| No giant | grabber bs 4 is the largest; nothing ruled is giant | **the galuush** (bs 6, one per Deep, a ceiling sun that is also a methane bomb), from the twelve |
| Darkness is safe | the Deep punishes light; nothing punishes the unlit | **the hush** (an ambush predator untargetable on unlit floor), from the twelve |
| The ruled collapse has no voice | dust and sand warnings ruled; no animal hears it | **the knocker** (drums before a roof fails; tamed, a collapse alert), from the twelve |

**No new names are invented here.** The twelve already cover every hole the sheet leaves, in his
own remake register (pale blue skin, yellow hydrocarbon blood), each with one mechanic and a plain
trade. The crystal cast is ruled and needs building, not filling. All twelve are invented names,
so they belong to the free `RM_` tier, inline in `RM_LanternDeeps`.

### Ruled: all twelve, every one a hydrocarbon organism (owner, turn 1)

His words, typed: *"Both yes, both must be made hydrocarbons to survive, and yolk is now called
galuush"* · *"Love these. Also hydrocarbon."* · *"Yes all 7 and ensure hydrocarbon"*.

All twelve are admitted, free `RM_` tier, inline in `RM_LanternDeeps`, one home each. Every one is
built in his remake register: pale glowing blue skin, yellow hydrocarbon fluids (oil, wax, light
gas) in place of blood, metabolism that works at the Deep's 17 °C. The proposals doc's premises 1
to 4 (hydrocarbon biology, warm-reactive products, not food, methane as a body gas) are now
**ruled** by this answer; premise 12 (survival away from the Deep) is the build's to measure, not
to assume.

| animal | def | role (one line; full concept in `rosters/lantern_deeps_repopulation_proposals.md`) |
|---|---|---|
| **galuush** | `RM_Galuush` | *the giant* (mark 5): a roof-pinned sun, bs 6, one per Deep; lights its chamber; a chamber-sized methane charge |
| hush | `RM_Hush` | ambush predator unseen and untargetable on unlit floor |
| knocker | `RM_Knocker` | blind grazer that drums before a roof fails; tamed, a collapse alert |
| candler | `RM_Candler` | the Deep's cow, milked for a cold wax fuel that spoils when warmed |
| sipper | `RM_Sipper` | light-drinking vermin that clusters on lamps |
| drifter | `RM_Drifter` | floating methane grazer; explodes if killed by fire or spark |
| tapper | `RM_Tapper` | eats electricity; tamed, gives aurora charge back |
| pooler | `RM_Pooler` | living puddle that drapes over the hottest thing and smothers it |
| blinker | `RM_Blinker` | flashes when hurt: blinds attackers, draws every predator |
| chiller | `RM_Chiller` | pumps heat out of the room |
| slick | `RM_Slick` | sweats a flammable fuse-trail |
| shoal | `RM_Shoal` | filter-feeders sharing one circulation (`RM_CompWoundLink`) |

## 4. The slate

The sheet is frozen, so most rows are an **order of build** for ruled content. Owner turn 1: **everything at once**; every row below is ruled and ticketed (§7).

**0. Housekeeping (ruled by Q12, no card needed).** Port the eight invented residents from `RSW_`
to `RM_` defs wired inline in `RM_LanternDeeps`, carrying their regen art, labels and the built
grapple, stun and drink comps. Repoint `DeepPredatorKindNames` at the `RM_` drinker and shatterjaw.
Shrink `WildAnimals_LanternDeeps.xml` to whatever campaign-only rows remain (none today). This makes
the free tier's law fire. Size M.

| order | package | marks | reuses | size |
|---:|---|---|---|---|
| 1 | **The well-provisioned dead and the Working Dead.** A Deep genstep that places high-technology remains (exosuit corpses, cutting gear, power cells, dead droid chassis) along galleries and at shaft bottoms; near a Shard-mind (an immobile crystal building), dead chassis stand and work, and turn toward light. The signature image, built. | 1, 4 | Anomaly shambler shape, Droidworks chassis, vanilla `ThingSetMakerDef` | L |
| 2 | **The Lantern.** The one safe light: a colony crystal whose glow the darkness mechanic does not count. Harvested, it becomes ordinary lanternstone, and ordinary light. *Light now vs light later, sold.* | 1, 3 | `MapComponent_LanternDeepDarkness` (one exclusion) | M |
| 3 | **The twelve hydrocarbon animals** (§3, all ruled in), the galuush among them. | 4, 5 | the `CreatureBehaviors` comps named per row | L |
| 4 | **The Creep and the Cleavers.** The accretive predator that grows over sleepers; the fragment-life that moves by fracturing. | 4 | lanternstone formations, `RM_CompVerminBreeder` | L |
| 5 | **The sky through the rock.** A Deep `GameCondition` when the aurora storms overhead: the lattices wake, lanternstone brightens, the Chorus rises, the Cleavers run. And the ruled collapse with its dust trails, sand piles and grumble. | 8 | Nightside's reconnection storm (ruled, surface), vanilla roof collapse | M |
| 6 | **The mindstone and the cousins** (campaign). A mindstone gallery the Shard-minds keep; the mindstone becomes findable here and only here, which makes `RSW_DW_Head_Mindstone` and the Kindled's first making reachable. Canon from `MECHANOID_ORIGIN_CANON_1`. | 2, 9 | Droidworks assembly | L |
| 7 | **Orun-Ghal, the inhabitant** (§5, revised by the owner). | 5, 1 | row 1's Working Dead, the Shard-minds | L |
| 8 | **The Answering** (§6, campaign rite). | 9 | `mandrake.rut.rites` found-rites row | M |
| 9 | **Art commission.** The twelve animals, Lantern, Creep, Cleavers, Chorus masses, Shard-minds, mindstone, the Working Dead's chassis poses, Orun-Ghal. Checked against `artpipe/done/` first: none existed. | all | artpipe | — |

Row 0 is the one ordering constraint: the animals' `RM_` names must exist before the darkness
mechanic and the twelve are wired against them.

## 5. GPT consult: five ideas

Consult: `Transient/bedazzle_gpt_enrich_2026-10-01/lanterndeeps.md` (prompt beside it), run
2026-10-01 under the standing rule: exactly five ideas, each different from the others and from
every other biome's signature (the prompt lists them all, Nightside Ice's new rulings included), with
research on other games and RimWorld mods cited. The prompt also listed the ruled crystal cast and
the twelve unruled repopulation concepts as off-limits, and barred darkness-gated rites (the
Abyss's). Model `gpt-5.6-sol`, via `codex exec`.

Of GPT's five, the owner took two, both changed:

- **Orun-Ghal, revised (ruled).** His words, typed: *"I like the mining suit that's alive despite
  the skeleton within it. But it might not just mine as when animated it is controlled by the
  sentient crystals. Instead it becomes an inhabitant on the map to study and befriend. I don't
  think the crystals are too keen mining."* So: a huge dead mining exoframe, its miner's skeleton
  still inside, worn and moved by the Shard-minds. **It does not mine and cuts no tunnels.** It lives
  on the Deep's map as an inhabitant: it walks its rounds, keeps near the Lantern, and can be
  **studied** (what the crystals are, what they want) and **befriended** over visits. Never a boss,
  never a worker. Large build; drawn huge on an ordinary pawn footprint, not a multi-cell pawn.
- **Zizzik's Nine Faults, redesigned and ruled elsewhere:** `design/Jawa/nine_faults_permanent_rite_2026-10-01.md`
  (register B8), build `NINEFOLD_FAVOUR_ODDS_BUILD_1`. Its inscription is found here (a dead droid
  with nine wires crossed).

The keel hoist became a campaign-wide device: `SHIP_CARGO_HOIST_DESIGN_1`, built as
`HOIST_SHIP_PART_BUILD_1`, which uses a Deep mouth as its test site. The other GPT ideas were not
taken; the consult file keeps the record.

## 6. Discoverable rites

Per `design/Jawa/salvation_rites_2026-10-01.md` (e): found at a site with a reason to be there,
learned through the Rites tab's found-rites row (`mandrake.rut.rites`), performable anywhere after.
Campaign tier. Owner turn 1 kept **The Answering** (Ohm). **Neither rite is gated on darkness**: the Abyss's four own that gate, and a dark rite here
would be the same rite in a second cave. God balance after the Nightside Ice: Oomo 4 (overfed), Ohm 3.

**Not taken: a rite before the aware mindstone in the dark** (the scores doc's seed). It is the Dark
Vigil with a stone in it. **Not taken: Rekko and the dead's gear.** The Wasteland's Inherited Wreck
already inherits a failed expedition's wreck.

### R1. The Answering, for Ohm: settlement (RULED-KEPT, owner turn 1)

- **Grounding:** Ohm is sentience in machinery and *"wants his droid servants back"*; displeased by
  *"droids lost"* (§2.0b ②). The Deeps hold the wild cousins of machine minds, and living droids
  freeze near mindstone.
- **Found:** a Working Dead chassis that has scratched the same short line into the gallery wall
  over and over: the cousins' terms, half-legible.
- **Asks:** a colony droid stands at the edge of a mindstone's (or Shard-mind's) sight for as long as
  it will bear, while the organiser speaks the clan's terms: its droids kept running, never wiped,
  never left broken. Needs a mindstone or Shard-mind in line of sight and a colony droid present.
  Lit is fine.
- **Outcomes:** Poor, the droid stops and must be carried out (it restarts outside). Fair, a
  settlement entry for Ohm. Good, plus the droid's log holds one line it did not write (a lore rung
  toward the cousins' voice). Excellent, plus the line names where the next mindstone lies on this
  Deep, and it is there.
- **Readable sign:** the stopped droid; the written log line on its inspect pane; the wall line.
- **Collision check:** Ohm's other rites feed him (the Engine Hour, the Deserter's Welcome) or
  console him (the Last Track). This is his first settlement: terms agreed, not a machine fed.

### Zizzik's Nine Faults (ruled, specced elsewhere)

Found here; designed and ruled in `design/Jawa/nine_faults_permanent_rite_2026-10-01.md`, built by
`NINEFOLD_FAVOUR_ODDS_BUILD_1`. Not ticketed by this sitting.

Tally: Ohm 3 → 4 (his first settlement). No god above four.

## 7. Turn 1 rulings (owner, 2026-10-01) and ticket-out

| Card item | Ruling | Ticket |
|---|---|---|
| 1. Build first | **Everything at once.** Slate rows 0 to 9 all go. | Decision taken by question card. One FOUNDRY item per package, below. |
| 2. Animals | **All twelve**, every one a hydrocarbon organism that survives the Deep; the yolk is renamed **galuush** (typed, quoted in §3). | `LANTERNDEEPS_HYDROCARBON_FAUNA_BUILD_1` |
| 3. New marks | **Orun-Ghal only, revised**: an inhabitant to study and befriend, crystal-controlled, not a miner (typed, quoted in §5). The keel hoist went to `SHIP_CARGO_HOIST_DESIGN_1`. | `LANTERNDEEPS_ORUN_GHAL_BUILD_1` |
| 4. Rites | **The Answering** (Ohm), added to register B8. Nine Faults kept and redesigned elsewhere. | `LANTERNDEEPS_ANSWERING_RITE_BUILD_1` |

FOUNDRY items, each `--caused-by LANTERNDEEPS_BEDAZZLE_SITTING_1`:

| slate row | item |
|---:|---|
| 0 | `LANTERNDEEPS_FAUNA_TIER_PORT_BUILD_1` (Q12 port of the eight; darkness predators repointed) |
| 1 | `LANTERNDEEPS_WORKING_DEAD_BUILD_1` (the well-provisioned dead, the Working Dead, the Shard-minds) |
| 2 | `LANTERNDEEPS_LANTERN_LIGHT_BUILD_1` |
| 3 | `LANTERNDEEPS_HYDROCARBON_FAUNA_BUILD_1` |
| 4 | `LANTERNDEEPS_CREEP_CLEAVERS_BUILD_1` |
| 5 | `LANTERNDEEPS_AURORA_COLLAPSE_BUILD_1` |
| 6 | `LANTERNDEEPS_MINDSTONE_GALLERY_BUILD_1` |
| 7 | `LANTERNDEEPS_ORUN_GHAL_BUILD_1` |
| 8 | `LANTERNDEEPS_ANSWERING_RITE_BUILD_1` |
| 9 | art: `infrastructure/artpipe/art_lists/lanterndeeps_bedazzle_cast.csv` |
