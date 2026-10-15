# Gimme Some Slack (GSS) — release-push context for a pre-release source read (2026-10-15)

Written by BENCH for the GPT consult. Facts below were read from the repo this morning; paths are repo-relative.

## What the mod is

`mandrake.rm.gimmesomeslack`, RimWorld 1.6, C# + Harmony (shared `PatchApplier` wraps every Harmony patch so one
failing patch logs and is skipped rather than killing the mod). All five DLCs are always loaded (a project ruling:
every DLC is assumed, there is no DLC-less path). It ships in a ~22-mod pilot tier and on the owner's full ~500-mod list.

Two halves, one Mod Settings entry with two tabs:

1. **Cables (cosmetic only).** Vanilla conduit is made invisible but keeps working exactly as vanilla. A cosmetic
   layer reduces the conduit network to a NODAL graph (generators, batteries, machines, junctions, places the
   conduit dives into a wall/rock and emerges) and draws loose, over-long, slack "extension cords" between connected
   neighbours over walkable floor: never across a wall, never joining two things that are not really connected.
   A conduit end on a powered net sparks; a dead end lies limp. Dense conduit grids read as a tangle with power
   strips. **Nothing of the cables is saved** — the graph is rebuilt from the map; adding/removing the mod
   mid-game is meant to be safe for them. Code: `Source/Core/*`, `CordWorldAdapter.cs`,
   `RM_MapComponent_CordGraph.cs`, `SectionLayer_RM_MessyCords.cs`, `CordMaterials.cs`, `ConduitVisuals.cs`,
   shared geometry `src/RimMandrake/_Shared/SlackGeometry/*`.
2. **Overhead lines (real buildings, saved).** Masts, lamp masts and wall brackets (`Defs/Aerial/RM_AerialAnchors.xml`)
   carry REAL power over open ground on sagging wires that sway; wires may pass over roofed rooms. Spans are saved
   links (`RM_MapComponent_Aerial`, `CompAerialAnchor`). A cut/orphaned wire hangs to the ground and sparks while
   live; explosions and roof collapse can cut a wire; a wire-down alert lists them. Live fallen wires shock pawns
   (knock-out + knockback; a weak heart dies of a heart attack) and can ignite fuel puddles
   (`RM_FallenWireShock.cs`). A power-tap clamp (`CompPowerTap`) drains another faction's grid into ours one-way
   without merging nets; being seen stealing costs goodwill (owner card 2026-10-11: 2 goodwill/day, 12-cell notice;
   `PowerTheftConsequences.cs`). Pole owner change coils wires to other owners' poles (`OwnerMismatchSweep`, every
   250 ticks). Lamp masts should register light like vanilla wall lights (owner card 2026-10-11).
3. **Styles.** Four looks — Scrapper, Industrial, Modern, Futuristic — picked per build on the build button
   (Mod Settings sets the default). A connected conduit RUN has exactly one style (owner: "a single connected run of
   conduit no matter how large would be a single art style"); bridging two runs: the largest wins; splitting keeps
   styles; lamps can "match their cable run". Code: `Aerial/ConduitStyles.cs`, `ConduitStylePicker.cs`,
   `RM_MapComponent_ConduitRuns.cs`, `AerialStyles.cs`, `StylePicker.cs`, `_Shared/StylePicker/StylePickerCore.cs`,
   Ideology-style `ThingStyleDef`s in `Defs/Aerial/RM_ConduitStyles.xml`, `RM_AerialStyles.xml`,
   `Patches/RM_ConduitStyleable.xml`.
4. **Settings.** `AerialSettings.cs` + `GimmeSomeSlackMod.cs` + the shared SettingsKit (master switches grey their
   dependents; Reset-all). Owner rule: every behaviour has a switch, defaults = shipped behaviour, every master off
   brings vanilla art back at once, all-off degrades gracefully.
5. **Probes.** `GimmeSomeSlackProbe.cs`, `StyleProbe.cs`, `AerialProbe.cs`, `StyleProbeAerial.cs`,
   `ConduitStyleProbe.cs` are bridge-callable read/act verbs used by the live harness. They ship in the DLL.

**Hoses moved to FlowWorks** (2026-10-10/11). Anything hose-shaped is out of scope here; say so if you see residue.

## Design intent (owner's words; the north star)

The `## north star` section of `design/validation_walks/RimMandrake/GimmeSomeSlack.md` (inlined) is the owner's
statement of what a player must see. Key bars: conduit reads invisible; cords lie slack in loops, never taut;
cord meets a wall at its face; never a cord across impassable cells; dense grid reads as a tangle; a break's live
and dead ends differ; overhead span drawn above everything; a downed span lies on the ground; four styles are
distinguishable; one run = one style. Motion has no bar by ruling.

## Known behaviours and history (do not re-report these unless the fix is wrong or incomplete)

- `design/RimMandrake/gss_gpt_source_read_2026-10-06.md` (inlined) — the previous GPT read: 35 findings, 31
  confirmed, and the list of what was fixed (B*, A*) and what was deliberately not changed (A3 unseeded Rand in
  preview/sparks; A7 unroutable cords still drawn; A16 grouped gizmos; A14 latch; A9/A11 render paths).
  **Please check that the listed fixes are actually present and correct in the current code** — a regression
  there is a valuable finding.
- Items since then (all built): `TAP_CONSERVATION_SELFTEST_1` (multi-tick tap conservation; probe read must not
  call `ProcessPending`), `WIRE_DOWN_ALERT_1`, `POLE_OWNER_CHANGE_DROPS_WIRES_1` (OwnerMismatchSweep; no live check
  run yet), `FALLEN_WIRE_SHOCK_1` (open: live criteria A2-A5 unrun), `POWER_THEFT_BUILD_SLOW_GOODWILL_LEAK` (open),
  `TAPCLAMP_REDRAW_BITES_DOWN_AT_LAST` (open, art), `SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST` (open, live L1 owed).
- Live status 2026-10-15: `proof_all.py --live` (one session, one fresh quicktest map; cords, matrix scenes,
  aerial, styles, save/load rows SL1-SL4) passes 110/110 repeatedly on fresh maps (rounds r5, r7, r8 of 2026-10-14/15). Every
  failure in those rounds was test-environment noise (hostile mechs, hives, fleshbeasts woken by unfog), not GSS.
  So whatever is still wrong is NOT on the proven path: it lives in reloads, multiple maps, map removal, other
  mods, long play, settings changes, odd geometry, and edge timing.
- UNMEASURED live: settings Reset-all, the spark settings, fallen-wire shock (A2-A5), owner-change sweep (L2).

## A bug class that just bit us (lesson 20261015T025544Z, 2026-10-14)

"A static (session-wide) table keyed by thing/pawn IDs breaks across fixture reloads: a reload hands out the same
IDs at the same tick, so 'already handled' entries from an earlier map refuse the new one. Bit twice on
2026-10-14 (Pyrelands burrow nudge, scorchfruit roll). Key such tables per map (MapComponent) or clear them on
load." — Our test harness reloads saves and creates/destroys quicktest maps many times per session, and players
reload to an earlier save constantly. Static caches keyed by thingIDNumber, map index, Map reference, cell, or
tick are therefore suspects; so are static Material/mesh caches and "once" latches.

## How we debug RimWorld (summary; `design/RimMandrake/debug_process.md` inlined)

- Every mod has a functional script (`validation.py`, `northstar/proof_all.py`) and is debugged THROUGH it: a
  finding becomes a row that fails first, then passes.
- Offline tier: Verse-free C# selftests (`Source/SelfTest/*`, a fuzz `GssFuzz.cs` over ~43k random worlds), XML
  validation, art sanity. Live tier: a bridge (RimBridge GABP + our JawaBench companion DLL) drives a running game:
  spawn things, step ticks, call the mod's probe verbs, read state, save/load, screenshot. Evidence is a probe
  read or a Player.log line, never a screenshot alone.
- A quicktest map costs ~90 s; a cold load of the full list ~15-25 min, so a suggested live check should be one
  quicktest + bridge reads, and offline checks are preferred where they can decide.
- `MayRequire` on a top-level patch Operation is ignored; a patch that matches nothing logs nothing; `Plant`
  only ticks TickLong. (`project-engine-facts.md` inlined.)
- Instruments that lie (`instrument_traps.md` inlined): a round/zero count is a query bug until a sanity probe
  proves the instrument can see.
