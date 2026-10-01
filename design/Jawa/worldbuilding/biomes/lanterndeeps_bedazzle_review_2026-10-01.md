# Lantern Deeps: bedazzle review (grandfathered sitting, movements 1-2)

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
hush, knocker, tapper, pooler, blinker, yolk, chiller, slick, shoal). 🔴 **Finding 2.** Its keep/cut sheet was ruled to
be served *"NOW"* on 2026-09-19. **No picks were ever recorded.** The item is still `proposed`;
none of the twelve names occurs in `src/`. The §3 roster fill starts from these twelve and invents
only what they leave open.

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
| 5 | GIANT beast | MISS | PARTIAL | grabber, bs 4 | nothing ruled is giant; the yolk (bs 6) waits in the unruled twelve |
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
| The repopulation he asked for | *"repopulate this biome's fauna significantly"*, 2026-09-18 | **his picks from the twelve** (card Q2) |
| No giant | grabber bs 4 is the largest; nothing ruled is giant | **the yolk** (bs 6, one per Deep, a ceiling sun that is also a methane bomb), from the twelve |
| Darkness is safe | the Deep punishes light; nothing punishes the unlit | **the hush** (an ambush predator untargetable on unlit floor), from the twelve |
| The ruled collapse has no voice | dust and sand warnings ruled; no animal hears it | **the knocker** (drums before a roof fails; tamed, a collapse alert), from the twelve |

**No new names are invented here.** The twelve already cover every hole the sheet leaves, in his
own remake register (pale blue skin, yellow hydrocarbon blood), each with one mechanic and a plain
trade. The crystal cast is ruled and needs building, not filling. All twelve are invented names,
so they belong to the free `RM_` tier, inline in `RM_LanternDeeps`.

### BENCH's recommended five (he may take any, all, or none)

1. **yolk** (`RM_Yolk`), *mark 5.* A roof-pinned sun, bs 6, at most one per Deep. Lights its whole
   chamber and is a chamber-sized methane charge: killed cold, a fortune in fuel; one spark, and
   the room comes down. XML (`CompGlower` + `CompExplosive`). Its glow counts toward the light-draw,
   so a yolk chamber is always hunted ground.
2. **hush** (`RM_Hush`), *mark 4.* Ambush predator of the unlit fungal floor, 1-2 per map; cannot be
   seen or targeted on an unlit cell. *Your lamp makes it visible; your lamp is the beacon.* The
   other half of the light law. Small C# on `RM_CompAquaticAmbusher`.
3. **knocker** (`RM_Knocker`), *mark 8 support.* Blind tunnel grazer that drums before a roof fails;
   tamed, a collapse alert with the cells marked. Gives the ruled collapse its readable sign.
4. **candler** (`RM_Candler`), *mark 3.* The Deep's cow: milked for cold wax, a fuel that spoils and
   ignites when warm. The Deep's economy on legs. XML only.
5. **sipper** (`RM_Sipper`), *mark 4.* Light-drinking vermin that clusters on lamps and shrinks their
   radius: a smaller beacon and fewer predators, at the cost of seeing less. Bottom of every chain.

The other seven (drifter, tapper, pooler, blinker, chiller, slick, shoal) stay on the table. The
proposals doc's twelve "invented premises" (hydrocarbon animals are not food; warm ruins their
products; tamed Deep fauna may die above −40 °C) are rulings that come with the picks, not before.

## 4. The slate

The sheet is frozen, so most rows are an **order of build** for ruled content. Only the
repopulation picks (§3) and the new marks (§5, §6) need him.

**0. Housekeeping (ruled by Q12, no card needed).** Port the eight invented residents from `RSW_`
to `RM_` defs wired inline in `RM_LanternDeeps`, carrying their regen art, labels and the built
grapple, stun and drink comps. Repoint `DeepPredatorKindNames` at the `RM_` drinker and shatterjaw.
Shrink `WildAnimals_LanternDeeps.xml` to whatever campaign-only rows remain (none today). This makes
the free tier's law fire. Size M.

| order | package | marks | reuses | size |
|---:|---|---|---|---|
| 1 | **The well-provisioned dead and the Working Dead.** A Deep genstep that places high-technology remains (exosuit corpses, cutting gear, power cells, dead droid chassis) along galleries and at shaft bottoms; near a Shard-mind (an immobile crystal building), dead chassis stand and work, and turn toward light. The signature image, built. | 1, 4 | Anomaly shambler shape, Droidworks chassis, vanilla `ThingSetMakerDef` | L |
| 2 | **The Lantern.** The one safe light: a colony crystal whose glow the darkness mechanic does not count. Harvested, it becomes ordinary lanternstone, and ordinary light. *Light now vs light later, sold.* | 1, 3 | `MapComponent_LanternDeepDarkness` (one exclusion) | M |
| 3 | **The repopulation picks** (card Q2). | 4, 5 | the `CreatureBehaviors` comps named per row | M to L |
| 4 | **The Creep and the Cleavers.** The accretive predator that grows over sleepers; the fragment-life that moves by fracturing. | 4 | lanternstone formations, `RM_CompVerminBreeder` | L |
| 5 | **The sky through the rock.** A Deep `GameCondition` when the aurora storms overhead: the lattices wake, lanternstone brightens, the Chorus rises, the Cleavers run. And the ruled collapse with its dust trails, sand piles and grumble. | 8 | Nightside's reconnection storm (ruled, surface), vanilla roof collapse | M |
| 6 | **The mindstone and the cousins** (campaign). A mindstone gallery the Shard-minds keep; the mindstone becomes findable here and only here, which makes `RSW_DW_Head_Mindstone` and the Kindled's first making reachable. Canon from `MECHANOID_ORIGIN_CANON_1`. | 2, 9 | Droidworks assembly | L |
| 7 | **Art commission.** Lantern, Creep, Cleavers, Chorus masses, Shard-minds, mindstone, the Working Dead's chassis poses, his picks from the twelve. Check `artpipe/done/` first. | all | artpipe | — |

Recommended: **0 and 1 together first.** Row 0 is ruled and makes the free Deep alive; row 1 is the
sheet's own image and has been missing since the sheet was written. The Lantern (2) is the cheapest
second: one exclusion in a component that already exists.

## 5. GPT consult: five ideas

Consult: `Transient/bedazzle_gpt_enrich_2026-10-01/lanterndeeps.md` (prompt beside it), run
2026-10-01 under the standing rule: exactly five ideas, each different from the others and from
every other biome's signature (the prompt lists them all, Nightside Ice's new rulings included), with
research on other games and RimWorld mods cited. The prompt also listed the ruled crystal cast and
the twelve unruled repopulation concepts as off-limits, and barred darkness-gated rites (the
Abyss's). Model `gpt-5.6-sol`, via `codex exec`.

GPT's own check lines: verbs *demonstrate, hoist, baffle, contract, miswire*; systems *production
pedagogy, cross-map gravship logistics, acoustic room weather, persistent giant diplomacy, Ideology
ritual.*

| # | GPT's idea (faithful summary) | marks | GPT cites | BENCH judgement on uniqueness |
|---|---|---|---|---|
| 1 | **Ithrix, the Bench That Remembers.** A mindstone gallery's stress-lines unlock a research row. At an Ithrix bench a skilled crafter demonstrates one recipe into a lanternstone plate; afterwards lesser workers can make that recipe at a capped skill and quality until the plate cleaves. Free, M. | 2 | Caves of Qud tinkering, Dwarf Fortress strange moods | **Unique, and the cleanest mark 2 on offer.** Piezo crystal that keeps a gesture is the sheet's physics (*"stress makes voltage"*) put to work, and it is free-tier with no kyber. Not Contagion's draftprints (those copy bodies). Risk: the owner passed on a learned-tech piece at the Nightside Ice; this one is cheaper and stays in its biome's material. |
| 2 | **The Veyrline Keel Hoist.** A gravship parked over a Deep mouth anchors a cable; a powered capstan below winches sealed cargo cages up the shaft. The ship cannot launch while tethered. Free, M. | 6 | ONI interplanetary launcher, Anomaly pit gate | **Unique mechanism, thin need.** It is the only idea that touches the ship from underground, and the tether-locks-launch cost is honest. But pawns already carry things through a pocket-map portal, so the problem it solves is small. A mark 6 answer that exists for the mark. |
| 3 | **Nhal, the Standing Note.** A condition in which the chorus resolves into one note: room shape, open doors and placed baffles make quiet nodes and violent antinodes. Lanternstone grows fast but shatters easily at antinodes; mining at a node is slow and safe. Free, M. | 8 | ONI room overlay, The Long Dark aurora | **Unique, and it makes the inert calm matter.** It grows straight from *"a lattice talks by singing"* and gives the Chorus a mechanical body. Not the Rust Cathedral's hum (that answers behaviour; this is geometry). Risk: a live interference field is real engineering, and legibility rests on the floor grit reading clearly. |
| 4 | **Orun-Ghal, the Last Shiftboss.** A huge mining exoframe, its dead operator still inside, worn by a Shard-mind, walks toward the nearest Lantern. It offers work through the suit's cracked terminal: repair a system, earn a warrant, paint a route, and it cuts the tunnel, then kneels by the Lantern again. Free, L. | 5 (and 1, 4) | Dwarf Fortress forgotten beasts, Kenshi leviathans, VFE Mechanoids | **Unique, and the best fit to the sheet on the planet:** it is the signature image (*"a dead miner's suit walking toward"* the lantern) made giant, and it is the Shard-minds' first body. Not the Forge's giant-on-the-clock. BENCH would cut GPT's five-cell footprint to a huge render on an ordinary pawn (multi-cell pawns are a pathing rewrite), which keeps it L, not XL. |
| 5 | **Zizzik's Nine Faults.** A found inscription teaches a rite: worshippers miswire one healthy machine into a controlled breakdown; quality banks "vented faults" that redirect later breakdowns into that vessel. Campaign, M. | 9 | Ideology rituals, Against the Storm blightrot | **Unique, a first venting for Zizzik, and fully lit** (clear of the Abyss). But the redirect is a granted power, which the rites law forbids (*"no rite grants a power"*). Kept in §6 as R2 with the outcome trimmed to the law. |

GPT's own build-first ranking: Ithrix, then Nhal. BENCH's: **Orun-Ghal first** (it builds the
sheet's own image and the Shard-minds at once), then Ithrix.

## 6. Discoverable rites

Per `design/Jawa/salvation_rites_2026-10-01.md` (e): found at a site with a reason to be there,
learned through the Rites tab's found-rites row (`mandrake.rut.rites`), performable anywhere after.
Campaign tier. **None is gated on darkness**: the Abyss's four own that gate, and a dark rite here
would be the same rite in a second cave. God balance after the Nightside Ice: Oomo 4 (overfed, gets
nothing), Mob'Unloo 3, Ishko 3 (fed only), Ohm 3, Zizzik 3. No kind repeats inside this biome.

**Not taken: a rite before the aware mindstone in the dark** (the scores doc's seed). It is the Dark
Vigil with a stone in it. **Not taken: Rekko and the dead's gear.** The Wasteland's Inherited Wreck
already inherits a failed expedition's wreck.

### R1. The Answering, for Ohm: settlement

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

### R2. Zizzik's Nine Faults, for Zizzik: venting (GPT idea 5, trimmed)

- **Grounding:** Zizzik is *"the coming-apart of minds"* and the wrong spark; in the Deeps a droid
  that lingers comes out mind-wiped.
- **Found:** a dead droid at a gallery mouth, its panel open, nine wires crossed by its own hand: a
  machine that chose its own fault before the stone could take its mind.
- **Asks:** worshippers surround one healthy, powered machine of real value and miswire it, nine
  faults in sequence, into a controlled breakdown in front of everyone.
- **Outcomes:** Poor, the machine burns (a real fire, a real loss). Fair, the breakdown holds;
  Zizzik's meter vents a step. Good, two steps, and the vessel stays as a fault-board others pass
  ("we gave him his spark"). Excellent, plus an art tale. **Trimmed from GPT:** no banked charges and
  no redirected breakdowns; an outcome is a meter step and an ordinary thing.
- **Readable sign:** nine bulbs fail in sequence; the broken vessel stays where it stood.
- **Collision check:** Zizzik is warded (the Kept Mistake), starved (the Capping) and settled (the
  Calling-Pyre, the controlled waking). Never vented. The Unburdening destroys wealth to vent Ozzik's
  pride; this breaks one working machine to let out a spark.

### R3. The Lantern Toll, for Mob'Unloo: warding

- **Grounding:** *"no gift without a counter-gift"* (§2.0b ④); the sheet's Lantern is light as an
  economy: *"light now against light later, sold"*. The Deep eats light; a clan that pays first is
  owed safe passage.
- **Found:** a ring of spent lamp cells at a mineshaft bottom, counted and laid in rows, left by the
  one expedition that came back up.
- **Asks:** before a descent, the organiser counts out light (lamp fuel, power cells or cut
  lanternstone) at the mouth, priced aloud, and leaves it there. Quality from value and the count's
  care.
- **Outcomes:** Poor, the toll is short (the ledger says by how much). Fair, paid (a ledger entry).
  Good, the descent's light exposure starts at zero and the first draw comes late (one visit). Excellent,
  plus Mob'Unloo warding sized by value.
- **Readable sign:** the toll stays at the mouth, lit, until the party returns; its hover names the
  sum.
- **Collision check:** the Blind Offering (Abyss) leaves an item in the dark for an unseen taker; the
  Cold Ledger pays a dead man's debt. This prices a passage in advance, in light. New kind for him.

Tally if all three are admitted: Ohm 3 → 4, Zizzik 3 → 4, Mob'Unloo 3 → 4. No god above four.

## 7. Owner turn-1 card (DRAFT, for BENCH to put)

Four questions, plain words. Headers are 12 characters or fewer, for `AskUserQuestion`.

**Q1 · header "Build first" · What should FOUNDRY build first for the Lantern Deeps?**
- **The walking dead and the dead's gear (recommended).** Fill the caverns with the
  well-equipped dead the sheet promises: exosuit corpses, cutting gear, power cells, dead droids.
  Near an aware crystal, the dead droids stand up and work, and turn toward your light. Big build.
  *Why: it is the biome's own picture, and today no Deep has a single corpse in it.*
- **The safe light first.** The Lantern: one crystal whose light does not draw the cave's hunters.
  Medium build, small and quick to see.
- **New animals first.** Your picks from Q2. Medium to large.
- **Commission everything at once.** Every ruled piece in one order. Largest and slowest to see.

(Either way, the eight animals you remade on 2026-09-18 move into the free mod under our own
names, already ruled. Today the free Deep has no animals at all, so its "light draws hunters" rule
draws nothing.)

**Q2 · header "New animals" · Which of the twelve new Deep animals do you want? (pick any)**
You asked on 2026-09-18 to repopulate the Deeps with alien, oil-blooded life. Twelve were proposed
and are still waiting. BENCH recommends five:
- **Yolk (the giant, recommended).** A huge glowing sac stuck to a cavern ceiling, one per Deep. It
  lights a whole chamber and is full of gas: kill it cold for a fortune in fuel; one spark and the
  room comes down.
- **Hush (recommended).** A predator you cannot see or shoot on unlit ground. Your lamp reveals it,
  and your lamp is what draws everything else. *Why: today darkness is perfectly safe.*
- **Knocker (recommended).** A blind grazer that drums before a roof falls; tamed, it warns you
  of cave-ins.
- **Candler (recommended).** The Deep's cow, milked for a cold wax that burns as fuel and spoils if
  warmed.
- **Sipper (recommended).** Tiny pests that cluster on your lamps and drink their light: fewer
  hunters drawn, but you see less.
- **All twelve** (adds drifter, tapper, pooler, blinker, chiller, slick, shoal; one line each in
  `rosters/lantern_deeps_repopulation_proposals.md`).

**Q3 · header "New marks" · Which of these new pieces do you want? (pick any)**
- **Orun-Ghal, the giant (recommended).** A huge dead mining suit, its miner still inside, walked
  by an aware crystal. It does not attack: repair it and it will cut a tunnel where you paint one,
  then go back to kneel by its lantern. *Why: it is your sheet's picture of a dead miner's suit
  walking toward a lantern, made into the Deep's giant.* Large build.
- **Ithrix, learned tech (recommended).** A crystal bench that remembers one recipe your best
  crafter shows it; weaker hands can then make it, a little worse, until the crystal cracks.
  Medium build.
- **The Standing Note (cave weather).** Sometimes the hum locks into one note; room shapes and
  baffles you place decide where crystal grows fast and shatters easily, and where it is safe to mine.
  Medium build.
- **The Keel Hoist (ship).** Your parked ship anchors a cable down a cave mouth and winches heavy
  cargo up; it cannot take off until reeled in. Medium build; BENCH thinks the need is small.

**Q4 · header "Rites" · Which rites should the Deeps teach the Salvation? (pick any)**
- **The Answering (Ohm, recommended).** A droid stands before an aware crystal while the clan
  speaks its terms: its droids kept running, never wiped. *Why: Ohm's first agreement rather than
  another feeding.*
- **Zizzik's Nine Faults (Zizzik).** Deliberately break one good machine in front of everyone to
  let the bad-luck god's spark out where you chose.
- **The Lantern Toll (Mob'Unloo).** Pay the cave in light at its mouth before going down; the first
  hunters come later.
- **None for now.**
