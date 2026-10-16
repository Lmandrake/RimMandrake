#!/bin/bash
# One candidate per worker; hung_north is the master, every other look carries it as image 3 and in words.
# usage: gen.sh <tag> <codexhome>      (codexhome under /mnt/<drive>/, one per concurrent worker)
set -u
tag=$1; home=$2
R=/home/mandrake/rm/bench
cd "$(dirname "$0")"
CI="python3 $R/skills/generating-images/scripts/codex_image.py edit --model gpt-6.1-sol --codex-home $home --timeout 900"
LAD=$R/src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Canals/RM_Ladder.png
RAI=$R/src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Canals/RM_LadderRaised.png
MAT="A crude scavenger ladder of weathered grey-brown timber poles, rungs lashed to the rails with tan rope, dark riveted iron bands at the joints, exactly the material, colours and painterly brushwork of image 2. Two heavy black wrought-iron hooks are forged onto the top ends of the rails."
COMMON="RimWorld building sprite, hand-painted, warm 1970s earth-brown palette. Orthographic RimWorld building camera, light from overhead and in front, no cast shadow, no outline, no ground, no wall, no pit drawn: only the ladder. Fully transparent background with real alpha. The ladder occupies the image exactly where the grey shape in image 1 does: same position, same silhouette, same proportions, same number of rungs."
SIB="It is the same ladder as image 3: match image 3's timber, rope, iron, colours and brushwork exactly."
run() { # name, prompt, images...
  local name=$1 prompt=$2; shift 2
  local args=(); for i in "$@"; do args+=(--image "$i"); done
  for try in 1 2; do
    $CI --out raw/${tag}_${name}.png "${args[@]}" --prompt "$prompt" > raw/${tag}_${name}.log 2>&1 && [ -s raw/${tag}_${name}.png ] && return 0
    echo "$tag $name try $try failed" >&2
  done
}
run hung_north "Repaint image 1 as a ladder hung on the far wall of a dug pit, seen from above and in front. The ladder stands upright against the wall, rails vertical, rungs face-on to the viewer and evenly spaced; its two iron hooks at the top edge of the image curl forward over the pit's rim, gripping it; the feet of the rails rest on the pit floor at the bottom of the shape. It reads as installed, hanging straight and square, ready to climb. $MAT $COMMON" guides/guide_hung_north.png $LAD
M=raw/${tag}_hung_north.png
run hung_south "Repaint image 1 as the top end of a ladder hung on the NEAR wall of a dug pit, seen from above and in front: the ladder descends down into the pit away from the viewer, hidden behind the pit's near rim. Only the two iron hooks at the bottom edge of the image, gripping the rim, and the top two or three rungs show; upward in the image the rails and rungs sink into deep shadow and fade out completely to transparency, as if going down into darkness behind the rim. $SIB $MAT $COMMON" guides/guide_hung_south.png $LAD $M
run hung_east "Repaint image 1 as a ladder hung on the east (right) wall of a dug pit, seen edge-on in side profile: narrow, its two rails nearly overlapping, the near rail lit and the far rail slightly darker just behind it, the rungs shown as short foreshortened stubs between them. It leans against the right edge of the image with its foot lower-left and its top at the upper right, where one iron hook curls over the right edge of the image, gripping the rim. $SIB $MAT $COMMON" guides/guide_hung_east.png $LAD $M
run stowed_north "Repaint image 1 as the same ladder pulled up out of the pit and laid flat on the ground, lying horizontally, seen from above like image 2. Its iron-hooked top end is at the right, the hooks bent downward; a short neat coil of tan rope tied to the middle of the lower rail lies just below it. It reads as stowed and ready to be lowered. $SIB $MAT $COMMON" guides/guide_stowed_north.png $RAI $M
S=raw/${tag}_stowed_north.png
run stowed_south "Repaint image 1 as the same ladder pulled up out of the pit and laid flat on the ground, lying horizontally, seen from above: identical to image 3 but with the iron hooks at the right end bent UPWARD and the short coil of tan rope lying just ABOVE the upper rail. $SIB $MAT $COMMON" guides/guide_stowed_south.png $RAI $S
run stowed_east "Repaint image 1 as the same ladder pulled up out of the pit and laid flat on the ground, lying VERTICALLY (top to bottom), seen from above: image 3 turned upright, with its iron-hooked end at the bottom, the hooks bent toward the LEFT, and the short coil of tan rope lying just to the LEFT of the left rail. Light still comes from overhead and in front. $SIB $MAT $COMMON" guides/guide_stowed_east.png $RAI $S
echo "$tag done"; ls raw/${tag}_*.png
