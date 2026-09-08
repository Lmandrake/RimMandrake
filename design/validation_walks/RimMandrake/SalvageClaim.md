# SalvageClaim — validation walk
subject: src/RimMandrake/SalvageClaim  (packageId mandrake.rm.salvageclaim)
deps: mandrake.rm.property (hard modDependency, "RimMandrake: Property" — this mod is a thin verb layer over Property's `PropertyEngine`/`ClaimEngine`/`RecognizabilityUtility`)
list: minimal+property
status-hint: adds ONE right-click float-menu order, "pay claim fee," any colonist can issue against an unowned Thing (or a downed mechanoid/droid Pawn); fee scales with the target's recognizability and any prior claim's decayed strength, paid from the acting pawn's own carried silver, and fires `PropertyEngine.Fire` with `ClaimBasis.ClaimFeePaid` unconditionally-authorized.

## must be true
- `SalvageClaimFeeUtility.ComputeFeeSilver` returns a value in `[MinFeeSilver=5, MaxFeeSilver=350]`, floored at `UnclaimedStrengthFloor=0.2` of the recognizability-driven ceiling even for a fully-decayed/never-claimed Thing (`SalvageClaim/Source/SalvageClaimFeeUtility.cs:26-49`).
- `FloatMenuOptionProvider_PaySalvageClaim` offers the order only for: a downed Pawn that IS a mechanoid (`targetPawn.Downed && targetPawn.RaceProps.IsMechanoid`), or an ordinary Thing whose `def.category` is `Item`/`Building`, is not natural rock, and has `MarketValue > 0` (`SalvageClaim/Source/FloatMenuOptionProvider_PaySalvageClaim.cs:65-84`).
- The order is withheld entirely when `IsAlreadyFreeToUse` (the actor already owns it, or it's Commons-and-same-faction) — mirrors `PropertyEngine`'s private authorization rule as a UI-only pre-check (`FloatMenuOptionProvider_PaySalvageClaim.cs:129-142`).
- Insufficient silver or unreachable target produces a disabled `FloatMenuOption` with an explanatory label ("not enough silver (need X, have Y)" / "NoPath") rather than a silent no-op (`FloatMenuOptionProvider_PaySalvageClaim.cs:97-108`).
- Executing the order removes exactly `fee` silver from the actor's inventory and fires `PropertyEngine.Fire(new TakingEvent(thing, actorRef, TakingAct.Claim, tick))`, which resolves to `ClaimBasis.ClaimFeePaid`, `WasAuthorized=true` unconditionally (no perception roll) — Property's own fabric, exercised end-to-end for the first time by this mod (`FloatMenuOptionProvider_PaySalvageClaim.cs:110-119`).
- The float-menu label reads exactly `"Pay salvage claim fee (" + fee + " silver) on " + clickedThing.LabelShort`.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.salvageclaim" and no XML error naming SalvageClaim's About.xml (mod ships no Defs — confirmed no `Defs/` folder)   # load-time
2. [B] `jawa/spawn_batch` (or `rimworld/spawn_thing`) a colonist-reachable `Steel` chunk with `MarketValue > 0`, then `jawa/spawn_pawn` a colonist near it
3. [B] `jawa/inventory_transfer {mode: "add", ...}` to give the colonist ≥ `MaxFeeSilver` (350) silver, then confirm via `rimworld/get_selected_pawn_inventory_state`
4. [B] `rimworld/right_click_cell` on the spawned Thing's cell with the colonist selected, then `rimworld/get_context_menu_options` → expect an option starting with "Pay salvage claim fee (" and containing " silver) on "
5. [B] `rimworld/execute_context_menu_option {label: "Pay salvage claim fee"}`, then re-check the colonist's inventory silver dropped by exactly the quoted fee amount
6. [D] def read-back is not applicable (no Defs shipped) — instead confirm via a live RimDefDump/log check that `RM_Property`'s claim ledger now records the Thing with `ClaimBasis.ClaimFeePaid` (cross-mod verification; exact read mechanism belongs to Property's own instrumentation, not duplicated here)
X. [S] (human pass) none beyond the float-menu text itself, already covered by step 4
