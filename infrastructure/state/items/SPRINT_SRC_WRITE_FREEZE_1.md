# SPRINT_SRC_WRITE_FREEZE_1

## Spec
BENCH is executing MOD_CONSOLIDATION_SPRINT_1 (owner's word, 2026-09-08):
mod folders under src/ are MOVING and merging per
infrastructure/state/mod_consolidation_map.csv. Until this item closes:
- Finish DROIDWORKS_APPARELMONEY_MISSING_1 freely — Droidworks does not
  move on the map.
- Start NOTHING new that writes src/ — a build against half-renamed
  folders ships wrong (NAMING_SCHEME_PLAN §5 Phase-2 precedent).
- Repo-side only right now; redeploy + ModsConfig swap wait for the next
  real game-down window, so the LIVE game keeps loading the old copies
  and is unaffected.

## Verify
This item is closed by BENCH when the map's repo-side rows are done.

## Criteria
No FOUNDRY src/ commit (outside Droidworks apparelMoney) lands between
this filing and the close.
