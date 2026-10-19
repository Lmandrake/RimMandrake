#!/bin/bash
# One rails candidate per worker (image 1 = grey guide, image 2 = the ladder master whose material the rails match).
# usage: gen.sh <tag> <codexhome>      (codexhome under /mnt/<drive>/, one per concurrent worker)
set -u
tag=$1; home=$2
R=/home/mandrake/rm/bench
cd "$(dirname "$0")"
mkdir -p raw
CI="python3 $R/skills/generating-images/scripts/codex_image.py edit --model gpt-6.1-sol --codex-home $home --timeout 600"
LAD=../raw/B_hung_north.png
P="Repaint image 1 as a pair of fixed guide rails for a sliding ladder, fastened flat against an earthen pit wall, seen face-on from the front. Each rail is a long straight vertical timber beam faced with a dark iron U-channel down its middle (the groove a ladder pole slides in), held to the wall by four flat iron bracket plates with big round bolt heads, and ending at the bottom in a chunky iron stop block. Crude scavenger work: weathered grey-brown timber, dark riveted iron, exactly the material, colours and painterly brushwork of the ladder in image 2. RimWorld building sprite, hand-painted, warm 1970s earth-brown palette, orthographic, light from overhead and in front, no cast shadow, no ground, no wall drawn and NO ladder drawn: only the two rails and their brackets. Fully transparent background with real alpha. The rails occupy the image exactly where the grey shapes in image 1 do: same positions, same lengths, same widths, same bracket heights."
for try in 1 2; do
  $CI --out raw/${tag}_rails_front.png --image guides/guide_rails_front.png --image $LAD --prompt "$P" > raw/${tag}_rails_front.log 2>&1 && [ -s raw/${tag}_rails_front.png ] && break
  echo "$tag try $try failed" >&2
done
echo "$tag done"; ls raw/${tag}_*.png
