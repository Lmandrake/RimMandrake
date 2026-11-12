# JUDGE: SEA_FLOOR_AND_CATCH_PASS_1 (blind judge, CLAUDE_STEVEDESKTOP_OFFLINE4 clone, 2026-11-11, HEAD 8172fd6026)

I read STATEMENT.md, NOTES.md, the item file's ruling, spec, verify and criteria sections, and all six evidence files. I did not read DONE.md or BROADEN.md.
What I ran myself:
- `selftest_sea_catch_alive.py`: ALL OK.
- `selftest_seabed_descent_wiring.py`: PASS, 25 mutants.
- `TerminalBiomes/validation.py`: STATIC PASS.
- My own parse of the four RM_ sea BiomeDefs, reading labels from the defs (`/mnt/d/ClaudeWork/rimmandrake/judge_seafloor/out.txt`).
- `src/RimUtinni/UtinniPatches/Patches/WildAnimals_TwilightSea.xml`, which adds Mee and Faa to the Twilight Sea.
- `ResyncStaleFloors` in `RM_SeabedLayer.cs`. It is present and committed, and `git status src` is clean.

## The statement has one line. I split it along the item's verify and criteria clauses, because the line says "done as the item file says".

1. **Each sea has a stated shore verdict: TRUE (authored).**
   - per_sea_verdict.txt names the RM_SeaShoreExtension and its shore terrains for all four seas, and every terrain def it names exists.
   - Nothing in the evidence shows a shore cell actually being generated.
2. **Every catch row has a living floor body, or a recorded reason it has none: TRUE.**
   - My own parse agrees row by row:
     - Scald: 9 rows. RM_Saal's body is RM_Noohm, whose label is "saal".
     - Grey: 4 rows.
     - Twilight: 12 rows, plus RSW_Mee and RSW_Faa added by the Utinni patch.
     - Chill: 9 rows.
   - Each body is in its sea's wildAnimals.
   - Every catch is an item, not a race. sea_catch_alive turns red under 4 mutants.
3. **Every sea's description names both its floor and its catch: TRUE.**
   - I checked each creature the text names against the def labels:
     - "iridai" is RM_Muddal.
     - "shimmer eel" is RM_Thuum.
     - Reefback, lanternwhale and gripping terror are all in wildAnimals.
   - One overstatement: the Grey Sea's "under the slow shadow of reefbacks" and the Twilight Sea's lanternwhales and gripping terrors all have weight 0.005. A typical dive will not show them.
4. **validate_patch is clean on every touched file: TRUE.**
   - This rests on offline_checks.txt, which shows 5 XML files OK. I did not rerun it.
5. **"A floor the gravship flies down to and that is populated": CANNOT TELL.**
   - The evidence proves the wiring: the floor BiomeDef exists, the generator lists the fauna genstep, and the density is ×30.
   - Nothing shows a generated floor map or a count of pawns on it.
   - The Chill floor meets a provisional 3 animals drawn from a 10-species roster (GenStep_SeaFloorFauna.cs:91-112). The Grey Sea gets about 6.6. So "shows you the animals its descriptions promised" is doubtful at the Chill even on paper.
   - What would settle it: a generated floor map per sea with pawns counted by kind. That could be a bridge mapgen on a seabed tile with no flight, or an offline mapgen harness.
6. **Criteria: the descent shows the promised animals, and fishing the shore pulls out the same creatures: CANNOT TELL.**
   - All of the evidence is static.
   - The chain audit marks every engine fact as [engine-assumption] because RimSage was not available. That includes the transpiler argument that shore fishing depends on.
   - What would settle it: on each sea's land shore tile, a fishing zone accepted and catches drawn from that sea's table. Plus item 5.

**Overall, the statement line is FALSE as worded ("done as the item file says"):**
- Half of the item's verify and criteria clauses can only be judged from authored defs and code.
- The owner's note of 2026-11-03 puts this item in the Designer bucket ("its design still needs arguing out"). The evidence does not show that bucket being cleared.
- The item names the RUT_ seas, including the Propane Lake, and says of propane fishing "Ask rather than assume". The evidence judges the RM_ seas and treats the Chill as fishable propane. That is a reasonable reading of the RM_ tier move, but no ruling is cited.

## Where the evidence is staged or flattering
- selftests_after_fix.txt is a green subset: 3 of its 5 PASSes are cache answers ("KNOWN PASS ... not spent").
  - The chain audit's own reds are absent from the after-fix evidence: selftest_seashores (a build environment failure), swim_shore_reach under the runner, and the CRASHes of the divinginteraction, seashores and terminalbiomes fuzzers.
  - The audit itself lists them as owed.
- The DLL in offline_checks.txt was built from a "+dirty" source tree (27ee2eb8fa19+dirty). It is not shown that the shipped DLL matches the committed source.
- per_sea_verdict.txt pairs catch to body by the catch def's race/naming. It cannot show that an animal is ever seen.

Owed before this goes to the owner:
- A per-sea floor mapgen count of pawns by kind.
- A shore catch per sea, as a BENCH live look.
- The 4 build-dependent tests rerun green on a seat that has the game assemblies.
- A ruling, or a Designer pass, for the 2026-11-03 Designer-bucket note and the Propane/Chill verb.

would show: no
