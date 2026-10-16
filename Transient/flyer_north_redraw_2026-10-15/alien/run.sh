#!/bin/bash
# one alien fleet flier set: S from refs, then E and N from that S
cd /home/mandrake/rm/bench; O=Transient/flyer_north_redraw_2026-10-15/alien; F=src/RimMandrake/TheForge/Textures/Things/Pawn/Animal/RM_FleetFlier
IFS='|' read -r K COL FACE <<< "$(grep "^$1|" $O/sets.txt)"
CI=/home/mandrake/rm/bench/.claude/skills/generating-images/scripts/codex_image.py
BASE="The fleet flier is a small alien flying creature from another world that darts into volcanic vapor columns to graze on fireweed. It is NOT a bird: it has very long, narrow, elegant wings, each wing about twice the length of its body, $COL; $FACE. It has a slim body and a long thin tail. Pose at rest: it stands on two thin legs with both long wings held half-open and drooping at its sides so the full length of each wing reads clearly. Same flat painterly RimWorld cartoon style, bold dark outline and line weight as the reference images. Square 1024x1024 canvas, fully transparent background, the whole creature and both wingtips INSIDE the canvas with a clear empty margin on every side, no shadow."
P="Image 1 and image 2 are an earlier version of this creature, for style and line weight only; redesign it as described. Draw it SOUTH facing: front view, the RimWorld top-down three-quarter camera, the face toward the viewer. $BASE"
mkdir -p /mnt/d/Luke/dev/_rmscratch/ch_al${K}S /mnt/d/Luke/dev/_rmscratch/ch_al${K}E /mnt/d/Luke/dev/_rmscratch/ch_al${K}N
echo "$P" > $O/prompt_${K}_south.txt
python3 $CI edit --model gpt-6.1-sol --image $F/RM_FleetFlier_south.png --image Transient/flyer_north_redraw_2026-10-15/fleet/RM_FleetFlier_north_A.png --prompt "$P" --out $O/raw_${K}_south.png --codex-home /mnt/d/Luke/dev/_rmscratch/ch_al${K}S > $O/log_${K}_south.txt 2>&1 || exit 1
INV="Image 1 is this exact creature seen from the FRONT (south facing). Keep it the same individual: same colours and markings, same face, same wing length and shape, same size on the canvas, same style and outline. $BASE"
PE="Draw it from the SIDE, facing RIGHT (east facing): head and face pointing right, the near wing half-open showing its full length, tail trailing left. $INV"
PN="Draw it from BEHIND (north facing), the RimWorld top-down three-quarter camera looking at its back: the back of the head, the back, both long wings half-open and drooping at its sides showing their upper surfaces and full length, the tail toward the bottom. $INV"
echo "$PE" > $O/prompt_${K}_east.txt; echo "$PN" > $O/prompt_${K}_north.txt
python3 $CI edit --model gpt-6.1-sol --image $O/raw_${K}_south.png --prompt "$PE" --out $O/raw_${K}_east.png --codex-home /mnt/d/Luke/dev/_rmscratch/ch_al${K}E > $O/log_${K}_east.txt 2>&1 &
python3 $CI edit --model gpt-6.1-sol --image $O/raw_${K}_south.png --prompt "$PN" --out $O/raw_${K}_north.png --codex-home /mnt/d/Luke/dev/_rmscratch/ch_al${K}N > $O/log_${K}_north.txt 2>&1 &
wait
