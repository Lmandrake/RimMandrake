# FOUNDER_ROBE_MAGENTA_1 — the founders' robes render as flat magenta

## what is wrong

Observed 2026-09-21 during `FOUNDERS_EXPORT_TO_REPO_1`'s round-trip verification: the
founders' **robe layer renders as a flat magenta block**.

🔴 **Magenta is what RimWorld draws for a failed texture lookup.** This is the classic
signature of a `texPath` that does not resolve.

## 🔑 it is NOT a round-trip artefact

It renders identically **in the canonical world** — the source these pawns were exported
from — not only in the spliced throwaway save. The two were compared directly. So the
defect is in the shipped apparel, and it has been there all along; the round trip merely
put eyes on it.

Suspect def: `guy762_Robes_jawa`.

Pictures: `D:\Luke\dev\Rimworld\Transient\founders_roundtrip\`

## why it matters

These are the **founders** — six hand-made colonists, one of the three artifacts ruled to
survive the world remake. They are the first pawns a player sees.

## spec

Find what `guy762_Robes_jawa` (and any sibling robe def on these pawns) sets as its
`texPath`, and whether a texture exists at that path in the mod that ships it.

⚠️ **A texture binds by `texPath`, not by defName** — a byte-identical deploy can still
render nothing if the path is wrong. Check the *deployed* copy under
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\`, not just the repo: writing
a file is not deploying it.

⚠️ Apparel art is per-layer and per-body-type; confirm which facing/body-type combinations
fail before concluding the whole def is broken.

## verify

The robe renders with its real art on all four facings, in game, on a founder.

## criteria

No founder renders a magenta block.
