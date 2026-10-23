# Class prompt — items: CATCHES (fish and pool creatures as caught items)

Read `00_preamble.md` first. A catch is an ITEM: one picture (no facings) of the caught creature lying on the
ground or stacked, as the player hauls and cooks it. Some catch rows show a living-body facing set as a
reference; judge the item picture.

Look for:
1. **Is the caught species** (`CATCH_WRONG`, `PLACEHOLDER`): the item shows that creature (matching its living
   art, if shown) as an object — not generic vanilla meat, not a living swimming pose with facings, not another
   species.
2. **Reads as an item at 32 px/cell** (`LEGIB_32`): compact, clear silhouette, fills its single cell sensibly.
3. **No baked scenery** (`ALPHA_HALO`): no plate, net, water or table unless the description makes it the item.
4. **Matches the description's catch text** (`DESC_MISS`), and is painterly-realistic (`STYLE_CARTOON`).
5. Donor/vanilla icons standing in (`DONOR`) are not a final keep.

A catch whose living species is not settled yet may still be judged on the picture in front of you.
