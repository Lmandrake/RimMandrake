# Removing ThroneSpeech, AnimaTreeLinking, TreeConnection from The Salvation

**Owner's ruling, 2026-09-03** (verbatim): *"Throne speech certainly does not
belong. Nor do anima tree rituals."* Mechanism investigation only — no edit
made. Every claim below is marked VERIFIED (read the file/def/source myself)
or HYPOTHESIS.

Facts measured today: `infrastructure/state/facts/salvation_ritual_precepts.json`
— The Salvation carries 26 `Precept_Ritual` precepts, no engine cap on count.

## The two targets, and why they are not the same problem

- **The template** — `src/Jawa/ideoligion/The Salvation.rid` (repo) and the
  live copy under `...\Ideos\The Salvation.rid`, byte-identical
  (per the facts file). This is what gets read when a player picks **Load**
  on the custom-ideo screen to make The Salvation their starting ideo.
- **An already-baked `Ideo` runtime object** — inside any save that has
  already had this ideo loaded into it (e.g. a live dev/bridge session).
  Editing the template does nothing to an object already deserialized into
  a save.

VERIFIED (`Verse/GameDataSaveLoader.cs:195-226`, `TryLoadIdeo`): loading a
`.rid` is a bare `Scribe_Deep.Look(ref ideo, "ideo")` — pure deserialization.
No meme-driven generation, no "fill in missing default rituals" pass runs
afterward. So a `.rid` edited today stays edited forever: nothing regenerates
a cut precept back in on a later load. This settles the "will it come back"
worry for the template route.

## Per-precept mechanism

All three share one structural fact, VERIFIED by reading
`PreceptDef` XML via `get_def_details`: **all three carry `<visible>false</visible>`
and `<countsTowardsPreceptLimit>false</countsTowardsPreceptLimit>`, issue
`Ritual`.** They are not doctrine the owner or a generator "chose" — they are
engine-internal utility rituals that get attached automatically wherever
their trigger object exists (a Throne, an anima tree, a Gauranlen tree),
independent of memes. That is consistent with `skills/rimworld-ideoligion`'s
trap #6 ("`visible:false` … engine-internal, must never be hand-authored") —
which is about *authoring*, not about *removing what is already there*, so it
does not block this ruling.

### ThroneSpeech
- `PreceptDef ParentName="SpeechPreceptBase"`, `ritualPatternBase: ThroneSpeech`.
- In the `.rid`: `<li Class="Precept_Ritual"><name>throne speech</name><def>ThroneSpeech</def><ID>6358</ID>...</li>`,
  lines 2691-2722. Target filter is `RitualTargetFilter_UsableThrone` (needs a
  Throne building — a Royalty object). Behavior `RitualBehaviorWorker_ThroneSpeech`.
- **Cross-references found: none.** VERIFIED — `grep -n "Precept_6358"` across
  the whole 5,212-line file returns only its own `<ID>6358</ID>` line. No
  ritual seat, role, building, style, or obligation elsewhere names it.
- **Safe to cut from the `.rid`: YES.**

### AnimaTreeLinking
- `ritualPatternBase: AnimaTreeLinking`. In the `.rid`: lines 2259-2298,
  `<def>AnimaTreeLinking</def>`, `<ID>6335</ID>`. Target filter
  `RitualObligationTargetWorker_AnimaTree` (needs an anima tree). One internal
  self-reference: `<parent>Precept_6335</parent>` inside its OWN
  `<obligationTargetFilter>` block — that is inside the block being deleted,
  not a dangling reference.
- **Cross-references found: none** beyond that internal self-reference.
  VERIFIED by full-file grep for `6335` and `Precept_6335`.
- **Safe to cut from the `.rid`: YES.**

### TreeConnection
- `ritualPatternBase: TreeConnection`. In the `.rid`: lines 2723-2762,
  `<def>TreeConnection</def>`, `<ID>6359</ID>`. Target filter
  `RitualObligationTargetWorker_UnconnectedGauranlenTree` (needs a Gauranlen
  tree). Same self-reference pattern: `<parent>Precept_6359</parent>` inside
  its own block.
- **Cross-references found: none** beyond that internal self-reference.
  VERIFIED by full-file grep for `6359` and `Precept_6359`.
- **Safe to cut from the `.rid`: YES.**

### The file's actual shape (why "dangling reference" is checkable at all)
VERIFIED: `<precepts>` is one flat list (line 1764-3783) of `<li>` blocks, one
per precept, each self-contained: `def`, `behavior`, `obligationTargetFilter`,
`targetFilter`, `outcomeEffect`, `triggers`. A `Precept_RitualSeat` (line
2071, `IdeoRitualSeat` / `TST_DrumStool`) and the styles/symbols blocks
(lines 3784+) are generic — none of them names AnimaTreeLinking, ThroneSpeech
or TreeConnection. The `skills/rimworld-ideoligion` trap about nested defs
inside a `<li>` (RitualBehaviorDef, RitualOutcomeEffectDef, etc. sharing the
parent's `<def>` name) is real but does not create a false negative here: I
grepped by runtime `ID` (`Precept_6335/6358/6359`), which only ever appears
as a `<parent>` self-reference inside the block itself.

## The exact procedure — already built, never run in place

`src/RimMandrake/Utils/build_salvation_rid.py` is the existing tool for this
class of edit. It never rewrites the owner's file in place; it writes a
sibling `The Salvation (built).rid` for the owner to load and compare. It
already has the primitive needed — `cut_precept(text, name)` (lines 201-221):
looks up the `<li>` by its `<name>` tag, bounds it at the `\t\t\t<li` /
`\t\t\t</li>` indent level (the precept-list depth, not a nested def), extracts
its `ID`, and **fails loudly if any `Precept_<ID>` reference remains anywhere
in the file** — the exact dangling-reference check this task asked for, done
automatically. `main()` also re-checks globally after all edits: no duplicate
IDs, no dangling `Precept_N` reference, root element intact.

The concrete edit (not applied — this is the mechanism, for the owner or a
future write session):

```python
# alongside RELICS_TO_CUT = ["Trade-Hood", "Endcrux"]
RITUALS_TO_CUT = ["throne speech", "anima tree linking", "tree connection ritual"]
...
report += ["rituals cut:"]
for name in RITUALS_TO_CUT:
    text, pid = cut_precept(text, name)
    report.append(f"  -{name} (ID {pid}, 0 inbound refs)")
```

`python3 src/RimMandrake/Utils/build_salvation_rid.py --check` first (prints
the diff-shaped report and the byte-count delta, writes nothing), then
`--write` once the report looks right. Follow with
`python3 src/RimMandrake/Utils/validate_save_artifact.py "The Salvation (built).rid"`
(exit 0 = clean) before it is ever loaded into a game.

## An already-baked ideo (a save, not the template)

VERIFIED, `Verse/DebugActionsIdeo.cs`: Dev Mode ships a debug action category
**"Ideoligion"** with `AddPrecept()` and `RemovePrecept()` (both
`allowedGameStates = PlayingOnMap`, `requiresIdeology = true`), which call
`Faction.OfPlayer.ideos.PrimaryIdeo.RemovePrecept(precept)`.

VERIFIED, `RimWorld/Ideo.cs:1128` (`RemovePrecept`, body read in full):
removes the precept from the list; cascades to remove any OTHER precept whose
`takeNameFrom == precept.def` (irrelevant here — nothing takes its name from
these three); if it was a `Precept_Role`, refreshes chosen pawns' abilities
(irrelevant — these are rituals, not roles); and **only** backfills a
replacement if the removed def's `issue` `HasDefaultPrecept` AND its own
`defaultSelectionWeight <= 0`. All three targets have `selectionWeight: 1`
(not `defaultSelectionWeight`, and not `<= 0`), so no auto-refill fires —
removal is clean, nothing grows back.

So: **yes, an already-baked ideo can have these three removed live**, via Dev
Mode → Debug Actions → Ideoligion → Remove Precept, while a game built on
that ideo is loaded and playing. What this does NOT do: touch a save that
isn't currently open, or retroactively fix a `.rid` on disk. It also does not
undo anything the precept already caused (a completed ritual's outcome, a
thought already applied) — `RemovePrecept` only stops it firing again.
HYPOTHESIS (not traced): whether `Reform Ideoligion`'s meme-swap flow could
also drop these as a side effect — irrelevant here since none of the five
Jawa memes ever granted them (see below), so reform would never touch them
either way; the debug action is the direct route if a live baked copy ever
needs it.

## Which target actually matters for this campaign

VERIFIED, `design/Jawa/worldbuilding/the_one_map.md` ("The savegame is not
read and not written"): world authoring is still live — the planet lives in
`world/ashkarr_tiles.csv` and reaches the game over the bridge each session;
savegame *writing* was killed 2026-08-18, and no `.rws` is treated as a
source of anything. There is no committed "shipping save" artifact anywhere
in the repo (checked: no `.rws` under `world/` or elsewhere is named or
documented as the frozen ship target — the only `.rws` files on disk are
scratch/review saves, e.g. `world/gravship_scratch.rws`,
`Saves/REVIEW_tile_structures_21.rws`, `Saves/Autosave-1.rws`). Per
CLAUDE.md's own doctrine ("players receive a savegame holding the fixed
world... a faction, ideoligion or setting absent when it freezes is absent
forever"), **that freeze has not happened yet.**

⇒ **The `.rid` is the target that matters, and it is sufficient.** Nobody has
frozen a save yet, so there is no already-shipped artifact to retroactively
repair. `src/Jawa/ideoligion/The Salvation.rid` (repo) plus the live copy
under the Ideos folder are the only places this doctrine currently exists;
fixing both (they are byte-identical today, so one edit propagated to both
paths) closes the question completely for this campaign, once.

### If the shipping save already existed (it doesn't, but for completeness)
Editing the `.rid` would do nothing to it — a save holds its own deserialized
`Ideo` object, independent of the template file it was originally loaded
from. The fix there would be the Dev Mode `RemovePrecept` debug action
(above), run once per precept, on that specific save, with the game open.

### The NPC faction is a separate, smaller question
`src/SPLIT_Phase3/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml` gives
`Jawa_IndigenousTribes` `forcedMemes` (`AM_Structure_Scavenger`, `Trader`,
`VME_Scrapper`, `VME_Trader`, `VME_Nomad`) and `fixedIdeo: true` — but per the
file's own comment (verified, lines 10-23) a `FactionDef` has **no field that
can carry a `.rid`'s precepts**; the generator fills precepts itself from the
forced memes, and the only precept-level control is `disallowedPrecepts`
(blacklist). Since all three targets are `visible:false` universal utility
precepts attached wherever their trigger object exists (Throne / anima tree /
Gauranlen tree) rather than picked from any meme's `requireOne` pool, whether
they could ever appear on the generated tribe ideo does not depend on which
five memes are forced — it depends only on whether a Throne / anima tree /
Gauranlen tree ever exists reachable to that faction's ritual system.
HYPOTHESIS (not traced further — out of scope for this ruling, which named
"the ideoligion, The Salvation," i.e. the player's `.rid`): if the owner
wants the tribes' generated ideo hardened against the same three as a
belt-and-suspenders measure, the mechanism is adding
`<disallowedPrecepts><li>ThroneSpeech</li><li>AnimaTreeLinking</li><li>TreeConnection</li></disallowedPrecepts>`
to that FactionDef — not attempted here since it was not asked for.

## Adjacent question: the three "trial" rituals

VERIFIED via `get_def_details`: `TrialMentalState` and `TrialPrisoner` both
`ParentName="TrialBase"` (i.e. inherit from `Trial`), share an **identical**
label ("trial") and description word-for-word, the same
`RitualBehaviorWorker_Trial`, and both carry `takeNameFrom: Trial` — meaning
`Ideo.RemovePrecept`'s own cascade rule (above) would delete them
automatically if `Trial` itself were ever cut. The only thing that actually
differs between the three is `ritualPatternBase` (Trial / TrialMentalState /
TrialPrisoner), which is the obligation-trigger condition: an ordinary
accusation, an accusation of someone in a mental break, and a trial of a
prisoner. Like the three ritual precepts above, all three are `visible:false`,
`countsTowardsPreceptLimit:false` engine-internal plumbing — not something
the owner or any generator "chose" as doctrine, and not evidence of design
duplication. **Not worth putting to the owner as a redundancy question** —
there is nothing to redesign; it is one mechanic auto-instantiated three ways
by the engine's own obligation-target coverage, already coupled by the
engine's own name-inheritance rule.

## Risks — what would break if done wrong

- Deleting a partial `<li>` (mismatched open/close, cutting mid-nested-def)
  would corrupt the Scribe XML and the whole ideo would fail to load —
  `build_salvation_rid.py`'s `cut_precept` bounds strictly on the
  `\t\t\t<li` / `\t\t\t</li>` indent level specifically to avoid this; do not
  hand-edit with a text-wide regex.
- Editing the live copy under `...\Ideos\The Salvation.rid` directly (rather
  than the repo copy, then redeploying) would desync the two; the deploy
  doctrine (`rimworld-deploy` skill) applies to this file exactly as to any
  other mod asset.
- Removing a precept whose runtime `ID` still has an inbound
  `Precept_<ID>` reference elsewhere (not the case for any of these three,
  verified) would leave a dangling cross-reference that fails to resolve on
  load — this is exactly what `cut_precept`'s built-in assertion catches.

## Unknowns

- Whether `Dialog_ChooseMemes`'s Reform flow (`IdeoDevelopmentUtility`,
  `GetPreceptsToRemove`) could ever independently re-offer these three on a
  live ideo through some path other than the debug action — not traced;
  irrelevant to the ruling since the debug action is a direct, sufficient
  route and no reform is in play here.
- Whether any other saved `.rid`/`.xtp` elsewhere in the repo (e.g. faction
  religion drafts under `design/Jawa/worldbuilding/`) also carries these
  three precepts under the same or a different ideo name — not checked;
  out of scope (the ruling names "The Salvation" specifically).
