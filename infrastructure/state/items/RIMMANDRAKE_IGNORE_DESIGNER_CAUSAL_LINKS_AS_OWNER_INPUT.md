# Keep causal repair links out of Designer owner input

## refs

file: src/RimMandrake/rimflow/designer_stage.py
file: src/RimMandrake/rimflow/selftest_designer_stage.py
file: design/concepts/Stillsand/stage.json

## spec

Stillsand run rm-role-designercodex-1794832693 reopened stage 2 for OWNER:1794831087978003730. That event files the completed cross-clone pipeline repair under a standing ruling. Its only reference to the Stillsand Designer item is caused_by. It carries no ownerSaid or byCard input. owner_uncited searches the entire serialized event and treats this causal metadata as new design direction.

Exclude the top-level caused_by field when determining whether an event names the concept item. Preserve intake from the event's own id and every other field, including explicit owner words on related items. Keep all existing provenance and delegated-call citation checks.

## verify

Add the regression before implementation. After accepting stage 2 in a temporary concept, append a standing-ruling system filing whose only concept reference is caused_by. Its unread owner feed must stay empty and its accepted design must stay current. An explicit owner correction on a related item must still become unread input. Run the complete Designer stage selftest and the affected pipeline tests. Check the real Stillsand run through designer_stage.py check without advancing it.

## criteria

- A causal link alone adds no owner input and invalidates no accepted design.
- Explicit owner words naming the concept item still reopen the design, including words on related items.
- Genuine same-item replies and authenticated delegated calls retain their existing intake and provenance behavior.
- The real Stillsand result passes its stage-2 check with every built capability and adopted decision preserved.
