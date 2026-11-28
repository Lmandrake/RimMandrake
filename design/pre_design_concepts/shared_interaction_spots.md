# Shared interaction spots

- **Name:** Shared interaction spots
- **Kind:** capability for a mod that does not exist yet
- **Gets:** the player can place two work benches so that both face one shared spot, where the worker stands.
- **Added:** 2026-11-26
- **From ticket:** `RIMMANDRAKE_ALLOW_SHARED_INTERACTION_SPOTS_TWO_BENCHES_ONE_STOOL` (ended 2026-11-26: this file keeps the concept)
- **Code:** none. Measured 2026-11-26 with `git grep -n PreventInteractionSpotOverlap -- '*.cs'`: no C# file names the vanilla placeworker `RimWorld.PlaceWorker_PreventInteractionSpotOverlap`. Some of our def files list that placeworker on their own buildings; that is the vanilla rule, not this concept.
- **Last offered:** 2026-11-27
- **His answer:** Flesh out now with the Conductor (his card answer of 9:25 PM PST 2026-11-27: he picked 'Utility creatures' and 'Shared work spots')
- **Went to:** the ticket `RIMMANDRAKE_PATCH_SHARED_WORK_SPOTS_BOTH_STAND_IN_IT` (2026-11-27), a small patch in the RimMandrake patches mod. It waits behind the pipeline repairs by his order of the same evening.

## His words

- 2026-11-14 (ledger, OWNER `file` event of the ticket, 2026-11-14T20:03:10Z, from his live look about 11:30 AM to
  12:10 PM PST, finding 2, `D:\ClaudeWork\rimmandrake\conductor\sitting_20261114\OWNER_LOOK_WORDS.md`): "I noted that
  you couldn't overlap two interaction spots for furniture. Could we patch it so that you can? This would be put in some
  other RimMandrake mod I presume."
- 2026-11-14 (ledger, OWNER note, 2026-11-14T20:14:35Z), decided by card: "Where does shared interaction spots belong?
  → Small tweaks mod, Polish". The note: "DECIDED 2026-11-14 12:1x PM PST: home is the RimMandrake patches mod, as a
  Polish item with an on/off mod setting; not part of FlowWorks' version or bars." The card store holds no copy of the
  card (`card_capture.py show` on the ticket, 2026-11-26: no ledger event carries a card), so the other options are not
  known.
- 2026-11-26 (ledger, OWNER note on the ticket, 2026-11-26T21:12:03Z): "I do like both of those ideas still utility
  creatures and shared interaction spot. Is there a designation or safe place for good mod ideas we haven't designed out
  yet?"

## Where it would live

The card put it in the RimMandrake patches mod (`D:\Luke\dev\RimMandrake\src\RimMandrake\MandrakePatches\`, packageId
`mandrake.rm.patches`, Harmony already a dependency). That mod has code but no folder in
`D:\Luke\dev\RimMandrake\design\concepts\`, so it has no next-version list. When that mod enters the Maturation Pipeline,
this concept moves to its next-version list (the store's rule for a capability of a mod that exists).

## The source ticket, whole

`RIMMANDRAKE_ALLOW_SHARED_INTERACTION_SPOTS_TWO_BENCHES_ONE_STOOL`. State `proposed`, kind `task`, needs `offline`,
target `v1`, owner BENCH, filed 2026-11-14T20:03:10Z.

Title: "Let two benches share one interaction spot: patch vanilla PlaceWorker_PreventInteractionSpotOverlap (owner look
2026-11-14 #2; home mod undecided; PROPOSED Polish)"

The ticket's prose, whole (`infrastructure/state/items/RIMMANDRAKE_ALLOW_SHARED_INTERACTION_SPOTS_TWO_BENCHES_ONE_STOOL.md`,
`## spec`):

> Owner, live look 2026-11-14 about 11:30 AM to 12:10 PM PST (finding 2, `D:\ClaudeWork\rimmandrake\conductor\sitting_20261114\OWNER_LOOK_WORDS.md`):
>
> > "I noted that you couldn't overlap two interaction spots for furniture. Could we patch it so that you can? This would be put in some other RimMandrake mod I presume."
>
> What blocks it in vanilla. RimSage was unavailable, so this was read from the decompile at `D:\ClaudeWork\rimmandrake\decomp\rw16\all\RimWorld`:
> - `RimWorld.PlaceWorker_PreventInteractionSpotOverlap.AllowsPlacing` refuses with "InteractionSpotOverlaps" or "InteractionSpotWillOverlap" when the new building's interaction cell equals the interaction cell of an existing (or blueprinted) building. It scans the things within 1 cell of each interaction cell.
> - The official def dump (August 2026) shows that placeworker on 476 ThingDefs. A sanity probe found 16108 ThingDefs carrying some `PlaceWorker_`. Examples are TableButcher, HandTailoringBench and CraftingSpot.
> - `GenConstruct` adds two more rules that are not this one and stay:
>   - `InteractionCellStandable`: nothing impassable may sit on an interaction cell.
>   - `NotBlockingAnyInteractionCells`: a new building may not stand on another's spot.
>
> Likely fix: a Harmony prefix that makes `PlaceWorker_PreventInteractionSpotOverlap.AllowsPlacing` return Accepted (behind a setting, default on). Removing the placeworker from 476 defs by XML patch would be the wrong route.
> - Then check that two pawns working benches that share one spot queue rather than stack. The vanilla reservation is on the bench, not the cell, so two workers can stand on one cell; this needs a live look.
>
> Home mod: his words say "some other RimMandrake mod". Which one is not decided here; it is not FlowWorks.
>
> Design Version class: PROPOSED Polish (an owner call).
>
> Build effort: small.
>
> Acceptance test (offline, a local model could run it): a selftest loads the patched assembly's Harmony targets and asserts a prefix on `RimWorld.PlaceWorker_PreventInteractionSpotOverlap.AllowsPlacing` that returns Accepted while the setting is on and defers to vanilla while it is off. The vanilla `InteractionCellStandable` refusal must stay unpatched.

History (4 events):

- 2026-11-14T20:03:10Z OWNER `file`: for BENCH, kind task, needs offline, target v1, with his words above.
- 2026-11-14T20:14:35Z OWNER `note`, by card: the home decision above.
- 2026-11-24T05:44:38Z BENCH `home`: home `unplaced`, group `home-mod-undecided`, flag `LOOKS CURRENT`. Reason: "the
  ticket says that its home mod is undecided" (the owner's grouping by home, 2026-11-23). That reason was out of date:
  the card of 2026-11-14 had named the home.
- 2026-11-26T21:12:03Z OWNER `note`: "He still wants this idea (his word of 2026-11-26). Not designed, not scheduled.
  No sweep drops it as stale." With his words of 2026-11-26 above.

## Offers

- 2026-11-27: Flesh out now with the Conductor (his card answer of 9:25 PM PST 2026-11-27: he picked 'Utility creatures' and 'Shared work spots')

## The design talk of 2026-11-27 (his card of 9:51 PM PST)

The one open point was put to him: when two workers want the shared spot at the same time, what should happen? He picked
"Both stand in it". The description of that option, word for word: "Why: no extra code. The base game already lets two
workers stand in one square while they work, so both benches run at once. Costs: two colonists drawn on top of each
other." The options that he did not pick: "One waits (Recommended)" and "Decide after a look".

So the design is: the patch only, behind an on/off Mod Setting (default on); no rule that reserves the spot.
