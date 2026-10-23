#!/bin/bash
# One look's bank-stake and silt-trap pieces through codex $imagegen (edit: image 1 = guide, image 2 = the look's tank for
# materials). RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS fixes 8 and 10. Usage: generate.sh <Look> [piece ...]  -> raw/<Look>_<piece>.png
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; REPO="$(cd "$HERE/../../../../.." && pwd)"
LOOK="$1"; shift; TANK="$REPO/src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Tank/$LOOK/RM_LiquidTank.png"
CI="$REPO/skills/generating-images/scripts/codex_image.py"; mkdir -p "$HERE/raw"
RMS="$(python3 "$REPO/src/RimMandrake/Utils/rmpaths.py" scratch)" || exit 2
case "$LOOK" in
 Scrapper) MAT="weathered grey-brown salvaged timber, mismatched planks, patched with rusty riveted scrap-metal plates, frayed rope lashings - the same rust, worn steel and old wood as image 2";;
 Industrial) MAT="heavy dark-stained timber held by dark gunmetal steel straps and channel with hex bolts, yellow-and-black hazard stripes on one band - the same gunmetal and hazard yellow as image 2";;
 Modern) MAT="clean sawn honey-brown treated timber with glossy red-painted steel caps and brackets and polished chrome bolts - the same glossy red and chrome as image 2";;
 Futuristic) MAT="smooth white composite panels with pale grey seams, rounded white brackets and a thin glowing cyan light strip - the same white and cyan as image 2";;
esac
COMMON="RimWorld building sprite, river bank works, look: $LOOK. Image 1 is a grey geometry guide: keep its silhouette, placement, proportions and camera exactly (orthographic, about 35 degrees above horizontal, top faces lit and fully visible, light from overhead-front). Replace the grey blockout with finished painted game art. Materials and palette: $MAT. Image 2 is only the material and colour reference; draw no tank. The background is fully transparent (real alpha). Draw no cast shadow and no grass. Clean readable shapes that survive shrinking to 128 pixels per cell; the outline is crisp."
prompt_for() {
 case "$1" in
  ridge_h) echo "Subject: a LOW EARTH LEVEE RIDGE running left to right across the whole canvas and continuing off both side edges (a repeating section of a longer bank; both ends cut flush at the canvas edges, no end posts). Packed brown earth with a lit flat crest, its face toward the camera retained by a low crib of boards in the look's material, two crib uprights, a darker damp band along the foot. Earth stays earth-brown in every look.";;
  ridge_v) echo "Subject: a LOW EARTH LEVEE RIDGE seen from above running from the top edge to the bottom edge of the canvas and continuing off both (a repeating section; ends cut flush, no end posts): packed brown earth with a lit flat crest down the middle, the right flank retained by crib boards in the look's material, two crib uprights set in the crest. Earth stays earth-brown in every look.";;
  post) echo "Subject: one lamp-topped bank stake standing alone in the centre: a stout post in the look's material driven into a small mound of packed brown earth, a lashing band, and a small lantern on top with a warm glowing pane. Only this one post and its footing; nothing else.";;
  baffle) echo "Subject: a SILT-TRAP BAFFLE: a short sturdy wall of boards in the look's material set between three posts, standing in the shallow edge of a river: its lower band is dark and visibly wet with a thin bright waterline, and a faint ring of small ripples where the posts meet the water. Draw no ground and no water body other than that waterline ring.";;
 esac
}
run() {
  [ -s "$HERE/raw/${LOOK}_$1.png" ] && { echo "$LOOK $1 cached"; return 0; }
  python3 "$CI" edit --model gpt-6.1-sol --out "$HERE/raw/${LOOK}_$1.png" --image "$HERE/guides/guide_$1.png" --image "$TANK" \
    --codex-home "$RMS/codex/home_riverworks_$LOOK" --timeout 480 --prompt "$COMMON $(prompt_for "$1")" > "$HERE/raw/${LOOK}_$1.log" 2>&1
  echo "$LOOK $1 exit=$?"
}
PIECES="${*:-post ridge_h ridge_v baffle}"
for p in $PIECES; do run "$p"; done
