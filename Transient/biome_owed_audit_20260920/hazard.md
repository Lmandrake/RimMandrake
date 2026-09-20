# Biome Owed-Work Audit — hazard sheets (the_forge, the_scald, the_miasma, the_sump, the_fever_wood, the_rust_cathedral, the_greentide, the_scarlands, the_slime, the_slime_gene_lists)

Audit date 2026-09-20. Method: read each sheet's `## Owed` section in full, split
each bullet into individual work items, then for each item check
`infrastructure/state/items/*.md` and `infrastructure/state/items/closed/*.md`
(via `rimflow show`), the per-biome roster JSON in
`design/Jawa/worldbuilding/biomes/rosters/*.json` (its `new_defs` array is the
sheet's roster/creature owed work broken into individually named defs), and
`src/` for whether a def actually exists on disk. A "kit" item
(`*_MECHANICS_1/2`) was checked line-by-line for whether it actually mentions
the specific creature/flora, not just the biome's mechanics generally — several
kit items (Fever Wood, Rust Cathedral, Greentide) turned out to honestly track
their own creature gaps in detail; others do not mention the gap at all.

~58 individual owed sub-items examined across the 10 sheets (Owed bullets ×
each roster JSON's `new_defs` breakdown).

## the_forge.md

5 Owed bullets → ~9 sub-items.

- `FORGE_MECHANICS_1` — **FILED**, live, state `doing`. Real build progress
  confirmed (F2 tibanna-tap on `RSW_Beldon` shipped; kit spec drafted; owner
  cards ruled 2026-09-12).
- `TIBANNA_EMBARGO_PLOT_1` — **FILED, DONE** (closed `f2926bfe`).
  `TIBANNA_SOURCE_CUT_1` (cited as already executed) — **CONFIRMED closed**.
- Roster bullet (Beldon, Fumerider rename, fleet fliers, flash-flora +
  fireweed): the real assignment pass ran (`rosters/the_forge.json`,
  authored 2026-09-09) — Beldon kept (predator flag corrected to placid),
  fireweed/fire-lavender/magma-cactus flora assigned. But its own
  `new_defs` array flags **fleet fliers** (small darting fireweed-eaters,
  §4) as a creature with no def yet, and search found no queue item that
  owns building it. — **UNFILED.** Searched: "fleet flier", "fleet
  fliers", "fireweed-eater" (0 hits in items/ or items/closed/, only design
  mentions in `forge_kit_spec.md` and the roster JSON itself).
- Canon-sitting bullet (sacred-geography correction, Tribes precept,
  smeltery history, Empire roster entry): only traceable to the generic,
  superseded chain `CANON_LORE_PROPAGATION_1` → `CANON_DRAIN_1`; not
  verified line-by-line against Forge's specific asks. — **UNCERTAIN.**

## the_scald.md

7 Owed bullets → ~12 sub-items.

- `SCALD_MECHANICS_1` — **FILED**, doing. Real progress: silver-shoal fish
  (`RUT_Eesh`) and the bubble-sailor's *catch* item both shipped via
  `FISH_BESTIARY_BUILD_1` (live, doing). But the item's own text says
  outright: *"the real bubble-sailor `PawnKindDef`/`ThinkTreeDef`/`DutyDef`
  ... nothing live"* — the roaming creature itself is unbuilt, tracked
  honestly inside this item (not a silent gap).
- `SCALD_DARK_TOWER_1` — **FILED, DONE** (closed `da71770d`).
- 🔴 **Bottom-walker herd — UNFILED, and never even entered the roster
  pass.** The Scald's submerged mat-mowing megafauna (§4, one of only 4
  named residents; their dung is the entire silver-shoal food chain) does
  **not appear in `rosters/the_scald.json`'s `new_defs` at all** — it fell
  through the assignment pass itself. It surfaced only because
  `SCALD_DIVING_MOD_1` (a different, later item) happened to check and
  found *"zero bottom-walker PawnKindDef/ThingDef exist in the live def
  set"*, and explicitly declined to build one (*"would invent lore outside
  this item's charter"*). No item anywhere owns authoring this creature.
  Searched: "bottom-walker", "bottom walker", "mat-mower", "the_scald.json
  new_defs" (absent from the array itself).
- "Two seas' enrichment" bullet — **effectively DONE, sheet text is
  stale.** `the_grey_deep.md` and `the_twilight_deep.md` (full seabed
  design sheets) were written the *same sitting*, 2026-09-07 — the Scald
  sheet's "next sitting" language just never got updated to point at them.
  Not a filing gap; a sheet-decay note.
- Salinity ruling bullet — **DONE** (ruling recorded in the sheet itself,
  §3; terrain fields already shipped per `LIQUID_BIOMES_MAP_1`).
- Canon-sitting bullet — same **UNCERTAIN** as Forge's (generic
  `CANON_DRAIN_1` chain, not verified per-line).

## the_miasma.md

5 Owed bullets → ~11 sub-items (the roster bullet alone splits into 5 via
`rosters/the_miasma.json`'s `new_defs`).

- `MIASMA_MECHANICS_1` — **FILED**, doing, real spike-pass progress
  (surge/salt-line, fever-forged boons).
- Roster items, checked individually against `new_defs`:
  - **warden mother** (placed set-piece elder) — mentioned in
    `MIASMA_MECHANICS_1` as a design constraint ("placed, never random") —
    **tracked**, build state unclear.
  - **the stranded** (transitional orphan forms) — mentioned as the kit
    spec's "last v1 mechanic" — **tracked**.
  - 🔴 **karr- fever-swarm** (the disease vector AND *"the mangals' only
    pollinator... you cannot have the trees without the fever"*, §4) —
    **UNFILED.** Zero hits for "fever-swarm" or "karr-clade" in any item
    except a passing hediff-mechanic mention in the kit spec (a
    *Swarm-marked* status effect, not the creature build). No item owns
    authoring this def, and the sheet itself says the mangal ecosystem
    doesn't function without it.
  - 🔴 **delta-loam composter** (burrowing muck-worker, §4 and §7 trade
    good) — **UNFILED.** Zero hits anywhere for "delta loam"/"composter"
    outside the sheet and roster JSON.
  - 🔴 **rainbow flora suite** (3–4 genuinely-benign blooms, §4/§6 —
    explicitly hard-banned from ever being a trap, unlike the Scarlands'
    rainbow pools) — **UNFILED.** Zero hits anywhere.
  - Attar/delta-loam/flotsam item chain — rides the same gap as delta loam
    above.
- `LIQUID_TYPES_MOD_1` — **FILED**, live, doing (cross-cutting, covers
  brackish/brine grades generally, not Miasma-specific).
- Canon-sitting / cross-flow bullets — **UNCERTAIN** (same generic chain).

## the_sump.md

3 Owed bullets → ~9 sub-items.

- `SUMP_MECHANICS_1` — **FILED**, doing, and unusually explicit about its
  own gaps: *"Owed, not done, explicitly: the real sump-mouse
  `PawnKindDef`/`ThingDef`... stays the roster pass's own work, not
  authored [here]"* — the item itself disclaims ownership of the creature
  build even while tracking it. Tar beast (S3) and mouse-line telegraphy
  (S4) explicitly BLOCKED per the item's own text.
- **sump-mouse** (the prey base / mouse-line instrument, §4) — tracked
  inside `SUMP_MECHANICS_1` as explicitly not-yet-owned by anything — a
  half-step better than fully unfiled (the gap is named and visible) but
  **no item actually claims the build**. — borderline **UNFILED**.
- **tar beast** (Patient-family set-piece) — same pattern: tracked as
  blocked inside `SUMP_MECHANICS_1`, not independently filed.
- 🔴 **wick-plant** (the crop — "light as a crop", §7's signature trade
  good, farmed by every station) and **edge-chemotroph ring flora** (§4) —
  **UNFILED.** Zero hits anywhere outside the sheet/roster JSON; not even
  named inside `SUMP_MECHANICS_1`'s text the way sump-mouse/tar-beast are.
- Roster/cross-flow bullets — bumbledrone verdict cited but not
  independently verified this pass (`UNCERTAIN`).

## the_fever_wood.md

5 Owed bullets, but this sheet is the **best-tracked** of the ten — its
kit item is unusually explicit.

- `FEVER_WOOD_MECHANICS_1` — **FILED**, doing. Per-mechanic (F1–F9)
  breakdown with honest PROVED/BLOCKED/OWED status per piece, including:
  - **the deep thing (F4)**: *"PROVED (gate + seam only), rest OWED by
    design... the L-effort remainder (`RUT_TenantEmergedMass`,
    `RUT_TenantTentacle` pawn wiring, all art) is explicitly not done —
    off the critical path by the sheet's own design, not silently
    skipped."* — this is FILED and honestly tracked, not a Blue-Desert-style
    miss.
  - **thornbugs (F8)** — PROVED (built).
  - **ant raiders (F9)** — C# scaffolding built; FactionDef/quest wiring
    explicitly not yet done, tracked.
  - **boughway network (F6/F7)** — BLOCKED on `GREENTIDE_MECHANICS_1`'s
    Greatbole class not existing in `src/` yet (verified: it does not).
- **They/Them ant mod verification** (BENCH's delegated call) — not
  independently re-verified this pass; **UNCERTAIN**.
- Canon-sitting bullet — same generic-chain **UNCERTAIN**.

Verdict: nothing UNFILED here that isn't already visibly tracked inside the
filed item itself.

## the_rust_cathedral.md

5 Owed bullets → ~7 sub-items.

- `RUST_CATHEDRAL_MECHANICS_1` — **FILED**, doing, "4/6 sections" built per
  its own tally: walls, cockroach reskin, hum-mood, living bolts all done.
  Living bolts (§3) and coolant eels (§4, mechanically) are **DONE**.
- **Coolant eel as a fish** — **FILED, live**, via `FISH_BESTIARY_BUILD_1`
  ("Rust Cathedral (canals) — veen" row).
- **Cockroach-mod candidate** — **DONE**, verified and wired
  (`LingLuo.Cockroach`, confirmed ACTIVE in the mod list per the item text).
- `LIQUID_TYPES_MOD_1` — cross-cutting, **FILED**, doing.
- Donor def reconciliation, canon-sitting (naming settlement propagation)
  — **UNCERTAIN**, generic chain only.

Verdict: this sheet's Owed work is the most completely filed and built of
the ten.

## the_greentide.md

7 Owed bullets → ~13 sub-items.

- `GREENTIDE_MECHANICS_2` (successor to the closed-at-spec-only
  `GREENTIDE_MECHANICS_1`, which the sheet's own Owed text still cites by
  the dead `_1` name — a live instance of the CLAUDE.md-flagged decay
  pattern) — **FILED**, doing, heavy real build progress: wet-bulb, dry-air
  blower, churnmud, causeways, Lunger ambush comp all shipped or
  spiked. **Gnawer and Lunger both ship as explicit placeholder
  PawnKindDefs** (`RUT_Placeholder_GreentideGnawer`,
  `RUT_Placeholder_GreentideLunger`) with the real creature content
  honestly flagged as "roster/design content" still owed.
- **Shatterer** — no HediffDef/PawnKindDef exists yet in `src/`
  (confirmed via grep); tracked inside the item as roster-owed, not
  independently filed.
- `EXPLOSIVE_PLANT_GROWTH_1` — **FILED**, live, doing (parent engine item).
- Def rename ("the Greentide" label) and Wildsteam template pass — not
  independently verified; **UNCERTAIN**.

Verdict: creature gaps (Gnawer, Shatterer, canopy Swinger) are real but
honestly tracked with shipped placeholders, not silent — same pattern as
Fever Wood/Rust Cathedral, not the Blue Desert failure mode.

## the_scarlands.md

6 Owed bullets → ~10 sub-items.

- 🔴 **`SCARLANDS_MECHANICS_1` is a DEAD ID** — the sheet's own Owed
  section still names it as the live filed item; it was superseded by
  `SCARLANDS_MECHANICS_2` on 2026-09-14 and no longer exists as `live` or
  `closed` under that name (it's simply gone from the ledger). This is a
  stale-citation flag, same class as the CLAUDE.md-documented
  `NAMING_SCHEME_EXECUTION_1` decay pattern — not itself a missing-work
  finding (the successor covers the same scope and is filed, doing), but
  worth fixing in the sheet if it weren't frozen (it is — flagging only).
- **Plated-grazer scaria onset** — **DONE**, per `SCARLANDS_MECHANICS_2`'s
  own text: *"shipped, not just defined."*
- 🔴 **"The Glowers"** (black radiotrophic crust flora — the Scarlands'
  **only** native flora, §4, harvestable fuel+pigment) — the biome
  currently runs on an interim DONOR placeholder (`RUT_ScorchedStars`,
  ported from the retiring Polluted Lands mod via
  `POLLUTED_LANDS_FLORA_PORT_1`, closed) explicitly noted in the roster
  JSON as *"stands in for the Glowers until the new def lands... eye test
  owed: must read black/glass, never green (ban 3)."* The bespoke def
  itself has **no filed item**. — **UNFILED**, though not a total void
  (placeholder art exists and is tagged as needing a black/glass eye-test).
- **Mortuary guild carrion-specialist** — interim body assigned
  (`AA_Helixien`), tracked in roster JSON; **not independently filed** as
  its own build but not silent either.
- `STAGED_LORE_DESCRIPTIONS_1` (from the sheet's Owed) — sheet cites this
  name; ledger shows it **closed under `STAGED_LORE_DESCRIPTIONS_1`**
  (confirmed present in `closed/`) — consistent, not a gap. A second name,
  `STAGED_LORE_BUILD_1`, appears nowhere (neither live nor closed) —
  likely just an informal reference in the sheet's own owner-cards prose,
  not a separate filing; **UNCERTAIN**, low stakes.
- `ANCIENT_RUINS_MOD_AUDIT_1` — **FILED, DONE** (closed).
- Canon-sitting / river-tile flag / def-label check — **UNCERTAIN**,
  generic chain.

## the_slime.md / the_slime_gene_lists.md

6 Owed bullets on the_slime.md → ~9 sub-items; the_slime_gene_lists.md is
itself the accepted content for one of those bullets.

- `GELATINOUS_SLIME_MOD_1` (design) → `SLIME_MOD_BUILD_1` (build) — **both
  FILED, DONE** (closed), and **verified on disk**: `src/RimMandrake/
  GelatinousSlime/` exists with the biome def, `GeneSeeker.cs` (the
  scanner→extractor→injectable flow, exactly as the owner redesigned it),
  `SlimeRain.xml`, `SlimeWorks.xml` (the Slime Pit's likely home),
  `SlimeThoughts.xml`. The mechanic itself is real and built.
- 🔴 **The ratified gene lists are NOT wired in — the biome's headline
  feature currently serves the wrong content.** `the_slime_gene_lists.md`
  was owner-**ACCEPTED 2026-09-06** (33 target genes from named Star Wars
  races + 25 hidden rider genes, with the P1–P8 curation laws). But
  `src/RimMandrake/GelatinousSlime/Defs/GeneArchiveDefs/DefaultArchive.xml`
  — the only `GeneArchiveDef` that exists anywhere in `src/` — is
  explicitly the **generic universal-mod placeholder** (17 vanilla
  Biotech genes, e.g. `ToxResist_Total`, `MoveSpeed_VeryQuick`), and its
  own header comment says outright: *"the RUT layer swaps the campaign's
  frozen SW gene lists in by shipping its own `RM_GeneArchiveDef` with a
  HIGHER priority... Nothing in this mod's C# names a single gene."* **No
  such RUT_ archive def exists anywhere in `src/RimUtinni`** (confirmed:
  `grep -rl GeneArchiveDef src/RimUtinni` returns nothing), and
  `SlimeGenes.xml` (the campaign-tier gene file) contains exactly **one**
  `GeneDef` (`RM_Gene_SlimeResistance`, = list item A34) — none of A1–A33
  or B1–B25 exist as defs. — **UNFILED, CONFIRMED.** Searched: "RUT_
  Archive", "campaign gene archive", "gene archive priority", "frozen SW
  gene lists" (0 hits in `infrastructure/state/items/` or `closed/`).
  This is the closest analog in these 10 sheets to the Blue Desert
  failure: fully owner-ratified design content (a whole named gene
  economy) that has never become build work, sitting silently behind a
  generic placeholder that makes the feature *look* finished in-game.
- `EDIBLE_GENEPACK_NATIVE_1` — the sheet names this ID directly as
  covering the native genepack-consumption mechanic, and says its research
  is "half done" with a complete IL-cited spec on file
  (`edible_genepack_native_mechanism.md`, confirmed present). **The item
  itself does not exist** — neither `live` nor `closed`. — **UNFILED,
  CONFIRMED**, and it is a second, independent instance of the "sheet
  names an ID that was never actually filed" pattern the owner asked this
  audit to find.
- **Filter-feeder line** (scooping-mouth slime-grazer) — searched "NEW-ART
  ledger" and related terms; the two hits found (`ART_REGEN_WAVE5_QUEUE_1`,
  `SW_SEA_MONSTERS_ART_1`) are about unrelated sea-monster filter-feeders,
  not this creature. — **UNFILED**, low stakes (a flavor grazer, vanilla
  graze mechanic already covers behavior; only the art/def is missing).
- Helix wiring, roster reconciliation, def-tails check — **UNCERTAIN**,
  not independently verified this pass.

## Summary

~58 individual owed sub-items examined across the 10 sheets. Every
`*_MECHANICS_*` kit item is genuinely filed and, in most cases, honestly
self-tracks its own remaining creature/flora gaps rather than hiding them —
Fever Wood, Rust Cathedral and Greentide in particular name their own
unbuilt creatures inside the filed item's own text. The real gaps cluster
in two places: (1) content that was fully **ratified by the owner** and
never converted to a build item at all (the Slime's gene lists), and (2) a
handful of named creatures/flora that **never entered the roster
assignment pass's own `new_defs` list**, so nothing downstream ever had a
chance to pick them up (the Scald's bottom-walker; Miasma's karr-swarm,
delta-loam, rainbow flora; Scarlands' Glowers; Sump's wick-plant and
edge-chemotroph; Forge's fleet fliers).

### UNFILED, worst first

1. **The Slime** — the owner-ACCEPTED 2026-09-06 gene target/rider lists
   (33+25 named genes) are not wired into any campaign `GeneArchiveDef`;
   only a generic 17-gene universal placeholder ships. The gene machine is
   the Slime's headline "Uniquely available" feature and is currently
   serving the wrong content while looking complete in-game. — searched:
   "RUT_Archive", "campaign gene archive", "gene archive priority", "frozen
   SW gene lists". **CONFIRMED.**
2. **The Slime** — `EDIBLE_GENEPACK_NATIVE_1`, named directly by the sheet
   as covering the native genepack mechanic with a complete IL-cited spec
   already on file, does not exist as a ledger item at all (neither live
   nor closed). — searched: "EDIBLE_GENEPACK_NATIVE_1" (0 hits),
   "genepack native", "edible_genepack_native_mechanism". **CONFIRMED.**
3. **The Scald** — the bottom-walker herd (one of only 4 named residents;
   the anchor of the silver-shoal dung economy) has no def and never even
   entered the roster JSON's `new_defs` list — it surfaced only by
   accident, when an unrelated later item happened to check. No item owns
   building it. — searched: "bottom-walker", "bottom walker", "mat-mower",
   `the_scald.json` new_defs contents. **CONFIRMED.**
4. **The Miasma** — the karr- fever-swarm (disease vector *and* "the
   mangals' only pollinator... you cannot have the trees without the
   fever") has no def and no build item beyond a passing hediff mention.
   — searched: "fever-swarm", "karr-clade", "karr swarm". **CONFIRMED.**
5. **The Miasma** — delta-loam composter and the rainbow flora suite (3–4
   species, hard-banned from ever being harmful) — zero hits anywhere
   outside the sheet/roster JSON. — searched: "delta loam", "delta-loam",
   "composter", "rainbow flora", "rainbow bloom". **CONFIRMED.**
6. **The Scarlands** — "the Glowers," the biome's *only* native flora, is
   running on a donor placeholder with an explicit unresolved eye-test
   ("must read black/glass, never green") and no filed item to finish the
   bespoke def. — searched: "the Glowers", "radiotrophic", "glower fuel".
   **CONFIRMED** (placeholder exists; bespoke def unfiled).
7. **The Sump** — wick-plant (the signature "light as a crop" trade good)
   and the edge-chemotroph flora ring have no def and aren't even named
   inside `SUMP_MECHANICS_1`'s own text the way sump-mouse/tar-beast are.
   — searched: "wick-plant", "wick plant", "edge chemotroph". **CONFIRMED.**
8. **The Forge** — fleet fliers (small ambient flier) unbuilt, no tracking
   item; lowest stakes here — a flavor mob, biome fully playable without
   it. — searched: "fleet flier", "fleet fliers", "fireweed-eater".
   **CONFIRMED.**
9. **The Slime** — filter-feeder line (scooping-mouth grazer) art/def
   missing; low stakes, vanilla graze mechanic already covers behavior.
   — searched: "filter-feeder", "NEW-ART ledger" (2 hits, both unrelated
   sea-monster creatures). **CONFIRMED.**

### DONE-BUT-UNRECORDED / stale sheet text (not filing gaps)

- **The Scald's "two seas' enrichment"** Owed bullet is stale: it asks for
  a "next sitting" that already happened the same day
  (`the_grey_deep.md`/`the_twilight_deep.md`, both 2026-09-07). Design is
  done; implementation is deliberately deferred by standing owner ruling
  to the diving mods, not missing.
- **Rust Cathedral's cockroach candidate** — DONE, verified ACTIVE in the
  mod list, contrary to the "verify and grade" framing still in the
  sheet's Owed section.
- **The Scarlands' plated-grazer scaria onset** — DONE ("shipped, not just
  defined" per the item's own text).

### Stale filed-item citation

- **`the_scarlands.md`'s Owed section still names `SCARLANDS_MECHANICS_1`**,
  which no longer exists under that name (superseded 2026-09-14 by
  `SCARLANDS_MECHANICS_2`, which is live and covers the same scope). Same
  decay class CLAUDE.md already documents for `NAMING_SCHEME_EXECUTION_1`;
  the sheet is FROZEN so this note is a flag, not a fix.

All claims above are marked CONFIRMED where I read the actual def/item text
myself, or found a named zero-hit search; a few cross-flow/canon-sitting
bullets across every sheet are marked UNCERTAIN because I traced them only
to a generic superseded chain (`CANON_LORE_PROPAGATION_1` →
`CANON_DRAIN_1`) and did not verify each sheet's specific canon ask
line-by-line against it — that would be its own full pass.
