# GELATINOUSSLIME_TITAN_CHUNK_BOMB_1 — the giant's story: a chunk of the titanoslime is a terrible bioweapon

**Free tier** (the chunk and its use as a weapon), `mandrake.rm.gelatinousslime`. The vault use is campaign:
`GELATINOUSSLIME_VAULT_SEAL_BREACH_1`. Design: `design/Jawa/worldbuilding/biomes/gelatinousslime_bedazzle_review_2026-10-02.md` §3 (the giant), §8.
Caused by `GELATINOUSSLIME_SCORING_SITTING_1` (turn 1). Owner, typed 2026-10-02 (card, item 2): *"Grab a chunk of the giant and it becomes a terrible bomb like weapon to use on someone. Bioweapon after all. Can use it to open one of the vault dungeons blocked by assailant seals."* None of the three pitched stories (the unfiled hull, the cook's giant, the return to sender) was chosen; this replaces them.

## What exists (reuse first)

- `RM_Titanoslime` (bs 6, five life stages, engulf via `RM_CompEngulfer` + `RM_Verb_MeleeEngulf`, grows as it
  eats, sheds gelatids when cut, shrinks off the body, six settings): `TITANOSLIME_SLIME_BIOME_1`,
  `design/RimMandrake/RM_titanoslime_spec.md`.
- Slimification (`HediffComp_Slimification`) is the body's reading; the engulf is its digestion.

## spec (BENCH's reading of the ruling; numbers `// INVENTED`)

1. **Taking a chunk:** cutting a titanoslime (or butchering one) yields `RM_TitanoslimeChunk`: a live piece of
   the giant, still reading. Taking it is the danger (it sheds and engulfs as it does today).
2. **The weapon:** the chunk is thrown or planted (a grenade-shape verb or a placed trap; FOUNDRY picks the
   cheaper honest route). On release it bursts: everyone in the radius is drenched and starts slimification at
   a late stage, and nearby ground turns to slime terrain for a while. *"Terrible"*: no armour stops it; only the
   antidote and dry ground undo it. Readable: a green burst, the alert naming who was drenched.
3. **It does not keep:** off the body the chunk shrinks like the giant does, so it is a carried, timed weapon,
   never a stockpile (keeps sheet ban 6, no shelf-stable extraction). A settings slider for the shelf time.
4. **It is not the body arming itself.** Ruled an exception (decision taken by question card, 2026-10-02 14:44 PDT) to sheet §6 ban 7 (*"no re-arming… content re-arming it
   (weapon-generation behavior) is a violation"*): the owner's explicit ask makes a harvested piece a weapon in
   the clan's hands; the body itself still never generates weapons. Recorded as his, not altered.
5. Settings: on/off for the chunk weapon.

## criteria

- `jawa/get_defs` `ThingDef/RM_TitanoslimeChunk` `foundCount` 1.
- Live (quicktest): a thrown chunk drenches a test pawn into slimification; an unused chunk shrinks to nothing
  within its shelf time.
- Art from `gelatinousslime_turn1_2026-10-02.csv`.
