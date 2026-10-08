# Droidworks offline validation, 2026-10-07 (FOUNDRY, uncommitted, no bridge)

## 1. Survey (5.1k lines, 52 .cs in src/RimStarWars/Droidworks/Source/Droidworks + BoltCore)
Chosen kernels (all were inline expressions in comps/recipes/needs/Harmony postfixes):
1. **Format-tier ladder + recipe rules** (DroidFormatTier, Recipe_DWFormat): severity<->tier, which recipe is offered from which tier, "sapient mind destroyed".
2. **Service-record drift** (CompDWServiceRecord, DroidServiceRecordUtility): absolute-tick clock, due time per accreted count x setting, tier/cap gates,
   first-drift Programmable->Sapient promotion, chassis-weighted no-repeat draw, wipe erasure. Dense sequence state (wipes, formats, settings, reloads).
3. **Power economy** (Need_Power, CompDWCharger, JobDriver_DWRecharge, HediffComp_DWBoltResentment, CompDroidDetonation): drain per NeedInterval, dock vs nimbus
   charge rates, power-down line, pinned capped resentment, detonation scale/radius/damage.
4. **Data-spike resistance** (CompDWDataSpike): skill-scaled resistance, target/faction truth tables.
5. **Protocol-droid trade advantage** (Patch_ProtocolTradeAdvantage): net advantage, buy/sell floors and rounding tail.
6. Small tables: part slots per chassis, head per chassis, quality bucket, weighted pick (wild-droid crash + idiosyncrasy draw).
Rejected as kernels: Recipe_DWMemoryWipe.ApplyOnPawn (PawnGenerator.GenerateTraitsFor, relations, memories, Pawn_RecordsTracker reflection: all engine calls, the
only logic is the call order, which the existing step try/catch already covers), JobGiver_DWRecharge / Patch_DroidBillGiverNoBed / Patch_ApparelForDroids
(path/reservation/IL transpiler), StockGenerator_*, Recipe_Install*/Assemble (engine Thing/Bill plumbing), Patch_ShouldHaveNeed_Power (one flesh-type test
plus a setting), DroidEthicsExtension (3-way switch). They stay with the live chains (validation.py).

## 2. Kernels + fuzz
Extracted (behaviour preserving except the fixes below; call sites call the kernel with the same expressions):
- `src/RimStarWars/Droidworks/Source/Droidworks/DroidworksKernel.cs` (pure, no Verse/Unity; enums DroidFormatTier, DroidChassis moved here with the same names),
  in `Droidworks.csproj`'s Compile list. Callers changed: DroidFormatTier.cs, DroidServiceRecord.cs, CompDWServiceRecord.cs, Recipe_DWFormat.cs, Need_Power.cs,
  CompDWCharger.cs, JobDriver_DWRecharge.cs, HediffComp_DWBoltResentment.cs, CompDroidDetonation.cs, CompDWDataSpike.cs, Patch_ProtocolTradeAdvantage.cs,
  CompDWPartDropper.cs, CompDWHeadDropper.cs, DroidAssembly.cs, IncidentWorker_WildDroidCrash.cs, DroidworksModExtension.cs (new `OfRace` helper).
Defects found while extracting, all FIXED in the kernel/callers (and guarded by the fuzz):
1. **A deformat kept the droid's earned personality.** `DroidServiceRecordUtility.NotifyWiped` says every route that wipes or reformats a droid must call it,
   but only Recipe_DWMemoryWipe did. A sapient droid with 3 idiosyncrasies deformatted to Blank kept all 3 and its drift clock, and picked up where it left
   off on reformat. Now `Recipe_DWFormatBase.ApplyOnPawn` calls NotifyWiped when the target is Blank (`FormatClearsServiceRecord`). Design call: Blank only; the
   restrictive format (Mindless, "a reduced state") still keeps the record. Say if you want Mindless to clear it too.
2. **Severity 2.5 read as Mindless.** `Mathf.RoundToInt` rounds half to even, so exactly 2.5 -> 2 -> Mindless, while the RSW_DW_FormatTier hediff stage that starts
   at 2.5 is Programmable (the doc comment promises the cuts 0/1.5/2.5/3.5). Also the int cast of a huge severity wrapped to Blank and NaN read as Sapient.
   Now rounds half away from zero, clamps in float first, NaN -> default tier.
3. **Need_Power read the FAMILY's DroidworksExtension.** `GetModExtension` is first-wins and XML inheritance appends the race's copy after the family's, so a
   race-level `powerFallPerDay` was ignored (every other reader uses LastOrDefault, per CompDroidDetonation's own comment). Latent today: measured 0 races
   override a different value. Now `DroidworksExtension.OfRace`; the lint forbids the first-wins call.
4. **Detonation damage cast overflowed** (float beyond int range -> int.MinValue, a negative blast). Now saturates at 100,000.
Observation, NOT changed (design call): protocol-trade round trip is profitable once (1+a)/(1-a) exceeds the base buy/sell ratio of the item; at the default
6% per side the best case a=0.12 needs ratio < 1.27, but the settings slider allows 25% per side (a=0.5 -> 3.0x), where buying and re-selling would print money.
Fuzz: `src/RimStarWars/Droidworks/Source/SelfTest/{DroidFuzz.cs,Program.cs,RimStarWarsDroidworks.SelfTest.csproj}`, wrapper
`src/RimMandrake/Utils/selftest_droidworks_fuzz.py` (families drift | power | spike | trade | units; --fuzz-scale/--fuzz-seed/--fuzz-only).
Invariants:
- drift: a check fires exactly when an independent decimal oracle says (setting on, tier >= Programmable, accreted < cap, elapsed >= (first + n x interval) x scale,
  some positive-weight trait left); at most one trait per check; no duplicates; drawn weight > 0; first drift promotes Programmable->Sapient only if allowed,
  tier never changes otherwise; a wipe and a deformat leave 0 traits and clock 0; the clock is one int that survives save/load; unset clock reads 0; recipes
  offered from exactly the right tiers; Standard raises, the others lower; mind-destroyed iff Sapient -> Blank/Mindless.
- power: bar in [0,1]; drain never raises and tracks a double reference; powered-down line honoured per interval and ignored when the setting is off; dock/nimbus
  gain equals pph x rate/100 per hour and agree per tick; resentment monotone, capped, pinned without a bolt or on a non-thinking droid, equals perDay x rate per
  day; detonation iff effective density > 0 and charge > 0.05, deny-module floor of 1, scale/radius/damage vs double reference, monotone in charge, in range.
- spike: resistance never rises or goes negative, strictly falls each spike, captured iff it reaches 0 (or no resistance mechanic), a level-20 spiker never
  behind, captured within ceil(r0 / (perUse x 0.5)) + 1 spikes.
- trade: advantage == net x perSide, |adv| <= 2 perSide, both-or-neither cancels, antisymmetric under role swap, uninspectable trader changes nothing, prices keep
  the vanilla floors and rounding tail, advantage never raises buy / lowers sell (and the reverse), monotone in base price.
- units: severity -> tier equals the hediff stage cuts across boundaries +-1 ulp, +-1e30, inf, NaN; weighted pick proportional (200k rolls, 1% tolerance), never
  picks zero/negative/NaN, top-of-range roll safe; design timeline 2 y / 3.5 y / 5 y; part and head tables; spike truth tables (exhaustive); format matrix.
Seeds: default scale 11,007 cases / 1.22M steps in 1.4 s; `--fuzz-scale 25`: 275,007 cases / 25.75M steps in 28 s, all green.
Mutation (each planted, caught, reverted; file compared byte-identical afterwards; 4 s sleep before each run):
- M1 banker's rounding back (defect 2): units FAIL "severity 2.5 maps to Mindless but the hediff stage cuts say Programmable".
- M2 deformat keeps record (defect 1): drift FAIL, shrunk to Check/Time/Format actions.
- M3 drift ignores the time scale: drift FAIL "drift fired but elapsed 7200001 vs due 10800000".
- M4 power-down ignores its setting: power FAIL "powered down at level 0.019999 (enabled False)".
- M5 spike resistance rises: spike FAIL 1-action case. M6 trader sign flipped: trade FAIL. M7 wreck boundary `<` for `<=`: power FAIL charge 0.05.
- M8 damage cast unsaturated (defect 4): power FAIL "damage -2147483648 out of range". M9 drift cap off by one: drift FAIL.
Initial run before the rounding fix: units failed on 2.5 (that is how defect 2 was found), the rest green.

## 3. Lint
`src/RimMandrake/Utils/selftest_droidworks_lint.py` (+ generic `src/RimMandrake/Utils/moddefs_lint.py`, which REUSES check_creaturebehaviors_defs.py's parser/field/enum helpers
and adds checks; the Abyss/Miasma/TheRot wrappers reuse it). Counts on the real tree: 88 classes, 179 XML class refs, 113 Class= nodes, 230 field children, 19 enum
values, 52 .cs == both csproj Compile lists, 10 RSW_ literals, 36 Scribe labels, 48 [DefOf] fields, 30 settings fields (default == Scribe default == ResetToDefaults,
inside slider range), 4 format-tier stages, 24 DroidworksExtension nodes. Findings on the tree: 0 (the first-wins call was fixed before the first lint run; the
lint reports it if it returns). Extras: hediff ladder cuts, first-wins extension ban, chassisClass 0..7, kernel purity. A min-count probe turns a half-blind
lint into UNMEASURED. Self-proof: 13 planted breaks (misspelt Class, misspelt field, enum typo in a nested `<li>`, non-numeric int, csproj missing the kernel,
bogus def literal, duplicate Scribe label, two kinds of settings drift, [DefOf] naming no def, first-wins extension, hediff ladder moved, Unity import in the
kernel) are each caught, every run.

## 4. Build
`python3 src/RimMandrake/Utils/winbuild.py src/RimStarWars/Droidworks/Source/Droidworks/Droidworks.csproj`: 0 warnings, 0 errors. DLL + .srchash modified, NOT committed.
The SelfTest project builds on net8.0 (0 warnings). Nothing committed or pushed.

## 5. How to run
- `python3 src/RimMandrake/Utils/selftest_droidworks_fuzz.py [--fuzz-scale 25] [--fuzz-seed N] [--fuzz-only drift|power|spike|trade|units]`
- `python3 src/RimMandrake/Utils/selftest_droidworks_lint.py`
- Trap: the wrapper stages with rsync `--modify-window=2`; wait >= 4 s between editing a kernel and re-running or a stale staged copy builds.
