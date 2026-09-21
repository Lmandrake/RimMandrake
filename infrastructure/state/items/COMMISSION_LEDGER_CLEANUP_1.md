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
