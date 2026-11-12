# BROADEN — what a real player would try that the proof did not

## The question (to GPT via `src/RimMandrake/Utils/gpt_consult.py`, 2026-11-11 21:59 -0800)

I gave it the owner's statement, what the feature does (notches, the deep-stone pick, the 25% roll and the new certain
first strike, the lip rule, the letter's exact text, the settings), what I had tested live (a bridge pre-dug D3 square, a
colonist with a shovel cutting D3 -> D4 at the player's own settings, the work scan taking the job, the letter and pit
captured, the deep rock's wall count on the map measured at 0) and what I had not (digging from the surface, wide pits,
machines, ice, save/load, a biome with its own deep-rock list, mineral finds on together with deep stone, no lip nearby).
Asked: "what would a real player try that I haven't (someone new, someone experienced, someone trying to break it, a messy
real case)? Give the 5 most revealing concrete experiments, ranked, each with what outcome would reveal a defect."

## The answer (verbatim)

1. **Play the whole first dig with an ordinary colony.** On a fresh map, leave mineral finds on, use a normal shovel-equipped miner, and designate one square from untouched ground through D4. Let meals, sleep, other jobs, and hauling interrupt naturally. Watch the instant each notch finishes; a hauler might move the chunk before you inspect it.  
   **Defect revealed:** deep stone appears before D4; an interrupted job skips or repeats a notch; the first D4 cut produces no deep chunk; or a mineral find suppresses the deep chunk or its letter. Check that the letter names the actual chunk and the colonist who finished the cut.

2. **Make the first discovery happen where no chunk can land.** Prepare a broad pit whose central square has no standable, undug square within six squares, then have a colonist finish that square’s D3→D4 cut. Afterwards, finish a fresh D3 square at the outer edge, beside valid ground. Also try leaving exactly one eligible lip square for the central cut.  
   **Defect revealed:** an error or stuck job; a chunk placed in dug ground or beyond the search radius; a letter falsely announcing a chunk at the edge; or the failed placement consuming the guaranteed first discovery, so the later valid cut loses it. With one eligible square, placement should find it.

3. **Save across discovery, then try the refill exploit.** Save just before the first D4 completion and reload to finish it. Save again after receiving the chunk and letter, quit and reload, then refill that square and dig it back to D4 repeatedly. Finally, reach D4 on fresh squares.  
   **Defect revealed:** reloading loses the pending first-discovery guarantee; the discovered map sends another first-find letter; or the refilled square produces another deep chunk at an already-rolled depth. Fresh squares must remain eligible. Replaying the *pre-discovery* save and getting its first letter again is expected.

4. **Have several miners break through together.** On a fresh map, prepare three separated D3 squares, each with an obvious valid lip. Give three shovel-equipped colonists access and arrange their final notches to finish close together at high speed. Keep mineral finds on and inspect all resulting chunks and notifications.  
   **Defect revealed:** multiple first-find letters, inconsistent deep-stone types on one map, a letter crediting the wrong miner, or no guaranteed chunk across those first completions. Several chunks are legitimate: subsequent cuts can succeed at 25%. Several *first-discovery letters* are not.

5. **Take the feature somewhere its usual stone selection cannot hide mistakes.** Repeat a normal first discovery in a biome with an explicit deep-rock list, then on a map using the fallback selection. For the fallback map, inspect both its natural walls and its tile’s surface-stone types; absence of spawned walls alone does not establish that a rock is absent from the surface selection. Reload each map and discover the layer at another location.  
   **Defect revealed:** the explicit biome list is ignored; fallback chooses a surface stone or one vanilla disallows in that biome; the selected layer changes after loading or between locations; or the letter names a different stone from the chunk.

## What I tried, and what I found (SteveDesktop game A, fresh quicktest maps, current build)

Added to the proof as broaden modes of `src/RimMandrake/FlowWorks/northstar/deep_stone_live.py`, each its own row id so the
statement rows stay unchanged.

1. **The whole first dig, ordinary colony (GPT's #1)** — `--from-surface`: a colonist with a shovel digs untouched soil
   from D0, re-designated after each notch as a player clicks dig again; the colonists' own work scan takes every notch.
   - First attempt: every colonist died by tick 20,000 ("Death: Forbes — beamed to death", three of blood loss). The map
     had an ancient complex with security turrets ~40 squares east. That is the SITE, not the mod. The script now stops
     the wait the moment no colonist is left and says so, instead of stepping out its whole budget over corpses.
   - Second attempt (`evidence/ds_surf2.json`, `evidence/deep_stone_surf2_pit__cell_rect.png`): PASS. Notches landed at
     ticks 6,500 (D1), 19,000 (D2), 38,500 (D3) and 68,500 (D4). The soil notches turned up nothing ("Dirt makes no
     chunks"), so nothing before 2 m. The D4 cut gave ChunkSlate on undug ground (chunk-square depth 0) and the letter
     "Deep stone: Slate", "Jonny dug 2 m down and broke through into a layer of slate...". That is the "digging finally
     pays" moment in ordinary play: about a colonist-day of digging with no reward, then the reward at 2 m.
   - Caveat I caught in the record: this run's `settings_before` shows mineral finds OFF. Two runs I had killed earlier never
     reached their `finally`, so the run override stuck in the game's settings. I restored the shipped defaults and read
     them back. I tested finds-on separately (item 3) and filed the trap as a lesson.
2. **The first discovery where no chunk can land (GPT's #2)** — `--wide-pit 15`: a 15 x 15 pit pre-dug to D3, only its
   middle designated. Found: no colonist can reach the middle (`flowworks_job_probe` canReach false for all three), so in
   FlowWorks a colonist cannot make that cut at all. The case GPT worried about cannot arise from colonist digging. I still
   widened the lip search from 6 to 12 squares, because the old fallback (the cut square itself) would drop the find
   back into the pit the letter says it lies beside. The code keeps the first-strike certainty unspent when placement
   fails (`found` is recorded only after a successful placement).
3. **Mineral finds together with deep stone (GPT's #1, the part the first attempt missed)** — `--finds-on`: finds on at
   the player's settings, with the proof's `force` armed so the D3 -> D4 cut certainly rolls a mineral find too
   (`evidence/ds_finds.json`, `evidence/deep_stone_finds_pit__cell_rect.png`). PASS: one cut gave ChunkSandstone at
   (48,47) AND 10 Steel at (47,48), two different lip squares, and two letters, "Found while digging: Steel" and "Deep stone:
   Sandstone". Neither swallowed the other's chunk or letter. The report's `last` reads the steel (written second); the
   deep chunk is counted (finds 2, first-found 2).

Not tried from the list: save/load across the discovery (GPT #3; `found` and the rolled-depth grid are both scribed, read
in code by the reviewer, not exercised live), several miners breaking through together (#4), a biome with its own
`deepRocks` (#5: no BiomeDef carries the extension yet, so only the fallback exists to test). On #5's point that "no
spawned walls" is not "absent from the tile's surface types": the fallback excludes the tile's own `NaturalRockTypesIn`
list in code, and the proof now measures the map's actual walls (0 of the deep rock in every run).
