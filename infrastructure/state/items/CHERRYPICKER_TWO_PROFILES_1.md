# CHERRYPICKER_TWO_PROFILES_1 — one cut list cannot be both the shipped game and the test game

Owner, 2026-09-02, after asking whether Cherry Picker was making the modlist hard to
vary for testing: *"Yes to two cut lists and other recommendations. I can certify I
have always been cutting things for lore reasons and the belief I was making things
easier to debug by reducing complexity. Imagine my surprise to see I made some things
harder."*

## spec

**The measured position when this was filed.** 1509 cuts live (`cherrypicker.py
--source live`, config mtime 2026-09-01): ThingDef 1318 · BackstoryDef 141 ·
BiomeDef 26 · IncidentDef 8 · PawnKindDef 7 · HediffDef 5 · GeneDef 2 · TraitDef 2.
🔑 **Not one of them was cut to fix a breakage** — every attributable batch is lore or
roster curation (143 wrong-fiction backstories, 28 non-roster turrets, 26 biomes that
do not touch Ash'karr, ~1140 unattributed theme culling). That is what makes an empty
review profile safe: cutting has only ever CAUSED failures here, never prevented one.

**The three costs already paid, all recorded:**
- The def dump is captured BEFORE Cherry Picker runs, so 1,162 of the then-1,289 cut
  ThingDefs still appeared in dump-derived review sheets — the owner reviewed animals
  that no longer existed in his game (`facts/dump-is-pre-cherrypicker.md`).
- Cutting vanilla `MeleeWeapon_Ikwa`, sole Core carrier of `NeolithicMeleeDecent`,
  silently disarmed every kind inheriting `TribalWarriorBase`. Four days, no log line.
- A weapon audit reported 12 disarmed kinds when the truth was 2, by subtracting the
  cut list (intent) from a capture that was already post-cut (reality).

### ✅ DONE — the swap itself
`src/RimMandrake/Utils/cherrypicker_swap.py`, mirroring `modlist_swap.py`: identity by
KEY LIST not bytes (the game reformats its own settings files), snapshot-before-write
that skips a snapshot identical to one already held, plan-by-default, and a loud status
line while REVIEW is live. Profiles committed at
`infrastructure/state/cherrypicker/CherryPicker.{SHIP,REVIEW}.xml`.

### Still owed
1. **A reason per cut batch.** ~1140 keys are UNATTRIBUTED — answering "why was this
   cut" today costs a git-archaeology pass. Record the reason at cut time, in a form
   `cherrypicker.py` can read back.
2. **Sheet builders must consult `cherrypicker.py`, not the raw dump.** Until they do,
   the next review sheet handed to the owner still describes content that is not in
   his game. This is the defect that cost him time; the swap only gives him a game
   where the dump happens to be honest.

## verify
- `cherrypicker_swap.py --status` names which profile is live and warns while REVIEW is.
- Round trip proven 2026-09-02: SHIP 1509 → REVIEW 0 → SHIP 1509, no PRESWAP noise.
- ⚠️ Still UNMEASURED: that a game started under REVIEW actually loads the uncut
  content. The swap is INERT until the next game start, and no load has run under
  REVIEW yet. Do not report the profile as proven until one has.

## criteria
A review or test pass can be run against a game that cuts nothing, and the owner's
campaign game keeps all 1509 cuts, without either being a hand-edit — and a review
sheet built from a dump no longer shows him content his game does not contain.
