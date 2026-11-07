# Instruments that return a confident wrong number — RimMandrake

Moved from the project `CLAUDE.md` on 2026-10-11 (weekly cleaning), text unchanged except heading levels. CLAUDE.md keeps a one-line rule and points here. Entries state what IS: delete a line the moment it turns false, never annotate it.

The general method is the global skill `~/.claude/skills/confident-wrong-numbers`; these are this repo's measured instances. 🔑 Any count that is round, zero or alarming is a query bug until a sanity probe proves the instrument can see.

## Instruments that return a confident wrong number

- 🔴 **A ledger event's key is `id`, NOT `item`.** `e.get("item")` returns `None` for every
  event, so a hand-rolled census over `model.read()` reports **0** and looks like a real
  finding. Measured 2026-09-26: a sitting census printed "0 sitting items in the ledger"
  when there are 9. Inspect one event's keys before deriving anything
  (`json.dumps(ev[0])`), or use `rimflow show`/`next`/`queue <SEAT>` (the queue views are gitignored caches since
  2026-10-02; `rimflow queue` renders before printing).
- 🔴 **A creature census must read DESCRIPTIONS, never defNames.** Our naming convention is
  invented exotic words, so a name-match for `RM_OssuaryShrimp` finds nothing while the
  creature ships as `RM_Fessk`. Measured 2026-09-26: two of the Grey Deep's three "unbuilt"
  anchors were fully built, and the wrong answer was stated to the owner before the
  descriptions were read.
- 🔴 **`jawa/get_defs` takes `defs` as a STRING `"DefType/DefName"`.** A list raises
  `System.InvalidCastException: Object must implement IConvertible` and returns
  `success: false`. ⚠️ And a check that substring-matches the payload reads that FAILED call
  as **ABSENT** — a false negative that in one pass would have failed all 22 biomes while
  looking like a catastrophic finding. Read the tool's own `success` / `foundCount` /
  `notFound` fields, and treat "could not ask" as UNMEASURED, never as "looked and it is
  not there".
- ⚠️ **`python.exe` emits CRLF.** A value captured into a shell variable is `"PRESENT\r"`,
  every `[ "$X" = "PRESENT" ]` fails, and a clean result records as a failure. Pipe through
  `tr -d '\r\n'`.
- ⚠️ **`grep -c` prints `0` AND exits 1 on no match**, so `$(grep -c … || echo 0)` emits
  **two** lines and every count becomes `"0\n0"`. Take `| head -1`.
- ⚠️ **A `grep -F` spot-check for a quoted phrase fails on LINE WRAPPING.** Verifying that a
  doc preserved an owner's sentence verbatim reported two of eight phrases missing; both
  were present, wrapped across lines. Search a distinctive short fragment, not a clause.
- ⚠️ **`rimbridge_client.py` cannot reach the bridge from WSL at all** — RimBridge binds
  Windows loopback and WSL2 is NAT-mode, so retrying never helps and the error says nothing
  about whether the game is running. Any bridge call runs under `python.exe`.
- ⚠️ **`modset_builder.py --apply` REFUSES while `Player.log` was touched in the last 3
  minutes.** In a kill-then-swap loop the kill must come FIRST, or the tier write fails
  every cycle. (Its refusal message used to claim the game rewrites `ModsConfig` on exit —
  false, corrected 2026-09-26.)

- 🔴 **`northstar.parse()` returns a DICT.** `getattr(w, "must_show")` yields `None` → `len()` 0,
  so all four VALIDATED walks read as "0 bars" — an alarming wrong number that looks like a
  catastrophic finding. Use `w["must_show"]`. 🔑 A count that is conveniently *or* alarmingly
  round is a query bug until proven otherwise, and the alarming direction is the one you will
  believe without checking.
- 🔴 **`ls <dir> | wc -l` answers 0 for a directory that does not exist**, so a "queue is empty" claim can be
  a wrong-path claim wearing a number. The artpipe queue is `<state>/pending/` (state dir `D:\ClaudeWork\rimmandrake\artpipe`,
  outside git since 2026-10-02; `artpipe_state.py where` prints it and its counts) — it held
  **182** jobs when a count of `artpipe/queue/` reported 0, and that figure was stated to the owner. ⇒ Prove
  the path (glob `*.json`, which errors loudly) before repeating any count of zero. ⚠️ **And the artpipe
  daemon does not run on the Mac**, so queueing work here generates nothing until the Desktop runs it.
- 🔴 **The shell here is zsh, and `for x in $NAMES` does NOT word-split** — it loops **ONCE** on
  the whole string. An artpipe art-existence check over 18 plant names ran exactly one query on a
  nonsense 18-word string and reported a confident **"0 of 18"** having checked nothing
  (2026-09-23). The real answer was also zero, which is why the bug nearly survived. ⇒ Write
  multi-subject sweeps in **python**, never a shell loop over a variable, and 🔑 **give every
  such sweep a SANITY PROBE** — search for something you know is present (`korrum` 17,
  `stoneback` 52, `hawkbat` 91 occurrences) and print the hit counts beside the result. A search
  that finds nothing must first prove it can find something. ⚠️ Same family as `$R file …` with
  `R="python3 …/cli.py"`, which fails with `no such file or directory: python3 …` because zsh
  passes the whole string as one word.
  ✅ **Fixed at the root:** `rimflow` and `modcheck` are commands on PATH (`~/.local/bin`) — call them directly; never `R="python3 …"; $R`.
- ⚠️ **A bare unprefixed defName in a design roster is the CONVENTION, not a defect.** MEASURED
  2026-09-23: **144** such rows across **18 of 29** rosters, 94 creatures — and the live biome XML
  does the same deliberately (`RUT_FeverWood.xml`: `<Urusai MayRequire="mlie.starwarsanimalcollection">`),
  because that IS the donor's defName. Our `RSW_Urusai` is a separate **absorbed port**
  (`MLIE_FAUNA_ABSORPTION_1` Wave C). ⇒ A homeless-creature census must match **both** spellings
  or it reads a cast creature as homeless — but ⛔ **never file the bare name as a naming
  defect**: one such note was filed and had to be retracted the same week.
- 🔴 **Never scan `ModsConfig.xml`.** `grep -c '<li>'` returned **48** where the parsed active count
  was **631** (2026-09) — it counts lines containing the tag, and that file puts many elements on one line.
  Parse it (`ET.parse(p).find("activeMods")`). Snapshots are in
  `infrastructure/state/modlists/`; the live file is a Windows path **unreachable from the Mac**,
  so a laptop claim about the LIVE list is UNMEASURABLE and must say so (2026-09-17).
- 🔴 **"Is there a mod that does X?" is NOT answered by matching packageIds, and NOT by the
  ACTIVE list.** Measured 2026-09-26, twice wrong to the owner's face: he said a mod existed
  that dives a gravship into the ocean; a keyword sweep over active packageIds returned "none"
  and that was reported as fact. The mod is **`GravTide`** — packageId `gravtide.mod`, which
  contains no diving substring, **installed but not active**, 665 C# source files and ~140
  Docs files, and it had already solved the entire problem. ⇒ **Scan every installed
  `About.xml` by `<name>` AND `<description>`, across BOTH roots** — `…/common/RimWorld/Mods`
  and `…/workshop/content/294100` (1,434 files; the sweep takes seconds). A packageId is an
  author's slug, not a description of behaviour, and an inactive mod is still installed
  evidence. 🔑 Same family as the rule below: give the sweep a **sanity probe** — "53 mods
  mention gravship" is what proved it could see. ⛔ And when the owner says a thing exists and
  your instrument says it does not, **suspect the instrument**, not him.
- 🔴 **An existence test is not an identity test, and a fixed line number is not a field.**
  `[ -e src/RimMandrake/Pits ]` passes while that folder holds only `__pycache__` — the mod
  merged into FlowWorks at `cade628c1`, yet its checklist is **VALIDATED with 12 binding bars**
  against nothing. Test `$dir/About/About.xml`. Likewise a sweep reading `subject:` from **line
  2** reported zero failures across 78 walks while missing the only file still broken, because
  `AtmosphericBase.md` carries it on line 3. Read the first matching line, never an index. Both
  checkers returned a confident clean bill of health (2026-09-17).
- 🔴 **A texture glob on `*south*` reads the MASK as often as the art.** `X_southm.png` is the
  colour mask, saturated across ~99% of its pixels by convention (MEASURED 259,344 of 262,144),
  so `glob(...)[0]` in filesystem order decides whether a head appears to carry baked colour —
  it inverted 4 of 7 decisions in one pass, and the tell was male vs female Cathar reading 253
  vs 0 on structurally identical files. **Measure `_south.png` alone** (2026-09-17).
- 🔴 **An `RM_` twin's BiomeDef carries ONLY generic vanilla filler — its real campaign cast is
  PATCH-ADDED**, from `UtinniPatches/Patches/WildAnimals_<Biome>.xml` targeting
  `Defs/BiomeDef[defName="RM_<Biome>"]/wildAnimals`. So **reading BiomeDefs alone sees the wrong
  half of a twin**: `RM_Greentide`'s own roster is Warg/Muffalo/Elephant/Cobra/Megaspider/Rat/Hare
  and contains none of the campaign cast. This is why two fauna censuses published **52** and both
  were wrong — eight species were invisible, `RSW_Gizka` read as 2 homes against a real 4, and
  `RUT_Sytheclaw` hid the **Pyrelands**, the one biome it was actually authored for. ⇒ Resolve a
  patch's target from the **PatchOperation's own `xpath`** and read species from its `<value>`;
  never by hunting for a nearby `<xpath>` element, which mis-assigns silently. 🔑 And two passes
  agreeing on a round number is **not** corroboration when both share an instrument.
- ⚠️ **`ls` on `design/RimStarWars/canon_references/` is not a canon test.** It is a curated set, not a census,
  **by design**, so absence proves nothing — `Mynock`, `Worrt`, `Gelagrub`, `Urusai`,
  `LongtailGorg`, `Woolamander` and `Gornt` are canon Star Wars creatures with no entry. Routing a
  canon-vs-ours decision off that directory listing would have rewritten canon text for all seven.
- **A number you brief a subagent with will come back to you.** A census reported "2 of
  the canon entries ruled"; the figure at the time was **25**. Two later agents measured 25 and
  both explicitly refused to adjust to the briefed figure — the correct behaviour. When
  two subagents disagree on a number, measure it yourself before it becomes a fact.
  ⚠️ And the count MOVES: it was 29 on 2026-09-28, so never cite a ruling
  count from this file. A `## ruling` section carries the literal placeholder
  `(empty — owner has not reviewed this …)`, so a non-empty test reports **136** and is wrong;
  exclude the placeholder.
- **`run_selftests.py` "SKIPPED N" is mostly caching, not a defect.** Its summary line reads
  `N SKIPPED as unchanged`: a test whose inputs have not changed since its recorded PASS is reused,
  not rerun. Only an excluded-by-name or off-tier skip is a gap. Read each SKIPPED line's reason
  before alarming (2026-10-13).

- 🔴 **`CurCelestialSunGlow(map)` freezes after the clock is set BACK.** PerformanceOptimizer caches it
  (`Optimization_GenCelestial_CurCelestialSunGlow`, a refresh-tick cache); after `jawa/time_set_ticks` rewinds
  the clock, every read returns the last value from the later time. 2026-10-20: a "locked sun" proof read
  0.7535 at five clock times — exactly vanilla's glow at the +15 d sample taken before the rewind (recomputed
  offline). For a time scrub call `GenCelestial.CelestialSunGlow(PlanetTile,int)` with explicit ticks, or
  only move the clock forward. Detail: `design/RimMandrake/world_physics_audit_2026-10-20.md` §5.

- 🔴 **`findings_fold.md`'s `generated` stamp is not liveness.** An unchanged rerun writes nothing (the designed one-file
  publication), so while the testq lane is paused the file stays days old with the fold ticking every minute
  (FINDINGS_FOLD_REVIVE_STALE_SINCE_NOV1: 1319 `unchanged since` runs 2026-11-01→03 during the Steve NVMe swap). Ask the
  journal: `journalctl --user -u testq-tick.service | grep findings_fold | tail`; every run prints `unchanged since <generated>`,
  a write, or `UNMEASURED`.
- 🔴 **`modcheck run_suite` returns each component's result under the key `verdict` (PASS/FAIL/UNMEASURED), not `status`.** A `--mock` harness that reads `c['status']` sees `None` and FAILs every row. Read `verdict`, and prove the mock can fail by feeding it one broken proof line.
- ⚠️ **Mock placeholder frames look like a capture set.** `validation_hose`'s `FlowWorks_HosePipeWalk_*` frames in `Transient/fw_hoses_walk` (and `owner_review_stage/hoses_*`) are flat green 'MOCK SCREENSHOT' images with real-looking names, sizes and dates. Count colours or open one before using any as evidence; real join close-ups need `system_screenshot.py` or the bridge.
- 🔴 **Key def lookups by (defType, defName), never defName alone.** `Shelf` and `FirefoamPopper` name both a ThingDef and a PrefabDef in 1.6 Data, so a defName-keyed index read Shelf's size from the wrong def. Vanilla also has no PawnKindDef `Mech_Centipede` (it is `Mech_CentipedeBlaster/Burner/Gunner`): resolve pawn kinds against the Defs before staging (`scenarios/common.def_facts`).
- 🔴 **`validate_patch.py --defs` reads the LIVE `ModsConfig.xml` as the load set.** While a modcheck or peer test has it on the 16-mod MINIMAL list, a run over a repo mod reports hundreds of false ERRORs ('ParentName resolves to no def', 'xpath matches 0 nodes') for every def whose parents live in an inactive mod. Parse `<activeMods>` (never grep) before believing a `validate_patch` ERROR sweep; `ModsConfig.xml` describes the NEXT load.
- ⚠️ **Counting which north-star bars a FlowWorks check claims with a regex over `shows=[...]` undercounts** (it said 35 unclaimed; `runner.load_validation(mod_dir).components_declared()` plus `floor.uncovered_shows` said 0). Use the modcheck functions, never a grep.
- 🔴 **A gate that decides 'ours' by namespace prefix (RimMandrake/RimStarWars/RimUtinni) is blind to our ports that keep their donor namespace** (KoltoTank, RuthlessPursuingMechanoids, LongHunger, StructureInjectionsRUT, ...): `modcheck/launch_gate` passed a stale DLL in those mods clean. Any 'is this ours' allowlist needs a drift census against the namespaces of `git ls-files src/*.cs`, as `selftest_launch_gate` now has.
- 🔴 **A selftest that runs a tool's real `main()` against a temp fixture still reaches every side channel the fixture did not patch.** `deploy_custom_mods`' telemetry emit wrote 159 fake 'deploy ModA/ModNew' events (30% of all deploy events) into the real telemetry inbox; `delegated_digest --pre-launch --bogus` wrote `Transient/delegated_digest_<date>.FAILED.md` because its failure path fell back to production paths when argument parsing itself failed. Gate side channels on the REAL target (realpath == the game's Mods folder) and recover the caller's paths with `parse_known_args` before any fallback (`delegated_digest._partial`).
- ⚠️ **A sanity probe that counts untracked files goes RED in a scratch clone.** `selftest_game_art.py` counts `REPO/Transient/biome_ffar/*_sheet_*.html` and needs >=20; `Transient` is untracked, so a scratch clone (11 sheets vs 115 in bench) fails for a reason unrelated to the change. Read the failing line before treating RED as a regression; the probe should skip with UNMEASURED when `Transient` is a partial copy.
- 🔴 **A measurement is wrong until a second agent re-checks it.** Confident numbers (a critic's "unreliable", a mutation run's "the tester is too harsh" where 13 of 17 "wrong" rejects were real bugs) reversed under an independent check three times in one session. Every trial number goes through a different agent before anyone acts on it or relays it to the owner; the owner's rule is "a different agent tests what was built".
- 🔴 **A "nothing wrong" over a list must be checked for "the list was empty because the lister failed".** `except OSError: return default` meant for "file missing" also swallows IsADirectory/permission errors (catch `FileNotFoundError` only); a selftest doing `json.loads(m.group(1)) if m else []` passes vacuously when its regex stops matching (make the missing block a FAIL plus a total-count sanity probe); an append-only lint that iterates only the shards present at the checked revision cannot see a shard deleted or truncated to zero bytes (`ledger_lint.py` now walks the union of rev and base shard lists, and an unknown `--rev` exits 2, though the pre-push hook still treats exit 2 as pass).
- **A count of ledger items must name its filter, and `doing` is not "being worked".** The same day, 118 (v1-targeted via `model.replay`) and 123 (all targets, `rimflow_metrics wip`) were both "doing"; and of those 123, 0 had a live lease (49 lapsed, 74 never leased). Any "work in flight" view must filter on a live lease, not on state.
- 🔴 **A hand-labelled selftest corpus can read 1.00 while the same regex hook reads 0.19 to 0.90 on unseen real cards** (`block_delegated_cards`: the old rows were short ledger topics, real cards carry a preamble). A recall bar on a tuned classifier needs a fresh sealed read each round; the rows you tune on stop measuring.
- **Check when the mechanism that produces an event began before comparing its rate across a rule change.** v2 read 0.0% reopened only because a failed run could not reopen a closed item until the earned-close rule began 2026-11-01 17:30Z. A noise band built from week-to-week spread over a ramping period is trend, not noise.
- 🔴 **A watchdog that shares the watched process's fatal dependency dies with it.** After a power-off, testq steward AND steward-watch both crashed in `escalate()`->`model.read()` on torn ledger lines before writing their heartbeats (87 min silent). Write the heartbeat before, or regardless of, any read that can raise.
- **A findings_fold note's first/last times are ledger event times; the reviewed fold stamps done-record finish times.** They differ by the ingest delay on every row, so compare counts, not times, to judge a merge. The fold's "reopen" is row-level: under exact signatures both T13_desperate_toxic_last reopens were NEW failures.
- **A census must record the kind read back off the pawn, not the kind requested.** `jawa/spawn_pawn` reports success with `Spawned 5/5 <kind>` while the census shows substituted vanilla colonists (4 of 80 spawns, every one bare-handed). Counting the requested kind blamed a non-existent defect for days. Report the substitution rate as its own number.
- **A def dump can lack fields the game has.** Before concluding a def declares no value from a `None`, check the coverage of the capture you are actually reading: a dump once carried no `statBases` for any def and the missing field was a capture gap, not a property of the defs (later captures widened the format, and a ColorDef gap was never re-checked). Settle price or stat questions from the mod XML, a live `jawa/thing_stats` call or a widened dump.
- **A denylist keyed on defName passes clean while the rule is broken.** Mods reskin the same real thing under their own defName (Core `Tortoise` banned, `GRimTortoise` shipped across six biomes and the verify passed 28 of 28). When a denylist check passes, scan the candidate pool's human-readable labels and comments for the banned concept and diff against the list; report the gap as a defect in the list.
- **`./game` printing "bridge silent" is UNMEASURED, not down.** The probe's bridge check returns `None` when `GABP_SERVER_PORT` is unset (it is unset in every seat window), the display prints that as silent and forces a LOADING reading on a game that is up. Settle it by looking for the literal `GABP server running` banner in `Player.log`, or resolve host, port and token from the log the way the rimbridge client does; a bare `127.0.0.1` connect is the wrong test.
- **Do not trust a generator's claim to own its output.** Before running any generator whose output is committed, `cp` the output, run, `diff`, and restore if surprised: generators have silently reverted hand curation, refused for reasons their error text got wrong, and re-introduced duplicates. A "nothing lost" check at def level misses fields stripped from rebuilt defs, and abstract defs have no `defName` (they key on `Name`), so a vanished abstract silently discards its children. Fix by porting the curation into a data table the generator owns, or declare the file hand-owned and make the generator refuse to overwrite it. The generator's input decays too (it re-emitted `PatchOperationFindMod` blocks for retired mods).
- **An audit tool that reads a generator instead of its output is suspect by construction.** One tool reported 0 unmeasured while a live harvest had 16 of 49 kinds rolling bare: it was reading the generator's stale table while the generator emitted from a different one. No known-answer check catches this, because the tool answers a different question than the one asked. Before trusting any audit, ask which file it reads and whether that is the file that deploys; diff its printed values against the deployed XML. A stale field that looks inert may still feed another calculation.
- **A pipeline stage that yields ZERO rows for one input prints a footnote, and every downstream count still reads healthy.** Two biomes (251 tiles) had no animal cast at all because neither was in `biome_terrain.csv`: `biome_fit.py` scored 0 candidates, `allocate_cast.py` had an empty pool and printed a `0/4, 0/8, ...` line as a footnote under a heading about biomes being slightly short. Producing 0 of 29 is a different event from 27 of 29 and needs a different report. Assert coverage against the authoritative inventory every run (name every input the artifact does not cover, with its size); make the downstream stage treat a missing input as the FULL amount of work, not as absent; never let a per-item shortfall report absorb a total absence; and check the FIRST stage, since the hole was inserted where the input list was built, several stages before it was noticed.
- 🔴 **A biome is done when the PLAYER'S tiles carry the content, not when the mod contains it.** A biome def with zero painted tiles, zero fauna or zero flora, a gene machine that hands out placeholder genes, and mechanics built onto a def that owns 0 tiles all pass their own item's `## verify`. Check what the planet or the player actually receives, and diff a sheet's Owed list (design intent) against the ledger before believing anything is finished. Hand-kept tables of biome bindings and hardcoded painted-def lists rot the same way: derive them from the world CSV.
- ⚠️ **A name-matched census undercounts built content; read descriptions, not defNames.** A donor-prefix test (`RSW_<donor>`) can never find a port because a port RENAMES the def (105 "to author" was really 2); our invented exotic names mean a defName match reports a fully built roster as empty (an ossuary shrimp ships as `RM_Fessk`). Also: a `measure sql` query with a wrong column name returns an error LINE that a row-grep reads as 0 rows, and `ET.iterparse` with `el.clear()` on every element yields features with all-None names.
- 🔴 **A donor-name scan over rosters over-reports: it said 182 stale rows, the real figure was 32.** The other 150 are bare names (`Kreetle`, `Bantha`) that resolve against an ACTIVE donor; only the `BMT_` subset is dead, because only `biomesteam.biomescaverns` is inactive. Before filing a pattern as a defect, measure whether it is the convention (144 bare rows across 18 of 29 rosters mirror the live biome XML on purpose). Multi-subject sweeps: write them in python, never `for x in $NAMES` under zsh (no word-split: one query on one 18-word string printed a trusted "0 of 18"), and print a sanity probe with a known hit count beside the result (`korrum` 17, `stoneback` 52, `hawkbat` 91). The corrected sweep then found a label clash a defName check misses: `RM_Mirrash` against the shipped label `mirrash veil`.
- 🔴 **`grep` here is ugrep: `grep -vxFf patterns big_file` with a large pattern set (8 MB ledger shard) fails with 'exceeds complexity limits' on stderr and prints a count of 0,** which reads as 'all lines present'. For line-membership checks against a big file use a Python set, never `grep -Ff`.
- 🔴 **OOB counters here are cgroup ceilings, not RAM.** Read `memory.events` per slice before blaming the machine; 118 MB kills of identical size are likely a selftest's planted cap. And `oom_attribution.py --since` (any `journalctl -k --since X`) reads ONLY the current boot (`-k` implies `-b`): a window reaching an earlier boot silently returns that boot's kernel kills as nothing (10-30..11-01 read 0 kills; 17 were there). Use `journalctl _TRANSPORT=kernel --since X --until Y`, or `oom_attribution.py --boot -2` for one older boot.
- 🔴 **A selftest that loads a big dump with `except Exception: continue` goes partially blind under parallel workers.** A MemoryError on `ThingDef.json` was swallowed, the def closure shrank (33356 -> 25684) and vanilla defs (MedicineIndustrial, Steel) read as outside. Catch `ValueError` only; let MemoryError crash.
- 🔴 **`validate_patch.py` reports 'OK - 0 errors' for xpaths nested inside a CUSTOM PatchOperation class** (e.g. a Mod Settings gate like `RSW_PatchOperationStarWarsPatchesSetting`): it does not descend into unknown operation classes, so a misspelt defName there passes (probe: defName `AncientTankZZ` still read OK). Check gated xpaths yourself (lxml against the target def file) or unwrap them for validation.
- 🔴 **The GSS aerial census has NO top-level `links`/`fallen` keys.** Links and fallen cords live under `anchors[].links` / `anchors[].fallen`, totals in `spansUp`/`spansCut`/`fallenCords`, and since the fix `shockCells`/`shockOrphans`/`shockCellList` report 'what is shocking' directly. A probe reading `c.get('links')`/`c.get('fallen')` reads 0/0 next to any wire (use `validation_aerial.live_fallen_wires(census)`); that blind read filed three GSS_FALLEN_WIRE shock tickets. `proof_all` leaves live fallen wires on the shared map (the M2-M3 span is left CUT after save_load; call `validation_aerial.clear_live_fallen` and re-string before any later scene), so a later phase's pawns can be shocked there: SITE debris, not MOD.
- 🔴 **Report the live UNMEASURED rate per distinct (item, criterion, sha) key, and split admission refusals from slot-spending runs.** The headline 55% of `live/runs.jsonl` rows mixed three things: 319 of 592 UNMEASURED rows never took the bridge (`relentless_live.run()` returns UNMEASURED for deploy gaps, stale builds and running-load gaps before `bridge take`), and 590 rows came from 264 distinct keys. Per distinct key the rate is 34%; rows that actually used a game slot are 26%, led by 'proof exited N: did not measure' (proof-script defects). Otherwise a fix can 'win' by moving rows out of the denominator.
- 🔴 **A rate's denominator must be the stated window.** The fast-testing baseline divided 230 PASS+FAIL rows by 84.6 h, but its own window (2026-11-02T04:14Z..2026-11-06T03:01Z) is 94.8 h: the baseline is 2.43 measured rows/h, not 2.7 (`proof_cost.py throughput --source runs`).
- 🔴 **Before sizing a sea/floor item, run TerminalBiomes `validation.sea_catch_alive_checks()` and check which tier the item is about.** A brief saying 'the floor half is large' was already done (0 catch gaps on all 4 RM_ seas); RUT_ seas always show full gaps because they are frozen.
- **`testing_metrics.py` max idle gap is truncated at its window end.** It reported 137.8 min for a gap that really ran 166 min (from testq `done/` timestamps). A gap still open at the window edge is a lower bound: mark it so, or measure from job timestamps.
- **testq `done/` holds every FINISHED job, not every DONE one:** on one day the 104 files were 88 DONE + 16 INVALID. Say 'finished' for a `done/` count and read the result status for DONE.
- **A `findings_fold.fold` run without the testq done records (`read_done`) cuts DIFFERENT signatures,** so every `findings_fold decide` (keyed on sig) misses and decide-routed findings read untriaged. A walled proof of `flow.untriaged_findings` must read `/mnt/d/ClaudeWork/rimmandrake/testq/done`.
- **Before fixing a mod for a one-run live FAIL, tally that row across every testq result (`D:/ClaudeWork/rimmandrake/testq/done/*.json`).** One row's '+0.8 double quench' was 3 FAILs then 9/9 PASS on unchanged C#, and one FAIL hit a baseliner the suspected doer never touches. Judge a row at the moment its action ends (from a trace), not after settle ticks a later drink can fill.
- **The modcheck gate's composed test list (profile) is in every chain key, so a full-list shadow sweep can never reuse a targeted-profile record.** A first full-list sweep read `would_skip` 0 of 93 (90 'no record at this key') though 75 chains had targeted records from the same day: that 0% is structural, not a gate measurement. Measure with a SECOND full-list run at an unchanged key.
- **A FlowWorks extension row that pours liquid and reads the channel dry may be a map-size problem, not a mod bug.** Check `isSinkCell`/`sinkTransferredTotal` in `jawa/flowworks_excavation_report` and the map size: a non-situational run anchors at the map centre (50, 200) of a map 100 wide, the 10-cell sink band starts at `sizeX - 10`, and the extension plot grid needs about 156 cells a side. `_prep_plot` now refuses UNMEASURED when a plot's buffered rect leaves the map interior and the pour row refuses UNMEASURED on sink squares. The map size is not in the run JSON: back-solve it from sink readings, never assume 250.
- **testq job logs and records are UTC, but `ssh ls`/`date` on SteveDesktop print Pacific.** A WeatherSuite mtime of 02:34 is 10:34Z, after the 09:37Z failures it seemed to predate; convert with `date -d` or `ls --time-style=+%s` before ordering a file against a job. A file's own mtime is preserved by the deploy, so the DIRECTORY mtime is the deploy time. A launch-gate refusal is read from the kept game's `Player.log`, so it can blame a job whose own list never named the mod: read the attempt that last loaded the game, not the one refused.
- 🔴 **`joint_check`'s `net:x,z` probe returns the FIRST role-bearing thing in a cell.** A sprinkler head on a pipe cell reads as a pipe, and a bleed well (`Building_LiquidDrill`, role None) reads as nothing. Count ports by def, not by `net:` role.
- **Anchor the basename when counting harnesses.** A glob ending `validation.py` matched 132 files but only 129 are mod harnesses (3 are `selftest_*_validation.py`, 2 more are hook files); count exactly `/validation.py`.
- **A deleter that acts on 'the search found nothing' must check the search's exit code, not just stdout.** `grep`/`git grep`/`git check-ignore` exit 0 = hits, 1 = none, anything else = the search did not run. Two deleters read a failed search as 'nothing here' (`saves_prune.py` deleted cited saves; `seat_sync.py` let `reset --keep` delete stop-tracked files). Collect the errors, print UNMEASURED, and refuse the destructive step while any search is blind.
- **Publishing a derived report and its machine table: one file, whole-tuple keys.** (1) Two files cannot be published atomically by two renames (a reader or crash between sees two generations): publish ONE file (embed the machine table as the last fenced block of the human report). (2) A truncated display hash used as a group key merges different failures (a 40-bit `S`+10 hex signature collided on `assert code 703455` vs `assert code 856996`): group by the whole tuple; a hash is only a label, use all of sha256 over `json.dumps(list(tuple))`, not NUL-joined fields. (3) Collapsing or stripping whitespace in a failure normaliser is a merge rule, not hygiene (the whitespace can be the bug). (4) 'missing' must mean `FileNotFoundError` only; any other read error or a partial previous table aborts. (5) A no-write test must snapshot the whole tree BEFORE the first run, with a probe that the comparator sees a new file.
- **`journalctl --user -u <unit>` exits 0 with NO lines when systemd does not know the unit**, so an empty journal reads as 'no errors / no 429s'. Check `systemctl --user show -p LoadState --value <unit>` == `loaded` before trusting an empty journal.
- **A rimflow `spawn` event carries the item id in `name`, not `id`.** A scan of ledger events on `e.get('id')` misses a spawned item until a later event names it (`relentless.ledger_has`).
- **A redaction grammar cannot tell a safe name from free text** (`swordfish`, `cost_nine` pass any letters-only grammar). Show only names issued by a trusted registry (repo defNames, ledger ids) and drop+count the rest. An exemption list (model names) must never exempt a key the account registry itself names, and a present-but-null registry map is malformed, not absent.
- **A failure that clusters by subject may be caused by concurrency, not the subject.** 9 `size_mismatch` failures at N=16 clustered perfectly by species; re-running the same jobs at N=3 gave 5/5 ok. Re-run failures at the safe setting before blaming their content or prompt.
- **A census over a rendered queue view double-counts.** Items appear under more than one section (449 rows, 389 unique ids). Dedupe by id before any count.
- **A calibration fitted on two hand-picked points cannot tell a reflection from a rotation.** `feature_drawcenter_audit.py` used (x,y,-z), passed on Fall Line and The Breaks, and moved 60 correct labels off their regions; the engine's `LongLatOf` gives a 90-degree rotation. Use calibration points the wrong model fails on.
- **A torn-write fault test that writes n/2 bytes of equal-length rows tears nothing:** with an even row count, half the chunk ends exactly on a newline. Tear inside a line (for example half of the first line) and mutation-check that the test fails without the repair.
- **Keep secrets out of a view with an ALLOW-list of the fields it may carry, never a denylist of words.** A word-list check for token leaks passed a blind digest that still said 'B | 93 % of the week used', which has no token word.
- **`glob.glob` swallows directory-listing errors: an unreadable directory reads as zero files.** When an empty result would be reported as a measured zero, enumerate with `os.scandir` (which raises) and report UNMEASURED on `OSError`.
- **A census that sets a KPI baseline must persist its per-item labels and state its interval.** The 'keep-going 31/day' baseline was 40% of a hand-labelled sample of n=140, so its 95% interval is about 25-37/day and a drop to the 26 target is inside the noise; the 140 labels were never saved, so it cannot be re-scored. Re-tag with the same tagger.
- **A simulation invariant that reads the same flag that gates the behaviour can never fail.** 'No two iterations at once' checked via `serial_busy` (the flag the loop itself tests) still showed overlap 0 when the gate was broken; a separate counter incremented where work begins and decremented where it ends showed 912. Also key per-iteration risks by (lane, iteration number), not (ticket, attempt), or one ticket collides forever.
- **Review a probe's body, not just its name.** Tester probe P3o in `foundry_arena/tp/bin/probes.py` wrote an empty file (placeholder never replaced), so its PASS on the original proved nothing.
- **Prove the acceptance gate on the correct answers before freezing a trial:** run the reference fix through the whole real gate and require PASS on every task (a gate once failed 18 of 26 reference fixes after the freeze).
- **A trial run from a working tree cannot stay frozen.** Rules on commits do not stop a pull, and gate and judge subprocesses load whatever is on disk. Pin a read-only copy and hash it.
- **One model read is a noisy gate: roughly 1% FP and recall .85-.94 is what it delivers here.** Adding a veto clause against a dev false positive trades recall one for one (dev FP 0 and recall .93+, then the next blind unanimous read gave recall .85, 3 FP of 387); rereading with unchanged prompts moved one 15-row set from recall .93 to .87 and another from 3 FP to 0. A zero-FP gate on hundreds of rows will not pass by prompt tuning: give a model gate enough rows that one flipped row cannot cross the bar, or score several reads.
- **A texPath-like XML field can be an art contract that C# fills in** (`RM_PipePoles` `spanTexPath` `RimMandrake/FlowWorks/PipePole/{look}/PipeSpan`; GSS `AerialMaterials.PipeMats` does `Replace("{look}")` over `AerialStyles.Looks`). A lint that reads it as a literal path reports a permanent MISSING gap; `texture_gap_lint` judges each expansion, with values read from the C# source.
- **Fit and calibration targets must come from the same instrument and window as the comparison.** The rimflow_v3_sim backtest missed because (1) ticket counts are not a constant unit of work in v2 (helpers/close 5.2, 3.3, 1.5 over three consecutive weeks; owner msgs->items 4%/34%/62%), so ticket-count cells missed by ~3x while work cells (helpers, ITE, vfail) passed; and (2) targets came from a 7 d window ending 10-27T06:25Z but `v3_vs_v2` measures the tag week to 10-26T14:00Z (file events 1545 vs 1281, close 806 vs 647), so the fit expected 17-20% more closes than its reference.
- **Completion measures go blind to the owner's strongest evidence unless they read it in its own shape.** `mod_completion.py` run 1 scored GimmeSomeSlack 29% working / 3% art because (a) a whole-mod owner verdict ("all looks great! Verified.") names no def, so per-def matching credited nothing; (b) GSS draws cords from C# texture literals, so 80 of 120 slots looked unused; (c) review-sheet picks live only in `*.decisions.json` sidecars, never in the art ledger's protected set; (d) close-sha and title-mention attribution pulled in bridge-tool, Pyrelands and TESTENV_ harness items as GSS bugs. Fix: credit whole-mod owner walks to every name present at the walk sha, read Source literals and human-timestamped sidecar slot rulings, require the close commit to touch only the one mod and the title key in the subject position, exclude TESTENV_. GSS has only 6 explicit owner accepts; the rest is 'seen in a walk'.
- **Unread is not empty, and a stale report is not a fresh pass.** A reader that returns a count returns None when it could not read (check the exit code and output shape) and the caller prints UNMEASURED and fails. Check the source exists before comparing tallies (absent == absent printed 'same'); delete a subprocess's output file before running it (a crashed lint passed on yesterday's clean report). Seen: `sync_test_mods.remote_tally` ignoring ssh's exit code (ssh down tallied (0, 0)), `preflight_bridge` O14. Also a selftest outside `run_selftests` SEARCH_ROOTS never runs.
- **A donor's defName prefix is not its own:** `AB_` is Alpha Biomes AND live Alpha Memes (PreceptDef `AB_MiningYield_VeryHigh`), and Alpha Biomes declares abstract `Name="Plant_Bush"`, shadowing vanilla's def. Find a retired donor's dead references by an inventory of its defNames filtered against a donor-off def dump (`retired_donor_refs.py`), and match its abstracts only as `ParentName`, never by prefix.

## Doc rot and stale gates

- **A doc can describe defects that were fixed before the doc was written.**
  `liquids_framework_design.md` (2026-09-13) blocked all engine work on three flood
  defects fixed 2026-09-02 and closed at `747b0025`, and an open item was still telling
  FOUNDRY to re-fix them. Check the code and the ledger before believing any doc's
  "engine status" — and check whether an open item is asking for work already done.
- 🔴 **A gate cited by NAME outlives the item it names — check the item's state.**
  `NAMING_SCHEME_EXECUTION_1` closed **2026-08-31** at `54a8e28d` on the owner's word,
  yet ~20 live docs still said "do not rename ahead of it" 16 days later, which is why
  FlowWorks (named by ruling 20) kept shipping as `fluidcanals` for those 16 days. Now
  `mandrake.rm.flowworks` (RE-VERIFIED 2026-09-19 against `About.xml` and the live
  Mods folder). Owner: *"That file may be VERY old… do not accept stale info."*
  Sweep: `STALE_RENAME_GATE_SWEEP_1`.
- 🔴 **memwatch's `oom_kill ... in rm-harness.slice` does not mean the slice ran out.** cgroup counters are hierarchical and a
  short test's scope is gone before the next sample; the kernel's `oom_memcg=` names the limit that fired. On 2026-11-03 all 19
  were the planted `bomb.py` in `selftest_run_selftests.py`, which reads PASS. Read kills with `src/RimMandrake/Utils/oom_attribution.py`;
  measured: `infrastructure/state/facts/oom_kills_2026-11-03.md`.
- **A frozen design sheet can hold an image that is false for the setting, not merely stale** (a line that "its mother is the reason ships sink" in a world with no nautical ships). Check a metaphor against the WORLD, not just against other docs; a phrase can be consistent everywhere and still describe nothing that exists.
- **Trust a registry sheet's status only after resolving its defNames.** The mineral registry CSV listed three rows as BUILT whose defs were gone (two salts merged into `RM_RawSalt`, fulgurite excised) and `RUT_TibannaGas`, which never existed. A free-text `defs` column cannot be checked; the CSV now has a machine-read `bindings` column that `gen_mineral_registry.py` resolves against the def dump plus the repo XML.

## placeholder_lint texture tags
- **`placeholder_lint` is blind to some texture tags and masks.** `texpaths()` keeps only tags whose name contains 'texpath', so it misses `texturePath` (terrain), `pollutedTexturePath` and `leaflessGraphicPath` (`donor_retire_census` srctex saw 21 of 55 StandIn texts; use `donor_retire_census.py standin`, any tag; `regen_eligibility`/`bulk_accept_renders` TEXTAGS lacked them too, so the gate refused those twins as 'renamed'). Its MASK regex `m(_(south|east|north|west))?$` matches any stem ending in lowercase m (AB_MangrovePalm), silently dropping real pictures as masks; RimWorld masks are `<path>_m` and `<path>_<facing>m` (`donor_retire_census.MASK_STEM`).
