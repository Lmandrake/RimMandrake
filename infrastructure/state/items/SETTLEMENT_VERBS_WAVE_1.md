## 2026-09-18 (FOUNDRY, belt mode, subagent) — fourth verb family started: social fabric

Tally, all four v1 verb families from `design/Jawa/ownership_settlement_spec.md`
item 9: **salvage-law gray zone (built, 2026-09-01) · walkable commerce
(built, 2026-09-12) · crime suite (pickpocket built 2026-09-18, this pass
fixed a build gap in it — see below; night burglary/fencing/smuggling still
unbuilt) · social fabric (hiring the placeless built THIS pass; rumors as
intel, sabacc, and bribes/bought-rounds-as-dampers still unbuilt).** **All
four families now have at least one live, actually-compiled-in piece** —
first time this item can say that. Each family still has real open scope
(see the per-family notes below and the prior passes' own entries); this is
not the item's closure, just the point where every family has crossed from
zero to one.

**Found and fixed first, before any new code** (a real defect, not a
scope note): `RM_Property.csproj` sets `EnableDefaultCompileItems=false`
and lists every source file explicitly — and the 2026-09-18 crime-suite
commit (`d95d7ec55`) added `Pickpocket/FloatMenuOptionProvider_Pickpocket.cs`
and `Pickpocket/PickpocketUtility.cs` to disk and to git, but never added
them to the csproj's `<Compile>` list. Every `dotnet build` since then
silently skipped both files and still reported "0 warnings, 0 errors" —
truthfully, of the file set the csproj actually named, which never included
Pickpocket. Caught by literal-string-checking the built DLL for
`FloatMenuOptionProvider_Pickpocket`/`PickpocketUtility` before trusting the
prior pass's own "compiles clean" claim (`MEASURE_ALLOW_SCAN=1 strings` per
the measuring-large-artifacts skill's literal-existence-check carve-out,
never a census) — neither string was present. **The shipped DLL never
contained the pickpocket verb at all**, from `d95d7ec55` until this pass's
fix, despite the item file and commit message both saying it was built.
Added both files to the csproj this pass, rebuilt, and the *first ever real
compile* of `PickpocketUtility.cs` turned up an actual bug the untested code
had been carrying the whole time: `TransferToActor`'s
`ThingOwner.TryTransferToContainer(...)` call returns the transferred
**count** (`int`) in this RimWorld API version, not `bool`, so the bare
`return source.TryTransferToContainer(...)` didn't compile (`CS0029`) —
fixed to `> 0`. Re-verified via the same literal-string DLL check after the
fix: `FloatMenuOptionProvider_Pickpocket`, `PickpocketUtility`,
`FindStealableItem`, `TransferToActor` all now present in the rebuilt DLL.
**Lesson for whoever reads this next**: "compiles clean, 0/0" is not proof a
new file was even compiled when a project uses explicit `<Compile>` lists —
check the csproj lists the file, or check the DLL for the type name, before
trusting the claim. Pickpocket is genuinely untested beyond this compile fix
(no live-quicktest ever ran against a DLL that actually contained it) —
still owed, same as its own still-open live-quicktest note below.

**Built this pass** (`mandrake.rm.property`, same mod as SalvageClaim/
WalkableCommerce/Pickpocket — `src/RimMandrake/RimProperty/Source/
HirePlaceless/`): a right-click `FloatMenuOptionProvider_HirePlaceless`
order, the same shape as every other verb this item built (needs a selected
acting pawn + a clicked target Pawn; no JobDriver, the transaction — a
silver payment and a provenance record — runs instantly from the option's
own delegate).

**Checked first, per this pass's own brief**: does hiring map onto an
already-implemented case? Yes, and this is the cleanest fit of the four
verbs built so far — `WalkableCommerce`'s own doc comment (2026-09-12)
explicitly flagged this exact gap when it scoped a live Pawn target OUT of
its own pass: *"a live Pawn is hiring/indenture — social-fabric/crime-suite
territory, out of this pass."* That points straight at `PropertyEngine.
Fire`'s existing `TakingAct.Buy` case (`RecordTransfer(...,
ClaimBasis.Purchased, 1f, ...)`, `WasAuthorized = true` unconditionally —
"a completed sale is legitimate by definition"). `TakingEvent.Thing` is a
plain `Verse.Thing` field and `Pawn` *is* a `Thing`, so firing `Buy` against
a target Pawn needed no new field, no new `TakingAct` case, no new
`ClaimBasis` — the fabric doesn't know or care that the "merchandise" is a
person. This pass built only the gate and the fee.

**The gate IS the verb, and it's the mirror image of BuyMerchandise's own
gate**: `BuyMerchandise` requires a *resolved* prior claim (an unclaimed
item has no seller). Hiring the **placeless** requires the *absence* of any
resolved claim, virtual or recorded (`ClaimEngine.ResolveClaim(...)
.HasValue` must be `false`) — verified by reading `ClaimEngine` before
writing this, not assumed: `ResolveVirtualClaim`'s `FindPossessor` only
fires for a Thing held in someone's equipment/apparel/inventory/carry
tracker, which a spawned map Pawn never is of itself, and its Commons
fallback reads `thing.Faction`, which is null for a "placeless" pawn by
definition — so a faction-less, unpossessed, unclaimed Pawn genuinely
resolves to no claimant at all, and the same check correctly blocks a
second hire on someone another actor already hired (their still-resolving
`Purchased` record resolves and the gate refuses). `HirePlacelessUtility.
ComputeHireFeeSilver` reads a flat, Mod-Settings-tunable advance
(`PropertySettings.hirePlacelessFeeSilver`, default 20 silver,
`PropertyTuning.HirePlacelessFeeSilver`) — same "no second pricing model,
flat and tunable only" discipline `WalkableCommerce`'s markup and
`Pickpocket`'s value floor already used; no wage/contract/skill-scaling
system exists to price against instead. Silver counting/removal reuses
`SalvageClaimFeeUtility.CountSilverInInventory`/`RemoveSilverFromInventory`
directly, same reuse chain `BuyMerchandiseUtility` already established.

**Where it differs from the prior three verbs, deliberately**: no physical
hand-off, no job, no schedule, no AI-following behavior — same "the point is
the provenance RECORD, not a move" v1 simplification `WalkableCommerce` and
`PaySalvageClaim` both already apply to their own targets. Gated off
`targetPawn.Downed` specifically so this verb never competes with the
claim-fee gizmo's own "powered-down droid" case (item point 3) for the same
target — Downed routes to salvage-law, active routes to here. Gated off
`targetPawn.HostileTo(actor)` (same reasoning Pickpocket's own gate uses) and
off `targetPawn.IsPrisoner` (a prisoner already belongs somewhere; freeing
and recruiting them is vanilla's own territory). Scoped to
`RaceProps.Humanlike || RaceProps.IsMechanoid` targets only — an active,
unclaimed droid is a legitimate "placeless" hire under this same gate, not
just people.

**Not built this pass, explicitly out of scope** — social fabric's other
three sub-mechanics from spec item 9 (*"rumors as intel, sabacc, hiring the
placeless, bribes and bought rounds as propagation dampers"*), same "pick
ONE, flag the rest" discipline the crime-suite pass applied to its own
sub-list:
- **Rumors as intel** and **bribes/bought rounds as propagation dampers**
  both need a genuinely new read or write surface on `FactionRecord` that
  does not exist yet — `GetSuspicion`/`HasAnyPropagatedKnowledge` already
  compute exactly what rumors would need to report (and currently have
  *zero* callers anywhere in the codebase — confirmed by reading
  `PerceptionUtility`'s own doc comment: "the consequence-reader layer is
  unbuilt"), so rumors is real, buildable, well-scoped follow-up work, not
  invention from nothing. Bribes need a NEW mutator on `FactionRecord`
  (nothing today lets a verb reduce or remove a witness entry) — genuinely
  new fabric work, not a float-menu wrapper. **Open design tension flagged
  for the owner, not resolved here**: this item's own module-boundary table
  says "Verbs ... must not know perception outcomes (hidden even from the
  verb code's UI)" — rumors-as-intel's whole point is reporting a
  perception-derived fact TO the player, which reads in real tension with
  that boundary as written. Whoever builds rumors should either get an
  explicit ruling on that tension or design the reveal as qualitative
  flavor text (never the raw suspicion float) to stay inside the "no meter,
  no indicator" spirit of spec item 6 while still answering "rumors as
  intel."
- **Sabacc** is a whole card-game minigame (deck, stakes, a UI loop) — not a
  right-click order at all, and not attempted here.

Mod Settings retrofitted (`PropertySettings.cs`): `hirePlacelessEnabled`
(default on) and `hirePlacelessFeeSilver` slider (0-100 silver), same
checkbox+slider pattern as every other gateable mechanic in this mod.
Module doc-comment count updated from six to seven gateable mechanics.

**Verified this pass**: `dotnet build RM_Property.csproj -c Release`
compiles clean, 0 warnings, 0 errors (after the Pickpocket csproj fix and
its `TryTransferToContainer` bug fix above), DLL rebuilt at
`src/RimMandrake/RimProperty/Assemblies/RimMandrakeProperty.dll`. Re-verified
via literal-string DLL check (not trusted on the build log alone, per this
pass's own lesson): `FloatMenuOptionProvider_HirePlaceless`,
`HirePlacelessUtility`, `ComputeHireFeeSilver`, `FloatMenuOptionProvider_
Pickpocket`, `PickpocketUtility` all present. `deploy_custom_mods.py --mod
RimProperty` (plan only) reports drift, as expected — **not deployed**: the
game is up tonight and `mandrake.rm.property` is already an active, loaded
mod, same posture as every prior pass on this item.
`selftest_property_fabric.py` passes 20/20, unaffected (it tests
`ClaimDecay`/`ClaimantRef`/`ClaimEngine`'s own decay math, none of which
this pass touched). Full `run_selftests.py` sweep: 58/60 passed; the two
failures (`selftest_art_checks.py`, `selftest_one_path_seam.py`) are
pre-existing and unrelated (art-check tooling and a LocalLow path literal in
`artpipe/build_flora_legibility_sheet.py`), matching every prior pass's own
note on this item. No new XML/patches shipped (C#-only), so
`validate_patch.py` has nothing to check. **Not live-quicktest-observed**
(needs the bridge, contended tonight per the shared-worktree note) — same
"left `doing`, not closed" posture every prior pass on this item took, and
now doubly true for Pickpocket specifically since tonight is the first time
a DLL containing it has existed at all.

**Owner note (MODE=afk, filing rather than waiting)**: not closing this
item despite all four families now having a first piece — re-read `##
criteria` below and it was written for the *original* salvage-law-only
filing ("a claim-fee interaction exists... the other three verb families
are untouched and remain open work"), never revised when crime suite/
walkable commerce/social fabric were folded in as the item grew. It states
no "all four families done" closing bar at all, so there's nothing in the
item's own criteria to satisfy toward closure — leaving `doing`. If the
owner wants this item closed now that every family has crossed zero-to-one,
that's a scope ruling only he can make, and the `## criteria` section
below should be rewritten to say so explicitly before any future pass reads
it as ambiguous the way this one did.

## 2026-09-18 (FOUNDRY, belt mode, subagent) — third verb family built: crime suite

Tally, all four v1 verb families from `design/Jawa/ownership_settlement_spec.md`
item 9: **salvage-law gray zone (built, 2026-09-01) · walkable commerce
(built, 2026-09-12) · crime suite (pickpocket built THIS pass; night
burglary/fencing/smuggling still unbuilt) · social fabric (unbuilt)**. Three
of four now have at least one live-code-complete piece; social fabric
remains untouched — no capacity left this pass to start it (see the item's
own steer against a shallow stub, same reasoning the 2026-09-12 pass gave for
skipping crime suite/social fabric that time).

**Built this pass** (`mandrake.rm.property`, same mod as SalvageClaim/
WalkableCommerce — `src/RimMandrake/RimProperty/Source/Pickpocket/`): a
right-click `FloatMenuOptionProvider_Pickpocket` order, the exact same shape
as `FloatMenuOptionProvider_PaySalvageClaim`/`BuyMerchandise` (needs a
selected acting pawn + a clicked target Pawn; no JobDriver, the whole
transaction — including the physical hand-off — runs instantly from the
option's own delegate).

**Checked first, per this pass's own brief**: does crime map onto an
already-implemented case? Yes, and it's the same "fabric already implements
the RESULT" situation Claim/Buy were in, but for a DIFFERENT reason than
those two. Claim/Buy fire `TakingAct.Claim`/`Buy`, whose `PropertyEngine.
Fire` case sets `WasAuthorized = true` unconditionally — never witnessed, by
definition. Pickpocket fires plain `TakingAct.Take` against a Thing a
target Pawn currently possesses (`ClaimEngine.FindPossessor`'s
`Pawn_InventoryTracker` case resolves a virtual `Situational` claim to that
Pawn at strength 0.9) with actor != that Pawn — `PropertyEngine.IsAuthorized`
correctly refuses it, `Fire`'s `Take` case records a `ClaimBasis.Stolen`
record for the ORIGIN claimant (the victim) at strength 1.0 and rolls
perception (`RollPerceptionAndPropagate`), all already built and already
exercised by AnimalTheft (unattended ground items) and TheftHauler
(buildings, via `Strip`). Pickpocket is the first verb to point `Take` at a
PERSON's own carried inventory rather than an unattended item or a building
— that target-kind gap, not the claim/perception math, is what this pass
actually built. `PickpocketUtility.FindStealableItem` picks the highest
`MarketValue*stackCount` item in the target's `Pawn_InventoryTracker`
container above a tunable floor (`PropertySettings.
pickpocketMinItemValueSilver`, default 5 silver, `PropertyTuning.
PickpocketMinItemValueSilver`) — reuses the fabric's own published stat, no
second pricing model.

**The one physical hand-off this wave actually performs**: unlike the
claim-fee/buy verbs (deliberately provenance-record-only, no inventory
move), a pickpocket that doesn't move anything isn't a theft, so
`PickpocketUtility.TransferToActor` calls `ThingOwner.
TryTransferToContainer` with `canMergeWithExistingStacks: false` —
deliberately not the API default. `GameComponent_PropertyLedger.
RecordClaim`'s own doc comment explains why: the ledger keys claim records
on the Thing INSTANCE, and a stack-merge into something the actor already
carries would `Destroy()` the just-stolen Thing and orphan the `Stolen`
record `PropertyEngine.Fire` recorded against it moments earlier in the same
delegate. `Fire` is called BEFORE the transfer (same ordering AnimalTheft/
TheftHauler already use — "at the moment of taking, not haul-pickup"),
because `ClaimEngine.ResolveClaim` needs to see the item still in the
target's inventory to resolve the victim's `Situational` claim correctly.

**Where it differs from the prior two verbs, deliberately**: scoped to the
target Pawn's `Pawn_InventoryTracker` only — never an equipped weapon
(`Pawn_EquipmentTracker`) or worn apparel (`Pawn_ApparelTracker`), same
"no ripping slotted gear off a living body" simplification the prior passes
already applied to their own target kinds. Gated off `targetPawn.
HostileTo(actor)` — pickpocketing mid-firefight isn't this verb; that's
vanilla's own attack/capture territory. Not gated on the target being awake
or downed: `PerceptionUtility.RollWitnesses` already excludes anyone
`!Awake()` or `Downed` from personally witnessing, so a sleeping or downed
target's own perception risk drops out for free with no special-casing —
this incidentally covers part of "night burglary"'s flavor (an unaware
target) through the SAME code path, but this pass makes no claim to have
built burglary as its own verb: no unattended-building/container target
kind, no night/day gate, no gate-search interaction. Fencing (needs a
buyer/vendor NPC) and smuggling past gate searches (needs a district/gate
concept) are explicitly OUT — both need groundwork from
`SETTLEMENT_VISIT_LOOP_1` (still `doing`) that doesn't exist yet, same
reasoning the 2026-09-12 pass gave for leaving all of crime suite untouched
that time.

Mod Settings retrofitted (`PropertySettings.cs`): `pickpocketEnabled`
(default on) and `pickpocketMinItemValueSilver` slider (0-50 silver), same
checkbox+slider pattern as every other gateable mechanic in this mod. Module
doc-comment count at the top of `PropertySettings.cs` updated from five to
six gateable mechanics.

**Verified this pass**: `dotnet build RM_Property.csproj -c Release`
(via the Windows-native `dotnet.exe`, D-drive path — this box has no
`dotnet` on the WSL `PATH`) compiles clean, 0 warnings, 0 errors, DLL
rebuilt at `src/RimMandrake/RimProperty/Assemblies/RimMandrakeProperty.dll`.
`deploy_custom_mods.py --mod RimProperty` (plan only) reports drift, as
expected — **not deployed**: the game is up tonight and `mandrake.rm.
property` is already an active, loaded mod, same posture as the 2026-09-12
pass. `selftest_property_fabric.py` (the offline C# decay/claimant-math
selftest) still passes 20/20, unaffected — it doesn't touch anything this
pass changed. Ran the full `run_selftests.py` sweep afterward: 58/60 passed;
the two failures (`selftest_art_checks.py`, `selftest_one_path_seam.py`) are
pre-existing, unrelated to this pass (art-check tooling and an unrelated
LocalLow path literal in `artpipe/build_flora_legibility_sheet.py`), not
introduced by this change. No new XML/patches shipped (C#-only, same as
SalvageClaim/WalkableCommerce), so `validate_patch.py` has nothing to check.
**Not live-quicktest-observed** (needs the bridge, which is contended
tonight per the shared-worktree note) — same "left `doing`, not closed"
posture every prior pass on this item took.

**Owner note (MODE=afk, filing rather than waiting)**: this pass reads
"crime suite" as satisfied by ONE genuinely-scoped verb (pickpocket), not
all four of its spec-item-9 sub-list. If the owner intends "crime suite" to
mean the whole sub-list before this family counts as built, that's a scope
call only he can make — flagging it explicitly rather than guessing either
way. Fencing and smuggling in particular are blocked on `SETTLEMENT_VISIT_
LOOP_1`'s cast-NPC/vendor and district-gate concepts landing first, not on
anything in this pass's control.

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
