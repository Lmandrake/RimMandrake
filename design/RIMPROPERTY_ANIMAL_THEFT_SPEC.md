# RimProperty animal theft — RIMPROPERTY_ANIMAL_THEFT_1

**Status: DRAFT — pending owner review**

Owner, verbatim (2026-09-08): *"Some droid loaders have this property. Also add
that some agile pets may be trained to steal as do some wild animals."*
Lands in RimProperty (`mandrake.rm.property`, post-consolidation). All three
routes are verb-job territory per the fabric's own doctrine ("no Harmony hook
auto-detects a vanilla pickup"): each route's job code constructs a
`TakingEvent` and calls `PropertyEngine.Fire` explicitly.

## The one call every route makes

```csharp
PropertyEngine.Fire(new TakingEvent(thing, ClaimantRef.OfPawn(animal),
                                    TakingAct.Take, Find.TickManager.TicksGame));
```

(`RimMandrake.Property.PropertyEngine.Fire(TakingEvent)` —
`src/RimMandrake/RimProperty/Source/PropertyEngine.cs`.) Fire resolves the
prior claim, decides authorization, writes the `ClaimBasis.Stolen` origin
record on an unauthorized Take/Strip, rolls witnesses, and files per-witness
faction records. The droid route already does exactly this with
`TakingAct.Strip` (`JobDriver_TheftHaulUninstall`, in-assembly). Chronicle
spine: per CHRONICLE_EVENT_SPINE_1's ratified roster, **Fire itself** raises
`property.taking` into RimChronicle by reflection — the routes add no spine
code of their own and must not raise directly. (That raise is not yet in
Fire; it is CHRONICLE_EVENT_SPINE_1's wiring, not this item's.)

## Route 1 — trained-pet stealing (RM mechanism)

- **New `TrainableDef` `RM_Steal`**: `requiredTrainability` Advanced,
  `prerequisites` [Obedience], `defaultTrainable` false, `difficulty` ~300
  (Haul-tier). No `minBodySize` floor — "agile" wants small animals; a
  `maxBodySize`-style cap does not exist on TrainableDef, so the species gate
  is the extension below, not a size field.
- **Species gate**: the trainable is offered only on races carrying
  `RM_StealTrainableExtension` (new field-less-plus-tuning DefModExtension),
  via the standard `TrainableDef` visibility hook (`CompanionDialog`/
  `TrainableUtility` filtering — same idiom trainability mods use). No marked
  species, no steal training anywhere.
- **The job**: autonomous, mirroring trained Haul's idiom (animals take no
  direct orders): a ThinkTree JobGiver gated on
  `pawn.training.HasLearned(RM_StealDefOf.RM_Steal)` picks a nearby loose item
  whose resolved claim is neither the pet's own faction's Commons nor a
  same-faction pawn, carries it to the home area / master's stockpile, and on
  pickup fires `Fire(..., TakingAct.Take, ...)`. At the colony this only
  matters against guest/visitor-claimed things — engine already makes
  same-faction Commons takes authorized, so a pet cannot "steal" clan stock.

## Route 2 — wild-animal theft (RM mechanism)

- **Species gate**: `RM_WildThiefExtension` (DefModExtension) with tuning
  fields `mtbDays` and `maxMass`. Unmarked species can never fire it.
- **Trigger**: MTB-gated JobGiver in the wild-animal think tree (factionless
  animals only): pick one unforbidden item under `maxMass` with a resolving
  claim, grab it, flee toward map edge. Fires `Fire(Take)` on pickup; a
  factionless actor is never the claimant, so the take is unauthorized and
  the Stolen origin record is written.
- **Fairness**: the item physically travels — the animal visibly carries it
  and can be hunted down before it exits; nothing is deleted silently. If
  Fire's returned `evt.Witnesses` contains a player-faction pawn, post a
  message/letter ("a NAME made off with X"); unwitnessed thefts stay silent
  by design (spec item 6: a crime nobody saw — the player reads the world).
  Claim-less junk resolves *authorized* in the engine, so wild theft
  self-limits to things somebody owns.

## Route 3 — droid loaders (existing pattern extended)

`TheftHaulerExtension` already exists (field-less marker; carry-weight
scaling is an explicitly deferred later pass — do not add it here). Extend
`Patches/TheftHauler/MuckrakerChassis_TheftHauler.xml`'s MayRequire-gated
`PatchOperationFindMod` pattern: additional `<Operation>` blocks adding the
extension to each Droidworks race the owner designates as a "loader"
(defNames read from the live Races_*.xml, never guessed). Absent Droidworks
the file stays a silent no-op; the engine stays generic.

## RM / RUT split (ratified pattern)

| Tier | Ships |
|---|---|
| **RimProperty (RM)** | `RM_Steal` TrainableDef, both DefModExtension classes + JobGivers/ThinkTree patches, generic default tuning (mtbDays, maxMass), the Droidworks MayRequire patch mechanism |
| **RUT data** | which Ash'karr species get `RM_StealTrainableExtension` / `RM_WildThiefExtension` (pure XML patches), campaign mtb/mass overrides, which loader chassis join the patch |

Species lists are authored against the live def dump at build time (owner
picks; see open questions) — no species defName appears in RM code.

## v1 ships / deliberately NOT

**Ships**: the three routes above, dev-mode debug actions to force each job
(quicktest-provable), selftest coverage of the Fire calls, negative gate
(unmarked species have no route).
**NOT (YAGNI)**: carry-capacity scaling on loaders (deferred pass, per
`TheftHaulerExtension` doc); a "steal that" targeting UI; settlement-visit
stealing (needs Inhabited); fencing/heat/social-fight consequences (verbs
wave + RUT heat tuning); animals stealing buildings; a
principal/"on-behalf-of" field on TakingEvent (see constraint below); pet
theft of equipped/worn items (loose things only).

## API constraints on the owner's ask

1. **No principal field**: `TakingEvent.Actor` is one `ClaimantRef`;
   `RegisterWitness(evt.Actor, …)` files faction suspicion against the
   ANIMAL, not its master or the clan. A trained pet's thefts accrue heat to
   the pet in v1. Changing that means widening the event, not the routes.
2. **Unclaimed resolves authorized** — animal theft of claim-less junk
   records nothing and alerts nobody. Feature, not bug, but it means tests
   must use claimed items.
3. **Same-faction Commons is authorized**: a colony pet cannot steal from
   the clan; Route 1 is only visible against guests/visitors until the
   settlement loop lands.
4. **Trainables.xml warns** that DefMap-saved trainability data is
   order-sensitive; `RM_Steal` is append-only via mod XML (standard, but the
   save-compat note belongs in the def's comment).

## Verification (quicktest-shaped, minimal list)

| Route | PROVE | EXPECT | LIES |
|---|---|---|---|
| Trained pet | debug-complete `RM_Steal` on a marked pet; spawn guest pawn + item claimed to them; force job | ledger holds `Stolen` record for the guest; `evt.WasAuthorized == false` | item moved but Fire never called — assert on the LEDGER, never item position; spawn tool substitutes kinds silently — verify actual race |
| Wild animal | spawn marked factionless animal + colonist-claimed item; debug-force the job | Stolen record + witness letter iff a colonist was in the rolled witness list | MTB path is untestable in 90 s — the debug action is the test; an unclaimed item proves nothing (authorized) |
| Droid loader | cold-load with Droidworks; read each target race's live modExtensions; float-menu a non-player building | `TheftHaulerExtension` present on every designated chassis; Strip event on uninstall finish | `PatchOperationFindMod` is true-on-no-match — a wrong defName is a SILENT no-op; check the live def, not the patch log |
| Negative | unmarked pet at Advanced trainability; unmarked wild animal | no steal trainable offered; no theft job ever generated | absence needs the gate asserted in selftest, not "didn't see it happen" in one quicktest |

## Open questions for the owner

1. Trainability gate: Advanced + Obedience prerequisite acceptable, or should
   "agile" pets get it at Intermediate (making it cheaper than Haul)?
2. Which Ash'karr species: give me your list, or should I draft a candidate
   roster from the live animal dump (small body, high moveSpeed) for a card?
3. Is pet-theft heat landing on the ANIMAL (constraint 1) fine for v1, or do
   you want a `Principal` field on TakingEvent now so the clan answers for it?
4. Wild thieves: player colony only, or symmetric (they also rob settlements
   and guests wherever they roam)?
5. Which Droidworks chassis count as "loaders" besides the Muckraker?
6. Autonomous stealing (trained-Haul idiom, no direct orders) acceptable for
   v1, or is a master-directed order the actual ask?

## Ruling on open question 3 — owner, 2026-09-09 (verbatim)
"The pet for the theft, but seeing the player click on the pet to issue
the command gives heat to the colony."
→ TakingEvent stays single-actor (the pet) for the taking itself; a
SEPARATE witness check fires at ORDER-ISSUE time — a witness who sees
the command moment attributes suspicion to the colony, not the animal.
Two witnessable moments, two different attribution targets. No Principal
field needed in v1.
