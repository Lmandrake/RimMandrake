# RIMMANDRAKE_MOVE_IMAGE_SKILLS_TO_WORKFLOWS_GPT_TOOL_BORROWS

## What the card said

<!-- answered 2026-11-19T21:03:33Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** [owner-asked] Thu Nov 19, 12:53 PM PST. The Crystallize sweep found two skills in this repo that do general Codex image work: generating-images and editing-images. Neither depends on RimMandrake, so no other project can use them today. One catch: our ask-GPT tool (gpt_consult.py) borrows a file from inside one of them, so a move must also give that tool its own copy of the Codex finder. (Hard to read? Type STE, Binding or Both for a rewrite.) Where should the two image skills live?
**Picked:** Move to MandrakeWorkflows (Recommended)
**Its description:** Why: every project gets them, one copy to maintain. Cost: one Opus run to move them, fix the ask-GPT tool and add the registry row; a small risk the ask-GPT tool breaks until tested. Recommended: they are generic, and the dependency is the only real work.
**Other options:** Keep them in RimMandrake · Move later, after the mods run
