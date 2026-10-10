# GELATINOUSSLIME_VAULT_SEAL_BREACH_1 — a giant's chunk opens a vault blocked by an Assailant seal

**Campaign tier** (`RUT_`, the vault family). Design: `design/Jawa/worldbuilding/biomes/gelatinousslime_bedazzle_review_2026-10-02.md` §8. Depends on `GELATINOUSSLIME_TITAN_CHUNK_BOMB_1`.
Caused by `GELATINOUSSLIME_SCORING_SITTING_1` (turn 1). Owner, typed 2026-10-02 (card, item 2): *"Grab a chunk of the giant and it becomes a terrible bomb like weapon to use on someone. Bioweapon after all. Can use it to open one of the vault dungeons blocked by assailant seals."* None of the three pitched stories (the unfiled hull, the cook's giant, the return to sender) was chosen; this replaces them.

## What "vault dungeons blocked by assailant seals" refers to

Searched `src/`, `design/`, `infrastructure/state/items/` and canon (2026-10-02) for assailant seal, sealed
vault, vault dungeon. **The vaults exist; no seal def existed when searched.** The seal is now ruled (see the 2026-10-09 ruling below).

- **The vault dungeons are the six Forsaken vaults**: `design/Jawa/worldbuilding/dungeons_arc_spec.md` §3,
  `VAULT_DUNGEON_BUILD_1` (layouts, `RUT_VaultHeart`, `src/RimUtinni/StructureInjectionsRUT/Defs/VaultDungeons/`),
  `VAULT_THAW_QUEST_FAMILY_1` (the quest family; both FOUNDRY, doing). Type ② vaults (V4 Deadstone, **V5 the
  Slough**) are the ones the Assailant's flesh weapon breached; **V5 sits in the Slough, the Slime's own largest
  patch** (landmark `RUT_Slough_GelatinousBreach`). The Slime is the Assailant's bioweapon (sheet
  `the_slime.md`, the Rot's sibling).
- **Sealed doors in the record:** V6's arrival text (*"The doors are sealed from both sides"*, spec §3.10) and the
  Assailant complex's *"previously-sealed passages"* that open on the thaw (spec §2.3, `ASSAILANT_DUNGEON_BUILD_1`).
  Neither is called an Assailant seal, and **no seal mechanic, door def or "nothing else opens it" rule exists**.

## spec

1. An **Assailant seal**: a sealing growth or plug of the Assailant's flesh across one vault's inner door
   (candidate: a type ② vault; V5 at the Slough is the obvious first), impervious to ordinary breaching.
2. A thrown or planted titanoslime chunk **reads and dissolves the seal** (the bioweapon eats its maker's
   work), opening the way; the cost is the chunk's drench radius at the door.
3. Built inside the vault family's templates, not as a separate site. Notes on `VAULT_DUNGEON_BUILD_1` and
   `VAULT_THAW_QUEST_FAMILY_1` point here.
4. **Ruled (decision taken by question card, 2026-10-02 14:44 PDT):** only the Slough vault (V5) carries the seal, and a chunk is the only way through it.

## criteria

- Live: a vault map with the seal; a chunk dissolves it; ordinary explosives do not.

## Ruling 2026-10-09 (decision taken by question card)

The seal is a **flesh plug across the Slough vault's (V5) inner door**: a new building def with its own art, placed by the vault layout, dissolved only by a slime chunk (ordinary explosives do nothing). Build is filed as `GELATINOUSSLIME_VAULT_SEAL_PLUG_1` (def + art + vault placement).
