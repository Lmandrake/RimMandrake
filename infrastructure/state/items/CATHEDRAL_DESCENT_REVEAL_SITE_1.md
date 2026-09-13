
<!-- Split from the 2026-09-12 build decomposition; standing constraints: arc spec section 'The law' (knowledge gate, bans 1/2/3/6, rationed patience, Oracle laws, no Force, no worldgen) bind this item. -->


## spec
Arc §5, A7 RULED: a **real structure-injected site the player walks** in v1 —
no worldgen; structure injection on the fixed world / a descent map, built
via the bridge lanes (rimworld-world-editing / layout injection; smaller
set-piece and text-only options were DECLINED). Content: canyon-scale halls,
the mile-long production line, the second coolant circuit toward the Scald,
Sentinels walking past the party (pass behavior — reuse item 6's exception
scoped to the escort). One-time escorted descent; at the bottom the first
direct address in the whispered-voices register through droid/comms gear
(origin canon §3 channel grammar) — text/menu, prescribed fallback first,
Oracle upgrades voice only. Discloses aliveness + scale + the-audition ONLY
(A2); bans 2/6 hold; scoped to the player — no faction text, trader chatter,
or codex artifact changes; after-letters stay §P. Trigger: VOUCHED + post-
restore-choice flag (the choice itself, either answer), never Regard alone;
fires ONCE, sets the reveal flag items 6/8 read. **A1 propagation rides this
item:** the Utinni is the usher — she KNOWS because she receives the dead
Rakatan transponder band; propagate the receiver-lore into
`reconciled_lore/03_deep_history.md` and the gravship/Utinni bond material in
the same change (owner: "propagate when the arc builds"). NEW defNames
(flag): descent site/quest defs `RUT_CathedralDescent_*`, RUT_ tier; walls
and dressing reuse kit §2 defs wherever possible.

## verify
Arc §8 seed 3: fires once, only from the ruled trigger set (dev-flag matrix:
VOUCHED without flag = no fire; flag without VOUCHED = no fire); re-trigger
attempts refused; no faction-visible text changes anywhere (diff the string
surface); all reveal text passes item 3's linter (scale/aliveness yes, mercy/
drill never); completes Oracle-absent end to end; site verified actually
present per-slot (`jawa/list_things`, not the placement log's net count); A1
lore landed in the named docs with inbound references fixed.

## criteria
Descent playable start-to-bottom on a quicktest-loaded save; reveal flag
published to the blackboard; stage 3 entered by this beat and only this beat.

**Depends on:** item 1 (VOUCHED + flags), item 2 (stage-3 hum register),
item 3 (linter), item 4 (VOUCHED earnable), item 6 soft (escort pass
behavior — can stub with faction-neutral spawns if 6 lags), restore-choice
flag existing (origin canon §4 — already specced, mirror only). **Waited on
by:** item 6's Helix-REVOKE, item 8 (bans-through-the-fall use the same
string gate; gate stays player-only through it). **Seat/needs:** FOUNDRY;
bridge + game-up (structure injection, escort run); quest authoring for the
escort shell.
