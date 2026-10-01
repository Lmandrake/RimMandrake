You are a senior game designer consulting on a RimWorld mod campaign. The owner wants recommendations to ENRICH one biome that has already been through a design sitting. Be concrete, vivid and buildable in RimWorld 1.6 (XML defs, C# comps, Harmony, incidents, map components, weather, sounds).

BIOME: The Warscar

Standing rules of this project (binding on every recommendation):
- RimWorld 1.6 with ALL five DLCs assumed present; a Star Wars (old Tatooine / Jawa scavenger clan) campaign on one hand-made fixed planet. No worldgen, no alternative planets.
- Each animal lives in ONE biome unless there is an in-game reason (migration, life stage).
- Invented exotic names are fine; genuine Star Wars canon goes in a separate Star Wars layer.
- Heat is ONE planet-wide kind riding vanilla heatstroke; biomes differ by heat kind (overhead sun, low sun, ambient steam/volcanic).
- Animals or pawns must never vanish without a readable sign of what happened.
- If it flies in the fiction, it flies in the game.
- Every mod ships real Mod Settings.
- A biome's ideas must NOT echo another biome's signature; each biome has its own voice.
- The "bedazzle" bar is nine marks: unique mechanic, discoverable technology, unique resources, surprising creatures, a GIANT beast, a gravship touch, an interesting soundscape, interesting weather, a relationship to the gods.

WHAT THE OWNER HAS ALREADY RULED for this biome (2026-09-30, by question card; do NOT contradict or re-propose anything cut):
- Volley turn-1 slate IN: the Settling (toxin falls when the wind stops; film keeps footprints that PERSIST until the next wind), the projectors still hum + learnable aerosol screen (works in EVERY polluted biome, also on the gravship), the totchak (embankment colossus; once woken eats ruins AND player walls), the Geiger choir soundscape, the chatrak's snap (scaria curse ported to the free tier), the mark made a trade, the hospice (wake a reclaimed droid; built FIRST), the old tongue, the rainbow pools, pilgrim camps (campaign tier).
- CUT: glower black uses (fuel/pigment/hull coat); the Watch ritual.
- Roster: chatrak, totchak, tetchik names kept; wreck-lichen added (scorched stars kept for now); pallbearer and scar roach move to the free tier; fertile Soil band dropped; label "Warscar" (no article).

THE BIOME AS IT STANDS (design review, turn 1):

## 1. What is there

Sources read this pass, all from `origin/main`: every file under `src/RimMandrake/Scarlands/`
(BiomeDef, flora, item, settings C#), `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Warscar.xml`
(each `PatchOperationConditional` resolved from its own xpath, which is `RM_Warscar` in all three ops,
and its `<value>` parsed as element-named rows), the frozen sheet `the_scarlands.md`,
`rosters/the_scarlands.json`, `kits/scarlands_kit_spec.md`, the live item `SCARLANDS_MECHANICS_2`, the
closed `SCARLANDS_STANDALONE_MOD_1` / `SCARLANDS_SHIPPING_NAMES_1` / `SCARLANDS_RENAME_OURS_1`, the
lore ladder `RUT_ScarlandsLadder.xml`, `BIOME_SHIP_CONTRIBUTIONS_1`, the names doc batch 4e, freeze
ruling R23, and every ledger event whose text names Warscar or Scarlands (15 ids, most of them
`SCARLANDS_MECHANICS_2`). Creature behaviour is read from descriptions and the roster's MEASURED
specials, not from defNames.

### Two defs, and the mechanics all live on the wrong one

| def | tier | what it carries |
|---|---|---|
| **`RM_Warscar`** | `mandrake.rm.warscar`, free | Odyssey's own `BiomeWorker_Scarlands`, Odyssey's six donor gensteps (ruins, three crater sizes, junk clusters, junk prefabs), vanilla `wildAnimalScariaChance 0.5`, vanilla weather, **2 flora, 1 item, 3 donor animals inline, zero owned creatures, zero mechanics**. Its settings C# says it outright: *"This biome ships no bespoke mechanic of its own."* |
| **`RUT_Scarlands`** | UtinniPatches, the frozen campaign twin | everything `SCARLANDS_MECHANICS_2` built: **the Scarlands mark** (`RUT_ScarlandsMark` + thoughts + the permanent `RUT_ScarlandsMarkLock`, with a severity floor so it never fully fades), **scaria incubation** (`RUT_ScariaIncubation` + `RUT_ScariaOnsetArming`, so the plated grazers always snap in the end), **Sentinel grave-wards** (`RUT_SentinelGraveWard` + `RUT_LordJob_SentinelDefend` + `RUT_SentinelDefend` duty, defend-only, placed by `RUT_ScarlandsGraveWardScatter`), **pre-sprung dangers** (3 prefabs + genstep), and the **staged-lore ladder** (`RUT_ScarlandsLadder`, 5 rungs, every text a placeholder, no gate wired) |

So a free-tier player landing in the Warscar gets Odyssey's Scarlands with two plants renamed.
Q11a's rule is that *"the top mod without star wars will look precisely the same"*, and today it does
not. **The first job of this bedazzle is to give `RM_Warscar` a body of its own.** The campaign twin is
frozen until the repaint, so its mechanics are not re-argued here. Where a slate idea needs one of
them on the free tier, it says so.

Name drift, one row: the `RM_Warscar.xml` header says the label is *"Warscar"* with no article
(Q5), but the def ships `<label>the Warscar</label>`. That goes on the cards.

### Flora (free tier, inline)

| row | comm | what it is | state |
|---|---:|---|---|
| `RM_Glower` | 1.2 | black radiotrophic varnish that eats the radiation, thickening for centuries; harvests `RM_GlowerCrust` | no comp. Its texPath resolves **nowhere** in `src/`. The def header says its art is *"still pending/failed"*. That is **stale**: `infrastructure/artpipe/done/rutglower_v1` and `rutglowercrust_v1` are **done**. Wire-only. |
| `RM_ScorchedStars` | 0.25 | a round spined cactus "said to look like a burnt star" | own art copy, renders. A **duplicate of the Wasteland's interim plant** (the roster calls it the placeholder *"until the Glowers def lands"*). Not this biome's own voice. |

The sheet's ban 3 (*no green*) and §4 (*"The Glowers… the only flora"*) hold. The second row is an interim.

### Item

`RM_GlowerCrust`: a raw resource, MV 4.5, *"burned, it makes a crude, hot fuel; reduced to ash, a
pigment nothing else on the planet can match"*. **Nothing consumes it.** There is no fuel use, no
pigment recipe, and no dose loop (the header defers that to `SCARLANDS_MECHANICS_2`, which never built it).

### Fauna, merged (inline + patch-added)

| row | comm | bs | route | what it is (from its description / MEASURED special) |
|---|---:|---:|---|---|
| `AA_SpinedGow` | 0.15 | — | inline, Alpha Animals | the **interim plated grazer**, the scaria host (roster `new_defs`: "AA_SpinedGow is the interim body") |
| `RG_Rimclaw` | 0.1 | 1.0 | inline, Regrowth | pollution-adapted predator, bursts into a toxic cloud on death. Drafted label **kettix** (batch 4e) |
| `AA_Helixien` | 0.08 | — | inline, Alpha Animals | the interim Mortuary Guild corpse-decayer (drafted *vulloth*, batch 3) |
| `SW_Electrictick` | 0.3 | 0.25 | patch, isopoda | runs on a discharge organ, dies when it empties, explodes: *a munition with legs* (drafted **tzikket**) |
| `SW_Electricgryllotalpa` | 0.15 | 1.5 | patch, isopoda | a caste that **shoots** arcs (drafted **katchit**) |
| `SW_Juggernautbeetles` | 0.05 | 3.0 | patch, isopoda | thick-shelled charger with a burning blade (drafted **kroxxat**) |
| `RSW_Mynock` | 0.5 | — | patch, SWBestiary | *"a leathery, wet-winged ship-leech that drifts through vacuum toward any hull with power still running"*. Canon, and carries the shipped hull-vermin kit |
| `RSW_CrystalFairyMole` | 0.5 | 0.86 | patch | crystal-plated digging mole (drafted **pittok**) |
| `RSW_MegaphoridLarva` | 0.5 | 0.32 | patch | ravenous larva that bursts out of an infected animal (drafted **tsutta maggot**) |
| `RSW_FoundryBeetle` | 0.18 | 2.4 | patch | massive-mandibled herbivore *"bred as war bugs by the more vicious cave dwellers"*, used as a plated grazer by `RUT_ScariaOnsetArming` (drafted **takkret**) |
| `RSW_Korrum` | 0.05 | 4.0 | patch | the boulder-shelled crab, *"placid to the point of indifference"*. Ruled "anywhere on the dayside", so multi-homed by owner word |
| `RUT_ScarRoach` | 0.08 | 0.25 | patch | scar-dust cleaner, flees before it fights. Art in `src/`, renders |
| `RUT_MortuaryCrawler` | 0.06 | 2.2 | patch | *"the pallbearer"*: armour-plated, one speed (unhurried), digests the preserved dead; *"never seems to notice there was a war at all"*. Art **done** (`rutmortuarycrawler_v1` ×3), texPath state not re-checked |

**Count: 13 species. 0 are owned free-tier inventions.** The free tier's 3 inline rows are all donor
defs, and the 10 patch rows are donor (isopoda), canon/port (RSW), or campaign (RUT). The roster's own
`new_defs` has had two rows open since 2026-09-09: *"plated grazer signature (rhino-armored crust browser,
the scaria host)"* and *"mortuary guild carrion-specialist (dedicated body)"*. The second is now
`RUT_MortuaryCrawler`. **The plated grazer, the sheet's headline animal, has never had a body of
its own.**

Roster rows not wired by the patch, recorded only: `AA_AcanthamoebaGiganteaSmall`, `SW_Electricfish`
(chekkit), `SW_Grenadierworm` (xattuk), and `RSW_ShaleGorger`, which batch 4e calls a misfiled
**sea beast**. Whether they join is a per-row card at this sitting, not a sweep.

### Terrain, weather, sound, ship, gods

- **Terrain:** vanilla `AncientMegastructure` + Soil (fertility ≥ 0.5). 🔴 That **Soil band breaks
  ban 2** ("no soil terrain, no farmable cell"). It is a small fix and goes on the cards. Toxic water
  comes from Odyssey. **The rainbow pools (§8, ⭐) do not exist.** `LIQUID_TYPES_MOD_1` lists "rainbow
  reaction-liquor" as a liquid type and nothing builds it.
- **Weather:** stock Clear 50 / Fog 1 / DryThunderstorm 1 / GrayPall 10 / ToxRain 10 / Overcast 6. R23
  ruled the toxic fall a **war aerosol, not rain**, *"settling out as a corrosive fall when the air
  stills"*. No owned def expresses that: it ships as vanilla ToxRain.
- **Sound:** none. No SoundDef and no ambient. The sheet §9 names a register (wind on metal,
  Geiger-tick, the pools' faint boil, Sentinels the pawns cannot hear), and none of it is built.
- **Ship:** the mynock boarding/breeding/gnaw/hunt-out loop is **shipped** (`SHIP_VERMIN_MOD_1`,
  `WRECKAGE_VERMIN_SPAWN_1`), but on a canon RSW creature, in shared kit code also used at the Fall
  Line, and campaign-routed. `BIOME_SHIP_CONTRIBUTIONS_1` has **no Warscar row**.
- **Gods:** §GM's truth ladder exists (the last stand → Sentinels → the Cathedral as a god's deathbed
  → the Rakata → the pilgrims) and the staged-lore engine swaps its texts, but **all five rungs are
  placeholders and no gate calls `AdvanceStage`**. No ideoligion, precept, ritual or relic touches the
  biome. `RAKATAN_ARCHOTECH_MACHINES_1` (owner's vision, unbuilt) is the tech-side neighbour.
- **Unbuilt sheet promises** (each ⭐ or §-named): the rainbow pools · reclaimable droids / the droid
  hospice · the old tongue (translation monopoly) · the pilgrim ends · the stripped fleet · the bastion
  that couldn't fall · humming shield projectors · glower fuel + dose loop · mynock pets.

### Art state

Probe: `mynock` returns 12 registry lines and 6 `done/` files, so the instrument can see.

- **Wire-only (done, unwired):** `rutglower_v1` and `rutglowercrust_v1` → `RM_Glower` / `RM_GlowerCrust`.
- **Done:** `rutmortuarycrawler_v1` (3 facings).
- **Renders:** `RUT_ScarRoach` and `RM_ScorchedStars`.
- **Nothing in any store for:** a plated grazer, the Sentinel grave-ward (vanilla fortified-wall
  atlas), or the sprung prefabs (reused vanilla).


## 2. Scorecard: the nine marks

Each mark is scored twice. **Free** is `RM_Warscar` with its patch-added cast, which is what ships to
every player. **Campaign** adds the `RUT_Scarlands` twin's mechanics. The program's verdict is the
free column, because Q11a requires the free mod to stand alone.

| # | Mark | Free | Campaign | Evidence |
|---|---|---|---|---|
| 1 | Unique mechanic | **MISS** | HIT | The free tier has none (its own settings say so). Scaria 0.5 is Odyssey's donor field, not ours. On the twin: the **Scarlands mark** (a permanent mood scar with a severity floor), **scaria incubation** (grazers that always snap), and **defend-only Sentinels**. The mark is the strongest, and it is the sheet's own "you'll return… changed". |
| 2 | Discoverable technology | **MISS** | MISS | Nothing teaches. `RM_GlowerCrust` has no recipe. The old tongue, the reclaimable droids and the rainbow reagents are all unbuilt. |
| 3 | Unique resources | **PARTIAL** | PARTIAL | `RM_GlowerCrust` exists and is only here, but it has no use and no wired art. The rainbow reagents (§7) and sealed salvage are donor Odyssey crates, not ours. |
| 4 | Surprising creatures | **PARTIAL** | HIT | The free tier's surprise is donor (rimclaw's death cloud). The patch cast is genuinely strange: living munitions that explode, shoot and spray eggs, a larva that bursts from a host, and the pallbearer that *"never seems to notice there was a war"*. **None is an owned invention of the free tier.** |
| 5 | GIANT beast | **MISS** | MISS | Largest: `RSW_Korrum` bs 4.0 at 0.05, multi-homed across the dayside by ruling, and `SW_Juggernautbeetles` bs 3.0. There is no colossus of the Warscar's own. |
| 6 | Gravship touch | **PARTIAL** | PARTIAL | The mynock infestation is real, shipped, and the sheet's own (*"the biome follows you home"*). But it rides a canon RSW creature, a shared kit (the Fall Line uses it too), and the campaign route. The free tier gets nothing. There is no `BIOME_SHIP_CONTRIBUTIONS_1` row, so the ship gains nothing **from** the Warscar either. |
| 7 | Soundscape | **MISS** | MISS | No SoundDef. The sheet §9 register is unbuilt. |
| 8 | Interesting weather | **MISS** | MISS | Vanilla ToxRain / GrayPall / Fog. R23's *war aerosol that settles when the air stills* has no def. |
| 9 | Relationship to the gods | **MISS** | PARTIAL | The twin carries the 5-rung staged-lore ladder (placeholder text, gates unwired), and §GM makes the Rust Cathedral *"a god's deathbed"*. No ideoligion, ritual or relic touches either def. |

**Free tier: 0 HIT / 3 PARTIAL / 6 MISS. Campaign: 2 HIT / 3 PARTIAL / 4 MISS.** This matches the
program table's "content today: 1". **What sets the Warscar apart: the lore is the richest of the
eleven, and the free body is the poorest.** The frozen sheet is one of the best-written on the
planet, with its outward-facing defense, its unnamed enemy, its pools that lie about their colour,
and machines that defend and never explain. Almost none of it is on the ground. The twin got the
*curse* (the mark, scaria, the Sentinels), and the free mod got nothing.

⇒ Movement 3 should aim at **the free tier's body first**: the giant, the grazer, the tech, the
sound, the sky. It should spend the sheet's unbuilt ⭐ promises (the rainbow pools, the reclaimable
droids, the shield projectors, the old tongue) rather than inventing new lore. **The admission test
for this biome**, from its own image: *every new thing must be something the war left, or something
that eats what the war left* (§4: "everything alive here eats what the war left"). Nothing pastoral,
nothing green, no intact treasure in the open, and §GM never in a description.


## 3. Roster fill

### The gaps, read from the sheet only

The admission test above, plus the stillsand rule: *if the roster looks healthy, it is wrong*. Only
gaps the frozen sheet names, or a bar mark the free tier cannot meet, are filled.

| gap | source | fill? |
|---|---|---|
| **The plated grazer has no body.** It is the sheet's headline animal (§4: *"they care little about weapons or much of anything... until the madness inevitably comes"*), and the roster's `new_defs` row has been open since 09-09. `AA_SpinedGow` (donor) and `RSW_FoundryBeetle` (a war-bred mandible beetle, ported) stand in. | §4, `new_defs` | **YES, #1** |
| **No colossus** (mark 5). The korrum is a placid crab on loan across the dayside. | bar | **YES, #2** |
| **The Geiger-tick has no source** (§9's sound register: *"wind on metal, Geiger-tick ambience"*). | §9 | **YES, #3**, sound as a creature |
| **The plated grazer eats nothing that exists.** §4 says it browses *"crust and wreck-lichen"*. The glower is the crust, and wreck-lichen has no def. | §4 | **YES, flora #1** |
| Free-tier fliers / wiring-eater | the mynock is canon and campaign-routed | **NO.** An RM mynock-alike would be an echo of canon. The free tier's ship touch comes from the slate instead (§4 #2). |
| Pool life | §8: *"the color isn't life, it's reaction and acid"* | **NO, by ban.** Nothing lives in the rainbow pools. |
| More munitions | the isopoda castes already carry the weapon-descendant band | **NO.** Tier-routing them is a card (§5), not a fill. |
| Mortuary Guild body | `RUT_MortuaryCrawler` is built (invented, ours) | **NO new def.** It moves inline to RM (card), as Q11a allows an invented creature. |

### The sweep

All candidates are in the batch-4e Scarlands accent: voiceless and clipped, t/k/ts/ch/x, short
vowels, -t/-ak/-ix. Every name already drafted in that batch is avoided (takkret, tzikket, katchit,
kroxxat, chekkit, xattuk, kettix, pittok, tsutta, and their alternates).

**Instruments, run this pass:**

1. `git grep -il <name> origin/main -- src design infrastructure skills`. Probes: `korrum` **93**
   files, `mynock` **239**, `takkret` **2**, so the instrument sees both common words and the batch
   doc itself.
2. Wookieepedia `api.php?action=query&list=search&srsearch=<name>`. Probe: `mynock` → *Mynock,
   Mynock/Legends, Ord Mynock…*. 🔑 The probe paid for itself. **`tokkat`, the first grazer
   candidate, is CANON** (*Tokkat*, *Tokkat/Legends*) and was struck.
3. `check_pseudo_sw_name.py`: all PASS. ⚠ This instrument also passes `mynock` (it shape-checks
   against the 138-entry library, which has no mynock entry), so it is not counted as a collision
   test, only as a shape test.

| candidate | repo | wiki | verdict |
|---|---:|---|---|
| tokkat | 0 | **Tokkat (canon)** | ✗ struck |
| **chatrak** | 0 | 0 | ✓ |
| kachet | 0 | 0 | ✓ (alt) |
| **totchak** | 0 | 0 | ✓ |
| tsotrax | 0 | 0 | ✓ (alt) |
| **tetchik** | 0 | 0 | ✓ |
| kotrix | 0 | 0 | ✓ (alt) |
| chikkit, tikchit | 0 | 0 | ✓, but held back: too near the drafted *chekkit* / *tzikket* to read apart aloud |
| `RM_WreckLichen` | 0 (sheet prose says "wreck-lichen", not a def) | 0 | ✓ |

### Proposed fills: 3 creatures + 1 plant, all `RM_` tier, one home each

| # | name (alt) | band | bs | the creature |
|---|---|---|---:|---|
| 1 | **chatrak** (*kachet*) · `RM_Chatrak` | the plated grazer, the scaria host | ~3.0 | A low, rhino-plated browser that grinds **wreck-lichen and glower crust off metal** with a rasp of a mouth. Its plate is layered like an embankment, and bullets mostly ricochet. It **ignores you**: it ignores gunfire, ignores its own wounds, and walks through a firefight to reach a lichen-crusted hull. Then the madness comes. Its plate **lifts and flares** (a readable second graphic or overlay), it stops eating and starts circling, and a day later it charges. The sheet's own *"an animal built beyond fear, guaranteed to lose its mind"*. On the free tier it carries the incubation mechanic (slate #3), so the free mod finally has the curse. Milk/wool: none. Leather: a heavy plate-hide. Tame: hard, and pointless, since it always goes mad in the end. That is the joke the Jawa keep failing to learn. |
| 2 | **totchak** (*tsotrax*) · `RM_Totchak` | the colossus | ~14 | **The embankment that breathes.** A colossal armoured slag-eater that sleeps for seasons at a time half-buried in the Last Line, its back crusted in slag, glower and turret stubs until it is **indistinguishable from the fortifications** (dormant, its graphic one of the line's own silhouettes). It eats what the war left: slag, hull plate, the ruins themselves, which is why a ruin ring sometimes has a bite out of it. It wakes to mining, deconstruction or explosions within its radius (vanilla `CanBeDormant` + wake-on-damage/noise), stands up out of the line, grazes the nearest wreck for days and lies down somewhere new. It is not hostile unless hurt, and when hurt it is a siege. 🔴 **§GM guard:** it must never read as *the enemy* the line faced. Its description says only that it eats ruins and that the Jawa say it *"was here after"*. Pairs with slate #4. |
| 3 | **tetchik** (*kotrix*) · `RM_Tetchik` | the Geiger-tick | ~0.1 | A thumbnail beetle that lives in the glower crust and **clicks**. Its shell plates snap faster the hotter the ground, so a crater bowl full of tetchik **ticks like a counter**. Harmless, inedible (it tastes of metal), and the player's free radiation map, by ear. Thick ticking means thick glower: rich harvest, and the place to stand least long. The sound bed of the whole biome (slate #5). It scatters into silence near Sentinel ground (campaign), a sign readable by ear. |
| F1 | **wreck-lichen** · `RM_WreckLichen` | the second flora, on metal | — | A rust-orange-to-bone crust that grows **only on ruins and wreck**: steel walls, junk clusters, chunks. It never grows on ground, so it is not soil and not green (bans 2 and 3 hold). The chatrak's food and the reason the grazers walk *toward* the wrecks. It is a `Plant` with a ruin-adjacent placement validator, or a filth-like "crust" overlay (engine call at turn 3). Scraped, it yields a little dye-mordant that fixes the glower pigment (slate #10). It replaces `RM_ScorchedStars` as the second flora, and the Wasteland duplicate retires from this biome (card). |

All four are invented (Q11a → `RM_`) and single-homed. None reuses a neighbour's mechanism. The
chatrak's snap is the **twin's own** incubation, brought down a tier. The totchak's dormancy is
vanilla, and its disguise is the Warscar's own (the line). The Stillsand's siidda is a dust husk
woken by storm or wound, and the totchak is a fortification woken by **demolition**. The tetchik is a
sound source, not a warning-sentinel (the Stillsand's piinnok sinks to warn; the tetchik only ever
reports).



THE TURN-1 SLATE (for reference; rulings above override):

## 4. Volley turn 1: the slate

**Kept clear of** the other ruled and offered packages (read from every `*_bedazzle_review`, `*_cast`,
`stillsand_turn3_development` and `*_GPT_ENRICHMENT` on origin/main):

- **Stillsand:** the Listening / geophone, the dunes take the ship, the Stillstorm, the Return,
  biosilica optics, eternal noon.
- **Long Shade:** shade currency, Sh'kaar, the golden hour, the shade awning / Shipfall Commons, the
  khorrak alloy, the dew condenser, middens.
- **Leaning Scrub:** the Stall-and-Gale wind calendar, the Lean, the tallest thing on the plain, the
  vaporator, the smother-craft, the calling-pyre.
- **Blue Desert:** silence-then-boom, the blue-ice heat sink.
- **Cracked Lands:** read-the-land survey, water-wake, floodline salvage claim.
- **Cauldron:** fluid conversion, the four-stroke weather, condensate gardens.
- **Forge:** giant-on-the-clock, floatstone keelwork, the four voices, white plume fronts.
- **Wasteland:** named storms (Deadlight Halo, Cinderwire), the Middenshell procession, the Sealed
  Cask Bay, the Rite of Tipping.
- **Contagion:** draftprints / bodyprints, the Dive.
- **Rust Cathedral (grandfathered neighbour):** the hum-mood, living bolts, eel fishing, the
  deep-drill response, the roaches.

Where a candidate reuses a shipped *mechanism* (not a package), it says so.

**The Warscar's family is the RECORD.** The Stillsand is what is under you. The Long Shade is where
you stand. **The Warscar is what already happened here, and the ground still telling it.** Every
candidate either makes the war legible (a sign, a sound, a residue), or makes something the war left
useful. None names the enemy.

| rank | candidate | marks | size | tier |
|---:|---|---|---|---|
| 1 | The Settling | 8 (+7) | M | RM |
| 2 | The projectors still hum: the aerosol screen | 2, 6 (+3) | M | RM |
| 3 | The chatrak's snap: the curse comes to the free tier | 1, 4 | S | RM |
| 4 | The embankment that breathes: the totchak | 5, 4 | M | RM |
| 5 | The Geiger choir | 7 | S–M | RM |
| 6 | The rainbow pools: colour is a lie you learn to read | 3, 2 | L | RM (FlowWorks dep) |
| 7 | The Watch: standing the line | 9 (+1) | M | RM ritual, RUT Sentinel hook |
| 8 | The mark, made a trade | 1 | S | RM |
| 9 | The pilgrim ends open the ladder | 9 | M | RUT |
| 10 | Glower black: fuel, pigment, the war-black hull | 3, 6 | S | RM |
| 11 | The hospice: carry one out and wake it | 2, 3, 4 | L | RM body / RUT droids |
| 12 | The old tongue | 2 (+9) | M | RM inscriptions / RUT translators |
| 13 | Movement-4 pre-ticket: the free-tier body wave | — | M | RM |

1. **The Settling: the war falls when the wind stops** *(mark 8, and the sound of 7).* R23 already
   ruled the physics and nothing built it: the toxin is *"aerosolised… still suspended over the
   province, settling out as a corrosive fall when the air stills."* So the Warscar's signature weather
   is **calm**. When wind speed drops below a threshold for a few hours, a GameCondition begins: a fine
   pale fall drifts straight down (a particle overlay), toxic buildup ticks on unroofed pawns, and
   exposed items, floors and roofs gather a **settled film** (a filth or terrain overlay). 🔑 **The
   film keeps tracks.** Anything that walks through it during or after a Settling leaves prints until
   the next wind, so **the ground literally records who came by**. Raiders' approach lines, a mad
   chatrak's circling, a pawn's route are all readable, which is the biome's thesis (*"a battlefield
   still explaining itself"*) turned into play. The wind's return lifts it. *Engine:* GameConditionDef
   + a `MapComponent` watching `map.windManager.WindSpeed`, a filth def with a footprint-trail
   writer (vanilla blood/dirt tracking is a precedent to read first). *Distinct:* the Leaning
   Scrub's Stall is a *calendar* calm that bends fire and plants, and Wasteland's named storms are
   moving fronts. This is calm as the hazard, and residue as the record. *Trade-off:* footprint
   filth at map scale is a performance and clutter risk. It needs a cap and a fade, or a toggle.
2. **The projectors still hum: the aerosol screen** *(marks 2 and 6, plus 3).* §8 ⭐: *"old
   emplacements aimed to keep something OUT… Some hum yet."* Scatter dead projector rings along the
   approaches (prefab content on the Odyssey ruins genstep), and make **a few still live**: under a
   humming ring's dome **the Settling does not fall** (the film stops at a crisp circle, a sign
   visible from orbit-zoom). It does not stop bullets. It is not a combat shield, and it screens
   only fallout. **Study** a humming ring (the Anomaly study-target shape; the Sump research is our
   precedent) and you learn the **aerosol screen**: a buildable low-power projector that keeps
   fallout, toxic buildup, and the Settling's film off what it covers. 🔑 **Ship touch:** the screen
   is **gravship-buildable**, so the ship carries a ring of the old defense with it. That is the
   Warscar's row for `BIOME_SHIP_CONTRIBUTIONS_1`, and it pays off in every polluted biome on the
   planet (Wasteland, Cauldron, Contagion), which is why it is worth landing here. *Uniqueness:* the
   only biome that teaches you to *keep the air off*. *Trade-off:* it must not trivialise those other
   biomes' toxic weathers. Small radius, real power draw, and the screen blocks particulates and
   fallout only, never gases (gases stay the Cauldron's).
3. **The chatrak's snap: the curse comes to the free tier** *(marks 1 and 4).* The twin's scaria
   incubation (`RUT_ScariaIncubation` + `RUT_ScariaOnsetArming`) is pure XML on RM-tier classes
   (`ArmLatentHazardExtension`'s `pawnKindFilter` / `requiredHediff`). Re-author it franchise-free on
   `RM_Warscar` with **the chatrak** (fill #1) as its filter, and add the one thing the twin lacks:
   **staged signs**. The plate lifts at stage 1, the chatrak stops eating at 2, circles at 3, and
   then it charges. *Nothing goes mad without warning.* *Engine:* XML, plus a hediff-stage graphic
   swap or overlay (small C# if no stock hook). *Trade-off:* a guaranteed manhunter on every map is
   a tax. Density must stay low and the snap rare enough to be an event, not weather.
4. **The embankment that breathes: the totchak** *(marks 5 and 4).* Fill #2 as a mechanic. Map gen
   places one dormant totchak **as a segment of the Last Line**: same silhouette, same slag crust,
   flagged only by a faint rise-and-fall (an idle breathing anim, or a slow 2-frame swap). Mining,
   deconstruction or an explosion within its radius wakes it. It stands up out of the wall, leaving a
   breach in the fortification, grazes the nearest wreck or ruin wall for days (the bite marks stay,
   the sign), and lies down somewhere new, often **inside your base's defensive wall line if you
   built one**, because to it a wall is a wall. *Engine:* vanilla `CanBeDormant`, a wake-on-noise
   comp (read the Stillsand's `RM_CompDrumLure` vocabulary first), and a JobGiver to eat buildings
   (the `RM_JobGiver_GnawTargets` hull-vermin kit already gnaws defNames, so it extends with a
   size-scaled bite). *Distinct:* the Forge's giant is on a clock and the Stillsand's oommok is a
   walking shade. The totchak is a **colossus disguised as ruins** that eats your fortifications.
   *Trade-off:* eating player walls can feel unfair. It needs the breathing tell, a letter on
   waking, and a bias toward ruin walls over player walls.
5. **The Geiger choir** *(mark 7).* The Warscar heard with eyes closed:
   - the **tetchik click-bed** (fill #3), whose tempo maps the glower heat under you;
   - **wind on metal**: turret barrels and ruin rings keen in wind, and go dead silent in a Settling,
     so *silence is the alarm* that the fall has begun;
   - the **pools' slow boil** near the rainbow pools (#6);
   - **the hole in the sound** around Sentinel ground (campaign): every ambient layer drops out
     inside a line, so the player hears what the pawns cannot.

   *Engine:* the shipped `RM_MapComponent_ProximitySoundscape` + extension (Greentide, and the
   Stillsand's ground layers) with new tagged sources. Placeholder grains until real audio.
   *Distinct:* the Stillsand is heard through the feet, the Long Shade as heat, and the Blue Desert
   as silence-then-boom. The Warscar is **a counter and a wind-harp**, and its silence means calm,
   which means fallout. *Trade-off:* a constant tick is grating. It needs a volume ceiling, and it
   should be sparse except over thick glower.
6. **The rainbow pools: colour is a lie you learn to read** *(marks 3 and 2).* §8 ⭐ and §7's
   reagents. Self-replenishing reaction pools (a FlowWorks liquid, per `LIQUID_TYPES_MOD_1`'s
   *"rainbow reaction-liquor"*), hot and lethal to enter. Their colour **cycles** as the reactions
   turn over, and each colour phase means a different reagent ready to draw. The trap is that
   **the prettiest phase is the deadliest** (*"the color isn't life, it's reaction and acid"*).
   Learning the true colour table is the discovery: a player-side "pool journal" fills as pawns
   draw and survive, and a reagent tap built at the rim reads the phase for you once researched.
   The reagents feed drugs, medicine and the glower pigment's fixer. *Engine:* FlowWorks liquid +
   a pool `MapComponent` cycling a colour/phase, with harvest via a rim building. **Large.**
   *Distinct from the Cauldron:* there gas becomes fuel by conversion tech. Here you **read a
   liar's colours** and draw finished reagents. *Trade-off:* the largest build on the slate, with a
   hard FlowWorks dependency. Could open as a static pool with a fixed table and grow the cycle later.
7. **The Watch: standing the line** *(mark 9, plus 1).* The free-tier god-touch with no §GM leak.
   An Ideology `RitualDef` (all DLC assumed): colonists **stand a night facing outward** at a ruin
   ring, keeping the old watch for whoever built it. Outcomes by quality: a mood of meaning, a
   reduction in mark severity, and at its best **a revealed sealed cache** (ban 4: value is sealed),
   as if the line rewarded its sentries. 🔑 **Campaign hook:** the Forgotten Sentinels
   (`RUT_SentinelDefend`) **let a pawn who has stood the Watch walk their ground** without being
   engaged, the only time they acknowledge anything. *"They do not explain."* They simply stop
   aiming. *Engine:* RitualDef + outcome worker, and on the twin a faction-relation-free
   pass-through check in the Sentinel duty (small C#). *Distinct:* the Stillsand's Return *pays* the
   sun god, and the Leaning Scrub's calling-pyre *summons*. The Watch **serves a dead army**.
   *Trade-off:* the Sentinel pass-through must not become a cheese to loot their ground for free.
   Its duration should be bounded, and taking anything should end it.
8. **The mark, made a trade** *(mark 1, free tier).* Port the Scarlands mark down to `RM_Warscar`
   franchise-free (RC4 lock + `RM_HediffComp_SeverityFloor`, both RM-tier and shipped), and make it
   **pay as well as cost**: a marked pawn **reads the ground**, with faster salvage and deconstruct
   on ancient structures and a chance to notice sealed caches. The sheet's *"you'll return…
   changed"* becomes a choice of *who* you send. *Engine:* XML on shipped classes + one stat offset
   per stage. *Trade-off:* a buff on a permanent scar tempts a min-maxer to farm it. The mood floor
   must stay real.
9. **The pilgrim ends open the ladder** *(mark 9, campaign).* The staged-lore engine is built and
   **no gate calls it**. Make the pilgrim ends (§8: terminal camps along the Ashfall Road, *"each
   one found is a rung"*) real map sites. Finding and reading one calls
   `GameComponent_LoreStage.AdvanceStage("Scarlands")`, so the biome's own description changes
   under the player as they learn. It also forces the **authoring sitting** for the five placeholder
   texts, which is owed anyway. *Engine:* SitePartDef/prefab + a readable journal thing + one call.
   *Trade-off:* R25. The texts must let the player *infer* and never *tell*, so it needs the owner's
   pen, not an agent's.
10. **Glower black: fuel, pigment, the war-black hull** *(marks 3 and 6).* The crust finally gets
    its promised uses:
    - **fuel**: a glower brazier or generator input that burns hot and adds a little toxic
      buildup to whoever tends it (the dose loop, cheap);
    - **pigment**: ash + wreck-lichen mordant = **war-black**, a dye and a floor/wall colour stuff
      *"that doesn't fade"* (the owner's *colour with material, not paint* doctrine);
    - **the ship**: war-black hull plating, a cosmetic with a tiny beauty-and-prestige stat, the
      Warscar's mark on every ship that stopped here.

    *Engine:* XML (recipes, a stuff/colour def). Art for `rutglower_v1` / `rutglowercrust_v1` is
    **done** and only needs wiring. *Trade-off:* it is the smallest, so the risk is that it reads
    as filler. Its value is that it finishes a resource that already exists.
11. **The hospice: carry one out and wake it** *(marks 2, 3 and 4).* §7 ⭐ *reclaimable droids*:
    rings of powered-down chassis facing the Cathedral. Most are dead, and some self-ended (the
    sign: a deliberate pose, never gore). **A few are intact.** Carry one home, and a long repair
    job wakes it as a colonist-machine. The free tier uses an RM "ancient servitor" body (Biotech
    mech machinery underneath). The campaign swaps in the canon droid chassis. Studying the dead
    ones yields salvage and research. *Overlap to check at turn 3:* `WreckedMachines` (repair in
    place) and `RAKATAN_ARCHOTECH_MACHINES_1` (*"they sag, they don't break"*). This is
    their natural consumer, not a rival. **Large.** *Trade-off:* a free colonist source can
    unbalance the game. Rarity and a long, costly wake keep it a prize.
12. **The old tongue** *(mark 2, plus 9).* §7: *script on every surface, readable only by the very
    educated*. Free tier: inscription panels on ruins that a high-Intellectual pawn can **transcribe**
    (a work job), yielding research progress and occasionally the location of a sealed sublevel.
    Campaign: full translation needs the Ascendant Helix or the Deepwater Compact (their scholars'
    monopoly), and each translated panel can be a ladder gate (pairs with #9). *Distinct:* the
    Cracked Lands survey reads *strata*, and this reads *words*. *Trade-off:* it overlaps #9 as a lore
    gate. Rule one primary gate surface.
13. **Movement-4 pre-ticket, not a mechanic: the free-tier body wave.** This is owed whatever the
    volley rules:
    - wire the done glower art;
    - build fills #1–#3 + `RM_WreckLichen` if admitted;
    - move `RUT_MortuaryCrawler` and `RUT_ScarRoach` inline as `RM_` (both are invented, Q11a);
    - card the isopoda castes' route (a non-SW donor, so inline with `MayRequire` like the `AA_`
      rows);
    - fix the Soil band (ban 2) and the label article;
    - correct the stale "art pending/failed" header in `RM_WarscarFlora.xml`.

**Recommended volley opener:** **#1 + #2 + #4** as the spine: *"the war falls when the wind stops,
the old shields still hum, and the wall gets up."* #1 and #2 are one system (the fall, and the thing
that stops it), which makes a cohesive package rather than a list. Then #3 and #5 for the free
tier's curse and ear, #7 for the gods, and #10 as the cheap resource finish. #6 and #11 are the two
large sheet ⭐s to rank against each other, since both are worth doing and neither should be
done half. #13 is ticketed regardless. #1–#5 + #7 turn every free-tier MISS except mark 2's depth
(which #2 covers) into a HIT.



TASK: Give 8 to 12 recommendations that would make The Warscar richer, more memorable and more distinct, filling the weakest of the nine marks first. Improve and extend what is ruled rather than restarting it. For each recommendation:
- **Name** and a one-line pitch
- What the player sees, hears and feels
- Which of the nine marks it lifts
- How it could be built in RimWorld 1.6 and a rough size (XML only / small C# / large C#)
- Why it belongs to THIS biome and no other

Then list your TOP 3 in rank order with one line of why each. Reply in Markdown, at most about 1500 words. Do not ask questions; do not modify any files.