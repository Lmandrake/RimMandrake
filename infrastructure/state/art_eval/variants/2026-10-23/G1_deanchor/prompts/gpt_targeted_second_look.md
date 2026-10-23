<!-- version: gpt_targeted_second_look@v1-G1deanchor -->
# Task: targeted second look (you are the second reviewer)

A first reviewer looked at this art and could not settle it. Its specific concerns are listed below under
"Concerns", each with an ID. You are not re-reviewing from scratch: you are settling those concerns, with
the images in front of you, and adding anything blocking it missed.

Treat each concern as a HYPOTHESIS, not a finding. The first reviewer flags anything it is unsure of, and on
pictures the owner later kept most of its low-confidence concerns were false alarms. Confirm a concern only when
you can point to the problem yourself in the picture and the owner, looking at normal zoom, would name it; a
concern you would not have raised yourself, or that needs squinting, is refuted when the picture shows it is fine.

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
  "concerns": [{"id": "K1", "answer": "confirmed|refuted|unclear", "evidence": "<what in the picture>"}],
  "findings": [{"code": "<code>", "where": "<image/facing>", "seen": "<what>", "quote": "<rule>",
                "confidence": 0.0, "model_severity": "blocking|polish", "fix": "<one positive sentence>"}],
  "verdict": "strong_accept|regen|unsure"
}
