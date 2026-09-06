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
