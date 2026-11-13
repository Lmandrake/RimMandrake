## spec
The offline storage census that scene sc_closed_containers start[5] asserts has passed; it does not exist yet. A selftest over the owner's FULL def dump (via `measure`, never a scan) classing every storage building def as closed exactly when RM_KnockbackCompat.IsClosedContainer would: showContents false on a comp or mod extension, a Building_Crate while vanillaCratesClosed is on, or the RM_KnockbackClosedStorage tag.

Expected readings (owner 2026-11-12, OWNER:1794529787425697771, "Anything that draws its contents is open"): Shelf, ShelfSmall, Hopper open; the Cold Storage lockers and crock (RM_ColdStorageUnitBase, no showContents) open; LWM_WeaponsLocker closed; no def that draws its contents carries the tag. Must show it can fail (mutate: tag a drawing def, it goes red).
