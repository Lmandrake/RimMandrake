# PLANETARY_LOADSCREEN_RENDERS_2 — photo-realistic loadscreen planet renders, seeded from OUR worldmap (AFTER the repaint)

Successor to `PLANETARY_BEAUTY_LOADSCREENS_1` (dropped 2026-09-12, "we will do
this manually"). Revived by the owner's typed messages 2026-09-27 (mid-turn,
recorded under BENCH): the old candidates were judged — candidate 2 unusable
(*"there are not supposed to be two suns, and that's also clearly Mars"*),
candidate 1 *"neither positively nor negatively our world... just a random
beauty shot"*. The fix he wants: *"MUCH better informed prompts seeded with
beauty shots from our actual worldmap"*, rendered *"into photo-realistic
imagery that features the planetary ring, our actual terrain appearance, etc"*,
with *"a mapping between the strange colors of the worldmap terrain and what
ours really looks like."*

🔴 **BLOCKED, by his own ruling in the same sitting:** *"That loading screen
generation should get blocked by the repaint of the world and regeneration of
those beauty shots. Otherwise it will be too hard to map from our custom biomes
to realistic imagery I fear."* ⇒ Gate = `BIOME_PAINT_ONCE_AT_THE_END_1` +
`WORLDMAP_BIOME_APPEARANCE_1` (which ends with a fresh beauty-shot set).

## spec (executes after both gates)

1. Inputs: the POST-repaint beauty-shot screenshot set (regenerated at the end
   of `WORLDMAP_BIOME_APPEARANCE_1`; the pre-repaint set at
   `Transient/final_review/beauty/` — crater, scald+seas, ring wide, limb,
   cap, each with a `_clean` variant — shows the intended camera language and
   MUST NOT seed final renders, since its biome faces are the wrong ones).
2. A color→reality mapping table: every worldmap tile color in the seeds mapped
   to what that biome really looks like from orbit, written from the frozen
   sheets (post-repaint this is nearly 1:1 because the biomes will wear their
   own faces — the reason for the gate).
3. Planet facts the prompt must carry: the planetary RING, tidal lock /
   terminator geometry, single sun, desert world register — and explicitly
   NOT Mars, NOT binary star (the failure of candidates 1–2).
4. Pipeline: `editing-images` skill (Codex $imagegen with the screenshots as
   reference), iterate against the seeds; deliver 3–5 candidates to
   `Transient/` for the owner's pick; wiring stays out of scope until he picks
   (mechanism already documented in the closed predecessor:
   `ExpansionDef.backgroundPath`).

## verify
- Candidates are recognisably ASH'KARR — the ring present, the crater/seas/
  terminator where the map puts them — not generic beauty shots.
- The owner picked one (or ruled another iteration).
