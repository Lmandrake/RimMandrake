## 2026-09-02 (FOUNDRY) — correcting the record: this was ALREADY BUILT, 2026-09-01

Claimed this off the queue believing it unstarted (the item file below carried
no build note, and neither did a fork's triage of the whole offline backlog —
both were fooled by the same gap). **It is not unstarted**: commit `3dfea85e`
(2026-09-01) built the full v1 under `src/RimMandrake/TheftHauler/` and just
never wrote it up here. Read the source before doing anything further, per
this session's own hard lesson about re-deriving what already exists — my own
independent design analysis (Fire()'s built-in authorization gate makes a
redundant own-claim check dead weight, reuse JobDriver_RemoveBuilding rather
than JobDriver_Uninstall to skip the player-Designation requirement, fire
against the pre-minify Building so the ledger's Thing-keyed dictionary still
resolves post-wrap) converged on exactly what's already there — a second,
independent confirmation the shape is right, not a critique of it.

**What's actually built** (`src/RimMandrake/TheftHauler/`, packageId
`mandrake.rm.theft_hauler`): `RM_TheftHaulUninstall` JobDef backing
`JobDriver_TheftHaulUninstall` (subclasses vanilla `JobDriver_RemoveBuilding`,
`Designation => null` so no player-placed Uninstall designation is needed —
deliberately avoids `Designator_Uninstall` because its `DesignateThing`
force-`SetFaction(Player)`s the target before the job starts, which would
erase the "not yours" fact this item exists to check); a
`FloatMenuOptionProvider_TheftHaulUninstall` right-click order (deliberate
choice over an automatic WorkGiver — a WorkGiver_Scanner would have the AI
freely target the player's OWN buildings too, wrong default for a strategic
heist); `TheftHaulerExtension` marker DefModExtension (no fields — carry-
weight-scales-with-chassis is explicitly deferred); one `MayRequire`-gated
patch marking Droidworks' Muckraker Crab Droid
(`RSW_DW_Race_OuterRim_MuckrakerDroid`, largest concrete Droidworks chassis,
`baseBodySize 1.2`) as the reused heavy hauler, per the item's own "reuse an
existing chassis" instruction. `FinishedRemoving` fires
`PropertyEngine.Fire(new TakingEvent(building, ..., TakingAct.Strip, ...))`
**unconditionally** — `Fire()` already resolves the prior claim and
authorization itself and is a documented no-op (no Stolen record, no
perception roll) for an own-claim/unclaimed building, so a droid stripping
its own colony's building stays silent ordinary deconstruction, matching this
item's own "must not fire a TakingEvent [for theft purposes]" gating
requirement without a second, drift-prone copy of that test in the job code.

**Re-verified this pass, not just re-read**:
- `dotnet build RM_TheftHauler.csproj -c Release` — clean, 0 warnings/errors.
- `deploy_custom_mods.py --mod TheftHauler --apply` — only the rebuilt DLL had
  drifted (fresh timestamp/MVID from today's rebuild, not a content change);
  now VERIFIED in sync. Everything else (About/Defs/Patches) was already
  deployed from the original build.
- `validate_patch.py` against the live 592-mod dump (`--defs` Data + Mods +
  Workshop roots) — **0 errors, 1 advisory warning** (the tool's own
  known-benign "target node not found in on-disk Defs, probably created by
  another mod's patch at runtime" shape for the Muckraker xpath — expected,
  matches the tool's own documented advisory case).
- **`mandrake.rsw.droidworks` is NOT in the live 592-mod `ModsConfig.xml`**
  (checked directly) — so the Muckraker patch is currently a true no-op (as
  designed, `MayRequire`-gated) and nothing on this mod list currently carries
  `TheftHaulerExtension`. The feature is present and inert, not broken; same
  situation `DROID_SYSTEM_BUILD_1`'s own notes describe for Droidworks itself.
- `mandrake.rm.theft_hauler`, `mandrake.rm.property`, `mandrake.rm.salvageclaim`
  ARE active on the live list already.

**Not done, unchanged from the original build**: live-quicktest proof (needs
a Droidworks-enabled session — bridge is with BENCH/the owner tonight chasing
`COLD_LOAD_STALL_INTERMITTENT_1`, so this stays offline-only for now). Left
`doing`, not closed — matches how every other "offline-done, live-owed" item
in this queue is being carried tonight (`DROID_KOTORDROIDS_PORT_WAVE1_1`,
`SANDWORM_MYTHOS_BUILD_1`, `RIVER_STEAM_ANIMATION_1`).

**Process note, worth surfacing**: this is the second time tonight FOUNDRY
nearly re-built something already done because the git log told the truth
and the item file didn't. A `rimflow`-side gap, not a one-off mistake —
worth a queue item of its own (filed separately) rather than trusted to
memory alone.

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
