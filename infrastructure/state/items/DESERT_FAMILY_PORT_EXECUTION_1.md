# DESERT_FAMILY_PORT_EXECUTION_1 — port the whole desert family to our own defs and art

## the ruling

Owner, 2026-09-20, verbatim: *"Yes. All of the desert sheet should be keep but
replace with our own version of creature and art. Port. All of them. Now."*

Every one of the desert sheet's **109 rows** is `replace`. Nothing is cut. The
decisions file is frozen and records that the ruling was blanket and uniform —
his instruction, not a default.

This satisfies `DONOR_DEFS_PORT_TO_OURS_1`'s "keep/cut pass first" precondition
**for the desert family only**. The other ~190 species still need their own pass.

## the work, MEASURED from the sheet's own rows

| origin | rows | port work |
|---|---:|---|
| Star Wars Animal Collection (mlie) | 68 | port |
| Alpha Animals (sarg) | 14 | port |
| Outer Rim — Droid Depot | 7 | port ⚠️ **mod is INACTIVE**, see below |
| Vanilla Core | 5 | re-author as ours |
| Alpha Biomes (sarg) | 4 | port |
| ReGrowth 2 (BOTR) | 4 | port |
| Horrors (mlie) | 1 | port |
| VFE Insectoids 2 | 1 | port |
| Vanilla Biotech DLC | 1 | re-author as ours |
| **OURS already** (3 SWBestiary, 1 UtinniPatches) | **4** | **no work** |

**~105 species to author.** By kind: ~92 fauna, ~17 flora.

## 🔑 the precedent — copy it, do not invent one

`BMT_FAUNA_ABSORPTION_1` already did exactly this operation for three Biomes!
Team mods: **68 defNames ported to `RSW_`**, landed at
`src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/` (Bodies, SoundDefs, Support,
ThingDefs_Items, ThingDefs_Races). Read that folder's header comment before
touching anything — it is the operating manual and it records what went wrong.

What it establishes:

- **Reference closure is the job.** Port the species *and* every def pulled in by
  reference — bodies, eggs, leather, sounds, hediffs, damage types — "so nothing
  dangles". A ported creature with a dangling BodyDef is a broken creature.
- **Drop donor-framework comps.** Any `modExtension`/comp whose C# lives in a
  retiring or inactive assembly comes OUT; the creature keeps its stats, body and
  behaviour-free form. Do not reimplement donor AI in this pass.
- **Repath texPaths.** The donor's texPath does not follow the def. A texture
  binds by `texPath`, not defName.

🔴 **ONE DELIBERATE DEPARTURE FROM THAT PRECEDENT.** `BMT_FAUNA_ABSORPTION_1`
copied the donor's textures verbatim. **This ruling does not** — he said *"our own
version of creature and art"*. So every ported species needs a NEW render, filed
through `fill_queue.py` only. Donor art may stand in only as a temporary
placeholder, and only where it is loudly commented as such.

## naming

- **Canon keeps its name.** Bantha, Massiff, Eopie, Ronto, Shyrack, Krayt dragon,
  Womp rat, Mynock, Gizka, Varactyl, Nuna, Lothcat and the rest are the point of
  the setting. Grade against `design/RimStarWars/canon_references/` (137 entries)
  via the `rimworld-canon-references` skill.
- **Non-canon gets a pseudo-Star-Wars name** — `NONCANON_BEAST_RENAME_1`.
  ⚠️ That item's own design is *"agent drafts, owner reacts"*. **Assumption this
  item proceeds under:** names are DRAFTED now so the port is not blocked, and
  surfaced to him in a batch for reaction. A drafted name is not a ruled name —
  mark them so, and never let a drafted name reach a canon creature.

## sequencing

1. **Defs first** (offline, unblocked) — author the defs with reference closure.
2. **Art jobs** as each batch's names settle — the art prompt needs the ruled
   name and description, so naming gates art, not defs.
3. **Land art** as the daemon clears it; review by eye before wiring, the way the
   Rot wave did — 4 of 61 renders there were bad and only an eye caught them.
4. **Rewire the biome tables** last: donor entry out, our defName in, `MayRequire`
   dropped because it is ours now.

## Watch out

- ⚠️ **Droid Depot is NOT in the active mod list** (`BIOME_ROSTER_DEAD_SPECIES_REFS_1`).
  Its 7 droids cannot be read from a live game. Porting them means authoring from
  the donor's files on disk, or deciding they do not come back at all — that is a
  question for him, not an assumption for this item.
- ⚠️ **5 Vanilla Core + 1 Biotech row.** Replacing vanilla is consistent with the
  desert cards' standing ban on *"instantly-nameable Earth organisms"* (plain
  `Rat` is in this set). But it is a bigger departure than porting a donor —
  confirm with him before authoring those 6.
- 🔴 The def dump has **no `statBases`** — calibrate from donor mod XML, never the dump.
- 🔴 Fauna size is the ADULT life stage `lifeStages/li[3]`, never `[0]`.
- ⚠️ `AB_GiantStikehr` was cut from the Extreme Desert this same day as misplaced;
  it is NOT part of this port. Do not re-add it.
- ⚠️ The world is repainted at the end (`WORLD_REMAKE_FINAL_STEP_1`) — do not
  build migration machinery for the current save.

## verify

Every desert-family biome table names our defs only; each donor mod can be
removed from `ModsConfig.xml` with the three biomes still generating; every
ported species has its own art; confirmed from a post-load def dump, never from
the patch files.

## criteria

The desert family is ours. Removing Star Wars Animal Collection, Alpha Animals,
Alpha Biomes, ReGrowth or Droid Depot changes nothing a player sees in the desert.
