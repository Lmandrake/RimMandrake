# Alien redraws — session status (2026-09-06)

🔴 **OWNER RULING, 2026-09-06, via the art review sheet: AA_Atispec and
Revenant art work is CANCELLED, not parked.** Verbatim: *"Revenant and
Atispec are separate from the terrestrial three. They should just be
dropped and no longer reskinned. Unneeded."* — on Atispec's v2 candidate:
*"That is so strange I almost love it. A rainbow lobster thing... well at
least it's creative."* (i.e. genuinely funny/interesting by accident, not a
reason to keep chasing a redraw); on Revenant: *"Do we really NEED this?"*

**Do not act on the v3/reworked-prompt plans below.** They are kept as a
record of what was tried and why it failed, not as a queued next step. If
either creature's art becomes a live question again later, it starts fresh
from this ruling, not from resuming these attempts.

Behemoth is finished and still live for review (approved, with a note:
"might be interesting for the nightside beasts"). Everything below the
Behemoth section is dead work, kept for provenance only.

## DONE — AA_FrostboundBehemoth (decisions.json key "AA_Behemoth")

Live defName is `AA_FrostboundBehemoth` (decisions.json's "AA_Behemoth" does not
match any live def — this is Alpha Animals' cold-biome giant, adult
`drawSize` 4.1, `texPath Things/Pawn/Animal/AA_FrostboundBehemoth/AA_FrostboundBehemoth`).

- Reference (256x256 shipped south sprite, upscaled proportionally to 1024x1024):
  `/mnt/d/Luke/dev/Rimworld/Transient/art_refs/AA_FrostboundBehemoth_south_ref1024.png`
- Candidate: `/mnt/d/Luke/dev/Rimworld/Transient/art_review_AA_FrostboundBehemoth_south_candidate.png`
- Validator: PASS, 1 WARN (1.24% faint alpha inside silhouette — intentional icy
  glow, confirm by eye).
- Contact sheet: `/mnt/d/Luke/dev/Rimworld/Transient/art_review_alien_redraws_sheet.png`
  (currently Behemoth only — re-run with Atispec/Revenant candidates added once
  they pass; see `contact_sheet.py --reference <ref> --out <sheet> <cand1> <cand2> ...`
  or stack per-creature sheets with `Transient/art_gen/stack_sheets.py`).

## CANCELLED (owner ruling, 2026-09-06) — AA_Atispec

- Reference: `/mnt/d/Luke/dev/Rimworld/Transient/art_refs/AA_Atispec_south_ref1024.png`
  (drawSize 4.5, texPath `Things/Pawn/Animal/AA_Atispec/AA_Atispec`)
- Two raw attempts on disk, both REJECT:
  - `Transient/art_gen/AA_Atispec_south_raw.png` (v1) — good claw span/aspect
    (0.658 vs ref 0.606) but 8% short on height and sits too low (origin y=114
    vs ref 32) — art didn't reach the top edge of the frame.
  - `Transient/art_gen/AA_Atispec_south_raw2.png` (v2) — fixed the top/bottom
    framing (touches both edges) but overcorrected: claws pulled in too close,
    aspect collapsed to 0.337 vs ref 0.606, width 44% short.
- **v3 prompt to try** (combines v1's wide claw span with v2's edge-to-edge
  framing — this exact prompt was queued once and only failed on a generation
  timeout, never actually rejected by the validator):
  > Top-down view of a bizarre alien insectoid predator, seen directly from
  > above, framed extremely tight so the creature fills the entire square frame
  > edge to edge, the tail-spike tip touching the very top edge and the claw
  > tips touching the very bottom edge, centered on a solid flat green
  > background. Narrow tapering tail-spike at the top leading down into an
  > elongated head-thorax shape, ending in two long serrated pincer-claws that
  > curve outward and open wide, spanning nearly the full width of the frame,
  > mirroring the wide splayed pincer stance of a crab seen from above. Wet
  > translucent violet-magenta chitin plating with visible glowing veins
  > beneath the shell and an iridescent oily sheen. A row of small glistening
  > black eyes and dripping venom fangs along the centerline. Pulsing
  > bioluminescent toxic-green glow beneath the translucent shell. Fierce,
  > unsettling, alien beauty mixed with horror. Flat cel-shaded
  > creature-compendium game art style with bold black outlines and hard-edged
  > shading, high contrast, tall symmetrical bilateral silhouette with wide
  > splayed claws.
- Pipeline once it lands: check corner alpha first (some generations already
  come back with real alpha, no chroma_key.py needed — see Behemoth); then
  `conform_sprite.py --reference AA_Atispec_south_ref1024.png --input <raw> --out
  art_review_AA_Atispec_south_candidate.png`; then `validate_sprite.py`.

## CANCELLED (owner ruling, 2026-09-06) — Revenant

- Reference (unmodified, 256x256 = the 128px/cell target for drawSize 2.0,
  extracted from `resources.assets` via the existing bundle-texture cache):
  `/mnt/d/Luke/dev/Rimworld/Transient/art_refs/Revenant_south_ref256.png`
  (PawnKindDef `Revenant`, `lifeStages[0].bodyGraphicData`, texPath
  `Things/Pawn/Revenant/Revenant`, `Graphic_Multi`, drawSize 2 — this is the
  BODY layer only; the separate head overlay, `Things/Pawn/Revenant/RevenantHead`
  drawSize 1.4, was out of scope this session).
- Three consecutive real generation timeouts (each ~180s, no file produced,
  same failure signature every time), while every other generation this
  session (Behemoth, Atispec x2, two throwaway apple tests) succeeded on the
  1st or 2nd try.

- 🔴 **OWNER CORRECTION, 2026-09-06: the failed prompt was conceptually wrong,
  independent of the timeout.** It described a "tall gaunt hooded humanoid
  figure" in a "dark cloak" with a "hood" and "robe hem" — that is the stock
  evil-sorcerer/lich silhouette (owner rendered it directly via ChatGPT and
  called it out: *"why are we making things that look like evil sorcerers?"*).
  **Not wanted, and not a Jawa/desert-setting thing either — it would be just
  as wrong in vanilla RimWorld.** The actual ThingDef description is body
  horror, not wizardry: *"a spindly figure of desiccated skin stretched over an
  impossibly tall humanoid frame."* No hood, no cloak, no robe.
- **Do not reuse the hooded-figure shape at all.** The next prompt should
  describe: a bare, gaunt, unnaturally tall humanoid body (no clothing/cloak
  silhouette of any kind), taut grey-white desiccated skin pulled tight over a
  visible bone/joint structure, unnaturally elongated limbs and neck, a small
  hollow-eyed head at the top. The legibility fix (the owner's actual
  complaint — "can't even see what this thing is") should come from
  **exaggerating the tall-and-thin proportions and giving it one clean,
  unbroken outline**, not from adding a hood/robe shape to hide the figure
  behind. Keep the "fills the frame edge to edge, touches top and bottom"
  framing instruction — that part was fine and is unrelated to the concept
  problem.
- Whether "moderation stall" was ever the real cause of the three timeouts is
  now moot — the prompt needed to change regardless. Try the reworked concept
  first; if it still times out repeatedly, that's the point to suspect the
  pipeline again rather than the prompt.
- Pipeline once it lands: same as Atispec above, reference is already 256x256
  (drawSize 2.0 × 128px/cell = 256, no upscale needed) so `conform_sprite.py`
  will scale the generated art DOWN to 256x256 automatically.
