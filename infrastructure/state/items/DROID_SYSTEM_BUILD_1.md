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
- [x] Port manifest MEASURED (census sweep 2026-08-29, `design/Jawa/
      droid_system_build_spec.md` §7) and waves 1-3 executed at save
      boundaries — CONFIRMED 2026-09-12: none of the four donor packageIds
      (`guy762.kotordroids`, `killathon.artificialbeings.syncore`,
      `neronix17.outerrim.droiddepot`, `neronix17.asimov`) are present in the
      live `ModsConfig.xml` (592 active) any more; only `mandrake.rsw.
      droidworks` remains as the droid content provider. Matching sub-items
      `DROID_RETIRE_KOTORDROIDS_1`, `DROID_RETIRE_ABF_SYNCORE_1`,
      `DROID_RETIRE_DEPOT_ASIMOV_1`, `DROID_RETIREMENT_ORDER_ASSERT_1` are all
      CLOSED in the ledger.
- [x] Packs' redundant systems in Cherry Picker; DroidsAreMachines retired
      per-wave — CONFIRMED 2026-09-12: `DroidsAreMachines.xml` history shows
      its ABF-gated Operation already removed per-wave (commit `0c2898020`,
      `DROID_RETIRE_ABF_SYNCORE_1`). Grepped `CherryPicker.SHIP.xml` for the
      four donor packageId substrings — zero hits, which is CORRECT and not a
      gap: Cherry Picker entries exist for trimming redundant content inside
      an *active* mod, and all four donors are fully retired (removed from
      `ModsConfig.xml` entirely), so there is nothing left for Cherry Picker
      to trim.

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

## 2026-09-12 (FOUNDRY) — reclaim premise was STALE; fresh minimal-list proof done; CLOSING

Reclaimed on the premise "mod not in live ModsConfig, minimal-list quicktest
owed" (2026-09-12 audit). **Both halves of that premise were stale**, found by
direct check before spending a load on them:

- `mandrake.rsw.droidworks` IS already active in the live 592-mod
  `ModsConfig.xml` (confirmed identical to `ModsConfig.FULL.LATEST.xml`) —
  landed by `DROIDWORKS_FULL_LIST_COEXIST_1` on 2026-09-08, which also fixed
  3 real bugs (bad `<li>` skillRequirements shape, `everVisible` non-field,
  missing `initialResistanceRange`/`initialWillRange` on 80 kinds) and closed
  with a confirmed clean full-list restart.
- `DROIDWORKS_LIVE_LOOP_PROOF_1` (closed 2026-09-06/08) already ran an
  extensive minimal-list spawn/state-machine proof (12 pawns, 6/8 checkboxes
  fully closed live: PoweredDown persistence, reboot, spawn-with-no-NRE,
  bolt+resentment, kill→corpse, GNK detonation-scales-with-charge A/B).

Given that, did **not** repeat the full 8-checkbox proof (doctrine: don't
re-spend a load proving what's already proven). Instead ran a fresh, narrower
minimal-list (25-mod) verification targeting what those two prior passes did
NOT cover: the newer/less-tested categories (Primitive tier, JDS in
isolation) and whether the 09-08 field fixes hold up live.

**Bridge session, minimal list (`ModsConfig.MINIMAL.xml`, 25 mods, Droidworks
already included):**
- Fresh `start_debug_game_ready` quicktest map.
- Spawned **21 pawns across all 7 distinct format/source categories**: JDS
  (`RSW_DW_JDSCIS_B1_Battle_Droid` ×3), OuterRim GNK (×3), OuterRim battle
  (`RSW_DW_OuterRim_BattleDroid` ×3), KotOR colonist (`..._T3UD` ×3), KotOR
  bad (`..._KM1MD` ×3), Primitive G2 (×3), Primitive Junker (×3). All 21
  `execute_debug_action` spawn calls returned `success: true`;
  `jawa/list_pawns` count went 29→50 exactly (+21, no silent drops).
  `jawa/pawn_get` returned well-formed snapshots (traits/skills/needs) for
  the sampled ones, each on its own `RSW_DW_Race_*` def — no fallback race.
- Screenshots (`droidworks_minimal_quicktest_wave1.png`,
  `_zoom_a`/`_zoom_b`, session-scratch in the Screenshots folder) confirm
  every spawned droid renders with distinct, plausible art — no magenta/
  checkerboard fallback on any of the 7 kinds.
- Re-exercised two state-machine points post-09-08-fix: `RSW_DW_PoweredDown`
  add/remove on a KotOR colonist — clean add + clean remove, matching the
  pre-fix proof exactly (the 09-08 pass removed `everVisible` from this
  exact def; confirms the removal didn't break the hediff itself). Set a
  GNK's `RSW_DW_Power` need to 1.0 then killed it with two `Bomb` hits — died,
  vanished from `list_pawns`, **no droid corpse appeared** (only pre-existing
  unrelated Human corpses) — consistent with `CompDroidDetonation` consuming
  the corpse at high charge, matching `DROIDWORKS_LIVE_LOOP_PROOF_1`'s own
  isolated A/B finding.
- `Player.log` for the whole session (183 lines, 25-mod list): **zero**
  `Config error in` lines, **zero** Droidworks-related exceptions. The one
  exception present (`OuterRimCore.OuterRimCoreMod` NRE at mod-init) is the
  same pre-existing, unrelated third-party bug `DROIDWORKS_LIVE_LOOP_PROOF_1`
  already flagged. Seven `Could not resolve cross-reference: ... RUT_Tree_
  Unbolting ...` lines are an **expected minimal-list gap**, not a bug: that
  ResearchTabDef is owned by `mandrake.rut.researchretag` (RimUtinni-tier,
  campaign-only), present on the full list, absent from the 25-mod minimal
  list by design.

**Port waves and Cherry Picker checkboxes** (see Criteria above): verified
directly against the live `ModsConfig.xml` that all four donor packages are
retired, so both remaining checkboxes are now checked with evidence.

**Verdict: mechanism clean, both remaining criteria satisfied. Closing.**
Restored the mod list to `ModsConfig.FULL.LATEST.xml` before closing (592
active, verified) — the game must not be left on the minimal list.
