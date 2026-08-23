## spec
Two `Inhabited` cast characters are **defined by a breath mask** and, since
`CAST_ROSTER_DEAD_MASK_1` closed, wear nothing at all:

- **Rah'da Onn** (HELIX) — *"The mask rasps on every exhale and he leans in when he speaks."*
- **Kaad'ro Tenth-Breath** (JUNKERS) — *"He cannot breathe your air and never forgets it —
  the mask, the goggles, the ninety-second margin if either cracks."*

Both carried `apparel: guy762_KelDorMask`, a def from a retired mod. It resolved to nothing,
so **they already wore no mask** — removing the line changed the log, not the game. This item
is the part that actually gives them one.

🔑 **In this stack a Kel Dor mask is a GENE, not apparel.**
`RimMandrake_HeadAttachment_keldormask` (`src/Jawa/RimMandrake_StarWarsRaces/Defs/GeneDefs/SW_Genes.xml:1569`)
applies `RimMandrake_GeneHediff_keldormask` and spawns the item on removal.
⛔ **Do NOT "fix" this with `RimMandrake_KelDorMask`.** That def exists and loads, but it is
`ParentName="ResourceBase"` and its own description says *"This is not an apparel item!"* —
a rename trades a loud error for a silent one.

## the blocker, and it is a TOOL change not an XML edit
`src/RimMandrake/Utils/cast_to_xml.py` parses exactly four optional kit lines —
`weapon:`, `apparel:`, `item:`, `skills:`. **There is no `gene:` line**, so the prose cannot
express this today. The work is: add a `gene:` field to the parser, emit it into
`Inhabited.CharacterDef`, and confirm `Inhabited`'s C# reader consumes it — that last part is
unverified and may itself be the real cost.

⚠️ **Check `Inhabited.CharacterDef` accepts a gene at all before touching the parser.** If the
C# has no genes field, this becomes a mod change too and should be sized accordingly.

## verify
`python3 src/RimMandrake/Utils/cast_to_xml.py --dump <capture>/defs` reports `gene 2`, and the
two CharacterDefs carry `RimMandrake_HeadAttachment_keldormask`. In game: both pawns spawn
with the mask hediff.

## criteria
- [ ] `cast_to_xml.py` parses a `gene:` line and round-trips it.
- [ ] `Inhabited` actually applies it at spawn — proven, not assumed.
- [ ] Zero cross-reference errors naming either mask def.

## Watch out
🔑 **`cast_to_xml.py` needs `--dump <capture>/defs`, NOT the DefDump root.** The dump moved to
`captures/<id>/` plus a top-level `defs.sqlite`, and the tool still wants the old per-type
JSON layout. Pointed at the root it fails with `no TraitDef.json` and reads as broken when it
is fine. `validate_patch.py --live` has the same blind spot. See `DUMP_LAYOUT_BROKE_TOOLS_1`.
✅ **The generator has NOT diverged** — measured 2026-08-23: a full `--write` over all 12
roster files changed only the two intended blocks. Regenerating is safe.
