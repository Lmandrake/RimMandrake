## 2026-09-02 (FOUNDRY) — correcting the record: this was ALREADY BUILT, 2026-09-01

Same bookkeeping gap as `BUILDING_THEFT_HAULER_1` (see `QUEUE_ITEM_FILES_DECAY_1`):
commit `ad778ef0` (2026-09-01) built the full salvage-law claim-fee gizmo
under `src/RimMandrake/SalvageClaim/` and never wrote it up here, so this
item file still read as pure spec/verify/criteria. Caught by `git log` on
the folder name after `BUILDING_THEFT_HAULER_1`'s own near-miss, not by the
queue tooling.

**What's built** (packageId `mandrake.rm.salvageclaim`): a right-click
`FloatMenuOptionProvider_PaySalvageClaim` order (chosen over a Gizmo for the
same reason `TheftHauler`'s provider was — needs both a selected paying pawn
and a clicked target Thing) that fires
`PropertyEngine.Fire(TakingEvent(..., TakingAct.Claim, ...))`, gated off
already-free-to-use (own claim / same-faction Commons — a narrow local copy
of `PropertyEngine`'s own private authorization test, used only to decide
whether to OFFER the gizmo; `Fire()` would still behave correctly without
it). Fee scales via `SalvageClaimFeeUtility.ComputeFeeSilver` from
`RecognizabilityUtility.Score` and the resolved prior claim's
`EffectiveStrength` (5-350 silver, floor 0.2 recognizability-weight so a
decayed claim on something recognizable never prices like a decayed claim on
a steel bar) — reuses the fabric's own published numbers, no second pricing
model. Silver is drawn from the acting pawn's own carried inventory only (v1
simplification, documented in-file). The powered-down-droid case (item point
3) is handled: `clickedThing is Pawn` falls through the same generic `Thing`
path, gated to `Downed && RaceProps.IsMechanoid` (deliberately narrower than
"any downed pawn" — a downed humanlike is vanilla's own
arrest/rescue/capture territory, out of this pass's scope).

**Re-verified this pass**: `deploy_custom_mods.py --mod SalvageClaim` reports
in-sync (no rebuild needed, DLL already matches game copy); `mandrake.rm.
salvageclaim` is active in the live 592-mod `ModsConfig.xml`. Not re-run:
`validate_patch.py` (this mod ships no XML patches, only an About.xml and
compiled C#, so there's nothing for that tool to check) and `dotnet build`
(deploy already reported in-sync, unlike TheftHauler's stale DLL, so nothing
to resync).

**Not done, unchanged from the original build**: live-quicktest proof (pay
the fee on an unclaimed/weakly-claimed wreck and on a downed droid pawn,
confirm a `ClaimBasis.ClaimFeePaid` record lands) — needs a bridge session,
not available tonight. Left `doing`, not closed, same as `BUILDING_THEFT_
HAULER_1`.

## spec
Full ruling: `design/Jawa/ownership_settlement_spec.md` (owner sitting 2026-08-31),
item 9: "v1 verb families: crime suite (pickpocket, night burglary, fencing,
smuggling past gate searches), salvage-law gray zone (claim-fee gizmo, wreck
rights, the powered-down droid), walkable commerce (merchandise, haggling,
purchase as the legal provenance record), social fabric (rumors as intel,
sabacc, hiring the placeless, bribes and bought rounds as propagation
dampers)." Module boundary: "Verbs | gizmos/jobs that EMIT TakingEvents and
read AccessPolicy | must not know perception outcomes."

Four verb families is too large for one build pass — each is really its own
item. **This pass scopes to ONE: the salvage-law gray zone**, because it is
the family most directly grounded in systems already built and live-tested
tonight (`RM_Property`'s `ClaimBasis.BattleLootOrigin`/`ClaimBasis.Looted`
pair already models exactly this — see `PropertyEngine.RecordLoot` — and
`BUILDING_THEFT_HAULER_1`'s `TakingAct.Strip` pattern is the template for a
claim-fee gizmo firing its own event). Crime suite, walkable commerce and
social fabric remain unbuilt — file them as separate items when picked up,
do not silently fold them into this one's closure.

Scope for this pass:
1. **Claim-fee gizmo**: a `Gizmo`/`CompUseEffect`-style interaction on an
   unclaimed or weakly-claimed Thing (a wreck, a powered-down droid) that
   lets a pawn pay a fee and fire `PropertyEngine.Fire(TakingAct.Claim)` —
   read `PropertyEngine.cs`'s existing `Claim` case
   (`ClaimBasis.ClaimFeePaid`, `WasAuthorized = true` unconditionally) before
   building; the fabric already fully implements the RESULT of this verb,
   this item only needs to build the JOB/INTERACTION that fires it.
2. **Wreck rights**: gate the claim-fee gizmo's availability/fee scaling on
   the Thing's recognizability and prior claim strength (a fresh battlefield
   wreck vs. an old abandoned one) — read
   `src/RimMandrake/Property/Source/RecognizabilityUtility.cs` and
   `ClaimEngine.cs` for the existing decay/strength model, do not invent a
   second one.
3. **The powered-down droid** case: confirm the gizmo also works on a
   `Pawn` (a droid) as well as an ordinary `Thing` — `ClaimantRef`/
   `TakingEvent` are already typed generically enough (`Thing Thing` field)
   to cover a downed mechanoid/droid pawn, verify this rather than assume it.

Explicitly OUT of this pass: crime suite (pickpocket/burglary/fencing/
smuggling), walkable commerce (merchandise/haggling), social fabric (rumors/
sabacc/bribes), and any change to `RM_Property`'s own claim math.

## verify
- `validate_patch.py` clean on any new XML.
- Compiles clean; reuses `PropertyEngine.Fire`/`ClaimEngine`/
  `RecognizabilityUtility` rather than reimplementing claim/decay logic.
- Live-quicktest-observed (FOUNDRY, not the build agent): a pawn pays the
  claim fee on an unclaimed/weakly-claimed wreck or downed droid, a
  `ClaimRecord` with `ClaimBasis.ClaimFeePaid` appears against the paying
  actor. `RM_Property` is not yet in `ModsConfig.xml` — enabling it is part
  of running this test, same as `BUILDING_THEFT_HAULER_1`'s still-owed
  quicktest.

## criteria
A correct v1: a claim-fee interaction exists, fires exactly the fabric's
already-built `TakingAct.Claim` path, is gated by recognizability/prior-claim
strength rather than a flat fee, and works on both an ordinary Thing and a
downed droid Pawn. The other three verb families are untouched and remain
open work.
