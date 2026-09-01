# Expected outcomes — next load, 2026-09-01 (FOUNDRY, owner AFK)

Riding this load: kotorweapons retirement re-verify (586 mods, config-only,
free) + first live proof of two already-deployed-but-unverified assemblies +
a freshly redeployed bridgetools companion.

1. **`mandrake.rsw.armoury` / Jawa_Patches after kotorweapons retirement**
   Expect: `[JawaBench] context: modSet 586/...`, zero NEW `PatchOperationConditional
   ... failed` lines beyond the pre-existing baseline (5 patchfail), crossref count
   25 -> up to 28 is ACCEPTED (the 3 known dangling apparelRequired entries), not RED.
   Wrong if: any `guy762_` PatchOperationConditional failure survives — means the
   WeaponTags_Renormalise.xml guard fix didn't take.

2. **`mandrake.rm.graffiti` (JobDriver_PaintGraffiti/JoyGiver_PaintGraffiti)**
   Expect: no `[Def Error]`/type-load error naming `RM_Graffiti` or
   `JobDriver_PaintGraffiti`; mod loads silently (no init line by design — not
   yet exercised by a live pawn this load, that's a follow-on, not this load's job).
   Wrong if: DEAD MOD or TYPE LOAD error naming this assembly.

3. **`mandrake.rm.ninefold` (GameComponent_Ninefold)**
   Expect: no DEAD MOD / TYPE LOAD error naming `Ninefold`; if a save loads,
   the GameComponent should attach with no Scribe exception. No save is being
   loaded this session (main-menu-only proof), so this only rules out a load-time
   crash, not full runtime proof.
   Wrong if: DEAD MOD or TYPE LOAD error naming this assembly.

4. **bridgetools `JawaBench.BridgeTools.dll` (redeployed, --gm, includes
   `jawa/harmony_patches`)**
   Expect: `[JawaBench] ready: N tools` on first tool call (lazy init — call one),
   `context: modSet 586/...`, build hash `e91f6b7c5763` or later (matches HEAD).
   Wrong if: ready line missing after a call, or tool count regresses without a
   removed tool being intentional.

All four are independently attributable (distinct log strings / distinct mod
names), so batching them is the owner's standing three-assembly waiver, not a
new judgment call.
