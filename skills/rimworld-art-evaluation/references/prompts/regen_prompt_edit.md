<!-- version: regen_prompt_edit@v1 -->
# Task: turn review findings into the next generator prompt

You write the prompt for the NEXT render of one RimWorld sprite. You are given the subject's description, the
previous generator prompt (if any), and the review findings that made this render fail. A reroll with the same
words is a wasted render: every blocking finding below must become an explicit change in the prompt.

Rules (from `generating-rimworld-sprites` and `rimworld-sprite-facings`):
- Phrase every change as the state wanted, never as a prohibition ("the north view shows the rear: back, tail
  and haunches, eyes hidden" — not "no face on north"). Image models condition on the words present.
- Say the surface, never the compass: "rear view, seen from behind", "front view, eyes toward the viewer".
- Keep what passed: name the invariants that must not change (palette, body plan, the features the review
  confirmed), so fixing one thing does not break another.
- A finding that rejects the ANATOMY (reads as an Earth animal, wrong body) means the old render must not be the
  reference image: say `reference: none` and build the body from the description and the departures.
- A catch item is a dead specimen of the living body, lying on the ground, limp, eyes dull.
- Transparent background, painterly vanilla RimWorld style, realistic, clean dark outline.

Return exactly this JSON object (no prose, no code fence):

{
  "schema": "rm-art-eval/regen@v1",
  "subject": "<defName>",
  "edits": [{"finding": "<code>", "change": "<the sentence added or replaced in the prompt>"}],
  "invariants": ["<what must stay as it is>"],
  "reference": "keep|none",
  "prompt": "<the full next generator prompt>"
}
