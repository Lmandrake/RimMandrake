# src/Jawa/art_bench/smelter — the survivors, and why only these

Pruned 2026-08-12 by a retired seat, at the owner's request: **89 files → 4, 143 MB →
2.1 MB.** Everything deleted was untracked scratch from the generation pipeline.

Nothing was lost. Before deleting, all 89 files were SHA-256'd against every
committed copy of the mod's art; the 12 shipped facings were confirmed
byte-identical to
`src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Factories/AutomatedSmelter/`,
which is where they actually live now.

## What is here

⚠️ **This table is a snapshot; the filesystem is the authority.** It was correct
when written and will not update itself. To see what is actually here and which
of it is a deliberate keep rather than fresh scratch:

```bash
ls src/Jawa/art_bench/smelter/
git ls-files src/Jawa/art_bench/smelter/     # the tracked keeps — anything else is scratch
```

| file | why it survives |
|---|---|
| `variant_flat.png` | rejected style candidate |
| `variant_painterly.png` | rejected style candidate |
| `variant_rendered.png` | **the chosen one** — became the wrecked south anchor, and through it the house style for the whole ladder |
| `_alltiers.png` | the ladder in one image: donor / wrecked / kludged / repaired × 4 facings |

The three `variant_*.png` are **tracked in git** and `DESIGN.md` §1b points at
this directory for them by name. Do not delete them; the style ruling is only
re-openable if the losing candidates still exist.

`_alltiers.png` is the single artifact that answers "do the three tiers read as
the same machine?" — checklist item 2 in the `NEXT_RELOAD.md` handoff.

## What was thrown away

27 `*_raw.png` (generator output before cropping), 25 `*_cut.png` (chroma-key
intermediates), 11 other contact sheets, 12 duplicates of the shipped finals,
and 10 superseded finals — the v1 kludged and repaired passes, the v1 wreck
north, and the earliest pilot south.

## Keep it this way

This directory is a **workshop bench, not an archive.** The pipeline writes
`_raw` → `_cut` → final for every generation, so it refills fast and it refilled
to 143 MB in about ninety minutes of work. Sweep it when a machine is finished:
the finals belong in the mod's `Textures/`, the intermediates belong nowhere,
and contact sheets are regenerable from the finals with
`Source/sheet.py` / `contact_sheet.py` for as long as the finals exist.

⚠️ Only `variant_*.png` are tracked. Everything else here is one `rm` from gone
with no way back — hash against the committed tree before deleting, the way this
sweep did.
