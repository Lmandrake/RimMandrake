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

## root cause and fix — 2026-09-20, `40d376501`

**The absorption copied the inventory ICON and nothing else.**

`guy762_Robes_jawa` lives in our own `Armoury`, absorbed from workshop 3254370945
(`guy762.MM.KotORCore`) by `src/RimStarWars/Armoury/Source/gen_kotorcore_absorption.py`.
Its `wornGraphicPath` is `SWApparel/Robes/jawa/Apparel`.

🔑 **What renders is not that path.** MEASURED against the decompiled engine
(`ApparelGraphicRecordGetter.TryGetGraphicApparel`): for anything whose `LastLayer` is
not `Overhead`/`EyeCover` and that is not a pack, the path handed to `Graphic_Multi` is
**`<wornGraphicPath>_<BodyTypeDef>`** — so the files that matter are
`Apparel_Male_south.png` … `Apparel_Hulk_north.png`, fifteen of them.

`find_and_copy_texture()`'s suffix ladder was **bare + `_south`/`_north`/`_east`/`_west`
only**. `Apparel.png` (the icon) existed, so `copied_any` went true, the generator
logged the texture as FOUND, and all fifteen worn graphics were left behind with no
warning. Second defect in the same function: **`wornGraphicPath` was never collected as
a texture root at all** — only `texPath`/`iconPath`/`uiIconPath` — so a garment whose
worn art sits apart from its icon got no art copied whatsoever.

Nothing else supplied the missing files, because **both donor packs are inactive** in
`ModsConfig` (`guy762.MM.KotORCore`, `guy762.KotORWeapons` — parsed, not grepped).

⚠️ **It was never only the robe.** MEASURED: **123 absorbed apparel defs** were missing
worn graphics — every KotOR undersuit, jacket, bodysuit, accessory, jedi/sith tunic and
armour in the Armoury, 1,560 PNGs in total.

**Fixed:** the 1,560 files copied from the workshop sources into
`src/RimStarWars/Armoury/Textures/` and deployed; the body-type rung and
`wornGraphicPath` collection added to all six absorption generators
(`gen_kotorcore` / `gen_kotorweapons` / `gen_jds_armory` / `gen_sovsith` /
`gen_theforcelightsaber_kyber` / `gen_additionalmods`). `selftest_absorption_generators.py`
4/4.

## live-verified — 2026-09-20 21:26

Cold load of the full 618-mod list, `CANONICAL_ASHKARR_START_2026-09-12` loaded through
the bridge, camera on the founders, `jawa/clear_ui`, screenshot:
`Transient/founders_roundtrip/founders_robe_FIXED_2026-09-20.png`.

All six founders render their real jawa robes — south-facing and north-facing both in
frame, zero magenta pixels sampled, and **0 `SWApparel` lines in `Player.log`**. Nothing
was saved; every keeper save is untouched.

🔑 East/west are covered by the files, not by the log: `Graphic_Multi.Init` logs *only*
when all four rotations **and** the bare path are missing, and degrades silently
otherwise — so a clean log alone would not have proved it. All 15
`_{Male,Female,Thin,Fat,Hulk}_{south,east,north}` files are present and non-magenta at
the deployed path; `_west` is absent in the donor too and mirrors east
(`westFlipped`), which is how the mod always shipped.
