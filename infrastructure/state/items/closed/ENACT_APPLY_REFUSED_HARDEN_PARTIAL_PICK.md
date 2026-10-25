# ENACT_APPLY_REFUSED_HARDEN_PARTIAL_PICK

Found in the enact_vet5 review of 8fa14fcec6 (FOUNDRY, 2026-10-24). Low severity: apply-time only.

## Defect
The plan now refuses a pick whole when one of its facings is refused: an owner-kept live file or a shared-file clash
(`held_back` in `build_plan`, shipped with this item's review). At APPLY, `L.install` can still raise `L.Refused` for one
facing while its siblings install, because each install is tried on its own. The result is a creature drawn from two
sets, which is the same picture the plan fix prevents.

Two more problems follow:
- A rebind group is rebound when ANY of its installs succeeds, so a def can point at a path with a missing facing.
- A folder's shed retires (no `replaced_by`) are gated on `ok_rows`, i.e. any install on the row. A ticked variant
  installing therefore sheds the folder even when the folder pick itself failed.

## Fix direction
Group the installs by (row, letter). Install a group into staging, or undo the group on the first Refused, so that a
pick lands whole or not at all. Rebind only when every install of the group landed. Gate the folder shed on the folder
pick's own (row, letter), as `replaced_by` retires now are (`ok_picks`).

## Failing-test sketch (selftest_enact.py apply fixture)
Use a two-facing pick. Monkeypatch `L.install` to raise `L.Refused` for the north facing only, then apply.
- Expect: east is not installed, or is rolled back, and the row is listed.
- Today: east lands, and north keeps the old picture.
