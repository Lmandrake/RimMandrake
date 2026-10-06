# ARMOURY_JUMPPACK_INVALID_IL_1 — findings 2026-10-06 (FOUNDRY helper, offline)

## State on arrival
The item was already fixed: `618463ba1` (2026-10-05, on origin/main) replaced the
transpiler with a Postfix. The item prose file is absent, so `rimflow show` warns it may
be stale. The committed DLL's `.srchash` matched all 52 source files and the DLL bytes
(measured), so the shipped DLL is the Postfix build. Earlier history: `12ad4c448`
(2026-09-03) tried to fix the transpiler's stack depth. The insertion point sat in the
middle of an expression at the `op_Implicit(Thing)` call. The `InvalidProgramException`
came back afterwards.

## Vanilla TryGiveJob shape (RimSage, decompiled 1.6, read 2026-10-06)
Return paths: null (several) · ability job · `OnlyUseAbilityVerbs` branch → Wait_Combat /
Goto · melee verb → `MeleeAttackJob` (AttackMelee) · ranged → Wait_Combat (has cover or
close range, and can hit) / null (no shooting position) / Wait_Combat (already at the
position) / Goto(dest).

## Postfix review
- Melee: replaces AttackMelee with CastJumpOnce when `GetJunpPackMelee` offers one.
  This matches the transpiler's intent.
- Ranged: replaces Goto/Wait_Combat. The transpiler injected before the cover/wait
  decision, so it also overrode every ranged outcome. The behaviour is the same except:
  (a) when vanilla returns null because there is no shooting position, no jump happens now;
  (b) the `OnlyUseAbilityVerbs` branch's Goto/Wait_Combat can now also be swapped.
  That case is rare, because it needs a non-colonist humanlike with a jump verb and only
  ability verbs. Left as is.
- Fixed one false comment in `GetJunpPackMelee`. It still said "the IL stays exactly as
  shipped" (transpiler era).

## Build
`winbuild.py src/RimStarWars/Armoury/Source/JawaArmoury.csproj`: succeeded, 0 warnings,
0 errors. The DLL and `.srchash` were rewritten. NOT committed (brief forbids it).

## Only a live run can confirm
- Player.log no longer shows InvalidProgramException / a Harmony error for
  JumppackForMeleeAI, and the patch is listed on `JobGiver_AIFightEnemy.TryGiveJob`.
- Raiders with jump packs actually jump, both melee-closing and ranged-flanking. The
  ranged timing is PROVISIONAL, as stated in the commit.
