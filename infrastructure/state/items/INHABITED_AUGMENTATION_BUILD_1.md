# INHABITED_AUGMENTATION_BUILD_1

No item file existed before this pass despite five days of ledger notes
against this ID — writing one now so the true state stops living only in
scattered `rimflow note` text.

## What this item actually is

The big build phase behind the owner's 2026-09-05 "inhabited and alive
tiles" directive: `design/Jawa/worldbuilding/tile_augmentation_matrix.md`
(313 ideas across 6 latitude bands × 12 factions × 8 biome families) and
`design/Jawa/worldbuilding/structure_procedural_spec.md` (14 archetypes to
build-level, §8.1–8.14) are the design, both Fable-drafted and BENCH-graded
2026-09-05. Scope: author rimplace `.lua` templates per archetype, wire each
to a responder (`TileMutatorDef` naming `Inhabited_Cast` + `RM_InhabitedStock`
or a `GenStepDef`), then **hand-place on Ash'karr tiles via the bridge**.

## State found at pickup (2026-09-09, this pass)

Five days of prior work exist under THIS id and under siblings, none of it
previously consolidated into a status doc:

- **This item's own pilot** (`ade756fc`, 2026-09-05): §8.1 (abode/homestead/
  compound → `homestead.lua`) and §8.3 (mining site → `mining_site.lua`),
  both live-verified by FOUNDRY. A real bug in `mining_site.lua`'s ore-yard
  scatter was found and fixed (`MINING_SITE_SCATTER_COLLISION_1`, closed
  `e94b70a9`).
- **§8.2 (moisture farm)** shipped as 5 templates under a *different*
  commit message with no item ID attached (`5b34a08c`, "Moisture farm
  templates: 5 rimplace plans for the Badlands") — `moisture_farm.lua`,
  `moisture_farm_ruined.lua`, `moisture_homestead.lua`,
  `moisture_vaporator_field.lua`, `moisture_walled_compound.lua`.
- **The six engine deltas (E1–E6)** the spec's own §2 says templates need
  before being "worth building" shipped under `RIMPLACE_ENGINE_DELTAS_1`
  (closed, `ab3a825e`): CLEAR, RUN, PAWN, the `ctx:hug`/`clutter`/`aisle_ok`
  prelude helpers, palette roles, and lint rules. `INHABITED_CONTENT_DEFS_1`
  (closed, `3c8d5d73`) shipped the two named NEW defs (`RUT_WindowAdobe`,
  `RSW_BeastNest_Large`).
- **A large, overlapping body of work rode under `TILE_STRUCTURE_DESIGNS_1`**
  (a sibling item, the 22-promise/22-whisper roster) and
  `DISTRICT_TEMPLATE_LIBRARY_1` — 30+ more templates (Junkers, Hutt,
  Deepwater, Free Droid, Deep Desert rows) sharing the exact same engine
  and the exact same owner room-realism ruling this item's spec encodes.
  `TILE_STRUCTURE_DESIGNS_1`'s own 2026-09-09 note explicitly credits row
  22 (The Homestead) to *this* item and flags the cross-item bookkeeping
  gap — worth reading before anyone re-does that reconciliation.
- **Net: of the 14 archetypes in `structure_procedural_spec.md` §8, three
  were built before this pass** (8.1 abode/homestead/compound, 8.2 moisture
  farm, 8.3 mining site) — the rest (8.4 trading outpost, 8.5 warehouse,
  8.6 tiny garrison, 8.7 oil refinery, 8.8 gas-geyser power station, 8.9
  crashed ship, 8.10 broken wagon, 8.11 beast lair, 8.12 battle-site ruin
  transform, 8.13 breeding facility, 8.14 storage cache) were unbuilt.
- **Zero rows of either kind have live placement on Ash'karr.** Every
  batch note across both items says so explicitly; `mandrake.rut.injections`
  is deployed but not enabled in the live `ModsConfig.xml`.

## This pass (2026-09-09/10, FOUNDRY, BELT/offline — game confirmed DOWN)

Briefed to continue the item; the game crashed twice tonight and a bridge
call is out of scope for this pass by the dispatch's own instruction, so
nothing here touches Ash'karr placement — that step stays exactly as
un-met as it was.

**Built §8.14, storage cache** (`design/Jawa/templates/cache.lua`) — the
spec's own "smallest template in the roster." Three forms (`buried`,
`dugout`, `cairn`) per the spec, rolled by `rng.pick` or pinned via
`params.form`, plus the spec's "Debtor's Cache" addition
(`params.debtor` or a 25% unforced roll) layered on top of any form.

- **defNames verified against RimSage, not guessed**, because tonight's
  def-dump capture (`2026-09-10T00-28-43Z`) is unreadable — almost
  certainly the same crash that took the game down, so `rimplace verify`'s
  usual live-dump cross-check could not run. `AncientHermeticCrate`,
  `AncientSealedCrate`, `ChunkSandstone`, `SculptureSmall`, `Skull`,
  `TorchLamp`, `Filth_Sand`, `Filth_Dirt`, `Filth_ScatteredDocuments`,
  `FlagstoneSandstone` all confirmed real via `search_defs`. Three of the
  spec's named defs do not exist in this stack's index at all
  (`LWM_Safe`, `VFEPD_WoodenChest`/`_Large`, `ASF_StoragePit`/
  `ASF_CellarStone`, `CanisterA`, `QE_TreasureChest`) — substituted with
  verified real equivalents (`AncientSafe`, `AncientWoodenCrate`,
  `AncientChemfuelCanister` not used / omitted rather than guessed) and
  said so in the template's own header, same pattern boneyard.lua's
  SILVERBOLE_STANDIN note set.
- **Two real generator bugs found and fixed by this pass's own lint sweep,
  not shipped on the first draft's word:**
  1. The dugout form's room was floored/roofed but never walled
     (`ctx:room()` does not call `wall_rect()` — that is a separate call
     every other template makes explicitly, `dead_beacon.lua` included,
     and this draft missed it) — `room-not-sealed` ERROR on every seed.
     Fixed by adding the missing `ctx:wall_rect()` call.
  2. The Debtor's Cache addition picked one fixed direction/distance for
     its second crate and refused outright whenever that one cell was
     occupied — over half of 30 test seeds on a dense cairn roll, at BOTH
     the 5×5 min canvas and the 7×7 production one. Fixed with a search
     over all 4 sides × 2 distances (shuffled by the seeded rng) before
     giving up.
- **Verify, offline only (matches this pass's own constraint — game down,
  no bridge):**
  - `rimplace lint cache` clean (0 findings) across all 3 forms × the 5×5
    min canvas, the 7×7 production canvas, and a 9×9 canvas × seeds 0–39
    (360 combinations) with the debtor addition forced on every run —
    **one WARN remains**, `cairn` seed 1 at the absolute 5×5 floor: a
    dense 5–7 chunk roll genuinely leaves no cell within reach for the
    optional debtor crate. A WARN (`generator-refusal`), not an ERROR, and
    the base cairn still builds complete — the same accepted-tradeoff
    shape other templates' own min-canvas edge cases carry.
  - `rimplace selftest`: 62/62 (engine unchanged by this pass).
  - `rimplace export` round-trips a flat plan (spot-checked, not committed
    — see below).
  - `rimplace verify` (defName-vs-live-dump cross-check): **UNMEASURED**,
    correctly — the tool itself refuses on the unreadable capture rather
    than reporting a false pass, exactly the behavior the
    measuring-large-artifacts skill asks for.
- **Not wired to any responder, deliberately, matching precedent.**
  Roster whispers #8 ("The Debtor's Cache") and #1 ("Something Buried")
  are what cite this shape, and `TILE_STRUCTURE_DESIGNS_1`'s own
  2026-09-09 note already established that **the whisper subsystem does
  not exist at all** (no territory table, no weighted-selector GenStep,
  no landing-letter hook) — building that engine is a separate, much
  larger undertaking than one template and is not this pass's to invent.
  Checked: five other design/Jawa/templates/*.lua files
  (`boneyard`, `waste_camp`, `long_crossing`, plus the `dwelling`/`nursery`
  bases other templates extend) are in the identical unwired state, so
  `cache.lua` is not a new gap, just one more template waiting on the same
  missing engine piece. Not exported to any mod's `Templates/` folder for
  the same reason — nothing would read it yet.

## What remains — stated plainly, not invented

1. **10 of 14 spec archetypes still unbuilt**: 8.4 trading outpost, 8.5
   road warehouse, 8.6 tiny garrison, 8.7 oil refinery, 8.8 gas-geyser
   power station, 8.9 crashed ship, 8.10 broken wagon/dead caravan, 8.11
   giant-beast lair, 8.12 battle-site ruin transform (engine-only — `ctx:ruin`
   already exists per E4, this is authoring the archetype-agnostic
   `battle_site.lua` driver), 8.13 breeding facility. Each is already
   specced to build-level in `structure_procedural_spec.md` §8 — this is
   volume, not a design gap, and each one is a multi-hour pass on the
   scale of tonight's single smallest-archetype build.
2. **8.7 and 8.8 carry named prerequisites** (`required_mods.md:517` and
   `:489`, buildability strips) that are NOT this item's to execute blind.
3. **Per-faction palette materials remain an owner ruling**, per the
   spec's own §9 — every faction stuff in `palette.json` is still invented
   placeholder, unticketed here.
4. **Zero live placement on Ash'karr, for any archetype this item has ever
   shipped**, including tonight's — this needs the bridge and a human (or
   BENCH) decision on WHICH tiles get WHICH archetype, which is exactly
   the kind of creative/world-authoring call this dispatch said not to
   invent solo.
5. **The cross-item bookkeeping gap `TILE_STRUCTURE_DESIGNS_1` flagged**
   (this item's built rows not visible in that item's own coverage lint,
   and vice versa) is still open — a future pass should reconcile the two
   items' rosters rather than let both keep growing independently blind
   to each other.

## criteria (this item's own bar, restated since none existed before)

1. Every archetype in `structure_procedural_spec.md` §8 exists as an
   offline-verified rimplace template. **3/14 before this pass, 4/14 now.**
2. Each is wired to a live responder once the promise/whisper vocabulary
   it needs exists. **Blocked on the whisper subsystem for whisper-shaped
   archetypes (this pass's cache included); the promise-shaped ones (most
   of the remaining 9) are not blocked on that, only on being built.**
3. Hand-placed on Ash'karr tiles via the bridge. **NOT MET for anything
   this item has ever shipped** — needs the bridge (down tonight) and a
   placement decision (not this pass's to invent).

Staying `doing`. This is real, bounded progress (one more archetype,
offline-verified, two real bugs caught before shipping) on a genuinely
large multi-week item — not a stall, and not a false close.
