<!-- status: evidence + decision menu — CAI_FOG_DEEP_DIVE_1, BENCH 2026-08-31.
     Owner's brief, verbatim: "We had already been wanting to pull in the cai fog of war. That mod
     needs full exploration. It promised much improved pawn combat experiences and real fog of war.
     Go ahead and do a deep dive now both for general gameplay as well as wrt underwater needs.
     It's a big integration so be thorough." Three-domain fan-out: disk (both DLLs strings + settings
     keys), source (GitHub repos read), field reports (Steam 429'd — those rows marked UNCERTAIN). -->
# CAI 5000 fog-of-war deep dive

## What is true, measured

**On this disk, both subscribed, both INACTIVE:** `[1.6] CAI 5000 (continued)`
(workshop 3673768803, packageId `Krkr.rule56` — same id as the original, so it
REPLACES it) and `(NWN) Real Fog of War (Continued)` (3391128917).

### CAI 5000 — what it is
- One 459 KB assembly carrying both the combat AI and a from-scratch FoW:
  `SightTracker`/`SightGrid` (bucketed async updates), LOS by **priority-queue
  flood fill** (`CellFlooder`, the "extremely fast" part — no per-tick
  raycasts), fog rendered by its own bundled shader in 16×16 sections.
- **FoW has a master toggle independent of the AI toggles**
  (`FogOfWar.Enable`), plus direct levers: `FogOfWar_RangeMultiplier`,
  `RangeFadeMultiplier`, density, per-source reveal (allies/animals/turrets),
  home-map fog off, indoor-rooms-never-fogged, and a
  write-to-vanilla-unexplored mode. Switchably separable, not architecturally
  separable.
- 1.6 fork splices into vanilla fog via Harmony (`FogGrid.IsFogged`,
  `FloodFillerFog.FloodUnfog`) and exposes thread-local
  `PushSuppressAllFog/PushSuppressCAIFogOnly` — a real per-map override hook.
- **Pawn sight radius in the read source has NO light term**: melee/shooting
  skill and verb range, clamped ~4–19 cells; fog-reveal radius scales by
  capacities and rest, still lightless. The one glow-aware primitive is
  `CompProperties_Sighter` (`radius`, `radiusNight`, `powered`, `mannable`) —
  a fixed-radius reveal source XML-attachable to a BUILDING, day/night lerped
  by sky glow.
- ⚠️ **UNRESOLVED, and it decides the underwater answer:** the 1.6 fork's
  compiled DLL contains glow-sight machinery the read source does not explain —
  `BuildSightGlowCoeffLut`, `GetSightGlowBucket`, `GroundGlowAt`,
  `GetNightVisionEfficiency`. Either the fork added per-cell glow-driven sight
  (the lamp-cone for free) or those strings serve fog rendering only. The
  fork's own source is at `yuganxia/CAI-5000-continue` (GitHub, confirmed) —
  one targeted read settles it. Do not state either version as fact until then.

### The license reality 🔴
**Neither CAI repo has any license** (`kbatbouta/CAI-5000` frozen at 1.4;
`yuganxia/CAI-5000-continue` for 1.6) — all rights reserved by default, so
**absorbing CAI code into a mod we own is not authorized**. Enabling it as a
mod-list member, patching it at runtime via Harmony, and reading it for
understanding are all fine; copying is not.
**NWN Real Fog of War is Apache-2.0 at BOTH ends of its lineage**
(`lukakama/rimworld-mod-real-fow` original, `emipa606/NWNRealFogOfWar`
continued) — the only legally absorbable FoW base in existence.

### NWN Real FoW — the rival, measured
FoW-only, per-FACTION shared vision, glow/night-aware (`GroundGlowAt`,
`NightVisionEffectiveness`, `denyDarkness`), base-view-range and per-source
vision multipliers exposed as settings, **explicitly gravship-aware** (clears
fog during takeoff/landing-site selection), ships camera/watchtower
vision-extender buildings, 96 KB assembly. Its own About.xml states it
coexists with CAI **only if CAI's fog is off** — the two fog engines collide
by default.

### Field-report risks (Steam pages 429'd; UNCERTAIN except the GitHub issues)
Open issues on the original repo, CONFIRMED: SightGrid null-ref spam in
battle (#90), incompatible with Search and Destroy (#86), breaks SOS2 shuttle
control (#94, we don't run SOS2). UNCERTAIN but repeated: turrets not driven
by the AI layer; a heavy-modlist performance complaint pattern; fork
provenance/cadence unverified. Anomaly/Odyssey coverage of the AI is
undocumented anywhere; the fork's changelog snippet claims gravship-preview
and pocket-map fixes (unverified).

## The decision — three viable routes

| route | what it buys | what it costs |
|---|---|---|
| **A. Enable CAI whole (AI + its fog)** | the owner's original want: smarter combat AND real fog, one mod, fastest engine | fog+AI coupled; turret-AI gap; unlicensed → forever a dependency, never ours; Odyssey behavior unproven |
| **B. CAI combat AI + NWN fog** (CAI fog toggled off — the documented-compatible combo) | best AI + a gravship-aware, glow-aware, Apache-licensed fog | two systemic mods to shepherd; NWN's per-faction model is simpler/slower than CAI's grid |
| **C. NWN lineage as the base we absorb** (no CAI, or CAI later) | the only route to fog code WE OWN — and it already speaks glow/night, which is the underwater mechanic | gives up CAI's combat AI and its fast flood-fill engine |

**For the underwater lamp-cone specifically:** every route needs one small
piece from us — either `CompProperties_Sighter` on the dive lamps (XML, route
A/B) plus a glow clamp on pawn sight for the seafloor maps (a Harmony patch in
our companion DLL — legal against any route), or NWN's glow model absorbed and
retuned (route C). The unresolved fork glow-LUT question above may make route
A/B's clamp unnecessary — check first.

## Next steps, in order
1. Read `yuganxia/CAI-5000-continue`'s 1.6 sight source — settle the glow-LUT
   question (one subagent, no game).
2. Grep our ModsConfig for Search-and-Destroy-class AI mods before any enable.
3. Minimal-list quicktest (22 s cycle): enable per the chosen route, spawn a
   night raid, LOOK at fog behavior + a `Sighter`-comp lamp; then a full-list
   trial ride on an existing cold-load run sheet — never its own load.
4. Fold the verdict into `depths_build_spec_v1.md` §0.2 (currently pointing
   here).
