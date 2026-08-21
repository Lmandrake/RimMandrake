# MAGENTA_CONTACT_SHEET_1 — show him the magenta before anyone fixes it

## spec

🔴 **OWNER, 2026-08-21: "I want to see the magenta with my own eyes before we fix it, I
don't trust it."** ⇒ **This item produces a PICTURE, not a fix.** Nobody touches a texPath
until he has looked and said go.

⛔ **`d-chk2-magenta-heads-fixed-by-path-and-texture-not-by-regenerate-7b3e01` does not
start until this closes.** The doubt is the point: the claim has been asserted twice, from
two directions, and never rendered.

**The claim to be tested,** as BUILD measured it 2026-08-19 — four families, ~25 lines:

| | path |
|---|---|
| female Chagrian | `OuterRim/Genes/Headbone/ChagrianF` |
| Gand | `Pawn/HeadAttachments/gand/mask_*` |
| Selkath | `Pawn/HeadAttachments/selkath/fishyjowls_female` |
| yellow eyes | `Pawn/HeadAttachments/yelloweyes/YellowEyes_Female` |
| gene icons | 16 × `OuterRim/GeneIcons/*BG` |

**Deliver a contact sheet** of every affected texPath, each cell showing what the game
would actually draw, labelled with the def and the path. Put the DONOR mod's version of
the same texture beside it, because the standing claim is that *the donors still hold
every texture and nothing is lost — only unmigrated*. If that is true the sheet proves it
in one look; if it is false, that is the finding.

🔑 **A magenta square is RimWorld's missing-texture placeholder, so its ABSENCE is not
proof of health.** `reading-rimworld-graphics` records the blind spot: a `Graphic_Multi`
with a bare path falls back rather than going magenta, so a broken path can render as the
wrong art instead of an obvious error. **Report per path: magenta · wrong art · correct
art · could not determine.** Four buckets, not two.

⚠️ **And check the claim that D-CHK2's own offline test is wrong** — it says no path may
begin `UI/` without the `RimMandrakeSW/` prefix, but `UI/Icons/Xenotypes/Baseliner`,
`UI/Icons/Genes/Gene_Furskin` and a dozen more are **vanilla paths that must stay**. If
that test is what generated this list, some of these four may not be broken at all, which
would vindicate the owner's doubt directly.

**Offline. No game load.** The textures are files; `reading-rimworld-graphics` covers
loose PNGs, AssetBundles and `resources.assets`.

## verify

- One image or HTML sheet, its full native path reported to the owner.
- Every path in the list above appears in it, with a donor comparison where one exists.
- Each is bucketed magenta / wrong art / correct art / undetermined, with a count.
- The D-CHK2 `UI/` rule is re-run and its vanilla-path false positives are counted.

## criteria

The owner looks once and says fix or drop — and if the list turns out to be partly wrong,
that is a successful outcome of this item, not a failure of it.
