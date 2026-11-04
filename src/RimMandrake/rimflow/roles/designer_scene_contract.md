# Designer packet: the proof-scene contract

Injected at stage 0 (the script audit) and stage 3 (planning). The contract is data in `scenes.json`, checked by
`designer_stage.py`; the tree's schema rejects unknown fields, so none of this goes in `tree.json`. Owner, 2026-11-03:
*"the ladder is installed in a pit that he can climb without the ladder, so that's not a good test."* *"I guarantee you
most mods do not have mature testing scripts. That's part of what I'd like Designer's help on."*

## Exploration versus acceptance

- **Exploration** (`kind: exploration`) may be a labelled mock or a hand-staged demonstration, the Conductor's included.
  It names the `question` it explores. It never accepts a leaf, however it is labelled.
- **Acceptance** (`kind: acceptance`) is created by a named entry point in the mod's proof script (`staged_by: script`,
  `entry_point: "<repo path>::<function or scene name>"`). If that entry point does not exist yet, file its
  implementation as a build item and name it in `entry_point_item` before the acceptance review is scheduled. A hand or
  mock scene with `kind: acceptance` is refused.
- **Interaction** (`kind: interaction`) joins two or more features (`features`: leaf ids) where the acceptance property is
  their interaction. Each feature still has its own acceptance scene; an interaction scene never substitutes for one.

## Each acceptance or interaction scene

```
{"id": "ladder_climb", "kind": "acceptance", "requirement": ["<leaf id>"], "staged_by": "script",
 "entry_point": "src/.../validation.py::scene_ladder_climb", "entry_point_item": "<item, if the entry point is missing>",
 "start": ["pit depth 3, walls unclimbable without a ladder (asserted)", "pawn can climb ladders"],
 "action": "order the pawn into the pit", "expect": "the pawn uses the ladder: its path crosses the ladder cell",
 "control": {"case": "the same pit with the ladder removed", "expect": "the order is refused: no path",
             "rules_out": "the pawn climbing the wall without the ladder"},
 "restore": "remove pit and ladder, restore terrain from the recorded snapshot", "hold": "immediate | owner_review"}
```

- **Start**: a known, asserted starting state appropriate to the scene. "Cleared and dry" is one recipe; it is wrong for
  flooding, vegetation, obstruction, fire or integration behaviour.
- **Control**: passes when the expected rejection or absence occurs, and it must distinguish the intended mechanism from
  a plausible alternative explanation (`rules_out`). Removing the object is not automatically a useful control: the
  positive case needs evidence it used the mechanism.
- **Hold**: whether the scene ends at once or stays up for his review.
- **Recovery**: before a scene changes persistent state, the runner records how to restore it
  (`designer_stage.py scene-begin <dir> --scene <id> --recovery "<what to put back>"`). A normal exit restores and closes
  it (`scene-end`); an `owner_review` scene is held instead (`scene-hold --until "<when>"`). After an interrupted run the
  open entry stays, and the launcher refuses every further run on the concept until it is restored or held.
- The mod's script lacks a part (start assertion, control, restoration)? The stage 0 audit lists it; stage 3 files the
  build item. You write no code.
- Each experience or walk leaf off the offline tier has at least one acceptance scene.

The intent behind a scene is the approved requirement it cites (`requirement`), or the exploration's `question`.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
