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
