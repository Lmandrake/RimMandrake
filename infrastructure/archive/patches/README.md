# Retired patches — kept for the record, not for loading

Nothing in this folder is deployed. `deploy_custom_mods.py` never looks here.

## `HuttEyes_Slitted.xml` · `WookieeHead_Upgrade.xml` — retired 2026-08-22

**Owner's ruling, 2026-08-22:** *"Move the dead patches to disposal… Don't feel the need
for the slit eyes, archive for now."*

Both patched **`btd.XenotypeRemix.StarWars`**, which is **not in `ModsConfig.xml` at all**.
Measured against `OFFICIAL-2026-08-21T22-44-59Z`: `BTD_Hutt`, `BTD_Wookiee` and
`OuterRim_WookieeHead` are all absent from the 578-mod capture. Both patches are wrapped in
`PatchOperationConditional`, so they were not erroring — **they were doing nothing, silently,
and had been for as long as that mod has been gone.**

🔑 **What actually happened:** the campaign migrated its species onto our own `RimMandrake*`
set and these two patches were never migrated with it. The successors are ours and exist —
`RimMandrakeWookiee` (XenotypeDef), `RimMandrake_WookieeHead` (GeneDef), `RimMandrake_Wookiee`
(HeadTypeDef), `RimMandrake_Head_hutt` and `RimMandrake_Tail_hutt` (GeneDefs). Note
`OuterRim_WookieeHead` → `RimMandrake_WookieeHead` is a straight rename, same word, new
namespace.

⚠️ **This was the third sighting of ONE half-finished `OuterRim_*` → `RimMandrake_*` rename
in a single day.** The first was `genideo.py`, which gated 94 grammar rules on
`OuterRim_Jawa` after its own output had already moved (`GENIDEO_REVERTS_DEAD_KINDS_1`,
fixed `3bb39e5`). ✅ The sweep for more is done and came back clean: `validate_patch.py
--defs --live` over all 62 files in `Jawa_Patches`, `RimMandrake_StarWarsRaces` and
`JawaVoice` found no other patch targeting an absent def.

**If the intent is ever wanted back**, do not re-point these files blind — check first
whether our own species defs already ship the look they were adding. Re-pointing a patch
that duplicates a def is worse than deleting it.
