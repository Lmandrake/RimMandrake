# WARDEN_MOTHER_SUCCESSION_1 — warden mother young: self-taming, water-scoped training, and succession on her death

Caused by `WARDEN_MOTHER_BEFRIENDING_1`.

## what

`WARDEN_MOTHER_BEFRIENDING_1` shipped the core "waterline is the friendship"
mechanism: `RM_WardenMother`, the water-only movement constraint, the tolerance
state (`RM_CompTerritorialAnchor.GrantTolerance`/`IsTolerated`, read by
`RM_JobGiver_AnchorDefense.ExtraTargetValidator`), and spawn-linked stranded young
(`RM_SetPieceElement_AnchoredPawn`'s new `youngSpawnChance`/`youngKinds`/
`youngDeformationHediff` fields, wired in `RUT_Miasma_CrecheScatterer.xml`) plus
"the young's call" (`RM_HediffComp_LocatableCall` on `RUT_StrandedDeformation`).

**Not built in that pass**, per the roster's own §6a ruling (owner, 2026-09-23):

1. **Self-taming.** *"the babies should be trainable... they should frequently
   self-tame if there are no hostilities against them."* Same consent pattern as
   the Fever Wood's sap-drinker guild and the mother's own tolerance — nothing here
   is a taming grind. Needs new C# (a periodic check on a stranded/rescued
   juvenile's "clean record" against its own crèche, rolling self-tame while clean,
   barred or reset the moment the player harvests/kills/butchers one of that
   crèche's young).
2. **Water-scoped trainability.** Once self-tamed: Guard (patrol the channel),
   Release/Attack in water, and Haul-from-water-only (feeding `RM_Thrannock`'s
   flotsam root-lines per the roster's own §7 economy) — explicitly NOT Rescue and
   NOT general Haul, both of which need land a water-bound animal cannot reach.
   The roster's own text: "an animal that fails its own trained job is a bug
   wearing a feature."
3. **Succession on death.** The mother dies of age (`RM_WardenMother.race.
   lifeExpectancy` is already set to 45, INVENTED-BUILD, in the shipped ThingDef)
   — but nothing currently detects that death and promotes a self-tamed young to
   inherit the crèche (a smaller anchor radius, the same `RM_CompTerritorialAnchor`
   mechanism on a smaller creature). Per the roster: NOT guaranteed — rescue
   nothing and the crèche is just a place, and scavengers come. `RM_CompTerritorialAnchor.
   Notify_Killed`/`IRM_AnchorDeathListener` (already used by `RM_CompCrecheMarker`
   for the despoiled-memory mechanic) is the natural hook to extend, but old-age
   death may not route through `Pawn.Kill()` the same way a violent death does —
   check that before assuming `Notify_Killed` fires at all for old age.
4. **Foreshadowing.** The roster's own hard requirement: "a player surprised by
   her death means this was built wrong" — visibly ancient art (owed, no art
   exists for her at all yet), an inspect string that says it outright, measurable
   slowing as she ages, and an NPC (the Deepwater vigil) who tells you how long she
   has. None of this is built; it is content/UX work, not a mechanism gap.

## why this is its own item, not folded into the parent

Self-taming and succession are each a genuinely new mechanism (a consent-based
auto-tame trigger; a death-triggers-inheritance hook), not a content-only follow-on
— the same reason the parent's own text treats "the young's call" and the water
constraint as separate, named, load-bearing pieces. Bundling this into the parent
would have blocked closing the core befriending loop, which is fully built and
independently valuable, on work this roster's own owner-ruling accepts may never
fire in a given playthrough ("deliberately NOT guaranteed").

## spec (draft — offline, no engine questions flagged)

1. A new comp (working name `RM_CompSelfTameOnRecord`) on a juvenile carrying
   `RUT_StrandedDeformation`, or on the plain nursery juvenile species once rescued:
   tracks whether the player has harmed any member of the SAME crèche (keyed by the
   `RUT_CrecheMarker` Thing, mirroring how `RM_CompTerritorialAnchor.IsTolerated`
   keys tolerance); rolls a periodic self-tame chance while the record is clean.
2. On self-tame, set `Faction = Faction.OfPlayer` and add the water-scoped
   trainable tags via a `TrainableIntelligence`/allowed-jobs restriction —
   likely a small Harmony patch or a `WorkGiver`/`JobGiver` gate reusing
   `RM_CompWaterLocked.IsWaterCell`, since vanilla trainability has no native
   "water only" concept either.
3. On the mother's `Notify_Killed` (or an old-age-death hook, to be confirmed) with
   at least one clean self-tamed young registered to her crèche: promote one such
   young by calling `RM_CompTerritorialAnchor.SetAnchor()` on it, pointed at the
   same `RUT_CrecheMarker`, with a smaller `anchorRadius`.
4. Foreshadowing art/UX is separate content work, likely its own follow-on once
   art exists for the mature warden mother at all.

## Watch out

- ⛔ Not a taming grind — self-tame is consent-only, matching the Fever Wood guild
  and the mother's own tolerance. A conventional taming mechanic here fights three
  independent owner rulings at once (see the parent item's own text).
- Confirm whether old-age death actually calls `Pawn.Kill()` (and therefore
  `ThingComp.Notify_Killed`) before building the succession hook on that seam —
  if it does not, a different death-detection point is needed.
