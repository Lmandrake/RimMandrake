## spec
Full ruling: `design/Jawa/wrecked_machines_resurrection.md` (owner, 2026-08-31,
verbatim: *"Maybe they steal big things from colonies to have them, using
powerful, strong droids to do so. A hauler droid that can steal buildings is a
fantastic idea! Use that too."*). Canon: `canon.yml` `wrecked_machines`
(`building-theft via a Droidworks heavy hauler emitting ownership-fabric
TakingEvents`).

Build a heavy Droidworks-chassis pawn whose job is uninstalling a building it
does not own and carrying it off-map (or back to the colony), firing the
ownership fabric's TakingEvent through `RimMandrake.Property.PropertyEngine`
exactly like any other theft — per `ownership_settlement_spec.md`'s module
boundary table: **verbs emit TakingEvents and read AccessPolicy; they must
not know perception outcomes** (no peeking at witness rolls, no UI telegraph).

Scope for this pass:
1. **The pawnkind**: reuse an existing Droidworks heavy chassis race (check
   `src/RimStarWars/Droidworks/Defs/` for a suitable `DW_Race_*` — do not
   invent a new race unless nothing fits; this is a JOB capability, not
   necessarily a new body).
2. **The job**: a WorkGiver/JobDriver that lets this pawnkind target ANY
   `Building` (not gated by the vanilla "can this colonist deconstruct this"
   permission check, since the whole point is taking something NOT yours) —
   uninstall it to a `MinifiedThing` (reuse vanilla's own
   `GenConstruct`/uninstall machinery, do not reimplement it), then haul the
   minified building.
3. **The ownership hook**: at the moment of uninstall (not at haul-pickup —
   the theft act itself is detaching it from its owner), fire
   `PropertyEngine.Fire(new TakingEvent { Act = TakingAct.Strip, Thing = ...,
   Actor = ... })` against the building. Read the existing `TakingEvent`/
   `TakingAct` shape in `src/RimMandrake/Property/Source/` before adding
   anything — do not add new acts or fields to the fabric itself.
4. **Gating**: only fires the theft act (and thus only allowed) when the
   building is NOT the actor's own claim (check via
   `ClaimEngine.ResolveClaim`, same pattern `PropertyEngine.IsAuthorized`
   already uses) — a droid uninstalling ITS OWN colony's building is just
   ordinary deconstruction/reinstall, not theft, and must not fire a
   TakingEvent.

Explicitly OUT of this pass: new droid art/chassis (reuse existing
Droidworks assets), any change to `RM_Property`'s claim math, settlement/
district integration (that is `SETTLEMENT_VISIT_LOOP_1`'s territory), and any
UI/telegraph of the theft succeeding or failing perception (perception stays
fully hidden per the fabric's own rule).

## verify
- `validate_patch.py` clean against the live mod set.
- Compiles clean (new C# job/workgiver + the PropertyEngine call site).
- `Def.ConfigErrors()` triage on the next live cold load (grep
  `^Config error in`), same discipline as fire ecology/weather suite tonight.
- Live-quicktest-observed: a droid of the target pawnkind uninstalls a
  building it does not own, the building becomes a haulable MinifiedThing,
  and a `ClaimRecord` with `ClaimBasis.Stolen` appears against the prior
  owner in the ledger (readable via whatever debug/inspect surface
  `RM_Property` exposes, or a temporary debug log line if it exposes none
  yet). Confirm the SAME droid uninstalling ITS OWN faction's building does
  NOT produce a Stolen record.

## criteria
A correct v1: the droid can strip an unowned building off a map into a
haulable MinifiedThing using vanilla's own uninstall mechanics, and exactly
one `TakingEvent(Act=Strip)` fires through `PropertyEngine` per theft,
correctly gated on ownership. No new art, no settlement integration, no
change to the fabric's own event/claim shape.
