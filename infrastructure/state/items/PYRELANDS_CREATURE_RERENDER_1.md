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
2. **Every creature re-rendered under the restored painterly style**
   (ART_PAINTERLY_RESTORATION_1 — the wave-4/5 prompt family is canonical;
   the toy-figurine law and leg budget that stood here 2026-09-13 are
   stood down, preserved only as a selectable option in
   `infrastructure/artpipe/STYLE_CARTOONISH.md`, never default):
   - vivid distinctive coloration — no dull-brown collapse (owner ruling; the
     peko-peko cobalt render is the exemplar);
   - canon creatures: prompts authored FROM the canon reference library
     (gated on CANON_REFERENCE_LIBRARY_1 for those rows only — invented
     creatures proceed immediately);
   - true drawSize canvases (drawsize×128 → next pow2) via
     `infrastructure/artpipe/drawsize_backfill.json` (extend it for any
     roster creature it lacks — dump drops drawSize, use PawnKindDef
     lifeStages bodyGraphicData from mod XML) — a sizing rule of thumb, not a
     refusal; errs GENEROUS until re-measured at the modded maximum zoom-in;
   - all facings each creature ships with (east/north/south minimum), through
     the artpipe daemon; the legibility gate is advisory-only, never a
     rejector (ART_PAINTERLY_RESTORATION_1).
3. **The goal state is the WALK**: after renders pass and deploy, the owner
   walks Pyrelands in game. Deliver via the options-as-savegame rule if a
   staged review map helps, but the real acceptance is his in-game feel.
   Deploy path per rimworld-deploy skill (repo → Mods folder, verify).
4. Flora in the biome is NOT in this item (FLORA_LEGIBILITY_BAR_1 owns the
   flora bar); note in the walk report what flora gaps he will see.

## verify

Roster listed with sources; every roster creature has all facings generated,
deployed; a quicktest or the owner's walk confirms in-game appearance; canon
rows cite their library entries. (The legibility gate is advisory-only per
ART_PAINTERLY_RESTORATION_1 — a band recorded is informative, not a
pass/fail condition.)

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

## Walk 2 staging (2026-09-14 ~01:00, BENCH, owner AFK)

- **The walk map moved: tile 59952, save `PYRE_WALK2_59952.rws`, settlement "Pyrelands Walk" (PlayerColony).** Tile 104504 sits in the scratch world's polar band — the sun NEVER rises there (three screenshots across a full day cycle, glow 0% at 10 AM Clear with zero active conditions). 59952 is equatorial: "Brightly lit (100%)" at 2 PM, Spring. All prior color judgments were made on an unlit map.
- Daylight resolves the ash-tier legibility worry: "Light ash" reads as a distinct pale tier at walk zoom. Standing critique for the owner's eyes: lush green donor flora breaks the burn-biome fiction; steam river reads olive-mud; grey stone scatter reads cold.
- Review grid staged ×2 each at rows z=90/101/112, x=80+11k, order: Razorjack Barbslinger FireWasp Boomsnake FireHawk FurnaceBeast / Orray Gizka Anooba Iriaz Nuna Zeer / Dalgo Boomalope Bolotaur Gualaar GreenGoo. Natural wildlife ALSO spawns here (23 wild roster-kind pawns at mapgen — self-injection working; contrast PYRELANDS_ANIMALS_GENSTEP_1's NRE on the 104504 regen, now known conditional).
- Route that works for a fresh walk map (the leave/re-enter harness silently no-ops on player settlements): `jawa/world_tile_set`+`world_commit` → `jawa/colony_found` (or `world_objects_set` re-faction if a dead Settlement blocks it) → `jawa/world_tile_map_generate` → save+load to make it current. ⚠️ A faction-none Settlement's map AUTO-CLOSES once ticks pass — re-faction BEFORE stepping time.

## Open owner questions (parked while AFK)

1. **Iriaz identity conflict**: `design/RimStarWars/canon_references/iriaz/description.md` exists (four-legged Dantooine antelope, olive-teal + orange spots, one horn, ruling field EMPTY) and contradicts the two-legged Dathomir identity used by both regen waves. No Iriaz art regenerated until ruled.
2. **AA_GreenGoo north**: faceless amorphous slime — its _north reads frontal but there is no rear cue possible. Does the facing law apply to it? (Owner praised this art; untouched.)
3. Anooba + Orray painterly norths are FACE-VISIBLE; corrected rear-view derivations queue on the Codex reset.

## Painterly wave 2 tally (2026-09-14 ~02:30, BENCH, owner AFK) — Codex WEEKLY quota now walled until Sep 19 ~13:01 PDT

**DEPLOYED to the game folder (visible after next restart), all owner-verified-by-eye painterly with rear-view norths unless noted:**
Razorjack (full set) · Zeer (full set) · Dalgo (full set) · Nuna (f full; m north/south are INTERIM COPIES of the f derivations) · EmberGrass A/B/C flora · plus the earlier reverts: Anooba, Orray (norths still FACE-VISIBLE — fix queued), FireHawk, FurnaceBeast.

**In repo only, deploy HELD (incomplete sets would style-flip when turning):**
Mantistanis E+N (south missing) · Boomsnake E (N/S missing) · Gizka + GizkaW easts (N/S missing).

**Not started:** Barbslinger, FireWasp, Quickgrass/Leafless/ScorchFruit/Fulgurite flora, Anooba+Orray rear-view norths, Iriaz (owner identity ruling owed).

**DECISION OWED (owner):** Codex imagegen weekly cap exhausted (plan_type plus, resets Sep 19 ~13:01 PDT). Remaining work waits ~5 days on the Codex-only ruling, or the owner re-rules the channel. The 18 reverted Gemini renders remain in git history if ever wanted.
