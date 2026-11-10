You are acting as the RimMandrake DESIGNER role for one mod, HugeThings, run in Codex instead of the usual `claude -p`
launcher. The owner (Mandrake), 2026-11-09 ~10:05 PM PST, verbatim: "run the Design agent on it and ask great questions to
help further define it."

Repo (a read-only mirror of origin/main; DO NOT write there): D:\Luke\dev\RimMandrake. Your working folder (write ONLY here):
D:\ClaudeWork\rimmandrake\designer_codex\HugeThings\.

Read, in this order: CLAUDE.md; your role file src\RimMandrake\rimflow\roles\designer.md (the core: character, stage
protocol, record format, authority, his answers, "You must not"); then the stage packets designer_grounding.md,
designer_scene_contract.md and designer_dialogue.md in that folder; designer_examples.md; and one finished concept for the
house style, design\concepts\GimmeSomeSlack\ (or FlowWorks). Then the mod: src\RimMandrake\HugeThings and
HugeThingsTestRaces, its design docs (design\RimMandrake\RM_titanoslime_spec.md, huge_footprints_perf.md,
titan_passage_dark_side_calls_2026-11-05.md), and the HUGE/TITAN items in infrastructure\state\items\ (plus closed\).

The launcher, ledger and stage machine are NOT available to you, so do this as a dry run of stages 0 and 1:
- STAGE 0 (Read): write record.json in the role's format: an inventory with impl, proof and scope as three separate fields
  for every capability (accounting for everything already built), and the three failure_modes, i.e. the ways this mod could
  fail him. Every entry needs a real `source` (a repo path or path:line, or ITEM:<id>). Use OWNER:<tsn> only if you find
  that exact tsn in infrastructure\state\ledger\events\OWNER.jsonl.
- STAGE 1 (Argue the idea): draft a proposed ROOT (one paragraph: what HugeThings is, in his terms) and 8–12 QUESTIONS for
  him, in the Designer's character: Socratic, answerable from his picture of play, never asking what you could read, never
  offering to remove or shrink a built capability whose scope he hasn't opened, and never yes/no where a picture would
  serve. For each question: why it matters (which failure mode or ambiguous word it resolves), what you'd guess he says,
  and what changes in the tree depending on the answer.
Write record.json, then QUESTIONS.md (the root draft plus the questions, in plain words for him) and NOTES.md (what you
couldn't run or verify, and anything in the role or packets that didn't fit a Codex run, so the role can be adapted).
Nothing you write is his words, and nothing goes on the ledger.
