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

## The showcase set

Owner, 2026-11-05: *"Maybe it might be good to add the idea of multiple showcases then that are as orthogonal as
possible. The Other showcases (if present) should feature ONLY very different functionality compared to the prior ones,
until efficient coverage is had."*

A mod's face is an **ordered list of showcases**, not one first-judged scene. A showcase is a group of scenes from this
file that he judges as the mod's face. In `scenes.json`, beside `scenes`:

```
"showcases": [
 {"id": "moat", "scenes": ["<scene id>", ...], "exercises": ["<inventory id>", ...], "source": ["OWNER:<tsn>"],
  "decision": "<record.json decision id>"},
 {"id": "...", "scenes": [...], "exercises": [...], "overlap_why": {"<inventory id>": "why staging needs it"}}],
"coverage_rest": [{"capability": "<inventory id>", "by": ["<scene id or leaf id>"], "why": "why an ordinary check is cheaper"}]
```

- **The unit** is a record.json inventory capability: every built entry (`impl: present`, whatever its scope: it ships
  until it is removed) and every entry in scope (`approved`, `opened_by_owner`). A built entry scoped `out` is covered
  only through `coverage_rest` (its removal or absence check), never by a showcase. `exercises` names the capabilities
  the showcase really uses in play, not those it merely has on the map.
- **Showcase 1 is the flagship he picked**: its `decision` names the record.json decision (speaker `owner`) that records
  his pick, with `"flagship": "<this showcase id>"`, and its `source` shares that decision's `OWNER:<tsn>`. His root
  approval is not a pick. If he has picked none, ask at stage 2. A mod whose only units are built but scoped out has no
  showcase: `coverage_rest` covers them.
- **Each next showcase is chosen greedily**: of the candidates, the one that newly exercises the most capabilities no
  earlier showcase exercised. The program checks this against every later showcase in the list: none may have offered
  more new capabilities at an earlier position. It features ONLY very different functionality: what it shares with earlier showcases is
  the minimum needed to stage it. The numbers are in `src/RimMandrake/rimflow/showcase_rules.json`: `max_overlap` 0.25
  (share of its exercised capabilities that earlier showcases already exercised) and `min_new_after_first` 3. Both are
  **UNMEASURED** first guesses until replayed against real concepts. Above the overlap limit, every shared capability
  carries its staging reason in `overlap_why`. A scene he named that is not orthogonal (FlowWorks' pit trap and island
  bridges both reuse the moat's pits and drawbridges) stays a scene; it is a showcase only if it passes these rules, or
  its shared capabilities carry `overlap_why`.
- **Stop criterion: efficient coverage.** Add showcases until no candidate would newly exercise at least
  `min_new_after_first` capabilities within the overlap limit. Then stop: every capability left is listed in
  `coverage_rest` with the cheaper ordinary scene or leaf check that covers it (`by`: a scene id here or a tree leaf id)
  and `why`. Coverage is had when every unit is exercised by a showcase or listed in `coverage_rest`; no capability is
  silently uncovered.
- **Interactions stay.** Orthogonality chooses showcases; it deletes no check. The per-mod `walk` leaf, every leaf whose
  point IS an interaction, and every `interaction` scene remain whatever they share with a showcase. Each experience or
  walk leaf still has its own acceptance scene; a showcase never stands in for one.

What the program checks (`designer_stage.py showcases <dir>` prints it; stage 3 and stage 5 refuse on it): per
showcase the new-coverage count and overlap; showcase 1 is bound to his recorded pick; a later showcase newly exercises
at least `min_new_after_first`, and no later showcase would have added more at its position (greedy order); an overlap over the limit has a staging
reason for each shared capability; each `coverage_rest` entry names a real scene or leaf and a why; and every unit is
covered. Whether two showcases are "very different" in play is a judgement the exam and his review make, not the
program.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
