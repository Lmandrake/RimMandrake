# SHIELD_MODS_LEVERAGE_1 — particulate screen finished, predictive-failure and landing-advisory built, offline-verified only (FOUNDRY, 2026-09-12)

## Build (FOUNDRY, 2026-09-12) — resumes the 2026-09-09 slice

Game was mid-cold-load all session (RimWorldWin64.exe running, ShipShields
already deployed to the live Mods folder but **not enabled in ModsConfig**)
— bridge and world state untouched throughout, per this session's scope.
All work below is `dotnet build` compile-clean (0 warnings, 0 errors)
against the real `Assembly-CSharp.dll`/`0Harmony.dll`, plus every C#
symbol used (ToxicUtility, GameConditionDefOf, LetterDefOf, FleeUtility,
Map.Center, Pawn.BodySize, DefDatabase.GetNamedSilentFail,
Scenario.PostGravshipLanded) confirmed via RimSage source reads before
being called — nothing guessed.

1. **Particulate screen (shd:particulate-screen) — now built in full.**
   The 2026-09-09 slice only swept filth. This session added the two
   pieces the item file flagged as missing:
   - **Small-animal repulsion**: `CompShieldParticulateScreen` now scans
     wild animals (`Faction != OfPlayer`) at or below `smallAnimalMaxBodySize`
     (0.35, tunable) in radius and starts a real vanilla `FleeUtility.FleeJob`
     aimed away from the generator — the same mechanism wildlife already uses
     to flee fire or a predator, not a teleport or an invented push.
   - **Direct weather-damage negation**: read every vanilla weather/hazard
     source before building this (WeatherDef, GameCondition_ToxicFallout,
     ToxicUtility) — **vanilla has no direct-HP-damage effect for wind, ash,
     sand, smoke or rain at all** (Sandstorm only sets `accuracyMultiplier`/
     `moveSpeedMultiplier`/mood; confirmed by reading the live WeatherDef and
     every GameCondition source, not assumed). The one real, concrete match
     for "vapor, bio contamination... damage completely" is **airborne Toxic
     Fallout** (`ToxicUtility.DoAirbornePawnToxicDamage`, the `ToxicBuildup`
     hediff, plus `GameCondition_ToxicFallout.DoCellSteadyEffects`'s
     plant-kill/item-rot). Two new Harmony prefixes skip both effects for any
     pawn/cell inside an active, powered, particulate-mode screen's radius.
     Ground-pollution toxicity (`ToxicUtility.PawnToxicTickInterval`) is
     deliberately left untouched — a different, non-airborne hazard a
     particulate *screen* has no business filtering.
   - Both gated by their own Mod Settings toggles
     (`particulateAnimalRepulsionEnabled`, `particulateWeatherDamageNegationEnabled`),
     independent of the base filth-sweep toggle.
   - **Honest residual gap**: the design doc's "wind, ash, sand, smoke, rain"
     language reads as more than Toxic Fallout alone, but there is no other
     vanilla mechanism it could plausibly mean (checked, not guessed) —
     closing that gap further would mean inventing a new damage source for
     weather that currently has none, which is a design call for the owner,
     not a build gap in this comp.

2. **Predictive shield-failure alert (shd:shield-collapse-evacuate's
   evacuation-warning half) — built.** `CompShieldGenerator` now samples its
   own `currentHitPoints` every 250 ticks, projects a linear time-to-failure
   from the decline rate, and sends one `LetterDefOf.ThreatSmall` warning
   ("recommend the crew return to the hull") the first time projected
   collapse falls inside roughly an in-game hour — clearing once hit points
   recover past 60% of max so it can warn again on a second decline. Reuses
   the same `currentHitPoints` field the base `CompProjectileInterceptor`
   already drains from combat/EMP/forced collapse; no new stressor-tracking
   invented. Persisted across saves (`PostExposeData`).

3. **Landing-hazard advisory (shd:no-hard-landing-gate) — v1 slice built.**
   New `ShieldLandingAdvisory.Evaluate(Map map)`, fired from a Harmony
   postfix on `RimWorld.Scenario.PostGravshipLanded` — the hook
   `GIZKA_HOLD_HOOK_SPIKE_1` confirmed live-firing this session for every
   gravship landing. On landing, checks the map for an extreme-heat hazard
   (`OutdoorTemp >= 58`, or `HeatWave`/Odyssey's `LavaFlow` game conditions)
   and an airborne-particulate hazard (`ToxicFallout` active, or the live
   weather's `sandRate > 0` — a field check, not a guessed modded defName,
   so it also catches a modded dust-storm weather without naming it). For
   each hazard present, checks whether any `RUT_ShieldGenerator` on the map
   has the matching module unlocked, selected as current mode, and powered;
   if not, sends one non-blocking `LetterDefOf.NeutralEvent` letter naming
   what's missing. No hard block, ever — matches the ruling's "advise...
   but no more than that."
   - **Not built**: the design doc's other landing-gate half — escalating
     damage ticks for staying unshielded, and the "lava landing causes
     immediate severe damage" case. That needs a genuine per-tick
     hazard-application system hooked to hazard type and shield state,
     which is a materially larger build (own comp/GameComponent, its own
     tuning, its own live-test pass) — correctly out of scope for this
     session's remaining time, not attempted rather than half-built.

**Deploy status**: `deploy_custom_mods.py --mod ShipShields` shows drift
(the rebuilt DLL) and confirms ShipShields is **not currently enabled in
ModsConfig.xml** on this machine's live list. `RimWorldWin64.exe` was
running the entire session (mid-cold-load per this session's brief) — the
live DLL is very likely OS-locked by the running process, so no deploy was
attempted (`rimworld-deploy`'s "a companion DLL cannot be written while the
game runs"). Left `needs=deploy` for the next game-down window; enabling the
mod in ModsConfig is a separate, ceremony-gated step (`ModsConfig.xml
writes` on CHARTER's expensive list) not done here.

**Verification performed this session**: compile-only + RimSage source
verification of every new API call, as above. **Still zero live/bridge
verification of anything in this mod** — nothing has ever been spawned,
shot at, landed on, or module-installed in a running game. First live pass
(unchanged from 2026-09-09's list, plus the new mechanisms): spawn
`RUT_ShieldGenerator`, fire a fast and slow projectile at it in Bubble mode,
install both modules and confirm mode-cycling, force-drain hit points to
confirm the collapse explosion and check the predictive-failure letter
fires before it does, land a gravship on a hot/dusty map with no shield
configured to confirm the advisory letter, and verify the particulate
screen actually repels a wild animal and blocks a Toxic Fallout tick.

## Build (FOUNDRY, 2026-09-09)

## Build (FOUNDRY, 2026-09-09)

Scoping WAS complete before this session started: the owner ruled 2026-09-04
by card (`design/Jawa/canon_reintegration_plan.md` sec G.9): "bespoke
building-scale comp, NOW. The full fantasy owned immediately; the new C#
system's maintenance cost accepted. SHIELD_MODS_LEVERAGE_1 unblocked." That
ruling superseded the earlier lean toward forking VEF (this item's own
2026-09-02 source-verification had already found `CompShieldField` is a
pawn-apparel comp, not building-scale, which is WHY the owner ruled bespoke).
An `OWNER unblock` ledger event on 2026-09-04 was itself refused by the
process guard ("OWNER may not `unblock` SHIELD_MODS_LEVERAGE_1 — it belongs
to FOUNDRY") but the ruling text and its authorization stand regardless —
recorded in canon_reintegration_plan.md, not contingent on that one ledger
write.

Built this session, all under `src/RimUtinni/ShipShields/`
(`mandrake.rut.shipshields`, depends on Odyssey):

- **`RUT_ShieldGenerator`**, one building, one field active at a time,
  switched by installing a module (shd:loadout-tradeoff) instead of four
  separate buildings.
- **Bubble/kinetic field (shd:bubble-not-wall)**, default, unlocked from the
  start. `CompShieldGenerator` is a real subclass of vanilla's own
  `CompProjectileInterceptor` — the same base class Odyssey's native
  `CompGravshipShieldGenerator` uses (confirmed via rimsage source read, not
  guessed) — not a fork of any mod's engine. Forcibly draining it to 0 hit
  points fires a `GenExplosion.DoExplosion` collapse (shd:bubble-not-wall's
  "prone to overheating or even explosion when forcibly collapsed").
- **Canon-wide slow-pass-through (shd:shield-collapse-evacuate)**:
  `CompProjectileInterceptor.CheckIntercept` is a normal instance method, not
  virtual, so a Harmony prefix (`HarmonyPatches.cs`) adds a
  `projectile.def.projectile.SpeedTilesPerTick` gate — below
  `slowPassThroughSpeed` (0.3 tiles/tick default), the projectile is let
  through untouched. Scoped by `__instance is CompShieldGenerator` type
  check, so vanilla's own gravship/mech shields are untouched — extending
  this canon-wide (the owner's note reads "including the crew," i.e.
  arguably every shield) is a separate, larger call left open, not silently
  done here.
- **Thermal veil (shd:thermal-veil)**, module-gated. `CompShieldThermalVeil`
  reuses the same two primitives vanilla's own heaters/coolers are built on
  (`GenTemperature.ControlTemperatureTempChange` + `PushHeat`), applying only
  `rejectionFactor` (0.45 default) of the ideal correction each interval —
  the room still drifts toward outdoor extremes, just far more slowly,
  matching "reflect heat outward... but not nearly as badly."
- **Particulate screen (shd:particulate-screen), module-gated — PARTIAL.**
  `CompShieldParticulateScreen` only sweeps and destroys weather-deposited
  `Filth` in radius each interval. It does NOT implement small-animal
  repulsion or direct negation of wind/ash/sand/rain damage — the ruling's
  "handle... damage completely as well as repel small animals" is only
  partly built. This is the one shd: row this session did not finish.

Defs: `Buildings_ShieldGenerator` XML fields (`radius`, `hitPoints`, `color`,
`activeSound`, etc.) and the placeholder `texPath`
(`Things/Building/GravshipShieldGenerator`) are copied from vanilla's own
`GravshipShieldGenerator` ThingDef via rimsage, not guessed. The two module
items' `recipeMaker` blocks are copied from vanilla's own `Apparel_ShieldBelt`
(same bench, same work stat, same effecter/sound). Research prerequisite
`ShieldBelt` (vanilla's personal-shield research) verified via rimsage, not
invented. Real building/module art is NOT done — placeholder vanilla
textures only.

**Verification performed**: `dotnet build` against the real
`Assembly-CSharp.dll`/`0Harmony.dll` on this machine — 0 warnings, 0 errors
— plus well-formedness checks on every new XML file (caught and fixed three
files where prose inside XML comments used a bare `--`, illegal in XML
comments). This is compile-only, offline verification; there is NO live
game-load or bridge test of this session's work — the bridge was held by
another agent for an unrelated check all session, and this item's own
instructions scoped it to offline work only.

**Remaining gap, precise** (why this stays `doing`, not closed):
1. Particulate screen's small-animal repulsion and direct weather-damage
   negation (see above) — not built.
2. shd:shield-collapse-evacuate's *predictive* failure alert ("shields that
   are slowly failing due to an environmental stressor can predict and
   alert to let the crew return and leave") — not built. Only the
   slow-pass-through half of that ruling row is done.
3. shd:no-hard-landing-gate — not started. This is a separate mechanism
   (a landing-site hazard advisory), not part of the shield generator's own
   comp; it rides on the same design doc but needs its own hook into
   gravship landing, which nothing in this build touches.
4. No live verification at all: the building has never been spawned, no
   projectile has ever been fired at it, the module-install gizmo has never
   been clicked, and the Harmony patch has never been proven to actually
   fire in a running game. Compile-clean is not behavior-correct. First
   live pass should: spawn `RUT_ShieldGenerator` via the bridge, shoot both
   a fast and a slow-moving projectile at it in Bubble mode, install a
   module and confirm mode-cycling changes behavior, and force-drain its
   hit points to confirm the collapse explosion fires exactly once.

## Local ground-truth check (FOUNDRY, 2026-09-02) — BENCH's survey was WebSearch-only

Survey: research/Jawa/shield_mods_survey_2026-09-02.md. Recommended shape:
- **Foundation: VEF's shield engine** (`CompShieldField`, MIT, already in our
  stack) — energy-drain-to-EMP-explosion is exactly the ruled
  overheat/collapse behavior, XML-tunable.
- **Extend Odyssey's NATIVE gravship shield slot** rather than duplicating a
  parallel system — two workshop mods already prove that hook works.
- **Module architecture from ED-Shields** (jaxxa, MIT): projector/converter
  modules match the ruling "same shields, install modules to increase
  switching capacity/configuration".
- ⚠️ Verify before building: VFE-Security 1.6 vs native gravship shield
  compat, and VEF point-defense's "slow projectiles intercepted MORE easily"
  reading — that is BACKWARDS from our pass-through canon
  (shd:shield-collapse-evacuate) and must be checked against source.

## Local ground-truth check (FOUNDRY, 2026-09-02) — BENCH's survey was WebSearch-only

BENCH's survey (`research/Jawa/shield_mods_survey_2026-09-02.md`) explicitly
says "No local files, mod list, or game state were touched" — this checks
its top candidates against what is ACTUALLY installed/active on this
mod stack, per the owner's own "download them for study" framing:

- `oskarpotocki.vanillafactionsexpanded.core` (VEF) — **ACTIVE**, confirmed
  in `ModsConfig.FULL.LATEST.xml`'s live 592-entry list.
- `vanillaexpanded.vfesecurity` (VFE Security, the likely actual home of
  `CompShieldField`/point-defense) — **ACTIVE**.
- Odyssey's native gravship system — **ACTIVE** (`knownExpansions` lists
  `ludeon.rimworld.odyssey`); `vanillaexpanded.gravship` is also active,
  which may be a VE compat/extension layer over the native slot, not a
  duplicate — worth confirming which owns the actual shield-slot hook
  before extending it.
- **ED-Shields is NOT present anywhere on this machine** — not in the
  592-mod active list, not found in a `<packageId>`/name scan across the
  installed Workshop tree. BENCH's own survey already flagged this mod's
  1.6 support as unconfirmed/search-snippet-derived; this confirms it also
  isn't downloaded yet. Per the owner's "look them up and download them for
  study" instruction, ED-Shields specifically needs a Workshop subscribe
  before its module-architecture pattern can be studied from real source
  rather than a search snippet.

**Also surveyed independently, before finding BENCH's item file already
existed**: `neronix17.shieldgenerators` (active) is a genuine local match,
but for the WRONG row — its `TabulaRasa.Comp_Shield`/`CompProperties_Shield`
(radius-scalable, EMP-overload-on-collapse, `interceptGroundProjectiles`)
is a kinetic/anti-projectile bubble shield, matching the ruled
`bubble-not-wall` row (a Star-Wars-style deflector, explicitly adjacent to
but distinct from L6's combat shield per the design doc's own framing), NOT
the v1 build-ladder's thermal-veil/particulate-screen environmental shields
— nothing in it models heat/cold radius mitigation. Its
`ShieldGen.CompProperties_PlasmaVenting` + `PipeSystem.CompProperties_ResourceStorage`
plasma-pipe-network IS a useful architectural precedent for the "modulated
plasma field" fuel/power economy language the owner ruled for ALL four
shields, even though the interception logic itself doesn't transfer to a
thermal/cold gate. No local mod was found that already models a
heat/cold-radius environmental gate — that comp is original work regardless
of which foundation mod is chosen.

## Source verification of BENCH's two flagged caveats (FOUNDRY, 2026-09-02)

Direct read of `Vanilla-Expanded/VanillaFurnitureExpanded-Security` and
`Vanilla-Expanded/VanillaExpandedFramework` GitHub source (1.6/main), not
search snippets — this resumes the check the pre-reboot session started and
lost:

1. **Point-defense speed reading — CONFIRMED, not backwards.**
   `CompPointDefense.InterceptChance` (VFE Security):
   `chance = 0.98 * exp(-max(0, speed-30)/10)`, clamped `[0.05, 0.98]` — a
   strictly decreasing function of speed, so slower projectiles genuinely
   are more interceptable. That IS backwards from our
   `shd:shield-collapse-evacuate` "slow things pass through" canon, exactly
   as BENCH's survey worried. The curve is hardcoded inside
   `InterceptChance` with nothing exposed on `CompProperties_PointDefense`
   (only `interceptionRadius`, `interceptionAttemptInterval`,
   `blacklistedProjectileDefs` are XML fields) — reusing this needs a new
   comp or a Harmony patch over `InterceptChance`, not an XML retune.
   Written up in `research/Jawa/shield_mods_survey_2026-09-02.md`'s open
   questions.

2. **`CompShieldField` is a PAWN-WORN shield, not a building/gravship one —
   correction to the survey's "foundation" framing.** It lives at
   `Source/VEF/Apparels/Comps/CompShieldField.cs`, driven by
   `Apparel_Shield`/`JobDriver_EquipShield`/`PawnShieldGenerator` — a
   `ThingComp : PawnGizmoProvider` meant for an apparel item a pawn equips
   (the vanilla-style personal shield belt pattern), not a
   `Building`/gravship-scale comp. VEF's Gravship-adjacent files
   (`GravshipLaunchExtension`, the launch-confirmation/copy-cell-contents
   Harmony patches) live in a completely separate `Buildings` namespace with
   no reference to the Shield classes — there is no existing hook between
   VEF's shield engine and Odyssey's native gravship shield slot. The
   energy-drain-to-EMP-collapse behavior BENCH's survey wanted to borrow is
   real and matches our ruling, but as a **personal-shield** precedent; the
   environmental/gravship-scale shield needs its own `Building`-hosted comp
   inspired by this pattern, not a fork of `CompShieldField` itself.

**Net effect on the recommended shape:** point 1 stands as flagged (needs
inverting, confirmed not a misreading). Point 2 changes the survey's
"Foundation: VEF's shield engine" line from "fork/extend" to "study the
energy/EMP pattern, build our own `Building`-scale comp" — this is a design
call, not a FOUNDRY build decision; flagging for BENCH/owner before the
actual shield build item is filed.
