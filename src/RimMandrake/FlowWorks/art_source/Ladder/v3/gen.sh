#!/bin/bash
# v3 redraw candidates for the rail ladder (RAIL_LADDER_REDRAW_CLIMB_NOT_CRAWL) and pit spikes
# (PIT_SPIKES_REDRAW_SPOKES_NOT_LOGS), owner walk 2026-10-21. One codex worker per candidate, all in parallel.
#   usage: gen.sh [which...]   (default: all)    raw output: Ladder/v3/raw, Spikes/v3/raw
set -u
R=/home/mandrake/rm/bench
FA=$R/src/RimMandrake/FlowWorks/art_source
CI="python3 $R/skills/generating-images/scripts/codex_image.py edit --model gpt-6.1-sol --timeout 560"
H=/mnt/c/Users/Mandrake/.codex_workers
LMAT=$FA/Ladder/raw/B_hung_north.png
SMAT=$R/src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Canals/RM_Spikes.png
OREF=$R/Transient/pile_2026-10-21/walk/spikes_reference_owner_2026-10-21.png
STYLE="RimWorld building sprite, hand-painted, warm 1970s earth-brown palette, matte painterly brushwork, soft painted edges, no outlines. Orthographic RimWorld building camera, about 35 degrees above horizontal, light from overhead and in front, no cast shadow on the ground. Fully transparent background with real alpha: no ground, no wall, no pit, no dirt drawn."
LADMAT="A crude scavenger ladder of weathered grey-brown timber poles, rungs lashed to the poles with tan rope, dark riveted iron bands at the joints and two forged black iron hooks at its top end: exactly the material, colours and brushwork of image 2."
SPKMAT="Each stake is a single slender pole of charred, weathered dark timber, whittled to a long needle-sharp fire-blackened point; the palette and painterly brushwork of image 2."

run() { # name outdir home prompt images...
  local name=$1 dir=$2 home=$3 prompt=$4; shift 4
  local args=(); for i in "$@"; do args+=(--image "$i"); done
  for try in 1 2; do
    $CI --codex-home $H/$home --out $dir/$name.png "${args[@]}" --prompt "$prompt" > $dir/$name.log 2>&1 && [ -s $dir/$name.png ] && { echo "OK $name"; return 0; }
    echo "$name try $try failed" >&2
  done
}

NORTH="Repaint image 1 as a ladder standing flat against the FAR wall of a dug pit, seen from above and in front, so the wall face and the ladder on it are strongly foreshortened: short and squat on screen, its rungs packed close together, every part pressed flat against the wall. The ladder rises straight up the wall from the pit floor at the bottom of the shape to the rim at the top, where its two iron hooks curl forward over the rim. Its two poles ride in a pair of fixed iron-faced timber guide rails bolted to the wall just outside them (the darker grey bars in image 1, held by flat iron brackets). $LADMAT $STYLE The ladder occupies the image exactly where the grey shape in image 1 does: same position, same size, same proportions, same number of rungs."
EAST="Repaint image 1 as a ladder seen from almost directly above, leaning in a dug pit: its top end hooks over the pit's EAST rim at the right of the image (the two dark iron hooks in image 1 grip the rim edge), and from there the ladder goes DOWN into the pit, its two long poles running leftward and slightly downward on screen to its foot standing on the pit floor near the middle of the image. The rungs are short bars running up-and-down on screen, parallel to the wall. The top end, near the rim, is brightly lit; the poles darken steadily toward the foot, which sinks into the pit's shadow, so it reads as going down and away. $LADMAT $STYLE The ladder occupies the image exactly where the grey shape in image 1 does: same position, same angle, same proportions, same number of rungs."
EASTB="Repaint image 1 as a ladder in a dug pit, seen from above: it leans against the pit's EAST wall, which is just off the right edge of the image. Its top end, with two black iron hooks, grips the rim at the right; its foot stands on the pit floor out toward the left. We look down along it, so the poles run left-right across the image and the rungs are short up-down bars between them. Strong depth: the top end is lit, warm and crisp; down toward the foot the timber goes into cool deep shadow. $LADMAT $STYLE Same position, angle and proportions as the grey shape in image 1."

SPK="Repaint image 1 as a bed of many thin sharpened wooden stakes planted upright in the floor of a pit, seen from above and in front: every grey spike in image 1 becomes one slender stake, the same position, height and lean, its sharp point at the top and its base driven into the ground at the bottom; a tiny dark socket of disturbed earth at each base. Thin spokes with lots of empty space between them, like the stake field at the bottom of the pit in image 3 - never logs, never a mound, never a solid mass. $SPKMAT $STYLE"
SPKC="Repaint image 1 as a dense field of thin sharpened stakes planted upright in a pit floor, seen from above and in front: every grey spike in image 1 becomes one slender stake, same position, height and lean, point up. Mix of charred timber stakes and a few rusty iron spear-heads lashed onto thin poles with tan rope - scavenger work. Thin and spiky with clear empty space between them, like the stakes at the bottom of the pit in image 3 - never logs, never a mound. $SPKMAT $STYLE"
SPKD="Paint a square RimWorld sprite of a pit-floor spike trap seen from above and in front: about forty thin, needle-sharp wooden stakes planted upright, spread evenly over the whole square, each a slender pole tapering to a sharp blackened point, leaning very slightly at random, with empty space between them - exactly the kind of stake field at the bottom of the pit in image 2, but painted. Charred dark timber, the palette and brushwork of image 1. Every stake stands fully inside the square, the bases spread from near the bottom edge up to about a fifth from the top. $STYLE"

L=$FA/Ladder/v3/raw; S=$FA/Spikes/v3/raw; G=$FA/Ladder/v3/guides; SG=$FA/Spikes/v3/guides
want() { [ $# -eq 0 ] && return 0; return 1; }
ALL=("$@")
sel() { [ ${#ALL[@]} -eq 0 ] && return 0; for a in "${ALL[@]}"; do [ "$a" = "$1" ] && return 0; done; return 1; }
sel lnA && run north_A $L bench_lad1 "$NORTH" $G/guide_north.png $LMAT &
sel lnB && run north_B $L bench_lad2 "$NORTH Keep it very flat and tight to the wall." $G/guide_north.png $LMAT &
sel leA && run east_A $L bench_lad3 "$EAST" $G/guide_east.png $LMAT &
sel leB && run east_B $L bench_lad4 "$EASTB" $G/guide_east.png $LMAT &
sel leC && run east_C $L bench_lad5 "$EAST The rope lashings and hooks are crisp and readable." $G/guide_east.png $LMAT &
sel sA && run spikes_A $S bench_spk1 "$SPK" $SG/guide_stakes_6.png $SMAT $OREF &
sel sB && run spikes_B $S bench_spk2 "$SPK" $SG/guide_stakes_8.png $SMAT $OREF &
sel sC && run spikes_C $S bench_spk3 "$SPKC" $SG/guide_stakes_8.png $SMAT $OREF &
sel sD && run spikes_D $S bench_spk4 "$SPKD" $SMAT $OREF &
wait
ls -la $L/*.png $S/*.png 2>/dev/null
