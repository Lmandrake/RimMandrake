# Review batch 6 — 2026-10-06 (FOUNDRY helper, offline)

Engine facts checked with RimSage against the decompiled 1.6 source (Thing.TakeDamage, Listing,
DesignationCategoryDef, BiomeDef).

## RM_VexxithAcidImmunity.cs — CLEAN (marked at 5dc8af767)
- Thing.TakeDamage(DamageInfo) is the only overload and is non-virtual, so the patch target resolves
  and covers pawns, apparel and buildings alike.
- A prefix that returns false with an empty DamageResult matches what vanilla returns itself for
  Destroyed and zero-amount hits. That skips PostApplyDamage, filth and ignition, which is what was intended.
- Cost: on the hot path it is a static bool, then `def.modExtensions != null`. Nearly every DamageDef
  has null extensions, so it exits after two field reads.
- Null thing, def and stuff are all handled. Armour gets acid-proofing because ArmorUtility calls
  TakeDamage on the apparel itself.
- Door gate: designators are resolved inside an ExecuteWhenFinished queued at ResolveReferences, which
  runs before the static constructors, so RemoveAll does the work and nulling the category is the
  backstop. DoorBase has no designatorDropdown, so the designator is never hidden inside a dropdown.

## RM_CauldronMod.cs — CLEAN (marked at 5dc8af767)
- Both new fields are scribed with matching keys and defaults. The scroll view uses
  Mathf.Max(lastContentHeight, inRect.height) together with maxOneColumn, which is correct.

## RM_WarscarMod.cs — FIXED (uncommitted, rebuilt)
- Scribe keys, the rows removed from the startup roster, and the five RM_ defNames all match the
  inline <wildAnimals> rows in Defs/BiomeDefs/RM_Warscar.xml. No donor row is left to gate, and the
  stale enableInterimDonors key does no harm.
- BUG: the settings Listing had no maxOneColumn, and the view height started at a fixed 2400. The
  content is about 36 checkboxes, 37 labels, 32 sliders and 13 gap lines, roughly 2,500–2,700 px
  (estimated, not measured). It overflows the 2400 px rect, so Listing.NewColumnIfNeeded wraps the
  tail into an off-screen second column. CurHeight then reports only that column's height, so
  viewHeight shrinks on the next frame and the species section, including the five new switches,
  can no longer be reached.
  Fix: `maxOneColumn = true` and `Mathf.Max(viewHeight, inRect.height)`, the same pattern as Cauldron.
  Rebuilt with winbuild.py Scarlands (0 errors). Re-reviewed with nothing else found. Not marked clean,
  because the file was edited and the edit is uncommitted.

## Other small C# in 8259254c9..HEAD
- None. Only the three files above changed in that range.
