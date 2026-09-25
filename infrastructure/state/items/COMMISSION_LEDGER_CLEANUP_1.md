# COMMISSION_LEDGER_CLEANUP_1 — 85 genuinely-owed new-art/def commissions from the 118-row ledger

## what

`SHEET_ORPHAN_CONSUMPTION_1`'s "NEW-ART/DEF commission ledger" channel: 118
`ledger:<sheet>:<slug>` rows, all `decision: "in"`, sitting unconsumed in
`design/Jawa/worldbuilding/review/flora_assignment_register.decisions.json` since
the owner graded them 2026-09-10 (`ASSIGNMENT_SHEETS_VERDICT_SITTING_1`). A
2026-09-20 measurement pass (offline, FOUNDRY) found the register itself is dirty:
12 of the 118 slugs are already-built defs (some predating the sheet's own grading
date), 20 are already named and deferred by other live mechanics items/kit specs
(filing them again would double-book), and 1 flatly contradicts a separate,
already-run decision channel (`creature_art_register.decisions.json`). Full
per-row accounting: `Transient/sheet_orphan_118_ledger_2026-09-20.md`.

**This item is the clean remainder: 85 slugs, one per row, verified to have no
live def, no art, no owning item, and no conflicting decision as of 2026-09-20.**
It exists so a future build pass has a trustworthy starting list instead of
re-auditing the noisy original 118 from scratch.

## why

The owner's own condition for the 148-row flora `art:improve` channel (*"please
make sure nobody has already done so before you"*) applies with even more force
here — these are proposals for entirely new creatures/plants/mechanics, so
duplicating one wastes a full commission (design read, art job, def authoring),
not just a re-render. The 2026-09-12 audit already caught 7-9 stale rows via a
partial keyword sweep; this pass's full 118-row sweep plus targeted verification
caught 12 (including one, `RUT_PaleTree`, whose art landed the SAME DAY as this
audit) — the true count of stale rows only goes down with more scrutiny, never up,
which is exactly why nobody should build against the raw register again.

## the 85 owed slugs, by sheet

**arid_shrubland** (6): `scrap-nest-bird-analogs-glittering-treasure-nests-steal-from`, `the-fuzz-knee-high-silver-green-canopy-plant`, `the-huge-grazer-large-young-parental-enrage-body-donors-famb`, `tree-guardian-uniques-owner-candidate-not-yet-ruled`, `tunnel-snake-analog-the-signature-corridor-predator`, `venomvine-fortress-flora-passability-by-body-size`

**desert** (7): `burst-predator-flagship-bursts-grabs-retreats-to-cool`, `defending-shade-plants-thorn-venom-patch-flora`, `filter-feeding-shade-whale-megafauna-body-donor-gr-paraceram`, `glitter-birds-megafauna-shadow-commensals`, `shade-grid-mapcomponent-shadeat-the-keystone`, `staggerseed-cycle-plant-prepared-seed-euphoric-dish`, `ultracactus-owner-s-own-name-stands`

**dune_sea + deep_desert** (8): `cavern-beast-with-prized-massive-eggs-mandalorian-reference`, `dormancy-trigger-dune-fauna-reskin-lane-107-live-vfei2-dorma`, `drum-lure-subsurface-predator-lures-that-drum-juicy`, `egg-trap-clutch-birth-trap-eggs`, `glass-nub-light-pipe-flora`, `mirror-plated-sun-axis-asymmetric-giant`, `shade-commensal-micro-fauna-living-under-a-walking-giant`, `silverbole-owner-to-name-silver-required-heat-flame-immune-w`

**fall_line** (3): `feral-droid-behaviour-flee-prone-memwipe-capture-no-droid-re`, `feral-races-crash-survivors-pawnkind-permanent-mental-scar-h`, `wreck-shade-flora-pockets-gate-hardy-smalls-on-wreck-mutator`

**nightside_ice** (6): `chemical-frosts-ambiguously-alive`, `hectare-scale-sessile-catalytic-sheets-landform-catalysts`, `icy-insects-of-the-inclusions`, `the-one-move-animal`, `the-tunnelers-within-ice-blind-thermal`, `thermal-sensing-seam-striker`

**poison_forest** (3): `dark-crust-phototroph-flora-black-purple-red-films-on-starwa`, `eyeless-vibration-sensing-ambusher-the-signature`, `toxic-prized-meat-def-property-on-the-4-flagged-keepers-neeb`

**terminator_sea + the_grey_deep** (4): `salt-rimed-blade-flora-grey-shore-variant-distinct-def-from-`, `shadow-lane-detritivore-condensate-drinker-grey-shore-distin`, `the-ossuary-shrimp-man-sized-skeletal-seeming-shy-and-evasiv`, `the-pillar-mason-grey-monoculture-crystal-binding-film-that-`

**terminator_sea + the_twilight_deep** (6): `condensate-drinker-fog-lick-fauna`, `salt-rimed-blade-flora-black-sail-on-white-pan-planar-vertic`, `shadow-lane-detritivore`, `shore-scavenger-on-stranded-carcasses-stonecrab-hermitcrab-b`, `the-mold-mat-roof-organism-twilight-monoculture-shore-to-sho`, `the-twilight-deep-set-deferred-to-diving-mods-kelp-forest-fl`

**the_blue_desert** (4): `burner-fast-oxidizer-blue-fire-halo-at-speed-explodes-when-g`, `picker-ablation-line-scavenger`, `swallower-sealed-armored-herbivore-whole-root-swallow-anaero`, `transparent-fractal-flora-set-ferns-dandelion-heads-fuzzball`

**the_contagion** (1): `the-unfinished-random-stat-short-lived-chimera-spawns-goo-co`

**the_cracked_lands** (4): `bloom-crop-flood-week-boom-bust-harvest-visible-growth`, `emperor-vulture-the-sky-s-undertaker-rides-the-flats-thermal`, `sealed-signature-sleeper-wax-lined-burrow-water-wake-sheds-c`, `twisted-trees-shade-line-grasses-mosses-our-own-vegetation-o`

**the_fever_wood** (1): `ant-raider-wiring-theft-hauling-two-front-war`

**the_forge** (2): `contagion-corpse-ring-ambient-die-off`, `fleet-fliers-small-darting-fireweed-eaters`

**the_greentide** (2): `canopy-swinger`, `digestive-accelerant-fruit-the-fruit-that-yearns`

**the_miasma** (3): `delta-loam-composter-castings-producer`, `karr-fever-swarm-vector-pollinator-one-swarm`, `the-stranded-transitional-orphan-forms-2-3-species`

**the_propane_lakes** (2): `burner-polar-ascendant-form-blue-fire-halo-as-locomotion-alm`, `v-wake-propane-sea-exotic-kin-propane-native-agitated-by-pum`

**the_pyrelands** (1): `burrower-grazer-dives-under-the-burn-emerges-into-ash`

**the_rot** (4): `health-share-species-tagging-both-variants`, `heat-generating-gene`, `symbiont-parasites-three-ratified-bargain-pairs`, `tea-source-guardian-mushrooms-per-species-defense-repertoire`

**the_scald** (1): `welcome-blanket-thermophile-mats-rainbow-banded-by-temperatu`

**the_scarlands** (2): `mortuary-guild-carrion-specialist-dedicated-body`, `the-glowers-black-radiotrophic-crust-flora-crater-bowl-varni`

**the_slime** (1): `filter-feeder-line-scooping-mouthed-slime-grazers`

**the_webwork** (1): `parasitic-root-mat-flora-the-stolen-river-s-plumbing`

**wasteland** (5): `brine-battery-pool-owner-ion-gradient-discharge`, `excretor-herd-creature-metal-salt-bezoar-product-def`, `radiothermal-solitary-living-furnace-spacing-law`, `radiotroph-flora-dosimeter-lawn-vault-root-sequestration-tre`, `the-three-storm-weather-defs-ash-radiation-halo-plasma-termi`

**weeping_stones** (8): `blade-flora-with-bladder-fruit-forage-target-re-points-donor`, `burrak-burradar-well-digger-claw-combs-elder-form`, `mirrik-dew-smoke-swarm-dewsilk-cocoon-source`, `sillik-weep-face-licker-whisker-combs-prey-base`, `ssurr-crest-fan-display-reptile-the-romance-ruling-made-anim`, `tirbak-walking-cistern-caravan-colossus-dorsal-rain-fins`, `vhakk-the-warden-margin-apex-never-hunts-at-water-by-design`, `weep-mat-drip-garden-corduroy-mats-ridged-wind-square`

Each slug's full original text is still readable verbatim at
`ledger:<sheet>:<slug>` in `flora_assignment_register.decisions.json` — the slug
names above ARE the concept descriptions (the register never stored a shorter
label), so read the key itself for the pitch rather than guessing from the
truncated form.

## work owed (not done by this item)

For each of the 85: a build pass still needs to (1) turn the slug's prose into an
actual creature/plant/mechanic concept brief, (2) decide ThingDef/PawnKindDef shape
and naming (three-tier grammar, `design/NAMING_SCHEME_PLAN.md`), (3) commission
real art through the normal artpipe path (search `infrastructure/artpipe/done/` and
`pending/` by SUBJECT before queuing — this list was cleared against those
directories as of 2026-09-20, but time will pass before anyone builds against it),
and (4) get an owner ruling on anything ambiguous (several slugs are themselves
literally "owner candidate, not yet ruled" or "owner to name" — read the text).

**None of this was done by the filing pass.** No ThingDefs were authored, no
artpipe jobs were queued, no roster edits were made — this item exists purely to
hand a future build pass a pre-cleaned list instead of the raw 118.

## watch out

- **Re-verify currency before building anything off this list.** It was accurate
  2026-09-20; the daemon and other seats keep shipping art and defs continuously in
  this repo (see `sheet_orphan_118_ledger_2026-09-20.md`'s own catch of
  `RUT_PaleTree` landing the same day as the audit). Re-check
  `infrastructure/artpipe/done/`, `pending/`, `src/`, and open items by subject
  before spending a commission on any one slug.
- **Several slugs name a body-donor or mechanic dependency** (e.g. `desert:...
  body-donor-gr-paraceram`, `dune_sea...:...vfei2-dorma`) — read the full slug text
  for the donor/prior-art pointer before starting from scratch.
- **A few slugs are explicitly deferred within their own text**
  (`terminator_sea+the_twilight_deep:the-twilight-deep-set-deferred-to-diving-mods-kelp-forest-fl`,
  `fall_line:...` droid/pawnkind asks that may belong to a mechanics item rather
  than an art commission) — some of these 85 may turn out, on a closer read than
  this pass did, to be mechanics/behavior asks rather than pure art/def
  commissions, similar to `darkbeast-dark-halo-behaviour` (excluded from this list
  for exactly that reason). Read each slug's full text before queuing art for it.
- **Do not re-add** any of the 12 ALREADY BUILT, 20 OWNED-ELSEWHERE, or the 1
  FLAGGED row from the original 118 — see
  `Transient/sheet_orphan_118_ledger_2026-09-20.md` for exactly which and why.

## verify

- Each of the 85 slugs, when eventually worked, gets a real ThingDef/PawnKindDef
  OR an explicit drop/supersede ruling — never silently skipped.
- Before any art job is queued for a slug on this list, `infrastructure/artpipe/
  done/`, `pending/`, and `registry.jsonl` are re-checked by subject (not just
  defName) for a render that already exists.

## criteria

All 85 slugs resolved to one of: built, queued, dropped, or superseded — with the
ruling recorded per-slug, not as a bulk claim. This item does not close until that
accounting exists; a partial pass may close a sub-batch instead if that fits the
project's item-granularity practice better at build time.

## 2026-09-20/21 (FOUNDRY, offline subagent) — desert sheet's 4 remaining slugs resolved

Slice: the desert sheet's 4 slugs not already claimed by
`DESERT_STAGGERSEED_BUILD_1`/`DESERT_SHADE_PLANTS_DESIGN_1` (another agent, in
flight) or already built (`ultracactus`). Re-verified currency first, per this
item's own "watch out" — and found the re-verify caught real drift: two of the
four had ALREADY BEEN BUILT AND CLOSED by other work since this item's own
2026-09-20 audit (same day), which is exactly the "time will pass before anyone
builds against it" warning firing for real within hours, not days.

- **`burst-predator-flagship-bursts-grabs-retreats-to-cool` → BUILT, already
  closed.** `DESERT_BURST_PREDATOR_FLAGSHIP_1` shipped `RSW_WraidAlpha`
  (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_WraidAlpha.xml`,
  commit `1d9360a71`) before this slice started. No action needed; recorded
  here only so this slug is never re-queued.
- **`shade-grid-mapcomponent-shadeat-the-keystone` → BUILT, already closed.**
  This was the one slug this item's own "watch out" flagged as likely a
  mechanics ask in disguise (`kind: "C#"` in `rosters/desert.json`, not
  creature/plant) — correctly so, and it's done:
  `DESERT_SHADE_GRID_KEYSTONE_1` landed `RM_MapComponent_ShadeGrid.ShadeAt`
  plus two consumers (`RimMandrake.CreatureBehaviors`, commit `50c022770`)
  before this slice started. No action needed.
- **`filter-feeding-shade-whale-megafauna-body-donor-gr-paraceram` → BUILT
  (def), C# behavior split to a new item.** No prior work existed for this
  one (re-verified against `artpipe/done/`, `pending/`, `src/`, open items —
  clean). Authored `RSW_ShadeWhale`
  (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_ShadeWhale.xml`): a
  reskin of the already-ported `RSW_Horax` (body + art reused, retinted —
  same zero-new-PNGs precedent as `RSW_WraidAlpha`/`RSW_Wraid`), re-purposed
  herbivore/solitary per desert.md §4c, wired into `RUT_Desert.xml`'s
  `wildAnimals` alongside (not replacing) the `RSW_Horax` placeholder it
  supersedes as the biome's actual megafauna flagship. Carries
  `RM_ShadeSeekingWanderExtension` — existing, previously-unused C#
  infrastructure from `DESERT_SHADE_GRID_KEYSTONE_1` — so real shade-seeking
  behaviour ships day one. The register's own donor note ("body donor:
  GR_Paraceramuffalo, RESKIN SOURCE ONLY, GR_ defs never placed as-is") was
  followed as a scale reference (bs 16 target), not a literal art source —
  GR_Paraceramuffalo is a "dormant"-status cross-mod donor
  (`design/Jawa/fauna/animal_census.csv`, Vanilla Genetics Expanded), and
  reusing its texPath would have added a live external-mod art dependency
  the register's own rule reads as exactly what it was warning against.
  Filter-feeding and dung-seeding (desert.md §4c/§10 — no native
  `FoodTypeFlags` route) are real C# work, deferred per
  `rosters/desert.json`'s own "def can land first" note for this slug: filed
  as `DESERT_SHADE_WHALE_FILTERFEED_1`.
- **`glitter-birds-megafauna-shadow-commensals` → superseded/re-filed, not
  built.** This is a mechanics ask, not a pure art/def commission: desert.md
  §4c's "tiny glittering bird-like creatures that live their entire lives in
  one animal's shadow" needs a shade-FOLLOW behaviour (track a specific
  moving shadow, harder than the static `ShadeAt` query), and — caught only
  by reading past this slug's own text — `EXTREME_DESERT_GIANT_COMMENSALS_1`
  (open, unrelated dune_sea/deep_desert sheet) is already mid-design on the
  IDENTICAL mechanism for a different host. Filing a fresh design pass here
  would have duplicated that open item's own unresolved question. Filed
  `DESERT_GLITTER_BIRDS_COMMENSALS_1` instead, scoped to depend on
  `EXTREME_DESERT_GIANT_COMMENSALS_1`'s eventual shade-follow route rather
  than re-deriving it, and cross-referenced back onto that item so its own
  future builder knows there are two consumers now.

All four resolved (2 already-built found on re-verify, 1 built this pass, 1
re-filed as a correctly-scoped design item) — none skipped. 81 slugs across
the other 25 sheet groups remain untouched by this slice; this item stays
open.

## 2026-09-21 (FOUNDRY, offline subagent) — arid_shrubland sheet's 6 slugs resolved

Slice: all 6 arid_shrubland slugs. Re-verified currency first, per this
item's own "watch out" — re-read `arid_shrubland.md` in full (not just the
truncated slug names), `rosters/arid_shrubland.json`'s own `new_defs` entry
(which carries a `mechanic_load` tag per slug — "none blocking", "C#: ...",
or "unruled" — that drove every build-vs-file decision below), and
`RUT_AridShrubland.xml`'s own header comment (which independently confirmed
the same three "NOT this pass's scope" items the roster flagged). Also
checked `infrastructure/artpipe/{done,pending,registry.jsonl}` by subject for
all six before touching anything, and `design/Jawa/fauna/cast_assignment.csv`
before reusing any donor species' body/art (this caught a real conflict, see
tunnel-snake below).

- **`the-fuzz-knee-high-silver-green-canopy-plant` → BUILT.** `RUT_Fuzz`
  (`src/RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/RUT_Fuzz.xml`,
  `mandrake.rut.ashkarrflora`) — the biome's dominant groundcover (0.9
  commonality), replacing the `Plant_ShrubLow` placeholder the roster's own
  flora list documented as "the knee-high fuzz stand-in UNTIL THE FUZZ DEF
  LANDS." One art job filed, `rutfuzz_v1`
  (`infrastructure/artpipe/pending/rutfuzz_v1.json`) — `mechanic_load` reads
  "none blocking" so no companion mechanics item. Working name only, per
  arid_shrubland.md's own "Owed" naming list; folded into
  `ARIDSHRUBLAND_SHIPPING_NAMES_1` (filed this pass) rather than a solo card.
  `validate_patch.py` clean against the full 618-mod load set except the
  expected pending-texPath warning (same status as `RM_Venomvine`/
  `RUT_Staggerseed` at filing time).
- **`the-huge-grazer-large-young-parental-enrage-body-donors-famb` → BUILT
  (def), C# split to a new item.** `RSW_ShrublandGiant`
  (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_ShrublandGiant.xml`)
  — a reskin of the already-ported `RSW_Fambaa`/`RSW_Dewback` body and art
  (retinted, zero new PNGs, same `RSW_ShadeWhale`/`RSW_WraidAlpha`
  precedent), using Fambaa's own juvenile facing set for "large young" at no
  extra cost. The register's named donor pair was Fambaa/Mastmot — Mastmot
  has sounds already absorbed but no ThingDef was ever authored for it
  (checked this pass), so Fambaa is the sibling that actually landed.
  Converted from Fambaa's egg-laying amphibian profile to live-birth
  herbivore (no standing water in this biome), `trainability None` matching
  the sheet's "indifferent to the intelligent races" law. Wired into
  `RUT_AridShrubland.xml`'s wildAnimals at 0.35, alongside (not replacing)
  the pre-existing Ronto/Bantha/Corinathoth giants. Ships as a plain grazer
  — the life-stage + parental-enrage mechanic itself is real C# the biome
  doc's own "Owed" section flags as part of a still-unrun engine feasibility
  pass, so it's deferred per the `DESERT_SHADE_WHALE_FILTERFEED_1` precedent
  (def lands first, behaviour comp follows). Filed
  `SHRUBLAND_GIANT_ENRAGE_1`.
- **`tunnel-snake-analog-the-signature-corridor-predator` → BUILT.**
  `RSW_TunnelSnake`
  (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_TunnelSnake.xml`) —
  a reskin of the already-ported `RSW_Klorslug` body and art. The roster's
  own fauna list already carries `Terrorworm` (a foreign `mlie.horrors`
  donor) as an explicit interim at this band, `mechanic_load: "none
  blocking"`. Almost placed `Klorslug` itself directly instead — caught
  before doing it: `cast_assignment.csv` already assigns the *species*
  `Klorslug` to `RUT_Greentide` ("the Gnawers", row 177, status keep), so
  reusing it as-is here would have double-booked one species into two
  biomes' signature niches. Reused the body/art ASSET only (retinted, new
  defName), the same asset-reuse-without-species-reuse pattern
  `RSW_ShadeWhale` used on `RSW_Horax`. Wired into `RUT_AridShrubland.xml`'s
  wildAnimals at 0.5, alongside the Terrorworm interim (not removed, same
  not-replaced precedent). No companion mechanics item — this was a pure
  art/def commission.
- **`venomvine-fortress-flora-passability-by-body-size` → superseded/
  re-filed, not built.** Confirmed a mechanics ask, exactly the failure mode
  this item's own "watch out" names — `VENOMVINE_CONTACT_VENOM_BUILD_1`
  (built 2026-09-20, `10033074a`) shipped the desert-lineage `RM_Venomvine`
  and its own text explicitly named this slug as future work ("Do NOT build
  the shrubland thicket's body-size passability here... Just don't preclude
  it"). Filed `VENOMVINE_FORTRESS_PASSABILITY_1`, scoped to reuse
  `RM_Venomvine`'s existing plant/comp rather than inventing new terrain, and
  noting the art job already queued for the desert build
  (`rmvenomvine_v1`) was explicitly written to double as this biome's own
  venomvine art ("its shrubland sibling," per the job's own `style_notes`) —
  so no new art is owed here, only the size-gate C#.
- **`scrap-nest-bird-analogs-glittering-treasure-nests-steal-from` →
  superseded/re-filed, not built.** `mechanic_load: "C#: nest-theft/
  scrap-hoard"` in the roster — a mechanics ask, and the slug's own text
  flags the base-stealing half as an unruled "candidate" besides. Filed
  `SHRUBLAND_SCRAPNEST_BIRDS_1`, noting the bird-donor pick is still open
  (check `cast_assignment.csv` first, same care that caught the tunnel-snake
  conflict) and that the base-stealing candidate needs its own ruling before
  being built, not just the nest-theft mechanic.
- **`tree-guardian-uniques-owner-candidate-not-yet-ruled` → superseded/
  re-filed as an owner card, not built.** The only slug in this sheet the
  roster itself tags `mechanic_load: "unruled"` (every other slug got
  "none blocking" or a specific "C#: ..." tag) — its own name says exactly
  what it is. Filed `SHRUBLAND_TREE_GUARDIAN_1` as an owner-ruling card
  (`--needs offline`, same class as `STAGGERSEED_SHIPPING_NAME_1`) with four
  options (per-tree unique / generic guardian species / drop / owner's own
  idea), not as a build item — there is nothing to build until the ruling
  lands.

Also filed `ARIDSHRUBLAND_SHIPPING_NAMES_1`, an owner card covering the
working names shipped this pass (`RUT_Fuzz`, `RSW_ShrublandGiant`,
`RSW_TunnelSnake`) plus the biome doc's own pre-existing "Owed" naming list
(venomvine, the Stall/Gale) — one consolidated card rather than five solo
ones, since none of these builds is blocked on its own name landing.

All six resolved (3 built as def/art commissions, 1 def-built with its C#
split out, 2 re-filed as their own items — one mechanics, one owner-ruling
card) — none skipped. `validate_patch.py` run against all four touched/new
XML files plus the full 618-mod load set: 0 errors on the three built
defs and the biome file; the one expected warning is `RUT_Fuzz`'s pending
texPath. 75 slugs across the other 24 sheet groups remain untouched; this
item stays open.

## 2026-09-24/25 (FOUNDRY) — poison_forest sheet's 3 slugs resolved

Slice: all 3 poison_forest slugs (the smallest remaining group, picked over
the in-flight `dune_sea + deep_desert` ["Extreme Desert"] group to avoid
file collision with a parallel FOUNDRY subagent's flora build there, per
this session's own briefing). Re-verified currency first, per this item's
own "watch out": read `poison_forest.md` in full (FROZEN, `BIOME_FREEZE_
FABLE_REVIEW_1`), `rosters/poison_forest.json`'s own `new_defs` entries
(mechanic_load "none blocking (prep §12)" / "none" / "meat hediff def, no
C#" — none flagged "unruled"), `_assignment_prep.md` §5's IMPORT-candidates
notes (the ambusher's own "NEW ART/DEF NEEDED — no donor is vibration-themed;
nearest body: Biomes! Caverns blind fauna" pointer), and `RUT_PoisonForest.xml`'s
own header (which explicitly listed the toxic-meat chain as "NOT this pass's
scope" — stale, corrected in place, see below). Checked `infrastructure/
artpipe/{done,pending,registry.jsonl}` by subject for all three before
touching anything (clean — `sagecrust_v1`/`rot_sagecrust_v2` are an
unrelated the_rot subject) and `design/Jawa/fauna/cast_assignment.csv`
before reusing any donor species' body/art (caught the same class of
near-miss the tunnel-snake slug caught last wave — see below).

- **`eyeless-vibration-sensing-ambusher-the-signature` → BUILT.**
  `RSW_VentStalker` (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/
  RSW_VentStalker.xml`) — the prep doc's own suggested donor (Biomes!
  Caverns blind fauna) is not ported into this repo at all, so the body
  actually reused is the already-ported `RSW_Kinrath`: a blind ambusher by
  its own donor description ("could sense heat... navigate their way
  around"), already carrying the poisonous-appendage body group this
  biome's "everything is either sealed or poisoned" law wants. Checked
  `cast_assignment.csv` FIRST, same discipline that caught the tunnel-snake
  near-miss last wave: `Kinrath` itself is cast to `RUT_Greentide`
  ("canopy-ambush", row 184, status keep), so this def reuses the body/art
  ASSET only (new defName, retint, zero new PNGs — both `kinrath_v1` and
  `canon_kinrath_v1` artpipe jobs confirm real generated art already sits at
  the reused texPath) without double-booking the species. Re-themed
  heat-sense to ground-vibration-sense in flavor text only (no stat says
  "heat"). ComfyTemperature reset to poison_forest.md §0's own measured
  extremes; Kinrath's Odyssey-gated WebShot ability and egg-layer comp
  dropped for a plain live-birth profile (same simplification precedent
  `RSW_TunnelSnake` used reskinning Klorslug). Wired into
  `RUT_PoisonForest.xml`'s wildAnimals at 0.25.
- **`dark-crust-phototroph-flora-black-purple-red-films-on-starwa` →
  BUILT.** `RUT_DarkCrust` (`src/RimUtinni/UtinniPatches/Defs/
  ThingDefs_Plants/RUT_PollutedFlora.xml`) — no donor crust/lichen form
  exists for a bark/rock-face film specifically (the biome's already-admitted
  AB_* flora are upright growths, not the doc's own "moss on a north wall"
  comparison), so this is a plain new PlantBase groundcover rather than a
  reskin. One art job filed, `rutdarkcrust_v1`
  (`infrastructure/artpipe/pending/rutdarkcrust_v1.json`) — `mechanic_load`
  reads "none" so no companion mechanics item. Wired into wildPlants at 0.25,
  clearly subordinate to the dominant trees (0.5-0.6) per §4's own "tiny,
  marginal, crowded-out minority" line.
- **`toxic-prized-meat-def-property-on-the-4-flagged-keepers-neeb` →
  BUILT.** The roster's own fauna list flags exactly four keepers "toxic-
  prized-meat carrier": Neebray (donor `mlie.starwarsanimalcollection`),
  RSW_Screecher (ours — the slug's own stale `BMT_Screecher` spelling
  already corrected by `ROSTER_DEAD_BMT_NAMES_SWEEP_1`), Visceral (donor
  `mlie.horrors`), AA_Helixien (donor `sarg.alphaanimals`). Mechanism
  verified against the real engine before authoring anything (`rimsage
  read_csharp_symbol ThingDefGenerator_Meat`): a race's meat ThingDef is
  ENGINE-GENERATED at load time and only skipped when `race.specificMeatDef`
  is already non-null — there is no XML node to Add/Replace on a
  "Meat_Neebray"-style def, so patching one directly would have silently
  done nothing. Authored 4 hand-made meat ThingDefs
  (`RUT_PoisonForestPrizedMeats.xml`, `ParentName="OrganicProductBase"`,
  same shape as this mod family's own `RM_StockedPoolMeats.xml` precedent)
  and a patch (`Patches/PoisonForest_ToxicPrizedMeat.xml`) setting
  `<race><specificMeatDef>` on all four via `PatchOperationFindMod` on each
  donor's owning mod (the exact mod-NAME strings already proven live in this
  repo's own `MegafaunaYield.xml`) — `validate_patch.py`'s live xpath check
  confirms all four patches hit exactly one real node. The toxic half reuses
  `VanillaAnimalsExpandedWaste.IngestionOutcomeDoer_Toxic`, a donor C# class
  already absorbed wholesale into this SAME mod's own Assemblies/ and
  already live on `VAEWaste_ToxicMeat` in `Absorbed_VAEWasteMegatardi_
  Defs.xml` — zero new C#, matching `mechanic_load: "meat hediff def, no
  C#"` exactly. The "prized" half is `preferability RawTasty` (not the
  vanilla generator's default `RawBad`) plus a new positive thought pair
  (`RUT_PoisonForestMeatThoughts.xml`, one shared pair across all four
  meats — the slug's own title reads "def PROPERTY on the 4 flagged
  keepers", a single mechanical property, not four bespoke dishes) and
  above-market `MarketValue`, inverting the VAEWaste precedent's negative
  "disgusting" framing per poison_forest.md §7 ("the things a cook brags
  about surviving"). Placeholder art: vanilla meat-stack textures
  (`Meat_Small`/`Meat_Big` by body size) retinted per species — zero new
  PNGs, no artpipe job needed.

Also corrected `RUT_PoisonForest.xml`'s own header, which still called the
toxic-meat cuisine chain "NOT this pass's scope" — true when written
(2026-09-09, before this item existed), false now; left in place would have
misled the next reader the same way the stale `NAMING_SCHEME_EXECUTION_1`
citations did (CLAUDE.md's own logged incident).

Filed `POISONFOREST_SHIPPING_NAMES_1`, an owner card covering the two
working names shipped this pass (`RSW_VentStalker`, `RUT_DarkCrust`) — this
biome's own doc names no pre-existing "Owed" naming list the way
`arid_shrubland.md` does, so unlike that wave's card this one only covers
what this pass itself minted.

All three resolved (2 built as def/art commissions — one an asset reskin,
one a genuinely new PlantDef with art queued — 1 built as a pure def/patch
mechanism commission with zero new art) — none skipped.
`skills/rimworld-modding/scripts/validate_patch.py` run against all six
touched/new files plus the full 621-mod load set: 0 errors except the one
expected pending-texPath error on `RUT_DarkCrust` (same class, same
validator wording, as `RUT_Fuzz`'s own still-current state — re-checked
directly against that file this pass, confirming this is the standing
"art not landed yet" condition, not a regression); 8 informational/expected
warnings (4 vanilla meat-stack texPaths the validator cannot resolve from
loose files by design, 4 "test differs from inner xpath" notes explicitly
flagged "intentional for add-if-missing patterns"). `run_selftests.py`:
75/75 passed. 72 slugs across the other 23 sheet groups remain untouched;
this item stays open.

## Wave 10 (2026-09-25) — the_cracked_lands, 4 slugs, all resolved

Checked `git status`/`git log` first (per this item's own concurrency
warning) and found a concurrent FOUNDRY sibling mid-edit on `the_scald`
(uncommitted `RUT_WelcomeBlanket.xml` etc., later committed as that
sibling's own wave 9 at `4b94a2da6`) plus large uncommitted art batches for
`the_contagion`/`the_slime`/`nightside_ice` — avoided all four, picked
`the_cracked_lands` (untouched by anyone, confirmed via `git status`).

- **`emperor-vulture-the-sky-s-undertaker-rides-the-flats-thermal`** →
  BUILT. `RUT_EmperorVulture` (`ThingDefs_Races/RUT_EmperorVulture.xml`),
  `AnimalThingBase`/`Bird` body, native 1.6 flight (`MaxFlightTime` 60,
  `FlightCooldown` 2, `flightStartChanceOnJobStart` 0.6 — "rides the flats'
  thermals" read as a real mechanical property, most of its day spent
  aloft, same discipline RUT_FleetFlier's ComfyTemperatureMax used).
  `predator=false` + `foodType Carnivore`, same combination
  `RUT_MortuaryCrawler` (this item, the_scarlands wave) already used for a
  non-hunting carrion specialist. Checked `cast_assignment.csv`/
  `animal_census.csv` first: `BMT_CarrionVulture` (Biomes! Polluted Lands)
  is the only candidate donor and is recorded `dormant` — its mod is not
  in the active `ModsConfig.xml` list, so per the `GR_Paraceramuffalo`
  precedent (wave 1) it is not a live asset, only a scale/flavor
  reference — authored from scratch. "emperor vulture" is the sheet's own
  capitalized name, so no shipping-name card owed for this half.

- **`sealed-signature-sleeper-wax-lined-burrow-water-wake-sheds-c`** →
  BUILT as an interim. `RUT_SealedSleeper`
  (`ThingDefs_Races/RUT_SealedSleeper.xml`) uses stock
  `CompProperties_CanBeDormant`/`CompProperties_WakeUpDormant` —
  `CompWakeUpDormant.cs` read in full via RimSage this pass: its only wake
  triggers are `wakeUpOnDamage`, `wakeUpOnThingConstructedRadius`, and
  `wakeUpIfAnyTargetClose` (a `TargetingParameters` check); there is no
  stock water-terrain trigger, exactly matching the roster's own
  `mechanic_load` flag ("C#: water-trigger wake ... borrow the dormant
  comp"). Shipped with `wakeUpOnDamage=true` +
  `wakeUpOnThingConstructedRadius=6` (INVENTED) as the interim trigger,
  and a new companion item `RUT_CrackWax`
  (`ThingDefs_Items/RUT_CrackedLandsItems.xml`, `ResourceBase`, same shape
  `RUT_Bitumen` already used for this mod's "biome's signature material"
  pattern) wired as an interim `butcherProducts` yield rather than the
  sheet's actual "gathered off the flats after a wake" ground-drop. The
  genuinely-new piece — a small rare-tick comp that activates
  `CompWakeUpDormant` near real (non-boil) water terrain, plus the
  gather-after-wake job — is filed as its own dedicated item,
  `CRACKED_LANDS_SEALED_WAKE_MECHANISM_1`, rather than guessed at inline,
  same posture `PYRELANDS_BURROWER_GRAZER_1`/
  `MIASMA_KARRATHIL_POLLINATION_GATE_1` used for a genuinely-new,
  non-trivial C# piece. `receivesSignals=true` set per
  `CompProperties_CanBeDormant.ConfigErrors` (read via RimSage — required
  whenever `jobDormancy` is false).

  Checked `RUT_CrackedLands.xml`'s existing `wildAnimals` first:
  `RSW_MutagenicNorphea` ("the-Sealed, keep") and `AA_SandSquid`
  ("the-Sealed, adjust-keep") already tag the-Sealed bestiary SORT — same
  "sort-filler vs. signature flagship" gap `RUT_MortuaryCrawler`'s own
  header worked through for `AA_Helixien` one biome over. Both left
  untouched; this is a new fourth species, not a replacement.

  🔴 THE NAME IS NOT SETTLED — `RUT_SealedSleeper` is the INTERNAL working
  defName, same posture `RUT_MortuaryCrawler` used. Filed
  `CRACKEDLANDS_SHIPPING_NAMES_1` (owner card, both new working names —
  no existing `the_cracked_lands` naming-draft doc was found the way
  poison_forest/scarlands/propane_lakes/miasma each had one).

- **`bloom-crop-flood-week-boom-bust-harvest-visible-growth`** → BUILT as
  a ships-now-hooks-later stand-in. `RUT_BloomCrop`
  (`ThingDefs_Plants/RUT_BloomCrop.xml`), an ordinary `PlantBase`-derived
  fast-cycle crop (`growDays` 2.5, big yield). `EXPLOSIVE_PLANT_GROWTH_1`
  (the actual "visible growth" world mechanic this slug's real payload)
  checked and confirmed still open/proposed with no C# shipped this pass —
  same "stands in ... until it lands" posture `RUT_VWake`
  (`PROPANE_LAKE_PIPE_MECHANICS_1`, wave 6) used for its own deferred-
  mechanic half. Not wired into `wildPlants`: flood-week-only appearance
  is `EXPLOSIVE_PLANT_GROWTH_1`/`FLOOD_WITNESS_EVENT_1`'s own "the flood
  as an engine event" build territory, not invented here.

- **`twisted-trees-shade-line-grasses-mosses-our-own-vegetation-o`** →
  ALREADY BUILT (interim). `RUT_CrackedLands.xml`'s `wildPlants` already
  carries `RUT_TwistingThornwood` (tree), `RUT_TwistingThorngrass`,
  `RUT_TwistingThornweed` (all `RUT_PollutedFlora.xml`, donor-texture
  reskins of a "Biomes! Polluted Lands"-family plant set) plus `GRimMoss`
  — live, already wired at real commonalities. These satisfy the slug's
  content ask but are donor-texture reskins, not fresh art authored under
  `TREE_GRAPHICS_OWNERSHIP_1`'s "our own tree, our own scale" mandate
  literally (that item's own scope, re-read this pass, targets one named
  landmark tree — arid_shrubland's sweetline tree — not a general
  "replace every donor tree" campaign). A future fresh-art pass in that
  item's house style remains optional future work; not re-filed as new
  since `TREE_GRAPHICS_OWNERSHIP_1` already exists as the umbrella if the
  owner wants it extended.

Art: checked `infrastructure/artpipe/{done,pending,registry.jsonl}` for
"vulture"/"emperorvulture"/"sealedsleeper"/"bloomcrop"/"bloom crop" first —
clean. 7 jobs filed via `fill_queue.py`
(`rutemperorvulture_v1_{south,east,north}`,
`rutsealedsleeper_v1_{south,east,north}`, `rutbloomcrop_v1`).

Validation: `validate_patch.py --live` (2026-09-24T22-19-22Z dump)
`--defs` Data+Mods+Workshop+src/RimUtinni+RimMandrake+RimStarWars — 2
expected errors (`RUT_CrackWax`/`RUT_BloomCrop` own-namespace pending
texPath, same class as `RUT_DarkCrust`/`RUT_Fuzz` precedent), 6 expected
warnings (vulture/sleeper `PawnKindDef` pending texPaths). No C# touched
this wave. `deploy_custom_mods.py --mod UtinniPatches --apply`: applied,
then byte-diffed all 5 touched files repo-vs-deployed — all VERIFIED
identical (`RUT_EmperorVulture.xml`/`RUT_CrackedLandsItems.xml` deployed
silently without appearing in the tool's printed `+`/`~` summary — worth
flagging for whoever next touches `deploy_custom_mods.py`, since
CLAUDE.md's own standing warning is exactly "verify a def actually
deployed"). `run_selftests.py`: 75/75 passed, including
`selftest_deployed_biome_refs.py`.

All four slugs resolved (2 built new, 1 built as a ships-now-hooks-later
stand-in, 1 confirmed already built) — none skipped. 49 slugs across 15
sheet groups remain (`dune_sea+deep_desert`, `nightside_ice`,
`terminator_sea+the_grey_deep`, `terminator_sea+the_twilight_deep`,
`the_contagion`, `the_greentide`, `the_rot`, `the_slime`, `wasteland`,
plus `the_fever_wood`/`weeping_stones`/code-review-loop scopes still
excluded; `the_cracked_lands` now closed out); this item stays open.

## Wave 11 (2026-09-25, FOUNDRY, resumed session) — wasteland (5), the_slime (1), the_greentide (2) resolved; one live freeze violation caught and fixed

This item had been claimed and started by a prior FOUNDRY session that
rebooted mid-work: its ledger shard already carried 7 `file` events for new
sub-items (`WASTELAND_BRINE_BATTERY_CREATURE_1`,
`WASTELAND_BRINE_BATTERY_DISCHARGE_1`, `WASTELAND_EXCRETOR_BEZOAR_1`,
`WASTELAND_RADIOTHERMAL_SOLITARY_1`, `WASTELAND_SHIPPING_NAMES_1`,
`WASTELAND_STORM_WEATHER_DEFS_1`, `GREENTIDE_YEARNING_FRUIT_1`) with no
item prose written and nothing committed, but the actual def/XML authoring
for most of them was already done and sitting uncommitted in the working
tree, unfinished only in wiring/validation/write-up. This session verified,
fixed, wired, validated and finished that work rather than redoing it.

**wasteland (5 slugs), all resolved:**

- `radiotroph-flora-dosimeter-lawn-vault-root-sequestration-tre` → BUILT.
  `RUT_DosimeterLawn` (ground-cover) + `RUT_VaultRoot` (tree),
  `Defs/ThingDefs_Plants/RUT_WastelandFlora.xml`, wired into
  `RUT_Wasteland.xml` wildPlants at 0.15/0.08. Ships as plain flora; the
  actual dose-correlated-growth/ore-mining mechanics stay inside
  wasteland.md's own already-named "dose/geiger layer" engine-feasibility
  scope, not re-filed. Art job `rutvaultroot_v1` already queued by the
  prior session; `rutdosimeterlawn_v1` already landed in
  `infrastructure/artpipe/done/`.
- `excretor-herd-creature-metal-salt-bezoar-product-def` → BUILT, closed
  as `WASTELAND_EXCRETOR_BEZOAR_1`. `RSW_Excretor` (reskin of the
  already-ported, not-otherwise-wired `RSW_FeralNerf`, zero new art) +
  `RUT_MetalSaltBezoar` (`RUT_WastelandItems.xml`), wired at 0.15.
  `CompProperties_Shearable` retargeted from wool to the bezoar resource —
  the roster's "mechanic exists in donors" claim resolved to a plain
  vanilla comp, no donor C# needed at all.
- `brine-battery-pool-owner-ion-gradient-discharge` → BUILT (interim),
  closed as `WASTELAND_BRINE_BATTERY_CREATURE_1`. `RUT_BrineBattery`
  (`TurtleLike` body), wired at 0.1. Checked this repo's own XML for any
  absorbed EMP/zap comp first — none exists, so the roster's "comps exist
  in donor C# to borrow" claim does not hold for the live mod set (the one
  named candidate, `SW_Electrictick`, is both cast elsewhere and its
  owning mod is dormant). The discharge-as-defense mechanic itself split
  to `WASTELAND_BRINE_BATTERY_DISCHARGE_1` (open).
- `radiothermal-solitary-living-furnace-spacing-law` → BUILT (interim),
  `WASTELAND_RADIOTHERMAL_SOLITARY_1` stays open. `RUT_Radiothermal`
  (`QuadrupedAnimalWithPawsAndTail`), solitary/no-herd, wired into
  `RUT_Wasteland.xml`. Both halves of the roster's own mechanic_load (heat
  emission, same-species spacing law) are genuinely new C# with no vanilla
  or donor shortcut found — importantly, whether the vanilla
  `CompProperties_HeatPusher` (the building-heater comp) even attaches to
  a Pawn ThingDef is an ENGINE question this machine (WSL/Mac, no RimSage)
  cannot answer, so it is explicitly NOT assumed; the item's remaining
  scope says so and flags the Desktop check.
- `the-three-storm-weather-defs-ash-radiation-halo-plasma-termi` →
  re-filed as an owner-ruling card, `WASTELAND_STORM_WEATHER_DEFS_1` —
  wasteland.md's own Owed section already names this as a scope question
  ("the storm map-reshuffle... needs its own tooling and its own ruling"),
  not a def-authoring task; three options given (flavor-only now / full
  scope now / drop the mutator-churn half).

Also filed `WASTELAND_SHIPPING_NAMES_1` (owner card, all five working
names from this sheet, one consolidated card per this item's own
established pattern).

**the_slime (1 slug, the sheet's only one), resolved:**

- `filter-feeder-line-scooping-mouthed-slime-grazers` → BUILT.
  `RUT_SlimeGrazer` (new creature, no live donor — the one candidate,
  `BMT_Megakrill`, is dormant), wired into `RUT_Slime.xml` at 0.5. Ships
  the flagship of the "whole family" the sheet asks for, same
  one-representative-def posture every prior wave used for a family/line
  ask. Deliberately NOT wired into the parallel `RM_GelatinousSlime.xml`
  split mod — that item's (`GELATINOUSSLIME_RM_MOD_BUILD_1`) own build
  pass owns that second wiring op. `the_slime` sheet is now fully
  resolved.

**the_greentide (2 slugs), resolved — and a real mistake caught mid-wave:**

- `canopy-swinger` → BUILT, but its wiring needed a correction.
  `RSW_CanopySwinger` (reskin of the already-ported, not-otherwise-wired
  `RSW_KowakianMonkeyLizard`, zero new art) was found ALREADY ADDED
  directly to `RUT_Greentide.xml`'s live `wildAnimals` block by the prior
  session — but that file carries an explicit 🔴 FROZEN banner
  (`GREENTIDE_RM_MOD_BUILD_1`, 2026-09-22: "content lives in
  `mandrake.rm.greentide`; do not edit here") that a wave 5 note of this
  same item had already correctly identified and respected. **This was a
  real freeze violation, reverted this pass.** The correct route — proven
  by `WildAnimals_Greentide.xml`'s own existing pattern for exactly this
  situation — is a `PatchOperationAdd` onto `RM_Greentide`'s
  `wildAnimals`, so that's where the row now lives, filling the slot the
  dianoga vacated (owner ruling 2026-09-23, "the slot is reserved for a
  NEW creature"). Updated that patch file's own header, which had claimed
  a "verbatim mirror" of the frozen def that is no longer true now that a
  row has been added beyond it — left uncorrected, that claim would have
  misled the next reader the same way other stale-doc incidents in this
  repo's CLAUDE.md have. The live world (still running on the frozen
  `RUT_Greentide.xml` until Phase B's repaint) does not carry this row
  yet, by design.
- `digestive-accelerant-fruit-the-fruit-that-yearns` → BUILT (interim).
  `RUT_YearningFruit`/`RUT_YearningFruitHarvested`
  (`Defs/ThingDefs_Plants/RUT_YearningFruit.xml`) + `RUT_DigestiveAccelerant`
  (`Defs/HediffDefs/RUT_YearningFruit_Hediffs.xml`) — a genuinely new fruit
  (not a reskin of the sheet's existing, untouched Jogan/Muja rows), whose
  hediff ships the "digests fast / hunger returns / brief waddle" half for
  real with plain vanilla stats (`HungerRateMultiplier`, `MoveSpeed`), zero
  new C#. The "filth follows, ground sprouts" half needs a genuinely new
  comp (same shape as `RUT_VorrelBrood`'s
  `RM_HediffComp_ShadeStagger`, but filth/seedling instead of
  shade/germinate) — split out as `GREENTIDE_YEARNING_FRUIT_FILTH_1`.
  **Not wired into the world at all yet** — same frozen-`RUT_Greentide.xml`
  situation as the canopy swinger, except `WildAnimals_Greentide.xml` only
  covers `wildAnimals`, not `wildPlants`, so there is no existing patch
  route to reuse; `GREENTIDE_YEARNING_FRUIT_1` (stays open) notes this as
  owed, cross-referenced to `GREENTIDE_RM_MOD_BUILD_1`.

Also filed `GREENTIDE_SHIPPING_NAMES_1` (owner card, both new greentide
working names — no pre-existing greentide naming-draft doc was found).

**Art**: `rutbrinebattery_v1_{south,east,north}` and
`rutslimegrazer_v1_{south,east,north}` (filed by the prior session) had
FAILED in the daemon — both refused for the same reason, prompt text using
camera-angle language ("viewed from directly above") that contradicted the
declared per-facing stamp instead of describing the visible surface.
Re-filed as `rutbrinebattery_v2_*`/`rutslimegrazer_v2_*` with corrected
front/side/rear-view phrasing. New jobs filed for `rutradiothermal_v1_*`
(3 facings) and `rutyearningfruit_v1` (1 job, plant). Checked
`infrastructure/artpipe/{done,pending,failed,registry.jsonl}` by subject
for every one of these before filing anything, per this item's own
"watch out."

**Validation**: `validate_patch.py` caught real bugs of this session's own
making before anything shipped — three new files (`RUT_Radiothermal.xml`,
`RUT_YearningFruit.xml`, `RUT_YearningFruit_Hediffs.xml`) plus the
`WildAnimals_Greentide.xml` edit used a bare `--` inside XML comments
(illegal, breaks the whole file's parse) in prose written this session; all
fixed to em-dashes before the second run. Second run: 0 XML parse errors
across all touched/new files; remaining errors are the expected
own-namespace pending-texPath class (`RUT_MetalSaltBezoar`,
`RUT_DosimeterLawn`, `RUT_VaultRoot`, `RUT_YearningFruit`), same class as
every prior wave's new art. `deploy_custom_mods.py --mod UtinniPatches
--apply` and `--mod SWBestiary --apply`: both applied, all 8+2 touched
files byte-diffed repo-vs-deployed and VERIFIED identical.
`run_selftests.py`: 74/75 passed (wall 408.4s); the 1 failure
(`src/RimMandrake/TheRot/Tools/selftest_live_prep.py`) is PRE-EXISTING and
unrelated to this wave — it belongs to a separate, unrelated in-flight
biome-mod-split build (`src/RimMandrake/TheRot/`, untouched this pass) whose
own ThingDefs don't yet carry `RM_LivePrepExtension`.
`selftest_deployed_biome_refs.py` passed (400.4s), confirming this wave's
deployed defs resolve cleanly.

8 slugs resolved this wave (5 wasteland, 1 the_slime, 2 the_greentide) —
none skipped, one live mistake (the Greentide freeze violation) caught and
corrected rather than shipped. `the_slime` sheet is now fully closed out.
38 slugs across 8 sheet groups remain (`dune_sea+deep_desert` 8,
`nightside_ice` 6, `terminator_sea+the_grey_deep` 4,
`terminator_sea+the_twilight_deep` 6, `the_contagion` 1, `the_fever_wood`
1, `the_rot` 4, `weeping_stones` 8); this item stays open.

## Wave 12 (2026-09-25, FOUNDRY) — dune_sea+deep_desert, all 8 slugs resolved

Checked `git status`/`git log` first, per this item's own concurrency
warning, and found HEAVY concurrent activity across most of the remaining
groups: `nightside_ice` (untracked research docs dated today plus
failed-art jobs), `terminator_sea+the_grey_deep`/`+the_twilight_deep`
(modified `RM_TwilightSea.xml`/`RM_GreySeaCatch.xml`/catch tables plus 8
brand-new pending art jobs — 4 greysea + 4 twilightsea species, an exact
match to those two groups' slug counts), `the_fever_wood` (a same-day
naming pass, `fever_wood_rm_cast_proposal_2026-09-24.md`/
`fever_wood_syllable_variety_pass_2026-09-24.md`), and `the_rot` (STAGED
deletions of the old `RotSpecies` textures/patch under `UtinniPatches`,
mid-migration to a biome-mod split). All five avoided entirely. Picked
`dune_sea+deep_desert` (`rosters/dune_sea_deep_desert.json`'s `new_defs`,
9 rows including 2026-09-24's non-ledger "sand busters" amendment, which
is NOT one of this item's 85 and was left untouched) — confirmed clean of
any uncommitted work.

Read `dune_sea.md`/`deep_desert.md` in full (both FROZEN,
`BIOME_FREEZE_FABLE_REVIEW_1`) before touching anything. Found
`RUT_ExtremeDesert.xml` itself now carries its OWN fresh freeze banner,
dated 2026-09-24 (`STILLSAND_RM_MOD_BUILD_1`): "content lives in
`mandrake.rm.stillsand`; do not edit here." Every action below routes
through `RM_Stillsand` (invented, non-SW content, directly in that mod's
own Defs — no patch needed, Q11a) or was already routed through
`WildAnimals_Stillsand.xml` (genuine Star-Wars-named content) by earlier
work — never the frozen twin. This item's own "watch out" about editing a
frozen file directly (the Greentide lesson from wave 11) held again.

**Two of the eight slugs were ALREADY BUILT before this wave even
started**, found by reading the roster against `src/` rather than
assuming work was owed:

- `glass-nub-light-pipe-flora` and
  `silverbole-owner-to-name-silver-required-heat-flame-immune-w` → BOTH
  BUILT, closed under `EXTREME_DESERT_SIGNATURE_FLORA_1`.
  `RSW_LightPipeNub`/`RSW_Ollim`/`RSW_OllimWood`
  (`src/RimStarWars/SWBestiary/Defs/DesertPort/
  RSW_ExtremeDesertSignatureFlora.xml`), art rendered and deployed
  2026-09-24 (today), real non-placeholder textures on all three. The
  silverbole's final owner-ruled name is **ollim**
  (`EXTREME_DESERT_SIGNATURE_FLORA_1`, 2026-09-20) — "silverbole" survives
  only as descriptive prose, never a shipped name.
- `egg-trap-clutch-birth-trap-eggs` and
  `drum-lure-subsurface-predator-lures-that-drum-juicy` → BOTH BUILT,
  closed under `DRUM_LURE_PREDATOR_BUILD_1`, as a SINGLE creature:
  `RSW_Drazzik` (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/
  RSW_Drazzik.xml`) carries mechanic 1 (the vibration lure,
  `RimMandrake.CreatureBehaviors.RM_CompProperties_DrumLure`, real C#
  already shipped) AND mechanic 2 (the egg-trap clutch,
  `RSW_DrazzikEggFertilized`/`Unfertilized` via vanilla
  `CompProperties_EggLayer` + `ProximityHatch`) in one def. Already wired
  into `RM_Stillsand`'s live cast at 0.05 via
  `WildAnimals_Stillsand.xml`.
- `cavern-beast-with-prized-massive-eggs-mandalorian-reference` → BUILT,
  closed under `EXTREME_DESERT_CAVERN_BEAST_1`. `RSW_Zakkro` +
  `RSW_ZakkroEgg` (`src/RimStarWars/SWBestiary/Defs/DesertPort/
  RSW_Zakkro.xml`/`RSW_ZakkroEgg.xml`) — "the Mandalorian cave-beast"
  identified as Wookieepedia's mudhorn (already ported separately as
  ordinary wildlife, `RSW_Mudhorn`, which does NOT serve this design
  beat), so a distinct invented species was authored instead. Deliberately
  UNWIRED pending cavern map-generation, which the item's own scope
  correctly excludes as separate, larger work.

**Two slugs were genuinely new, built this wave — both RM_-tier (Q11a:
invented content, no Star Wars flavor), authored directly in
`mandrake.rm.stillsand` and wired straight into `RM_Stillsand_Biome.xml`'s
own `wildAnimals` (not the frozen twin, not the SW patch route):**

- `mirror-plated-sun-axis-asymmetric-giant` → BUILT. `RM_MirrorGiant`
  (`src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_MirrorGiant.xml`) —
  `EXTREME_DESERT_GIANT_COMMENSALS_1` (closed, design-only) had left open
  whether an existing giant (`RSW_KraytDragon`/`RSW_GreaterKraytDragon`/
  `RSW_WarWyrm`, all cast in `cast_assignment.csv` to a different
  ecological read — subsurface strike/bulk, never "surface-walking moving
  shadow") could be reskinned, or a new chassis was owed. Resolved as a
  new chassis: the sun-face/shade-face asymmetry dune_sea.md SS4 asks for
  is a property of the ART, which a uniform retint of an existing texture
  cannot express. Vanilla `QuadrupedAnimalWithHooves` body (Elephant/
  Muffalo family), no new BodyDef, no Star Wars dependency — correct for
  an RM_-tier def. Wired at commonality 0.0005, below every existing
  giant's own, per the sheet's "sparse to the point of discomfort" law.
  Corrected `RM_Stillsand_Biome.xml`'s own header comment in the same
  edit, which said `wildAnimals` was "all EMPTY here, on purpose" — true
  when written, false the moment this def landed.
- `dormancy-trigger-dune-fauna-reskin-lane-107-live-vfei2-dorma` → BUILT.
  `RM_DustHusk` (`src/RimMandrake/Stillsand/Defs/ThingDefs_Races/
  RM_DustHusk.xml`). The roster's own "107 live VFEI2 dormant rows"
  pointer (`_assignment_prep.md` §1.4) is PRECEDENT for the mechanic
  (confirmed `oskarpotocki.vfe.insectoid2` is genuinely active in the
  live 2026-09-24 ModsConfig snapshot, not stale-dormant per
  `animal_census.csv`'s own mod-status column), not an instruction to
  graft a live external mod's concrete ThingDef via `ParentName` — that
  would be a new, untested cross-mod inheritance shape this item has
  never used. Built instead on the SAME stock comp pair
  `RUT_SealedSleeper` (this item, wave 10) already proved out
  (`CompProperties_CanBeDormant`/`CompProperties_WakeUpDormant`,
  `wakeUpOnDamage` only — "blood," one of dune_sea.md's own three named
  triggers). The vibration/water triggers stay real future C# (same gap
  `RUT_SealedSleeper`'s own header measured in the stock class), not
  invented — satisfies the roster's own "no new C#" line as written.
  Grain-scale (bodySize 0.15, scaled off `VFEI2_Boomtick`'s 0.18 as a
  reference point only, no VFEI2 asset or def reused).

**One slug is a genuine mechanics ask, re-filed rather than forced:**

- `shade-commensal-micro-fauna-living-under-a-walking-giant` →
  superseded/re-filed. Filed `DUNESEA_SHADE_COMMENSAL_MICROFAUNA_1` as the
  THIRD consumer of the shared shade-follow mechanism
  (`EXTREME_DESERT_GIANT_COMMENSALS_1` raised it here first, closed
  design-only; `DESERT_GLITTER_BIRDS_COMMENSALS_1` is the second consumer,
  open) — same "do not re-derive, build as Nth consumer" posture wave 1
  used. Names `RM_MirrorGiant` (built this pass) as its now-real host.
  Filed via `rimflow file`, `## needs: offline`.

Art: checked `infrastructure/artpipe/{done,pending,registry.jsonl}` for
"mirror giant"/"sun-axis"/"dust husk"/"dormant" first — clean. 6 jobs
filed (`rmmirrorgiant_v1_{south,east,north}`,
`rmdusthusk_v1_{south,east,north}`), prompts written to require the
sun-face/shade-face split explicitly (a property no reskin could carry)
and the desiccated/matte look dune_sea.md's own hard ban demands.

Validation: `validate_patch.py --live` (2026-09-24T22-19-22Z dump)
`--defs` Data+Mods+Workshop+src/RimUtinni+RimMandrake+RimStarWars — 0
errors, 6 expected pending-texPath warnings (same class as every prior
wave's new art) across the 3 touched/new files.
`deploy_custom_mods.py --mod Stillsand --apply`: applied, `-> VERIFIED in
sync` on all 3 files (2 new, 1 modified). `run_selftests.py`: 73/75
passed; both failures are PRE-EXISTING and unrelated to this wave —
`src/RimMandrake/TheRot/Tools/selftest_live_prep.py` (the same in-flight
TheRot biome-mod-split noted in wave 11, still untouched by this pass) and
`src/RimMandrake/Utils/selftest_deployed_biome_refs.py` (1 unresolved
`RUT_Vorrel` reference from `RUT_Desert.xml`, traced to a concurrent
LongShade mod-split commit landed just before this session started —
`src/RimMandrake/Stillsand`/dune_sea/deep_desert content untouched by
that commit and not the cause).

All 8 slugs resolved (4 found already built by other closed items, 2
built new this wave, 1 re-filed as a scoped mechanics item) — none
skipped. `dune_sea+deep_desert` is now fully closed out. 30 slugs across
7 sheet groups remain (`nightside_ice` 6,
`terminator_sea+the_grey_deep` 4, `terminator_sea+the_twilight_deep` 6,
`the_contagion` 1, `the_fever_wood` 1, `the_rot` 4, `weeping_stones` 8),
all avoided this wave for live concurrent-agent activity except
`weeping_stones`, which was clean but not reached this pass; this item
stays open.
