## spec
The 2026-08-23 15:35 load is harvested OFFLINE and every offline signature in §10–§17 of
`infrastructure/state/EXPECTED_FAILURES_next_load.md` is answered — see the
`§10–§17 RESULTS` block appended by BUILD at 16:0x. This item is the half BUILD cannot
answer: the readings that need a running map, a spawned pawn or a tamed animal.

⛔ **Do not re-run the offline half.** It is done and quoted with its commands.

🔴 **The log evidence dies at the next launch.** `Player.log` rotates to `Player-prev.log`
on launch and the old prev is destroyed, so anything you want to quote from THIS load must
be quoted before the game restarts.

### The ⬜ rows, in the order they are cheapest to get

**On any map, no colony needed — dev-spawn and read the INSTANCE, not the def:**
- **T1** a pawn of a species with NO temperature gene (`Ugnaught`, `Twilek`, `KelDor`):
  `ComfortableTemperatureRange` PASS = **−40…+45**
- **T2** `Jawa` ≈ −40…+65, `Chiss` ≈ −50…+45 — proves the gene offsets still STACK
- **N1** a `Jawa` and a vanilla-human raider, PASS = **−50…+55** and **−40…+45**. Same
  reading = the xenotype patch did not apply; Jawa at −60…+65 = the LARGE tier came back
- **N2** a Wookiee reads comfy **−60**…+55 (`Furskin` stacks)
- **N3** no pawn carries BOTH `MinTemp_SmallDecrease` and `MinTemp_SmallIncrease`
- **J6** `Plants disabled` reads **False** on a Jawa

**Needs a growing zone and two pawns:**
- **J4** a Jawa will not sow; a Baseliner in the same colony will
- **J5** 🔴 the same Jawa still HARVESTS, CUTS plants and CHOPS trees. This is the failure
  mode, not a bonus check

**Needs one tamed animal — and this is the reading that matters most:**
- **P2** tame an animal and read its name. PASS = a corpus name; FAIL = `"<Race> 1"`.
  If it fails the cause is almost certainly Harmony patching a method the JIT INLINED, and
  the fallback is a postfix on `PawnBioAndNameGenerator.GeneratePawnName` guarded on
  `style == NameStyle.Numeric`
- **P3** over ~15 tames, roughly 2 in 3 lore / 1 in 3 humour
- **P4** ⛔ no MECHANOID is named this way
- **P5** a bonded animal keeps its bond name; a player-renamed animal is never overwritten

**Needs specific conditions:**
- **G3** LOOK at a `HorrorWastes` quicktest map — pale ice and near-black frozen muck, not
  warm sand, and plants CLUSTERED rather than uniform
- **T3** an unclothed pawn on `AB_PropaneLakes` (−59.8) takes hypothermia; on
  `ExtremeDesert` (+48.2) does not overheat. **Both outcomes are required**
- **T5** a raid arriving in a cold biome does not freeze before it reaches the colony
- **J7** a droid raid arrives with no NRE naming `Pawn_RelationsTracker`
- **J8** vanilla mechanoids still have NO relations — a centipede with a social tab means
  the guard is wrong
- **N5** the Ancient Arsenal boss draws from a real pool. ⚠️ two of its three offline
  warnings were `<match>` branches with 0 nodes, so the `<nomatch>` path is what fires and
  it is the untested half
- **K6/K7** a Blackstar Leader spawns holding a KotOR legendary weapon, not bare.
  ⛔ **If Blackstar arrives as one or two pawns that is the INTENDED SHAPE** — the owner
  took the difficulty jump on purpose. Do not "fix" 997/718 back down
- **H5** at `Page_SelectStartingSite`, `python.exe src/RimMandrake/Utils/w9_run.py` dry run
  prints `planetCoverage 1` and `tilesCount 21872` with nobody touching a control.
  ⚠️ bridge calls at that screen take **over 25 s** against a 30 s default — use
  `timeout=150` and a fresh connection per call
- **H6** the coverage control and the MLP slider are still draggable
- **H4** `[PlanetPresetPrime] ready:` fires when the world-creation page opens. It never
  opened this load, which is why it is unanswered rather than failed

## Watch out
- 🔑 **The bridge is UP and holds 246 tools, 121 of them `jawa/`.** Build `c1f3121ddf9e`,
  `modSet 581/fc658bb0`, `defDump ARMED`, `engine 1.6.4871 rev591` — all confirmed.
- ⚠️ **A `[JawaBench]` line proves nothing about a load until someone calls a tool** — it
  is a module initializer and fires on first execution, not at assembly load. If you see no
  `[JawaBench]` in a log, that is UNMEASURED. `BUILDABLE.md` 22.
- ⚠️ **Reading a def is not any of T1, T2, N1 or N2.** Apparel, hediffs and any Harmony
  `StatPart` in the 581-mod stack can shift the final number, and the assemblies were never
  censused. Read the INSTANCE.
- ⚠️ **T1 and T3 are a pair, and so are J4 and J5.** Neither half implies the other, and in
  both cases the second half is the one that catches an overshoot.
- 🔑 **The def dump is now current** — 581 mods, 79,093 defNames, 534 types, coverage
  complete, `captured=2026-08-23T22:49:51Z`. §12's G8 gap is CLOSED: an ABSENCE from the
  dump is evidence again. But a Cherry-Picker cut is still invisible there in both
  directions — use the log's removal block (`BUILDABLE.md` 21).

## verify
every ⬜ row above answered in the `§10–§17 RESULTS` table with the instrument's own output
pasted, not an assertion. A row that could not be reached is marked UNMEASURED with the
reason, never left blank and never inferred from a neighbouring pass.

## criteria
P2, N1 and J5 are the three that decide whether this build shipped what it claims: P2 is
the only proof the pet-name hook was not inlined away, N1 is the whole native-edge ruling in
one probe, and J5 is the check that the no-sow rule did not take harvesting and tree-chopping
with it.
