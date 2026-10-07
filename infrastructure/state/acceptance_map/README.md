# acceptance_map -- which modcheck component proves which acceptance criterion

Owner decision (card 2026-10-07): the mapping is ONE TABLE PER MOD, data not prose. A table is
`<Mod>.json`, `<Mod>` being the mod's repo folder name (the name `modcheck run` takes). Tool:
`python3 src/RimMandrake/Utils/acceptance_map.py {check|list|apply}`; selftest
`src/RimMandrake/Utils/selftest_acceptance_map.py`. Item: `MODCHECK_ACCEPTANCE_MAPPING_TABLE_1`.

## Row schema

A table is a JSON list of rows. Every key but `accept` is required; unknown keys are refused.

| key | meaning |
|---|---|
| `item` | ledger item id (any state; closed items are fine) |
| `criterion` | the item's criterion id, e.g. `A3` (must exist in the ledger's criteria manifest) |
| `level` | must equal the ledger's level for that criterion: L0 L1 L2 GREEN-MIN GREEN-FULL L3 L4 |
| `components` | ids that must pass, `chain/component` exactly as `Transient/modcheck/*.json` and `l2sweep_*.json` name them; plus the pseudo-ids below |
| `mode` | `all` (every component), `any` (one suffices), `classified`, or `unmapped` |
| `notes` | why this mapping is right, or why it cannot be mapped. Required, never empty |
| `accept` | optional, `["PASS","UNMEASURED"]`: only when the criterion's own wording accepts "recorded as unmeasured". FAIL is never acceptable |

Pseudo-components: `@run` -- the result file parsed and holds at least one component (the
"one live run produced a results JSON" criteria). `*` -- every component of the run (`classified` only).

## Modes and verdicts

- `all`: any FAIL -> FAIL; else any component missing from the run (or UNMEASURED, unless
  accepted) -> UNMEASURED; else PASS.
- `any`: one accepted component -> PASS; else UNMEASURED if anything is unknown; else FAIL.
- `classified`: for "every non-pass is classified" wording. PASS only if the run has no non-pass
  component, or a `--classified file.json` (`{"chain/component": "harness|site|mod|unmeasured: why"}`,
  written by a person after reading the failures) classifies every one. Without the file: UNMEASURED.
- `unmapped`: no component honestly proves the criterion. Listed on every `apply`, never passed.
  **When in doubt, `unmapped` -- a wrong mapping records a false pass.**

## Rules

- `apply --record` calls `rimflow verify` only for a PASS on a criterion the ledger lists as
  outstanding at the table's level. FAIL, UNMEASURED, UNMAPPED, already-passed: never recorded.
- Outstanding criteria on a mapped item that have no row print as `NOT-IN-TABLE`.
- Component ids rot when `validation.py` changes: run `check` after editing either side.
- A row that over-claims (criterion says more than the component shows) is a defect; split the
  criterion or mark it `unmapped` and say what is missing in `notes`.
