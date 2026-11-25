# Instruments that return a confident wrong number — RimMandrake

This file moved from the project `CLAUDE.md` on 2026-10-11 (weekly cleaning). On 2026-11-23 the text was rewritten in
Simplified Technical English, and each measurement stayed (item `RIMMANDRAKE_REWRITE_INSTRUMENT_TRAPS_KEEP_EVERY_MEASUREMENT`).
`CLAUDE.md` keeps a one-line rule and points here. Each entry states what is true now. When an entry turns false,
delete the line at once. Never annotate a false line.

The general method is the global skill `~/.claude/skills/confident-wrong-numbers`. This file holds the measured
instances of this repo. Any count that is round, zero or alarming is a query bug until a sanity probe proves the
instrument can see. A sanity probe is a search for something that you know is present, with its hit count printed
beside the result.

## Instruments that return a confident wrong number

- 🔴 **A ledger event's key is `id`, NOT `item`.** `e.get("item")` returns `None` for every event. So a hand-rolled
  census over `model.read()` reports **0**, and the 0 looks like a real finding. Measured 2026-09-26: a sitting census
  printed "0 sitting items in the ledger" when there were 9. Before you derive anything, inspect the keys of one event
  (`json.dumps(ev[0])`). Or use `rimflow show`/`next`/`queue <SEAT>`. The queue views are gitignored caches since
  2026-10-02; `rimflow queue` renders a view before it prints the view.
- 🔴 **A creature census must read DESCRIPTIONS, never defNames.** Our naming convention uses invented exotic words. So
  a name match for `RM_OssuaryShrimp` finds nothing, while the creature ships as `RM_Fessk`. Measured 2026-09-26: two
  of the three "unbuilt" anchors of the Grey Deep were fully built. The wrong answer went to the owner before anyone
  read the descriptions.
- 🔴 **`jawa/get_defs` takes `defs` as a STRING `"DefType/DefName"`.** A list raises
  `System.InvalidCastException: Object must implement IConvertible` and returns `success: false`. Also, a check that
  substring-matches the payload reads that failed call as **ABSENT**. That false negative looks like a catastrophic
  finding: in one pass it would have failed all 22 biomes. Read the tool's own `success` / `foundCount` / `notFound`
  fields. Treat "could not ask" as UNMEASURED, never as "looked and it is not there".
- 🔴 **`jawa/list_pawns` field `hostile` reads only the pawn's FACTION, so a mad animal reads `hostile: false`.** The tool
  computes `pawn.Faction != null && pawn.Faction.HostileTo(player)`. A wild manhunter has no faction. Measured 2026-11-24 on a
  three-day watch of the Pyrelands walk save: one ashwallow was in `AttackMelee` from tick 826,083 to 850,483 and downed
  every colonist, and the watch read `hostile` 0 at every sample. A run then reported "0 hostile at every sample". A
  "no hostile at build" gate that counts this field passes a save with a mad animal in it. To see a mad animal, also
  read the pawn's `MentalStateDef` (`jawa/thing_read`), until the bridge fix
  `RIMMANDRAKE_WIDEN_LIST_PAWNS_HOSTILE_TO_MAD_ANIMALS_ZERO_WHILE_BITING` lands.
- ⚠️ **`python.exe` emits CRLF.** A value captured into a shell variable is `"PRESENT\r"`. Then every
  `[ "$X" = "PRESENT" ]` fails, and a clean result records as a failure. Pipe the value through `tr -d '\r\n'`.
- ⚠️ **`grep -c` prints `0` AND exits 1 on no match**, so `$(grep -c … || echo 0)` emits **two** lines. Every count
  then becomes `"0\n0"`. Take `| head -1`.
- ⚠️ **A `grep -F` spot-check for a quoted phrase fails on LINE WRAPPING.** One check tested that a doc kept an owner's
  sentence word for word. The check reported two of eight phrases missing. Both phrases were present, wrapped across
  lines. Search for a distinctive short fragment, not a clause.
- ⚠️ **`rimbridge_client.py` cannot reach the bridge from WSL at all** — RimBridge binds Windows loopback, and WSL2 is
  NAT-mode. So a retry never helps. The error says nothing about whether the game runs. Run every bridge call under
  `python.exe`.
- ⚠️ **`modset_builder.py --apply` REFUSES while `Player.log` was touched in the last 3 minutes.** So in a
  kill-then-swap loop, do the kill first. Otherwise the tier write fails every cycle. (The refusal message once claimed
  that the game rewrites `ModsConfig` on exit. That claim was false, and was corrected 2026-09-26.)

- 🔴 **`northstar.parse()` returns a DICT.** `getattr(w, "must_show")` yields `None` → `len()` 0. So all four
  VALIDATED walks read as "0 bars". That alarming wrong number looks like a catastrophic finding. Use
  `w["must_show"]`. A count that is conveniently *or* alarmingly round is a query bug until proven otherwise. The
  alarming direction is the one that you will believe without a check.
- 🔴 **`ls <dir> | wc -l` answers 0 for a directory that does not exist**, so a "queue is empty" claim can be a
  wrong-path claim wearing a number. The artpipe queue is `<state>/pending/`. The state dir is
  `D:\ClaudeWork\rimmandrake\artpipe`, outside git since 2026-10-02. `artpipe_state.py where` prints the state dir and
  its counts. The queue held **182** jobs when a count of `artpipe/queue/` reported 0, and that figure went to the
  owner. Before you repeat any count of zero, prove the path: `ls <dir>/*.json` errors loudly in bash and
  in zsh when the path is wrong (Python's `glob.glob` does not). Also, **the artpipe
  daemon does not run on the Mac**. So work queued on the Mac generates nothing until Archmagi (the Windows
  desktop) runs it.
- 🔴 **In zsh, `for x in $NAMES` does NOT word-split** — it loops **ONCE** on the whole string. The shell differs: the
  agent's Bash tool on Archmagi ran bash on 2026-11-23, where the loop does split; his login shell is zsh. An
  artpipe art-existence check over 18 plant names ran exactly one query, on a nonsense 18-word string. The check
  reported a confident **"0 of 18"** and had checked nothing (2026-09-23). The real answer was also zero, so the bug
  nearly survived. Write multi-subject sweeps in **python**, never as a shell loop over a variable. **Give every such
  sweep a SANITY PROBE**: search for something that you know is present (`korrum` 17, `stoneback` 52, `hawkbat` 91
  occurrences), and print the hit counts beside the result. A search that finds nothing must first prove that it can
  find something. `$R file …` with `R="python3 …/cli.py"` is the same family. That command fails with
  `no such file or directory: python3 …`, because zsh passes the whole string as one word.
  **Fixed at the root:** `rimflow` and `modcheck` are commands on PATH (`~/.local/bin`). Call them directly; never
  `R="python3 …"; $R`.
- ⚠️ **A bare unprefixed defName in a design roster is the CONVENTION, not a defect.** Measured 2026-09-23: **144**
  such rows across **18 of 29** rosters, 94 creatures. The live biome XML does the same on purpose
  (`RUT_FeverWood.xml`: `<Urusai MayRequire="mlie.starwarsanimalcollection">`), because the bare name is the donor's
  defName. Our `RSW_Urusai` is a separate **absorbed port** (`MLIE_FAUNA_ABSORPTION_1` Wave C). So a homeless-creature
  census must match **both** spellings. Otherwise the census reads a cast creature as homeless. But **never file the
  bare name as a naming defect**: one such note was filed and had to be retracted the same week.
- 🔴 **Never scan `ModsConfig.xml`.** `grep -c '<li>'` returned **48** where the parsed active count was **631**
  (2026-09). `grep -c` counts lines that contain the tag, and that file puts many elements on one line. Parse the file
  (`ET.parse(p).find("activeMods")`). Snapshots are in `infrastructure/state/modlists/`. The live file is a Windows
  path, **unreachable from the Mac**. So a laptop claim about the LIVE list is UNMEASURABLE, and the claim must say so
  (2026-09-17).
- 🔴 **"Is there a mod that does X?" is NOT answered by matching packageIds, and NOT by the ACTIVE list.** Measured
  2026-09-26; the answer was wrong twice to the owner's face. The owner said that a mod existed that dives a gravship into the
  ocean. A keyword sweep over active packageIds returned "none", and that was reported as fact. The mod is
  **`GravTide`**, packageId `gravtide.mod`, which contains no diving substring. The mod is **installed but not
  active**, with 665 C# source files and ~140 Docs files. GravTide had already solved the entire problem. So **scan every
  installed `About.xml` by `<name>` AND `<description>`, across BOTH roots**: `…/common/RimWorld/Mods` and
  `…/workshop/content/294100` (1,434 files; the sweep takes seconds). A packageId is an author's slug, not a
  description of behaviour. An inactive mod is still installed evidence. The zsh entry above and the donor-name-scan entry
  below state the same rule: give the sweep a **sanity probe**. "53 mods mention gravship" is what proved that the sweep could
  see. When the owner says that a thing exists and your instrument says that it does not, **suspect the instrument**,
  not him.
- 🔴 **An existence test is not an identity test, and a fixed line number is not a field.**
  `[ -e src/RimMandrake/Pits ]` passes while that folder holds only `__pycache__`. The mod merged into FlowWorks at
  `cade628c1`, yet its checklist is **VALIDATED with 12 binding bars** against nothing. Test `$dir/About/About.xml`. In
  the same way, a sweep read `subject:` from **line 2**. The sweep reported zero failures across 78 walks, and it
  missed the only file still broken: `AtmosphericBase.md` carries `subject:` on line 3. Read the first matching line,
  never an index. Both checkers returned a confident clean bill of health (2026-09-17).
- 🔴 **A texture glob on `*south*` reads the MASK as often as the art.** `X_southm.png` is the colour mask. By
  convention a mask is saturated across ~99% of its pixels (MEASURED 259,344 of 262,144). So with `glob(...)[0]`, the
  filesystem order decides whether a head appears to carry baked colour. In one pass the glob inverted 4 of 7
  decisions. The tell: male and female Cathar read 253 vs 0 on structurally identical files. **Measure `_south.png`
  alone** (2026-09-17).
- 🔴 **An `RM_` twin's BiomeDef carries ONLY generic vanilla filler — its real campaign cast is PATCH-ADDED**, from
  `UtinniPatches/Patches/WildAnimals_<Biome>.xml` targeting `Defs/BiomeDef[defName="RM_<Biome>"]/wildAnimals`. So
  **reading BiomeDefs alone sees the wrong half of a twin**. The own roster of `RM_Greentide` is
  Warg/Muffalo/Elephant/Cobra/Megaspider/Rat/Hare, with none of the campaign cast. For this reason two fauna censuses
  published **52**, and both were wrong. Eight species were invisible. `RSW_Gizka` read as 2 homes against a real 4.
  `RUT_Sytheclaw` hid the **Pyrelands**, the one biome that it was authored for. Resolve the target of a patch from the
  **PatchOperation's own `xpath`**, and read the species from its `<value>`. Never hunt for a nearby `<xpath>`
  element: that method mis-assigns silently. Two passes that agree on a round number are **not** corroboration when
  both share an instrument.
- ⚠️ **`ls` on `design/RimStarWars/canon_references/` is not a canon test.** That directory is a curated set, not a
  census, **by design**. So absence proves nothing. `Mynock`, `Worrt`, `Gelagrub`, `Urusai`, `LongtailGorg`,
  `Woolamander` and `Gornt` are canon Star Wars creatures with no entry. A canon-vs-ours decision routed off that
  directory listing would have rewritten canon text for all seven.
- **A number you brief a subagent with will come back to you.** A census reported "2 of the canon entries ruled"; the
  figure at the time was **25**. Two later agents measured 25, and both explicitly refused to adjust to the briefed
  figure. Their refusal is the correct behaviour. When two subagents disagree on a number, measure the number yourself before
  it becomes a fact. Also, the count moves: it was 29 on 2026-09-28. So never cite a ruling count from this file. A
  `## ruling` section carries the literal placeholder `(empty — owner has not reviewed this …)`. So a non-empty test
  reports **136** and is wrong. Exclude the placeholder.
- **`run_selftests.py` "SKIPPED N" is mostly caching, not a defect.** Its summary line reads
  `N SKIPPED as unchanged`. A test whose inputs did not change since its recorded PASS is reused, not run again. Only
  a skip that is excluded by name or off-tier is a gap. Before you alarm, read the reason on each SKIPPED line
  (2026-10-13).

- 🔴 **`CurCelestialSunGlow(map)` freezes after the clock is set BACK.** PerformanceOptimizer caches the value
  (`Optimization_GenCelestial_CurCelestialSunGlow`, a refresh-tick cache). After `jawa/time_set_ticks` rewinds the
  clock, every read returns the last value from the later time. 2026-10-20: a "locked sun" proof read 0.7535 at five
  clock times. That value is exactly vanilla's glow at the +15 d sample, taken before the rewind (recomputed offline).
  For a time scrub, call `GenCelestial.CelestialSunGlow(PlanetTile,int)` with explicit ticks, or move the clock forward
  only. Detail: `design/RimMandrake/world_physics_audit_2026-10-20.md` §5.

- 🔴 **`findings_fold.md`'s `generated` stamp is not liveness.** An unchanged rerun writes nothing (the designed
  one-file publication). So while the testq lane is paused, the file stays days old, and the fold ticks every minute
  (FINDINGS_FOLD_REVIVE_STALE_SINCE_NOV1: 1319 `unchanged since` runs 2026-11-01→03 during the Steve NVMe swap). Ask
  the journal: `journalctl --user -u testq-tick.service | grep findings_fold | tail`. Every run prints
  `unchanged since <generated>`, a write, or `UNMEASURED`.
- 🔴 **`modcheck run_suite` returns each component's result under the key `verdict` (PASS/FAIL/UNMEASURED), not
  `status`.** A `--mock` harness that reads `c['status']` sees `None` and FAILs every row. Read `verdict`. Prove that
  the mock can fail: feed it one broken proof line.
- ⚠️ **Mock placeholder frames look like a capture set.** `validation_hose`'s `FlowWorks_HosePipeWalk_*` frames in
  `Transient/fw_hoses_walk` (and `owner_review_stage/hoses_*`) are flat green 'MOCK SCREENSHOT' images. The frames
  have real-looking names, sizes and dates. Before you use any frame as evidence, count its colours or open it. Real
  join close-ups need `system_screenshot.py` or the bridge.
- 🔴 **Key def lookups by (defType, defName), never defName alone.** In 1.6 Data, `Shelf` and `FirefoamPopper` each
  name both a ThingDef and a PrefabDef. So a defName-keyed index read Shelf's size from the wrong def. Also, vanilla
  has no PawnKindDef `Mech_Centipede`; the kinds are `Mech_CentipedeBlaster/Burner/Gunner`. Before staging, resolve
  pawn kinds against the Defs (`scenarios/common.def_facts`).
- 🔴 **`validate_patch.py --defs` reads the LIVE `ModsConfig.xml` as the load set.** A modcheck or peer test can put
  that file on the 16-mod MINIMAL list. While the file is on that list, a run over a repo mod reports hundreds of false
  ERRORs ('ParentName resolves to no def', 'xpath matches 0 nodes'). The tool reports a false ERROR for every def whose
  parents live in an inactive mod. Before you believe a `validate_patch` ERROR sweep, parse `<activeMods>` (never grep).
  `ModsConfig.xml` describes the NEXT load.
- ⚠️ **Counting which north-star bars a FlowWorks check claims with a regex over `shows=[...]` undercounts.** The regex
  said 35 unclaimed. `runner.load_validation(mod_dir).components_declared()` plus `floor.uncovered_shows` said 0. Use
  the modcheck functions, never a grep.
- 🔴 **A gate that decides 'ours' by namespace prefix (RimMandrake/RimStarWars/RimUtinni) is blind to our ports that
  keep their donor namespace** (KoltoTank, RuthlessPursuingMechanoids, LongHunger, StructureInjectionsRUT, ...).
  `modcheck/launch_gate` passed a stale DLL in those mods clean. Any 'is this ours' allowlist needs a drift census
  against the namespaces of `git ls-files src/*.cs`. `selftest_launch_gate` now has such a census.
- 🔴 **A selftest that runs a tool's real `main()` against a temp fixture still reaches every side channel the fixture
  did not patch.** Two cases:
  - The telemetry emit of `deploy_custom_mods` wrote 159 fake 'deploy ModA/ModNew' events (30% of all deploy events)
    into the real telemetry inbox.
  - `delegated_digest --pre-launch --bogus` wrote `Transient/delegated_digest_<date>.FAILED.md`. Argument parsing
    itself failed, and then the failure path fell back to production paths.

  Gate side channels on the REAL target (realpath == the game's Mods folder). Before any fallback, recover the
  caller's paths with `parse_known_args` (`delegated_digest._partial`).
- ⚠️ **A sanity probe that counts untracked files goes RED in a scratch clone.** `selftest_game_art.py` counts
  `REPO/Transient/biome_ffar/*_sheet_*.html` and needs >=20. `Transient` is untracked. So a scratch clone (11 sheets
  vs 115 in bench) fails for a reason that is not related to the change. Before you treat RED as a regression, read
  the failing line. The probe should skip with UNMEASURED when `Transient` is a partial copy.
- 🔴 **A measurement is wrong until a second agent re-checks it.** Confident numbers (a critic's "unreliable", a
  mutation run's "the tester is too harsh" where 13 of 17 "wrong" rejects were real bugs) reversed under an
  independent check three times in one session. Every trial number goes through a different agent before anyone acts
  on it or relays it to the owner; the owner's rule is "a different agent tests what was built".
- 🔴 **A "nothing wrong" over a list must be checked for "the list was empty because the lister failed".** Three cases:
  - `except OSError: return default`, meant for "file missing", also swallows IsADirectory/permission errors. Catch
    `FileNotFoundError` only.
  - A selftest that does `json.loads(m.group(1)) if m else []` passes vacuously when its regex stops matching. Make
    the missing block a FAIL, and add a total-count sanity probe.
  - An append-only lint that iterates only the shards present at the checked revision cannot see a shard that was
    deleted or truncated to zero bytes. `ledger_lint.py` now walks the union of the rev and base shard lists, and an
    unknown `--rev` exits 2. But the pre-push hook still treats exit 2 as a pass.
- **A count of ledger items must name its filter, and `doing` is not "being worked".** On the same day, 118 items
  (v1-targeted, via `model.replay`) and 123 items (all targets, `rimflow_metrics wip`) were both
  "doing"; and of those 123, 0 had a live lease (49 lapsed, 74 never leased). Any "work in flight" view must filter
  on a live lease, not on state.
- 🔴 **A hand-labelled selftest corpus can read 1.00 while the same regex hook reads 0.19 to 0.90 on unseen real
  cards** (`block_delegated_cards`: the old rows were short ledger topics; real cards carry a preamble). A recall bar
  on a tuned classifier needs a fresh sealed read each round. The rows that you tune on stop measuring.
- **Check when the mechanism that produces an event began before comparing its rate across a rule change.** v2 read
  0.0% reopened for one reason only: a failed run could not reopen a closed item until the earned-close rule began
  2026-11-01 17:30Z. A noise band built from week-to-week spread over a ramping period is trend, not noise.
- 🔴 **A watchdog that shares the watched process's fatal dependency dies with it.** After a power-off, testq steward
  and steward-watch both crashed in `escalate()`->`model.read()` on torn ledger lines. Both crashed before they wrote
  their heartbeats (87 min silent). Write the heartbeat before any read that can raise, or regardless of that read.
- **A findings_fold note's first/last times are ledger event times; the reviewed fold stamps done-record finish
  times.** The two times differ by the ingest delay on every row. So to judge a merge, compare counts, not times. The
  fold's "reopen" is row-level: under exact signatures, both T13_desperate_toxic_last reopens were NEW failures.
- **A census must record the kind read back off the pawn, not the kind requested.** `jawa/spawn_pawn` reports success
  with `Spawned 5/5 <kind>`, while the census shows substituted vanilla colonists (4 of 80 spawns, every one
  bare-handed). For days, a count of the requested kind blamed a defect that did not exist. Report the substitution
  rate as its own number.
- **A def dump can lack fields the game has.** A `None` can look like proof that a def declares no value. Before you
  conclude that, check the coverage of the capture that you actually read. One dump carried no `statBases` for any
  def: the missing field was a capture gap, not a property of the defs. Later captures widened the format. A ColorDef
  gap was never checked again. Settle price or stat questions from the mod XML, a live `jawa/thing_stats` call or a
  widened dump.
- **A denylist keyed on defName passes clean while the rule is broken.** Mods reskin the same real thing under their
  own defName. Core `Tortoise` was banned, `GRimTortoise` shipped across six biomes, and the verify passed 28 of 28.
  When a denylist check passes, scan the human-readable labels and comments of the candidate pool for the banned
  concept. Diff the result against the list. Report the gap as a defect in the list.
- **`./game` printing "bridge silent" is UNMEASURED, not down.** The probe's bridge check returns `None` when
  `GABP_SERVER_PORT` is unset, and that variable is unset in every seat window. The display prints that `None` as
  silent, and forces a LOADING reading on a game that is up. To settle the state, look for the literal
  `GABP server running` banner in `Player.log`. Or resolve host, port and token from the log, the way the rimbridge
  client does. A bare `127.0.0.1` connect is the wrong test.
- **Do not trust a generator's claim to own its output.** Before you run any generator whose output is committed:
  `cp` the output, run, `diff`, and restore if surprised. Generators have silently reverted hand curation, refused for
  reasons that their error text got wrong, and re-introduced duplicates. A "nothing lost" check at def level misses
  fields stripped from rebuilt defs. Abstract defs have no `defName` (they key on `Name`), so a vanished abstract
  silently discards its children. Fix this in one of two ways: port the curation into a data table that the generator
  owns, or declare the file hand-owned and make the generator refuse to overwrite it. The generator's input decays
  too: one generator re-emitted `PatchOperationFindMod` blocks for retired mods.
- **An audit tool that reads a generator instead of its output is suspect by construction.** One tool reported 0
  unmeasured, while a live harvest had 16 of 49 kinds rolling bare. The tool read the generator's stale table, while
  the generator emitted from a different table. No known-answer check catches this, because the tool answers a
  different question than the one asked. Before you trust any audit, ask which file it reads, and whether that file is
  the file that deploys. Diff the printed values of the audit against the deployed XML. A stale field that looks
  inert may still feed another calculation.
- **A pipeline stage that yields ZERO rows for one input prints a footnote, and every downstream count still reads
  healthy.** Two biomes (251 tiles) had no animal cast at all, because neither biome was in `biome_terrain.csv`.
  `biome_fit.py` scored 0 candidates. `allocate_cast.py` had an empty pool. It printed a `0/4, 0/8, ...` line as a
  footnote, under a heading about biomes being slightly short. Producing 0 of 29 is a different event from 27 of 29,
  and needs a different report. So:
  - Every run, assert coverage against the authoritative inventory. Name every input that the artifact does not
    cover, with its size.
  - Make the downstream stage treat a missing input as the FULL amount of work, not as absent.
  - Never let a per-item shortfall report absorb a total absence.
  - Check the FIRST stage. The hole was inserted where the input list was built, several stages before anyone noticed
    it.
- 🔴 **Content is done when the player receives it in the mod, not when its item's `## verify` passes.** Each of these
  passes the `## verify` of its own item: a biome def with zero fauna or zero flora; a gene machine that hands out
  placeholder genes. Check what the player actually receives. Before you believe that anything is finished, diff a
  sheet's Owed list (design intent) against the ledger. A tile count is never the evidence: a BiomeDef of ours on 0
  tiles is the expected state until the planet is painted once, at the end (`CLAUDE.md` §A biome with zero tiles is
  not a defect). Hand-kept tables of biome bindings and hardcoded painted-def lists rot: derive them, do not keep them
  by hand.
- ⚠️ **A name-matched census undercounts built content; read descriptions, not defNames.** A donor-prefix test
  (`RSW_<donor>`) can never find a port, because a port RENAMES the def: 105 "to author" was really 2. Our invented
  exotic names mean that a defName match reports a fully built roster as empty (an ossuary shrimp ships as
  `RM_Fessk`). Two more traps:
  - A `measure sql` query with a wrong column name returns an error line. A row-grep reads that line as 0 rows.
  - `ET.iterparse` with `el.clear()` on every element yields features with all-None names.
- 🔴 **A donor-name scan over rosters over-reports: it said 182 stale rows, the real figure was 32.** The other 150
  are bare names (`Kreetle`, `Bantha`) that resolve against an ACTIVE donor. Only the `BMT_` subset is dead, because
  only `biomesteam.biomescaverns` is inactive. Before you file a pattern as a defect, measure whether the pattern is
  the convention. (144 bare rows across 18 of 29 rosters mirror the live biome XML on purpose.) Write multi-subject
  sweeps in python, never as `for x in $NAMES` under zsh. Under zsh that loop does not word-split: one query on one
  18-word string printed a trusted "0 of 18". Print a sanity probe with a known hit count beside the result
  (`korrum` 17, `stoneback` 52, `hawkbat` 91). The corrected sweep then found a label clash that a defName check
  misses: `RM_Mirrash` against the shipped label `mirrash veil`.
- 🔴 **In the agent's Bash tool on Archmagi, `grep` is ugrep (7.8.4; under `zsh -c` it is GNU grep 3.12, measured
  2026-11-23): `grep -vxFf patterns big_file` with a large pattern set (8 MB ledger shard) fails with
  'exceeds complexity limits' on stderr and prints a count of 0,** which reads as 'all lines present'. For
  line-membership checks against a big file, use a Python set, never `grep -Ff`.
- 🔴 **OOM (out-of-memory kill) counters here are cgroup ceilings, not RAM.** Before you blame the machine, read `memory.events` per slice.
  118 MB kills of identical size are likely a selftest's planted cap. Also, `oom_attribution.py --since` (and any
  `journalctl -k --since X`) reads ONLY the current boot, because `-k` implies `-b`. A window that reaches an earlier
  boot silently returns the kernel kills of that boot as nothing: 10-30..11-01 read 0 kills, and 17 were there. Use
  `journalctl _TRANSPORT=kernel --since X --until Y`, or `oom_attribution.py --boot -2` for one older boot.
- 🔴 **A selftest that loads a big dump with `except Exception: continue` goes partially blind under parallel
  workers.** A MemoryError on `ThingDef.json` was swallowed. The def closure shrank (33356 -> 25684), and vanilla defs
  (MedicineIndustrial, Steel) read as outside. Catch `ValueError` only; let MemoryError crash.
- 🔴 **`validate_patch.py` reports 'OK - 0 errors' for xpaths nested inside a CUSTOM PatchOperation class** (e.g. a
  Mod Settings gate like `RSW_PatchOperationStarWarsPatchesSetting`). The tool does not descend into unknown operation
  classes, so a misspelt defName there passes. (Probe: defName `AncientTankZZ` still read OK.) Check gated xpaths
  yourself (lxml against the target def file), or unwrap them for validation.
- 🔴 **The GSS aerial census has NO top-level `links`/`fallen` keys.** GSS is the GimmeSomeSlack mod. Links and fallen
  cords live under `anchors[].links` / `anchors[].fallen`. Totals are in `spansUp`/`spansCut`/`fallenCords`. Since
  the fix, `shockCells`/`shockOrphans`/`shockCellList` report 'what is shocking' directly. A probe that reads
  `c.get('links')`/`c.get('fallen')` reads 0/0 next to any wire; use `validation_aerial.live_fallen_wires(census)`.
  That blind read filed three GSS_FALLEN_WIRE shock tickets. `proof_all` leaves live fallen wires on the shared map
  (the M2-M3 span is left CUT after save_load), so the pawns of a later phase can be shocked there. That shock is SITE
  debris, not MOD. Before any later scene, call `validation_aerial.clear_live_fallen` and re-string.
- 🔴 **Report the live UNMEASURED rate per distinct (item, criterion, sha) key, and split admission refusals from
  slot-spending runs.** The headline 55% of `live/runs.jsonl` rows mixed three things. 319 of 592 UNMEASURED rows
  never took the bridge: the retired `relentless_live.run()` returned UNMEASURED for deploy gaps, stale builds and
  running-load gaps before `bridge take`. And 590 rows came from 264 distinct keys. Per distinct key, the rate is 34%.
  For rows that actually used a game slot, the rate is 26%, led by 'proof exited N: did not measure' (proof-script
  defects). Otherwise a fix can 'win' by moving rows out of the denominator.
- 🔴 **A rate's denominator must be the stated window.** The fast-testing baseline divided 230 PASS+FAIL rows by
  84.6 h. But its own window (2026-11-02T04:14Z..2026-11-06T03:01Z) is 94.8 h. So the baseline is 2.43 measured
  rows/h, not 2.7 (`proof_cost.py throughput --source runs`).
- 🔴 **Before sizing a sea/floor item, run TerminalBiomes `validation.sea_catch_alive_checks()` and check which tier
  the item is about.** A brief said 'the floor half is large'. That work was already done: 0 catch gaps on all 4 RM_
  seas. RUT_ seas always show full gaps, because they are frozen.
- **`testing_metrics.py` max idle gap is truncated at its window end.** The tool reported 137.8 min for a gap that
  really ran 166 min (from testq `done/` timestamps). A gap still open at the window edge is a lower bound. Mark it
  so, or measure from job timestamps.
- **testq `done/` holds every FINISHED job, not every DONE one:** on one day the 104 files were 88 DONE + 16 INVALID.
  For a `done/` count, say 'finished'. For DONE, read the result status.
- **A `findings_fold.fold` run without the testq done records (`read_done`) cuts DIFFERENT signatures,** so every
  `findings_fold decide` (keyed on sig) misses, and decide-routed findings read untriaged. A walled proof of
  `flow.untriaged_findings` must read `/mnt/d/ClaudeWork/rimmandrake/testq/done`.
- **Before fixing a mod for a one-run live FAIL, tally that row across every testq result
  (`D:/ClaudeWork/rimmandrake/testq/done/*.json`).** One row's '+0.8 double quench' was 3 FAILs, then 9/9 PASS on
  unchanged C#. One FAIL hit a baseliner that the suspected doer never touches. Judge a row at the moment its action
  ends (from a trace), not after settle ticks that a later drink can fill.
- **The modcheck gate's composed test list (profile) is in every chain key, so a full-list shadow sweep can never
  reuse a targeted-profile record.** A first full-list sweep read `would_skip` 0 of 93 (90 'no record at this key'),
  though 75 chains had targeted records from the same day. That 0% is structural, not a gate measurement. Measure
  with a SECOND full-list run at an unchanged key.
- **A FlowWorks extension row that pours liquid and reads the channel dry may be a map-size problem, not a mod bug.**
  Check `isSinkCell`/`sinkTransferredTotal` in `jawa/flowworks_excavation_report`, and check the map size. A
  non-situational run anchors at the map centre (50, 200) of a map 100 wide. The 10-cell sink band starts at
  `sizeX - 10`. The extension plot grid needs about 156 cells a side. `_prep_plot` now refuses UNMEASURED when the
  buffered rect of a plot leaves the map interior. The pour row refuses UNMEASURED on sink squares. The map size is
  not in the run JSON: back-solve it from sink readings, never assume 250.
- **testq job logs and records are UTC, but `ssh ls`/`date` on SteveDesktop print Pacific.** A WeatherSuite mtime of
  02:34 is 10:34Z, after the 09:37Z failures that the file seemed to predate. Before you order a file against a job,
  convert with `date -d` or `ls --time-style=+%s`. The deploy keeps a file's own mtime, so the DIRECTORY mtime is the
  deploy time. A launch-gate refusal is read from the kept game's `Player.log`. So the refusal can blame a job whose
  own list never named the mod. Read the attempt that last loaded the game, not the attempt that was refused.
- 🔴 **`joint_check`'s `net:x,z` probe returns the FIRST role-bearing thing in a cell.** A sprinkler head on a pipe
  cell reads as a pipe. A bleed well (`Building_LiquidDrill`, role None) reads as nothing. Count ports by def, not by
  `net:` role.
- **Anchor the basename when counting harnesses.** A glob that ends in `validation.py` matched 132 files, but only
  129 are mod harnesses (3 are `selftest_*_validation.py`). 2 more are hook files in `.claude/hooks`, outside the 132.
  Count exactly `/validation.py`.
- **A deleter that acts on 'the search found nothing' must check the search's exit code, not just stdout.** For
  `grep`/`git grep`/`git check-ignore`: exit 0 = hits, 1 = none, anything else = the search did not run. Two deleters
  read a failed search as 'nothing here': `saves_prune.py` deleted cited saves, and `seat_sync.py` let `reset --keep`
  delete stop-tracked files. Collect the errors and print UNMEASURED. While any search is blind, refuse the
  destructive step.
- **Publishing a derived report and its machine table: one file, whole-tuple keys.** Five rules:
  - (1) Two renames cannot publish two files atomically: a reader or a crash between the renames sees two
    generations. Publish ONE file: embed the machine table as the last fenced block of the human report.
  - (2) A truncated display hash used as a group key merges different failures. A 40-bit `S`+10 hex signature
    collided on `assert code 703455` vs `assert code 856996`. Group by the whole tuple. A hash is only a label: use
    all of sha256 over `json.dumps(list(tuple))`, not NUL-joined fields.
  - (3) To collapse or strip whitespace in a failure normaliser is a merge rule, not hygiene: the whitespace can be
    the bug.
  - (4) 'missing' must mean `FileNotFoundError` only. Any other read error, or a partial previous table, aborts.
  - (5) A no-write test must snapshot the whole tree BEFORE the first run, with a probe that the comparator sees a
    new file.
- **`journalctl --user -u <unit>` exits 0 with NO lines when systemd does not know the unit**, so an empty journal
  reads as 'no errors / no 429s'. Before you trust an empty journal, check that
  `systemctl --user show -p LoadState --value <unit>` == `loaded`.
- **A rimflow `spawn` event carries the item id in `name`, not `id`.** A scan of ledger events on `e.get('id')`
  misses a spawned item until a later event names the item. This trap bit the retired `relentless.ledger_has`.
- **A redaction grammar cannot tell a safe name from free text** (`swordfish`, `cost_nine` pass any letters-only
  grammar). Show only names issued by a trusted registry (repo defNames, ledger ids). Drop the rest, and count them.
  An exemption list (model names) must never exempt a key that the account registry itself names. A registry map that
  is present but null is malformed, not absent.
- **A failure that clusters by subject may be caused by concurrency, not the subject.** 9 `size_mismatch` failures at
  N=16 clustered perfectly by species. A rerun of the same jobs at N=3 gave 5/5 ok. Before you blame the content or
  prompt of a failure, rerun it at the safe setting.
- **A census over a rendered queue view double-counts.** Items appear under more than one section (449 rows, 389
  unique ids). Before any count, dedupe by id.
- **A calibration fitted on two hand-picked points cannot tell a reflection from a rotation.**
  `feature_drawcenter_audit.py` used (x,y,-z) and passed on Fall Line and The Breaks. It moved 60 correct labels off
  their regions. The engine's `LongLatOf` gives a 90-degree rotation. Use calibration points that the wrong model
  fails on.
- **A torn-write fault test that writes n/2 bytes of equal-length rows tears nothing:** with an even row count, half
  the chunk ends exactly on a newline. Tear inside a line (for example half of the first line). Mutation-check that
  the test fails without the repair.
- **Keep secrets out of a view with an ALLOW-list of the fields it may carry, never a denylist of words.** A word-list
  check for token leaks passed a blind digest that still said 'B | 93 % of the week used'. That line has no token
  word.
- **`glob.glob` swallows directory-listing errors: an unreadable directory reads as zero files.** When an empty result
  would be reported as a measured zero, enumerate with `os.scandir` (which raises). On `OSError`, report UNMEASURED.
- **A census that sets a KPI baseline must persist its per-item labels and state its interval.** The 'keep-going
  31/day' baseline was 40% of a hand-labelled sample of n=140. So its 95% interval is about 25-37/day, and a drop to
  the 26 target is inside the noise. The 140 labels were never saved, so nobody can re-score the sample. Re-tag with
  the same tagger.
- **A simulation invariant that reads the same flag that gates the behaviour can never fail.** The invariant 'No two
  iterations at once' was checked via `serial_busy`, the flag that the loop itself tests. The invariant still showed
  overlap 0 when the gate was broken. A separate counter showed 912: the counter went up where work begins and down
  where work ends. Also, key per-iteration risks by (lane, iteration number), not (ticket, attempt). Otherwise one
  ticket collides forever.
- **Review a probe's body, not just its name.** Tester probe `P3o` in `foundry_arena/tp/bin/probes.py` wrote an empty
  file, because its placeholder was never replaced. So the PASS of that probe on the original proved nothing.
- **Prove the acceptance gate on the correct answers before freezing a trial:** run the reference fix through the
  whole real gate, and require PASS on every task. One gate failed 18 of 26 reference fixes after the freeze.
- **A trial run from a working tree cannot stay frozen.** Rules on commits do not stop a pull. Gate and judge
  subprocesses load whatever is on disk. Pin a read-only copy and hash it.
- **One model read is a noisy gate: roughly 1% FP and recall .85-.94 is what it delivers here.** A veto clause added
  against a dev false positive trades recall one for one: dev FP 0 and recall .93+, then the next blind unanimous read
  gave recall .85, 3 FP of 387. A reread with unchanged prompts moved one 15-row set from recall .93 to .87, and moved
  another set from 3 FP to 0. A zero-FP gate on hundreds of rows will not pass by prompt tuning. Give a model gate
  enough rows that one flipped row cannot cross the bar, or score several reads.
- **A texPath-like XML field can be an art contract that C# fills in** (`RM_PipePoles` `spanTexPath`
  `RimMandrake/FlowWorks/PipePole/{look}/PipeSpan`; GSS `AerialMaterials.PipeMats` does `Replace("{look}")` over
  `AerialStyles.Looks`). A lint that reads such a field as a literal path reports a permanent MISSING gap.
  `texture_gap_lint` judges each expansion, with values read from the C# source.
- **Fit and calibration targets must come from the same instrument and window as the comparison.** The
  rimflow_v3_sim backtest (since renamed `sim/process_sim.py`) missed for two reasons:
  - (1) Ticket counts are not a constant unit of work in v2. Over three consecutive weeks, helpers/close was 5.2, 3.3,
    1.5, and owner msgs->items was 4%/34%/62%. So ticket-count cells missed by ~3x, while work cells (helpers, ITE,
    vfail) passed.
  - (2) The targets came from a 7 d window ending 10-27T06:25Z. But `v3_vs_v2` measures the tag week to 10-26T14:00Z
    (file events 1545 vs 1281, close 806 vs 647). So the fit expected 17-20% more closes than its reference.
- **Completion measures go blind to the owner's strongest evidence unless they read it in its own shape.**
  `mod_completion.py` run 1 scored GimmeSomeSlack 29% working / 3% art, for four reasons:
  - (a) A whole-mod owner verdict ("all looks great! Verified.") names no def, so per-def matching credited nothing.
  - (b) GSS draws cords from C# texture literals, so 80 of 120 slots looked unused.
  - (c) Review-sheet picks live only in `*.decisions.json` sidecars, never in the protected set of the art ledger.
  - (d) Close-sha and title-mention attribution pulled in bridge-tool, Pyrelands and TESTENV_ harness items as GSS
    bugs.

  The fix: credit whole-mod owner walks to every name present at the walk sha. Read Source literals and
  human-timestamped sidecar slot rulings. Require that the close commit touches only the one mod, and that the title
  key is in the subject position. Exclude TESTENV_. GSS has only 6 explicit owner accepts; the rest is 'seen in a
  walk'.
- **Unread is not empty, and a stale report is not a fresh pass.** A reader that returns a count returns None when it
  could not read (check the exit code and output shape). The caller then prints UNMEASURED and fails. Before you
  compare tallies, check that the source exists: absent == absent printed 'same'. Before you run a subprocess, delete
  its output file: a crashed lint passed on yesterday's clean report. Seen: `sync_test_mods.remote_tally` ignored the
  exit code of ssh (ssh down tallied (0, 0)); `preflight_bridge` check `O14` (`effective_def_lint`). Also, a selftest
  outside `run_selftests` SEARCH_ROOTS never runs.
- **A donor's defName prefix is not its own:** `AB_` is Alpha Biomes AND live Alpha Memes (PreceptDef
  `AB_MiningYield_VeryHigh`). Also, Alpha Biomes declares abstract `Name="Plant_Bush"`, which shadows vanilla's def.
  To find the dead references of a retired donor, take an inventory of its defNames and filter it against a donor-off
  def dump (`retired_donor_refs.py`). Match its abstracts only as `ParentName`, never by prefix.
- **'Fix within 72h of a previous fix on the same file' saturates on hot files and measures nothing:** a
  daily-changing file scored 31 of 32 fixes, another 19 of 22. Use fix commits per commit, and hand-classify a sample.
  The fix-subject regex also over-counts: 6 of 25 sampled 'fix' commits were art picks, owner reverts or hardening.
- **A live row that asserts another mod's def FAILs when the suite's list does not load that mod.** The verdict reads
  as a mod defect, but it is a list fact (findings fold 2026-11-06..13):
  - CreatureBehaviors asked for `RSW_Ollopom` (SWBestiary's).
  - UtinniPatches asked for `RSW_Zersium`/`RSW_Phrik` (Armoury's).
  - Atlas asked for `RUT_Rites_ScrapShrine` (Rites').

  None of those mods is named in the About.xml of the asking mod. A row whose subject lives in another mod does one of
  two things: it loads that mod on its list, or it returns UNMEASURED when `get_defs` reports the subject `notFound`.
  Atlas's `_expect_lit` even detects "subject is not loaded" and still raises FAIL.
  `validation_core.missing_def_verdict(owner, own, active)` is the one rule. CreatureBehaviors's `RSW_Ollopom` row
  uses it; Atlas's `_expect_lit` does not yet.
- **`jawa/get_defs` flattens a list of objects to its class names** (`products` -> `['ThingDefCountClass']`,
  `statBases` -> `['StatModifier', ...]`). So a readback row that wants a count or stat value from such a list can
  never pass (Cuisine `recipes_readback` and `skewer_stats`, 2026-11-06 and 2026-11-12). Read list fields element by
  element (thingDef+count, stat+value). `skills/rimbridge/references/traps/pawns-factions.md` already says this for
  vehicle `components`.

## Doc rot and stale gates

- **A doc can describe defects that were fixed before the doc was written.** `liquids_framework_design.md`
  (2026-09-13) blocked all engine work on three flood defects. Those defects were fixed 2026-09-02 and closed at
  `747b0025`. An open item still told a seat (FOUNDRY, since retired) to re-fix them. Before you believe the "engine
  status" of any doc, check the code and the ledger. Also check whether an open item asks for work that is already
  done.
- 🔴 **A gate cited by NAME outlives the item it names — check the item's state.** `NAMING_SCHEME_EXECUTION_1` closed
  **2026-08-31** at `54a8e28d` on the owner's word. Yet 16 days later, ~20 live docs still said "do not rename ahead of
  it". For that reason FlowWorks (named by ruling 20) kept shipping as `fluidcanals` for those 16 days. FlowWorks is
  now `mandrake.rm.flowworks` (RE-VERIFIED 2026-09-19 against `About.xml` and the live Mods folder). Owner: *"That
  file may be VERY old… do not accept stale info."* Sweep: `STALE_RENAME_GATE_SWEEP_1`.
- 🔴 **memwatch's `oom_kill ... in rm-harness.slice` does not mean the slice ran out.** cgroup counters are
  hierarchical, and the scope of a short test is gone before the next sample. The kernel's `oom_memcg=` names the
  limit that fired. On 2026-11-03, all 19 kills were the planted `bomb.py` in `selftest_run_selftests.py`, which reads
  PASS. Read kills with `src/RimMandrake/Utils/oom_attribution.py`. Measured:
  `infrastructure/state/facts/oom_kills_2026-11-03.md`.
- **A frozen design sheet can hold an image that is false for the setting, not merely stale.** Example: a line that
  "its mother is the reason ships sink", in a world with no nautical ships. Check a metaphor against the WORLD, not
  just against other docs. A phrase can be consistent everywhere and still describe nothing that exists.
- **Trust a registry sheet's status only after resolving its defNames.** The mineral registry CSV listed three rows as
  BUILT whose defs were gone: two salts merged into `RM_RawSalt`, and fulgurite was excised. The CSV also listed
  `RUT_TibannaGas`, which never existed. A free-text `defs` column cannot be checked. The CSV now has a machine-read
  `bindings` column. `gen_mineral_registry.py` resolves that column against the def dump plus the repo XML.
- 🔴 **A sum of detached run tokens or dollars over runs that finished before the fix of 2026-11-19 counts resumed
  sessions more than once (RIMMANDRAKE_COUNT_RESUMED_RUN_TOKENS_ONCE_SESSION_TOTAL_LOGGED).** A run launched with
  `--resume` gets a result whose `modelUsage` and `total_cost_usd` are the whole claude session so far.
  `detached_helper.finish` recorded that session total as the run's `tokens` and `cost_usd`. The total went into the
  record, the Conductor log's `DETACHED RUN ENDED` line, and the maturation books and stage ceiling built on them.
  Measured 2026-11-19: 27 of 27 resumed runs since 2026-11-18 that follow an earlier run of their session recorded
  too much. On 2026-11-18 (PST), the overcount was 81,158,999 of 371,342,565 recorded weighted tokens
  (`design/experiments/2026-11-19-night-hypotheses/tools/check_resumed_run_tokens.py`, which prints the corrected
  sum). Records since then carry their own part, and `session`, `session_tokens`, `session_cost_usd`. Old records are
  not rewritten. The result's `usage` block is this process only (not cumulative), but it leaves out subagents.
- 🔴 **A coverage judge round re-asked between 2026-11-17 07:00 UTC and the fix of 2026-11-19 counts its first ask
  twice (RIMMANDRAKE_COUNT_JUDGE_AND_ART_REASK_TOKENS_ONCE)**. From the weighted_v2 change (`381db58f59`),
  `run_tokens` reads the result's `modelUsage`, which is the whole session. And `coverage_judge` added the figure of a
  `--resume` re-ask to the figure of the first ask (in the round `tokens` and in the concept's `review` charges).
  Graffiti `rm-coverage-judge-1794940039` recorded 566,882 = 2 x 270,651 + 25,580, from its transcript. Pyrelands has
  three such rounds. Earlier weighted_v1 rounds read `usage` and are right (Contagion's 1,119,788 is its session's v1
  total). `coverage_calibration` added the re-ask's `total_cost_usd` to the first ask's (2026-11-18 run: all five
  re-asked cases). Both now take `detached_helper.session_part`. `art_calibration` lists a re-ask's figure beside the
  first ask's in the same way. But no art calibration re-ask has ever run, so the trap is unproven there and not
  fixed.

## placeholder_lint texture tags
- **`placeholder_lint` is blind to some texture tags and masks.** Two blind spots:
  - `texpaths()` keeps only tags whose name contains 'texpath'. So it misses `texturePath` (terrain),
    `pollutedTexturePath` and `leaflessGraphicPath`. (`donor_retire_census` srctex saw 21 of 55 StandIn texts; use
    `donor_retire_census.py standin`, any tag.) The TEXTAGS of `regen_eligibility`/`bulk_accept_renders` lacked those
    tags too, so the gate refused those twins as 'renamed'.
  - Its MASK regex `m(_(south|east|north|west))?$` matches any stem that ends in lowercase m (AB_MangrovePalm). So the
    regex silently drops real pictures as masks. RimWorld masks are `<path>_m` and `<path>_<facing>m`
    (`donor_retire_census.MASK_STEM`).
