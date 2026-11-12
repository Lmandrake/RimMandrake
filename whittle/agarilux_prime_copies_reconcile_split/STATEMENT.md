# AGARILUX_PRIME_COPIES_RECONCILE_SPLIT — done statement

Item text (infrastructure/state/items/AGARILUX_PRIME_COPIES_RECONCILE_SPLIT.md): "RM_AgariluxPrime ships as two
DIFFERENT texture copies, TheRot and UtinniPatches (one shadows the other at load). Judged separately in gptredo_03:
TheRot copy ACCEPT, UtinniPatches copy REGEN. ... Decide which mod owns the def/texture, delete the other copy (fix
every inbound reference), then re-judge only if the surviving copy is the REGEN one."

- **One owner is decided and recorded.** Which mod owns RM_AgariluxPrime's def and texture is stated on the item with
  the reason, drawn from what the game actually loads (the def's texPath after patches, load order). Evidence: a
  resolved-texPath read of the def chain (base def + TheRot `RotSpecies_NamesAndSizes.xml` repoint) written to
  `evidence/`.
- **Exactly one copy of the texture ships.** The losing copy is deleted from `src/`; nothing in `src/`, the art ledger
  or art-eval state still points at it, or a remaining reference is shown to serve a different def. Evidence: a
  repo-wide search for the deleted path/stem after the change, in `evidence/`.
- **Every inbound reference is fixed.** Defs, patches, art ledger/artpipe rows, deploy manifests and any doc naming the
  deleted copy are updated in the same change. Evidence: the same search, plus the relevant offline validator /
  selftest passing (validate_patch.py or the art-ledger check that covers the touched files).
- **The surviving copy's judgement stands, or it is re-judged.** If the survivor is the TheRot (ACCEPT) copy, no re-judge
  is owed and that is stated with the gptredo_03 decision row; if it is the UtinniPatches (REGEN) copy, a regen/re-judge
  is filed or run. Evidence: the gptredo_03 decisions.jsonl rows for both subjects.
