#!/usr/bin/env bash
# TANK_TALL_BUILD_TWICE_THE_DRINK v3: restyle one shape master into one of the four GSS looks (Scrapper, Industrial,
# Modern, Futuristic). image 1 = the master (camera + shape held), image 2 = the look's GSS/FlowWorks reference sheet.
# usage: restyle.sh <master.png> <Look> <out.png> <worker n>
set -u
V=src/RimMandrake/FlowWorks/art_source/TankTall/v2
M=$1; L=$2; O=$3; N=$4
case $L in
  Scrapper)   D="salvaged and patched: rust-brown and copper-toned metal, riveted patch plates, scavenged wood, rope and wire lashings, bronze fittings";;
  Industrial) D="dark gunmetal and blackened iron, heavy bolted flanges, yellow-and-black hazard stripe bands, worn but maintained, dark iron fittings";;
  Modern)     D="glossy fire-engine red paint with polished chrome fittings and light grey accents, clean and new";;
  Futuristic) D="white and light-silver composite panels with dark grey trim and glowing cyan light strips along the seams, sleek and clean";;
esac
export CODEX_MODEL=gpt-6.1-sol
exec python3 skills/generating-images/scripts/codex_image.py edit --codex-home /mnt/d/Luke/dev/_rmscratch/codexhome_tank$N \
  --image "$M" --image "$V/look_$L.png" --out "$O" --prompt "Restyle image 1 into the $L look shown in image 2: $D. \
The silhouette, canvas size, camera angle, proportions and the position of the tank on the canvas all stay exactly as in image 1: \
the same tank, the same top ellipse, the same hatch, fittings, valves, gauge and base in the same places, only their materials \
and colours change to match image 2's $L look. Light from overhead and slightly in front. Fully transparent background, real alpha."
