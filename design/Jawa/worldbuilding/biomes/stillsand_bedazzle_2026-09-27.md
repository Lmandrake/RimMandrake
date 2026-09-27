# The Stillsand — bedazzle to full-mod status (proposal, 2026-09-27)

**Intent:** prepare an owner sitting that takes `RM_Stillsand` (mod `mandrake.rm.stillsand`, campaign label "the Dune Sea" as a Utinni patch) from a built-but-thin biome to a full marquee mod. This document rules nothing; every decision lands as a card question in §7.

_DESIGN pass, 2026-09-27 (`STILLSAND_DESIGN_SITTING_1`), written against the two frozen
sheets `dune_sea.md` + `deep_desert.md` (amendments add detail, never change a ruling),
the built mod `src/RimMandrake/Stillsand/`, `rosters/dune_sea_deep_desert.json`, names
batch 4d, the closed items `STILLSAND_RM_MOD_BUILD_1` / `STILLSAND_KORRUM_HOLE_1`, and the
sibling proposal `long_shade_bedazzle_2026-09-27.md`, whose Q6/Q7/Q9 hand this sitting
five cross-desert pairs. Tier law: `biome_mod_architecture.md` §7 Q11/Q11a. Nothing here
is a def; nothing here is filed; every DRAFT name awaits the owner._

## 1. Thesis

**The Stillsand is the biome that is not there.** Next door, the Long Shade is the desert
a colony can live off — position, tenure, a food web steady enough to hunt. The Stillsand
is its exact negative: the dayside terminus, the ocean of nothing every green line is
drawn against, the distance between places rather than a place. Its two sheets agree on
the mechanism from opposite ends: the dune sea's deep dayside is where **time does not
pass** (no night, no season, no moving shadow — ever), and the deep desert's far ring is
where **absence itself is the anomaly** (19–40° of arc from any water). Both resolve to
the same design law: the biome is not lifeless, it is **latent, and armed** — dormant for
years, event-driven, woken by water, vibration or blood, with the player as the detonator.

Against the register the sibling docs set up: the Grey's reward is a preserved thing, the
Twilight's a living process, the Long Shade's a position. **The Stillsand's reward is the
crossing itself** — and what the crossing shakes loose: the moving shade of a walking
mountain, the eruption you triggered, the pristine thing the dune finally walked off of.
Nobody holds ground here. You transit, you detonate, you dig, you leave.

⇒ **The admission test, one line: if an idea makes a Stillsand map look busier, it is
wrong.** (The sheet's own words: *"a reviewer's instinct to add one more thing is the
defect"* — dune_sea §5.) Everything admitted must be **buried, dormant, giant, or a
line** — below the surface, asleep until triggered, terrain-scale, or a hard edge. A
medium-sized, visible, awake, ordinary thing fails on sight.

### 1a. How the two sheets map onto the ONE def — stated plainly

**`RM_Stillsand` is one def carrying the union of both sheets, by ruling.** R22
(`_freeze_rulings_2026-09-07.md`, restated in the frozen `RUT_ExtremeDesert.xml` header):
*"the dune sea and the deep desert stay ONE owned def… Splitting them is cheap once owned
but is the OWNER's call to reopen, not authored here."* The architecture's own grouping
pass (§2) confirms row 1 as one standalone mod; the roster is one merged file
(`dune_sea_deep_desert.json`), and its law is the **strict intersection** — both sheets'
§6 bans bind everywhere in the biome.

- **What binds def-wide:** both ban lists (no night, no fire ecology, no rot, no green,
  no medium bodies, no lush, no mineralized shine, subsurface-strike-only predation);
  the merged roster; the weather block (Clear 95 / Sandstorm 4 / everything wet zeroed).
- **What is a label-layer distinction, not a def split:** "the Dune Sea" is the campaign
  label, carried by Utinni patches (`BiomeNames_Ashkarr.xml` /
  `BiomeDescriptions_Ashkarr.xml`); "the Stillsand" is the shipped RM_ label. Same tiles,
  same content.
- **What genuinely differs between the sheets and cannot be expressed by one def:** the
  dune sea's content is θ 0–40 material (light-pipes, the corrugation, the sand busters);
  the deep desert's is far-ring material (the ollim, sandstorm destruction, caverns,
  yardangs). A BiomeDef cannot gate content by arc, so the def carries the union and the
  eventual painting pass places one biome over both zones. Whether that union ever splits
  into two painted defs is **an agenda question (§7 Q13), not this doc's ruling** — the
  recommendation is no, per R22.

## 2. Cast partition

Every wired row of the built `RM_Stillsand` (2 inline) + its Utinni patch
`WildAnimals_Stillsand.xml` (14 fauna + 3 flora + 5 pack), with **measured** bodySize
(`race/baseBodySize`, read from the defs this pass) — per the `STILLSAND_KORRUM_HOLE_1`
law: no hole and no verdict without measuring what is already wired. Verdicts are
recommendations for the sitting, not rulings.

### 2a. Canon rows — stay in the Utinni patch forever (Q11)

Batch 4d's census: *"Canon kept: Gizka, Kreetle, Scurrier, Granite slug, Krayt dragon,
Greater krayt dragon"*, plus WarWyrm (**canon** — Sith wyrm, corrected that pass).

| row | comm | bs | band | note |
|---|---:|---:|---|---|
| RSW_WarWyrm | 0.2 | 15.0 | giant | ruled a BURROWER (owner card 2026-09-09) — subsurface-strike legal |
| RSW_KraytDragon | 0.15 | 12.0 | giant | icon; canonical dune-swimmer |
| RSW_GreaterKraytDragon | 0.001 | 15.0 | giant | icon; correctly near-zero |
| RSW_Kreetle | 0.2 | 0.2 | grain | ⚠ cross-desert pair — §7 Q3 |
| RSW_GraniteSlug | 0.1 | 0.2 | grain | ban-3 mineralized-look eye test still owed (roster confidence) |
| RSW_Scurrier | 0.1 | 0.2 | grain | |
| RSW_Gizka | 0.01 | 0.18 | grain | icon carve-out; ⚠ cross-desert pair — §7 Q3 |
| pack: RSW_Bantha 4.0 / Ronto 6.0 / Eopie 1.4 / Jamel 1.9 / Falumpaset 3.0 | — | — | — | all five canon → all five stay Utinni; see the free-tier hole in §2d |
| flora: RSW_Plant_Bloddle | 0.05 | — | — | genuine canon (Tatooine bloddle) |

### 2b. Invented-name rows riding the Utinni patch — Q11a says they belong RM_-side

`STILLSAND_RM_MOD_BUILD_1` already flagged the flora pair and Drazzik as wrong-tier
("invented content is RimMandrake-tier, prefix notwithstanding — flagged, not decided").
This table completes the sweep. **Recommendation: move all nine, renamed `RM_`** (§7 Q1).

| row (comm) | bs | band | name state | evidence / note |
|---|---:|---|---|---|
| RSW_Kudda 0.3 | 0.15 | grain | **kudda**, RULED | light-feeder — eternal noon is its natural home; ⚠ dual-homed with the Long Shade — §7 Q2 |
| RSW_Ikee 0.15 | **0.4** | ⚠ mid | **ikee**, RULED | ported off AA_Eyeling (roster bs 0.13); the port measures 0.4 — inside the banned 0.3–3.0 band. §7 Q7/Q8 |
| RSW_Vozzik 0.0005 | 5.0 | giant | **vozzik**, port-named | barely-moving alien giant |
| RSW_TruffleMole 0.5 | 0.9 | ⚠ mid | **pikkut**, DRAFT (batch 4c) | subsurface burrower; ⚠ wired in BOTH deserts — §7 Q4 |
| RSW_SandLion 0.5 | 2.0 | ⚠ mid | **vekka** ⚠ FLAG | batch 4c Flag 1: *vekka* was porting-agent-coined, never owner-ruled, and is a canon character's given name (Vekka Lodik); offered swap **shakkir** — §7 Q6 |
| RSW_Drazzik 0.05 | 2.2 | ⚠ mid | **drazzik** (build item) | the biome's own drum-lure archetype (`RM_CompDrumLure`, shipped) + its egg-trap clutch |
| JOE_Cephalope 0.5 | 1.2 | ⚠ mid | **qorrax**, DRAFT | spd 8.8 (MEASURED); ⚠ home-and-ban conflict, sibling recommends Stillsand — §7 Q5. Moving it RM_-side also means moving its ThingDef out of Utinni-tier `Absorbed_Cephaloids_Defs.xml` (the build item's own §10(a) flag) |
| flora RSW_LightPipeNub 0.1 | — | — | descriptive-English (flora convention) | the dune sea's whole visible biome; invented, built, real art |
| flora RSW_Ollim 0.01 | — | — | **ollim**, RULED | deep_desert §4b's shade tree; built, real art, and `RSW_OllimWood` ships the ruled stat signature (§3) |

### 2c. The mid-band question — surfaced, not ruled

Five wired rows sit inside R22's banned 0.3–3.0 band: ikee 0.4, pikkut 0.9, qorrax 1.2,
vekka 2.0, drazzik 2.2. Three are the owner's own round-2 imports; drazzik was built to
the sheet's own named archetype. **All five are subsurface animals** — and the dune sea's
bimodal law is two-armed: *"the only passive defences are mass… and depth — a small
enough animal never leaves the cool sand. Both work; the middle does not"* (§4). A
mid-band body that lives UNDER the surface is defended by depth; the ban's target was
the mid-sized *surface* animal. ⛔ Evictions are stopped (owner, 2026-09-22), and this
sitting is exactly the per-biome venue the law names. **Recommendation: annotate the
depth-arm reading in the roster and def comments (the screecher precedent — in place,
with why), evict nothing** (§7 Q7). The one row that fits neither arm cleanly is the
ikee (0.4, surface micro-fauna whose port quietly tripled its roster bodySize) — §7 Q8
offers the one-word fix: re-measure it back toward the roster's 0.13.

### 2d. The free tier as built, and the holes — measured, then mostly left empty

Standalone (no Utinni, no SWBestiary), `RM_Stillsand` today carries **2 fauna
(RM_MirrorGiant bs 18.0 at 0.0005, RM_DustHusk bs 0.15 at 0.15), 0 plants, 0 pack
animals, forageability 0.0, animalDensity 0.1**. After §2b's nine moves it carries ~9
fauna + 2 flora — the weird bands are covered: giants (mirror giant, vozzik), grain
(kudda, ikee, dust husk), subsurface strikers (vekka, drazzik, qorrax), a burrower
(pikkut). 🔑 Unlike the Long Shade, most remaining thinness is **correct** — *"if the
dune sea's roster looks healthy, it is wrong"* — so this table fills only what a sheet
or ruling explicitly OWES, and leaves every other gap deliberately empty:

| owed by | what | filler (DRAFT names, Dune Sea accent: the Desert accent — doubled consonant, -a/-ik/-ok, 5–7 letters — said once into silence, with one long vowel) |
|---|---|---|
| roster §5 of the build item — the ONE confirmed unwired row | AA_SpinedGow, the heat-drinking plated grazer, owner-reviewed for this biome at 0.15 | **aurrok** (already drafted, batch 4d) — ⚠ donor bs 2.75 is mid-band and it is a SURFACE grazer, so wiring it as-is violates the law on both arms; §7 Q8 recommends growing the port to bs ≥4 (a small walking mountain) or declining the row |
| dune_sea amendment, RULED 2026-09-24 | **the sand busters** — the vanilla infestation trio rebuilt to sheet law, ONE planetary home here, incident banned planet-wide by the Utinni layer | **ruukka** (the eruptor — giant caste, bs ≥4), **oorrik** (the swarm — grain caste, bs ≤0.3), hive = a structure, "ruukka mound" (plain stage word). Invented bodies → RM_ tier; the planet-wide incident ban → UtinniPatches, per the amendment's own split. No build item exists yet — §7 Q9 |
| dune_sea §4 ⭐ + live item `DUNESEA_SHADE_COMMENSAL_MICROFAUNA_1` | grain-scale commensals riding the mirror giant's moving shadow | **eemmok** (bs ~0.1) — the item already binds the C# question (shade-follow, answered ONCE for three consumers); the def is art + wiring on top of that answer |
| Q11a's stand-alone bar + `DESERT_PACK_ANIMALS_FOR_TRADERS_1`'s own mechanism | all five pack animals are canon → standalone, `allowedPackAnimals` resolves empty and **no trader caravan ever generates** in the free tier | **vaalok** (bs ~4.0) — slow water-holding pack giant ("mass IS the water balance sheet", deep_desert §4); giant band, so it passes the size law where every donor pack candidate (Eopie 1.4, Jamel 1.9, Falumpaset 3.0) would not |
| deep_desert §8 + closed `EXTREME_DESERT_CAVERN_BEAST_1` | the Mandalorian cave-beast with prized massive eggs | ⚠ that item closed with criteria "a correctly-scoped item exists" — **no such successor item was found this pass** (items/ swept). The creature remains design-owed; §7 Q10. No name drafted — it should be coined with its cavern, not before |

All four new coins (ruukka, oorrik, eemmok, vaalok) are DRAFT, struck to the accent,
**checker- and Wookieepedia-unprobed this pass** (probe at or before the sitting — the
glowspore lesson: verify via the search API, never a guessed title). The mirror giant
and dust husk defNames are working names by their own headers' admission — both cite
`STILLSAND_SHIPPING_NAMES_1`, ⚠ **which does not exist in items/ or the ledger shards**
(swept this pass); §7 Q11 cards the names directly: mirror giant → **oommok** (DRAFT),
dust husk → **siidda** (DRAFT). Read aloud with the ruled set: kudda, ikee, vozzik,
pikkut, shakkir, drazzik, qorrax, aurrok, ruukka, oorrik, eemmok, vaalok, oommok,
siidda — one biome, said once into silence.

## 3. Flora

The signature flora is further along than most docs record — both invented plants are
BUILT with real deployed art (`EXTREME_DESERT_SIGNATURE_FLORA_1`, art 2026-09-24), and
the ollim's material already ships its ruled stat signature:

| plant | state | tier | what remains |
|---|---|---|---|
| **the ollim** (deep_desert §4b's shade tree) | ✅ BUILT (`RSW_Ollim`, real art) — and **`RSW_OllimWood` ships the ruled signature, MEASURED from its def this pass**: `StuffPower_Armor_Sharp` 0.15 against vanilla WoodLog's 0.54, heat axis inverted to near-immune, calibrated against measured vanilla values per its own header. The sheet's "armour that laughs at fire and folds to a hammer" is shipped, not owed | ⚠ Q11a move → `RM_Ollim` / `RM_OllimWood` (§7 Q1) | its CONTEXT: the sheet says the tree grows *among the bones of vast creatures, nursing the buried moisture* — a bone-field set piece (§4.6), and its shade is *rented* — tenants pay in waste and water (an ecology hook; `RM_TenantTruceExtension` is the shipped in-house truce shape to evaluate first, grep before inventing) |
| **the light-pipe nub** (dune_sea §4 — the visible biome) | ✅ BUILT (`RSW_LightPipeNub`, real art) | ⚠ Q11a move → `RM_LightPipeNub` | the harvest: dune_sea §7 names **optical-grade biosilica** ("real lenses, harvested by the handful, the only non-volcanic natural glass on the planet") — whether the def yields a distinct biosilica item is UNMEASURED this pass; if not, one harvest item + 1–2 recipes is pure XML (§7 Q12 confirms the item) |
| **the bloddle** | ✅ wired, eye-test MEASURED (0 green pixels on all three variants) | canon — stays Utinni forever | nothing |

**One NEW flora behaviour, sheet-owed, no new plant:** the **anhydrobiotic bloom**
(deep_desert §4: *"when a rare flood reaches this far the ground blooms within hours and
is dead again within days"*). This is an event, not a roster row — a short-lived bloom
flora family spawned by a trigger and self-terminating on the sheet's own clock.
`RM_IncidentWorker_BloomBurst` + `RM_BloomBurstExtension` already ship in-house — the
mechanism exists to evaluate before writing anything (§5). The bloom is the one legal
exception to "nothing green": the sheet's own hours-to-days carve-out, and its art stays
pale, not lush.

⛔ Deliberately NOT proposed: any ambient scrub, any dead-wood scatter (deep_desert §8:
there is NO fuel here — imported fuel is the tribes' treasure, and `TreeDead` was purged
from the roster on exactly this law), any third signature plant. Two plants and a scatter
of glass IS the flora of this biome at full strength.

## 4. The marquee

In the sheets' own register — giants-or-grains, the crossing as the experience, the sand
busters, buried archaeology, eggs-as-water — ranked, each with what it reuses and what it
costs. The Stillsand's engine luck is unusually good: **three of its five marquee ideas
have their expensive half already shipped in-house.**

### 4.0 If we only build three

| rank | idea | one line | why it is in the three |
|---|---|---|---|
| **1** | **§4.1 The sand busters** | The planet's only infestation biome: the ground you camped on erupts. | The only marquee already **owner-ruled** (dune_sea amendment, 2026-09-24) and still unfiled/unbuilt — making the ruled thing real outranks new ideas. Mechanics are vanilla's own (hive eruption, escalating waves); the work is bodies-to-sheet-law + biome gating + the Utinni planet-wide ban. |
| **2** | **§4.2 Crossing with the giant** | Following a walking mountain is how you cross the dune sea — its shadow is the only road. | The sheet's own ⭐ gameplay sentence. The C# keystone (follow-a-moving-shadow) is already bound to be answered ONCE for three consumers by the live commensal item; the caravan payoff lands on top of that single answer. |
| **3** | **§4.3 The buried record** | Anything the sand has taken comes back intact — the dayside's salvage game is pristine-and-buried. | Cheapest: the engines exist TWICE — `mandrake.rm.movingdunes` ships burial caches with a `BuryThingsAt` API, and Greentide ships the `RM_BuriedCache`/`DigOutBuried` dig loop. Wiring, loot tables and set pieces, almost no new C#. |

**If a slot must be cheaper, swap §4.4 eggs-as-water in for §4.2** — its trap half is
already shipped and its item half is pure XML.

### 4.1 The sand busters — the eruption you triggered

**Pitch.** The dune sea looks the same whether it is empty or loaded, and the player is
the detonator (§4). Vanilla's infestation event has its ONE planetary home here — banned
everywhere else by the Utinni scenario layer (ruled split: the biome mod owns the castes
and the biome-gated incident; UtinniPatches owns the planet-wide ban).

**What the player does.** Camps, builds, mines, drills — and learns that activity on dry
sand is a wager. An eruption (ruukka bursting from under the colony, oorrik waves after
it) is the biome's only mass threat, and the surface heals to blank sand afterward: an
eruption scar is the only mark it leaves. **What they get:** the emptiness made
load-bearing — dread with nothing visible to dread — plus the busters' own carcass
economy (giant chitin-plate in the sheet's mirror/ceramic palette). **What it costs:**
the trio's bodies must be rebuilt to sheet law — giant or grain, sun-axis polarised, no
nameable insect/spider silhouette (a nameable giant is this sheet's worst offence) — so
this is mostly an art-and-def bill, not code. **Engine surface:** vanilla infestation
mechanics reused; a biome gate on the incident; one Utinni patch suppressing it
planet-wide. **Cost:** small C#/XML + the real art bill for two castes and a mound.

### 4.2 Crossing with the giant — the moving shade is the road

**Pitch.** *"Following a giant is how you cross the dune sea. A caravan that stays in
the shade of a walking mountain travels; a caravan that does not, does not"* (§4 ⭐).

**What the player does.** Finds the region's oommok (mirror giant — already built, bs 18,
wired at 0.0005) and falls in on its shade side. Map-scale v1: pawns adjacent to the
giant's shaded flank read as sheltered (heat-load paused), the eemmok commensals boil
around their feet, and the giant's route — not the player's — decides where the crossing
goes. Its underside is *"wetter, cooler and busier than the entire landscape it
crosses"*: the one moving foraging ground in the biome. **What they get:** the only safe
transit of the deep dune, at the pace of a shadow on a sundial — slower, safer, and
going where the mountain is going. **What it costs:** tempo (the giant does not hurry
and does not detour) and proximity (everything else that needs shade is under there with
you). **Engine surface:** the shade-follow C# question — a per-host tracked shadow-caster
or `ShadeAt` + heuristic — is `DUNESEA_SHADE_COMMENSAL_MICROFAUNA_1`'s bound design
question, answered once for commensals + glitter-birds + this; the caravan payoff v1 is
map-scale only (the Long Shade's §4.7 priced the same split honestly: world-scale escort
is large, defer it). **Reuses:** `RM_MapComponent_ShadeGrid`,
`RM_ShadeSeekingWanderExtension`, `RM_TitanicCreatures` (footprint plumbing for bs-18
bodies — whether `RM_MirrorGiant` carries a `RM_TitanicExtension` is UNMEASURED, check
at build). **Cost:** the one shared C# answer + small wiring; art already owed elsewhere.

### 4.3 The buried record — pristine archaeology, sorted by the wind

**Pitch.** *"Anything buried is perfectly preserved"* (dune_sea §5); *"everything that
ever died out here is still here, intact and mummified"* (deep_desert §7). The dayside's
salvage prize is sealed, dry and uncorroded — the exact opposite game to the poison
forest's corroded standing ruins, and the most Jawa content this biome can carry.

**What the player does.** Reads the sand. Structures walk themselves out of the ground
over centuries (§8) — a hull emerging from a dune face, bright and half-in — and the
dunes' own migration uncovers and swallows finds on a real clock. Digs mummified fields,
buried caches, the wreck the last storm exposed. **What they get:** the scavenger
livelihood on the biome's own physics: steady, locatable, pristine — sealed containers,
intact machines, ancient corpses with gear. **What it costs:** everything is out on open
sand — no cover, full sightlines, and vibration is the dinner bell for everything
subsurface (digging is drumming; §4.1 and the strikers both key on exactly what
excavation does). **Engine surface:** `mandrake.rm.movingdunes` is BUILT and ships
`RM_Dunes_BuriedCache` + a `BuryThingsAt` API + plant choke — ⚠ but its
`BiomeBindings.xml` targets only vanilla `Desert`/`ExtremeDesert`, so the engine is
**wired to no Ash'karr biome at all today** (§7 Q12); Greentide separately ships the
`RM_BuriedCache`/`RM_JobDriver_DigOutBuried` dig loop as the worked pattern. What's new:
loot tables in this biome's register, a genstep scattering emergence set pieces
(`RM_GenStep_PlacedSetPieces` is the shipped shape), the ollim bone-field set piece
(§3). **Cost:** small — bindings, XML, set pieces; the engines exist twice over.

### 4.4 Eggs-as-water — the canteen and the trap

**Pitch.** *"A large egg is portable water in a rigid shell… not food, drink you can
carry"* — and *"some eggs are birth traps"* (deep_desert §4).

**What the player does.** Raids clutches to provision the crossing — a real hydration
item with mass, the biome's only portable water source — knowing some clutches are
armed: approached, they hatch violently, and the newborn tries to drink the intruder.
**What they get:** the crossing's water math made playable (caravan range = eggs
carried), plus the sheet's cruellest bargain (the richest clutch is the likeliest trap).
**What it costs:** every clutch raid is a wager, and the mother's economics (water
invested in a weapon) mean trap density rises exactly where water is scarcest. **Engine
surface:** the trap half is SHIPPED — drazzik's egg-trap clutch
(`DRUM_LURE_PREDATOR_BUILD_1`) and the `ProximityHatch` mod (`RM_ProximityHatchMod`,
hatch-on-approach) both exist; the canteen half is one ingestible item family + FlowWorks
hookup if bottled. **Cost:** near zero C#; XML + item art.

### 4.5 The solar offer — infinite power, infinite logistics

**Pitch.** *"Solar power at 100% uptime, forever… infinite power in exchange for
infinite logistics"* (dune_sea §7 ⭐) — the single strongest reason to plant anything
here, and the biome's whole colony fantasy: a power station in the middle of nothing.

**What the player does.** Builds the panel farm nowhere else on the planet can host, and
pays for it in everything else: no water, no soil, no fuel, no cover, every input
imported across the crossing (§4.2's road), every vibration a dinner bell. **What they
get:** the campaign's energy anchor — power-hungry industry (and the gravship's
appetite) sited here on purpose. **What it costs:** the logistics ARE the gameplay; the
colony is a supply problem with a generator attached. **Engine surface:** ⚠ one
UNMEASURED gate — vanilla `CompPowerPlantSolar` reads the map's sky/daylight state, and
this biome's eternal noon will ship as a permanent GameCondition glow lock (§5); whether
solar output tracks that override or the raw day-night clock must be read from the
decompile before this is promised. If it tracks: zero build. If not: one small Harmony
patch. **Cost:** near zero to small.

### 4.6 What is deliberately NOT marquee here

The **sarlacc** is its own accepted, owner-ruled build (`SARLACC_HABITAT_BUILD_1`,
RSW-tier mod, design accepted whole 2026-09-12) — cited as this biome's dungeon anchor,
not re-designed or re-ranked here. The **green line** is the painting pass's drama, not
mod content. **Cavern authoring** is real and owed (deep_desert §8 calls it "the real
ecosystems") but is its own substantial work by the sheet's own note — §7 Q10 re-files
it rather than folding it in. And no idea above adds ambient life to the surface: the
`EXTREME_DESERT_UNRULED_VERMIN_1` ruling stands — *"that emptiness is the intended
outcome… what you meet there should be something that arrived."*

## 5. Weather / terrain / mechanics feasibility

*(to fill)*

## 6. Ship contribution row

*(to fill)*

## 7. Card agenda

*(to fill)*
