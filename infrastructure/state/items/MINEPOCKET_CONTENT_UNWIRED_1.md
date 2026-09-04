# MINEPOCKET_CONTENT_UNWIRED_1

Surfaced by the standing code-review sweep (`DIRTY_CODE_REVIEW_LOOP_RESTART_6`,
2026-09-03), reviewing `mandrake.rsw.armoury`'s `MinePocket` sub-feature.

## What's true

`src/RimStarWars/Armoury/Source/MinePocket/Verb_ShootMine.cs` and
`Projectile_SpawnMine.cs` are code-correct — verified near-verbatim matches
of vanilla's own `Verb_LaunchProjectileStaticOneUse`/`Projectile_SpawnsThing`
idioms against decompiled RimWorld source. `CompDefuse.cs` and
`MinePocketDefExtension.cs` (siblings) are the other two files in this
cluster — now independently reviewed (2026-09-03): both are code-correct
(a minimal `ThingComp` float-menu and a plain `DefModExtension` holder,
no logic bugs) but confirmed unreachable by the same test — no `ThingDef`
in the mod's XML (repo source or the deployed live copy) adds `CompDefuse`
as a comp or `MinePocketDefExtension` as a modExtension. Left DIRTY in
`CODE_REVIEW_STATUS.json` on purpose, matching their siblings.

**Zero XML anywhere in the mod references any of the four**: no weapon's
`verbClass` is `Verb_ShootMine`, no `ProjectileDef`'s `thingClass` is
`Projectile_SpawnMine`, no `ThingDef` adds `CompDefuse` or the def
extension. Checked via repo-wide grep and `mcp__rimsage__search_source`/
`search_defs` — no hits. All four compile into the live `JawaArmoury.dll`
and are reachable from managed code (so not literal dead files), but
inert — the "throw a mine, it lands, someone can defuse it" feature does
not exist in the running game.

Only `MinePocketJob.cs` (via the `MinePocket_Job` JobDef's `driverClass`)
and `MineDefOfs.cs`'s `TrapIED_HighExplosive`/`MinePocket_Job` references
are actually wired to anything — a different, narrower mechanism than
"shoot a mine".

A ledger note (`WEAPONS_ABSORPTION_WAVE_1`) says these classes were
"found load-bearing by a sweep," but whatever Def was meant to carry them
never landed in `Absorbed_KotorCore` (or anywhere else).

## spec

Not yet written — this item exists to hold the finding, not to prescribe
the fix. Two legitimate outcomes:
- Wire `Verb_ShootMine`/`Projectile_SpawnMine`/`CompDefuse`/
  `MinePocketDefExtension` to a real weapon/trap ThingDef, restoring the
  feature the C# was built for.
- Or confirm it's abandoned in favor of the narrower `MinePocket_Job`
  mechanism and file these four as a DEAD-FILE removal.

## verify

Whichever route: after the change, re-run the reachability grep above and
confirm either (a) a real XML reference now exists, or (b) the four files
are gone and nothing else references them.

## criteria

Not ruled. Needs an owner or BENCH call on which mechanism ships — this
is a design question, not a bug fix.
