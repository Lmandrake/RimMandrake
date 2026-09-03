## Spec
`design/Jawa/droid_system_build_spec.md` §2, state 3 ("Downed/off"): "buildup
≥ threshold or manual shutdown → `DW_PoweredDown` hediff: Consciousness
`setMax 0.10`, no decay (floor stage) — stays an object until externally
rebooted... Capturable here." `DW_PoweredDown` (hediff) and
`Recipe_RebootDroid`/`HediffComp_PoweredDown` (C#) exist
(`DROIDWORKS_PHASE0_XML_1`, `DROIDWORKS_DLL_COMPILE_1`, both closed), but
nothing currently ADDS `DW_PoweredDown` to a pawn when ion buildup crosses
the threshold.

## Live confirmation (quicktest, 2026-08-30, DW_OuterRim_GNKDroid pilot)
Hit a pilot chassis pawn with `JawaIon_Damage` x20 via `jawa/damage`.
`jawa/pawn_get` afterward: `hediffs: [{'def': 'JawaIon_Stun', 'severity':
1.0}]` — no `DW_PoweredDown`. `jawa/list_pawns` on the same pawn: `downed:
True`. The pawn IS mechanically downed and capturable, but purely through
`JawaIon_Stun`'s own vanilla `HediffStage.capMods` (`Consciousness setMax
0.10` at its "overloaded" stage, `minSeverity 0.9`) — the same mechanism a
flesh pawn uses. `DW_PoweredDown`'s own no-decay floor and "stays an object"
semantics never engage; when `JawaIon_Stun` decays back below 0.5
(`severityPerDay -0.3`), the droid gets back up on its own like any stunned
human would, rather than staying powered-down until externally rebooted.

## Why this matters
State 3 is supposed to be a DISTINCT droid-specific status (object,
externally-rebooted-only, `Recipe_RebootDroid`'s target). Right now a downed
droid behaves exactly like a downed human — it recovers on its own once the
ion hediff decays, `Recipe_RebootDroid` has nothing to target
(`GetPartsToApplyOn` gates on `HasHediff(DW_PoweredDown)`, which never
becomes true this way), and the "capturable here" claim rests on ordinary
vanilla stun-capture, not the intended state machine.

## Verify
1. Add the missing wiring: either a `HediffComp` on `JawaIon_Stun` (droid-only
   branch) or a Harmony postfix on `HediffWithComps.PostAdd`/`Notify_HediffChanged`
   analogous to `DamageWorker_IonBuildup`'s own pattern, that adds
   `DW_PoweredDown` when `JawaIon_Stun.Severity` crosses ~0.9 on a
   `DW_FleshType_Droid` pawn (depends on `DROIDWORKS_FLESHTYPE_NEEDS_GAP_1`
   landing first, so the guard has something real to key on).
2. Quicktest re-check: ion-down a pilot chassis, `jawa/pawn_get`, expect
   `DW_PoweredDown` present. Wait/step ticks past `JawaIon_Stun`'s decay
   floor and confirm the pawn stays down (does NOT self-recover) until
   `DW_RebootDroid` runs.

## criteria
- [ ] Crossing the ion threshold adds `DW_PoweredDown`, live-verified.
- [ ] A powered-down droid does not self-recover once `JawaIon_Stun` decays
      away — only `Recipe_RebootDroid` clears it.
- [ ] `Recipe_RebootDroid`'s `GetPartsToApplyOn` gate actually fires on a
      real powered-down pawn (currently untestable — nothing ever sets the
      hediff it gates on).

## Depends on
`DROIDWORKS_FLESHTYPE_NEEDS_GAP_1` — the guard for "is this pawn a droid"
should key on `DW_FleshType_Droid`, not `IsMechanoid` (wrong bucket) or
kindDef-name matching (fragile). Land that first. **Closed 2026-08-30.**

## Status, 2026-08-30 (FOUNDRY)
The wiring itself already landed: `HediffComp_IonOverloadsDroid.cs` +
`Patches/IonBuildup_PowersDownDroid.xml`, commit `6f4c3c77`. `deploy_custom_mods.py
--mod Droidworks` confirms the game copy is in sync (476 files) — but **Droidworks
is not enabled in the current 585-mod ModsConfig**, so this session's live game
cannot exercise it. Today's earlier "Live confirmation" note above was taken on a
Droidworks-specific quicktest tier, not this load. The three `## criteria` checks
need a dedicated Droidworks-tier quicktest load to verify (spawn a pilot chassis,
ion-damage past 0.9, confirm `DW_PoweredDown` lands and does not self-clear, confirm
`Recipe_RebootDroid` now has something to target) — not done this pass, still open.

## 2026-09-02 (FOUNDRY) — actual root cause found, three real bugs fixed

Opus code review (`feature-dev:code-reviewer`) of the whole ion/power-down
state machine, verified against decompiled 1.6 source and the live deployed
copy rather than trusted on prose. Found the mechanism was broken in THREE
independent, compounding ways — this is very likely why the wiring "landed"
but never actually worked when exercised:

1. **The real root cause**: `NeedDefs_Droidworks.xml`'s `RSW_DW_Power`
   `needClass` was the bare `Droidworks.Need_Power` — `GenTypes.
   GetTypeInAnyAssembly` does exact matching only, never a namespace-suffix
   match, against the real class `RimMandrake.StarWars.Droidworks.
   Need_Power`. Resolved to null, every droid silently failed `AddNeed`
   (caught and logged, not a crash), and NO droid ever had this need. That
   killed the power-exhaustion route into `RSW_DW_PoweredDown` entirely,
   both charger comps (`TryGetNeed<Need_Power>()` always null), and
   `Recipe_RebootDroid`'s charge restore. One straggler from the C#
   namespace migration that fixed everything else in this mod. **Fixed.**
2. `HediffComp_IonOverloadsDroid`'s conversion threshold (0.9, the ion
   hediff's TOP stage) sat above the actual Downed point (0.5, the
   `DROIDWORKS_ION_GUARD_1` floor stage added 2026-08-30 specifically so
   decay from 0.9 wouldn't un-down the pawn). Left a window where the
   droid is Downed at 0.5, combat naturally stops (AI won't keep hitting a
   Downed target), and buildup plateaus/decays back out before ever
   reaching 0.9 — self-recovering exactly like the reported bug. **Fixed**
   (threshold now 0.5, matching the actual Downed stage).
3. The guard was `pawn.def.GetModExtension<DroidworksExtension>() != null`
   — present only on `DW_Family_*` descendants — instead of this item's
   own "Depends on" note's instruction to key on `DW_FleshType_Droid`.
   Every non-Droidworks droid race silently failed the gate. **Fixed**
   (now keys on `pawn.RaceProps.FleshType == DroidworksDefOf.
   RSW_DW_FleshType_Droid`, added to `DroidworksDefOf`).

Also fixed in the same pass: `RemoveHediff(parent)` ran BEFORE
`AddHediff(RSW_DW_PoweredDown)`, leaving the droid with no
Consciousness-capping hediff for one instant — `CheckForStateChange` fires
a "no longer downed" message and can abort an in-flight rescue/capture job
on that exact pawn mid-conversion. Reordered: add first, then remove.

All fixes compile clean (`Droidworks.csproj`, 0/0). **Still open**: a
fourth finding, more architectural — `DamageWorker_IonBuildup.
ApplyMachineTier` re-applies vanilla EMP (a SEPARATE, self-clearing
`StunHandler` stun) to every non-mechanoid non-flesh pawn, including
droids, alongside the buildup hediff this comp watches. That dual-path
behavior is itself deliberate and well-documented (2026-08-12/22/29
comments in that file) — NOT touched here, since overriding it needs to
be a live-tested decision, not a code-review-prose one. Flag for whoever
runs the next Droidworks quicktest: does the vanilla EMP stun (not
`RSW_JawaIon_Stun`) end and let the droid appear to "get back up" before
the buildup-based conversion ever gets a chance? If so, that's a second,
independent contributor to the original symptom beyond findings 1-3.

Not fixed, filed separately as `DROIDWORKS_CHARGER_STATE_MACHINE_SWEEP_1`:
chargers ignoring building power/switch state, chargers charging hostile/
prisoner droids, `Recipe_RebootDroid` skipping `base.ApplyOnPawn`, and a
per-tick O(hediffs) scan in `HediffComp_DWBoltResentment`.

Deploy still owed — `Droidworks` mod is not in the live 587-mod ModsConfig
this session; these fixes need a Droidworks-tier quicktest load to
live-verify, matching the criteria below.

## 🔴 2026-09-02 (FOUNDRY, re-review pass) — the needClass fix above UNMASKED A GAME-ENDING BUG, now fixed

A fresh full-file re-review (not a diff review — CLAUDE.md's "code isn't
clean until a review says so") of the same file set found that fixing
`RSW_DW_Power`'s `needClass` (the finding-1 fix above) exposed a second,
independent, far worse defect that had been dormant only because the need
never worked before: **`RSW_DW_Power` has no gating field at all** — no
`minIntelligence`, `hediffRequiredAny`, `colonistsOnly`, `requiredComps`.
Verified against `Pawn_NeedsTracker.ShouldHaveNeed` (RimSage): every gate
defaults to a pass, so the method falls through to `return true;` for
**every pawn in the game** — human, animal, mechanoid alike. Since only
Droidworks race ThingDefs carry `Recipe_RebootDroid`, every other pawn
would drain to 0 in ~1.5 in-game days and be **permanently, irrecoverably
downed with no way to remove it**. Enabling this mod with the needClass
fix alone, before this second fix, would have ended any game inside two
days — including the owner's live campaign, if this mod were ever
switched on without the follow-up.

**Fixed**: added a Harmony dependency to `Droidworks.csproj` (this
project's first) and `Patch_ShouldHaveNeed_Power.cs` — a postfix on the
private `Pawn_NeedsTracker.ShouldHaveNeed` narrowing `RSW_DW_Power`
specifically to `FleshType == RSW_DW_FleshType_Droid`. The NeedDef itself
still has no native XML gate; the C# patch is the actual gate now.

**Also fixed in the same pass** (finding 2 from the same re-review): the
unpowered-charging fix only guarded `CompDWCharger.CompTick` (the
radius>0 nimbus's passive path). The radius-0 sockets/docks are charged
entirely by `JobDriver_DWRecharge`/`JobGiver_DWRecharge`, which never
checked power/switch state — hoisted the check into a shared
`CompDWCharger.IsOperational` property and applied it to the job-giver's
candidate filter and the job driver's tick action (ends the job cleanly
if the grid drops mid-charge), not just the comp's own tick.

All fixes compile clean (`Droidworks.csproj`, 0/0, now with a Harmony
reference). A third fresh full-file re-review is owed before this file
set can be marked clean in `infrastructure/state/CODE_REVIEW_STATUS.json`
— this is now the second time a fix in this exact file set introduced or
unmasked something the previous pass missed.
