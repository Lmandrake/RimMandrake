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
