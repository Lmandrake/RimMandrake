## ⛔ CLOSED BY THE OWNER — DO NOT REOPEN THIS, 2026-08-23

**The owner closed this item himself at 20:15 UTC**, recorded on the ledger:

> *"remove the DECIDE item before it gets picked up"*

⚠️ **DECIDE picked it up anyway, ~17 minutes later, and that was a mistake.** It was read from a
stale `rimflow next` listing taken before the close, and its state was not re-checked first. The
sizing below is therefore **unrequested work on a deliberately closed item.**

✅ **It is kept only because it is a measured negative that is cheap to keep and expensive to
re-derive.** It creates NO work: the item stays `done`, it is not in any seat's actionable queue,
and 🔴 **nothing here is a reason to reopen it.** If the mask question ever returns, this note
saves someone the measurement — that is its whole value.

⛔ **The reassign to BUILD on this item is bookkeeping, not a handoff.** No work is owed by BUILD
and none was requested of him.

---

## 🔴 SIZED — the `gene:` route is DEAD. Measured by DECIDE, 2026-08-23.

This item asked the right question — *"Check `Inhabited.CharacterDef` accepts a gene at all
before touching the parser. If the C# has no genes field, this becomes a mod change too."*
**It has no genes field. Answered, not guessed.**

    Inhabited.dll #Strings heap, 585 names:   'genes'  ->  0 matches

⇒ ⛔ **Do not add a `gene:` line to `cast_to_xml.py`.** The parser would emit a field
`Inhabited` cannot read, and an unknown field in a def is ignored **silently** — the sheet
would look done and the two characters would still spawn bare-faced.

### How that was measured, because `strings` cannot do it
`CLAUDE.md` is explicit that `strings -a -el` is not a census — it found 16 of 115 names on the
companion DLL. The reason is that it scans UTF-16 while the `#Strings` heap is packed UTF-8
inside the metadata blob. So a reader was written for it:
`src/RimMandrake/Utils/clr_metadata_names.py` (⚠️ left for BUILD to keep, move or fold into
`measuring-large-artifacts` — tooling is not DECIDE's to own).

✅ **Validated before it was trusted**: every field the shipped XML provably uses — `traits`,
`skills`, `weapon`, `apparel`, `items`, `chassis` — is present in the heap, and so is the type
`CharacterDef`. An instrument that cannot find a known answer must not be trusted for an unknown
one.

### Two candidate routes that are NOT dead — and what is and is not proven about them
`hediffs`, `AddHediff`, `HediffDef`, `xenotype`, `XenotypeDef` and `CustomXenotype` all DO appear
in the heap.

🔑 **That is suggestive and it is NOT proof.** `#Strings` also holds names this assembly
REFERENCES in others, and `hediffs` and `xenotype` are both RimWorld's own member names. So they
may be `CharacterDef` fields, or they may be calls into `Pawn.health.hediffSet` / `Pawn.genes`.
**Someone must read the declaring type to tell.** What is settled is only the negative.

⭐ **If `hediffs` turns out to be a CharacterDef field, this item gets much cheaper**, because the
gene the spec wants exists only to apply `RimMandrake_GeneHediff_keldormask` — and the hediff
could then be applied directly. That would make it the small parser change this item hoped for
instead of a mod change.

⇒ **Reassigned to BUILD**: reading a third-party assembly's declaring type, and any parser or mod
change that follows, is implementation. The DESIGN is unchanged and already ruled — both
characters are defined by the mask and must visibly wear one.

---

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

---

# ⛔ CLOSED UNBUILT 2026-08-23 — owner: *"remove the DECIDE item before it gets picked up."*

Not done, and deliberately not left open for someone to pick up. **Nothing is broken by
closing it:** the dead `guy762_KelDorMask` reference is already gone at the prose source and
regenerated, so the red cross-reference error is closed and those two characters wear exactly
what they wore before — nothing. This item was only ever the *nicer* outcome.

What it would have cost: a `gene:` field in `cast_to_xml.py`, plus confirming
`Inhabited.CharacterDef` can consume one at all — unverified, and possibly a C# change.
Reopen it under a new name if Rah'da Onn and Kaad'ro Tenth-Breath ever need to actually
wear the mask their prose is built around.
