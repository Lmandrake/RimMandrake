# RimWorld 1.6 — Jawa scavenger clan on a desert world

**Read `infrastructure/agents/CHARTER.md`** — the whole process rulebook — and your
own window file: `infrastructure/agents/BENCH.md` (with the owner) or
`infrastructure/agents/FOUNDRY.md` (autonomous queue). Game cycle:
`infrastructure/GAME_STATE_WORKFLOW.md`. *(The four-seat POLICY.md system was
superseded 2026-08-27 — redesign #4, `Fable_Review/`.)*

**Models — owner, 2026-09-02: BENCH orchestrates on Opus, backgrounds DESIGN work
to a Fable subagent, and steps every other subagent down to the cheapest tier that
still has a catcher.** The ladder lives in `infrastructure/agents/Agent_Policy.md`
and nowhere else; never restate a model choice outside it.

## 🔴 There is no worldgen feature, in any version — owner, 2026-08-15

- **OUT, permanently:** any automated or programmatic worldgen; worldgen as a
  player-facing capability. ⛔ v2 is not a parking space for it — mark such work
  dead, never deferred.
- 🔑 **Players never generate anything. They receive a savegame holding the fixed
  world** — one hand-made world, frozen, shipped. A faction, ideoligion or setting
  absent when it freezes is absent from every player's game forever.
- ⛔ **Do not build anything that produces ALTERNATIVE planets** (owner, 2026-08-18).
  No seed sweeps, no variants, no knobs that could roll a second world. ✅ Author
  THE map, judged by realism first, iterated by LOOKING (`worldview.py`); target and
  references: `design/Jawa/worldbuilding/the_one_map.md`.

## 🔴 A BIOME WITH ZERO TILES IS NOT A DEFECT — owner, 2026-09-20, said repeatedly

> *"Correct we will repaint the whole world when all the biomes are in. **You don't need
> to keep rediscovering this.**"* · *"Don't worry about worldmap painting. Once we have
> all the biomes in mods we will do the painting once and for all."*

**The planet is painted ONCE, at the end, after every biome is its own mod.** Biome-to-tile
assignment is redone wholesale at that pass.

- ✅ **A BiomeDef of ours carrying 0 of 21,872 tiles is the EXPECTED mid-migration state.**
  It is not a finding, not a defect, and not a reason to do, defer or escalate anything.
- ⛔ **Never repoint owned content at a donor def to make it appear on today's map.** That
  is backwards and was nearly shipped twice.
- ⛔ **Do not cite a tile count as evidence that something is or is not built.** It answers
  a question nobody is asking until the painting pass.
- ✅ Do keep a paint list of owned BiomeDefs as biomes finish, so the repaint has a source
  of truth. Item: `BIOME_PAINT_ONCE_AT_THE_END_1`.

🔴 **This has now cost three reconciliation passes.** The Pyrelands was "discovered" to
have all its content on `RM_FE_Pyrelands` with 0 tiles on 2026-09-19 AND AGAIN on
2026-09-20, the second time producing a whole filed item
(`PYRELANDS_WRONG_BIOME_DEF_1`, closed) and a false report to the owner. **If you find
yourself about to report that one of our biomes is on zero tiles, you have rediscovered
this. Stop.**

### 🔴 And the instrument that keeps producing it: the tiles CSV is a RECORD, not the planet

`world/ASHKARR_WORLDMAP_tiles.csv` is **exported from the savegame**, last on 2026-09-12.
Its own freeze stamp (`ASHKARR_WORLDMAP_tiles.csv.frozen.json`, owner ruling 2026-09-07)
says it outright:

> *"It is a RECORD of the planet, not a rival to it. To change the world, change the
> WORLD and re-export — never edit this file and import it back."* … *"Any future
> live-vs-CSV validate must state which direction it is evidence for."*

⇒ **Reading that CSV tells you what the planet looked like on its export date, never what
it is now.** A live bridge edit after that date is invisible to it — which is exactly what
happened: a live read on 2026-09-19 recorded the Pyrelands on 222 tiles of
`RM_FE_Pyrelands`, while the CSV still showed 222 on the donor `ZBiome_Grasslands`. ⛔ Do
not resolve such a disagreement from the CSV, and ⛔ never call a CSV-derived tile count
MEASURED about the live world — the live system is the only instrument for "right now"
(`~/.claude/skills/measuring-large-artifacts`).

## Facts you cannot guess

### Engine and game facts

- **The game reads `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`,
  never this repo.** Writing a file is not deploying it.
- **A cold load is ~15 minutes on the full list; a quicktest map is ~90 s.** Never
  "restart and see". *(MEASURED 2026-09-07: launch 15:12 → `Bridge token:` 15:27 on
  **599** active mods. Supersedes the long-standing ~25 min figure. Caveat: that was
  the second launch of a session, so a first launch after a reboot may run slower.)*
- **`ModsConfig.xml` is the live mod list**, at
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`.
  Read it for the active count, never a number written in a doc.
- **Never guess a defName, field, or namespace.** RimSage (`mcp__rimsage__*`), the
  def, the About.xml, or `measure` — and 🔴 **a number about a large artifact comes
  from `measure`, never from a scan** (`grep`/`strings`/`wc` return plausible wrong
  counts; `.claude/hooks/block_blind_scan.py` refuses and names the instrument).
  `0` means measured zero; ignorance answers `UNMEASURED`. The skill lives at
  `~/.claude/skills/measuring-large-artifacts`.
- 🔴 **RimSage answers on the Windows Desktop ONLY — on the Mac laptop it has never
  connected** (MEASURED 2026-09-16: five timed-out session logs 2026-09-02→09-16,
  `mcp.rimsage.com` TCP-dead while general egress is fine, no `mcp__rimsage__*` tool in
  the toolset at all, no cached decompiled tree). So on the laptop an **engine-internals
  question is UNMEASURABLE** — say so rather than reasoning from a doc, and never brief a
  subagent to "use RimSage" there: it costs a whole run to rediscover. Still fine offline
  on either machine: the def dump (`measure`, `refresh.py`) for DEFS, and reading our own
  source. ⚠️ **Several docs assert engine facts that trace to an earlier agent's prose,
  not a decompiler** — `About.xml`'s "vanilla ignition already works on any flammable
  terrain", and `Flood.noPossibleCell` being private with no accessor. Do not launder
  those into measurements.
- ✅ **CANON research DOES work from the Mac, and directly.** Wookieepedia's
  `action=parse&page=<X>&format=json&prop=wikitext` API answers unauthenticated over plain
  `curl` with **no size cap** (MEASURED 2026-09-23: 13 dianoga pages pulled clean). ⇒ Prefer it
  over Fetcher, which **silently TRUNCATES AT 50,000 chars** and has eaten a species' whole
  Biology section. Resolve titles with `action=query&list=search&srsearch=<name>` — a guessed
  exact page title returns MISSING for real subjects constantly, which is not evidence a subject
  is non-canon. ⚠️ `timeout` does not exist on macOS and its failure **resets the shell's cwd**;
  use `curl --max-time`.

### Instruments that return a confident wrong number

- 🔴 **`northstar.parse()` returns a DICT.** `getattr(w, "must_show")` yields `None` → `len()` 0,
  so all four VALIDATED walks read as "0 bars" — an alarming wrong number that looks like a
  catastrophic finding. Use `w["must_show"]`. 🔑 A count that is conveniently *or* alarmingly
  round is a query bug until proven otherwise, and the alarming direction is the one you will
  believe without checking.
- 🔴 **`ls <dir> | wc -l` answers 0 for a directory that does not exist**, so a "queue is empty" claim can be
  a wrong-path claim wearing a number. The artpipe queue is `infrastructure/artpipe/pending/` — it held
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
- ⚠️ **A bare unprefixed defName in a design roster is the CONVENTION, not a defect.** MEASURED
  2026-09-23: **144** such rows across **18 of 29** rosters, 94 creatures — and the live biome XML
  does the same deliberately (`RUT_FeverWood.xml`: `<Urusai MayRequire="mlie.starwarsanimalcollection">`),
  because that IS the donor's defName. Our `RSW_Urusai` is a separate **absorbed port**
  (`MLIE_FAUNA_ABSORPTION_1` Wave C). ⇒ A homeless-creature census must match **both** spellings
  or it reads a cast creature as homeless — but ⛔ **never file the bare name as a naming
  defect**: one such note was filed and had to be retracted the same week. The real gap is that
  **98 live rows across 11 biome files still name the donor for 73 creatures we already ported**,
  so the campaign still hard-depends on that mod and 73 ported creatures spawn nowhere
  (`MLIE_ABSORPTION_BIOME_WIRING_1`).
- 🔴 **Never scan `ModsConfig.xml`.** `grep -c '<li>'` returns **48** where the real active count
  is **631** — it counts lines containing the tag, and that file puts many elements on one line.
  Parse it (`ET.parse(p).find("activeMods")`). Snapshots are in
  `infrastructure/state/modlists/`; the live file is a Windows path **unreachable from the Mac**,
  so a laptop claim about the LIVE list is UNMEASURABLE and must say so (2026-09-17).
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
- ⚠️ **`ls` on `design/RimStarWars/canon_references/` is not a canon test.** It holds 137 entries
  **by design**, so absence proves nothing — `Mynock`, `Worrt`, `Gelagrub`, `Urusai`,
  `LongtailGorg`, `Woolamander` and `Gornt` are canon Star Wars creatures with no entry. Routing a
  canon-vs-ours decision off that directory listing would have rewritten canon text for all seven.
- **A number you brief a subagent with will come back to you.** A census reported "2 of
  137 canon entries ruled"; the real figure is **25**. Two later agents measured 25 and
  both explicitly refused to adjust to the briefed figure — the correct behaviour. When
  two subagents disagree on a number, measure it yourself before it becomes a fact.

### Tools with surprising side effects
- 🔴 **A `PreToolUse` hook added to `.claude/settings.json` mid-session does not fire** — not for this window's Bash calls and not for its subagents' — until a new session starts; a hook already present at session start does fire for subagents. Test a new hook in a fresh window, never by exercising it in the one that added it.

- 🔴 **A backgrounded `Agent` dies at 600 s of silence and leaves NOTHING on disk.** Three died
  that way 2026-09-17, all mid-read before their first write, all leaving a clean tree — so each
  cost a whole run rather than being truncated; the two that survived streamed output at 385 s
  and 575 s. **Brief every writing subagent to create its output file as a skeleton FIRST and
  fill it section by section** — a file write emits progress and persists partial work. A long
  read-then-write brief is the shape that trips it.
  🔴 **It happened AGAIN 2026-09-23** on a mechanical creature census, and the cheaper lesson is:
  for a **mechanical** census (glob, parse, count, tabulate), writing the script inline costs less
  than briefing an agent to survive the watchdog. Reserve subagents for work that needs judgement.
- ⚠️ **Two `PreToolUse` gates refuse tool calls outright and are easy to trip:**
  the `Agent` tool **refuses without an explicit `model`** (omitting it silently inherits this
  seat's tier, which is how past censuses ran on Opus; named agent types and `fork` are exempt) —
  ladder in `infrastructure/agents/Agent_Policy.md`. And `AskUserQuestion` is validated by
  `validate-question-card.py`: a `header` longer than **12 characters**, or a question not ending
  in `?`, refuses the **whole card**. Count the header before calling.
- 🔴 **A question-card option LABEL the owner clicks is OUR sentence, not his.** `block_forged_owner_said.py`
  refuses it and is right to: only text he **types** (a notes box, a free-text Other) is his. Record a click
  as **"decision taken by question card"** with no quote flag. ⚠️ The guard also reads **commit message
  bodies**, and being `PreToolUse` it refuses the **whole compound command** — so a chained write-then-commit
  loses the write too.
- ⚠️ **`RM_CreatureBehaviors.csproj` sets `EnableDefaultCompileItems false` and lists every file.** A new
  `.cs` in `Source/` without a `<Compile Include>` line **compiles into nothing, with no error**. Adding a
  file to that assembly is always a two-file change.
- 🔴 **`handoff.py` cannot tell two BENCH windows apart.** It REFUSES on "BRIDGE still held by
  BENCH" even when the hold belongs to the *other* window's live session, because both sign as
  `BENCH`. ⛔ Do not release it to satisfy the gate — that breaks a live game. `--force` records
  it as open, which is the correct exit, and the handoff must name whose hold it was.
- 🔴 **`modcheck run <Mod>` REWRITES the live `ModsConfig.xml`** — it calls `modlist_swap` and
  swaps to MINIMAL. It reads like a query verb and is a Charter expensive-list action. On the
  Mac it dies on the Windows path; on the Desktop it swaps his list unasked (2026-09-17).

### Design process and biome/roster rulings

- 🔑 **Before designing anything, read the source and the roster — this project keeps having already built
  it.** MEASURED 2026-09-23 in one session: the owner proposed a "special oil to seal part of the greatbole
  so it cannot regrow" and it ships as `RM_ToxinSealant` (item + terrain) with
  `RM_MapComponent_LivingRegrowth` **already gating regrowth on that terrain**; the grubs' two behaviours are
  `RM_EatCleanableExtension` and `RM_ParentalEnrageExtension` with one axis widened each; their breeding is
  `RM_CompVerminBreeder` + `RM_MapComponent_VerminPopulation` + its alert; and the mining thresholds need no
  new tracking because `BoleRecord.footprint`/`timers` are already Scribed. **Four of six mechanisms already
  built.** Again 2026-09-25: `SEA_SHORE_TILE_MUTATOR_1` was filed and sent to design while
  `mandrake.rm.seashores` — the exact mutator — had shipped two days earlier. ⇒ Search `src/` before FILING, not only before building. ⇒ Same for CONTENT: the flora roster had already named the wasps' hosts, the ant hive's farmed
  species and the sealant's toxic plant. ⛔ A design pass that invents before it reads will re-invent.
- 🔴 **Say which greatbole you mean, every time — the species is THREE defs.** `RM_Greatbole` is the mature
  fellable giant (roster row 22); `RUT_GreatboleHeartwood` is the mineable `RockBase` blob a player actually
  sees and digs, carrying its own flat-colour placeholder; `RUT_GreatboleCore` is a **1×1 bookkeeping
  marker** whose `drawSize (7,7)` renders a retinted vanilla `DeepDrillPowered` across the middle of the
  wood — a real visible defect in shipped content (`GREATBOLE_BARK_EDGE_ART_1`). Confusing them produced two
  false statements to the owner in one session, in opposite directions.
- 🔑 **An animal belongs to ONE biome unless there is an IN-GAME reason** — owner ruling
  2026-09-21, verbatim: *"Animals sound be biome-specific unless there is an in-game reason
  (e.g. flyers that migrate, young versions that grow in the miasma then migrigate to the sea
  later, etc.) So stonebacks hould have one home. We have plenty of creatures left to fill
  rosters if there are holes."* ⇒ 🔑 **A hole in a roster is filled with a NEW creature, never
  by re-using a neighbour's** — we have surplus cast. MEASURED 2026-09-22: **55** species are
  wired into more than one of our biomes. (⛔ Not 52 — that figure was published twice, on two
  different membership sets, by an instrument that cannot read a patched-in roster. See the twin
  trap two bullets down.)
  🔴 **The carve-out is NARROW, and habitat is not part of it** — owner, 2026-09-22: *"you are not
  understanding. I meant pick one arid home."* ⇒ **when he names several biomes for a creature,
  that is the CANDIDATE set, not an assignment**, and "they're both arid / both nightside / both
  sea" is **not** an in-game reason. Only his two mechanism cases are: a flier that migrates (he
  widened it: *from a wetter region into a hot one to lay eggs*), or a life stage that moves.
  🔴🔴 **EVICTIONS ARE STOPPED, AND THIS IS NOT A RULE SYSTEM** — owner, 2026-09-22: *"Let's stop
  evictions right now, because I think it's much better to carefully handle biome by biome rather
  than sweeping changes between unfinished biomes and nearly finished biomes."* ⇒ **No pass edits a
  roster to enforce this law.** A biome's multi-homed species become rows on **that biome's own
  review sheet** when it comes up for its sitting, judged at that biome's stage of completion.
  Deliberate multi-homing is **annotated in place, never cut** (worked precedent: the screecher,
  `29ccede91` — both rosters keep it, both say why, both say do not "fix" it).
  🔴 **The failure this ruling ends, because it cost a whole session:** "which biome does this
  creature live in" was escalated into a tie-break algorithm, and three owner cards each *added a
  clause* to it (a canon fork, a provenance override, a scope exception) until it deleted a species
  out of the Greentide roster that had been frozen and cast **the same day**. His diagnosis: *"I
  don't think we should be having rules here. This is a human review process issue."* and *"Just
  don't apply these broad sweeping rules to overturn human requests."* ⇒ 🔑 **If consecutive
  questions to him each add a clause to a procedure rather than resolving a concrete case, STOP** —
  it is review work, and review sheets are the existing machinery. ⛔ **Do not re-derive the
  algorithm from the rulings recorded in `BIOME_SPECIFIC_FAUNA_LAW_1`**; that item is now input to
  per-biome sittings, not a work queue. ⛔ And a rule derived in-session never overturns a placement
  a human already approved.
- 🔑 **A sea biome describes BOTH its floor and its catch** — owner ruling 2026-09-21:
  *"The biomes should be describing the sea floors (what you encounter as an animal there) as
  well as what you can FISH out of the oceans on the shore. There should be defs made for each
  fish as something swimming around the floor area as well as something you can pull out as a
  fish."* ⇒ each sea species owes **two** defs: a floor resident in `<wildAnimals>` and a
  catchable entry in `<fishTypes>`. The floor is reachable via the generic `RM_DiveEligible`
  terrain mechanism in `mandrake.rm.divinginteraction`.
  ✅ **RE-MEASURED 2026-09-26 on the RM tier, which is what ships: all four seas now carry
  `fishTypes` AND a real floor roster** — Scald 3 inline + 3 canon patch-added, Grey Sea 6,
  Twilight Sea 6, Propane Lake 6. The old "no `fishTypes` at all and 2 animals each" line
  described the `RUT_` twins and was already stale; the split did that work.
  🔴 **Parse `<wildAnimals>` as an XML ELEMENT, never by counting `<li>`.** `BiomeAnimalRecord`
  has a custom loader reading the node NAME as the animal and the node TEXT as the commonality
  — `<RSW_Faa>0.5</RSW_Faa>`, no `<li>`. A `<li>` count returns **0 for a populated roster**,
  which is how one pass in this very session first read all four seas as empty.
  ✅ **The "do wildAnimals spawn on an impassable biome" question is ANSWERED — MEASURED from
  the decompiled engine 2026-09-26, and `impassable` is a red herring.** Nothing in
  `GenStep_Animals` or `WildAnimalSpawner` reads it. The real gates are **`animalDensity > 0`**
  (`DesiredAnimalDensity` multiplies `map.TileInfo.AnimalDensity`, so 0 makes
  `DesiredTotalAnimalWeight` 0 and `AnimalEcosystemFull` instantly true) and, for ongoing
  spawns only, a walkable cell that `CanReachMapEdge`.
  🔴 **So `RM_PropaneLake` and `RUT_PropaneLake` leave `animalDensity` UNSET — it defaults to
  `0f` and their 6-animal roster is dead content that can never spawn.** Item:
  `PROPANELAKE_ANIMALDENSITY_ZERO_1`.
- 🔑 **A review sheet's `cut` is scoped to THAT SHEET'S BIOME, never the planet** — owner
  ruling 2026-09-21. The Lantern Deeps sheet cut `RSW_AaroxisDendoria`, `RSW_PodWorm` and
  `RSW_MossBeetle`; all three legitimately remain admitted elsewhere (the first two in the
  Miasma, the third in the Arid Shrubland at 0.3). ⛔ So a species cut in one sheet and
  alive in another biome is **correct, not a leak** — do not "fix" it, and do not read one
  sheet's verdict as a planet-wide sweep. A cut with an empty note says nothing about
  anywhere else.

### Doc rot and stale gates

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

### North-star validation state

- 🔴 **The north-star system cannot GREEN anything: `shows=` appears in 0 of 54 mod
  `validation.py` files** (RE-MEASURED 2026-09-17), so every VALIDATED mod's must-show bars are
  bound-and-uncovered and a `modcheck run` against one returns REFUSED before the game is
  consulted. Authoring more bars adds refusals, not coverage; `NORTH_STAR_PIT_PILOT_1` is the
  falsification test and has never run. 🔴 **And the 81 walk findings are NOT rot:**
  `doctor` derives a walk's mod from the walk's BASENAME, never from its `subject:` line, so its
  24 ORPHAN_WALKs and 10 SUBJECT_COLLISIONs are ONE phenomenon — **34 of 78 walks are deliberate
  per-feature walks sharing a live mod's subject** (MEASURED 2026-09-18). Of the 33 failing
  walks, 25 have a fully live subject and the defect is a stale id inside a STEP, and **0 are
  genuinely orphaned**. ⛔ Never "fix" a walk on an ORPHAN_WALK finding alone, and ⛔ do not
  rebuild the 43-row decision sheet: the owner ruled it was never his to adjudicate
  (*"this doesnt feel like a sheet I should be asked"*) and its data was wrong besides — a walk's
  subject packageId is backticked in 28 walks, BARE in 34 and absent in 16, so a backtick-only
  regex reads None for 50 of 78. `DETERMINISM_ASSESSMENT.md` §11a is the account; the walk-model
  ruling landed 2026-09-18 (owner card): **per-feature walks are first-class via a `feature:`
  key** — implementation is `WALK_FEATURE_KEY_1`. ✅ **The "modcheck status reads a stored field" bug is
  FIXED** (`fa27e1cab`, `status.check_or_orphaned` + `doctor.py`, same day as the claim above was
  first written) — live-checked 2026-09-17: `modcheck status` now correctly prints `FlowWorks
  STALE   [stored: GREEN]` and `Pits ORPHANED (no such mod folder)   [stored: GREEN]`, re-deriving
  every row rather than trusting the stored field. The dead `FluidCanals` key is gone too
  (`b110a7a2d`, `rename-key`/`forget-key`). Don't re-open this as a live defect without
  re-measuring; the stored field only ever appears now as a `[stored: ...]` drift annotation.
- **North stars: `FlowWorks`, `Graffiti` and `Pits` are VALIDATED; `WreckedMachines`
  REVERTED TO DRAFT** — RE-MEASURED 2026-09-20 (`modcheck floor --all`, new this session):
  `WreckedMachines.md`'s `### cannot show` prose was corrected at `6cdf52b39` (2026-09-17,
  same day as the MEASURED line below) without a same-sitting re-validation, so its hash
  no longer matches and it is exactly the failure mode two sentences below warns against —
  it needs `modcheck/cli.py validate WreckedMachines --owner-said "..."` before it binds
  again. The original MEASURED-2026-09-17 line (13+3 / 8+2 / 11+1 / 12+2 = 44 bars, every
  hash MATCHing) was true when written and is not true now. ⛔ Do not casually edit their
  `## north star` sections: the hash
  covers the **whole section including explanatory prose**, so correcting a stale caveat
  reverts the checklist to DRAFT and the mod quietly stops being refused (hit live
  2026-09-16). 🔴 **Owner ruled 2026-09-17 that this stays as it is** — verbatim: *"Change
  no code — you just re-validate when prose is corrected."* Bar-scoped hashing is
  **declined, not deferred** (`NORTHSTAR_HASH_SCOPE_1` dropped), so the remedy for false
  text in a hashed section is: correct it, then re-validate on his word, same sitting.
  ⛔ Never leave false text standing to protect a hash — that trade is now ruled against.
  🔑 Therefore **write only state-independent prose inside that section** — never "binds
  nothing until validated", which is false the moment it is. And `modcheck/cli.py
  validate <Mod>` refuses unless BOTH `state:` and `validated-hash:` header lines exist
  (blank is fine), and since 2026-09-17 refuses a section parsing to **zero bars** — a
  misformatted section used to record VALIDATED against an empty checklist, binding
  nothing; omit `--owner-said` for a dry run that writes nothing.

### Patch and def behaviour

- **A patch that matches nothing logs nothing.** `PatchOperationConditional` and
  `PatchOperationFindMod` both return true on no match.
- **Dumps and harvests decay** (owner, 2026-08-27): trust one only after its
  fingerprint matches the live mod set; the frozen `official` dump is the sole
  design target (`GAME_STATE_WORKFLOW.md`).
## In-game LLM access is the Claude Code CLI, never a hosted API key — owner, 2026-09-05

Every mod that calls out to an LLM (the Oracle, the raid-redesigner, any future
consumer) does it by shelling out to **`claude -p "<prompt>"`** (Claude Code in
non-interactive mode) as a subprocess, not by making an HTTP call to an
OpenAI-compatible endpoint. Owner, verbatim: *"Claude Code in non-interactive
mode (`claude -p "..."`) authenticates via your claude.ai login and can be
called from a shell script without any API key."*

- ⛔ **Supersedes `OracleClient`'s original HTTP/OpenAI-compatible design**
  (`design/RimMandrake/llm_ingame_wiring_spec.md` §1, `src/RimMandrake/Oracle`'s
  `OracleHttpClient`) — no base URL, no model string, no API key field, no local
  Ollama fallback. The two laws in that spec (text/menu authority only; the
  game is whole with the LLM absent) and the async/timeout/kill-switch
  threading shape are UNCHANGED — only the transport (HTTP → subprocess) moves.
- The game process (Mono/Unity on the owner's Windows machine) launches `claude
  -p` via `System.Diagnostics.Process`, same off-tick `Task`-based async
  pattern already built, reading stdout instead of an HTTP response body.
  Whoever rebuilds `OracleHttpClient` against this: verify the exact
  invocation and output shape against a real local `claude -p` call before
  wiring it — do not assume flags or JSON structure from this note.
- **New environment dependency this creates**: the owner's machine must have
  Claude Code installed and logged in for any consumer to work at all — this
  is now a fact about his machine, not a config value in Mod Settings.
- Affects `ORACLE_EXPERIMENT_SPIKE_1` (client rewrite owed) and
  `PLOT_MECHANISM_MODS_WAVE_1` Part 1 (the raid-redesigner's Oracle calls ride
  whatever `OracleClient` becomes).

## A pit is a SUPERDEEP cell, not a building — owner, 2026-09-17

*"I'm not really sure a pit is any different than a deep canal."* Ruled and fully
specified, **nothing built**: `infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md`.
A pit is depth 4 on the D/F primitive rulings 18/19 already established, so the
fitting concept collapses to **spikes alone** (oil and poison are FluidDefs; the
oubliette is CUT), an enclosed superdeep area is a room that becomes a prison room
once a bed is in it, `capture down`/`convert down` happen from the lip because
nobody who enters can leave, and TEMPERATURE is the softening mechanism.

🔴 **The ITEM is the authority, not the spec.**
`design/RimMandrake/pit_superdeep_collapse_spec.md` (1127 lines) was written BEFORE
three rounds of rulings that changed ten of its answers; the item lists the revisions
it is owed. ⛔ Do not read the spec and act on it without reading the item first —
you would build the version he rejected. Door family is its own item,
`FLOWWORKS_DOOR_FAMILY_1`: **two** stuffable defs, never the three he described and
then talked himself out of.

## 🔑 "Star Wars style" naming is NOT Star Wars IP — owner, 2026-09-22 (Q11a)

*"The fact that we will use "star wars style" naming doesn't mean they have to live in the star
wars layer. The top mod without star wars will look precisely the same as the star wars enhanced
one save for any star wars beasts we populate it with."*

**The tier line is IP, not flavour.** An **invented** exotic name is free to live in the
franchise-free `RM_` tier and be cast inline; only a **genuine canon** name (hydenock, jogan, muja,
chak-root, tooke-trap …) is IP and must route through the Utinni patch layer as Q11 requires.
Authority: `design/RimMandrake/biome_mod_architecture.md` §7 **Q11a**, beside Q11.

- ⇒ 🔴 **A `RM_` biome does NOT get a thin dependency-free "fallback" roster.** The free mod must look
  *the same* as the campaign one, with canon content added on top — never substituting for an
  impoverished base. "Rich enough to stand alone" is a requirement on every `RM_` roster.
- 🔴 **BENCH got this exactly backwards for an hour of his session**: read *"bizarre Starwars names"*
  as canon IP and routed a whole **invented** tree roster into the Star Wars layer. ⛔ Don't repeat it.
- 🔑 **The bigger lesson, and it recurred within 24 hours of the same failure in another domain:** he
  then removed canon from the roster altogether (*"we're making our own"*), which made **four** queued
  questions **moot rather than deferred**. ⇒ **When a tier or provenance question starts generating
  sub-questions, ask whether the CATEGORY is needed at all before adjudicating inside it.**
  Adjudicating first and having the category deleted is the same shape as the multi-homing tie-break
  algorithm he stopped (`BIOME_SPECIFIC_FAUNA_LAW_1`).
- ⚠️ **A canon claim whose evidence is a donor mod's defName is not sourced at all.** A roster row read
  *"Canon. Felucian glowspore is canon Felucia flora; the donor row `Plant_FelucianGlowspore_Wild` is
  the wild form"* — circular, and false: `glowspore` returns **zero** Wookieepedia hits. Verify via the
  search API (`action=query&list=search&srsearch=`), never a guessed exact title — a title miss returns
  `MISSING` and proves nothing. Absence from `canon_references/` proves nothing either (137 entries by
  design), which is exactly why the donor def is often the only evidence available and must still not
  count.
- ⚠️ **`<wildPlants>` uses the shorthand `<DefName>commonality</DefName>` form**, not `<li><plant>`
  children — a parser written for the `<li>` form reads every row as empty and reports a roster of
  `None`. It produced two flatly contradictory measurements of one file in a single session.

## Shipping names are three-tier — owner, 2026-08-30

Every NEW packageId, defName, C# namespace and mod folder uses the tier
grammar in `design/NAMING_SCHEME_PLAN.md`: **RimMandrake** (any RimWorld game) /
**RimStarWars** (any Star Wars scenario) / **RimUtinni** (this campaign) —
packageId `mandrake.<tier>.<modname>`, prefixes `RM_`/`RSW_`/`RUT_`,
C# namespaces nested `RimMandrake[.StarWars|.Utinni].<Mod>` (never bare
`RimStarWars`/`RimUtinni`). "Jawa" is lore text only. Dev tooling is exempt.

🔴 **The migration is DONE — there is no rename gate any more.**
`NAMING_SCHEME_EXECUTION_1` closed **2026-08-31** at `54a8e28d` on the owner's
own word (*"Deploy the full rename."*), which is why the mod set already carries
`mandrake.rm.*` / `mandrake.rsw.*`. So when a mod is RENAMED after that date, the
rename is simply owed work — execute it, do not defer it to a closed item. Three
live docs were still citing that item as a reason to wait 16 days after it
closed, which is how `FlowWorks` (named by ruling 20, 2026-09-16) kept shipping
as `fluidcanals`. If you find another such citation, delete it.

## Every mod ships superb Mod Settings — owner, 2026-09-12

Every mod we ship carries a real settings screen: on/off per major
feature/mechanic, tuning where a number is the experience, defaults = shipped
behavior, all-off degrades gracefully, and worldgen-affecting toggles labeled
as such. Biome-kit mechanics are feature-gated so they can be enabled in other
biomes without the biome. Spec + retrofit of existing mods:
`MOD_OPTIONS_RETROFIT_1`. Applies to every future mod, no exceptions.

## If it flies in the fiction, it flies in the game — owner, 2026-09-19

*"if we're going to wait for it as though it's not available, we might as well make
it a Flyer while we're here. Standing rule: we make flyers flyers when we can, ok?"*

Any creature whose description, canon entry or art shows it airborne gets real
flight, not a walking animal with wings drawn on. Applies to new defs and to any
def already open for another reason — the rule is "when we can", so the trigger is
touching it, not a sweep.

### 🔴🔴 NEVER live-test a flyer's flight without the owner present — said THREE times, 2026-09-25

Verbatim, third repetition, same day: *"For the third time, do not do live testing
of flyers without a human present. It doesn't work."* Also said the same day: *"Don't
try to capture images of flight. It doesn't work."* **You don't need to keep
rediscovering this — stop reaching for a live-bridge flight test at all.**

- ⛔ **No unattended bridge session — of any length, any sampling strategy — spent
  hunting a live mid-air frame or takeoff.** This includes screenshot hunts
  (`take_screenshot`/`screenshot_cell_rect` timed against `step_game_ticks`) AND any
  other unattended live-drive attempt at proving flight in the moment. One such pass
  ran ~35 minutes, ~25 screenshots, dozens of movement-segment checks, and caught
  nothing — inconclusive, not proof either way, and not a productive use of bridge
  time regardless of sampling density (worked example, now superseded:
  `FIREHAWK_FLIGHT_BEHAVIOR_1`).
- ✅ **Verify flight via a deterministic STATE read instead**, never a screenshot/visual
  hunt: a debug `[Tool]` (see `rimbridge-companion` skill) that reads
  `Pawn_FlightTracker`'s current state on a pawn directly. That is buildable and
  provable offline/asynchronously; a live *visual* sighting of the animation is the
  one thing that needs the owner actually watching.
- **How to apply:** if a flyer's live behavior needs eyes on it, that is a
  `rimworld-live-review`-style session done WITH the owner present, or it waits —
  it is never a FOUNDRY solo bridge pass. Don't file a "live verify" bar on a flyer
  item that can only be closed by an unattended screenshot/observation hunt; close it
  via the state-read instead, or leave the visual bar for a joint session.

🔑 **1.6 flight is CORE, not a donor framework and not Odyssey.** The stat
`MaxFlightTime` is declared in `Defs/Core/Stats/Stats_Pawns_General.xml` and Core's
own chicken uses it. MEASURED from the decompiled engine 2026-09-19.

⛔ **The switch is a STAT, not a bool.** `Pawn_FlightTracker.CanEverFly` returns
`GetStatValue(StatDefOf.MaxFlightTime) > 0f` — there is no `canFly` field, and
setting `race` flags alone gives you a grounded animal that reads as configured.

The vanilla shape, copied from `Locust` (`Races_Animal_Insect.xml`):

```xml
<statBases>  <MaxFlightTime>10</MaxFlightTime>  <FlightCooldown>5</FlightCooldown>  </statBases>
<race>
  <flightStartChanceOnJobStart>0.1</flightStartChanceOnJobStart>
  <flightSpeedFactor>2.5</flightSpeedFactor>
  <canFlyIntoMap>true</canFlyIntoMap>
  <canLeaveMapFlying>true</canLeaveMapFlying>   <!-- birds; omit for something that lairs -->
</race>
```

⚠️ **The flight ANIMATION is separate from the flight STAT, and it is its OWN
whole-body multi-frame system — not a wing render-tree.** `PawnKindDef`'s
`flyingAnimationFramePathPrefix` + `flyingAnimationFrameCount` need a real frame
sequence (Locust ships 5, Chicken/Duck/Goose/Sparrow ship 8). With none,
`GetBestFlyAnimation` returns null and the creature flies with no wing-beat —
correct behaviour, plainer look. Never block flight waiting on frames.

🔴 **REVERSED 2026-09-19 — do not build a `PawnRenderNodeProperties_Spastic`
wing-layer render tree for this.** `FIREHAWK_FLIGHT_BEHAVIOR_1` did exactly
that (a custom `BodyDef` wing part + a Spastic node jiggling one wing texture)
and the owner's own live test found it broken: standing still sideways with no
visible flap, and north missing one wing entirely with the other misaligned.
Root cause is architectural, not a bug to patch — Spastic drives a small idle
wiggle on ONE static texture per node; it was never a per-facing, per-frame
flying animation, so it cannot express "wings up" vs "wings down" the way the
directional flip-book below does, and nothing keeps a single wing texture
aligned across four facings.

**The correct mechanism, MEASURED against the installed game** (Core's own
Chicken/Duck/Goose retrofits, `Data/Core/Defs/ThingDefs_Races/
Races_Animal_ChickenGroup.xml`, and their textures pulled live from
`resources.assets` via UnityPy):

```xml
<PawnKindDef>
  <flyingAnimationFramePathPrefix>Things/Pawn/Animal/Chicken/Chicken_Flying_</flyingAnimationFramePathPrefix>
  <flyingAnimationFrameCount>8</flyingAnimationFrameCount>
  <flyingAnimationTicksPerFrame>2</flyingAnimationTicksPerFrame>
  <flyingAnimationDrawSize>2.4</flyingAnimationDrawSize>
  <flyingAnimationDrawSizeIsMultiplier>true</flyingAnimationDrawSizeIsMultiplier>
  <flyingAnimationInheritColors>true</flyingAnimationInheritColors>
</PawnKindDef>
```

The texture set is a **whole-animal directional flip-book**, one full-body pose
per frame, NOT a separate wing layer: `<prefix><N>_<direction>` for N = 1..
frameCount, directions `north`/`east`/`south` only (west mirrors east, same as
every other RimWorld facing set) — confirmed by extracting all 24
`Chicken_Flying_*` textures and diffing frame 1 (wings tucked) against frame 5
(wings spread) at `_east`: genuinely different poses, not a static image
jiggled. `flyingAnimationDrawSizeIsMultiplier` scales the whole flying sprite
relative to the grounded one (birds read bigger mid-flight); gendered species
(Quail, Peafowl) add `flyingAnimationFramePathPrefixFemale` alongside the
default (male) prefix. Reference doc:
`~/Desktop/RIMWORLD_1_6_NATIVE_ANIMAL_FLIGHT_IMPLEMENTATION.md` (owner,
2026-09-19) — read it before touching any flyer again; it names Sparrow as the
cleanest from-scratch template and Chicken/Duck/Goose as the retrofit
references, and gives the full verification checklist (loop correctness,
all-facing correctness, landing restores the grounded graphic, save/load
safety).

⛔ **`FIREHAWK_FLIGHT_BEHAVIOR_1`'s BodyDef/PawnRenderTreeDef/Spastic wiring
needs replacing with this**, not extending — the wing-split art
(`FireHawk_Wing_*`) and the custom body part it hangs off are the wrong shape
for the problem and should come back out once the real flip-book frames exist.
The `MaxFlightTime`/`FlightCooldown`/race-flag half of that work (and of the
2026-09-19 fire wasp/fire hawk flight pass) is unaffected — those fields are
correct and unrelated to the animation defect.

🔑 **Design assumes every DLC is present** — owner, 2026-09-25, verbatim: *"Always assume all
the dlcs."* No standalone-without-expansion fallback tier is owed (asked about the free mods'
deluxe gear without Odyssey). `MayRequire` guards stay for load safety, not as a design axis.

🔴 **And that assumption covers the PLAYER, not just us** — owner, 2026-09-26: *"it is assumed
that future players will have all the Rimworld DLC's currently installed."* ⇒ **Every DLC is a
hard prerequisite of shipping, exactly like the base game.** Royalty, Ideology, Biotech, Anomaly
and Odyssey content may be depended on outright in anything we ship — a mechanic, a def, a
biome roster, a quest, a scenario.
- ⛔ **Do not design, build or file a DLC-less degradation path**, and do not raise "what if the
  player lacks X" as a defect, a risk or an open question. It is answered: they have it.
- ⛔ **Do not spend a review, a test tier or a load round on proving a DLC-absent configuration.**
  There is no such supported configuration.
- ✅ `MayRequire` still goes on **mod** guards for load safety. On a DLC it is harmless but
  decides nothing, so never read one as evidence that a DLC-absent case is supported.

🔑 **ALL TEST MOD LISTS include ALL FIVE EXPANSIONS — no exceptions right
now.** Owner ruling, 2026-09-19, verbatim: *"Was Odyssey even loaded for this
test? ALL TEST MOD LISTS should include ALL THE EXPANSIONS; we're not trying
to ablate expansions out of our list at this time."* `modset_builder.py`'s
`bridge`/`pits`/`graffiti`/`oracle` tiers built Core-only before this ruling;
all tiers now set `dlc: True`. A tier's `want` list may still narrow which
*mods* load for isolation — it may no longer narrow which *DLC* loads.

## Queue items are NAMED, not numbered — owner, 2026-08-20

`THREE_UPPER_SNAKE_WORDS_#`, guessable cold: `SANDSTORM_WEATHER_TUNING_1`. No new
`B*`/`C*`/`D*`/`W*` IDs; legacy IDs are never renamed and are always cited with
their title attached — `B58 (the dead Jawa pawnkind)`, never bare.

## Correctness outranks seat ownership — owner, 2026-09-19

*"It is WORSE to leave incorrect information that belongs to another seat than it is
to violate seats... ok? I keep saying this. MAKE IT SO EVERYWHERE."*

🔴 **A false statement in another seat's file is yours to fix, on sight.** Item prose,
spec, design doc — no correction ticket, no note, no waiting. A wrong sentence left
standing is believed by everyone who reads it next; the seat boundary was never
supposed to protect one.

- **Commit it at once, explicit paths.** The danger was always the UNCOMMITTED fix in
  a tree four threads share — erased by the next checkout, nobody told. Committing is
  the safeguard, not the risk.
- **The commit says what was WRONG**, not merely what changed.
- ⛔ **Correcting is not redirecting.** Their scope, priorities and open decisions stay
  theirs — fix what is false, `rimflow file --for <them>` anything that is a judgement.
- Enforced, not exhorted: `.claude/hooks/queue_lint.py` WARNS on a cross-seat item
  edit and never blocks it. Pair with the deletion rule directly below — remove wrong
  content, don't annotate it.

## Inaccurate material is DELETED, not superseded-in-place — owner, 2026-09-09

*"Simply remove offending inaccurate material, don't leave it in and supersede
it."* Wrong or dead content is removed outright — git is the provenance — and
every inbound reference is fixed in the same change. A one-line successor
pointer at the top is only for content that MOVED somewhere else (owner,
2026-08-30); it is never a banner over wrong content left in place. Entries
state what IS, never what used to be. "Not my file" does not discharge it.
Single-source only what a generator can enforce; where only discipline enforces
a duplicate, write a pointer instead.

## Git

The laptop's `chore(sync): laptop` sweep commits whatever is in progress under a generic message — if the message matters, commit each unit the moment it lands (2026-09-15).

Explicit paths, never `git add -A`/`.`/`-a` (hook-enforced). Push immediately after
committing; rejected push → `git pull --rebase`, never `--force`. Never a file over
~50 MB.

🔴 **The pathspec goes on the `commit`, not just the `add`** — `git commit <paths> -F -`
(hook-enforced). Four threads share this working tree *and* its index, so a bare
`git commit -m` sweeps a peer's staged files into your commit under your message.
⚠️ The hook is `PreToolUse`, so it refuses a **compound** command whole: if you chain a
file write to a commit, the write never happens either. Keep writes and commits separate.

🔴 **No real merge in the shared tree** (owner, 2026-09-25; hook-enforced by
`block_shared_tree_merge.py`). Merge a branch in a private `git worktree add --detach`, push
`HEAD:main` from there. To publish THIS tree's commits and catch it up, run
`python3 src/RimMandrake/Utils/shared_sync.py` (`git replay` onto origin, push, then `reset --keep`,
which aborts rather than touch a dirty file) — this tree is never clean, so `pull --rebase`
refuses and a bare `git pull` merges. Linked worktrees are exempt.
⚠️ **A REFUSED merge is not harmless**: git's internal restore_state() stashes, hard-resets
and re-applies, and if a peer holds `index.lock` the re-apply fails — that erased 215 files'
edits 2026-09-25 07:54 with nothing in the reflog. The same hook refuses whole-tree
`reset --hard`/`checkout .`/`restore .`/pathless `stash`/`--autostash`/`clean -f` here.

🔴 **A committed mod DLL carries a `.srchash` sidecar and must be pushed together with it**
(`DLL_SOURCE_STAMP_GUARD_1`, `src/Directory.Build.targets` + `src/RimMandrake/Utils/dll_source_stamp.py`) —
after any merge touching a mod's `Source/`, rebuild in the merge worktree; never pick a
side's DLL. Enforced on `git push` by `.claude/hooks/block_dll_source_mismatch.py`.

🔴 **A subagent that runs `git reset --hard HEAD` destroys THIS window's staged work** — one
tree, one index. It ate 3 staged files 2026-09-18. Recovery: `git add` writes blobs before any
commit, so `git fsck --unreachable` + `git cat-file -p <sha>` restores them byte-exact. Brief
every subagent that `reset --hard`, `checkout --` and `stash` on shared paths are FORBIDDEN and
that a conflict is reported back, never cleared — "leave those files alone" reads as licence to
clear them another way.

🔴 **`git rebase --continue` saying "You must edit all merge conflicts" while `git status` says
all conflicts are fixed means the WORKTREE is dirty, not that a conflict remains.** Usually
self-inflicted: `code_review_status.py`'s `_trigger_health_rebuild` spawns the health publisher,
so every `prune`/`list` re-dirties 5 tracked artifacts. Commit them and the rebase finishes
(MIN_INTERVAL is 900 s, so it holds long enough).

🔴 **The ledger is SHARDED PER SEAT since 2026-09-23** (`EVENTS_JSONL_SHARDING_1`, `2b5947555`):
`events.jsonl` is frozen history nothing appends to, and every new event lands in
`infrastructure/state/ledger/events/<SEAT>.jsonl`, so BENCH and FOUNDRY can never rebase-conflict
in one ledger file again. **Two windows of the SAME seat still share one shard**, and a rebase
conflict there is resolved by git PLUMBING, because `Edit`/`Write`/redirect on any ledger file is
hook-blocked by design and the hook refuses the whole compound command.
Build the union of both sides **outside the repo** (`/tmp`), verify every line parses, then
`git hash-object -w` → `git update-index --cacheinfo 100644,<sha>,<path>` →
`git checkout-index -f -- <path>`. Regenerate the two derived queue views with
`rimflow render -- --overwrite-queues` — that flag belongs to `render.py`, must come **after
`--`**, and `reindex` does not accept it. ⛔ **Never resolve it with `checkout --ours/--theirs`:**
that silently discards a concurrent window's events — two BENCH windows appending minutes apart
is exactly when this happens. Done twice — `36de6942c` and 2026-09-23, the second keeping one
window's 11 notes alongside another's 5 events. Verify after: both windows' ids present, and
`unparseable=0` over the whole file.

⚠️ **A `cd` in one Bash call PERSISTS into later calls.** `modcheck` needs
`python3 -m modcheck.cli <verb>` from `src/RimMandrake/Utils`, and after that `cd` a git query
or a glob makes `infrastructure/` look DELETED. Use absolute paths, or `cd` back.

## Code isn't clean until a review says so

**Every file in this repo is dirty by default — including files nobody has
touched today.** The only way a file is CLEAN is a recorded entry in
`infrastructure/state/CODE_REVIEW_STATUS.json` (owned by
`code_review_status.py`, never hand-edited) whose recorded content hash is
byte-identical to the file on disk. No entry, or any byte changed — DIRTY.
(Content-based, not commit-based: a rewrite reverted to identical bytes is
CLEAN; a path moved by `git mv` has no entry at the new path — review 2026-09-06.)

```
python3 src/RimMandrake/Utils/code_review_status.py check <path>...   CLEAN/DIRTY, with the reason if dirty
python3 src/RimMandrake/Utils/code_review_status.py mark-clean <path>  only after a full-file review finds nothing — refuses on uncommitted changes
python3 src/RimMandrake/Utils/code_review_status.py list               every recorded entry and its current state
```

- **Fixing a finding does not clean a file.** Only a full-file review returning
  zero significant findings does, recorded with `mark-clean`.
- **Diff-scoped (incremental) review is only valid once a file is CLEAN.** Before
  that first clean mark, review the whole file — never just the diff.
- A single edit after `mark-clean` makes the file DIRTY again — `check` will say
  so and name the commits.
- **Before spending a review on a file, check it is still reachable** — owner,
  2026-09-03: old scripts sit around long after they stop mattering. A Python
  file with no importer, no `python3 <it>` in any doc/hook/script, and no CLI
  entry point is a DEAD-FILE candidate; a `.cs` file dropped from the `.csproj`
  or with no live caller (reflection-registered bridge tools included — grep
  the tool-name string, not just C# call sites) is the same. Say what you
  checked. **Don't delete on a grep alone — verify, then file it** (or drop
  it, if it's plainly gone) rather than spending a full review on code nobody
  runs. A file only a human runs by hand can look unused to a naive grep and
  not be.

## What is where

**Art is judged against the canon library, and canon is the target** (owner, 2026-09-15).
`design/RimStarWars/canon_references/` holds 137 entries — 45 creatures, 69 species, 23 droid
chassis — each with sourced canon, a visual brief written against real reference images, a
`## Must show` checklist and `## Engine limits`. **An empty `## ruling` means canon stands
unopposed, not that the entry is unusable**; he rules only on ambiguity, deliberate
departures and contested regens. `AGENT_BRIEF.md` there is the operating doc. 🔴 Keep the
three defect classes apart — a **missing gene** is edited in the def, an **engine limit**
needs new art or more mask channels, and a **rig limit** (Ithorian neck, Kaminoan
proportions, Muun body, Lasat legs) cannot be fixed at all, so art chasing it is waste.
⛔ **Cosmetic changes need his permission first** — they can break animated faces.

```
src/                    mods, defs, C#, art            FOUNDRY owns
design/                 campaign specs (Utinni)        the owner's, via BENCH
skills/                 tooling + how-to               curated in fresh-context passes
infrastructure/state/   ledger, items, facts/, V1.md   written only through rimflow
  items/<ID>.md         LIVE item prose only — this glob is the live set
  items/closed/         prose of done/dropped/superseded items (moved on close)
  handoffs/             reboot handoffs — NOT queue items, never greppable queue state
Transient/              output to LOOK AT, then bin    tracked+pushed, ~14 days
```

**Transient rule**: a human reads it once → `Transient/`; a program reads it →
`/tmp`, never the repo; anyone-later → the repo, committed outside `Transient/`.
Tracked and pushed so the owner can review it from another machine (his ruling
2026-09-01, recorded in `.gitignore`), but shelf life is ~14 days: never the
only copy of anything, and never a committed doc citing a file inside it.
`rimflow sweep --transient` lists by age; it never deletes.

## Tools

```
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod <name>   dry run; --apply writes
python3 src/RimMandrake/Utils/refresh.py            rebuild the offline def dump
measure count <DefType>                             one line; never a bare number
python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs ...
./src/RimMandrake/Utils/show.sh <path>              open it in Explorer
./game --said "<his words>" up|down|loading         the moment he says it; bare ./game measures
                                                     🔴 a REBOOT is yours to call, no asking
                                                     (owner 2026-09-02) — bridge free first,
                                                     then GAME_STATE_WORKFLOW.md's gates
./bridge [bench|foundry|free]                       OWNER ONLY — bare ./bridge says who has it
python3 src/RimMandrake/rimflow/cli.py …            the ledger: file/claim/close/drop/verify
node --check <file.js>                              Node 22 is installed user-local
python3 src/RimMandrake/Utils/run_selftests.py      run every selftest before a commit — parallel,
                                                     explicit N/N, never silently truncated
python3 src/RimMandrake/Utils/system_screenshot.py <out.bmp>   OS-level desktop capture (ctypes,
                                                     DPI-aware) — not the game's own F10/bridge
                                                     screenshot. Owner ruling 2026-09-09: always
                                                     OK to take one when in doubt of live state —
                                                     no asking first. Convert with PIL if needed.
python3 src/RimMandrake/Utils/system_click.py <x> <y>          OS-level click at real screen
                                                     coordinates (from a system_screenshot.py
                                                     capture, scaled to its actual resolution) —
                                                     for a Windows dialog a bridge call can't
                                                     reach (UAC/firewall prompts, native error
                                                     boxes). Same DPI-awareness as above.
```

## Options he must LOOK at ship as a savegame — owner, 2026-09-02

*"Save user review options as save games."* A screenshot shows one angle of one
thing; a save lets him walk it, zoom it, and read the tooltips. So when a pass
produces options for him to judge in-world — structures, layouts, creatures,
gear on a pawn — **build them and save the game.**

- **One map, all options** (his ruling by card), laid out on a grid with enough
  pitch that nothing overlaps, plus an item file giving the **grid key**: which
  option is at which cell.
- **Saves stay until he says delete.** Not auto-purged, not overwritten by the
  next review.
- 🔴 **Back up the Saves folder's keepers first and stat it afterwards.**
  `rimworld/save_game` has silently written the CURRENT slot instead of `saveName`.
  Confirm a NEW file appeared and no existing one changed size — never trust the
  path it hands back.
- ⚠️ Verify each option is actually THERE (`jawa/list_things` per slot) before
  calling it a review. A placement log's `thingsSpawned` is a NET count and goes
  negative when a build clears plants.

## Check for existing regenerated art before queuing more — owner, 2026-09-20

Before filing any `fill_queue.py` job (or otherwise deciding art is "owed"),
check whether art for that subject was **already generated and already ruled
on** — the artpipe daemon runs continuously and its output regularly sits
unused for days because the def/roster work that would wire it in hasn't
happened yet.

- **Search `infrastructure/artpipe/done/` (and `_artsrc/`, `registry.jsonl`,
  `art_status.json`) by subject/defName first**, not just by job-id guesswork.
  A finished job's `rimflow_item_id` and `style_notes` often name the exact
  roster row or item it was generated for.
- **Check for a review sheet's `.decisions.json`** (`Transient/*.decisions.json`,
  a `port_tail_*`/`bulk_art_*` sheet, or similar) — if the owner already ruled
  on that art (kept/replace/improve), queuing a fresh regen throws that
  ruling away and spends a job for nothing.
- 🔑 **Caught live, 2026-09-20 (`BMT_FLORA_ABSORPTION_1`):** three plants
  (giant leaf, fire lavender, heatsink fungus) were about to get a fresh
  `fill_queue.py` job each. All three already had finished, validated art
  sitting in `_artsrc/` since 2026-09-12/13 — one traced straight to the
  exact roster row being fixed — found only because the owner said *"I
  actually already saw beautiful art for giant leaf somewhere in a review
  sheet"* and asked for a check across the rest of the missing set. Nothing
  in the workflow up to that point had prompted the check on its own.
- **How to apply:** whenever a def/item is "missing art" or "owed new art",
  search first, generate only what the search comes up empty on.

## The bridge is passed through one file

One window drives the live game at a time — not for ownership, for attributability.
Who holds it is in **`infrastructure/state/BRIDGE`**, one glanceable line written by
`rimflow bridge` and never by hand. It mirrors the ledger; `bridge who` re-derives it.

```
rimflow bridge who                        is it free? (also repairs the mirror)
rimflow bridge take --for "<what for>"    request it — say what for, the other window reads it
rimflow bridge release                    the moment you stop. Not at the end of the session
```

🔑 **It errs toward ALLOWING, never toward mutual lockout** (owner, 2026-09-02).
A take is refused only while the holder is provably alive — an event within 45
minutes; after that the lock is stale and the next window simply takes it, saying so.
`take --force` always works and is recorded. **Nobody is coming to tell you it freed:
if you want it, look again.** ⚠️ Do not message the other window — that channel is off.

⭐ **The owner overrides both of you with `./bridge bench|foundry|free`**, and his word
lands in the same file you already read.

🔴 **Holding the bridge is blanket authorization — never ask what to do with it** (owner,
2026-09-19, verbatim: *"Never ask that. If you have bridge, you may start steam, launch
game, anything you need."*). Once `bridge who`/`bridge take` says it's yours, starting
Steam, launching the game, running a cold load, anything the session needs — none of it
needs a question first. This supersedes asking-first instincts elsewhere in this file for
anything gated only on "do you have the bridge."

`src/RimMandrake/Utils/broadcast.py` is the owner's tool; the game-state relay above is its only carve-out.
🔴 Run commands yourself — a `!`-prefixed paste handed to the owner is the defect
(hook-enforced on Stop); anything he must LOOK at comes with the complete native path.

## Skills

Roster: `skills/README.md`. Most reached for: `rimworld-modding` · `rimworld-deploy`
· `rimworld-load-round` · `rimbridge` · `efficient-subagents` ·
`generating-rimworld-sprites`. Lessons go to
`infrastructure/state/LESSONS_INBOX.md` (one line); skills are edited only in
fresh-context curation sessions.
