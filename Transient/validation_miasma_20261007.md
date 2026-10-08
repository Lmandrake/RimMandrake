# Miasma offline validation, 2026-10-07 (FOUNDRY, uncommitted, no bridge)

## 1. Survey (2.7k lines in src/RimMandrake/Miasma/Source)
Chosen kernels (all were inline expressions in comps, a hediff comp and map components tangled with Verse/Unity):
1. **The warden mother's creche**: young ledger, the clean record, betrayal, returns, the one-shot succession (RM_CompCrecheYoungLedger) and the self-taming timer (RM_HediffComp_SelfTameOnRecord).
2. **The mother's price**: buyer scheduling for held stranded young, reach/return/sale gates (RM_MothersPrice, RM_MapComponent_MothersPrice).
3. **Decay cell** digestion + power curve, **rotting bed** clock/bones/stacks, **flotsam yard** cadence/sizing/table pick, the three nearest-thing pickers (creche marker, mother for the young's call, plant predator prey), attar balm, biome score.
Rejected as kernels: RM_Patch_WardenYoungTrainableGate (Harmony gate on two engine methods), RM_AmbushFrogHunting (one race flag), RM_MiasmaSettingsApplier (reflection edits of defs), RM_MapComponent_DecayMeter (spawn), the attar float-menu/job driver (engine), RM_MiasmaProof (bridge hooks), NearestWaterCell (RadialPattern + CanReach), the sell/return letters.

## 2. Kernels + fuzz
Extracted (call sites call the kernel with the same expressions; every Scribe label unchanged):
- `src/RimMandrake/Miasma/Source/RM_MiasmaKernel.cs` (CrecheLedger<T>, SelfTameStep, BuyerPoll, DecayObserve, OutputFraction, RotStep/RotDownTicks/BonesFor/StackSplit, FlotsamStep/Want/Pick, NearestFirstInclusive/NearestFirstStrict/NearestLastInclusive, BalmScar, BiomeScore), in `RM_Miasma.csproj`'s Compile list.
  Callers changed: RM_WardenMotherSuccession, RM_MothersPrice, RM_CompPlantPredator, RM_MapComponent_YoungCall, RM_DecayCells, RM_RottingBed, RM_MapComponent_FlotsamYard, RM_Attar, RM_MiasmaBiome.
Defects: none found in these rules; the fuzz and the extraction turned up no behaviour that disagrees with the design text. Observations, NOT changed (design calls):
- **Buyer bookings are never cleared.** `buyerAt` only loses an entry on a successful send, so a booking for a young that left the player's hands (returned, sold, died) stays in the save for good (seen in 20,632 polls of the default run). It also means a young that came back into the player's hands later would meet a booking already past due and get its buyer at once.
- **One succession attempt per creche, ever, even if nobody is eligible.** If the warden mother dies before a young has self-tamed, the attempt is spent and a young that tames afterwards can never become heir (documented in the code as the roster's "not guaranteed"; flagged because a player who kills the mother early closes the creche's inheritance for good).
- **A decay cell with a trace of fuel makes `minOutputFraction` of full power at once** (0 at empty, then a step to e.g. 30%), by construction of `OutputFraction`.
- **Digestion can under-count** by at most the smaller of the burn and the refill in a 250-tick window that contains a refill (it only sees net fuel falls); exact in refill-free windows.
- The three nearest-thing searches differ on ties and on the bound on purpose or by accident: the creche marker takes the first closest at `<=` the radius, the young's call takes the first closest strictly inside 60, the plant predator takes the LAST of equal distances at `<=`. Pinned by the fuzz so a change shows.
Fuzz: `src/RimMandrake/Miasma/Source/MiasmaFuzz/{MiasmaFuzz.cs,Program.cs,RimMandrakeMiasma.Fuzz.csproj}`, wrapper `src/RimMandrake/Utils/selftest_miasma_fuzz.py`
(families creche | tame | price | decay | rot | flotsam | pick | units; --fuzz-scale/--fuzz-seed/--fuzz-only).
Invariants:
- creche: young distinct and in registration order; owed count equals an independent count; a spent succession never comes back; a broken record never heals; betrayal leaves the creche void (record gone, succession spent, no heir) for good; an heir is the FIRST eligible young in registration order, alive and the player's, chosen at most once; returning a young removes it and counts it; poll only while a succession is possible and the option is on.
- tame: first look only schedules (2000..3200 ahead); an early step touches nothing and rolls nothing; a due step reschedules exactly once; the chance is rolled only with the option on and no broken record (a ledger-less young can still tame); a tame never happens barred.
- price: first sighting books a buyer 60000..120000 out and sends nothing; nothing sent before the booked tick; a due young is tried exactly once per poll; a failed send rebooks exactly 60000 out; an offered young is never offered again and loses its booking; sends only for held young.
- decay: digestion never goes backwards, exactly the burn in a refill-free window, never more than burned, never under-counts beyond the refill bound; spent iff digested >= lifetime with a bed def and spawned; output 0 at empty, in [min,1] above, monotone in fullness, 1 when full.
- rot: the clock equals an independent per-corpse reference (restart on a new or moved corpse, +250 per rare tick, done at the setting's length, never runs past it, nothing stored leaves it at 0); rot length >= 2500; bones >= 1 and monotone; stacks sum to the total, each in 1..limit, only the last short.
- flotsam: seeds exactly once (24), restocks 14 only when the recede tick moves forward, nothing otherwise; the request is min(round(base x amount), round(70 x amount) - placed); table pick proportional (4/4/3/1, 200k rolls), edges safe.
- pick: the three pickers equal brute-force references on arrays with many exact ties and values exactly at the bound.
- units: rot-down table, bones table, reach defaults, return reach boundary (<= 16), sale/betrayal gates, balm takes ceil((s - 0.01) / 3) applications and never goes negative, biome score (warmer is higher, river required, mountains excluded, failed gate, edges, exclusive rainfall max).
- A coverage line checks 16 interesting events all fired (a heir chosen, a creche betrayed, a buyer sent / retried, a decay cell spent, a corpse rotted, ties at the bound, ...).
Seeds: default 39,005 cases / 1.58M steps in 1.7 s; `--fuzz-scale 25`: 975,005 cases / 34.7M steps in 30 s, all green.
Mutation (each planted, caught, reverted; files compared byte-identical afterwards; 4 s sleep before each run):
- M1 betrayal leaves the succession open, M10 a spent succession is polled again: creche FAIL. M2 a broken record does not bar taming: tame FAIL. M3 offered young re-offered, M4 failed send never retries: price FAIL. M5 a refill counted as digestion: decay FAIL. M6 rot swap keeps the clock: rot FAIL. M7 predator takes the first of ties, M11 strict bound on the marker search: pick FAIL. M8 restock on every look, M9 flotsam cap ignores the amount: flotsam FAIL. M12 balm leaves a 0.2 scar: units FAIL. (M7 first missed its pattern and was re-run with a shorter one.)

## 3. Lint
`src/RimMandrake/Utils/selftest_miasma_lint.py` over the generic `moddefs_lint.py`, which gained an opt-in REFLECTION_NAME check for this mod (a mod that reaches into another assembly by `GetField("x")` / `.Name == "X"` goes silently dead if that name is renamed): 8 such names (`LastRecedeCompletedTick`, `callSound`, `strandedDeformationChance`, `anchorRadius`, `RM_CompTerritorialAnchor`, `RM_MapComponent_GradientAxis`, `RM_PollinationGateExtension`, plus the engine's `allRecipesCached` allow-listed) and 4 helper-call names (`Betrayed`, `ColonyTolerated`, `RevokeForever`, `GrantColonyTolerance`) all resolve to identifiers in src/. Counts: 38 classes, 20 XML class refs, 12 Class= nodes, 15 .cs == csproj Compile list, 36 RM_/RUT_ literals, 41 Scribe labels no duplicates, 18 settings fields (default == Scribe default, inside slider range), 6 creche-ledger Scribe labels, 16 named def lookups. Findings on the tree: 0 (3 initial false positives, class names used as reflection strings, fixed in the lint by accepting identifiers). Self-proof: 12 planted breaks (misspelt class, misspelt field child, csproj without the kernel, bogus def literal, duplicate Scribe label, settings default drift, setting outside its slider, two reflection typos, renamed ledger label, Verse import in the kernel, missing named def) each caught.

## 4. Build
`python3 src/RimMandrake/Utils/winbuild.py src/RimMandrake/Miasma/Source/RM_Miasma.csproj`: 0 warnings, 0 errors. DLL + .srchash modified, NOT committed (rebuild after committing: the kernel file is untracked until then). The MiasmaFuzz project builds on net8.0 with 0 errors.

## 5. How to run
- `python3 src/RimMandrake/Utils/selftest_miasma_fuzz.py [--fuzz-scale 25] [--fuzz-seed N] [--fuzz-only creche|tame|price|decay|rot|flotsam|pick|units]`
- `python3 src/RimMandrake/Utils/selftest_miasma_lint.py`
- Trap: wait >= 4 s between editing the kernel and re-running (the staging rsync `--modify-window=2` can build a stale copy).
