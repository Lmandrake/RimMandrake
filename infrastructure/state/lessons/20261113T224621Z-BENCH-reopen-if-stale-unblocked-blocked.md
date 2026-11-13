designer_stage.reopen_if_stale reopened a BLOCKED concept (and could reopen a locked one) whenever any input went stale, so a fresh OWNER.jsonl note naming the item (even the owner's own PASS word) re-queued a concept the coverage judge had blocked and burned another Designer/judge run. Fixed in d482c3c7f6: reopen_if_stale returns None for blocked or locked; only unblock (a human or Conductor verb) lifts a block. Rule: an automatic 'inputs changed' reopen must never override a deliberate stop state.
item: RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH
home: src/RimMandrake/rimflow/roles/designer.md
