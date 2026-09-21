#!/bin/bash
# Generate 6 generic RM Graffiti mark candidates via Codex $imagegen.
cd /mnt/d/Luke/dev/Rimworld
D=Transient/art_review_generic_marks
CI=skills/generating-images/scripts/codex_image.py

STYLE="Painted straight-on, flat orthographic top-down-facing wall mark with no perspective and no cast shadow. Crude hand-daubed pigment applied with a finger or a scrap of rag: thick uneven strokes with ragged bristly edges, a scatter of small spatter dots, and one or two short drips running down from the heaviest strokes. High contrast, bold, readable as a single silhouette from far away. Muted earthy pigment palette only: soot black, burnt ochre, dried-clay red, chalk white. Painterly hand-made illustration in the art style of the video game RimWorld. Every stroke terminates cleanly well inside the frame, leaving a wide empty margin on all four sides. The mark is isolated on a completely flat pure green #00ff00 background: no wall, no bricks, no texture, no paper, no border, no frame, no caption, no signature, no lettering and no written words anywhere in the image."

run () {
  name="$1"; shift
  prompt="$1"; shift
  for attempt in 1 2; do
    timeout 400 python3 "$CI" generate \
      --out "$D/raw/${name}.png" \
      --codex-home "/mnt/d/Luke/dev/Rimworld/Transient/art_review_generic_marks/.ch_${name}" \
      --timeout 360 --force \
      --prompt "Use \$imagegen to create a 1024x1024 image. ${prompt} ${STYLE}" \
      && [ -s "$D/raw/${name}.png" ] && { echo "OK $name"; return 0; }
    echo "retry $name (attempt $attempt failed)"
  done
  echo "FAIL $name"
}

run tally "Subject: a tally count scratched and daubed on a wall. Three complete five-bar gates plus two extra upright strokes, so seventeen strokes in all, arranged in one horizontal row: each gate is four vertical strokes with a fifth stroke slashed diagonally across them. Soot black pigment, the leftmost gate faded and weathered, the rightmost strokes fresh and heavy." &
run arrow "Subject: one single big crude directional arrow pointing to the right, daubed in burnt ochre. A thick straight shaft with a broad open chevron head, painted in two or three confident strokes, with a drip running down beneath the arrowhead." &
run hazard "Subject: one single warning glyph: a rough hand-painted triangle outline with a single bold vertical exclamation stroke and a heavy dot inside it. Dried-clay red pigment, corners of the triangle overshooting where the strokes cross." &
run sun "Subject: one simple sun mark: a solid filled disc with eight straight tapering rays radiating evenly around it. Burnt ochre and pale yellow pigment, the disc slightly lopsided and hand-made." &
run handprint "Subject: one single human handprint, palm and five splayed fingers, made by pressing a pigment-covered open hand flat against the surface. Burnt ochre and dried-clay red, the print heavier at the palm and patchy at the fingertips, with a faint speckled halo of blown pigment around the edge." &
run spiral "Subject: one single continuous crude spiral, wound three and a half turns from a heavy centre out to a thinning tail. Soot black pigment over a faint offset dried-clay red echo of the same spiral, as if painted twice." &
wait
echo "ALL DONE"
