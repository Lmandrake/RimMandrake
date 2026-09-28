## what
Harvested from a full 629-mod load-test (2026-09-27/28, FOUNDRY, the session's
"deploy everything + game-up load test to catch bugs" bridge hold). Log shows
15 `Could not resolve cross-reference: No Verse.ThingDef named RM_<X> found to
give to RimWorld.BiomePlantRecord` errors, all naming plants owned by
`src/RimMandrake/FeverWood/Defs/ThingDefs_Plants/RM_FeverWoodFlora.xml`:
RM_Ammeth, RM_Cistrel, RM_Claithe, RM_Corvath, RM_Halquin, RM_Maulith,
RM_Nubrith, RM_Palefloss (BlueDesert-owned, separate cause — see
BLUEDESERT_MOD_DEPENDENCY_DECISION_1), RM_Plennith, RM_Seepril, RM_Skethral,
RM_Skimmel, RM_Sodderel, RM_Thulvane, RM_Varnoth, RM_Wanlith.

## ruled out this pass
- **Mod inactive**: `mandrake.rm.feverwood` IS active (confirmed against the
  live ModsConfig.xml).
- **Deploy drift**: `deploy_custom_mods.py --mod FeverWood` reports "in sync
  (101 files)" — the source and live Mods folder copy of
  `RM_FeverWoodFlora.xml` are byte-identical, and the def genuinely contains
  `<defName>RM_Ammeth</defName>` (grep-verified in both source and the
  deployed copy).
- **XML malformed**: `RM_FeverWoodFlora.xml` parses clean
  (`xml.etree.ElementTree`).
- **MayRequire/patch gate**: no `MayRequire` on this def or its containing
  `<ThingDef>` tag; the referencing side
  (`src/RimMandrake/FeverWood/Defs/BiomeDefs/RM_FeverWood.xml:245`,
  `<RM_Ammeth>0.35</RM_Ammeth>`) is a plain wildPlants shorthand entry in the
  SAME mod, no cross-mod patch involved.
- **A parallel, CONFIRMED-real cause for a similarly-shaped cluster**
  (RM_Suulk/RM_Vaulisk, `RimMandrake.TerminalBiomes`) turned out to be a
  stale deployed DLL missing a newer C# comp class, silently discarding the
  whole ThingDef. Checked whether the same applies here: FeverWood's plants
  carry **no `<comps>` Class attribute at all** (plain `PlantBase`
  ParentName, no C# touchpoint), so a DLL mismatch cannot explain this
  cluster the same way.

## still unexplained
Root cause UNMEASURED. The def is present, deployed, active, and
syntactically valid, yet the game's own post-load cross-reference resolver
says it doesn't exist. Candidates not yet checked: a duplicate `defName`
elsewhere in the active list silently winning; a load-order/version-folder
quirk specific to how `BiomePlantRecord`'s custom XML loader
(`<DefName>commonality</DefName>` shorthand, no `<li>`) times its lookup
relative to the standard deferred cross-reference pass; whether this is
specific to the FIRST post-reboot cold load (this session's) and would clear
on a second load of the same list, the way some load-order quirks do.

## next
Re-check against the CURRENT load (in progress as this item is filed,
`vanillaquestsexpanded.cryptoforge` removed, TerminalBiomes DLL redeployed).
If it reproduces identically, this is a real standing defect, not a one-off;
if it clears, the prior load's own state (mid-restart-recovery from a prior
session) was the actual cause and this item can close as unreproduced.
