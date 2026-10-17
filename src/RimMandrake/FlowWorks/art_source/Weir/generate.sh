#!/bin/bash
# One look's four weir pieces through codex $imagegen (edit: image 1 = guide, image 2 = the look's tank for materials).
# Usage: generate.sh <Look>   (run from anywhere; writes raw/<Look>_<piece>.png)
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; REPO="$(cd "$HERE/../../../../.." && pwd)"
LOOK="$1"; TANK="$REPO/src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Tank/$LOOK/RM_LiquidTank.png"
CI="$REPO/skills/generating-images/scripts/codex_image.py"; mkdir -p "$HERE/raw"
case "$LOOK" in
 Scrapper) MAT="weathered grey-brown salvaged timber planks, mismatched widths, patched here and there with rusty riveted scrap-metal plates, frayed rope lashings - the same rust, worn steel and old wood as image 2";;
 Industrial) MAT="heavy dark-stained timber planks held by dark gunmetal steel straps and channel with hex bolts, yellow-and-black hazard stripes painted on the crest beam at intervals - the same gunmetal and hazard yellow as image 2";;
 Modern) MAT="clean sawn honey-brown treated timber planks capped by a glossy red-painted steel crest rail with polished chrome bolts and brackets - the same glossy red and chrome as image 2";;
 Futuristic) MAT="smooth white composite planks with pale grey seams, rounded white brackets and a thin glowing cyan light strip along the crest - the same white and cyan as image 2";;
esac
COMMON="RimWorld building sprite for a river weir, look: $LOOK. Image 1 is a grey geometry guide: keep its silhouette, placement, proportions and camera exactly (orthographic, about 35 degrees above horizontal, top faces lit and fully visible, light from overhead-front). Replace the grey blockout with finished painted game art. Materials and palette: $MAT. Image 2 is only the material and colour reference; draw no tank. The background is fully transparent (real alpha). Draw no water, no ground, no grass and no cast shadow: the game draws the river beneath. Clean readable shapes that survive shrinking to 128 pixels per cell; the outline is crisp."
run() { # piece guide prompt
  [ -s "$HERE/raw/${LOOK}_$1.png" ] && return 0
  python3 "$CI" edit --model gpt-6.1-sol --out "$HERE/raw/${LOOK}_$1.png" --image "$HERE/guides/$2" --image "$TANK" \
    --codex-home "/mnt/d/Luke/dev/_rmscratch/codex/home_weir_$LOOK" --timeout 900 --prompt "$COMMON $3" > "$HERE/raw/${LOOK}_$1.log" 2>&1
  echo "$LOOK $1 exit=$?"
}
run h_spill guide_h_spill.png "Subject: a LOW TIMBER WEIR wall section running left to right across the whole canvas and continuing off both side edges (a repeating section of a longer wall; both ends cut flush at the canvas edges, no end posts). The level crest beam's lit top face runs straight; below it the downstream spill face of boards slopes toward the camera to a toe sill, with four squat support posts at the toe."
run h_upstream guide_h_upstream.png "Subject: a LOW TIMBER WEIR wall section running left to right across the whole canvas and continuing off both side edges (a repeating section; ends cut flush at the canvas edges, no end posts), seen from its UPSTREAM side: a level crest beam with a lit top face, below it a flat face of vertical boards whose lower band is dark and wet, with four pile heads set into the crest."
run v_east guide_v_east.png "Subject: a LOW TIMBER WEIR wall section running from the top edge to the bottom edge of the canvas and continuing off both (a repeating section; ends cut flush, no end posts), seen from above: a narrow shaded upstream edge on the left, the lit level crest beam, and the downstream spill face of boards sloping down to the RIGHT to a toe sill with four squat support posts."
run cap guide_cap.png "Subject: one stout weir end post: a single thick pile post with a lit top face (an ellipse) and a lashing band, standing alone in the centre."
