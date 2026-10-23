<!-- version: gpt_targeted_second_look@v1-G2ownview -->
# Task: targeted second look (you are the second reviewer)

A first reviewer looked at this art and could not settle it. Its specific concerns are listed below under
"Concerns", each with an ID. You are not re-reviewing from scratch: you are settling those concerns, with
the images in front of you, and adding anything blocking it missed.

Before you read the concerns, look at the pictures and write `own_view`: two or three sentences on what you see
and whether the owner would keep it, perhaps with a note (size, more variants, a little more realism), or redo it
(wrong surface on a facing, wrong or Earth-like animal, defining feature missing, baked backdrop, donor). Then
answer the concerns, using your own view as the yardstick.

For EACH concern answer:
- `confirmed` — the problem is really there (say where and what you see),
- `refuted` — it is not there; give **evidence**: what in the picture shows it is fine (a concern refuted
  without pointing at the picture counts as unclear),
- `unclear` — the images cannot settle it (say what is missing).

Then add your own findings (same codes and fields as the first reviewer) and a verdict:
- `strong_accept` — every concern refuted with evidence AND you see nothing blocking: ship it as it is.
- `regen` — anything else that should be redrawn.
- `unsure` — you cannot judge from these images.

Return exactly this JSON object (no prose, no code fence):

{
  "schema": "rm-art-eval/gpt@v1",
  "subject": "<defName>",
  "image_seen": "<one line: what the attached images show, so a wrong attachment is caught>",
  "own_view": "<your own view, written before the concerns>",
  "concerns": [{"id": "K1", "answer": "confirmed|refuted|unclear", "evidence": "<what in the picture>"}],
  "findings": [{"code": "<code>", "where": "<image/facing>", "seen": "<what>", "quote": "<rule>",
                "confidence": 0.0, "model_severity": "blocking|polish", "fix": "<one positive sentence>"}],
  "verdict": "strong_accept|regen|unsure"
}
