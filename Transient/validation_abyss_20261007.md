# Abyss offline validation, 2026-10-07 (FOUNDRY, uncommitted, no bridge)

## 1. Survey (3.8k lines in src/RimMandrake/Abyss/Source; the existing BroodSelfTest drives RM_BroodWakeLogic.cs and is left alone)
Chosen kernels (all were inline expressions in map components/comps tangled with Verse/Unity):
1. **The Dark**: temperature -> darkness curve, outdoor pocket noise, lane/phantom clearance, murk hediff hysteresis, weather gating (RM_MapComponent_Dark).
2. **Lamps shared by two controllers**: the Dark shrinks a building lamp (with a remembered baseline), a krizzak dims the same lamp (RM_MapComponent_KrizzakDimming).
3. **Timers/state machines**: gust controller + gharrek feeding, storm call (rumble -> flash -> maybe a summ), soundscape scheduler, hidden-ship cover with cooldown + probe schedule/scan bookkeeping.
4. **Fold-lamp lane** geometry + its touched-cell grid; **cryptid** ring cells (3+ cairns within 2.9), exchange payout, phantom pockets; **summ sunburn**; **biome score**; etchfall tries.
Rejected as kernels: RM_BroodLair/RM_BroodEgg (RM_BroodWakeLogic.cs already is the pure part and has its own selftest; the rest is spawn/lord plumbing), RM_ShipWreck (stock dictionary + bill deletion, engine), RM_GenStep_DurrgakSigns (random placement on a Map), RM_CompDurrgak/Cairn (RadialPattern + engine reads), RM_CompLightAversion (PsychGlow + pathing), RM_CompQuillHackle (stunner), RM_AbyssSoundHook, RM_HeatFoldingDiscovery (research manager + sight lines). They stay with the live chains.

## 2. Kernels + fuzz
Extracted (call sites call the kernel with the same expressions; every Scribe label unchanged):
- `src/RimMandrake/Abyss/Source/RM_AbyssKernel.cs` (RM_DarkKernel: curve, DarknessAt, MurkStepFor, Lamp + DarkLampPass + KrizzakFeed/Recover/AtFloor, LayLane + ClearGrid, CircleCells, ExchangeValue/Goods, PhantomClearance, SunStep, EtchTries, BiomeScore)
- `src/RimMandrake/Abyss/Source/RM_AbyssStateKernel.cs` (GustState/RM_GustKernel incl. GharrekStep, StormState/RM_StormKernel, SoundState/RM_SoundKernel, CoverState/RM_CoverKernel)
  both in `RM_Abyss.csproj`'s Compile list. Callers changed: RM_MapComponentDark, RM_CompKrizzak, RM_GustController, RM_CompGharrek, RM_MapComponentShipCover, RM_AbyssSoundscape, RM_AbyssLight, RM_AbyssCryptid, RM_CompSummHide, RM_MapComponentEtchfall, RM_AbyssBiome.
Defects found while extracting/fuzzing (FIXED unless noted):
1. **Stale "shrunk" memory.** `LampPass` remembered a lamp's baseline when the Dark shrank it and only forgot it on the restore path; when the Dark cleared while the setting stayed on, the main loop restored the radius and the entry lived for the life of the lamp. Kernel now forgets it when the lamp is back at full size. (Hygiene only; no visible effect.)
2. **Exchange stack count could overflow to nothing.** `Mathf.FloorToInt(value * share / price)` of a float past int range is int.MinValue, so an absurdly valuable item paid no goods at all. Now floored in double and saturated at the stack limit. (Latent: needs a value over about 1.7e11.)
Observations, NOT changed (design calls):
- **The cryptid's exchange under-pays big items.** The file header and spec say "goods of about its value" but each rung is one stack, so the payout caps at 1600 + 90 + 142.5 silver-equivalent (50 components, 75 tholin, 75 steel). Measured with the shipped prices: share of the value taken that comes back is 50: 99%, 100: 98%, 500: 85%, 1000: 62%, 5000: 37%.
- **A lit lamp can rest up to 0.15 tiles under its true radius.** The pass skips changes smaller than LampSlack (0.15), including the final step back to full size while the setting is on (it snaps exactly only when the Dark setting is off). Cosmetic.
- **ForceGust(ticks) is a gust of at least 120 ticks, not `ticks`.** The sample's end test ends a forced gust as soon as the wind is under 1.1x its average and 120 ticks have passed, and caps every gust at 900, so ForceGust(5000) lasts at most 900 and in calm wind about 120. The proof call uses 300.
- Equivalent mutant: the `!probeAlive` guard on a probe spawn is unreachable (a probe lives 1 day, the next one is scheduled 3-6 days out), so removing it changes nothing.
Fuzz: `src/RimMandrake/Abyss/Source/AbyssFuzz/{AbyssFuzz.cs,Program.cs,RimMandrakeAbyss.Fuzz.csproj}`, wrapper `src/RimMandrake/Utils/selftest_abyss_fuzz.py`
(families dark | lamp | lane | cryptid | cover | gust | storm | sound | units; --fuzz-scale/--fuzz-seed/--fuzz-only).
Invariants:
- dark: darkness in [0,1], 0 without the Dark / off map / in the Unveiling, roofed cells ignore the noise, warmer is never darker, lane/phantom only clear, full clearance is clear; murk present iff target >= 0.03, added/removed exactly then, severity moves only when a step (0.05) away and ends within it.
- lamp: radius in [0, baseline]; a krizzak never takes a lamp under 25% of what it found; the Dark never touches a krizzak's lamp; a second pass at the same inputs changes nothing; with the Dark off a shrunk lamp returns exactly and forgets; recovery waits 600 idle ticks and spends the entry only when back at full size.
- lane: every cell equals an independent column-walk reference on random walled grids (3/5/3 wide, fade, walls stop the column), touched list == nonzero cells, no duplicates, Reset zeroes everything.
- cryptid: ring cells equal a brute-force Euclid count of cairns within 2.9; exchange value 0.8..1.3 x max(5, value); goods <= stack limits, paid <= value, remainder consistent, value only left unspent when the steel stack is full; phantom profile 1 at the centre, 0 at the radius, non-increasing.
- cover: cover tracks a double reference to 2e-5 per interval (quiet gains 1/1440, noise loses 2x), engine/option off collapses at once without touching the cooldown, nothing moves during a cooldown (and cover is 0), a lapse needs ~15 days of cover and arms exactly 3 days, a probe never arrives before 3 days into cover, never closer than 3 days to the last, next one 3-6 days out, report collapses with cooldown, seen counter symmetric.
- gust: average tracks a double EMA and stays inside the speeds seen; every start needs the 600 cooldown and 1.3x the average; count changes exactly on starts; durations 120..900; a forced gust never shortens one; each gill is fed exactly once per gust, dormant iff not in a gust, open and unfed with the option off.
- storm: flash 180..300 after a rumble and never without one, next rumble 3000..9000 out and >= 3000 apart, summ only on a flash that was queued, chance <= 0.2 x strength (never queued at strength 0), the whole schedule drops when the storm or option ends.
- sound: impact iff the gust counter changed (first sight silent, none without a controller), rustle 45..90 after an impact, grain only on the 60-tick beat and spaced 240..900 / multiplier, schedule dropped when grain stops.
- units: curve opaque <= 8 C, clear >= 14 C, half at 11, 0.84375 at 9.5 (smoothstep), symmetric; sunburn climbs to the cap, cools out, removed only at <= 0.001; lane profile; biome score gates; cover timeline (6 days to full, 3.6 days to the 0.6 threshold); huge/NaN exchange values.
- A coverage line checks 25 interesting events all fired (a probe arrived, a cover lapsed, a report collapsed it, a gust opened, a summ came, ...) or the run fails.
Seeds: default 20,506 cases / 1.44M steps in 7.4 s; `--fuzz-scale 25`: 512,506 cases / 35.5M steps in 170 s, all green (run it in the background: it exceeds a 2 minute tool call).
Mutation (each planted, caught, reverted; files compared byte-identical afterwards; 4 s sleep before each run):
- K1 stale memory (defect 1): lamp FAIL. K2 float floor overflow (defect 2): units FAIL "a huge value did not fill every stack". K3 lane ignores walls: lane FAIL with the cell. K4 krizzak without a floor: lamp FAIL. K5 murk hysteresis gone: dark FAIL. K6 linear instead of smoothstep: units FAIL. K7 ring needs 2 cairns: cryptid FAIL.
- S1 lapse arms no cooldown: cover FAIL. S2 noise decays at 1x and S8 quiet grows 1.5x: cover FAIL (after tightening the reference tolerance from 2e-3 to 2e-5: the first S2 run was NOT caught because the reference was re-synced each step with a loose bound). S3 gust ignores cooldown: gust FAIL. S4 gill refeeds: gust FAIL. S5 flash may come early: storm FAIL. S7 rustle never re-arms: sound FAIL. S6 probe ignores a live probe: not caught, equivalent mutant (see above).

## 3. Lint
`src/RimMandrake/Utils/selftest_abyss_lint.py` over the generic `moddefs_lint.py` (reuses the CreatureBehaviors parser). Counts: 77 classes, 36 XML class refs, 29 Class= nodes, 72 field children, 23 .cs == csproj Compile list (the BroodSelfTest and AbyssFuzz folders are skipped), 38 RM_ literals resolve to a defName/tag/key, 67 Scribe labels with no duplicates, 30 settings fields Scribed under their own name with their declared default, 14 kernel state fields vs the Scribe labels the saves already use (a renamed label silently resets saved state), 3 weather defs the kernel keys on + 10 named lookups exist. Findings on the tree: 0. Self-proof: 10 planted breaks (misspelt class, misspelt field child, csproj without a kernel, bogus def literal, duplicate Scribe label, settings default drift, setting never Scribed, renamed save label, Unity import in a kernel, missing weather) each caught.

## 4. Build
`python3 src/RimMandrake/Utils/winbuild.py src/RimMandrake/Abyss/Source/RM_Abyss.csproj`: 0 warnings, 0 errors. DLL + .srchash modified, NOT committed; rebuild after committing (the two kernel files are untracked, so the stamp covers a different tree once they are added). The AbyssFuzz project builds on net8.0 with 0 errors.

## 5. How to run
- `python3 src/RimMandrake/Utils/selftest_abyss_fuzz.py [--fuzz-scale 25] [--fuzz-seed N] [--fuzz-only dark|lamp|lane|cryptid|cover|gust|storm|sound|units]`
- `python3 src/RimMandrake/Utils/selftest_abyss_lint.py`
- Trap: wait >= 4 s between editing a kernel and re-running (the staging rsync `--modify-window=2` can build a stale copy).
