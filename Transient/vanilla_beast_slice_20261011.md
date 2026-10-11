# VANILLA_BEAST_EXCISION_1 — wave 3 slice: the caravan-carrier route (2026-10-11)

## The slice (stated before building)

Close the **caravan pack-carrier** route for vanilla beasts where it can be closed without breaking the
trader role, fully offline:

1. **Instrument** `src/RimMandrake/Utils/vanilla_beast_carriers.py` — the engine's own rule
   (`PawnGroupKindWorker_Trader`, RimSage 2026-10-11): a trader caravan to a home map draws its carrier
   from `faction trader-group carriers ∩ the map biome's allowedPackAnimals`, and if that intersection
   is empty `CanGenerateFrom` is false — **no caravan from that faction at all**. Matrix: every world
   trader faction (read from the canonical start save, not guessed) × every one of our BiomeDefs (dump).
   Sanity probes: OutlanderCivil carries Muffalo; RM_LanternDeeps allows Muffalo (pre-patch).
2. **Patch** (Utinni layer only) — add the owned pack beasts our biomes already allow to every trader
   group's carriers; remove Muffalo/Alpaca from RM_LanternDeeps' allowedPackAnimals (its own beetles
   then carry).
3. **Proof** — the instrument's `--simulate` applies the patch file to the dump in memory and asserts:
   no faction loses a biome it could trade into; no official carrier remains reachable in a patched
   biome. Selftest with fixtures.

## Results

Measured over `defs.sqlite` (full 638-mod list, captured 2026-10-04T17:39:06Z) × the 26 factions in
`CANONICAL_ASHKARR_START_2026-09-12.rws`. Both sanity probes OK.

- **10 world trader factions**; `RUT_Jawa_FreeDroidEnclaves`' trader group has **no `<carriers>` node**, so
  per the engine it never generates on a home tile — that faction sends no caravans at all (not a vanilla-beast
  issue; filed, see below).
- **56 of our 62 BiomeDefs have an EMPTY `allowedPackAnimals`** ⇒ by the engine rule no faction's trader caravan
  can generate on a home map in them. UNVERIFIED live (a Harmony patch from some mod could change it; none found
  in our src). Not this item's to fix — filed.
- Of the 6 with a list: `RM_LongShade`, `RM_Stillsand`, `RUT_Desert`, `RUT_ExtremeDesert` allow only OWNED
  beasts (RSW_ ports + RM_Vaalok) that **no faction carried** (factions carry the donor `Bantha`, not
  `RSW_Bantha`) ⇒ no caravans there either. `RM_LanternDeeps` (Muffalo, Alpaca + its beetles) and `RM_Pyrelands`
  (Muffalo, Dromedary, Elephant) are the only biomes where a caravan can arrive — and only there could an
  official carrier walk in.

**Built:**
- `src/RimMandrake/Utils/vanilla_beast_carriers.py` — the matrix + `--simulate PATCH`.
- `src/RimMandrake/Utils/selftest_vanilla_beast_carriers.py` — 19 checks, fixtures + shipped-patch shape. PASS.
- `src/RimUtinni/UtinniPatches/Patches/VanillaBeastExcision_Carriers.xml` — every trader group gains the 8 owned
  pack beasts our biomes already allow (derived, not chosen: RSW_Bantha/Ronto/Eopie/Jamel/Falumpaset,
  RM_Vaalok, RM_BovineBeetle, RM_ShatterjawBeetle, weight 2); RM_LanternDeeps drops Muffalo + Alpaca.
  `DeepDesertTribes.xml` and `HomesteadDefenseLeague.xml` carry the same 8 lines literally in the trader groups
  they patch-add, because patch files load in directory order; the generic op's `[not(RSW_Bantha)]` keeps it
  idempotent either way.

**Proof:** `--simulate` → 37 (faction, biome) pairs opened, **0 lost**, no official carrier left in
RM_LanternDeeps, exit 0. `validate_patch.py --live`: 0 errors, op 1 matches 30 trader-carrier nodes, each removal
matches exactly 1 (3 warnings: ops not wrapped in a Conditional — intended, a silent no-op is the worse failure).

## What remains

- `RM_Pyrelands` is the last biome where an official carrier (Muffalo/Dromedary/Elephant) can walk in: its
  allowed list has no owned pack beast. Cut lands at its biome sitting, when its own pack beast is named.
- The 56 empty-allowedPackAnimals biomes (`PACK_ANIMALS_RESTORE_EMPTY_SADDLES`) — when each gets a list it
  must name owned beasts only; re-run the instrument after.
- Live verify (owed, game-up): a trader caravan reaches a RM_LanternDeeps / RUT_Desert home map with an owned
  carrier; RM_BovineBeetle/ShatterjawBeetle reach LanternDeeps' allowed list by a route not found in src XML
  (dump-measured present) — re-run the instrument on each new full-list dump.
- Other routes, unchanged from wave 2: trader stock (49 official), farm wander-in (10), quest animal rewards
  (unmeasured), coastal/pollution rosters + Odyssey AnimalHabitat (unchecked), then the Cherry Picker waves.
