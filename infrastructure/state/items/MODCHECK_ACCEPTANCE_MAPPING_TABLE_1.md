# MODCHECK_ACCEPTANCE_MAPPING_TABLE_1 - Modcheck acceptance mapping table

Filed 2026-10-07 from the GREEN-MIN / L2 sweeps (Transient/*_20261007.md).

## spec
Per-mod acceptance mapping: chain component text rarely matches acceptance-criterion wording, so L2/GREEN-MIN `rimflow verify --criterion` calls are made by hand-matching prose, slowly and inconsistently. Propose and build a mapping table (criterion id -> modcheck component names), data not prose. Recommended home: a `## covers` block per item or a single `infrastructure/state/acceptance_map/<Mod>.json` consumed by `modcheck`, so `modcheck verify-from-run <Mod> <results.json>` can propose the verify calls. Decide the location, record it in the item, then implement for 2 mods as proof (PyrelandsMechanics, Greentide).

## verify
Selftest: given a results JSON and the map, the tool lists criteria it can mark GREEN-MIN and criteria it cannot (unmapped).

## criteria
A1: location decided and written in the item and in src/RimMandrake/Utils docs.
A2: tool reproduces the 2026-10-07 hand-recorded criterion set for PyrelandsMechanics A2/A3 and Greentide A3 from the run JSONs.
A3: unmapped criteria are listed, never silently passed.

NEXT: claim this item and start with criterion A1.
