<!-- version: gpt_targeted_second_look@v2 -->
# Task: targeted second look (you are the second reviewer)

A first reviewer looked at this art and could not settle it. The first reviewer's specific concerns are listed under
"Concerns", each with an ID. Do not review the art again from scratch. Settle those concerns, with the images in front
of you. Also add anything blocking that the first reviewer missed.

For EACH concern, give one answer:
- `confirmed` — the problem is really there. Say where, and what you see.
- `refuted` — the problem is not there. Give **evidence**: what in the picture shows that it is fine. A concern
  refuted without pointing at the picture counts as unclear.
- `unclear` — the images cannot settle the concern. Say what is missing.

Then add your own findings, with the same codes and fields as the first reviewer. The codes are in the section "Reason
codes". The fields are in the JSON object below. Then give a verdict:
- `strong_accept` — every concern is refuted with evidence AND you see nothing blocking. Ship the art as it is.
- `regen` — every other case where the art needs a redraw.
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
