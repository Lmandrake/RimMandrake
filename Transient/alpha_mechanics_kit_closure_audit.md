# ALPHA_MECHANICS_KIT_1 closure audit

## Verdict
CONFIRMED: `ALPHA_MECHANICS_KIT_1` closed on **code compile + offline static
XML validation + selftests only** — its own closing commit says so in plain
words ("Deploy + live proof + content defs are separate follow-on work") —
and the mod it shipped (`mandrake.rm.environmentalhazards`) was **not added to
any mod list until six days later** (2026-09-17, `9bf9ccf4e`). So the
closure's own evidence never claimed a live run, and no live run could have
happened anyway: the mod could not have loaded in any game session between
filing (2026-09-11 05:19) and closing (2026-09-11 00:16 same session — the
whole item was worked in ~1h34m) or for six days after. All six RC comps ship
inside that one mod, so all six are equally unproven — there is no split
between "gated" and "fine" here; the mod IS the gate. This is not an isolated
incident: a same-day ledger sweep (`MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1`,
2026-09-19) independently names at least four other closed items with the
identical defect.

## 1 What the closure claimed
CONFIRMED (read via `rimflow show ALPHA_MECHANICS_KIT_1` and `git show`).

- Ledger: filed 2026-09-11T05:19:37Z (BENCH, for FOUNDRY), claimed/started
  2026-09-11T06:40:37-38Z, **closed 2026-09-11T07:14:58Z**, sha
  `ddd8d379f6d9f3127cfaa33f6429ee0c01f4f06f`. No `items/ALPHA_MECHANICS_KIT_1.md`
  prose file exists (live or in `closed/`) — the ledger event and the two
  commit messages are the only closure record.
- Commit `ddd8d379f` ("RM-tier generalized mechanics kit, all six comps",
  2026-09-11 00:13:21 -0700) adds the whole mod
  `src/RimMandrake/EnvironmentalHazards/` (22 files, packageId
  `mandrake.rm.environmentalhazards`) and says in its own body: **"Builds
  clean; LIVE PROOF STILL OWED."**
- Commit `636192203` ("Close ALPHA_MECHANICS_KIT_1: all 6 generalized comps
  built, compiled, validated", 3 minutes later, 00:16:10) is the actual
  ledger-close commit (touches only `events.jsonl` + queue files) and states
  the full evidence verbatim: **"dotnet build 0/0, validate_patch clean on
  full 579-mod set, 45/47 selftests (2 pre-existing unrelated skips). Deploy +
  live proof + content defs are separate follow-on work."**

## 2 What kind of evidence it was
CONFIRMED — three instruments, all offline, none a live run:
1. `dotnet build` — the assembly compiles (0 warnings/errors).
2. `validate_patch.py` — a **static XML structural checker** (per its own
   header docstring, read at
   `skills/rimworld-modding/scripts/validate_patch.py`): dispatches on root
   element (`<Patch>` vs `<Defs>`), checks a fixed shortlist of mechanical,
   decidable failures (xpath match, dangling references, etc.) against a def
   dump. It explicitly does **not** check "field names, field types, value
   ranges, C# class members" and does not require or prove the target mod is
   in the active `ModsConfig.xml` — "clean on the full 579-mod set" means the
   mod's own XML is internally well-formed against that def corpus, not that
   the mod loaded or ran.
3. `run_selftests.py` — 45/47 unit-style selftests, unrelated pre-existing
   skips.
None of these is a live game run, a def-dump reading of an actual loaded
game, or a bridge/quicktest check. The commit's own language ("live proof
STILL OWED", "live proof are separate follow-on work") is explicit that no
live evidence was claimed — this is a case where the closer stated the limit
correctly in prose but the ledger status field still recorded `done`/closed
with no gate stopping that.

## 3 Could the gated defs have loaded
CONFIRMED, via `ENVHAZARDS_NEVER_ACTIVATED_1` (filed 2026-09-18, MEASURED by
parsing `ModsConfig.xml` with ElementTree, not scanned) and the activation
commit itself:
- `mandrake.rm.environmentalhazards` was **absent from the live
  `ModsConfig.xml`, absent from `ModsConfig.FULL.LATEST.xml`, and absent from
  every snapshot in `infrastructure/state/modlists/`** at the time that item
  was filed (2026-09-18T03:04:12Z).
- It was first inserted into both lists at 2026-09-17T20:29:24Z
  (`9bf9ccf4e`, owner: "Yes, both lists") — **six days after**
  `ALPHA_MECHANICS_KIT_1` closed (2026-09-11T07:14:58Z).
- Therefore at closing, and for the six days that followed, the mod could not
  possibly have loaded in any game session — there is no mod-list state in
  the historical record that would have included it. Any claim of runtime
  behaviour for this period would be UNMEASURABLE-turned-false, but no such
  claim was made (see §2) — the defect is that the ledger nonetheless
  recorded the item `done`.

## 4 RC1-RC6: gated vs not
CONFIRMED, via `git show ddd8d379f --stat` and `About.xml`. All six comps
ship as C# source **inside `mandrake.rm.environmentalhazards` itself**
(packageId confirmed at `src/RimMandrake/EnvironmentalHazards/About/About.xml:3`):

| # | Comp | File | In env-hazards mod? |
|---|------|------|---|
| RC1 | ActiveGasEmitter | `Source/CompActiveGasEmitter.cs` + `CompProperties_ActiveGasEmitter.cs` | yes |
| RC2 | PeriodicAreaAttack | `Source/HediffComp_PeriodicAreaAttack.cs` + `HediffCompProperties_PeriodicAreaAttack.cs` | yes |
| RC3 | BiomeGlowMultiplier | `Source/BiomeGlowMultiplierExtension.cs` + `BiomeGlowPatches.cs` | yes |
| RC4 | EnvironmentalWeather | `Source/EnvironmentalWeatherExtension.cs` + `GameCondition_EnvironmentalWeather.cs` | yes |
| RC5 | ScaledDeathExplosion | `Source/DeathActionWorker_ScaledExplosion.cs` + `DeathActionProperties_ScaledExplosion.cs` | yes |
| RC6 | TargetedHediffAffliction | `Source/CompAbilityEffect_TargetedHediffAffliction.cs` + `CompProperties_...` | yes |

**There is no split.** All six are the mod, not consumers riding a
`MayRequire` reference to some other, live mod — the mod itself is the gate.
The commit itself says it "ships no content defs, only abstract gas parents"
(`RM_GasBases.xml`), so at closing there wasn't even another mod's def
attaching one of these comps to a real Thing yet. **Every one of RC1-RC6 was
equally unproven at closure and remained so for six more days** — none of the
six is "fine" by virtue of living in a mod that did load.

(Separately: several *later*, still-open build items — `MIASMA_MECHANICS_1`,
`SCALD_MECHANICS_1` — deliberately reuse RC1-RC6 as "ruled-comp reuses" per
their kit specs; those items are `doing`, not closed, and their own commits
explicitly flag "live/quicktest verification... owed to a later, separate
build item," so they do not compound the defect — they inherited it honestly
and left it open.)

## 5 Other items with the same defect
CONFIRMED via `infrastructure/state/items/closed/MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1.md`
(FOUNDRY BELT, 2026-09-19 — a fresh full parse of every `mandrake.*` mod's own
`About.xml` packageId, 141 found, against live `ModsConfig.xml`, 620
activeMods: 112 active / 29 inactive). Its own "Genuine activation-gap
candidates" section names closed items where content was built and the item
marked done with **no live verification on record**, for a mod confirmed
still inactive as of that sweep:

- **`TITANIC_CREATURES_MOD_1`** (closed 2026-09-09) — `mandrake.rm.titaniccreatures`.
- **`BRAINWORM_MOD_BUILD_1`** (closed 2026-09-11) — `mandrake.rsw.brainworms`.
- **`FLOOD_CANYON_BIOME_1`** (closed 2026-09-12) — `mandrake.rm.floodedcanyon`;
  its own close note flags a downstream plot-beat dependency, unresolved.
- **`DROID_FDE_GOODWILL_CAP_1`** (closed 2026-09-09) — `mandrake.rut.restrainingbolts`
  — explicitly closed "on OFFLINE criteria only," its own file stating
  "live-observed goodwill-cap-in-effect test stays owed."

Also directly relevant but a different sub-species of the same root cause:
`MAYREQUIRE_OPERATION_INERT_SWEEP_1` (closed 2026-09-18) found and fixed 10
files where a `MayRequire` on a `<Operation>` (not on the whole `<Patch>`) is
silently **not honored by the engine at all** — `ModContentPack.LoadPatches`
never reads it — so patches "gated" on `mandrake.rm.environmentalhazards`
ran and injected dangling references on every load "so far," per its own
citation of `ENVHAZARDS_NEVER_ACTIVATED_1`. Different mechanism (inert engine
field vs. mod never in the list) but the same family of "proven" work that
was never actually exercised.

I did not exhaustively re-verify each of the four/five named items' own
closing commits line-by-line (time-boxed) — treat the sweep's own list as
CONFIRMED-by-citation (it names its method and MEASURED packageId parse
count) rather than independently re-measured by this audit.

## Instruments and their limits
- `python3 src/RimMandrake/rimflow/cli.py show/why <ID>` — ledger event
  history and closure sha; **no item prose file exists for
  `ALPHA_MECHANICS_KIT_1`**, so the ledger + the two git commits are the only
  primary sources for its closure claim.
- `git show <sha> --stat` / `--no-patch --format` — used for commit messages
  and file lists; never `--patch` (per house rule, and unnecessary here — the
  commit messages state the evidence in prose).
- `validate_patch.py`'s own header docstring (read directly, not inferred) is
  the source for "what it does and doesn't check" in §2 — CONFIRMED by
  reading the file, not assumed from its name.
- `ModsConfig.xml` history: I did not re-parse the XML files myself this pass
  (no bare grep of `<li>` per house rule); the never-loaded/first-activated
  claims in §3 are CONFIRMED via **already-MEASURED** ledger notes
  (`ENVHAZARDS_NEVER_ACTIVATED_1`'s own filed text, which states it parsed
  with ElementTree) and the activation commit `9bf9ccf4e`'s own message,
  which is itself sourced from a re-parse per the item's OWNER-note event.
- §5's other-items claim rests on one closed sweep document's own citation
  rather than a fresh independent re-measurement of each named item's mod
  list state today (2026-09-20) — some of those 29 "inactive" mods could in
  principle have been activated since 2026-09-19; not re-checked here as it
  was out of scope for a closure-evidence audit and would need a fresh
  `ModsConfig.xml` ElementTree parse to confirm, which I did not run.
