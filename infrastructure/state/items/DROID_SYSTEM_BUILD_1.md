# DROID_SYSTEM_BUILD_1 — build the unifying droid platform

REOPENED by the owner 2026-08-29 (verbatim): "We've fallen in love with the full
droid item and would like you to fully work it out into a buildable spec. The
idea is that we will not build on any one of the packs, they all have too many
flaws. Rather, we will borrow from them and make our own... We would want to
port all the droids in the game to that one platform, whether we make it or not."

## Spec
`design/Jawa/droid_system_build_spec.md` — architecture (own DLL + HAR substrate,
packs demoted to asset libraries), five-state engine mapping, 14-unit C# work
breakdown, three port waves + strays, phase plan with per-phase proofs.
Design intent: `design/Jawa/droid_system_spec.md`. Verb authority:
`design/Jawa/droid_verbs_decisions.json` (FROZEN).

## Verify
Phase 0 proof on quicktest: pilot chassis (gonk) completes
spawn → ion-down → capture → bolt → wipe → kill → rebuild → detonation-scales-
with-charge, plus the edge-case matrix (caravan, pod, surgery-on-object,
storyteller targeting, no-food-need, drafted at 0 power).

## Criteria
- [x] Owner rules the §8 opens (name, race granularity, JDS identity, port timing)
      — all four closed 2026-09-01 (three already ruled 2026-08-29); see
      `canon.yml` `droid_system`. **Build greenlit, no longer parked.**
- [x] Phase 0 skeleton + pilot proven live (see 2026-09-01 note below — the
      checkbox was stale, work already landed before this note was written)
- [ ] Port manifest MEASURED (census sweep) and waves 1-3 executed at save boundaries
- [ ] Packs' redundant systems in Cherry Picker; DroidsAreMachines retired per-wave

## 2026-09-01 (BENCH) — dispatched to build the Phase-0 foundation, found it already built and shipped

Dispatched to build ONLY the foundation slice (mod skeleton, `DW_FleshType_Droid`,
`Need_Power`, three charging buildings), explicitly withholding ion integration,
`PoweredDown`, death rewiring, detonation, bolt/spike/wipe, and any chassis/race
def. **Before writing a line, checked `git log` and the existing item files —
every one of those units, in-scope AND explicitly-out-of-scope, was already
built, compiled, validated and (for several) live-quicktest-verified** by prior
work already on `main` HEAD (commits `d806127e` phase-0 defs, `064aba87` DLL
compile, `72858502` charging trio, `d340b213` bolt core, `6f38cc38` wipe+spike,
`9cd6cf18` chassis-family abstracts, `ee9c095b` 57/80 races+kinds generated,
`a9b13567` live proof on the gonk pilot, `18e1c814`/`715aeb82`/`b8ab6229` the
relations-crash fix closed 60/60 live, plus `0772bec7`/`e2fdf908` the tier-rename
migration that moved the whole mod to `src/RimStarWars/Droidworks/`).

**Confirmed on disk, not just from commit messages:**
- Mod folder `src/RimStarWars/Droidworks/` exists with the full layout
  (About/Assemblies/Defs/Patches/Source/Textures); `About.xml` carries
  `packageId mandrake.rsw.droidworks` — RimStarWars tier, per
  `design/NAMING_SCHEME_PLAN.md`'s own test (a general SW droid platform, not
  Utinni-campaign-specific) and already executed, not just decided.
- All defNames migrated to `RSW_DW_` (176 hits for `defName>RSW_DW_`, 0 for the
  old bare `DW_` prefix) — the naming-tier question this task asked me to work
  out was already ruled AND applied.
- `Droidworks.dll` (23,552 bytes) and `DroidworksBoltCore.dll` (6,144 bytes)
  present in `Assemblies/`, both newer (2026-08-31 00:15) than every `.cs` file
  under `Source/` — compiled clean, not stale.
- `NeedDefs_Droidworks.xml` (`RSW_DW_Power`), `Buildings_Charging.xml`
  (`RSW_DW_ChargeSocket`/`ChargeDock`/`ChargeNimbus`, three-tier per spec §3
  unit 1-2), and `RSW_DW_FleshType_Droid` (`isOrganic:false`, in
  `Defs/Races_Base.xml`) all exist and match the build spec's shape.
- `RSW_DW_FleshType_Droid` is authored but **deliberately not wired** onto
  `DW_Race_Base` yet — documented in-file and in
  `DROIDWORKS_ISFLESH_RELATIONS_CRASH_1.md`: wiring `isOrganic:false` onto a
  Humanlike-intelligence race NREs pawn generation
  (`PawnComponentsUtility` never allocates `pawn.relations` when `!IsFlesh`,
  but Humanlike generation dereferences it unconditionally) — a real engine
  interaction between units #1 (flesh type) and #5 (out-of-scope death
  rewiring/Harmony), found and root-caused by prior work, fix built and
  live-verified 60/60 on the three already-shipped droid packs, but the
  wire-back onto `DW_Race_Base` itself is still an open checkbox in that item.
  This is exactly the "unit boundaries don't hold up" signal this task's brief
  asked me to surface if found — it already was, by the work that got there
  first, and stayed correctly unresolved rather than routed around.

**Action taken this pass: none.** No code written, no defs authored, nothing
compiled, nothing deployed — writing any of the assigned units now would either
silently duplicate already-tested code under a different (stale `DW_`, pre-rename)
name, or collide with the live `RSW_DW_` versions. Verified via `git status`
that no other in-progress work touches `src/RimStarWars/Droidworks/` right now
(clean on that path), so nothing is mid-edit either — this is a genuinely
completed prior pass, not a race.

**What's actually still needed before the real Phase-0 quicktest proof
(spawn → ion-down → capture → bolt → wipe → kill → rebuild → detonation)**:
resolve `DROIDWORKS_ISFLESH_RELATIONS_CRASH_1`'s remaining open checkbox
(wire `fleshType` back onto `DW_Race_Base` and re-verify), then work through
whichever of `DROIDWORKS_POWEREDDOWN_NOT_WIRED_1` / `DROIDWORKS_WIPE_AND_SPIKE_1`
/ `DROIDWORKS_BOLT_CORE_1` / `DROIDWORKS_CHARGING_TRIO_1` still show open
criteria — read those item files directly rather than this summary, they carry
the current per-unit state.

## 2026-09-01 (FOUNDRY) — fleshType wired, deployed; Droidworks itself still not in ModsConfig

Wired `<fleshType>RSW_DW_FleshType_Droid</fleshType>` onto `DW_Race_Base`
(`src/RimStarWars/Droidworks/Defs/Races_Base.xml`) — unblocked by
`DROIDWORKS_ISFLESH_RELATIONS_CRASH_1`'s own close (commit `715aeb82`, live
60/60 on the shipped OuterRim/KotOR droids sharing the same `IsFlesh` gate,
not a Droidworks-native pawn). Deployed
(`deploy_custom_mods.py --mod Droidworks --apply`).

**Not live-verified against Droidworks itself, and can't be yet**: checked
`deploy_custom_mods.py`'s own plan output — `mandrake.rsw.droidworks` is
**not enabled in `ModsConfig.xml`**, despite the extensive prior build
(races, kinds, DLLs, bolt core, charging trio, wipe+spike, all compiled and
partly quicktest-proven per `a9b13567`'s pilot-gonk note). Whatever proved
Phase 0 live before must have used a scratch/minimal mod list
(`rimworld-load-round`'s 13-mod pattern), not the persistent 587-mod
`ModsConfig.xml` this session has been restarting all night — deliberately
did NOT add Droidworks to the full list tonight, since that's a materially
bigger decision (57-80 new races/kinds interacting with 587 other mods) than
"verify one field wiring," and a dedicated minimal-list quicktest is the
right-sized tool for it, not another full-list restart. Left as the next
concrete step: bring up a minimal quicktest list with Droidworks active,
spawn a `DW_Race_*` pawn, confirm `pawn.relations` is non-null and no NRE.
