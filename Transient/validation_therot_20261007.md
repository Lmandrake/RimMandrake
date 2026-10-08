# TheRot offline validation, 2026-10-07 (FOUNDRY, uncommitted, no bridge)

## 1. Survey (2.5k lines in src/RimMandrake/TheRot/Source)
Chosen kernels (all were inline expressions in comps, a world component and recipes tangled with Verse/Unity):
1. **The hwelgrue's gut**: digest clock to a casting, the per-map cap, the rot boost it feeds the ground (RM_CompGutDigest).
2. **The swallow**: digest length by body size, knocks that quicken, belly-cut damage, release acid, part-digested strangers (RM_CompGutSwallow).
3. **The gut-mother vat**: fuel burn, dormancy, the digest clock, splits and rests, what it accepts (RM_CompGutMotherDigest).
4. **The swallowed drive core**: who carries the world's one core, the ping clock, integrity under the ship's guns, ruin threshold, range factor (RM_CompSwallowedCore, RM_WorldComponent_SwallowedCore).
5. **The navigator's log** cadence and its cut, the **unjoining draught's** sorting, the **biome score**.
Rejected as kernels: RM_Hwelgrue's Digest/MakeCasting/PassCasting (ThingOwner and placement), Edible/FindFood/job giver and drivers (reservations, pathing), IsMetal/HoldsMetal (def graph reads), RM_CompSheenCasting, the whole of Purge's body/hediff plumbing, TryRevealSite (quest engine), RM_TheRotFront and the settings applier (reflection edits of other mods' defs), the Proof classes (bridge hooks).

## 2. Kernels + fuzz
Extracted (call sites call the kernel with the same expressions; every Scribe label unchanged):
- `src/RimMandrake/TheRot/Source/RM_TheRotKernel.cs` (GutSweep/OverCap/RotBoost, SwallowState + Begin/BeginStranger/Tick/KnockNext/BellyOpens/Clear/EarnedAcid/KnockKindFor, GutMotherTick/Burn/RestUntil/VatAccepts, Claim/PingDue/IntegrityAfterHit/DropsRuined/RangeFactor, EntriesDue/LogReads/CutLogOnDeath/CampaignTileIndex, Sort/PurgeTicks/ScarSeverity, BiomeScore), in `RM_TheRot.csproj`'s Compile list.
  Callers changed: RM_Hwelgrue, RM_HwelgrueSwallow, RM_GutMother, RM_SwallowedCore, RM_NavigatorLog, RM_Unjoining, RM_BiomeWorker_TheRot.
Defects: none found in these rules; extraction and fuzz turned up nothing that disagrees with the design text. Observations, NOT changed (design calls / not measurable offline):
- **The core claim is one-shot and order-sensitive.** A hwelgrue's first sweep either claims the world's core or never does (`claimChecked` is saved), and the claim refuses a hwelgrue that is over the map cap. It works today only because RM_Hwelgrue.xml lists RM_CompGutDigest (which destroys an over-cap hwelgrue) before RM_CompSwallowedCore. The lint now pins that order.
- **The core can be lost for good with no kill:** if the carrier leaves the game without dying (a map abandoned with it on it) `carrierId` stays set and `spent` stays false, so nobody can ever carry the core again. Not reachable by the kernel, UNMEASURED live.
- **An engine appearing pings at once**, so deconstructing and rebuilding a grav engine farms log entries (one ping per rebuild). By construction of PingDue.
- **A site entry whose quest fails to generate is lost:** the entry is read, `sitesRevealed` does not move, so the next site entry takes that tile; the failed entry's site is never revealed.
- Three pre-existing compiler warnings (CS0108: the comps' `ParentHolder` hides `ThingComp.ParentHolder`); build output is otherwise clean.
Fuzz: `src/RimMandrake/TheRot/Source/TheRotFuzz/{TheRotFuzz.cs,Program.cs,RimMandrakeTheRot.Fuzz.csproj}`, wrapper `src/RimMandrake/Utils/selftest_therot_fuzz.py`
(families gut | swallow | vat | core | log | unjoin | units; --fuzz-scale/--fuzz-seed/--fuzz-only).
Invariants:
- gut: the clock is exactly sweeps x 250 with something in the gut, a casting is due exactly at the interval, an empty gut holds no clock; interval >= 2500; OverCap == (others >= cap, 0 with the creature off), never for a factioned one; rot boost 0 unless multiplier > 1 and rate > 0, else rate x (mult-1) x 250.
- swallow: digest ticks equal an independent reference and never go under the creature's minimum; the inside clock equals ticks held; the time-left fraction is in [0,1] and never rises; finish exactly at the digest length (earlier only if the victim died); knock gaps follow 900 -> 180 with the time left (never under 180 apart), volume in [0.25, 1] x loudness, kind by 0.66 / 0.33, animals scrabble; the belly opens exactly when damage reaches the threshold; release acid in [5, 60]; a stranger has 2-6 hours left; clearing zeroes everything.
- vat: the clock moves only with a body inside and fuel left after the burn, 250 per rare tick, done at the digest length after at least that many active ticks; fuel never negative; accept refused when full / off / unusable; a split rests exactly restHours; busy iff holds or resting.
- core: at most one carrier ever, its id never changes, none after the core is spent (including the proof's spent-with-no-carrier), none that is factioned, over the cap or off the campaign tile; the ping clock gives next = now + interval, a grav engine appearing pings at once, nothing early; integrity never rises and floors at 0; ruined iff under the threshold; range factor 1 + bonus x integrity/100 (1 with the option off).
- log: entries read in order, never past the log, only ever catching up to pings / perEntry (a slower setting never un-reads), none once spent or cut; campaign tile index follows sites revealed; cut once, letter only if anything was heard.
- unjoin: Sort over all 16 combinations (symbiont = listed or marked symbiont, parasite = listed or carries the marker, a husk only for a symbiont).
- units: casting / ping / purge / vat tables, digest rises with body size, scar never kills the part, biome score (warmer and wetter score lower, edges, impassable, water).
- A coverage line checks 20 interesting events all fired (a casting, an over-cap kill, a release, a stranger, a vat finish, a dormant stall, a claim, a carrier death, an engine ping, a site reveal, a cut letter, ...).
Seeds: default 15,503 cases / 681k steps in 5.3 s; `--fuzz-scale 12`: 186,003 cases / 8.17M steps in 62 s, all green (the swallow family steps tick by tick and dominates: scale 25 would exceed a 2 minute call).
Mutation (each planted, caught, reverted; files compared byte-identical afterwards; 4 s sleep before each run):
- R1 empty gut keeps its clock: gut FAIL. R2 a factioned hwelgrue over the cap: gut FAIL. R3 digest one tick early, R4 belly opens only above the threshold, R5 knocks never speed up: swallow FAIL. R7 vat accepts while full, R6 dormant vat still digests: vat FAIL. R8 a second carrier may claim: core FAIL. R11 cut letter with nothing heard: log FAIL. R12 husk for every removal: unjoin FAIL. R13 acid lerp reversed: units FAIL.
- R9 (engine appearing does not ping at once) and R10 (spent core claimable) were NOT caught on the first pass: the model never required the immediate ping, and `spent` with no carrier id is only reachable from the bridge proof. Both gaps closed (an explicit check, and a SpendNoCarrier action) and both now FAIL. R6 first showed R5's failure (a stale staged build inside the 2 s rsync window) and was re-run clean with a longer pause.

## 3. Lint
`src/RimMandrake/Utils/selftest_therot_lint.py` over the generic `moddefs_lint.py`, which gained for this mod: checks of custom Def types written as `<RimMandrake.TheRot.X>` tags and of `<li>` items of `List<int/float/bool>` fields. Counts: 55 classes, 24 XML class refs, 13 Class= nodes, 4 list items, 9 .cs == csproj Compile list, 29 RM_ literals, 71 Scribe labels with no duplicates, 41 settings fields (defaults == Scribe defaults), 22 slider settings each read by something other than their own screen, 18 DefOf fields, 24 named def lookups, 4 swallow-clock Scribe labels. Extras: navigator log (8 entries, 4 site entries, indices in range, none twice), unjoining targets (every RM_ hediff exists, none both parasite and symbiont), kernel purity, and the comp-order pin (GutDigest before SwallowedCore). Findings on the tree: 0 (two initial false positives, toil debug names, fixed in the lint). Self-proof: 15 planted breaks (misspelt class, misspelt Def type tag, misspelt field child, non-numeric list item, site entry past the log, csproj without the kernel, bogus def literal, duplicate Scribe label, settings default drift, renamed swallow label, Unity import in the kernel, missing unjoin target, missing named def, unread slider setting, claim comp ahead of the cap comp) each caught.

## 4. Build
`python3 src/RimMandrake/Utils/winbuild.py src/RimMandrake/TheRot/Source/RM_TheRot.csproj`: 0 errors, 3 pre-existing CS0108 warnings. DLL + .srchash modified, NOT committed (rebuild after committing: the kernel file is untracked until then). The TheRotFuzz project builds on net8.0 with 0 errors.

## 5. How to run
- `python3 src/RimMandrake/Utils/selftest_therot_fuzz.py [--fuzz-scale 12] [--fuzz-seed N] [--fuzz-only gut|swallow|vat|core|log|unjoin|units]`
- `python3 src/RimMandrake/Utils/selftest_therot_lint.py`
- Trap: wait >= 4 s between editing the kernel and re-running (the staging rsync `--modify-window=2` can build a stale copy).
