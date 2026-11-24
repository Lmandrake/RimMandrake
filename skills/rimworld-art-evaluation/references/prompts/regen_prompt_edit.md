<!-- version: regen_prompt_edit@v2 -->
# Task: turn review findings into the next generator prompt

You write the prompt for the NEXT render of one RimWorld sprite. The input has three parts: the subject's description,
the previous generator prompt (if any), and the review findings that made this render fail. A reroll with the same
words is a wasted render. So every blocking finding below must become an explicit change in the prompt.

Rules (from `generating-rimworld-sprites` and `rimworld-sprite-facings`):
- Phrase every change as the state wanted, never as a prohibition. Write "the north view shows the rear: back, tail
  and haunches, eyes hidden". Do not write "no face on north". Image models condition on the words present.
- Say the surface, never the compass: "rear view, seen from behind", "front view, eyes toward the viewer".
- Keep what passed. Name the invariants that must not change: palette, body plan, the features that the review
  confirmed. Then a fix of one thing does not break another.
- Some findings reject the ANATOMY (reads as an Earth animal, wrong body). Then the old render must not be the
  reference image. Say `reference: none`. Build the body from the description and the departures (the visible features
  that make the subject NOT its nearest Earth animal).
- A catch item is a dead specimen of the living body, lying on the ground, limp, eyes dull.
- Transparent background, painterly vanilla RimWorld style, realistic. Value and colour contrast against the ground
  carry the silhouette.
- The style has no outlines. Write nothing about an outline, a keyline or a drawn line in your prompt. The queue tool
  adds the house style text, which says that. For a finding about an outline or a keyline, the change is: "soft painted
  edges; value and colour contrast carry the silhouette". The queue tool leaves that text out when your prompt itself says "no
  outlines". Take such words out of the previous prompt.

Return exactly this JSON object (no prose, no code fence):

{
  "schema": "rm-art-eval/regen@v1",
  "subject": "<defName>",
  "edits": [{"finding": "<code>", "change": "<the sentence added or replaced in the prompt>"}],
  "invariants": ["<what must stay as it is>"],
  "reference": "keep|none",
  "prompt": "<the full next generator prompt>"
}
