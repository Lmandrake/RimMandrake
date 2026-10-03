## spec
Owner, 2026-10-03 (typed, recorded on `LEANINGSCRUB_SWEETLINE_GUARDIAN_1`): any animal that produces items
like wool comes to the sweetline tree periodically to rub it off, an auto-shearing spot, whatever its material:
*"just a really wonderfully scratchy tree they like"*. Same sitting, PRIZE ruled "both": the free drop stays
generous and a harvested tree keeps shedding (the latter built at fd8b0b8d2). So this ADDS a visiting-animal
source; it does not remove the comp's shed timer unless the owner says so.

Hooks: `RM_CompSweetlineStation` (LeaningScrub `Source/RM_SweetlineStation.cs`) already Long-ticks and keeps
History. Vanilla shearing is `CompShearable` (fullness + `woolDef`); a visiting animal with fullness over a
threshold walks to the tree and its product drops beside the trunk, fullness reset. Bark-wardens never
target animals, so visits are safe.

## criteria
- A wild or tame animal with a `CompShearable` (any product) walks to a sweetline tree on its own and leaves its
  product beside the trunk, fullness reset; History records it.
- A Mod Setting toggles it (default on); off = no visits.
- Validation bar in `src/RimMandrake/LeaningScrub/validation.py`.
