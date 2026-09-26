# WARDEN_MOTHER_TRAINABLE_GATE_1 — hard-exclude Rescue/general Haul from a self-tamed warden young's training tab

Caused by `WARDEN_MOTHER_SUCCESSION_1`.

## what

`WARDEN_MOTHER_SUCCESSION_1` shipped self-taming and a water-scope BACKSTOP
for a self-tamed warden-mother young (`RM_HediffComp_SelfTameOnRecord` in
`src/RimMandrake/Miasma/Source/RM_WardenMotherSuccession.cs`): once tamed, the
comp interrupts (`EndCurrentJob`) any job it is executing the moment it is
found off water terrain. That correctly stops it from ever COMPLETING an
inland job.

Not built: the roster's own harder ask (miasma_fauna_roster_2026-09-23.md
§6a) — "explicitly NOT Rescue and NOT general Haul, both of which need land a
water-bound animal cannot reach... an animal that fails its own trained job
is a bug wearing a feature." That wants Rescue and general Haul removed from
the training tab ENTIRELY for this pawn, so the player is never offered a
trained behaviour that will only ever interrupt itself. The interrupt-backstop
above still lets the player TRAIN it for Rescue/Haul and watch it fail
repeatedly — the exact "bug wearing a feature" shape the roster rejects.

## why not built this pass

Excluding a specific `TrainableDef` from a specific pawn's training UI has no
plain per-pawn XML lever (`RaceProperties.trainability` is a coarse
None/Minimal/Advanced level, not a per-def allow-list) — it needs a Harmony
patch on whichever vanilla method the training tab and the trained-job
JobGivers call to decide "is td trainable for this pawn" (almost certainly a
`TrainableUtility` static method). This session could not verify that
method's exact name/signature: RimSage (the decompiler/def-detail MCP) is
Windows-Desktop-only and this session ran off it (CLAUDE.md). A wrong guess
at a Harmony patch target either fails to compile or silently patches nothing
— guessing it was rejected in favour of filing this instead. (Contrast: the
build DID recover from one earlier signature guess this same session —
`HediffComp.Notify_PawnDied(DamageInfo?)` doesn't exist; the real method is
`Notify_PawnPostApplyDamage(DamageInfo, float)`, found by loading the
installed game's `Assembly-CSharp.dll` via `System.Reflection` from
PowerShell and listing `HediffComp`'s virtual methods. The same technique
would resolve this item too, on a session that can reach that reflection
path or the Desktop's RimSage.)

## spec (draft)

1. On the Windows Desktop (or via the reflection technique above), identify
   the real method `TrainableUtility` (or wherever the training tab sources
   its per-pawn-per-def eligibility) calls to gate a `TrainableDef` for a
   `Pawn`.
2. A small Harmony postfix forcing that method to return false for
   `TrainableDefOf.Rescue`/`TrainableDefOf.Haul` (verify these two exact
   defNames exist — TrainableDefOf's known fields as of this session's
   reflection dump are Tameness/Obedience/Release/AttackTarget/Comfort/
   Forage/Dig/EggSpew/SludgeSpew; Rescue and Haul were NOT confirmed present
   and must be checked, since a mod or DLC may be what adds them) when the
   pawn carries a self-tamed `RM_HediffComp_SelfTameOnRecord`.
3. Ship it in `mandrake.rm.miasma`'s own assembly (matching the parent
   item's own choice to keep this whole mechanism dependency-free of
   `mandrake.rm.environmentalhazards`, several other seats' active files).

## Watch out

- Small blast radius by construction: the patch only needs to special-case
  pawns carrying this one hediff comp, so it should not need broad testing
  against unrelated animals — but any Harmony patch on a `TrainableUtility`-
  shaped method is still exactly the class of "could silently misfire for
  every animal in the game" risk this repo's own doctrine treats with
  extra caution (see `RM_CompWaterLocked.cs`'s own header on why THAT
  mechanism avoided a pathfinder-level patch for the same reason).
- Low priority: the shipped interrupt-backstop already prevents the failure
  mode that actually matters in play (the animal getting stuck on land or a
  hauled item stranding). This item only closes the UI-level "why does it
  even offer me a job it cannot do" polish gap.
