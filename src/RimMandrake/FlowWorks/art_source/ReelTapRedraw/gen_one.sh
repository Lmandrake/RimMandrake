#!/usr/bin/env bash
# REEL_TAP_CAMERA_REDRAW_STILL_SIDE_ON: one candidate. image 1 = the grey camera guide (reel_guide.py), image 2 = the
# look's installed art (material, palette, detail: the owner's kept style, judge brief B3).
# usage: gen_one.sh <Look|Tap> <stored|laid|-> <west|north|south|-> <outdir> <worker n>
set -u
cd /home/mandrake/rm/bench || exit 2
L=$1; ST=$2; F=$3; O=$4; W=$5
RMS="$(python3 src/RimMandrake/Utils/rmpaths.py scratch)" || exit 2
HT=src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose
G=$O/guides
case $L in
  Scrapper)   D="salvaged and patched: rust-brown riveted iron frame and flanges, tan stitched sack-cloth hose, brass fittings and coupling"; P="";;
  Industrial) D="dark gunmetal and blackened iron, black rubber hose, yellow-and-black hazard stripe bands on the flanges, steel fittings"; P="Styles/Industrial/";;
  Modern)     D="glossy fire-engine red paint, red hose, polished chrome valve and fittings, clean and new"; P="Styles/Modern/";;
  Futuristic) D="white and light-silver composite with dark grey trim, white hose with cyan stripes, glowing cyan light strips, sleek"; P="Styles/Futuristic/";;
esac
COMMON="Light from overhead and slightly in front; every top face is the brightest surface. Painterly RimWorld building sprite, clean edges, readable at small size. Fully transparent background, real alpha, no ground, no shadow, no scenery."
if [ "$L" = Tap ]; then
  REF=src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Machinery/RM_LiquidTap.png
  GU=$G/g_tap.png; OUT=$O/raw/RM_LiquidTap.png
  PR="Image 1 is a grey blockout that fixes the exact camera (orthographic, looking down from the front at 35 degrees), the shapes, proportions and position on the canvas. Image 2 is the existing bleed well: copy its materials exactly - rusty corroded iron pipe, riveted iron bands, a rust-red iron handwheel, brass ring fittings. Paint image 1 as that bleed well: a vertical iron pipe driven into the ground with a small round iron collar where it enters the ground, a riveted band halfway up, a valve body on top, and an iron handwheel lying FLAT on top of the valve stem, seen from above as a wide ellipse with its spokes in that ellipse. A short side outlet pipe runs horizontally to the right and turns straight DOWN into a spout; the spout opening points at the ground, so no pipe opening is visible anywhere. Keep every part exactly where image 1 puts it. $COMMON"
else
  ART=Reel_PumpHookup; [ "$ST" = laid ] && ART=Reel_Deployed
  B=frame; [ "$L" = Modern ] && B=pedestal
  REF=$HT/$P$ART.png
  GU=$G/g_${B}_${ST}_${F}.png; OUT=$O/raw/${L}_${ART}_${F}.png
  if [ "$ST" = stored ]; then SD="the drum is wound full of hose (the hose turns are the light ringed cylinder between the flanges)"; else SD="the hose is laid out: the drum is nearly empty, a bare core with only a few turns of hose left on it"; fi
  case $F in
    west)  FD="The reel's axle runs left-right. The flanges are thin discs seen edge-on, so each flange is a tall narrow plate. The outlet is a pipe from the left hub that bends down to the ground and runs LEFT along the ground to a coupling at the lower left; that coupling points left, seen from the side as a short cylinder - its opening faces left and is not visible. The crank (or valve) is on the right hub.";;
    north) FD="The reel's axle runs straight away from the viewer. We look at the near flange as a round disc (an ellipse slightly flatter than a circle) with the crank (or valve) on its hub facing us; the far flange's top rim and the top of the drum show above it. The outlet is on the far side, hidden behind the reel - nothing points up at the viewer and no pipe opening is visible.";;
    south) FD="The reel's axle runs toward the viewer. We look at the near flange as a round disc (an ellipse slightly flatter than a circle); the far flange's top rim and the top of the drum show above it. The outlet pipe comes from the near hub, bends down to the ground and runs straight TOWARD the viewer to a coupling at the very bottom: that coupling points at the camera, so its round opening shows as a slightly flattened ellipse - the only pipe opening visible. Things on the far side only peek over the top.";;
  esac
  PR="Image 1 is a grey blockout that fixes the exact camera (orthographic, looking down from the front at 35 degrees), the shapes, proportions and position of every part on the canvas. Image 2 is the same hose reel in its $L look, drawn from the side: copy its materials, colours, wear and level of detail ($D), never its camera. Paint image 1 as that $L hose reel: $SD. $FD Every part stays exactly where image 1 puts it, with the size image 1 gives it; image 1's grey tones are only shading hints. $COMMON"
  if [ "$L" = Modern ]; then
    PR="$PR The reel stands on the owner's chosen Modern stand: ONE round red post rising from a square red foot plate to a red yoke under the drum (exactly as image 1 places them; the post stays clearly visible below the drum), never a box base. On the hub opposite the outlet sits the same chrome valve image 2 shows on its right: a chrome valve body, a short stem, and a red spoked handwheel lying flat on top (seen from above as an ellipse with its spokes), never a plain cap."
  fi
fi
mkdir -p "$O/raw"
export CODEX_MODEL=gpt-6.1-sol
python3 .claude/skills/generating-images/scripts/codex_image.py edit --codex-home "$RMS/codexhome_reel$W" --timeout 540 \
  --image "$GU" --image "$REF" --out "$OUT" --prompt "$PR" > "$O/raw/$(basename "$OUT" .png).log" 2>&1
echo "$? $OUT"
