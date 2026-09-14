# PYRELANDS_CREATURE_RERENDER_1 — one dayside biome, every creature re-rendered, walkable in game

Filed by BENCH, 2026-09-13, owner's direct spec: *"regenerate all the contents
for a single biome. Please pick one of the dayside biomes that's currently in
the game (we've regenerated it to our own owned biome fully) and re-render ALL
the creatures present in that biome. We're going to focus on getting a single
biome working fully, so I can walk through it in game and really get a feel
for how it all looks."*

## The pick (BENCH's, one-line owner override welcome)

**Pyrelands** — dayside (the fire-ecology grasslands reskin), fully ours
(`src/RimMandrake/Pyrelands`, its own weather incl. `RM_FE_BlackRain`, fire
ecology engine, RiverSteam wiring via UtinniPatches), and the most complete
kit to judge a whole look in. Alternates if the owner prefers: Scarlands or
Scald (see `design/Jawa/worldbuilding/biomes/kits/`); Webwork is the
wyyyschokk biome and tempting, but it is gated harder on
CANON_REFERENCE_LIBRARY_1.

## spec

1. **Roster derivation (measure, never remember)**: the biome's creature list
   from the LIVE post-patch def (biome wildAnimals + kit-spec additions in
   the Pyrelands kit/spec docs + `decisions_propagated.json` assignments).
   Cross-check against the frozen dump; UNMEASURED beats guessed. List the
   roster in this file before generating anything.
2. **Every creature re-rendered under the full 2026-09-13 lawset**:
   - toy-figurine law: calm neutral pose, flat side profile, flat cel shading,
     no anatomy detail;
   - leg budget: low-slung mass, ≤2 fused stub legs, quarter-height, EXCEPT
     identity limbs (birds, spiders, wings, tentacles) kept prominent-simple;
   - vivid distinctive coloration — no dull-brown collapse (owner ruling; the
     peko-peko cobalt render is the exemplar);
   - canon creatures: prompts authored FROM the canon reference library
     (gated on CANON_REFERENCE_LIBRARY_1 for those rows only — invented
     creatures proceed immediately);
   - true drawSize canvases (drawsize×128 → next pow2) via
     `infrastructure/artpipe/drawsize_backfill.json` (extend it for any
     roster creature it lacks — dump drops drawSize, use PawnKindDef
     lifeStages bodyGraphicData from mod XML);
   - all facings each creature ships with (east/north/south minimum), through
     the artpipe daemon and the locked legibility gate (fitted model +
     floors + auto outside-stroke on borderline).
3. **The goal state is the WALK**: after renders pass and deploy, the owner
   walks Pyrelands in game. Deliver via the options-as-savegame rule if a
   staged review map helps, but the real acceptance is his in-game feel.
   Deploy path per rimworld-deploy skill (repo → Mods folder, verify).
4. Flora in the biome is NOT in this item (FLORA_LEGIBILITY_BAR_1 owns the
   flora bar); note in the walk report what flora gaps he will see.

## verify

Roster listed with sources; every roster creature has all facings generated,
gate-passed (band recorded), deployed; a quicktest or the owner's walk
confirms in-game appearance; canon rows cite their library entries.

## Watch out

- Deploying textures: texture binds by texPath, not defName — byte-identical
  deploys can still render nothing; verify a changed sprite IN GAME.
- Prompts must not say "painterly" (drift source) and must not carry
  reference= for inspiration (reference means reskin-validate — the
  2026-09-13 lesson; inspiration is prompt text + library images).
- model: opus for the roster derivation + walk verification judgment; sonnet
  fine for prompt authoring against ruled library entries.

## Roster (derived 2026-09-13, BENCH, owner present)

Sources: `design/Jawa/worldbuilding/review/round2/decisions_propagated.json`
(fauna:the_pyrelands rows + moves routed here), fire-web commission close
(`PYRELANDS_FIRE_WEB_COMMISSION_1`), live BiomeDef
`src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml`.

**Non-canon / invented — regenerate immediately (owner's word this sitting):**
1. `AA_Razorjack` — fire-follower recast (Alpha Animals donor art = reference)
2. `AA_Barbslinger` — ash-grazer (Alpha Animals)
3. `AA_FireWasp` — (Alpha Animals)
4. `GR_Mantistanis`
5. `GR_Boomsnake`
6. `RUT_FireHawk` — ours; currently single east-facing sprite
7. `RUT_FurnaceBeast` — ours; currently single east-facing sprite

**SW-canon — gated on CANON_REFERENCE_LIBRARY_1 + pilot grades:**
Anooba, Iriaz, Nuna, Orray, Zeer, Dalgo.

**Also in the roster** (per the later, authoritative
`design/Jawa/worldbuilding/biomes/rosters/the_pyrelands.json`, Sep 11 — it
post-dates and supersedes the Sep 10 sheet moves): Gizka (grain 0.3),
Boomalope (0.3, reskin rides the in-joke lane art pass). Burrower slot
deliberately open (commission close); Orray covers the burrows band.

**Known gap (filed as PYRELANDS_FAUNA_WIRING_1):** the shipped BiomeDef's
`wildAnimals` is the core-only vanilla placeholder; NONE of the roster above
is wired into the biome. The walk shows vanilla animals until wiring lands.
`drawsize_backfill.json` has zero roster entries — worker derives from mod XML.

## First-walk owner verdicts (2026-09-14, in-game review tier, scratch map)

- **Bolotaur — DONE** (owner: "I like the Bolotaur... call those done")
- **Gualaar — DONE** (same breath)
- Neither stem exists in the artpipe registry (grep 0) — their art predates or
  bypasses the pipeline; verdicts recorded here as the durable copy.
- **AA_GreenGoo — praised**: "little arms sticking out and waving around. It
  works on the new image." Study note filed (LESSONS_INBOX) on how the wiggle
  is achieved — donor-side animation mechanism + our art interplay.
- Systemic finding this walk: ARTPIPE_FACING_COHERENCE_1 (N/S facings broken
  everywhere, owner ruling recorded there).
