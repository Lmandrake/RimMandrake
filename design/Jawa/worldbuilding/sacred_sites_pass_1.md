<!-- status: live -->
# SACRED SITES — the F16 tile pass (SACRED_SITES_PASS_1)

_Spec-only pass, filed per `salvation_engine_review.md` F16 ("Full adoption, PLUS SACRED
SITES... Owed: a deep inspiration pass over all tile contents, mutators, landforms, and
features. Plus the tidal day/night split") and its essay two sections below: **geography
IS theology** — Sh'kaar owns the sunward half, Ishko the dark half, the terminator is
their eternal battlefield; every tile should get a divine reading; landing-site selection
becomes a theological act. Owner ruling on record; this doc is the deep-inspiration pass
it asked for. Linked from `divine_satiation_engine.md`'s new §11 pointer. Nothing here
edits the frozen map — Ash'karr's tiles, biomes, landmarks and mutators are read, not
touched (`the_one_map.md`, `ASHKARR_WORLD_DEFINITION.md` remain the numeric source of
record; every figure below is quoted from them, not re-measured)._

**What this is not:** a build. The engine hook that reads a tile and injects judgment
text at landing is real C# work against a live bridge (§5) and files as its own item when
the owner calls it. This pass is the theology + the annotation scheme + the flavor-text
drafts that hook would consume.

---

## 1. The annotation scheme — keyed on BIOME/MUTATOR/LANDMARK, not region name

**First finding, and it changes the design:** `REGIONS_THAT_LIE.md` (2026-08-23 audit)
swept all 71 named regions and found 13 are internally incoherent — Dune Sea alone spans
**13 different biomes**, Anvil spans 10, Nightspill 9, Twilight Sea 8. A named region is a
label-placement polygon (`WB_MapLabelFeature`), not a homogeneous zone. **⇒ The god-read
of a tile must key off that tile's own biome + active TileMutatorDefs + any LandmarkDef on
it — never off the region name it happens to fall inside.** The region name still supplies
toponymy for the judgment sentence ("you have landed in the Dune Sea"), but never decides
*whose* country the tile is.

This is also why the scheme is a **function, not a table of 21,872 rows**: `god_of(tile) =
f(biome, mutators, landmark, arc, temperature)`. Below is that function's rule set, in
priority order (a landmark on the tile wins over a bare biome read; a biome read wins over
the arc-band default).

### 1a. Landmark-level reads (highest priority — a landmark is always a strong claim)

Drawn from the curated ~16-entry gazetteer table in `ASHKARR_WORLD_DEFINITION.md` §13.3 —
**every defName below is one already named there**, none invented for this pass:

| landmark (defName) | where it is sited | primary god | why | secondary / contest |
|---|---|---|---|---|
| `Oasis` | `ZBiome_DesertOasis` tiles (227 painted, §5b) | **Oomo** | the archetype F16 itself names | — |
| `AncientQuarry` | The Ore Moot | **Rekko** | salvage/history — "the mine the sandcrawlers were stolen from" | Mob'Unloo (the theft itself is his art too) |
| `Ruins` / `AbandonedColonyOutlander` / `AbandonedColonyTribal` | Junkers' fields, the dead gravship near any future start tile | **Rekko** | the discarded given a second hand | **Ta'Baa** — canon: "old battlefields and lost settlements... holy ground of vindication" (§2.0b ⑥) pleases him *by the same tile*, for the opposite reason |
| `sw_Sarlacc` (Sarlacc Ground) | wherever the mod's legality gate lands it | **Zizzik** | a pit that eats the unwary is the wrong spark made literal — betrayal by the ground itself | Ishko (ambush from below is still ambush) |
| `AncientLaunchSite` | Rust Cathedral cluster **and** tile 4000 (Scorch), the Ashfall Road's origin | contested | at Rust Cathedral it reads **Ohm** (mechanoid, his machine-country); at Scorch, clean of mechanoid claim, it reads **Ta'Baa** (a launch site is his by function alone) | **worked example of the doctrine below** — same defName, two gods, decided by co-located mutators |
| `AncientGarrison` | Rust Cathedral cluster **and** the Kiln endpoint of the Ashfall Road (tile 20514) | **Ozzik** on the Ashfall Road instance | "a tarnished crown half-buried in sand; a monument no one remembers building" (§2.0b ⑨) is a description of this exact object | Ohm at the Rust Cathedral instance |
| `LavaLake` / `LavaCrater` | Scald rim volcanics | **Sh'kaar** | fire, killing heat, the war-sun's forge | — |
| `AncientHeatVent` | the deep waste | **Sh'kaar** | heat plume on the hottest world — "the right kind of joke" (§13.3's own phrase) | Ozzik (a vent is also old machinery, ambition's wreckage) |
| `DryLake` / `VEE_SaltPlains` | `Wasteland` salt pans | **Zizzik** | the contamination-class ground (§6c) — poisoned, broken, an old accident, not living horror | — |
| `Valley` (Scald Gate) | the one breach in the Spine | **Mob'Unloo** | the Empire itself uses it as a chokepoint (§7 faction table) — a pass is a toll before it is anything else | Ta'Baa (a pass is also an escape route) |

### 1b. Biome-class reads (where no landmark is present — the default fallback)

Grounded in `ASHKARR_WORLD_DEFINITION.md` §5b's census and §6c's two-legacy table.
Figures are the doc's last recorded pass, not re-measured for this spec:

| god | biome/class | grounding |
|---|---|---|
| **Oomo** | `Ocean` · `Lake` · `SeaIce` · `ZBiome_DesertOasis` (water, 5.19% liquid / 6.46% incl-ice, canon.yml `planet.water_pct`) | §3③'s existing terrain coupling ("a heavily-watered tile is a standing small PLUS") — this pass generalizes what already exists for him |
| **Rekko** | any tile carrying `Ruins`/salvage-flavored dressing; the Junkers' and Blackstar's holdings ("road junctions and ruins; they follow the money") | his domain is the discarded object, not a biome — reads through landmarks/settlements, not terrain |
| **Mob'Unloo** | road tiles themselves (`StoneRoad`/`DirtRoad`/`DirtPath` — the living network, §8), and the 11 non-palace Hutt holdings that "hold no water at all... a lesser Hutt who cannot own a well sells a SERVICE instead" | F16's own line: "Mob'Unloo's the trade roads" |
| **Ta'Baa** | `ExtremeDesert`/`Desert` in the open Dune Sea band (arc 20–40, "the vast unbroken tract... emptiness is a texture") — open sky with nothing to hide behind | F16: "Ta'Baa's the open sand between" |
| **Zizzik** | `Wasteland` (7.87%, 1,721 tiles) and the `AB_MechanoidIntrusion` pollution HALO (four-ring falloff, 303 tiles outside the 236-tile core) — the **contamination** class per §6c, "the weapon was used and left," not the living bioweapon class | F16: "Zizzik's the broken places"; the doc's own two-legacy split does the sorting for us |
| **Sh'kaar** | the dayside proper generally, and specifically the volcanic province (`Volcano`·`LavaField`·`AB_PyroclasticConflagration`·`Scarlands`·`AB_TarPits`, all one cluster on the Scald rim) and the substellar Anvil/Scorch regions (arc <20) | canon V.3: "one unsetting sun... half the planet permanently his"; §2.0b ⑧: "a war-sun" |
| **Ishko** | the nightside stack past the terminator: `HorrorWastes` (~468 tiles, −55…−30 °C), `AB_RockyCrags`'s −30…0 °C band (1,118 tiles), `AB_PropaneLakes`/`BMT_CrystalCaverns` (alien-chemistry, <−55 °C), and any `Cavern`-class mutator underground | canon §2.0b ①: "the dark terrains he loves are, by design, seeded with fleshbeast horrors" — his domain is already the nightside's danger, this pass names the tile classes |
| **Ohm** | `AB_MechanoidIntrusion` core (236 tiles, the Rust Cathedral), and any Free Droid Enclave settlement tile | the machine-god's own temple; 8 of 12 Enclave seats already stand on this ground (§7d) |
| **Ozzik** | the `AncientAsphaltHighway` (the Ashfall Road, 37 of 62 surviving edges) and its three named anchor ruins — "laid by people who did not care about shade, which is why it is dead" (§8) | reads his epithet almost verbatim: grandeur that outran its own survival |

### 1c. What is honestly ungrounded

Two gods have a **thinner** geography and this pass says so rather than papering over it:
- **Ishko** has no *curated LandmarkDef* of his own in the §13.3 table (his read above is
  biome-class only). §13's own shortlist names ~62 legal landmarks against ~16 hand-placed
  so far — a Cavern-class, ice-excluded def almost certainly exists in the unused ~46, but
  this pass does not name one it has not verified (no defName is guessed here per project
  rule). **Flagged for the build item (§5): pull the actual candidate from the live
  shortlist with RimSage before authoring anything.**
- **Mob'Unloo** owns infrastructure, not terrain — his "landmark" is a settlement/road tag,
  not a LandmarkDef at all, so §1a's `Valley` entry is the only terrain object that reads
  as his; the rest of his geography is functional (§1b).

---

## 2. Contested tiles are the good ones, not a bug

`divine_satiation_engine.md` §2.0d already states the doctrine this needs: *"No act is
clean — the faith is a tug-of-war, not a reward menu."* The tile pass should be read the
same way. Four worked contests, all grounded in real, already-authored geography:

- **The Scald.** Oomo's water (the planet's only large freshwater-adjacent body, feeding
  two Deepwater Compact seats and two Wildsteam Clan jungle holds) sits inside "the
  planet's only volcanic province" (§13.5) — Sh'kaar's fire cooks the lake that keeps the
  desert's one water-rich pocket alive. A landing on a Scald shore tile should stage BOTH
  claims, not pick one — exactly the Council-of-Voices mechanism (§5c of the engine doc)
  already built for ritual arguments, here triggered by geography instead of a rite.
- **Rust Cathedral.** Ohm's temple (the mechanoid core, his hands rebuilt in a place he can
  actually stand) is also `AB_MechanoidIntrusion`'s pollution halo — Zizzik's contamination
  class — and it is "permanently at war" (§7 faction table), which is Sh'kaar's business
  too. Three gods have a legitimate claim on one biome cluster.
- **`AncientLaunchSite`, twice.** See §1a — the identical defName reads Ohm at one
  coordinate and Ta'Baa at another, purely from what else shares the tile. This is the
  cleanest demonstration that the scheme is a function of co-located data, not a lookup
  table keyed on defName alone.
- **The Kiln.** A blast crater — five `Wasteland` tiles inside 878 tiles of otherwise
  ordinary sand (§13.3) — where a Hutt cargo manifest "cleared by the people whose job was
  to clear it" detonated an entire settlement. Zizzik's read (the wrong spark, the
  catastrophic accident) is primary; Mob'Unloo has a real secondary claim (a trade gone
  fatally wrong, a debt the Cartel is still paying in reputation). The four Homestead
  farms ringing it but never settling the core ("people who arrived afterwards, farm the
  edge of it, and do not dig in the middle") are already, unintentionally, the correct
  theological posture toward Zizzik's ground: work its margin, never its heart.

---

## 3. New / reinterpreted landmark kinds, one read per god

Per F16: "new landmark kinds (or reinterpretations of existing ones)." Ranked by cost —
**reinterpretation** (tag an existing, already-legal LandmarkDef with a patron-god field
for the judgment system to read; no new XML, no new art) is near-free and is what most of
§1a already is. **New content** (an unclaimed LandmarkDef pulled from the unused ~46-item
shortlist, or a bespoke def) is real authoring + testing and is flagged as such.

| god | proposal | cost |
|---|---|---|
| Oomo | reinterpret `Oasis` as his archetype site — the F16 example itself | free (data tag only) |
| Rekko | reinterpret `AncientQuarry`/`Ruins`-class as his shrines | free |
| Mob'Unloo | tag road-junction tiles and non-palace Hutt service-holdings as his sites (no LandmarkDef object needed — settlement/road data already exists) | free |
| Ta'Baa | reinterpret the Scorch `AncientLaunchSite` instance as his | free |
| Ozzik | reinterpret the `AncientAsphaltHighway` + its two grand ruin anchors as his monument-road | free |
| Sh'kaar | reinterpret `LavaLake`/`LavaCrater`/`AncientHeatVent` as his forge-sites | free |
| Zizzik | reinterpret `sw_Sarlacc` + `DryLake`/`VEE_SaltPlains` as his broken-ground sites | free |
| Ohm | reinterpret the `AB_MechanoidIntrusion` core as his temple (already lore-true — the Enclaves already worship there) | free |
| Ishko | **new content needed** — no curated cavern/dark landmark is named yet; pull a candidate from the ~46 unused-but-legal landmarks (§13.4) and verify it against the live shortlist before authoring | real work — build item |

---

## 4. The tidal day/night split, mapped onto THIS map's real numbers

`ASHKARR_WORLD_DEFINITION.md` §1–§2 fixes the convention: **arc 0 = substellar noon, arc
90 = terminator, arc 180 = antistellar midnight**, and gives the ruled temperature curve
(+70 °C at arc 0, +14 °C at arc 90, −80 °C at arc 180). Canon ruling V.3
(`salvation_engine_review.md`) already settled the theology half: **one unsetting sun,
Sh'kaar's, owning roughly half the planet.** This pass draws the concrete band on the
actual map:

- **Sh'kaar's undisputed country — arc 0 to roughly 70–75.** This is where the dayside
  rule holds cleanly: rivers exist ONLY here (highest arc carrying any river is **71.52**,
  zero river tiles beyond — §4 rule 7), the volcanic province sits at its hot end, and the
  Anvil/Scorch/Rust Cathedral all fall inside it (Anvil is explicitly `arc<20`, §3).
- **The terminator battlefield — arc roughly 74 to 100.** This is not a guess band; it is
  where the map's own data stops behaving like either side cleanly: the mycoid belt begins
  (`AB_MycoticJungle` is 1,874 of 1,939 tiles at arc > 82 — a hard onset, not a gradient),
  Twilight Sea (centre arc 91) and Grey Sea (centre arc 92) both sit here, and
  `AB_GelatinousSuperorganism` is explicitly ruled "on the terminator, patches only" (§6).
  Twilight Crags (~104–114) and Gray Crags (~106–116) are the named ranges just past this
  band, on the frontier. **This band is where every landing judgment should stage a
  Council argument (§5c of the engine doc) rather than name one god** — the mechanism
  already exists, it has simply never been triggered by geography instead of a rite.
- **Ishko's undisputed country — arc past ~110–120 to 180.** `HorrorWastes` (−55…−30 °C,
  arc 124–144) is his frontier proper; deep nightside (`Umbra`, arc>152; `AB_RockyCrags`'
  cold end; `AB_PropaneLakes`/`BMT_CrystalCaverns` below −55 °C) is his heartland, ending
  at the antistellar Long Dark.

**Mechanical/thematic hooks this supports, spec-only (no new mechanics required to state
them, C# required to wire them — see §5):**
1. A ship sitting on a dayside (arc <74) map for a stretch feeds Sh'kaar's battle-
   escalation meter (§3⑧ of the engine doc) a small continuous nudge, the same way sitting
   on a watered tile already nudges Oomo (§3③) — generalizing an existing hook rather than
   inventing a new one.
2. A ship sitting on a nightside (arc >100) map gets a small continuous Ishko satiation
   drift, the concealment god's mirror of the same mechanism — **this is the one F16
   claims already exists and generalizes**; it was not found written anywhere in the
   current matrix/engine text during this pass, so treat it as PROPOSED, not confirmed
   pre-existing (flagging rather than asserting, per project practice).
3. Landing IN the terminator band (§4, arc 74–100) is the only band that should trigger
   the Council mechanism at landing rather than a single-god judgment line — mechanically
   free (the Council-staging code already exists per §5c) once the trigger event exists
   (§5's build item).
4. "A pilgrimage sunward is a literal walk into the god of inevitability's mouth" (F16's
   own line) — the judgment text for any landing at arc <30 should say so outright; drafted
   in §5 below.

---

## 5. Landing-judgment flavor text — drafted for real (safe, bounded, no new mechanics)

Voice per the 2026-08-30 Narrator ruling (`divine_satiation_engine.md`, "Ruling
2026-08-30 — the Narrator"): hidden, non-egoic, second person, free to reference unrevealed
lore, Into-the-Woods register. These are landing-only openers — the first line the player
reads after `Page_SelectStartingSite`, before any other judgment content. Six drafted,
covering the extremes and two contested cases from §2:

> **Deep dayside (arc <30, e.g. Anvil/Scorch/Rust Cathedral vicinity):**
> "The ship settles onto ground that has never once been shadowed. Something vast and
> white-hot notes your arrival without hurry — it has always known you would come here
> eventually. Everyone does, in the end."

> **Volcanic Sh'kaar site (Scald rim):**
> "Steam rises where the mountain bleeds. This is a forge, not a shore — the water here was
> never meant for drinking, only for boiling. Something in the rock is pleased that you
> noticed the difference."

> **Oasis (Oomo archetype):**
> "A single trembling drop holds itself against the whole desert's want to drink it. The
> ship's hull throws its shadow across the water and does not spill a drop of its own — a
> good beginning, and it is noticed as one."

> **Terminator / contested (Twilight Sea, Grey Sea, mycoid belt):**
> "Two arguments are already being made about this ground before you have unpacked a
> single crate — one voice claims the long light, the other the long dark, and neither will
> yield the seam between them. You have landed in the argument itself."

> **Deep nightside (Ishko country, HorrorWastes/Umbra):**
> "No sun has ever touched this ground and none ever will. A pair of eyes that were already
> here before you arrived seem, for a moment, almost approving — you have found the one
> place on this world that agrees with hiding."

> **The Kiln (Zizzik/Mob'Unloo contest):**
> "Five tiles of dead flat ground sit inside eight hundred tiles of ordinary sand, and nothing
> has grown here since a manifest was cleared that should never have been signed. The
> rattle you cannot locate is quieter here than anywhere else on the planet — as if it
> already did its worst work in this one place and is, for now, satisfied."

These six are reusable templates (biome/landmark-class keyed, not tile-ID keyed) and would
be the seed set for a full pass once the C# hook exists to select among them.

---

## 6. What needs a build item — spec'd, not built

**The hook.** `Page_SelectStartingSite` (and the corresponding Playing-state re-check on
every subsequent launch/relocation, since Ta'Baa's whole theology is repeated departures)
needs a tile-read that runs the §1 function and returns a primary god (or a contested
pair, for the terminator band and the four §2 worked cases) before the map itself loads.
This is the same shape of call the `rimworld-world-editing` skill already documents for
world-state reads (`jawa/world_tile_get`-class tools reach `Find.WorldGrid` from either
`Page_SelectStartingSite` or Playing) — **no new bridge surface is obviously required**,
only a new consumer of tile fields that are already read for other purposes (biome,
mutators, landmark, arc).

**Data the hook needs, all of it already on the tile or one hop away:**
- biome defName (already on every tile)
- active `TileMutatorDef`s on the tile (already read by `jawa/world_mutators_get`)
- any `LandmarkDef` on the tile (already read by the landmarks API, §12.5 of the world def)
- arc (already computed at import time, §1 of the world def)
- optionally: the 71-region label, for TOPONYMY ONLY in the output sentence, never for the
  god decision (§1's caution)

**What is genuinely new engineering, not spec:**
- The function itself as C# (or a data table it reads) implementing §1a/§1b/§2's priority
  order and contest resolution.
- Wiring its output into whatever surfaces the Narrator's landing text today (the
  "judgement at landing" mechanic sketched 2026-08-29, `divine_satiation_engine.md`
  "Design sketch 2026-08-29 — 'in front'" — that sketch already wants a landing judgment
  for PAST-MAP performance; this pass's judgment is a *different*, earlier one — whose
  country is this — and the two should probably share one letter rather than double up).
- The two continuous ambient nudges proposed in §4 (Sh'kaar/Ishko arc-residency, mirroring
  Oomo's existing §3③ terrain coupling) — these touch the satiation engine's core loop and
  should not be built blind.

None of this is built here. It is precise enough that a FOUNDRY item can pick it up
without re-deriving the geography.

---

## Status

Spec-only, per the review doc's own framing of this item. `SACRED_SITES_PASS_1` stays
`doing` pending the owner's build call. Nothing on the frozen map was touched; every
figure above is quoted from `ASHKARR_WORLD_DEFINITION.md` / `the_one_map.md` /
`REGIONS_THAT_LIE.md`, not re-measured.
