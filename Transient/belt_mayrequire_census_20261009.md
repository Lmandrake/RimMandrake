# MayRequire packageId census 2026-10-09 (belt, FOUNDRY helper)

Instrument: `/home/mandrake/.seat-tmp/mr/census.py` over src/ (XML attr `MayRequire`/`MayRequireAnyOf`, `<mods>` FindMod lists, About.xml loadAfter/dependencies) against own-packageId of every About.xml under src/ (181), About.xml under both game roots (1307 ids), and Biomes.compose.json (30 entries, compose_wave 2 -> all 30 folded).

Probe (printed by the run): known-good `mandrake.rm.biomes`/`ludeon.rimworld.odyssey` resolve; known-dead `mandrake.rm.longshade` is present as a standalone About id in src (so a bare "exists in src" test is WRONG - it must be tested against the compose list). Composed-member set found: 30 ids.

## Counts by class (distinct ids / attribute sites incl. About lists)
| class | ids | sites | verdict |
|---|---|---|---|
| (a) standalone mod of ours / game core+DLC | 36 | 638 | live |
| (b) external mod installed in the game dirs | 149 | 2445 | live |
| (c1) composed member of mandrake.rm.biomes used as a gate | 9 | 62 | 53 of 62 sites are `loadAfter`/dependency lists inside the folded member's own About.xml (never read: composed About comes from compose.json) ; 3 live MayRequire/AnyOf sites OK (see below) |
| (c2) mandrake.* matching nothing | 1 (`mandrake.rut.rotsporekit`) | 6 | 1 live gate fixed; rest are About lists / comments |
| (c3) non-mandrake id not installed on this machine | 50 | 622 | intentional optional external gates (sarg.*, vanillaexpanded.*, kentington.saveourship2, guy762.lee.kotorpotf ...) - left alone |

(`ludeon.rimworld` lands in c3 only because Core's About is not under Mods/; it is the base game.)

## Live dead gates found
* `RUT_ContagionRingScatter.xml` `<filthDef MayRequire="mandrake.rut.rotsporekit">` : packageId provided by nothing, so the genstep never ran. `RUT_DeadCreep` is defined in the same mod (UtinniPatches). FIXED: gate removed (same-mod def, no gate needed).
* `RM_DuneGale.xml` (2 sites) `MayRequireAnyOf="mandrake.rm.movingdunes,mandrake.rm.biomes"`: second id is the host, loads composed. OK, deliberate dual id.
* LongShade/About.xml and Contagion/About.xml name `mandrake.rm.stillsand` / `mandrake.rm.therot` in a MayRequire: inside folded-member About.xml, not loaded in the player-facing mod. Left (harmless, standalone-only metadata).
* After sitting 2's repoint there is NO remaining live XML gate on a folded-member packageId in defs or patches.

## Whole-<Operation> MayRequire (PATCH_MAYREQUIRE_GUARD_INERT_1)
* Live top-level `<Operation ... MayRequire=...>` in src/ (comment-stripped): **0**. The two raw regex hits (`WreckVerminNest_ShipChunk.xml`, `RSW_SekkulaathTank_DianogaSwap.xml`) are inside comments recording earlier removals. Sanity: the raw non-stripped scan found exactly those 2, the stripped scan 0, and total live MayRequire attrs = 2568 so the scan sees attributes. The 74 figure in the item does not reproduce on this tree.
* 14 `MayRequire` on nested `<li Class="PatchOperation...">` (12 in FishTypesStrip_NoFishBiomes.xml, 1 AncientsAreRakata, 1 FlameStatuary_HolyAct): ids are Odyssey / mandrake.rm.biomes, all present; li-level MayRequire is the honoured form. None pulls an absent mod's def.
* FindMod `<mods>` lists use mod NAMES (core, odyssey, anomaly, ...) or ids; `mandrake.rsw.swbestiary`, `sarg.alphaanimals`, `oskarpotocki.vfe.insectoid2` resolved; not changed.

## Not done
validate_patch.py --defs/--live: UNMEASURED here (no deployed load set in a private clone; it refuses). The only touched file is a GenStepDef, XML well-formedness checked.
