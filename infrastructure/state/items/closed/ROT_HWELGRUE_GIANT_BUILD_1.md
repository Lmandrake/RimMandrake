# ROT_HWELGRUE_GIANT_BUILD_1 — the hwelgrue, the gut that walks: a huge slow maggot of the Rot that eats whatever lies down and passes polished salvage

Caused by `ROT_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.therot`. Design:
`design/Jawa/worldbuilding/biomes/rot_bedazzle_review_2026-10-02.md` §3 (the hwelgrue), §8;
`design/Jawa/worldbuilding/biomes/rot_new_marks_redo_2026-10-02.md` (what hangs off it).

Ruling, owner, typed 2026-10-02: *"(2) is AWESOME. Like a huge maggot slow maggot covered in small wriggling
tentacles and eye spots, I love the old ship that's pinging from within begging the players to figure out how
to kill it."* Build-first card: **land the decided work plus the giant** (decision taken by question card
2026-10-02 10:20 PDT). Name **hwelgrue** (`RM_Hwelgrue`): collision-proven in review §3 (0 files in `src/`,
`design/`, `infrastructure/` outside the review; stem `hwel` opens no other word; 0 Wookieepedia hits); re-checked
2026-10-02, 0 artpipe hits. Bans: **2** (it is a fungus/animal hybrid), **7** (no engineered organism), **8**
(the prize inside it is defended: by the giant itself).

Siblings, same sitting, all hang off this body: `ROT_STILL_ALIVE_SWALLOW_1` (it swallows the downed),
`ROT_SWALLOWED_NAVIGATOR_1` (the pinging drive core inside it), `ROT_GUT_MOTHER_VAT_1` (the sac cut from its
corpse).

## spec

1. **Body.** `ThingDef RM_Hwelgrue` + `PawnKindDef RM_Hwelgrue`: a colossal, slow, maggot-shaped decomposer,
   bone-white with a lilac underside, its whole length covered in small wriggling fungal feeding tendrils and
   scattered dark eye spots, a blunt front end opening into a dredge mouth rimmed with hyphae. Body size ~8,
   very high health scale, slow (move speed ~1.2), never tameable, never hunts, never flees, no
   manhunter-on-tame. Own `BodyDef` only if a vanilla insect/worm body cannot carry it (measure; prefer a
   vanilla one). Wild-only, `RM_TheRot/wildAnimals` at a very low commonality (one per map at most: a
   map-component cap, default 1), plus a guaranteed one on a Rot map whose tile is flagged by
   `ROT_SWALLOWED_NAVIGATOR_1` (that item owns the flag).
2. **It eats whatever lies down.** A think-tree branch (vanilla wander + a new `JobGiver_RM_GutGraze`): it
   crawls to and eats, in order of nearness: corpses, rotten or rotting food, and any haulable item lying on
   open ground (not in a stockpile zone, not under a roof). Eating destroys the thing; **downed pawns** are
   `ROT_STILL_ALIVE_SWALLOW_1`'s and are not eaten by this branch.
3. **It digests everything but metal.** Each eaten thing's metal content (its `costList`/stuff entries whose
   `ThingDef` is in the metallic stuff category, plus components and plasteel; corpses' carried
   weapons/apparel/inventory likewise) is put into a `ThingOwner` on the comp `RM_CompGutDigest`, not
   destroyed. Every **2 days** (setting) of crawling, if the owner holds anything, it passes one
   `ThingDef RM_SheenCasting`: a glossy Sheen-glazed shell holding those items. Opening it (a short job, any
   colonist; or a recipe at any crafting bench) drops the contents **polished**: hit points restored to
   full, quality unchanged. Non-metal things are gone for good. So scavengers follow it, and its trail is a
   salvage line.
4. **Where it rests, things rot.** While it stands still (idle) it applies the existing
   `RM_AcceleratedRotExtension` multiplier (×3, setting) to cells within 6 and marks them as warm ground
   through `RM_MapComponent_WarmGround` (reuse; no new meter).
5. **Hard to kill on purpose** (*"begging the players to figure out how to kill it"*): it never attacks first,
   but when hurt it turns and crushes whatever hurt it (melee only, slow), its hide halves sharp and blunt
   damage, and fire does full damage (the Rot's fungal weakness, shared with its kin). Ship weapons on it harm
   the core inside (`ROT_SWALLOWED_NAVIGATOR_1`).
6. **Death and butchering.** Butcher products: meat (insect), `RM_GutMotherSac` × 1 (defined by
   `ROT_GUT_MOTHER_VAT_1`), and everything in the digest owner dropped as castings. The drive core drop is
   `ROT_SWALLOWED_NAVIGATOR_1`'s.
7. **Readable signs:** inspect lines (*"Digesting. Something metal rattles inside."*, the casting timer), a
   letter the first time one is seen on a map, the castings on the ground behind it.
8. **Not the donor giants:** `AA_MycoidColossus` (vorrugath) and `AA_AnimaColossus` stay as rows; this is our
   own giant, not a replacement.
9. **Mod Settings** (Giant section): on/off; casting interval; rot multiplier; map cap.

Art: `RM_Hwelgrue` (three facings, giant), `RM_SheenCasting` in
`infrastructure/artpipe/art_lists/rot_turn1_2026-10-02.csv`. Depends on: none hard; soft
`ROT_RM_CAST_MIGRATION_1` (the free roster it joins). `THE_ROT_FIRST_SCRIPT_1` is written against this state.

## criteria

Deterministic, in `THE_ROT_FIRST_SCRIPT_1`'s `validation.py`, through `jawa/get_defs` and debug `[Tool]`s:
- `ThingDef/RM_Hwelgrue`, `PawnKindDef/RM_Hwelgrue`, `ThingDef/RM_SheenCasting`, `JobDef` for the graze job
  resolve; `RM_Hwelgrue` body size ≥ 6, not tameable (`RaceProps` read); description contains no `Force`.
- Graze: on a test map with one hwelgrue, a corpse and a steel-made weapon on open ground 10 cells away: after
  30,000 ticks both are destroyed and the comp's owner holds a steel-content thing (count > 0). A corpse inside
  a stockpile zone under a roof is untouched.
- Casting: after the interval with a non-empty owner, exactly one `RM_SheenCasting` exists on the map; opening
  it spawns the held items, each at max hit points; the owner is then empty.
- Rest: a raw meat stack within 6 cells of an idle hwelgrue rots strictly faster than one 20 cells away.
- It never starts a fight: over 60,000 ticks with an armed, undrafted colonist nearby, the hwelgrue's job is
  never an attack job unless it was damaged first.
- Butchering a dead hwelgrue yields ≥ 1 `RM_GutMotherSac` (once that def exists).
- Map cap: forcing 3 spawn attempts leaves 1 hwelgrue on the map.
- Each Mod Settings toggle off removes exactly its effect.
</content>
</invoke>
<invoke name="Bash">
<parameter name="command">head -1 /home/mandrake/rm/bench/infrastructure/state/items/ROT_HWELGRUE_GIANT_BUILD_1.md
## built (2026-10-03, FOUNDRY offline builder r14)
- `Source/RM_Hwelgrue.cs` + `Defs/Fauna/RM_Hwelgrue.xml`: race on `RM_RotLarvaLike` (no new BodyDef), body 8, health ×10, move 1.2, sharp/blunt armour 0.5, heat 0; graze via an `Animal_PreWander` splice (`RM_JobGiver_GutGraze` -> `RM_GutGraze`), `RM_CompGutDigest` (metal whole into a ThingOwner, rest destroyed, corpses' gear sorted), `RM_SheenCasting` (CompUsable "Crack open", contents to full HP; a smashed casting still drops its metal), rest rot ×setting within 6, retaliation melee on whoever hurt it, map cap, first-sighting letter per map. Inline roster row 0.02. Art wired from `_artsrc` (east/south; south stands in for north, north requeued). Giant section in Mod Settings (on/off with roster removal at startup, casting days, rot multiplier, map cap); settings screen now scrolls.
- Deviations: contents drop as a casting at DEATH, not at butchering; warm-ground marking not built (`RM_MapComponent_WarmGround` is terrain+room scoped with no cell API); the wild-spawn guarantee on a navigator-flagged tile belongs to `ROT_SWALLOWED_NAVIGATOR_1`.
- validation.py chain `hwelgrue` (map cap, digest, casting via `RM_HwelgrueProof`); live proof owed — first poke: `jawa/static_call RimMandrake.TheRot.RM_HwelgrueProof ProofSpawn 3` on any map.
