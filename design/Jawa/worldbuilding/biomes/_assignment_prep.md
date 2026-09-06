# Biome fauna/flora assignment — DECISION PREP for the owner's sitting

_BENCH DESIGN subagent, overnight 2026-09-05→06, for `BIOME_FAUNA_ASSIGNMENT_SITTING_1`.
Every list below is a **menu with a recommendation**, never a decision. Data:
`creature_register_rows.json` (1,165 rows, 595-mod dump 2026-09-05, calibration PASSED;
**live** = not cut, not zeroed, not modDropped = 895 rows MEASURED). Violation thresholds
are the **stated proxies** from `PORTFOLIO_creature_distribution.md` fig6 where they exist;
new ones are stated inline. The sheets (this folder) are the admission tests; where a prior
roster disagrees, the sheet wins pending the owner._

**⚠️ Instrument notes (data honesty):**
- The register's `flies` special is BROKEN — Muffalo carries it (1,161/1,165 rows do).
  Every "flier" claim below is by-name knowledge, labeled UNMEASURED.
- Life stages (juvenile sizes) are not in the register → every "huge-young" exemption is
  UNMEASURED.
- `RUT_LongHunger` and `SandWorm_Thing` have `statsResolved: false` → excluded from every
  stat test (UNMEASURED rows).
- Recognizability and art are the owner's EYE tests — no stat below can pass one. The
  recognizability lane (`creature_recognizability_rule.md` §6: per-mod survival % already
  measured) runs IN ADDITION to every biome test here.

**How to read each section:** §1 the sheet's fauna laws as a checkable list · §2 KEEP
(residents that pass) · §3 EVICT (residents violating a hard ban, law + failing stat
cited) · §4 IMPORT (non-residents fitting the sheet's niches, incl. NEW ART/DEF NEEDED)
· §5 open calls, one line each.

**Def bindings (the map's real inventory, MEASURED off `ASHKARR_WORLDMAP_tiles.csv`):**

| sheet | BiomeDef(s) on map | tiles | live residents (register) |
|---|---|---:|---:|
| dune_sea + deep_desert | `ExtremeDesert` (ONE def, two sheets) | 3,189 | 116 |
| desert | `Desert` | 4,151 | 172 |
| arid_shrubland | `AridShrubland` | 748 | 222 |
| wasteland | `Wasteland` | 1,699 | 52 |
| poison_forest | `PoisonForest` | 542 | 53 |
| nightside_ice | `AB_RockyCrags` + `AB_PropaneLakes` + `BMT_CrystalCaverns` | 3,392 | 76 (union) |
| terminator_sea | — none (the seas are `Ocean`/`Lake` tiles) | 823+322 | 0 |
| fall_line | injection layer over the arid defs | 308 | n/a |

---

## 1. THE DUNE SEA + THE DEEP DESERT — `ExtremeDesert` (116 residents)

🔴 **One def carries two sheets.** Dune sea (θ 0–40) and deep desert (far ring, arc 50–69)
are both painted `ExtremeDesert`, and the register can only bind per def. The lists below
apply the INTERSECTION of both sheets (the strict test); the owner's first call (§5) is
whether the def gets a region-level split or one merged roster.

### 1.1 Admission test (checkable)
- ⛔ No medium fauna: **bodySize 0.3–3.0 banned** (dune sea "giant or grain-scale only";
  fig6 stated proxy).
- ⛔ No pursuit/ambush-from-cover predators — subsurface strike only (dune sea §6).
- ⛔ No large surface herds (deep desert ban 7; herd special is checkable).
- ⛔ Nothing nocturnal/circadian (dune sea ban 1 — UNMEASURED in register; def audit owed).
- ⛔ No mineralized/shiny look (deep desert ban 3 — eye test).
- ⛔ Population target: **sparse to the point of discomfort** — "if the roster looks
  healthy, it is wrong."
- Recognizability doubly strict on giants (both sheets); SW icons protected.

### 1.2 KEEP candidates (pass on stats; residents, top commonality first)
**Grain-scale (10 residents pass the size law)** — recommend keeping ~5–6, cutting the rest
for sparseness:

| creature | bs | spd | comm | one-line reason |
|---|---|---|---|---|
| GraniteSlug (SW) | 0.2 | 1.0 | 0.1 | mineral-eater, slow, alien — the model grain resident |
| AA_Needleroll (Alpha) | 0.15 | 2.5 | 0.75 | strange rolling form, non-pred |
| AA_Eyeling (Alpha) | 0.13 | 3.0 | 0.25 | alien, subsurface-plausible |
| Kreetle (SW) | 0.2 | 3.5 | 0.2 | SW desert beetle |
| Gizka (SW) | 0.18 | 3.0 | 0.01 | SW icon (KOTOR) |
| Scurrier (SW) | 0.2 | 4.5 | 1.0 | SW icon — but comm 1.0 contradicts sparseness; trim to ≤0.1 |

**Giants (18 residents pass size; most FAIL other laws)** — pass the full test:

| creature | bs | spd | comm | reason |
|---|---|---|---|---|
| KraytDragon (SW) | 12 | 5.0 | 0.15 | 🔑 ICON — canonical dune-swimmer; subsurface strike is its native read |
| GreaterKraytDragon (SW) | 15 | 6.0 | 0.001 | icon; comm already correctly near-zero |
| AA_BoulderMit (Alpha) | 4 | 1.0 | 0.025 | slow mineral giant, dormant-looking |
| AA_TetraSlug (Alpha) | 5 | 0.6 | 0.0005 | barely-moving giant, alien |
| WarWyrm (SW) | 15 | 6.0 | 0.2 | wyrm body = subsurface strike read; keep IF ruled a burrower, else evict as pursuit |

### 1.3 EVICT candidates (violate a hard ban)
- **88 of 116 residents (76%, MEASURED) sit in the banned 0.3–3.0 band** — the dune sea as
  assigned is mostly medium. Top by spawn weight (law: no medium fauna; stat: bs):
  Shyrack (0.75, comm 0.8) · LavaFlea (2.4, 0.8) · Sketto (0.4, 0.7) · StoneCrab (0.3,
  0.7) · BMT_Glowtail (0.32, 0.7) · VFEI2_Megathrips (0.35, 0.7) · BMT_BloodropMoth
  (0.77, 0.7) · Locust (0.6, 0.7) · Stintaril (0.5, 0.7) · Wraid (3.0, 0.4) … full list
  is fig6's dune-sea panel.
- **Herd giants (deep desert ban 7, herd special):** Ronto (bs 6, herd) · Skalder ·
  Beldon · Thranta · Tukata — 5 of the 18 giants. (Ronto/bantha herds belong to `Desert`,
  where herds are infrastructure.)
- **Fast pursuit giants:** Lylek (bs 5, spd 5, comm 0.8 — top resident!) · Roggwart ·
  KellDragon · Vapaad · Drexl — pursuit predators in a biome where "nothing charges out
  of a bush; there is no bush."

### 1.4 IMPORT candidates
- **Subsurface strike predator:** Alpha Animals' Sand Prowler pattern (sheet §10 names its
  terrain-hiding XML as already solved) — check AA_Dunealisk (currently shrubland-region
  resident, wild×advanced corner per fig8). SandWorm_Thing exists but is UNMEASURED
  (prefab art, stats unresolved) — owner call.
- **Shade-commensal micro-fauna living under a walking giant:** **NEW DEF NEEDED** —
  nothing in 895 live rows is keyed to another creature's shadow (mechanic does not exist
  in any donor mod; needs our C# anyway, per desert sheet's shade grid).
- **Glass-nub light-pipe flora, mirror-plated sun-axis giants:** **NEW ART/DEF NEEDED** —
  no donor flora is buried-with-optics; no donor giant is asymmetric-mirrored.
- **Dormancy-triggered forms:** donor mechanic EXISTS — 107 live rows carry "lies dormant
  until something wakes it" (mostly VFE-Insectoids 2) — candidates for reskin into
  trigger-on-water/vibration dune fauna rather than new C#.
- Sarlacc: its own item (deep desert sheet, ticketed) — not part of this menu.

### 1.5 Open calls
1. Split `ExtremeDesert` roster by region (dune sea vs deep desert families) via
   pawnkind/mutator injection, or one merged strict roster?
2. Does the icon carve-out override the size ban? (A bantha herd on Tatooine dunes is THE
   icon image — but bs 4 herds violate deep desert ban 7. Recommend: herds stay `Desert`.)
3. WarWyrm: rule it a burrower (keep) or a pursuit giant (evict)?
4. Scurrier/Tooke at comm ~1.0: trim commonality or evict — sparseness is the sheet's
   headline; what ceiling per-creature commonality does the dune sea get?
5. Nocturnal-behaviour audit (ban 1) needs a def-level pass no register field covers —
   authorize as a lint task?

---

## 2. THE DESERT — `Desert` (172 residents)

### 2.1 Admission test (checkable)
- ⛔ **No pursuit predators** (ban 3): proxy = predator special AND moveSpeed ≥ 4.5
  (fig6's stated proxy). Burst-out-of-shadow is wanted; running prey down is banned.
- ⛔ No burrow-ambush on pavement (ban 6 — terrain-level, not a creature stat).
- ⛔ No nocturnal/day-night content (ban 1 — UNMEASURED; def audit owed).
- ⛔ No boom-and-bust populations (ban 4 — def audit).
- ✅ Herds WANTED (a herd is a mobile shade structure) — the one biome where herd defs are
  an asset. Familiar body ARCHITECTURE wanted; nameable terrestrial animals not.
- Body size maps to dash distance — a size-sorted roster is correct, not a defect.

### 2.2 KEEP candidates
**Positional/ambush predators (58 residents pass: predator + spd < 4.5)** — top:

| creature | bs | spd | comm | reason |
|---|---|---|---|---|
| Kreetle (SW) | 0.2 | 3.5 | 0.8 | small patch-rim ambusher |
| BMT_Jellypot (Caverns) | 0.65 | 1.65 | 0.7 | sits-and-waits — the "own a shadow" predator in one def |
| Shyrack (SW) | 0.75 | 1.5 | 0.6 | slow flier (UNMEASURED), cave-mouth ambusher |
| Gorg / LongtailGorg (SW) | 0.3–0.6 | 2.3–2.9 | 0.4–1.0 | SW ambush frogs |
| Sketto (SW) | 0.4 | 3.0 | 0.4 | desert skitterer |

**Navigator herbivores / herd beasts (62 non-pred residents)** — top:

| creature | bs | spd | comm | reason |
|---|---|---|---|---|
| **Bantha** (SW) | 4.0 | 4.5 | 0.5 | 🔑 ICON, herd — THE mobile-shade herd beast; recommend comm up |
| **Ronto** (SW) | 6.0 | 4.7 | 0.4 | icon, herd, leggy giant — carries its own shade |
| Jamel (SW) | 1.9 | 1.5 | 0.4 | slow herd endurer, camel-analog inside carve-out |
| Eopie (SW) | 1.4 | 4.3 | 0.8* | icon pack animal (*shrubland row; also here at lower comm) |
| Toxalope (Biotech) | 1.4 | 3.4 | 0.4 | strange, herd; in-joke lane (boomalope kin) |
| AA_DesertAve (Alpha) | 1.0 | 7.0 | 0.4 | fast NON-predator = the endurance-navigator archetype (speed law only bans predators) |

### 2.3 EVICT candidates (ban 3: pursuit)
**52 of 172 residents (30%, MEASURED) are pursuit-capable predators.** Top by spawn weight
(each cited: predator special + spd ≥ 4.5): **Wraid** (spd 5.0, comm 0.8) · **Scurrier**
(4.5, 0.8) · **Gutkurr** (4.5, 0.8) · **Meganeura** (8.0, 0.7) · BMT_Diggerpede (5.2,
0.4) · Massiff (5.0, 0.4) · Lylek (5.0, 0.4) · Scavrat (4.9, 0.4) · JOE_Cephalope (8.8,
0.4) · DA_Karabal (5.5, 0.2) · GR_Manwolf (6.5, 0.18) · + 41 more (fig6 desert panel is
the full ordered list). Disposition menu per creature: **evict here** (default) ·
**slow to <4.5 and keep as burst predator** (candidates: Wraid, Gutkurr, Massiff — SW
staples worth keeping SOMEWHERE) · **move to shrubland medium band** (Massiff bs 0.85
fits there).

### 2.4 IMPORT candidates
- **The filter-feeding shade-whale megafauna (sheet §4c):** best donor body =
  **GR_Paraceramuffalo** (bs 16, spd 2.5, non-pred — already the game's biggest meat
  yield; the fig5 "meat-piñata" fix folds into its beastnorm pass). Needs reskin + rename
  (VGE hybrid lane: REGENERATE, don't cut). Alternatives: AA_SummitCrab (bs 15, spd 1).
  True filter-feeding-through-sand mechanic = our C# (sheet §10) — the DEF can land first.
- **Glitter-birds (megafauna commensals):** **NEW ART/DEF NEEDED** — no donor.
- **Burst-predator flagship** (bursts, grabs, retreats to cool): **NEW DEF NEEDED** for
  the hediff-driven version; interim stat-passers exist (Horax bs 15 spd 2, Tibidee,
  Zakkeg — all SW, all currently rare here or elsewhere).
- **Flora:** ultracactus, staggerseed/cycle plant, defending shade plants — **NEW
  ART/DEF NEEDED** (owner-authored concepts; no donor equivalent). Current assigned flora
  (`biome_flora_rosters.md`) is Earth cacti — see §10 contradictions.

### 2.5 Open calls
1. The three high-commonality SW pursuit staples (Wraid/Scurrier/Gutkurr): evict, slow,
   or move? They are 3 of the 6 most-seen desert animals today.
2. Does assignment wait for the shade grid MapComponent, or land rosters first and let
   behaviour catch up? (Recommend: rosters first — the size sorting reads even without it.)
3. AA_DesertAve at spd 7.0 as a non-predator: is a fast HERBIVORE legal (sheet bans only
   pursuit predators — recommend yes, it IS the navigator archetype)?
4. Boom-and-bust audit (ban 4): insect hive defs (VFEI2) resident here — evict wholesale?

---

## 3. THE ARID SHRUBLAND — `AridShrubland` (222 residents — the largest roster on the planet)

### 3.1 Admission test (checkable)
- ⛔ **No resident in the LARGE band** (ban 4): proxy = **bodySize 1.5–3.5 banned**
  (fig6's stated band) unless the def is the juvenile stage of a huge species
  (life-stages UNMEASURED — every exemption is an owner call).
- ⛔ No flammable living flora (ban 9), no dense flora except venomvine (ban 6) — flora
  lane.
- ⛔ No still-air content, no natural ignition, no day/night keying (bans 2/3/5 —
  weather/def audit, not creature stats).
- ✅ Wanted ladder: SMALL (runway nations, venom-armed) · MEDIUM (interface killers:
  tunnel-shaped, edge-pouncers, divers) · **VOID** · HUGE (indifferent giants, enrage
  near young, despise fire).

### 3.2 KEEP candidates
- **Small (50 residents, bs < 0.6):** the runway nations largely exist already. Top:
  Gorg/FrilledGorg (comm 1.0), Lothcat (0.8, icon), Sketto (0.8), Kreetle (0.8),
  Scurrier (0.8), BMT_ImperialToad (0.7). Venom-armed smalls to favour: 26 live rows
  planet-wide carry "venomous bite" (register special) — filter this roster toward them.
- **Medium (43 residents, 0.6–1.5):** interface killers present: Massiff (0.85, spd 5 —
  legal HERE, the tunnel-runner shape) · Anooba (0.95, spd 5) · Urusai (0.75) ·
  LongtailGorg (0.6) · Kybuck (1.0, spd 6 — non-pred runner) · Eopie (1.4 — pack icon).
- **Huge (34 residents, bs > 3.5) — the giants' floor.** Pass the indifferent-grazer
  read: **Ronto** (6.0, herd, comm 0.8) · **Bantha** (4.0, herd, 0.5) · Corinathoth
  (4.0, herd, slow) · Skalder (4.0, herd) · JRWBrachytrachelopan/Ischigualastia (herd
  sauropod-analogs — dino lane: deeper-cut rule likely cuts them; REGENERATE candidates).

### 3.3 EVICT candidates (ban 4: the large-band void)
**95 of 222 residents (43%, MEASURED) sit in the banned 1.5–3.5 band** — 59 of the 95 are
Star Wars Animal Collection (the mod parks its whole midrange here; fig6). Top by spawn
weight, each `bs` cited: Jamel (1.9, comm 0.8) · Dactillion (3.0, 0.8) · IridonianReek
(3.0, 0.8) · Uvak (3.0, 0.8) · Zeer (3.0, 0.8) · Gutkurr (2.0, 0.8) · Insectomorph (2.0,
0.8) · MastiffPhalone (2.0, 0.8) · Varactyl (3.0, 0.8) · Manka (3.0, 0.8) · Mawvorr (2.5,
0.6) · Jimvu (2.0, 0.6) · Kwi (3.0, 0.6) … Disposition menu: **move to `Desert`** (herds
and midsize belong there — Jamel, Uvak, Zeer are natural desert herd stock) · **evict to
no-home** (feeds §11's homeless pool) · **owner exemption as huge-young** (requires
authoring a life-stage, none measured).
- **Huge pursuit predators failing the indifference read** (giants here ignore people;
  these hunt them): Mudhorn (4.0, pred, comm 0.8 — but ICON, Mandalorian) · Behemoth ·
  KraytDragon (belongs to the dune sea) · Rancor (icon — belongs in a lair/dungeon
  context, not open shrubland) · Narglatch · Tukata · Vapaad.

### 3.4 IMPORT candidates
- **Tunnel-shaped medium predators ("long, thin, terrible things shaped like the
  corridors"):** best donors: Terrorworm (Horrors, bs 0.6) · GR_Boomsnake (1.5 — band
  edge) · Titanoboa/"ssorrakoth" (Megafauna, bs 12 — CUT and mod slated retire; only as
  reskin source). Honest answer: **NEW ART/DEF NEEDED** for the signature snake-analog.
- **Fliers/divers (bird-analogs + scrap-nesters):** UNMEASURED (broken flag). By-name:
  Shyrack, Mynock (icons, present). The scrap-nest bird-analog with treasure nests =
  **NEW DEF NEEDED** (nest-theft/scrap-hoard mechanic exists nowhere in the donor pool).
- **Huge grazers with large young:** donors for the body: Fambaa (SW, bs 6) · Mastmot
  (SW, 6) · AA_AnimaColossus / AA_OvergrownColossus (Alpha, 6, spd 2 — strange, slow).
  The **parental-enrage-on-approach young** = life-stage + C# — **NEW DEF work** on
  whichever body is chosen.
- **Tree-guardian uniques, venomvine fauna:** owner's own candidates (sheet Owed) —
  **NEW ART/DEF NEEDED**.
- **Flora:** the fuzz, venomvine, sweetline trees — **NEW ART/DEF NEEDED**
  (`TREE_GRAPHICS_OWNERSHIP_1` already filed for the trees).

### 3.5 Open calls
1. The 59 SW midrange creatures: bulk-move to `Desert`, or per-creature triage at the
   sitting? (Recommend bulk-move the herd/pack herbivores, triage the predators.)
2. Mudhorn (icon, pred, bs 4.0, comm 0.8): icon carve-out vs the giants-are-indifferent
   law — keep as the one huge predator exception?
3. Which huge grazer body becomes THE giant (Fambaa / Mastmot / Alpha colossus / new)?
4. Do venom-armed smalls get a commonality boost as the biome's signature (recommend yes)?

---

## 4. THE WASTELAND — `Wasteland` (52 residents)

### 4.1 Admission test (checkable)
- ⛔ **No anomaly entities** (ban 1): kindOf == entity. **MEASURED: 0 residents — already
  satisfied.** (Keep it true: the linter keeps this at zero.)
- ⛔ No bioweapon-class lifeforms (ban 2 — def-lore audit).
- ⛔ **Wildlife never the headline threat** (ban 3): proxy = evict large capable
  predators (predator + bs ≥ 1.5).
- ⛔ **No unmarked wildlife** (ban 4): everything must read wretched/mutated or
  extremophile-odd — eye test, but "clean farm/fantasy animal" fails on sight.
- Wanted: wretched-mutated smalls (the many) + four extremophile archetypes (the few).

### 4.2 KEEP candidates (24 smalls; the wretched register)
Top by spawn weight — these already read as vermin-of-ruin: VFEI2_Swarmling (comm 1.0) ·
GraniteSlug (1.0) · VFEI2_BlackSwarmling (1.0) · SW_Electrictick (1.0 — electric = on
theme) · BMT_FleeceSpider (0.7) · **BMT_BloodletterPetrel** (0.7, Polluted Lands — the
mod's whole register is contamination-shaped) · GR_Beetlefleet (0.7) · GR_ParagonRat
(0.7) · Borcatu (0.7) · AA_Eyeling (0.6) · BMT_Maligoat (0.4 — "maligoat" is the
wretched-herd read exactly). VGE hybrids here (Molebear, Spidercat, Wolfscarab) read as
mutants — protected mechanics lane, REGENERATE art where too cute.

### 4.3 EVICT candidates
- **16 big predators (ban 3, bs ≥ 1.5 + predator, MEASURED):** GR_Bearalope (1.5, comm
  0.4) · Aiwha (3.0, 0.35 — a flying whale in a fallout pan is also a placement absurdity)
  · GR_Bearscarab (3.0) · GR_Bearhorse (3.5) · GR_Bearcat · GR_Thrumbocat ·
  GR_Spiderhorse · AA_Atispec (7.0) · AA_RoughPlatedMonitor · AA_Barbslinger ·
  AA_Cinderlisk · AA_GreatDevourer + 4 more.
- **Unmarked/clean fauna (ban 4, on sight):** DA_DwarvenMuffton (comm 0.4 — a fantasy
  farm animal) · DA_RedhornedLarpah · AA_EmpressButterfly (a pretty butterfly is the
  opposite of pathos).
- Fast clean runners contradicting the pathos read: GR_Wolfscarab (spd 9.0) ·
  DA_RedhornedLarpah (6.5) · SW_Electrictick (spd 6.0 — keep for theme but slow it?).

### 4.4 IMPORT candidates — the four archetypes
| archetype | closest existing | verdict |
|---|---|---|
| **Radiotroph** (feeds on the hot ground) | AA_FissionMouse (name+theme fit; ubiquity-25 row) | reskin/rename candidate; mechanics = **NEW C#** |
| **Excretor** (kept herd = slow refinery, sheds bezoars) | 59 live rows carry "produces a harvestable resource on a timer" — the mechanic EXISTS (e.g. Alpha/VGE producers) | body: reskin a producer; bezoar product = **NEW DEF** |
| **Radiothermal solitary** (living furnace, spacing law) | none — no donor emits heat | **NEW ART/DEF NEEDED** |
| **Brine-battery** (pool owner, discharges ion gradients) | SW_Electrictick (electric, wrong scale); AA goo family (right look) | **NEW ART/DEF NEEDED** (EMP/zap comps exist in donor C# to borrow) |
- Wretched imports from elsewhere: Toxalope (Biotech, currently `Desert` — belongs here),
  BMT Polluted Lands' full register (pustule hornets, Screecher — already
  contamination-authored).
- **Flora: radiotroph/sequestration vegetation** (the dosimeter-lawn, vault-root trees):
  **NEW ART/DEF NEEDED** — Biotech's pollution flora (toxipotatoes etc.) is the donor
  spine the sheet's Owed already names.

### 4.5 Open calls
1. Wretchedness is an art pass, not a cut: authorize a REGENERATE list (mutate the art of
   keepers) alongside the evictions?
2. Do the four archetypes ship v1 (each is real C#) or does the biome open with wretched
   smalls only? (Recommend: excretor first — mechanic mostly exists; radiothermal is the
   most design-load-bearing.)
3. SW_Electrictick: slow to walking pace and promote to brine-battery-adjacent signature?

---

## 5. THE POISON FOREST — `PoisonForest` (53 residents)

### 5.1 Admission test (checkable)
- ⛔ **Nothing fast** (ban 9): proxy = moveSpeed ≥ 4.5 evicts (sprinter/pursuit ban).
- ⛔ No open-grazing herbivore body plans (ban 8 — there is no grass; diet + silhouette).
- ⛔ Everything sealed (plated/shelled/waxed) or itself toxic — eye/def test; venom and
  toxic-meat defs pass by construction.
- ⛔ No green, no conventional trees, nothing volcanic (art lane).
- ✅ Wanted: eye-heavy or eyeless vibration-sensers, slow plated crawlers, toxic-meat game
  (prized — the cuisine chain input).

### 5.2 KEEP candidates (32 residents pass the speed law)
Top: **Neebray** (SW, spd 3.0, comm 1.0) · **GR_Beetlefleet** (spd 2.5, 0.7 — shelled) ·
AM dryads (Corruptor/Ocular/Tumorous, 0.7 — Alpha Memes, alien and slow; dryad lane
needs its Gauranlen context checked) · AA_InfectedAerofleet (0.5 — "infected" = the
biome's own adjective) · BMT_Screecher (0.4) · Visceral (Horrors, 0.4) · AA_OcularJelly
(eye-heavy in the name) · AA_PebbleMit (0.35, plated) · AA_BedBug (0.35) ·
AA_GiantCrownedSilkie (0.2). ⚠️ Little Critters' Lemming/PoisonMouse (comm 1.0, spd 4.0)
pass on stats and FAIL recognizability on sight — the top spawns in the biome are a
lemming and a mouse; recommend evict-by-recognizability.

### 5.3 EVICT candidates (ban 9: fast)
**21 of 53 residents (40%, MEASURED), moveSpeed cited:** PoisonButterfly (4.84, comm
1.0) · GR_ParagonRat (4.5, 0.7) · BMT_CaveLemming (6.0, 0.4) · BMT_FenridStoat (5.0,
0.4) · BMT_DarkAxolotl (4.6, 0.4) · AA_BlackSpider (5.0) · GR_Ratffalo (6.0) ·
MA_Raptorkhan (6.0) · DA_ImperialRedhound (5.5) · DA_LeviathanCrab (4.6) · Narglatch
(5.0) · VFEI2_BlackEmpress (5.6) + 9 more. Several also fail recognizability
(stoat, axolotl, redhound).

### 5.4 IMPORT candidates
- **Slow plated/mineral crawlers:** GraniteSlug (SW — mineral-eater; dual-home with the
  dune sea is thematically fine, or pick one) · AA_CrystalMit family (crystal = the
  trunks' crystal fans) · Mynock (icon, spd 2.0 — chemosynthetic parasite read).
- **Toxic-meat prestige game:** any keeper can carry it — toxic-meat is a def property
  we author (meat hediff), not a creature hunt; flag the 3–4 keepers that get it.
- **Eyeless vibration-sensing ambusher (the signature):** **NEW ART/DEF NEEDED** — no
  donor is vibration-themed; nearest body: Biomes! Caverns blind fauna (its 10%
  recognizability survivors).
- **Flora:** Alpha Biomes' chemical/fungal flora is the sheet's own named donor pool —
  the flora roster already assigns Polluted Lands trees here (TreeTwistingThornwood,
  TreeMartyr — owner favourites, keep); audit each against "no green, no leaf-crown".

### 5.5 Open calls
1. Little Critters at comm 1.0: evict both on recognizability despite passing every stat?
2. Do dryads stay (they are Gauranlen-mechanic creatures — do they function wild)?
3. Which keepers get the toxic-prized-meat treatment (cuisine chain input)?

---

## 6. THE TERMINATOR SEA — no BiomeDef (0 residents; the seas are `Ocean`/`Lake` tiles)

### 6.1 Admission test (checkable)
- ⛔ Roster CAP: "a handful of large organisms" — a rich list is itself a violation
  (ban: no high species count). Target ≈ 1 mat organism + 1–2 giants PER SEA + 1–2
  shore/shadow-lane forms.
- ⛔ No herds/flocks/schools/swarms (single-spawn, low-density by def — checkable).
- ⛔ No freshwater life, no seasonal behaviour, no sun-trackers, no trees.
- ✅ Every large organism endemic to its own sea — one def per sea, no sharing.

### 6.2 KEEP candidates
None — nothing spawns in Ocean/Lake in the register for these waters (MEASURED 0; water
biomes use a coastal-animal channel the register does not carry — UNMEASURED beyond that).
This roster is built, not curated.

### 6.3 EVICT candidates
None (empty roster).

### 6.4 IMPORT candidates — the endemic giants
**Our own homeless mod is the donor pool: `RimMandrake - SW Sea Beasts` — 12 live
creatures, 0 map homes (MEASURED).** Menu, one per sea (single-spawn, near-zero
commonality, renamed to be endemic):

| sea | candidate body | bs | why |
|---|---|---|---|
| Twilight Sea (*moldy*) | RSW_Lanternwhale | 40 | slow (1.8), luminous name fits the last-of-lineage read |
| Grey Sea (*shrinking*) | RSW_Reefback | 32 | carries-its-own-ecology read suits a dying sea |
| The Scald (if it gets one) | RSW_ElderSando / SandoAquaMonster | 20/14 | icon lineage (Naboo) — carve-out protected |

Remaining 9 sea beasts stay homeless (the seas cannot hold 12 kinds without breaking the
sheet) — dispose under §11. ⚠️ All 12 are on the linear-yield list (fig4) — their yield
ruling rides whatever the owner decides there.
- **The mat organism (one per sea), blade flora, shadow-lane detritivores, condensate
  drinkers:** **NEW ART/DEF NEEDED** — no donor in 895 rows is a planetary mat or a
  50 m salt-rimed blade.
- Shore scavengers: HermitCrab/StoneCrab (Odyssey) fit the shore niche but fail
  recognizability (a crab is a crab) — REGENERATE or NEW.

### 6.5 Open calls
1. Mechanically, do the seas get fauna via a coastal-water BiomeDef patch, map-condition
   spawner, or scripted encounters? (No def exists to hang commonality on — this gates
   everything above.)
2. One giant per sea or two (adult + the "last juvenile" as a story beat)?
3. Does The Scald (dayside, jungle-coast `Lake`) count as a terminator sea at all? (Sheet
   says no — its coast is the green line. Recommend: Scald fauna belongs to the river
   jungle conversation, not this sheet.)

---

## 7. THE NIGHTSIDE ICE — `AB_RockyCrags` + `AB_PropaneLakes` + `BMT_CrystalCaverns` (76 residents union)

### 7.1 Admission test (checkable)
- ⛔ No normal move speed (ban: warm/fast/pursuing/fleeing/flocking): proxy stated here =
  **moveSpeed ≥ 2.0 evicts**.
- ⛔ No bioluminescence (Glowforest owns glow — and Glowforest is on canon's deep night
  but NOT painted on the current tiles CSV; separate map question, not this sheet's).
- ⛔ No eyes, no ordinary animal silhouette, no dispersal, nothing warm-blooded — eye/def
  tests; "if a player can tell it is a creature before it acts, it is wrong."
- ✅ Wanted: sessile catalytic sheets at landform scale, the one-move animal,
  thermal-sensing strikers, clonal crusts.

### 7.2 KEEP candidates (10 of 76 pass the speed proxy, MEASURED)
The goo/mit/slug shelf — the only donor family that reads as "indistinguishable from
terrain": **AA_TetraSlug** (bs 5, spd 0.6) · **AA_BoulderMit** (bs 4, spd 1.0) ·
**AA_SummitCrab** (bs 15, spd 1.0 — landform-scale) · AA_GreenGoo / AA_RedGoo (spd 1.5)
· AA_CrystalMit (in CrystalCaverns — on-theme) · AA_Slurrypede · AA_Terramorph ·
AA_PebbleMit · GraniteSlug. Recommend: keep ≤6 of these at trace commonality; even they
need the no-eyes/no-glow art check.

### 7.3 EVICT candidates
**66 of 76 residents (87%, MEASURED — the hardest cut on the planet, as the sheet
predicts).** Everything with legs and a face: BMT_Megakrill/Megaroach (spd 5–6, comm
1.0) · GR_Spidersnake (4.8, 1.0) · TYR_Lemming (1.0) · Neebray · BMT_FreezerFrog (6.0) ·
BMT pustule hornets/famine locusts (flock + fast) · AA_DuskRat · AA_Murkling ·
AA_NightMule (a pack MULE at −60 °C) · GR muffalo-hybrids… Wholesale eviction is the
recommendation; the sheet routes anything that "reads as an animal" to the terminator.

### 7.4 IMPORT candidates
- **The one-move animal** · **thermal-sensing seam striker** · **hectare-scale sessile
  catalysts** · **chemical frosts ambiguously alive**: all four = **NEW ART/DEF
  NEEDED** — nothing in the donor pool senses heat, moves once, or is landform-sized
  flat. (The 107 "lies dormant until something wakes it" rows are the nearest MECHANIC
  for the one-move animal's trigger — borrow the comp, not the bodies.)
- Nightside-lush (the deep pans) is a reserved future biome — import nothing for it now.

### 7.5 Open calls
1. Accept ~87% eviction and open the nightside nearly empty (recommend yes — emptiness
   is the sheet), or keep the goo-shelf as interim texture?
2. The one-move animal is the biome's whole gameplay — commission it as its own item?
3. `HorrorWastes` (bioweapon legacy) and `AB_MycoticJungle` sit in the same θ band,
   undefined — does today's eviction dump anything INTO them by default? (Recommend: no
   default moves into undefined biomes; homeless pool instead.)

---

## 8. THE FALL LINE — injection layer, no BiomeDef (308 tiles over `ExtremeDesert`/`Desert`/`AridShrubland`)

### 8.1 Admission test (checkable)
- ⛔ No new BiomeDef (ban 1) — everything below is injected content.
- ⛔ Ferals carry NO faction (`Faction=null`), and killing feral droids must not touch
  droid relations (bans 3/4 — def-checkable).
- ⛔ No long-lived/territorial fauna (ban 6); wily, flee-prone behaviour.
- ⛔ Any plant gated on wreck-shade (ban 2); no water (ban 5); no lush (ban 8).

### 8.2 KEEP candidates
n/a — an injection layer has no register residents. The underlying biome rosters (§1–§3)
show through; the injection ADDS the ferals and vermin.

### 8.3 EVICT candidates
n/a (nothing injected yet).

### 8.4 IMPORT candidates
- **Ship vermin (eat what falls):** **Scavrat** (SW — the name is the job; currently a
  desert pursuit-evictee, re-homed here where scurrying between wrecks is correct) ·
  **WompRat** (icon) · **Mynock** (icon — hull parasite, its literal canon niche) ·
  VFEI2_Fuelmite ("fuelmite" — eats fuel; currently homeless after shrubland band cut).
- **Feral droids:** Outer Rim Droid Depot's 8 animal-classed droids (meatless — correctly
  butcher-less, MEASURED via fig4's droid note; icon-protected). Behaviour (flee-prone,
  memwipe-capture, no droid-relations hit) = **our C#** (sheet §8b names this the likely
  own-code piece).
- **Feral races (crash survivors → damaged slaves):** **NEW DEF + C# NEEDED** — no donor
  mod ships capturable feral sentients with permanent mental scars; pawnkind + hediff +
  capture wiring is ours.
- **Wreck-shade flora pockets:** gate existing hardy smalls (fuzz/ultracactus cousins)
  on wreck mutators — flora authoring, not new species.

### 8.5 Open calls
1. Which sentient RACES go feral here (the menu of installed alien races is a separate
   census — authorize it)?
2. Is the feral-droid C# scoped into `PLOT_MECHANISM_MODS_WAVE_1` or its own item?

---

## 9. GLOBAL — the ubiquity-25 disposition menu

fig7's 25 homogenizers (≥20 spawn biomes AND top commonality ≥0.3 — re-verified against
the register, 25 exactly). Whatever per-biome curation does, these are the connective
tissue everywhere until ruled on ONCE, globally. Menu — recommended disposition per row:

| creature | spread | top | recommend | why |
|---|---:|---:|---|---|
| AA_PebbleMit | 45 | 0.35 | TRIM to rock/cavern biomes | plated pebble — fine texture, wrong everywhere |
| AA_FissionMouse | 40 | 0.35 | RESKIN → Wasteland radiotroph | the name is already the archetype |
| AA_Swarmling | 40 | 0.35 | TRIM to 2–3 biomes | generic swarm noise |
| AA_Aerofleet | 35 | 0.5 | TRIM (terminator-adjacent only?) | floating jelly — atmospheric, keep scarce |
| AA_CrystalMit | 33 | 0.35 | TRIM to CrystalCaverns/PoisonForest | crystal belongs to two sheets only |
| AA_MegaLouse | 29 | 0.35 | TRIM | vermin texture, cap it |
| AA_AnimusVox | 28 | 0.35 | TRIM to one strange home | too distinctive to be everywhere |
| AA_LuciferBug | 27 | 0.5 | TRIM; ban from nightside (glow) | glow ban conflicts |
| AA_Bumbledrone | 27 | 0.35 | TRIM | |
| AA_AcanthamoebaGigantea (small) | 27 | 0.5 | TRIM to wasteland/pans | amoeba reads contamination |
| AA_PedigreedRaptor | 26 | 0.35 | EVICT planet-wide | reads dinosaur — deeper-cut rule |
| Boomalope | 25 | 0.7 | KEEP, reskinned (in-joke lane) | owner's deliberate exception |
| Rat | 23 | 3.0 | TRIM to Fall Line/settlements | comm 3.0 is the loudest single number in the table |
| GraniteSlug | 23 | 1.0 | TRIM to dune sea + poison forest | good creature, everywhere is too many |
| WildBoar | 23 | 1.0 | EVICT planet-wide | instantly nameable Earth animal |
| Warg | 22 | 0.4 | EVICT or reskin | fantasy wolf |
| AA_Murkling | 22 | 0.5 | TRIM | |
| Mynock | 22 | 0.7 | TRIM to Fall Line + poison forest | icon — but a parasite needs hosts/hulls |
| Hare | 22 | 2.0 | EVICT planet-wide | nameable; comm 2.0 |
| AA_AuroraSylph | 21 | 0.35 | TRIM (wasteland halo-storm fauna?) | aurora name fits one sheet |
| AA_Drainer | 21 | 0.35 | TRIM | |
| Raccoon | 20 | 0.5 | EVICT planet-wide | nameable |
| Muffalo | 20 | 1.0 | KEEP, reskinned (in-joke lane) | owner's exception; doctrine's calibration animal |
| Neebray | 20 | 1.0 | TRIM to poison forest + caves | icon, but capped |
| Scavrat | 20 | 0.8 | TRIM to Fall Line | see §8.4 |

One ruling pattern would clear the table in a sitting: **EVICT the nameable Earth five
(Rat/Hare/WildBoar/Raccoon/Warg), KEEP the two in-jokes reskinned, TRIM everything else
to ≤2 named home biomes.**

---

## 10. GLOBAL — contradictions with prior rosters (sheet wins pending owner)

1. 🔴 **`biome_and_fauna_roster.md` (2026-08-13, aspirational) vs the sheets — the big
   one.** It rules "Star Wars Animal Collection: ✅ KEEP ALL — this is the theme," parks
   SW herds in `AridShrubland` ("the liveable fringe — herds") and "SW large reptilian
   grazers + their predators" in `Desert`. The 2026-09-05 sheets invert all three: the
   shrubland size ladder evicts 59 SW midrange creatures, the desert bans its pursuit
   predators (Wraid/Gutkurr/Massiff at comm 0.8), and its "⛔ do NOT cut on predator
   grounds" note is superseded by the desert sheet's no-pursuit law (an ecology law, not
   a difficulty cut). Its §2 worldgen-weight machinery is dead anyway (no worldgen,
   owner 2026-08-15). **Recommend: mark the doc superseded-by-sheets at the top.**
2. **It also rules PoisonForest, AB_MycoticJungle, AB_PropaneLakes, HorrorWastes,
   Glowforest OUT (weight 0)** — the frozen map paints 1,939 MycoticJungle tiles, 1,589
   PropaneLakes, 542 PoisonForest. The one-map superseded the in/out table; nobody wrote
   that into the doc.
3. **`biome_flora_rosters.md` (generated, 2026-08-23) vs the desert/dune sheets:**
   `Desert` is assigned saguaro/agave/aloe/pincushion — instantly-nameable Earth cacti —
   and `ExtremeDesert` a 21-plant list where the sheet demands buried glass-nub flora
   and "no above-ground foliage." Flora predates the sheets wholesale; the generator
   (`biome_flora.py` FAMILIES) needs a sheet-law pass. ⚠️ Its own header says climate was
   deliberately not a filter — that job (`NORMALIZE_TEMPERATURE_TOLERANCES_1`) now folds
   into per-sheet flora law.
4. **`creature_recognizability_rule.md` survival table** already condemns Megafauna,
   Mythic Ages, Beasts of the Rim (0% survival, retirement rulings recorded) — so any
   import list above naming their bodies (Sivatherium, Titanoboa) is a RESKIN-SOURCE
   claim, never a keep.
5. Minor: `Alien_Bestiary.md` and `creature_names_ashkarr.md` predate the sheets;
   spot-checks found no direct law conflicts (they are naming/flavor layers) — UNMEASURED
   beyond that, flagged for the naming pass.

---

## 11. GLOBAL — "the planet has no temperate forest" (all MEASURED)

- The register's most-populated biome is **TemperateForest: 282 live residents** — a
  biome painted on **zero** Ash'karr tiles. The mods' default worldview and the frozen
  map disagree wholesale.
- **157 of 767 live wild creatures (animals+insectoids, 20%) already have NO residency
  in ANY biome painted on Ash'karr** — homeless before any sheet is enforced (221 total
  live rows have an empty biome list; the rest of the homeless are mech/vehicle/entity
  kinds that spawn by event, not biome).
- Applying just the STAT-CHECKABLE evictions above (desert pursuit, shrubland large
  band, dune-sea medium band, poison-forest speed, nightside speed) makes **48 more
  wild creatures newly homeless** (MEASURED under the stated proxies) — among them
  whole VFE-Insectoids midsize hives and SW staples (Orray, Akk, Gundark, Falumpaset,
  PaintedSpat).
- ⇒ **~205 of 767 live wild creatures (27%) will have no legal home once the sheets
  bind.** That pool is not a defect list — it is the sitting's raw material: each row
  ends as an IMPORT (re-homed under a sheet's test), a Cherry Picker cut, or a
  reserve-for-events creature. Recommend the owner rule the DEFAULT for the pool
  (cut vs reserve), then triage exceptions.

## 12. The NEW ART/DEF NEEDED ledger (feeds the graphics pipeline)

| biome | needed | mechanic load |
|---|---|---|
| dune sea | shade-commensal micro-fauna · mirror sun-axis giants · glass-nub flora | C# shade later; defs now |
| deep desert | silverbole · egg-trap clutch · cavern beast · drum-lure predator | sheet-ticketed |
| desert | ultracactus · staggerseed · glitter-birds · shade-whale reskin (Paraceramuffalo) | shade grid C# |
| shrubland | fuzz · venomvine · sweetline trees · tunnel snake-analog · scrap-nest birds · THE giant + young | enrage C#, nest C# |
| wasteland | radiotroph flora · excretor bezoars · radiothermal solitary · brine-battery | dose layer C# |
| poison forest | eyeless vibration ambusher · crust phototroph flora | none blocking |
| terminator | per-sea mat organism · blade flora · shadow-lane detritivores | water-spawn route (§6.5) |
| nightside | one-move animal · thermal seam striker · landform catalysts | thermal-sense C# |
| fall line | feral races (pawnkind+hediff+capture) · feral droid behaviour | C#, ours |

_Lesson filed to LESSONS_INBOX: the register's `flies` special is set on ~every row —
a fauna instrument that lies with a flag; validate specials against a known animal
before filtering on one._
