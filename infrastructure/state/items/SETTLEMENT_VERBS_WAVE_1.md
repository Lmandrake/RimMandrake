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
