# Fever Wood — RM_ invented cast proposal (2026-09-24)

DESIGN PROPOSAL for bench review. Fills the holes left in `RM_FeverWood` when its
Star Wars canon rows route out to the Utinni patch layer (Q11/Q11a). Nothing here
is built; nothing here is filed.

## Framing — what leaves, what already exists, what is genuinely new here

Per `FEVERWOOD_RM_MOD_BUILD_1`, the split sends **10 of 11 fauna rows and 3 of 7 flora
rows** to the Utinni patch layer: `RSW_GlowSlug` (0.5 sap-drinker), `Urusai` (0.5 flier),
`Gelagrub` (0.4 crown-grazer), `Nuna` (0.4 grazer), `Convor` / `Whisperbird` (0.3 fliers),
`LongtailGorg` (0.3 wait-ambush), `RSW_JewelBeetle` (0.2 crown-grazer), `RSW_AcidSlug`
(0.05 ground-slow), `Fambaa` (0.02 the-terribly-lost); plants `Plant_HydenockTree_Wild`
(**1.5 — the dominant tree**), `Plant_JoganTree_Wild` (0.6 fruit), `Plant_Chakroot_Wild`
(0.4 root). `RM_FeverWood` keeps only `VFEI2_Megathrips`, the 3 `AB_*` plants and
`RM_GiantLeaf`.

🔑 **Most of the holes are already filled, and this proposal does not re-invent them.**
`fever_wood_fauna_roster_2026-09-23.md` (11 invented `RM_` creatures) and
`fever_wood_flora_roster_2026-09-23.md` (18 invented `RM_` plants) were authored against the
owner's own 2026-09-23 rulings and cover the sap-drinker guild (F8's thornbug included), the
borer, the crown grazer/ambusher, all four birds, the towers, the crown flora and the margin.
The deep thing is already owner-named: **`RM_Sekkulaath`** (§1a of the deep-and-mud sheet).
**This proposal adopts those rosters as the `RM_FeverWood` cast** and adds the **five
creatures they left uncovered**: the two F9 war species (the roster scoped the raiders out),
a Tenant-prey wanderer (`Fambaa`'s hole), a ground-slow scavenger (`RSW_AcidSlug`'s hole),
and a ground grazer (`Nuna`'s hole). Flora needs **zero new names** — the three canon
departures map onto existing roster rows; my contribution there is the mapping and the
commonalities (the roster's own numbers were "slots, not values").

## Proposed fauna — 10 rows: 5 NEW, 5 adopted (†) from `fever_wood_fauna_roster_2026-09-23.md`

† = already drafted in the 2026-09-23 roster; listed here so every mechanic slot is visibly
covered, not re-proposed. The roster's other six rows (glavoth, ollareth, drommath, sarveth,
thavrik, skellick) are adopted with it. Names follow the Fever Wood register (§6o: -eth/-ith/
-ock/-el endings, doubled ll/mm/rr, wetter and slower than the Greentide).

| proposed name | syll. | size class | niche / role | mechanic hook | diet | commonality | art brief (one line) |
|---|---|---|---|---|---|---|---|
| **kurreth** (NEW, `RM_Kurreth`) | 2 | small (bs ~0.4) | the ant-swarm — the raider from the dry direction; steals nectar-beasts ALIVE; hive castes as plain-modifier variants (*kurreth queen*) | **F9** — off-map raider + `FEVERWOOD_ANT_HIVE_DUNGEON_1` | omnivore, nectar-thief | **0 — never a `wildAnimals` row** (roster ban: off-map only) | glossy red-black segmented worker, oversized carry-mandibles, always drawn mid-haul |
| **skreth** (NEW, `RM_Skreth`) | 1 | large (bs ~2.5) | the brood predator — the raider from the Webwork direction; hunts in a matron-led brood (*skreth matron*) | **F9** — off-map raider, the second front | carnivore | **0 — off-map only** | low eight-limbed silk-grey ambusher, forelimbs raised in a strike cock, egg-clutch sheen on the matron |
| **gorrameth** (NEW, `RM_Gorrameth`) | 3 | very large (bs ~4.0) | the terribly lost — a great placid wanderer that drinks at the mirrors and is subtracted | **Tenant-prey** — the ambient tragedy, and the Sekkulaath's visible food supply | herbivore | 0.02 | huge round-backed grey browser with a low-slung drinking head — built to look like it is about to kneel at the wrong pool |
| **grolth** (NEW, `RM_Grolth`) | 1 | medium (bs ~0.8) | ground-slow carrion-dissolver working the causeway margins; waits, never chases (ban 3) | none — fills `RSW_AcidSlug`'s trace slot | carrion | 0.05 | a wet dark hummock of a body, no visible head, a pale dissolving-slick under its front edge |
| **nemmel** (NEW, `RM_Nemmel`) | 2 | small (bs ~0.3) | ground grazer of the causeway edges — the floor's one honest meal animal | none — fills `Nuna`'s slot | herbivore | 0.4 | plump short-legged mud-brown grazer, oversized splay feet that read as mud-shoes |
| thornbug † (`RM_Thornbug`) | 2 (owner's word) | small (bs ~0.5) | the nectar-beast; yields only while calm (hard ban 6) | **F8** — `RM_CompGatherableCalmGated`, nectar product `RM_ThornbugNectar` | sap (ossagrel host) | 0.6 | great thorn-shaped insect clamped flush to bark — a thorn on the tree |
| mulleth † (`RM_Mulleth`) | 2 | medium (bs ~1.0) | crown grazer slung UNDER the boughs | canopy | herbivore (verrow gourds) | 0.4 | soft-bodied grazer hanging upside-down beneath a bough, mossy back |
| silloch † (`RM_Silloch`) | 2 | small (bs ~0.6) | the crown's patient wait-ambusher (never chases, ban 3) | canopy | carnivore | 0.3 | flat mottled wedge folded motionless against bark — reads as bark |
| chellow † (`RM_Chellow`) | 2 | small (bs ~0.25) | tameable chorus bird; with sarveth/thavrik/skellick † it makes the emergent cacophony (§6k) and its silence is the Sekkulaath alarm | canopy / boughway | omnivore | 0.4 (fliers total ~1.1 across four) | squat bird, bare wrinkled head, veined translucent throat-fan — a lamp with a bellows, never a parrot |
| brathek † (`RM_Brathek`) | 2 | medium (bs ~0.9) | the wood-borer that keeps digging (§6q); living excavation tool | boughway / bore-caves | wood pulp | 0.5 (beside kept `VFEI2_Megathrips`) | pale ringed grub, dark rasping head-plate wider than its body — a drill bit |

**Pyramid check (fact 5):** of the full adopted-plus-new cast, only gorrameth and skreth
exceed bs 2, and both are trace/off-map — small creatures dominate, matching the departing
distribution (biggest leaver `Fambaa` was 0.02) and `ECOSYSTEM_PYRAMID_LAW_1`'s 80.7%.
**Every fact-4 slot is covered:** F8 = thornbug; F9 = kurreth + skreth; Tenant-prey =
gorrameth (staple is the mud, per §6e — prey is the visible bonus); canopy/boughway =
mulleth, silloch, four birds, brathek; dominant tree below.

## Proposed flora — 5 rows, all adopted from `fever_wood_flora_roster_2026-09-23.md`; zero new names

The 18-plant roster already covers every departing role; what was unset is which row takes
which departing slot and at what commonality. No new plant is coined — inventing one here
would re-invent what the roster already built.

| proposed name | role | replaces which departing canon row | commonality | art brief (one line) |
|---|---|---|---|---|
| **thulvane** (`RM_Thulvane`) | **dominant tree** — the 16-cell fused tower, the biome's structural unit and the body of the bore-caves | `Plant_HydenockTree_Wild` (was 1.5, the dominant tree) | **1.5** | colossal grey-green fused column, crown permanently out of frame, bark in wet black-grooved plates |
| **skethral** (`RM_Skethral`) | co-dominant tree — the arch-thrower whose fused limbs ARE the boughway network | (none — new structural depth; hydenock carried both jobs alone) | 0.8 | two of them read as one arch: horizontal limbs knitting at pale scarred joins |
| **ossagrel** (`RM_Ossagrel`) | mid plant — the sap host the whole F8 guild clamps to; the nectar economy's food source | (none departing — but F8 is unfed without it, so it ships in wave 1) | 0.7 | swollen jointed cane weeping clear syrup at every split node — a leaking pipe |
| **verrow** (`RM_Verrow`) | mid plant — the crown's staple fruit on bough-soil | `Plant_JoganTree_Wild` (was 0.6, crown fruit) | 0.6 | heavy dull-skinned gourds hanging on long stalks below sparse high fronds |
| **tullick** (`RM_Tullick`) | ground cover — the floor's tuber, the causeway workers' starch | `Plant_Chakroot_Wild` (was 0.4, root plant) | 0.4 | tight low whorl of ribbed leaves over visibly domed ground |

Per the flora roster's own §6, the three departing canon plants come BACK via the Utinni
patch layer at reduced commonality (hydenock demoted from the structural-tower job it was
never right for) — the campaign game is the free game plus canon, exactly Q11a's shape.
⚠️ The crown rows (ossagrel, verrow) are blocked on bough-soil (§6b, `RUT_Boughway`
fertility 0) — a build-order fact, not a design gap.

## Names checked

The five NEW names were checked against **both naming docs read whole this pass** —
`noncanon_beast_names_propane_arid_forge_pyre_fever_greentide_rust_lantern_blue.md`
(including its Appendix C roll-up of every batch 1/2/3 drafted name, 168 rows) and
`noncanon_beast_names_crags_nightside_contagion_slime.md`'s style rules and drafts — plus
the Fever Wood/Greentide/Sump roster registers, on the four-letter-opening stem rule
(rule 3) and against Star Wars canon from my own knowledge.

| name | in either naming doc? | nearest existing opening | SW canon collision? |
|---|---|---|---|
| kurreth | no | korrum/korrag (`korr` ≠ `kurr`), kuvra (`kuvr`) | none known |
| skreth | no | skerrel (`sker` ≠ `skre`), skezzar (`skez`) | none known — superficially near the canon character *Sskeer*, but not that name |
| gorrameth | no | ghorrumak (`ghor` ≠ `gorr`) | none known — non-SW echo of Firefly's "gorram" noted as a taste flag only |
| grolth | no | gruzz (`gruz`) | none known |
| nemmel | no | nellith (`nell`), pemmel was self-rejected for the English *pommel* echo | none known |

Syllable variety (rule 7, owner-typed 2026-09-24): the five new names run 2×1 / 2×2 / 1×3
syllables (skreth, grolth · kurreth, nemmel · gorrameth). None is a slime, so the slime
monosyllable law does not bind any of them (grolth is carrion-flesh, not gel; if the owner
reads it as goo-bodied, its single long syllable already satisfies the law). **No UNCERTAIN
flags** — but the mechanical bar before ratification is `check_pseudo_sw_name.py` + the
`src/` label sweep + a Wookieepedia `list=search` probe, exactly as the naming docs ran, and
that has NOT been run on these five (proposal-stage only; the search API check is a Desktop/
network step).

## Open questions for the owner

- **Ratify the two 2026-09-23 rosters as the `RM_FeverWood` cast?** They are drafted, never
  ruled; this proposal builds on them, so a strike there is a strike here.
- **Does rule 7 (syllable variety) retro-apply to the roster's 11 fauna names?** Ten of
  eleven are two-syllable — exactly the monotony your ruling names — but they predate it by
  one day. Say the word and a variety pass is drafted; silence keeps them as written.
- **Where do the raider species ship?** kurreth/skreth defs could live in `RM_FeverWood` or
  in `mandrake.rm.environmentalhazards` beside the F9 war wiring — the kit spec left
  packaging as FOUNDRY's call, but the species names should be yours first.
- **skreth vs the Webwork:** in the campaign the second front reads as the Webwork probing
  the wetland. Is the skreth the free-tier face of that same brood (canon feralisk/wyyyschokk
  mapped over it, Sekkulaath-style), or its own species the campaign merely joins?
- **gorrameth herds or singletons?** The terribly lost read strongest as lone animals
  (0.02); if you want the occasional doomed herd for spectacle, that is an incident, not a
  commonality change.
