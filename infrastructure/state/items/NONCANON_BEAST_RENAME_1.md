# NONCANON_BEAST_RENAME_1 — non-canon beasts get pseudo-Star-Wars names

## the ruling

Owner, 2026-09-20, verbatim: *"Any non canon beasts need renaming as well into
pseudo Star Wars equivalents."*

"As well" attaches it to `DONOR_DEFS_PORT_TO_OURS_1`, said in the same breath:
as each donor creature becomes our own def, a creature whose name is **not Star
Wars canon** gets a name that sounds like it is.

## what this is and is not

- ✅ **In scope:** beasts with Earth names (`Rat`, `GiantSlug`, `CaveSpider`,
  `SmogMoth`, `Pillbug`), donor-invented names that read as generic sci-fi or
  fantasy (`AA_Needleroll`, `AA_BoulderMit`, `AA_Terramorph`,
  `BMT_PustuleHornet`), and anything a player would not place in the galaxy.
- ⛔ **Out of scope — do not touch:** real canon (`Bantha`, `Kreetle`, `Massiff`,
  `Nerf`, `Eopie`, `Ronto`, `Gutkurr`, `Shyrack`, `Gorg`, `Jamel`, `KraytDragon`,
  `WompRat`, `Mynock`, `Anooba`, `Gizka`, `Varactyl`, `Nuna`, `Lothcat`, …).
  Canon names are the point of the setting; renaming one is a defect.
- ⛔ **Not the flora.** He said *beasts*. Flora renaming has been handled per
  biome by its own verdict pass.

🔑 **The canon test is `design/RimStarWars/canon_references/`** — 137 sourced
entries, 45 creatures / 69 species / 23 droid chassis. If a beast has an entry
there, it is canon and keeps its name. If it does not, check before assuming:
absence from the library is not proof of non-canon, the library is not
exhaustive. The `rimworld-canon-references` skill is the operating doc.

## the precedent to follow

The Rot and Lantern Deeps verdict passes already did exactly this, on his
rulings, with campaign names replacing donor ones — `rot_flora_fauna_names.md`
and `lantern_deeps_flora_names.md` are the worked examples, and
`AA_MycoidColossus` → "vorrugath", `RUT_Nuitae` → "nissik gill" are the shape.
Read those before inventing a naming style; there is one already.

## spec

⛔ **Do not bulk-rename.** This is `kind: design` — per `Agent_Policy.md` design
is backgrounded to a Fable subagent, never done in-window, and the owner reacts
rather than composes.

1. **Census first**: every beast in every owned biome roster, split canon /
   non-canon / uncertain, with its current name, its art, and its biome. The
   MEASURED donor table is in `infrastructure/state/facts/biome_rosters.md`.
2. **Draft names in batches by biome**, so a biome's cast sounds like one place.
   Give each a one-line rationale; he reacts.
3. **Apply only after he rules**, then wire label + description together — a
   renamed def with the donor's old description is worse than not renaming.
4. Record each batch's rulings in the biome's own names doc, matching the two
   that exist.

## Watch out

- 🔴 **Rename the LABEL and the DESCRIPTION together.** A "nissik gill" whose
  description still says "nuitae" reads as a bug to the player. The Rot pass hit
  exactly this on marsh/growable sibling variants.
- ⚠️ **Sibling and variant defs share a base name** (`RUT_NuitaeMarsh`,
  `RUT_WrinklecapMarsh`, `*Growable`). Rename the family, not the base def alone.
- ⚠️ **A defName is not a label.** This ruling is about what the PLAYER reads.
  Whether the defName also changes is `DONOR_DEFS_PORT_TO_OURS_1`'s question, and
  keeping the two jobs separate is what makes either checkable.
- ⚠️ Check a new name does not collide with an existing `<label>` anywhere in
  `src/` — the Rot pass ran that sweep and it is cheap.
- ⛔ "Jawa" is lore text only, never a name tier.

## verify

Every beast a player meets reads as belonging to the galaxy; no canon name was
changed; no label collides; label and description agree on every renamed def.

## criteria

A player who knows Star Wars cannot pick our invented beasts out of the canon
ones by name alone.
