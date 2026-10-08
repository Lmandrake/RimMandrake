# Extra-art spending guidelines — DRAFT (2026-10-08)

> Owner, 2026-10-08 12:03, typed: *"Primarily the first option plus a design agent to find opportunities where
> spending on gender differentiald (eg herd animals that are often seen together) and juveniles (where young variants
> really are important like domesticated beasts) matter. Assess the impact on the game for everything we don't know
> we need and prioritize. Establish some guidelines and help me set them with you. We shouldn't make art for its own
> sake. But I'm not afraid to spend where it matters. Like flyers."*

Inputs: `D:\Luke\dev\RimMandrake\Transient\auxiliary_art_categories_2026-10-08.md`,
`D:\Luke\dev\RimMandrake\Transient\flyer_stable_body_study_2026-10-08.md`.

## 1. Guidelines (draft)

**Unit used throughout: one artpipe job = one facing.** A facing set (east master + derived south and north) is
**3 jobs**; that is how the queue files them (`<id>_east/_south/_north.json`). ⚠️ The auxiliary-categories note
counted "one job per facing set", so its **~450–670** is in *sets*; in queue jobs the same policy is **~1,350–2,000**.
A flyer flip-book on the locked-body recipe is **12 jobs** (3 body master + 9 wing layers, per the flyer study).

The test behind every rule: **spend where the player sees the art often, up close, or next to its own kind — or where
the engine draws nothing or magenta without it.** Not for completeness.

| category | rule | the in-game reason |
|---|---|---|
| **Desiccated** | **Always**, every creature. Share one skeleton across look-alikes (same body plan and size, by eye). | Without it the dry corpse is **invisible** (engine returns no graphic); 308 of our races today. A skeleton lies in the open for days to weeks, often in the home map where hunting or a raid happened, and a vanished body reads as a bug. A skeleton carries no colour or sex, so sharing costs nothing visible. |
| **Pack** | **Always**, every pack animal, and **again for its female body if it gets one.** | Missing pack art draws **magenta** the moment it carries goods, i.e. every caravan. ⚠️ The engine builds the pack path from the **female** body path when one exists, so giving a pack beast female art without a female pack set re-opens the magenta hole. |
| **Flight** | **Always**, every creature that flies, on the locked-body recipe. | Already ruled (owner, 2026-09-19; *"Like flyers"*, 2026-10-08). The wing beat is the only motion art in the game, seen every takeoff, and a gliding static reads as fake. |
| **Swim** | **Always**, every creature that enters water (`waterCellCost`). | Otherwise it walks on water, which reads as a bug at any zoom. |
| **Gender** | **Spend when several of the same creature stand together and are big enough to tell apart**: a herd (`herdAnimal`, wild group of ~6+), a penned or pack herd the player keeps, or **canon dimorphism that shows at sprite scale** (horns, crest, plumage, size). **Not** for solitary creatures, swarms, tiny sprites (body size under ~0.6), or sexless races. | A herd of 6–9 identical sprites reads as copy-paste; a pen of the player's own animals is on screen for the whole game. A male/female pair halves the clone effect and is real information (who breeds). A lone predator or a swarm of dots shows no benefit. Adult stage only; the young keep one set. Female flight frames only when the sexes differ **in flight** (a crest or plumage visible from above). |
| **Juvenile** | **Spend when the player raises them** (pack or farm beasts, easily-tamed herd animals with a young stage of ~15+ days) **or when canon says the young look different** (colour, pattern, no horns). Default otherwise: the adult shrunk by `drawSize` (what 550 of 579 kinds do now). One young set covers both baby and juvenile stages. | A player-bred herd shows calves constantly, for weeks, at the zoom he manages the pen at; a shrunken adult with full horns reads wrong there. A wild baby is rarely seen and briefly. ⚠️ Flight frames are per kind, not per stage, so a young flyer flies with the adult flip-book; give young flyers no flight (stat) or accept it. |
| **Variants** (alternate looks) | **Only** where canon shows colour morphs, or as the alternative anti-clone fix for a herd with no canon sex difference (decision D2). Same price as a female set (one body set; other states fall back to the base), but random per animal rather than tied to sex. | Variants multiply body, swim and desiccated states at once (but not flight or corpse), so populating them for every state is the most expensive axis; a body-only variant is cheap. |
| **Stationary** | Only creatures with a real at-rest form: shell, coil, roost, burrow, closed bell. | Shown every time it stands still or sleeps, so where it exists it is seen constantly; elsewhere the normal sprite is right. |
| **Eggs** | Every egg-layer the player can keep, one item sprite per species (or per look-alike family). | The egg sits in a stockpile next to its parent's name; a generic egg is acceptable but a wrong one is not. Small items, cheap: 1 job each (`Graphic_Single`). |
| **Corpse, rotting, silhouette, sleeping, downed, wounds** | **Never.** | The engine draws them from the live sprite (rotation, rot tint, shared overlays). No visible gain. |
| **Shear/milk/pregnant states** | **Never** (the engine has no field for them; it would be our own C#). | — |

## 2. Impact scoring — method and sanity probe

Instrument: `D:\Luke\dev\RimMandrake\Transient\extra_art_impact_2026-10-08.py` (python, ElementTree) over 2,392 XML
files under `src`, 0 parse failures. **574 non-humanlike races** with animal-style art, one row each. Per-race CSV:
`D:\Luke\dev\RimMandrake\Transient\extra_art_impact_2026-10-08.csv`; ranked shortlists:
`D:\Luke\dev\RimMandrake\Transient\extra_art_shortlists_2026-10-08.csv`.

- **Rosters**: BiomeDef `<wildAnimals>` read as elements (node name = animal, text = commonality), plus patch-added
  rosters resolved from each PatchOperation's own `xpath`. 593 roster creatures. **Sanity probe:** `RSW_Gizka` in 8
  rosters (RM_ and RUT_ twins both counted, so a twin biome doubles presence — the score caps presence to limit that),
  `RSW_Bantha` 4, `RM_Sytheclaw` 3, `RM_Fessk` 1; all found.
- **Fields read** (ParentName resolved inside our XML only; vanilla parents unseen, vanilla defaults assumed):
  `wildGroupSize`, `herdAnimal`, `packAnimal`, `hasGenders`, `Wildness`, `roamMtbDays`, `tradeTags`, `nuzzleMtbHours`,
  `baseBodySize`, `lifeStageAges` (young days = adult `minAge` × 60), milk/shear/egg comps, `MaxFlightTime`, swim art,
  existing female art, existing distinct young art.
- **"Easily tamed / penned"** (162 races) = farm trade tag, or `roamMtbDays` set (a pen animal), or Wildness ≤ 0.3.
- **Canon signals, read by hand.** A regex over the canon entry and description for *the sexes differ* found 8 hits;
  I read all 8 and rejected 2 (Varactyl: both sexes crested; Urusai: canon does not say). Of the 6 real ones, 4
  already have female art (Bantha, Nerf, Porg, Scurrier), leaving **Kybuck and Iridonian reek**. A regex for *the
  young look different* found 18; I rejected 10 (same shape, same colour, or about behaviour); **7 remain** (Mott,
  Clodhopper, Woolamander, Uvak, Colo claw fish, Dianoga, Neebray), plus Hawkbat, which already has young art.
  🔑 **Our invented (`RM_`) creatures have no canon either way**, so for them a sex or young look is a design choice,
  not a finding.
- **Gender score** = seen together (log of max group size, +herd) + roster presence (capped) + kept by the player
  (penned +3, pack +1.5, milk/shear/egg +1) + canon dimorphism (+4) + size, **all multiplied by a visibility factor**
  (body size ÷ 0.6, capped at 1), so swarms and tiny sprites fall out. Excludes the 26 sexless races and the 18 that
  already have female art.
- **Juvenile score** = bred by the player (penned +3, pack +1.5, tameable +1, pet-like +1) + length of the young stage
  (log days) + canon young-differ (+4) + roster presence + herd + size, times a visibility factor (size ÷ 0.4).
  Excludes the 28 kinds that already have distinct young art and separate larva/spawn races (their young IS a
  separate creature with its own art).
- **Job cost** (3 per facing set): gender = female body 3, **+3 female pack set** for a pack beast, +3 female swim if
  it has swim art, +12 female flip-book if it flies (upper bound: only if the sexes differ in flight); desiccated is
  shared across sexes (0). Juvenile = one young set 3, +3 young swim; desiccated reuses the adult skeleton scaled (0).
- ⚠️ The weights are mine and untested against his judgement; the ranking is a **starting order for a review sheet**,
  not a verdict. The CSV carries every input, so a different weighting is one re-sort.

## 3. Gender shortlist (top 30)

| # | creature | score | jobs | why |
|---|---|---:|---:|---|
| 1 | kybuck (`RSW_Kybuck`) | 16.96 | 6 | CANON dimorphism; herds of 3~6; pack beast (female pack set too); 1 rosters |
| 2 | aveluthia (`RM_Aveluthia`) | 16.54 | 6 | herds of 3~9; pack beast (female pack set too); 2 rosters |
| 3 | falumpaset (`RSW_Falumpaset`) | 16.29 | 6 | herds of 3~8; pack beast (female pack set too); 3 rosters |
| 4 | gelagrub (`RSW_Gelagrub`) | 16.04 | 6 | herds of 3~9; pack beast (female pack set too); 2 rosters |
| 5 | eopie (`RSW_Eopie`) | 15.37 | 6 | herds of 2~5; pack beast (female pack set too); 4 rosters |
| 6 | iriaz (`RSW_Iriaz`) | 14.95 | 3 | herds of 6~12; easily tamed/penned; 4 rosters |
| 7 | shaaks (`RSW_Shaak`) | 14.74 | 6 | herds of 4~8; pack beast (female pack set too); 2 rosters |
| 8 | tee muss (`RSW_TeeMuss`) | 14.56 | 6 | herds of 2~6; pack beast (female pack set too); 2 rosters |
| 9 | gennok (`RM_Gennok`) | 14.39 | 6 | herds of 4~8; pack beast (female pack set too); 1 rosters |
| 10 | jakobeast (`RSW_Jakobeast`) | 14.34 | 3 | herds of 3~9; easily tamed/penned; 2 rosters |
| 11 | lava flea (`RSW_LavaFlea`) | 14.31 | 6 | herds of 2~6; pack beast (female pack set too); 1 rosters |
| 12 | Jamel (`RSW_Jamel`) | 14.21 | 6 | herds of 2~6; pack beast (female pack set too); 3 rosters |
| 13 | blurrg (`RSW_Blurrg`) | 13.86 | 6 | herds of 2~6; pack beast (female pack set too); no roster (event/trade only) |
| 14 | chorn (`RM_Chorn`) | 13.85 | 6 | herds of 3~7; pack beast (female pack set too); 1 rosters |
| 15 | feral grazer (`RSW_FeralGrazer`) | 13.84 | 3 | herds of 3~9; easily tamed/penned; 2 rosters |
| 16 | runyip (`RSW_Runyip`) | 13.81 | 9 | herds of 2~6; pack beast (female pack set too); 3 rosters; swim set +3 |
| 17 | dalgo (`RSW_Dalgo`) | 13.72 | 6 | herds of 3~6; pack beast (female pack set too); 2 rosters |
| 18 | sacapillar (`RSW_Sacapillar`) | 13.7 | 18 | herds of 1~3; pack beast (female pack set too); 2 rosters; FLYER: female flip-book +12 |
| 19 | zeer (`RSW_Zeer`) | 13.59 | 3 | herds of 2~4; easily tamed/penned; 3 rosters |
| 20 | jerba (`RSW_Jerba`) | 13.31 | 6 | herds of 2~6; pack beast (female pack set too); no roster (event/trade only) |
| 21 | hrumph (`RSW_Hrumph`) | 13.19 | 3 | herds of 4~8; easily tamed/penned; 2 rosters |
| 22 | jimvu (`RSW_Jimvu`) | 12.94 | 3 | herds of 4~8; easily tamed/penned; 2 rosters |
| 23 | feral nerf (`RSW_FeralNerf`) | 12.93 | 3 | herds of 3~9; easily tamed/penned; 1 rosters |
| 24 | moravatha (`RM_Moravatha`) | 12.7 | 6 | herds of 1~3; pack beast (female pack set too); 2 rosters |
| 25 | olumetha (`RM_Olumetha`) | 12.57 | 3 | groups of 3~9; easily tamed/penned; 2 rosters |
| 26 | sulleth (`RM_Sulleth`) | 12.55 | 3 | herds of 3~7; easily tamed/penned; 1 rosters |
| 27 | excretor (`RSW_Excretor`) | 12.46 | 3 | herds of 2~6; easily tamed/penned; 2 rosters |
| 28 | julmox (`RM_Julmox`) | 12.39 | 3 | herds of 4~9; easily tamed/penned; 1 rosters |
| 29 | skalders (`RSW_Skalder`) | 12.26 | 9 | herds of 3~7; pack beast (female pack set too); 4 rosters; swim set +3 |
| 30 | corinathoth (`RSW_Corinathoth`) | 12.26 | 3 | herds of 3~6; easily tamed/penned; 1 rosters |

Top-30 total: **162 jobs**.

Read: the top is dominated by **pack and penned herd beasts**, where each female set costs 6 (body + pack). Only 2 of the 30 rest on canon; the rest are the anti-clone case the owner named. Flyers that reach the list show the flip-book surcharge.

## 4. Juvenile shortlist (top 30)

| # | creature | score | jobs | why |
|---|---|---:|---:|---|
| 1 | mott (`RSW_Mott`) | 12.62 | 6 | CANON young look different; easily tamed/penned; young for 18 days; swim set +3 |
| 2 | uvak (`RSW_Uvak`) | 12.43 | 3 | CANON young look different; pack beast, bred for work; young for 36 days; flyer (frames stay adult) |
| 3 | woolamander (`RSW_Woolamander`) | 12.0 | 3 | CANON young look different; easily tamed/penned; young for 18 days |
| 4 | falumpaset (`RSW_Falumpaset`) | 11.98 | 3 | pack beast, bred for work; young for 36 days |
| 5 | sacapillar (`RSW_Sacapillar`) | 11.26 | 3 | pack beast, bred for work; young for 60 days; flyer (frames stay adult) |
| 6 | jerba (`RSW_Jerba`) | 11.26 | 3 | pack beast, bred for work; young for 60 days |
| 7 | aveluthia (`RM_Aveluthia`) | 11.16 | 3 | pack beast, bred for work; young for 42 days |
| 8 | tellurox (`RSW_TelluroxRace`) | 11.09 | 3 | pack beast, bred for work; young for 24 days |
| 9 | dalgo (`RSW_Dalgo`) | 10.98 | 3 | pack beast, bred for work; young for 18 days |
| 10 | clodhopper (`RSW_Clodhopper`) | 10.88 | 3 | CANON young look different; easily tamed/penned; young for 6 days |
| 11 | zeer (`RSW_Zeer`) | 10.73 | 3 | easily tamed/penned; young for 36 days |
| 12 | vaalok (`RM_Vaalok`) | 10.63 | 3 | pack beast, bred for work; young for 36 days |
| 13 | gennok (`RM_Gennok`) | 10.53 | 3 | pack beast, bred for work; young for 27 days |
| 14 | chorn (`RM_Chorn`) | 10.52 | 3 | pack beast, bred for work; young for 30 days |
| 15 | moravatha (`RM_Moravatha`) | 10.49 | 3 | pack beast, bred for work; young for 20 days |
| 16 | blurrg (`RSW_Blurrg`) | 10.3 | 3 | pack beast, bred for work; young for 33 days |
| 17 | aurrok (`RM_Aurrok`) | 10.21 | 3 | pack beast, bred for work; young for 20 days |
| 18 | corinathoth (`RSW_Corinathoth`) | 10.17 | 3 | easily tamed/penned; young for 30 days |
| 19 | tee muss (`RSW_TeeMuss`) | 10.04 | 3 | pack beast, bred for work; young for 24 days |
| 20 | kybuck (`RSW_Kybuck`) | 10.02 | 3 | pack beast, bred for work; young for 12 days |
| 21 | gelagrub (`RSW_Gelagrub`) | 9.95 | 3 | pack beast, bred for work; young for 15 days |
| 22 | Jamel (`RSW_Jamel`) | 9.95 | 3 | pack beast, bred for work; young for 18 days |
| 23 | shaaks (`RSW_Shaak`) | 9.92 | 3 | pack beast, bred for work; young for 12 days |
| 24 | thunderstep (`RSW_ShrublandGiant`) | 9.91 | 3 | easily tamed/penned; young for 60 days |
| 25 | ronto (`RSW_Ronto`) | 9.86 | 3 | pack beast, bred for work; young for 60 days |
| 26 | tirbak (`RM_Tirbak`) | 9.86 | 3 | pack beast, bred for work; young for 24 days |
| 27 | dianoga (`RSW_Dianoga`) | 9.63 | 6 | CANON young look different; young for 36 days; swim set +3 |
| 28 | vellak (`RM_Vellak`) | 9.52 | 3 | pack beast, bred for work; young for 21 days |
| 29 | chatrak (`RM_Chatrak`) | 9.49 | 3 | easily tamed/penned; young for 48 days |
| 30 | beldon (`RSW_Beldon`) | 9.41 | 3 | easily tamed/penned; young for 48 days; flyer (frames stay adult) |

Top-30 total: **96 jobs**.

Read: the canon-distinct cases lead (Mott, Uvak, Woolamander, Clodhopper), then the player-bred work beasts. Large wild-only creatures that score on size and long youth alone are the first to cut if the rule is "player-bred only".

## 5. Decisions for the owner

Written to go straight onto question cards. Every count is measured from the CSV above; jobs are queue jobs (3 per
facing set). The "always" categories (desiccated, pack, flight, swim) are already his "first option" and are not
re-asked, except how far desiccated may be shared (D4).

**D1 — Which herds get a male and a female look?** *(herds seen together read as clones)*
- **Big herds only (wild groups of 8 or more):** 16 creatures, **~75 jobs**. Fixes the worst clone herds; most herds
  of 3–6 keep one look.
- **Ordinary herds (groups of 6 or more):** 47 creatures, **~220 jobs** (~195 without the 2 flyers' flip-books).
  Covers most grazers a player meets in numbers.
- **Every herd of 4 or more:** 62 creatures, **~295 jobs**.
- **Only the animals the player keeps** (penned or pack beasts, any herd size, big enough to see): 97 creatures,
  **~420 jobs**. Spends where he looks longest — his own pens — and skips wild herds.
- *Trade:* the canon-only rule (Kybuck, reek) costs **9 jobs** and fixes almost no clone herds; any herd rule adds
  invented sex differences to creatures canon is silent on, which someone must design.

**D2 — For a herd whose canon says nothing about the sexes, how do we break up the clones?**
- **A female look**: tied to sex, so it also tells him who breeds; must be invented; pack beasts need a second pack
  set (6 jobs instead of 3).
- **A second colour/marking variant**: random per animal, any number per herd, no sex claim to invent; same body
  price (3), and it does not touch the pack art. Does not show who breeds.
- *Same cost either way at one extra look per creature; the difference is meaning, not money.*

**D3 — Which young get their own look?** *(otherwise the adult is shrunk)*
- **Only where canon says the young look different:** 7 creatures, **~30 jobs**.
- **Pack beasts only** (the work animals he breeds): 32 creatures, **~100 jobs**.
- **Pack beasts and easily-tamed animals, big enough to see, young for 15+ days:** 56 creatures, **~180 jobs**.
  This is the "domesticated beasts" case he named.
- **Every tameable animal:** 445 creatures, **~1,490 jobs**. Mostly wild babies he rarely sees.
- *Canon-distinct cases ride along with whichever option he picks.*

**D4 — How widely may a dried skeleton be shared?** *(308 races have none, so their dry corpse is invisible today)*
- **One skeleton per body type:** 23 skeletons, **~70 jobs**. ⚠️ Our "snake" body type alone covers 78 very different
  invented creatures, so many skeletons would not match their animal.
- **Per body type and size class:** 61 skeletons, **~185 jobs**. Matches size; can still mismatch shape.
- **Per look-alike family, grouped by eye on a sheet:** ~150 skeletons (estimate), **~450 jobs**. What vanilla does.
- **One per species:** 308, **~925 jobs**. Exact, but a skeleton carries no colour, so most of the gain is invisible.

**D5 — Do female flyers get their own wing-beat frames?** *(a flip-book is 12 jobs)*
- **Only when the sexes look different in the air** (crest or plumage seen from above): adds ~0–2 flip-books today.
- **Every flyer that gets a female look:** +12 jobs each, and decide this **before** the flyer frames are made, or
  they get made twice.

**D6 — Is the score's idea of "seen often" right?** *(sets the order of all of the above)*
- **Pens first** (what he keeps outranks what roams wild) — the current weighting.
- **Wild rosters first** (how often a creature turns up across biomes outranks taming).
- Either way the shortlists become a review sheet he edits; this only sets the starting order.
