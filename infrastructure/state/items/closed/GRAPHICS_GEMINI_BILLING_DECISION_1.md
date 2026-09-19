# GRAPHICS_GEMINI_BILLING_DECISION_1 — enable Gemini billing for the facing pipeline?

Owner decision, prepared by BENCH overnight 2026-09-05 so the card is one yes/no.

## The situation
- The Wrecked-Machines facing pipeline needs an image model that can generate consistent
  N/S/E/W views. Channel + API key are ready; **Gemini free tier allows 0 images**.
- The free local route (MULTIVIEW_FACING_PIPELINE_1, InstantMesh on the 5080) fixed its
  pose-collision bug but the owner judged the output UNUSABLE ("crushed tin cans"), and
  the local-imagegen track is PARKED by ruling (it was killing seat windows). rembg +
  Remotion free wins are already landed and are not at issue.

## The cost (checked 2026-09-06, ai.google.dev/gemini-api/docs/pricing via search)
- Gemini 2.5 Flash Image ("nano banana"): ~$0.039 / 1024px image.
- Imagen 4 Fast: ~$0.02 / image. Batch API halves it.
- Scale math: even 100 machines × 4 facings × 5 iterations = 2,000 images ≈ **$40–80
  worst case, single digits for a first proving batch**. Prices decay — re-check at
  decision time.

## The card
**DO:** enable billing on the existing key (2 min, Google AI Studio) and cap it (budget
alert at $25) — unblocks FOUNDRY's facing work at coffee money.
**DON'T / cost of wrong call:** billing enabled and forgotten with no cap = the only real
downside; the cap removes it. Declining leaves Wrecked-Machines facings blocked with no
live route (local track parked, InstantMesh rejected).

## Blocked on
The owner flipping billing on (his account). Rides BIOME_FAUNA_ASSIGNMENT_SITTING_1's
morning or any 2-minute window.
