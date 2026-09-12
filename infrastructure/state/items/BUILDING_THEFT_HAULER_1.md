## 2026-09-12 (FOUNDRY) — DLL deploy confirmed done; mechanism re-verified, nothing wrong found

Reclaimed off the queue (staleness audit said only a DLL redeploy and the
live quicktest remained). Game was mid-cold-load this whole pass — per this
session's own instruction, **no bridge calls attempted**, offline-only.

**Deploy status: already done, not by this pass.** `deploy_custom_mods.py
--mod RimProperty` (plan-only) reports "in sync (10 files)" — the DLL that
09-09's note left locked mid-load is now byte-identical between repo and the
live Mods folder (`md5sum` checked directly, both sides
`ae9875757783aab87348ecb61a7f6682`, live copy timestamped Sep 12 01:25 —
after 09-09's session, before this one). No `--apply` needed; nothing to fix
here. `needs=deploy` from the prior note is CLOSED.

**Mechanism re-verified against the actual C#, not just "compiles + matches
dump"** (this pass's own explicit instruction, since 0 config errors only
proves the def loaded, not that the job does the right thing):

- **Whole building vs partial deconstruction — correct.** Both the float
  menu gate (`FloatMenuOptionProvider_TheftHaulUninstall.GetSingleOptionFor`)
  and the debug harness require `building.def.category == Building &&
  building.def.Minifiable` before offering the job. `Minifiable` is exactly
  vanilla's own whole-object-survives-intact flag (`MinifyUtility.MakeMinified`
  refuses and logs a warning otherwise) — this can never target a plain
  deconstruct-to-rubble object, only something that comes off whole as a
  `MinifiedThing`. Matches the item's own criteria ("using vanilla's own
  uninstall mechanics"), not the broader `wrecked_machines_resurrection.md`
  vision of also cracking *normally-unminifiable* buildings via a droid-only
  gate bypass — that line is real (doc line 77-78) but is NOT in this item's
  own scope/criteria text, so treating it as a v2 gap rather than a v1 defect.
- **Carry weight math — the "no override" claim checks out.** Read
  `JobDriver_RemoveBuilding.MakeNewToils` (vanilla, via RimSage): uninstall
  work is time-gated by `uninstallWork`/`ConstructionSpeed`, not mass:
  hauling the resulting `MinifiedThing` afterward runs through vanilla's own
  `HaulToStorageJob`/carry-capacity math with no bypass needed for a heavy
  chassis to be "strong enough" — nothing in vanilla's hauling path blocks a
  pawn from picking up one heavy item regardless of body size. Confirmed
  `design/Jawa/wrecked_machines_resurrection.md` line 78 ("carry weight
  scales with chassis") is a real, already-written future-pass line, not an
  invented deferral — legitimately out of this item's v1 criteria.
- **Failure mode — sane, not stuck, not a crash.** `JobDriver_
  TheftHaulUninstall` adds no toils of its own; it inherits vanilla
  `JobDriver_RemoveBuilding`'s own `FailOnForbidden`, `FailOnDestroyedNullOrForbidden`,
  `FailOnCannotTouch`, and the live-explosive-wick check — an
  interrupted/destroyed/no-longer-reachable target fails the job cleanly via
  the same machinery `JobDriver_Uninstall` already relies on, nothing bespoke
  to get wrong. `MinifyUtility.Uninstall()` (RimSage-read) returns `null` on
  an unspawned/non-Minifiable thing and the driver's own `if (minified !=
  null)` guard means a failed uninstall just skips the haul-enqueue rather
  than NREing or queueing garbage.
- **Ownership gating — re-traced against `PropertyEngine.Fire`/`IsAuthorized`
  directly** (not just trusted from the comment): `IsAuthorized` returns true
  for the actor's own claim and for Commons-claims shared by the actor's own
  faction, false otherwise; the `Stolen` `RecordTransfer` for `Take`/`Strip`
  only fires when `!WasAuthorized`. So `Fire()` runs unconditionally (as
  designed — single source of truth) but produces no record and no
  perception roll for an own-building uninstall. Matches item criteria
  exactly.

**No bugs found, nothing fixed, no rebuild needed.** `validate_patch.py`
re-run fresh this pass against the live 592-mod dump (Data + Mods + Workshop
roots): both TheftHauler patch files, **0 errors, 0 warnings**, all 5 xpaths
(Muckraker + 4 DroidLoaders) matched live.

**Still owed, unchanged:** the live droid-theft quicktest itself (droid
uninstalls an unowned building → Stolen `ClaimRecord`; same droid on its own
faction's building → no record) — genuinely reachable now (Droidworks +
RimProperty both active on the live 592-mod list per 09-09's note, DLL now
actually deployed), but this pass's own instruction was no bridge calls
while the game is mid-cold-load. Leaving `doing`. Next session with a
confirmed-reachable bridge: run it directly against a real chassis (Muckraker
or one of the 4 DroidLoaders adds), not just the chassis-bypassing debug
action, then close per the item's own `verify` section.

## 2026-09-09 (FOUNDRY) — re-verified after the RimProperty merge; Droidworks is now LIVE

Claimed off the queue mid-restart (game rebooting twice tonight, owner's
standing authorization); bridge confirmed FREE but per this pass's own
instruction, no live bridge calls attempted — offline verification only.

**Found it further along than the 2026-09-02 note describes, again** (this
queue's recurring failure mode). The code moved: `f32eef5f` (2026-09-08)
merged `TheftHauler` into `src/RimMandrake/RimProperty/` (packageId now
`mandrake.rm.property`, not the old `mandrake.rm.theft_hauler` the last note
cites — old packageId is dead, don't grep for it). `fc173df3` (2026-09-09,
closing the separate `RIMPROPERTY_ANIMAL_THEFT_1`) added
`Patches/TheftHauler/DroidLoaders_TheftHauler.xml`, marking 4 MORE Droidworks
Labour-family chassis (`RSW_DW_Race_OuterRim_ImperialLaborDroid`, both KotOR
KM1 mining/excavation droids at `baseBodySize 1.5` — the two largest concrete
Labour bodies in Droidworks, bigger than Muckraker's 1.2 — and the baseline
GE3 labor droid) with `TheftHaulerExtension`, alongside the original Muckraker
patch. The haul-away half the 2026-09-02 note flagged as a gap is also
already built: `JobDriver_TheftHaulUninstall.FinishedRemoving` now enqueues
`HaulAIUtility.HaulToStorageJob` right after `Building.Uninstall()` so the
minified crate doesn't just sit at the building's old position — matches the
float menu's own "Steal and haul away" wording. `DebugActions_TheftHauler.cs`
(a chassis-gate-bypassing debug action to prove the `PropertyEngine.Fire`
call fires independent of Droidworks being live) is new too, dated with an
"adversarial review, 2026-09-07" comment tightening its Minifiable/Building
gate to match the float menu's exactly. All of this is spec-compliant with
`design/Jawa/wrecked_machines_resurrection.md` and this item's own scope —
no invented mechanics, nothing needing a fresh ruling.

**Re-verified this pass**:
- `dotnet build RM_Property.csproj -c Release` (via the user-local SDK at
  `C:\Users\Mandrake\.dotnet\dotnet.exe`, not the Program Files runtime-only
  install) — clean, 0 warnings/errors.
- `deploy_custom_mods.py --mod RimProperty --apply` — 6 of 7 drifted files
  deployed (today's animal-theft + `DroidLoaders_TheftHauler.xml` additions,
  `About.xml`). The DLL itself **failed to deploy — locked by the live game
  mid-cold-load**, expected and non-blocking (writes to a running mod folder
  during a load are exactly the risk the "no live bridge calls" instruction
  is guarding against elsewhere; this is a plain file-copy failing safely,
  not a live call). Owed: re-apply the DLL once this cold load finishes and
  the game is closed or between sessions.
- `validate_patch.py` against the live 587-mod dump (Data + Mods + Workshop
  roots) on both TheftHauler patch files — **0 errors, 0 warnings**, and for
  the first time all 5 xpaths (Muckraker + the 4 new DroidLoaders targets)
  **actually MATCHED** rather than reading as an inert MayRequire no-op.
- **`mandrake.rsw.droidworks` IS NOW ACTIVE** in the live `ModsConfig.xml`
  (checked directly, not inferred from the match count) — this reverses the
  2026-09-01/09-02 notes' "Droidworks not on the live list, feature present
  but inert" finding. `mandrake.rm.property` is active too. This means, once
  the current cold load reaches Playing and the bridge is confirmed
  reachable, a real droid of one of the 5 marked chassis IS present on the
  live mod list and the item's own live-quicktest criterion is finally
  testable — not blocked on a separate Droidworks-enablement decision
  anymore.
- Checked the current (mid-load) `Player.log` for config errors: 19 present,
  literal-string-checked (`MEASURE_ALLOW_SCAN=1`, exact "Config error in"
  match, not a semantic scan) — **none** name anything in `RM_FE`-adjacent...
  none name `RimProperty`, `TheftHauler`, or any of the 5 chassis defNames.
  Zero `RimMandrake.TheftHauler`/`RimMandrake.Property` hits in the log at
  all yet (load hasn't reached that point, or logged clean either way).

**Leaving `doing`, not closing.** Two things still owed, both correctly
deferred rather than invented around:
1. Re-deploy the DLL once the game frees the file (this session's cold load
   finishes or the game closes) — pure mechanics, no decision needed.
2. The live-quicktest itself (droid uninstalls an unowned building -> Stolen
   ClaimRecord; same droid on its own faction's building -> no record) —
   now genuinely reachable given Droidworks is live, but this pass's explicit
   instruction was no live bridge calls while the game is mid-cold-load.
   Next session with a confirmed-reachable bridge should run this directly
   against the real chassis (Muckraker or one of the 4 new loaders) rather
   than only the chassis-bypassing debug action.

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
