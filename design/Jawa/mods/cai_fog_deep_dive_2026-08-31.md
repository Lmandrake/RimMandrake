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
- ✅ **SETTLED (fork source read, `yuganxia/CAI-5000-continue` @ `1769e8d`):
  pawn sight in CAI is NEVER glow-driven — RENDER-ONLY / SIGHTER-ONLY.**
  `GetSightRadius_Pawn`/`GetFogRadius` use skills, verb range and capacities
  with no glow term anywhere; per-cell GlowGrid appears only in
  `MapComponent_FogGrid` as a *rendering* layer (re-fogging explored-but-dark
  cells — visually useful for the deep, but not sight); `radiusNight` is the
  Sighter comp's global sky-glow day/night lerp. ⇒ **The lamp-cone under any
  CAI route costs us one small Harmony clamp on the two pawn formulas, scoped
  to seafloor maps, in our own companion DLL** (legal — runtime patching, not
  absorption), plus `CompProperties_Sighter` on lamp buildings.
  📌 *Correction kept visible:* an earlier disk-strings pass attributed
  `BuildSightGlowCoeffLut`/`GetSightGlowBucket`/`GetNightVisionEfficiency` to
  the fork DLL; the source read found none of the three in the repo, its full
  git history, or strings of its shipped DLL (`GroundGlowAt` is vanilla API the
  fork never calls). Either the installed workshop DLL is not built from this
  repo (provenance already flagged) or the strings pass misgrouped symbols —
  do not design against those three names.

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

## The decision — 🔴 RULED by the owner, 2026-08-31 (question cards)

**Route B: CAI combat AI + NWN fog (CAI's own fog toggled OFF), and
`memegoddess.searchanddestroy` is DROPPED** — CAI's combat AI supersedes what
S&D bolts on. Integration work: `FOW_ROUTE_B_INTEGRATION_1`. The S&D drop also
lands in the outgrown-mod audit as a settled retire.

The menu as it was put to him:

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

🔴 **Conflict confirmed in OUR list (measured 2026-08-31):**
`memegoddess.searchanddestroy` is ACTIVE — the exact mod in CAI's open
incompatibility issue #86. Routes A and B (anything enabling CAI's combat AI)
require dropping Search and Destroy or accepting a documented conflict; route C
is unaffected. This is a ruling the route decision must carry.

## Next steps, in order
1. ~~Read `yuganxia/CAI-5000-continue`'s 1.6 sight source~~ — done, see the
   ✅ SETTLED note above.
2. ~~Grep our ModsConfig for Search-and-Destroy-class AI mods~~ — done, see
   the red flag above.
3. ✅ **Minimal-list quicktest — done, `FOW_ROUTE_B_INTEGRATION_1`,
   2026-08-31.** `Krkr.rule56` + `Mlie.NWNRealFogOfWar` enabled on the 21-mod
   FoW test list (minimal + both, ordered right after the DLCs, before
   content mods — satisfies CAI's `loadAfter Ludeon.RimWorld[.Royalty]`),
   `memegoddess.searchanddestroy` dropped. CAI's own fog toggle
   (`FogOfWar_Enabled.15` in `Mod_3673768803_CombatAIMod.xml`, absent from a
   default-settings dump so inferred from the DLL's own string table — not
   confirmed against a Scribe read-back) set `False`. Two clean cold boots,
   zero CAI/NWN/Krkr exceptions in `Player.log` either time.
   - **Fog visuals**: confirmed by screenshot — NWN's own "Not visible area"
     overlay renders (a smooth diagonal front, not CAI's 16×16 blocky
     shader), consistent with CAI's fog engine being off and NWN driving.
   - **Combat AI**: 3 debug-spawned Pirates pathed ~9 tiles toward the
     colony over 2000 stepped ticks with no CAI errors — the AI is active
     and driving hostiles. `jawa/fire_raid` itself produced zero arrivals on
     this quicktest world (a known bridge trap, not a Route B defect — see
     `skills/rimbridge/references/traps.md`); direct debug-spawn was used
     instead.
   - 🔴 **New finding, unresolved: `CompProperties_Sighter` (CAI's fixed-radius
     reveal comp, the one the lamp-cone plan named) did not visibly reveal
     fog around a spawned `CombatAI_TribalPoleCCTV`** with CAI's fog off.
     Two live explanations, neither ruled out: (a) the comp's reveal only
     runs through CAI's own `MapComponent_FogGrid`, which does not run when
     `FogOfWar.Enable` is false — i.e. Sighter goes inert exactly when Route
     B is active; or (b) the freshly spawned building had 0 fuel
     (`CompProperties_Refuelable`, `consumeFuelOnlyWhenUsed`) and simply
     wasn't "in use" yet. **Not chased further — `depths_build_spec_v1.md`
     §0.2 had already routed the lamp-cone through NWN's own glow model
     instead of Sighter, so this doesn't block anything; it just means
     Sighter is confirmed unproven, not confirmed working, under Route B.**
     Whoever builds the actual dive lamp should settle (a) vs (b) before
     leaning on Sighter for anything, or just build on NWN's glow model as
     already planned and skip the question.
   - Full-list ride: the owner's live 593-mod list (592 + CAI + NWN − S&D) is
     written to `ModsConfig.xml`. FOUNDRY cold-booted it to confirm before
     handoff — bridge up, zero CAI/NWN/Krkr errors, no `incompatib*` warning;
     ready for his next play session.
4. Folded into `depths_build_spec_v1.md` §0.2.
