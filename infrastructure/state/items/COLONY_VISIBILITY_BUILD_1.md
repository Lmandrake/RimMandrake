# COLONY_VISIBILITY_BUILD_1

## spec

`design/Jawa/worldbuilding/colony_visibility_stat.md`, specifically
Annex A (BENCH merge, 2026-08-30) and the owner's 2026-08-31 ruling
closing it: "THREAT-SCOPED patching. The global-vs-threat-scoped fork is
closed: the Postfix replaces threat points for HOSTILE events only.
Quest budgets, herd sizing and friendly arrivals stay on vanilla wealth
scaling." Filed as the successor to `COLONY_VISIBILITY_STAT_1` (closed
2026-08-30), which built a safe core + one narrow raid-point call site
and explicitly left the dominant raid path and the mod's home as open
questions.

## What this pass did

**Rehomed** the safe-core `GameComponent_ColonyVisibility` (state vector,
band ladder, `Adjust()`, `ExposeData`) from `mandrake.rut.doctrine` into
its own dedicated mod, `mandrake.rm.visibility`
(`src/RimMandrake/Visibility/`) — the packageId the item's own title
names. `mandrake.jawadoctrine.core`'s bootstrap no longer calls the old
patch; the two superseded files (`ColonyVisibility.cs`,
`ColonyVisibilityRaidPatch.cs`) are deleted from Doctrine, which still
builds clean (0 errors/warnings) without them.

**Replaced the raid-point technique entirely**, per Annex A's simpler
formula (`points ×= VisibilityToThreatCurve(vis)` — a straight
multiplier, superseding STAT_1's more complex "reimplement vanilla's
pawn-power term, replace only the wealth term" approach, which needed no
reimplementation once the formula is multiplicative rather than
substitutive):

- **Verified from scratch, not assumed** (a fresh RimSage research pass):
  `IncidentCategoryDef` carries no hostility flag, and category-based
  filtering is **provably wrong** — `ProblemCauser`
  (`Defs/Royalty/IncidentDefs/Incidents_Map_Misc.xml`) is a quest-giving
  incident tagged `category>ThreatBig`, and `ThrumboPasses`/
  `HerdMigration` (both `category=Misc`) also carry
  `needsParmsPoints=true` despite being named as explicitly out of scope.
  No `incCat` filter at `DefaultParmsNow`/`GenerateParms` separates these
  correctly — confirmed with concrete counterexamples, not left as a
  hedge.
- **The reliable choke point**: a Harmony **Prefix on
  `IncidentWorker.TryExecute(IncidentParms parms)`**
  (`Source/RimWorld/IncidentWorker.cs:183`), gated on the CONCRETE worker
  type (`IncidentWorker_RaidEnemy`, `IncidentWorker_Infestation`,
  `IncidentWorker_AggressiveAnimals` for manhunter packs,
  `IncidentWorker_MechCluster`) rather than any category heuristic.
  `IncidentParms` is a class, so mutating `parms.points` in the Prefix
  changes what the real worker body consumes.
- **This single Prefix also covers `TimedDetectionRaids`** (it
  constructs and fires an `IncidentWorker_RaidEnemy` the same way any
  other raid does), so STAT_1's separate call-site transpiler for that
  one path is no longer needed — one mechanism now covers both the
  dominant storyteller-raid path STAT_1 could never reach AND the one
  path it had already gotten working.
- Ta'Baa's launch-reset Postfix on `GravshipUtility.GenerateGravship`
  carried over unchanged (STAT_1's own work — real, verified, no reason
  to redo it).
- Builds clean (0 warnings, 0 errors) for both `mandrake.rm.visibility`
  and the trimmed `mandrake.rut.doctrine`.

## Deploy state

`mandrake.rm.visibility` deployed clean, added to `ModsConfig.xml` after
`mandrake.rm.ninefold`. `mandrake.rut.doctrine`'s redeploy **failed** —
the game is up this session and has its old DLL locked
(`OSError: [Errno 22] Invalid argument`, not a corruption, just a
Windows file-lock on write). `deploy_custom_mods.py --mod Doctrine
--apply` re-run cleanly redeploys it once the game is down; confirmed
via a dry-run plan (`Drift found`, one file, `~ Assemblies/
JawaDoctrineCore.dll`) that nothing else needs touching.

## Not done — explicitly, not silently

- `VisibilityToThreatCurve`'s five anchor points are Annex A's own
  "first-guess," not tuned — §5's own tuning protocol (throwaway-save
  rig, measure at Visibility ∈ {0,25,50,75,100} × 3 wealth bands, 10
  samples each) has not been run.
- Every OTHER raise/lower hook in the design doc's §2 table (spotted/
  raided at home, challenge broadcasts, Renown, THE SHAMING, Overcurrent,
  melee fighting, flare-lighting, ambush kills, undetected-raid
  survival, concealed construction, darkness, blackout reign, Unseen
  Berth, the Unburdening rite) is still not wired to anything —
  `Adjust()` is ready, nothing calls it yet.
- Sh'kaar's escalation multiplier seam exists (`ShkaarEscalationMultiplier`,
  default 1f) but nothing sets it.
- F17's interface layer (reign-calendar clause, band-crossing letters,
  inspect tag) is not built.
- Tile-memory decay (owner card, 2026-08-31: "the desert remembers,
  decaying — a returned-to tile restores a decayed fraction of its old
  Visibility, halved per season away, TUNE") is not modeled — the
  GameComponent tracks one ship-wide value with no per-tile memory yet.
- No live proof this Prefix actually fires and multiplies correctly —
  needs a quicktest with a spawned hostile incident, owed to the next
  restart.

Left `doing`.
