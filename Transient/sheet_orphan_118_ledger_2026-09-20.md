# SHEET_ORPHAN_CONSUMPTION_1 — NEW-ART/DEF commission ledger (118 rows), final resolution

Scope: the item's fourth channel, "NEW-ART/DEF commission ledger (`decision=in`), 118
rows" — the only channel of the five never touched by any prior pass beyond a
read-only audit. Measurement-and-safe-filing only, per this pass's own brief: no
ThingDefs authored, no art jobs queued. Offline, no bridge, no game restart.

## Source of the 118

All 118 rows are `ledger:<sheet>:<slug>` keys inside
`design/Jawa/worldbuilding/review/flora_assignment_register.decisions.json`
(`.decisions`), **all** carrying `decision: "in"` — confirmed by parsing the JSON
(not grepping): exactly 118, zero elsewhere (the fauna decisions file carries zero
`ledger:` keys). They span 27 biome sheets. This matches the 2026-09-12 audit
(`Transient/sheet_orphan_audit_2026-09-12.md` §4) exactly.

## Method

1. Re-parsed the 118 `ledger:` keys directly from the decisions JSON (script, not
   eye-count).
2. Re-verified the 2026-09-12 audit's specific claims by reading the cited XML/items
   directly — every one still held (see "already built" and "owned elsewhere" below).
3. Ran a fresh automated token screen of **all 118** slugs (not just the ~130
   previously spot-checked) against: `infrastructure/state/items/*.md` +
   `items/closed/*.md`, `design/Jawa/worldbuilding/biomes/kits/*.md`, every `.xml`/
   `.cs` under `src/` (content, not filename), every `infrastructure/artpipe/done/`
   and `pending/` job file (content), and `registry.jsonl`.
4. Checked directly for a `"ledger:"` citation anywhere in artpipe (`done/`,
   `pending/`, `registry.jsonl`) the same way the flora `art:improve` channel matched
   on `"Source row: flora:<biome>:<defName>"` — **zero hits**, confirming no artpipe
   job has ever been filed against this specific channel by name.
5. The broad token screen (3 longest distinctive tokens per slug, ≥6 chars,
   substring match) produced hits on 116/118 rows — almost all noise: generic words
   (`grazer`, `predator`, `megafauna`, `animal`, `species`) matching unrelated
   creature/plant jobs and unrelated doc prose. Every non-trivial hit was read by
   hand; only one produced a genuinely new finding (`RUT_PaleTree`, below) beyond
   what 2026-09-12 already found. This confirms 2026-09-12's own warning: the screen
   is a candidate generator, not proof, and the manual read is where the actual
   verification happens.

## Result: 118 = 12 ALREADY BUILT + 20 OWNED ELSEWHERE (build deferred to a named
live item) + 1 FLAGGED (contradicts a separate decision channel) + 85 GENUINELY OWED

| status | count |
|---|---:|
| **ALREADY BUILT** | **12** |
| **ALREADY QUEUED** (artpipe job citing this channel) | **0** |
| **SUPERSEDED / OWNED ELSEWHERE** (named by a live mechanics item or kit spec, build/art deliberately deferred there — filing again double-books it) | **20** |
| **FLAGGED** (not a new commission at all; conflicts with a separate, already-adjudicated decision channel) | **1** |
| **GENUINELY OWED** | **85** |

### ALREADY BUILT (12) — a def (and often art) already ships for this concept

| slug | sheet | what shipped | evidence |
|---|---|---|---|
| `cindermare` | forsaken_crags | `RSW_Cindermare` ThingDef + PawnKindDef | `src/RimStarWars/SWBestiary/Defs/Livestock/ThingDefs_Animals/ThingDefs_ForsakenCrags.xml`; items `FORSAKEN_CRAGS_PREDATORS_BUILD_1`/`FORSAKEN_CRAGS_FAUNA_1`; built 2026-09-01, **predates the register's own 2026-09-10 grading** |
| `skarnix` | forsaken_crags | `RSW_Skarnix` ThingDef + PawnKindDef | same files; same pre-dating caveat |
| `fire-hawk-twig-carrying-raptor-analog` | the_pyrelands | `RUT_FireHawk` ThingDef + PawnKindDef + think tree | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PyrelandsFauna.xml`; real art in `infrastructure/artpipe/done/pyrelands_firehawk_v1*`; item `PYRELANDS_FIRE_WEB_COMMISSION_1` |
| `furnace-beast-thermal-circuit-megafauna` | the_pyrelands | `RUT_FurnaceBeast` ThingDef + PawnKindDef | same file; art in `infrastructure/artpipe/done/pyrelands_furnacebeast_v1*` |
| `quickgrass-rakatan-feral-forage-crop` | the_pyrelands | `RM_FE_Plant_Quickgrass` | `src/RimMandrake/Pyrelands/Defs/ThingDefs_Plants/Quickgrass.xml`, built and deployed |
| `scorch-fruit-plant-yield` | the_pyrelands | `RM_FE_Plant_ScorchFruit` + yield def | `src/RimMandrake/Pyrelands/Defs/ThingDefs_ScorchFruit/ScorchFruit.xml` |
| `living-bolts` | the_rust_cathedral | `RUT_LivingBolt` ThingDef + PawnKindDef + think tree | `src/RimUtinni/RustCathedralHum/Defs/ThingDefs_Races/RUT_LivingBolt.xml` |
| `sweetline-trees-huge-ancient-giant-wool-snag-harvest` | arid_shrubland | `RUT_SweetlineTree` | `src/RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/RUT_AshkarrFlora_Plants.xml`, commit `0d42dd16a` (2026-09-06) — **predates the sheet's own grading date**; not yet wired into `wildPlants`, art is placeholder — incomplete, not absent |
| `rename-ledger-rsw-reefback-...` | terminator_sea+the_grey_deep | `RSW_Reefback` ThingDef, real art, cast into `RUT_GreySea.xml` | slug text itself ("rename-ledger-") shows this was always a rename request on an existing def |
| `rename-ledger-rsw-lanternwhale-...` | terminator_sea+the_twilight_deep | same pattern, another live RSW sea-beast def | same |
| `darkbeast-dark-halo-behaviour` | forsaken_crags | `AA_Darkbeast` (donor) already cast into `RUT_ForsakenCrags.xml` | the slug asks for a new "dark halo" *behavior* on an already-existing creature, not a new one — a mechanics ask, not an art/def commission; out of this channel's scope either way |
| `the-pale-tree-anima-reskin-light-side-psycast-subset` | the_rot | `RUT_PaleTree` + `RUT_PaleMoss` ThingDefs, Royalty-gated anima-tree reskin | `src/RimUtinni/RotSporeKit/Defs/ThingDefs_Plants/RUT_PaleTree.xml`; item `ROT_PALE_TREE_1`; **art landed TODAY, 2026-09-20** (`rot_paletree_v3`, `rot_palemoss_v2`, `ROT_FLORA_FAUNA_VERDICTS_1`) — new finding this pass, not caught by the 2026-09-12 audit |

⚠️ Two of these (`sweetline-trees`, `cindermare`+`skarnix`) **predate the sheet's own
2026-09-10 grading**, and `pale-tree`'s art landed the same day as this audit —
meaning the register wasn't just stale against later rulings, it re-surfaced
concepts that were already answered, sometimes years before, sometimes hours before.

### SUPERSEDED / OWNED ELSEWHERE (20) — a live item or kit spec already owns the build, art deferred to the roster pass

Filing a fresh commission for any of these would double-book a concept a different,
still-open item already tracks. All 5 kit specs and 3 mechanics items cited below
were re-checked today and are still live/open (not closed, not stale):

- `the_rust_cathedral:coolant-eels` — `rust_cathedral_kit_spec.md` §3; item
  `RUST_CATHEDRAL_MECHANICS_1` (**still open**) explicitly names §4 eel-fishing as
  untouched. No `CoolantEel` def exists.
- `the_sump:` `tar-beast`, `wick-plant`, `sump-mouse`, `edge-chemotroph` — all four
  scoped in `sump_kit_spec.md`, each deferred to the roster pass. `sump-mouse` has a
  placeholder stub already (`RUT_Placeholder_SumpMouseRace`), confirming it's tracked,
  not orphaned.
- `the_greentide:` `gnawer`, `greatbole`, `shatterer` — `greentide_kit_spec.md`;
  item `GREENTIDE_MECHANICS_2` (**still open**) owns all three. **Re-verified deeper
  than 2026-09-12**: `greatbole` already has a real `RUT_GreatboleHeartwood` +
  `RUT_GreatboleCore` ThingDef (mineable building, M12) shipping **placeholder art,
  DEPLOY_HOLD** per its own header comment — a def exists, only bespoke art is owed,
  and that debt is already GREENTIDE_MECHANICS_2's, not a fresh commission. `gnawer`
  has a `RUT_Placeholder_GreentideGnawerRace` (recolored squirrel stand-in, "roster
  content owed" per its own header) — same story, same owning item.
- `the_fever_wood:` `thornbug-nectar-beast`, `seep-oil`, `the-deep-thing` —
  `fever_wood_kit_spec.md` §F4/§F8; the-deep-thing is explicitly "plot-reserved,
  Owed"; `RUT_Thornbug` PawnKindDef is named as "roster pass owns stats/art" —
  tracked, not orphaned.
- `the_miasma:` `rainbow-flora-suite`, `warden-mother` — `miasma_kit_spec.md`,
  item `MIASMA_MECHANICS_1` (**still open**).
- `the_scald:` `bubble-sailor`, `silver-shoal` — `scald_kit_spec.md`, item
  `SCALD_MECHANICS_1` (**still open**).
- `the_webwork:` `egg-mite`, `pale-flowers`, `wyyyschokk-guild-pawnkinds` —
  `webwork_kit_spec.md`. ⚠️ The guild-pawnkinds row (`nettik`/`chirrik`/`rothrik`)
  is a genuinely **different** ask from the existing `Wyyyschokk` art already in
  `infrastructure/artpipe/done/` (`wyyyschokk_v1_*`) — that art redoes the
  pre-existing Shokk creature; this row asks for three new guild pawn kinds. Still
  correctly OWNED-ELSEWHERE (webwork_kit_spec.md names it), just not "already done"
  by the existing Wyyyschokk art.
- `the_scarlands:plated-grazer...` — `scarlands_kit_spec.md` (scaria-onset section).
- `the_forge:tibanna-gland-harvest-on-the-beldon` — folded into item
  `FORGE_MECHANICS_1` (**still open**) §F2; `TIBANNA_SOURCE_CUT_1` (closed) ratified
  beldon-only tibanna, consistent with this deferral.

### FLAGGED (1) — not a new commission; conflicts with a different, already-run decision channel

`ledger:forsaken_crags:dusk-rat-art-redo` asks for an art redo of `AA_DuskRat`. But
`design/Jawa/worldbuilding/review/creature_art_register.decisions.json` already
carries `c:AA_DuskRat` → `decision: "approve"` (prefill `owner0823`) — a **separate,
already-run** curation channel that approved the creature's current art rather than
flagging it for redo. This row is not a "new commission" at all (it has no business
in a NEW-ART/DEF ledger) and it contradicts a decision already made elsewhere.
**Not filed as owed and not treated as done** — this is a data-quality artifact in
the register itself, flagged for an owner/BENCH call on which channel is
authoritative, not a FOUNDRY judgment call.

### GENUINELY OWED (85)

No live def, no art, no owning item or kit-spec deferral, no conflicting decision
found for any of these 85. Full list grouped by sheet (also filed verbatim into the
new item, see below):

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

## What was NOT done, deliberately

Per this pass's brief, this is measurement-and-safe-filing only for this channel —
the register's own data-quality problems (concepts re-surfacing already-shipped or
already-owned work, one row contradicting a separate decision channel) mean the
84-remaining "commission" reading of the sheet cannot be trusted blind, matching the
concern already on record in the item file. No ThingDef was authored, no art job was
queued, no `apply_assignment_verdicts.py --apply` was run. The 85 genuinely-owed
slugs are filed as a fresh, clean, already-verified starting list via a new item (see
`SHEET_ORPHAN_CONSUMPTION_1.md`'s closing section for this channel) instead of
leaving the noisy original 118 to be re-audited by whoever eventually builds them.

## Confidence

- The 12 ALREADY BUILT rows were each verified by reading the actual def XML or item
  file, not by keyword hit alone.
- The 20 OWNED-ELSEWHERE rows were each re-checked today against a still-open item or
  still-live kit spec (none had closed or gone stale since 2026-09-12).
- The 1 FLAGGED row was found by checking `creature_art_register.decisions.json`
  directly for the referenced defName, not by keyword screen.
- The automated token screen covered all 118 (not a ~130-hit subset across two
  passes, as before), but it is still a screen: false positives dominate, and a
  concept with no defName-shaped keyword (most of these 85 are, by design, requests
  for creatures/plants that don't exist yet and so have no distinctive on-disk name
  to find) cannot be proven absent by grep alone — only by there being no def, no
  art, and no owning item, which is what "genuinely owed" means here, not "proven
  impossible to find any evidence for."
- Not done: a `git log -S` per slug, a savegame check, artpipe's `_withdrawn`/
  `failed` folders (checked `done`/`pending`/`registry.jsonl` only — a job that was
  queued and then withdrawn or failed wouldn't show as "already queued" here, which
  is the conservative direction: it would just look genuinely owed again, not
  falsely done).
