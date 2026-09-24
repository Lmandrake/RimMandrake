# The Weeping Stones — flora roster

_Drafted by a Fable design subagent, 2026-09-24, against the frozen sheet, for
`WEEPING_STONES_DESIGN_SITTING_1`._

**Status: RULED 2026-09-24 (owner sitting, cards + typed words). Nothing authored yet.**

## ⚖️ Rulings, 2026-09-24 sitting

1. **Farmed crop: YES — the dewgourd.** Owner, typed, verbatim: *"Yes and it
   should be a large melon like gourd that takes a long time to grow but is
   then worth a lot of food and keeps for a long time."* Name **Dewgourd**
   taken by question card. Row 9 below. The bladderquill stays a separate
   wild forage plant, unchanged.
2. **Tree: keep, scarce — renamed ROCKFINGER.** Owner, typed, verbatim: *"Yes
   scarce but rename to Rimclaw due to its tendency to cast long terrible
   shadows from the rims of tall rocks. Make it look very scraggly and
   hardy."* — then, on BENCH reporting that `RG_Rimclaw` is already a live
   animal label (ReGrowth donor, cast Desert|Scarlands): *"Tree turns to
   Rockfinger"* (typed). Row 6 rewritten to his brief: rim-of-tall-rocks
   placement, long terrible shadows, scraggly and hardy.
3. **`AB_GreenRockFern`: replace with our own invented plant** (decision
   taken by question card) — `RM_Shadefern`, row 3b. No donor flora remains.
4. **Name collisions: CHECKED 2026-09-24** — all eight §2 coinages plus
   dewgourd/rockfinger/shadefern swept against design/ + src/ (probes korrum
   43, stoneback 87). Only real hit was rimclaw (the animal), resolved above.
   Prior `mirrik`/`weep-mat` hits are this biome's own earlier commissions.

Subject: the `RM_WeepingStones` biome mod (RM_ tier per Q12–Q15; live def today is
`RUT_WeepingStones`). Companion doc: `weeping_stones_fauna_roster_2026-09-24.md`.
Frozen sheet: `weeping_stones.md` — its rulings bind; this roster adds detail and
never changes one. The ruled roster JSON
(`rosters/weeping_stones.json`, 2026-09-09) is INPUT: its kept rows and purges
stand; nothing here re-adjudicates them.

## READ FIRST — every new plant on this page is OURS and INVENTED

Per the owner's standing method (2026-09-23, Webwork/Fever Wood rosters): invent
the complete roster first; look for Star Wars injection opportunistically
afterward, on the Utinni layer, additively. Every new row here is **`RM_` tier —
franchise-free, invented, cast inline** (Q11a, `biome_mod_architecture.md` §7).
The free mod must be **rich enough to stand alone**; campaign patches only add.
"Star Wars style" naming is NOT Star Wars IP — an invented exotic name lives in
the RM_ tier freely.

🔴 **Two hard laws govern every row (sheet §4–§6):**

1. **The blade law.** Plants grow as blades, not bushes — upright fins of leaf
   facing the prevailing wind, drip-tips feeding their own roots. Mats on the
   stone are ridged like corduroy, every ridge square to the sea-wind. A bushy
   leaf-crown fails §5's comb rule (the roster JSON already purged
   `Plant_Smokeleaf_Wild` on exactly this).
2. **R21 — condensate, never rain.** No row's water story is rainfall. Every
   plant here drinks the wind: combed film, drip-tips, seep lines, pool margins.
   A description that drinks rain violates the sheet.

And the standing bans: no Earth-nameable species (the JSON purged nineteen rows,
mostly palms, on this), no snow story, nothing that lives on soil — **everything
lives on stone-shade real estate**: the cold faces, the overhangs, the seep
lines. Fertility follows the patch-makers; the *life* follows the shade.

### The silhouette brief is the specification

Same rule as the sibling rosters: the **silhouette FORM** column is what art is
commissioned against. Every form here is a variation on the biome's one
silhouette — **the upright comb** — and each row must still be nameable at a
glance from a top-down sprite. The concentric-rings map read (water → green →
scrub → sand) is the plan view; these combs are the elevation.

---

## The dew ecology in one paragraph

Damp sea-wind forced up over high pale stone drops its water on the cold shaded
faces — combed from moving air, never rained. So the flora is arranged by
*catch*: film-lickers flat on the weep-lines, ridge-mats corduroying the cold
faces, blade-fins standing square to the wind on the shoulders, a hanging fringe
under every overhang drip-feeding its own catch-pool, and the green ring at each
true pool where everything peaks. The seep oases (§2b, Cratercrown/Anvil) invert
it: fed from below, mineral-tasting, their flora is steam-country strange. The
flora is also the biome's *plumbing diagram*: what grows where tells you where
the wind runs wet, where the stone weeps, and where the water stands.

---

## 1. The rulings this roster serves

| ruling | source | what the roster owes it |
|---|---|---|
| **The blade law — upright fins, corduroy mats** | sheet §4, §5 hard rule | every row's FORM is a comb variant; zero bushes, zero crowns |
| **Condensate, never rain** | R21; sheet §3, §6 | every row's water story is wind-comb, drip, seep, or pool — no rain-drinker |
| **Life on stone-shade, not soil** | sheet §4 | rows keyed to cold faces, overhangs, seep lines, pool margins — never open sand meadow |
| **No Earth-nameable flora** | sheet §6; owner card 2026-09-09 (the date-palm example) | zero Earth-nameable rows; the JSON's 19 purges stand |
| **Bladder-fruit re-points the forage economy** | sheet §11; JSON `new_defs` | one row is the forage staple that re-points donor `foragedFood` off RawAgave |
| **Concentric rings — the most legible tile on the world** | sheet §9 | commonalities banded by ring: pool green > seep lines > wind shoulders > outer scrub |
| **Seep oases are their own magic** | sheet §2b | one row grows ONLY at seep oases; the seep-salt tie (§11) |
| **The free mod stands rich alone** | Q11a | ten invented rows, no donor needed |

## 2. Rows — the blade country (8 invented plants)

### 2a. The ground cover — what makes the rings legible (3 rows)

| # | defName | label | silhouette FORM | what it looks like | job | size / commonality | mechanism | art |
|---|---|---|---|---|---|---|---|---|
| 1 | `RM_Dewblade` | dewblade | **sparse tuft of parallel upright leaf-fins, all facing ONE way** | Shin-high tufts of flat grey-green blades standing edge-on to the sun and face-on to the wind, each blade tipped with a drip-point that feeds its own root. Whole hillsides of them align like iron filings — the wind made visible. | **The baseline green** — the grass-analog and graze base. Its alignment is free art: every dewblade on a map faces the same way, so the prevailing wind reads at a glance. Denser toward water: the middle band of the concentric rings. | small / 1.0 (the commonest plant) | none; `growMinGlow` per vanilla grass, fertility rides the donor patch-makers | **OWED** |
| 2 | `RM_Weepmat` | weep-mat | **flat corduroy mat, ridges all square to one axis** | A dark green-black mat hugging the cold stone faces, ridged like corduroy, every ridge square to the sea-wind, glistening along the weep-lines. Sheet-named (§4, §11 "weep-mats"). | **The signature mark made flora** — it grows exactly where the stone weeps, so a weep-mat IS the wet black streak's green echo, and a face without one is a face that has gone dry. Graze for the sillik; walkable moss register. | small-flat / 0.7 on shade/weep terrain, 0 in the open | placement keyed to shade — ✅ **`RM_MapComponent_ShadeGrid`** (CreatureBehaviors) already computes a shade grid; a GenStep/placement read of it is small wiring, not new machinery | **OWED** |
| 3 | `RM_Verdimoss` | verdimoss | **low moss bosses in beaded rows, blue-green with metallic sheen** | Cushions of blue-green moss growing in beaded lines along seep cracks — and over the ancient vane arrays, where it takes the color of oxidised bronze. The sheet's palette row made a plant: "verdigris where metal meets moss." | **The relic-dresser.** It marks seep lines and it *ages the machines* — every ruin in the biome is half-mossed, which is the sacred ambiguity (§9: is the machine alive?). Zero yield; pure register, cheap density. | tiny / 0.6 on stone and ruin-adjacent cells | none; decorative-density | **OWED** |
| 3b | `RM_Shadefern` | shadefern | **one-sided fern fronds all combed to the dark side of the rock** (RULED 2026-09-24 — replaces donor `AB_GreenRockFern`) | A deep-green fern growing only on the shaded face of standing stone, every frond swept to the cold side as if combed, pale rachis catching what light bounces in. Takes the donor fern's kept-in-role slot under our own name. | **The stone-shade fern niche** the ruled JSON kept — now donor-free. Marks which side of a rock is the cold side at a glance. | small / 0.4, shade-keyed (same `RM_MapComponent_ShadeGrid` read as the weep-mat) | none | **OWED** |

### 2b. The economy — what a colony harvests (3 rows)

| # | defName | label | silhouette FORM | what it looks like | job | size / commonality | mechanism | art |
|---|---|---|---|---|---|---|---|---|
| 4 | `RM_Bladderquill` | bladderquill | **fan of hollow upright quills, each swollen at the base like a waterskin** | A knee-high fan of stiff translucent quills, each fat at the base with stored water, standing in arcs along the green ring. Cut a quill and it sloshes. | 🔑 **The forage staple** — bears the **bladder-fruit** (sheet §11: food and drink in one object). This is the row that re-points the donor's `foragedFood` off RawAgave. The visible promise of the green ring: where bladderquill stands, nobody dies thirsty. | small-med / 0.5, banded to the pool ring | harvest yields `RM_BladderFruit` (item def, sheet-named); no C# | **OWED** |
| 5 | `RM_Salvecomb` | salvecomb | **single arched frond with teeth on one edge — a comb, literally** | One waist-high arched frond per plant, serrated along its windward edge like a comb's teeth, silver-downy where it combs the fog. Grows alone in shade lines. | **The medicine plant** — the healroot the donor swap evicted, ours. Its down mats wick clean condensate; field dressing is the fiction. Rare enough to be worth a walk under the overhangs. | small / 0.2, shade-keyed | none; healroot-pattern PlantDef | **OWED** |
| 6 | `RM_Rockfinger` | rockfinger | **scraggly clawed tree on a rock rim, all its reach on one side — a long terrible shadow made of wood** (RULED 2026-09-24; was `RM_Sailfin`) | Owner's brief, verbatim: *"long terrible shadows from the rims of tall rocks… very scraggly and hardy."* A gnarled, wind-stripped hardwood rooted in the rim cracks of the tall stone, branches clawing out over the drop, bark pale as the stone it grips. At this biome's low sun its shadow runs down the rock face and across the ground for many times its height — you meet the shadow before the tree. | ⭐ **The wood economy and the dread of the skyline.** Slow, scattered, precious timber in high stone country; a felled rockfinger is a caravan event. | large / 0.15, rim/high-stone keyed | none blocking; long growDays | **OWED** |

### 2c. The strange — overhangs and seep oases (2 rows)

| # | defName | label | silhouette FORM | what it looks like | job | size / commonality | mechanism | art |
|---|---|---|---|---|---|---|---|---|
| 7 | `RM_Dripfringe` | dripfringe | **hanging fringe of downward comb-teeth under an overhang lip** | A curtain of dark fleshy fingers hanging from overhang lips and cistern mouths, each finger a drip-tip, forever ticking water into the catch-pool below. The comb inverted — teeth down. | **The overhang register** — where the biome's gloom-and-glare light rule lives (§9: hard glare above, cool gloom under the overhangs, a green fringe between). Marks natural catch-pools and cistern shafts; a dripfringe curtain over a dark mouth means water below. | small / 0.3, overhang/rock-edge keyed | placement at rock-edge cells (GenStep scatter rule; no per-tick C#) | **OWED** |
| 8 | `RM_Steamfrond` | steamfrond | **spiral of pale fronds around a central vent-hole, crusted white at the rim** | A rosette of mineral-pale fronds spiraled around a breathing vent, rims crusted with white salt bloom. Grows ONLY at the seep oases (§2b) — the green eye in open nothing is a steamfrond ring before it is anything else. | 🔑 **The seep-oasis signature.** Where the water rises from below, the flora is fed from below too — mineral-tasting, wrong-colored, magical. Harvest scrapes **seep-salt** (sheet §11: preservative and spice with the underworld's taste; only source, the magical ones). | small-med / 0.1, seep-oasis cells only | placement keyed to seep/vent features (`VAPOR_EMITTER_PLACEMENT_1` siting is CLOSED — the cells exist to key on); salt yield is an item def | **OWED** |

### 2d. The farm — the ruled crop (1 row, RULED 2026-09-24)

| # | defName | label | silhouette FORM | what it looks like | job | size / commonality | mechanism | art |
|---|---|---|---|---|---|---|---|---|
| 9 | `RM_Dewgourd` | dewgourd | **one huge pale gourd squatting under a small comb of shade-leaves** | Owner's spec, verbatim: *"a large melon like gourd that takes a long time to grow but is then worth a lot of food and keeps for a long time."* A single melon-sized gourd per plant, rind pale and waxy as the stone, swelling in the shade of its own little blade-comb, fed by drip. | 🔑 **The sowable crop** — the reason a colony can farm here. One slow gourd is a season's promise: very long growDays, big nutrition payout at harvest, very high rot-days (the rind keeps it). Sown at drip-gardens and the pool ring's soil patches. Balances against real farmland by time, not by yield. | med / sowable only (wild rows rare at pool ring) | plain PlantDef + item def `RM_Dewgourd` fruit; long `growDays`, high nutrition, high `daysToRotStart` | **OWED** |

## 3. Kept rows from the ruled roster JSON (input — not re-adjudicated)

| def | comm. | status here | note |
|---|---|---|---|
| `Plant_Reeds` | 1.0 | **kept** — vanilla, generic architecture, already obeys the blade law (JSON's own reading) | free for the RM_ mod: vanilla def, no dependency |
| `RUT_Dewshrooms` | 0.4 | **kept** — our own port (renamed off BMT_ 2026-09-19); the seep-line mat register | ⚠️ shared with `the_rot.json`'s identical plant — per Q13 (shared content duplicated per biome, then regenerated) the sitting should say whether `RM_WeepingStones` carries its own copy |
| `AB_GreenRockFern` | 0.4 | **RULED 2026-09-24: replaced by `RM_Shadefern` (row 3b)** — decision taken by question card | the kept-in-role slot survives under our own name; the donor def leaves the RM_ roster entirely |
| `Plant_Ambrosia` | 0.12 | **kept** — vanilla-fictional; "a rare sweet find at sacred water" (JSON law) | vanilla def, free; its event coupling (ambrosia sprout) is a vanilla behavior worth a note at build time |

The JSON's nineteen `flora_purged` rows (palms, bulrush, alocasia, Grindterra
copies, smokeleaf) stay purged; nothing here reopens them.

## 4. Donor dependencies to replace

| today | job | replaced by |
|---|---|---|
| `AB_GreenRockFern` (Alpha Biomes) | alien fern on stone-shade | **RULED: `RM_Shadefern`** (row 3b, invented, card decision 2026-09-24) |
| donor `foragedFood` = RawAgave (ZBiome_DesertOasis carry-over) | forageability target | `RM_BladderFruit` via `RM_Bladderquill` (row 4) — sheet §11 says this re-point explicitly |
| donor terrainPatchMakers (kept in spirit per sheet §0) | the water/mud/soil islands | reauthored under `RM_WeepingStones`'s own BiomeDef at mod build — mechanical copy, no design change |

## Open questions (ruled ones moved to the ⚖️ block at top)

1. **Seep-oasis flora — this roster or a seep sub-sheet?** `RM_Steamfrond`
   (row 8) plus seep-salt is one row here; if the seep oases (§2b) deserve
   their own flora register (Wildsteam claims, vent chemistry per
   `the_seas.md`), it should move there and this roster stays dew-country only.
2. `RUT_Dewshrooms` — duplicate into `RM_WeepingStones` as its own copy (Q13
   pattern) or leave it a shared def? Sitting's call, flagged not argued.
3. `RM_Steamfrond`'s seep-salt — confirm seep-salt is *this* row's harvest
   rather than a mineable crust (it could be terrain-scraped instead; cheaper
   as a plant yield). BENCH recommendation at build: plant yield, cheaper.

---

_Every row honours R21 (no rain), the §5 blade/comb rule, and the §6 bans.
Nothing here glows, snows, or ambushes. Art passes are graded against the
silhouette FORM column plus the sheet's palette: bone-white stone, wet black
weep-streaks, green held in blue shade, verdigris where metal meets moss._
