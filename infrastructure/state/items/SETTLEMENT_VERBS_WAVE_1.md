## 2026-09-12 (FOUNDRY) — second verb family built: walkable commerce

Tally, all four v1 verb families from `design/Jawa/ownership_settlement_spec.md`
item 9: **salvage-law gray zone (built, 2026-09-01, see below) · walkable
commerce (built THIS pass) · crime suite (unbuilt) · social fabric
(unbuilt)**. Two of four now live-code-complete; two remain open work — file
them as their own items when picked up, per this item's own standing
instruction not to silently fold them in here.

**Built this pass** (`mandrake.rm.property`, same mod as SalvageClaim —
`src/RimMandrake/RimProperty/Source/WalkableCommerce/`): a right-click
`FloatMenuOptionProvider_BuyMerchandise` order, the exact same shape as
`FloatMenuOptionProvider_PaySalvageClaim` (needs a selected paying pawn +
a clicked target Thing; no JobDriver, the whole transaction runs instantly
from the option's delegate) firing `PropertyEngine.Fire(TakingEvent(...,
TakingAct.Buy, ...))` — `TakingAct.Buy` and its `ClaimBasis.Purchased`
result already existed in the fabric (`PropertyEngine.cs`'s Buy case,
`WasAuthorized = true` unconditionally, "a completed sale is legitimate by
definition"), same "fabric already implements the RESULT" situation Claim
was in for SalvageClaim. `BuyMerchandiseUtility.ComputePriceSilver` prices
off `Thing.MarketValue * stackCount * markup` (a flat, Mod-Settings-tunable
markup, `PropertySettings.walkableCommerceMarkup`, default 1.15x from
`PropertyTuning.WalkableCommerceMarkup`) — reuses the fabric's own published
stat, no second pricing model; haggling (spec item 9's own word) is
explicitly NOT built this pass, flat markup only. Silver counting/removal
reuses `SalvageClaimFeeUtility.CountSilverInInventory`/
`RemoveSilverFromInventory` directly rather than duplicating them.

**Where it differs from the claim-fee gizmo, deliberately**: Buy requires a
*resolved* prior claim (`ClaimEngine.ResolveClaim(...).HasValue`) — an
unclaimed thing has no seller, so it's the claim-fee verb's territory, not
this one's. Scoped to `ThingCategory.Item` only (a live Pawn is
hiring/indenture — social-fabric/crime-suite territory, out of this pass; a
Building is fixed infrastructure, not stock for sale). No physical hand-off
of the Thing happens — same v1 simplification as the claim-fee gizmo (which
doesn't haul the wreck either): the point of the interaction is the
provenance RECORD (spec item 9's own framing "purchase as the legal
provenance record"), not an inventory move.

Mod Settings retrofitted (`PropertySettings.cs`): `walkableCommerceEnabled`
(default on) and `walkableCommerceMarkup` slider (0.5x-3x), same
checkbox+slider pattern as every other gateable mechanic in this mod.

**Verified this pass**: `dotnet build RM_Property.csproj -c Release`
compiles clean, 0 warnings, 0 errors, DLL rebuilt at
`src/RimMandrake/RimProperty/Assemblies/RimMandrakeProperty.dll`.
`deploy_custom_mods.py --mod RimProperty` (plan only) reports drift — the
freshly-built DLL differs from the game's deployed copy, as expected. **Not
deployed**: the game is UP tonight running the full mod list and
`mandrake.rm.property` is already an active, loaded mod — extending an
already-loaded mod's DLL while the game is up needs `needs=deploy`, not a
forced deploy over a live process (own instruction for this pass). No new
XML/patches shipped, so `validate_patch.py` has nothing to check, same as
SalvageClaim's own note. Not live-quicktest-observed (needs the bridge; the
bridge is currently held by another window's work tonight) — same
"left `doing`, not closed" posture as the salvage-law pass took for its own
still-owed live proof.

**Not attempted this pass**: crime suite and social fabric. Both need real
groundwork the fabric doesn't have yet (a cast-NPC/vendor concept from
`SETTLEMENT_VISIT_LOOP_1`, which is itself still `doing`) before a
correctly-scoped verb can be built rather than a shallow stub — per this
item's own "smaller, fully-correct batch beats a large broken one" steer,
better left open than rushed.

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
