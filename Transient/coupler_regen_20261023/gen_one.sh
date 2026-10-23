#!/bin/bash
# gen_one.sh <Look> <UnderCollar|UnderPipe> <tag> : one foreground Codex $imagegen edit, fixture texture as style reference
set -e
R=/home/mandrake/rm/bench; D=$R/Transient/coupler_regen_20261023
L=$1; K=$2; TAG=${3:-a}
P=$(python3 -c "import json,re,sys; p=json.load(open('$D/prompts.json'))['$L/$K']; print(re.sub(r'Image #\d+','Image 2',p))")
[ "$K" = UnderPipe ] && EXTRA="Paint it with the image generation tool as a painted texture with visible aged-metal character, not a computed gradient. " || EXTRA=""
P="${EXTRA}Image 1 is the exact shape, proportions, framing and canvas: keep its silhouette filling the canvas exactly as it does. Image 2 is ONLY a material, palette and brushwork reference (draw the fitting, not the tank). $P"
cd $R
timeout 300 python3 .claude/skills/generating-images/scripts/codex_image.py edit --timeout 280 \
  --image $D/guides/${K}_guide.png --image $R/src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Tank/$L/RM_UniversalCargoTank.png \
  --prompt "$P" --out $D/raw/${L}_${K}_${TAG}.png 2>&1 | tail -3
