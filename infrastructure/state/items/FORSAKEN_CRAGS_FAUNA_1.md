# FORSAKEN_CRAGS_FAUNA_1 — design rows for three promoted livestock mockups

Owner, 2026-09-01, reviewing `src/RimStarWars/Livestock/art/mockups/PICKS.md`:
*"Others get promoted to other crag creatures. The forsaken crags are the dark
biomes on the night side."*

**The Forsaken Crags** = `AB_RockyCrags`, the nightside ground biome (26% of the
nightside, −30…0 °C; `design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md`).

## spec

Three pictures exist before their creatures do. Write one design row each —
role band, diet, product or threat, valve, temperament, story hook — in the
voice of `design/Jawa/proposals/ludicrous_livestock_deep_design.md` §2, then
hand the rows to the owner as a review sheet:

1. `moornak_opt1.png` — crags creature (seven asymmetric eyes, damp black hide, no mouth)
2. `moornak_opt2.png` — crags creature (cat-large, one-sided eye cluster, violet undertone)
3. `karrask_opt3.png` — its own new creature (horned armadillo, hexagonal plates, fresh
   shoulder band). NOT necessarily crags fauna — the owner said only "its own new creature".

Nothing here is livestock by default; a crags animal may be wild fauna. The
beast-normalization spirit applies (born normalized).

## verify

Owner rules each row on a review sheet (`review-sheets` skill; `check_sheet.py` exit 0).

## criteria

Three rows ruled; each promoted image has a named creature, a biome, and a
build item or a dead mark.

## 2026-09-01 (FOUNDRY) — three design rows written, sheet built, awaiting the owner's ruling

Looked at all three mockups directly (not designed from the prompt text alone)
before naming anything. Three names coined, none of them the owner's:

- **Cindermare** (`moornak_opt1.png`) — wild threat, `AB_RockyCrags`. No mouth
  in the art, so its kill mechanic is a cold-drain grip (saps body heat on
  contact) rather than a bite; solitary and untameable, mane/hide harvested
  only from a kill.
- **Skarnix** (`moornak_opt2.png`) — wild threat, `AB_RockyCrags`. Cat-large
  ambush stalker; valve is behavioral (will not cross firelight/a heated
  space), so a lit camp neutralizes it rather than requiring combat stats.
- **Tellurox** (`karrask_opt3.png`) — livestock, biome left general (owner's
  promotion note only committed the two moornak options to the Forsaken
  Crags, not this one). A genuine draft/pack beast, deliberately NOT another
  molt-armor farm like karrask — its shell is permanent (grows with the
  animal, never sheds), so first-rate plate only comes from slaughtering a
  mature working animal. Keeps this from cannibalizing karrask's niche.

Sheet: `design/Jawa/worldbuilding/review/forsaken_crags_fauna_sheet.html`
(built off `review-sheets`' `sheet_template.html`, custom `RENDER` block for
the full field table). `check_sheet.py`: **0 FAIL, 0 WARN, 28 ok**. All three
rows pre-filled `approve` — that's FOUNDRY's call, not the owner's; every
invented premise (the three names, Cindermare's feeding mechanism, Tellurox's
un-pinned biome, Tellurox's permanent-shell differentiation from karrask) is
declared in the sheet's own `CONFIG.invented` block, not buried.

No decisions file exists yet — nobody has reviewed it. To open it:
`python3 /home/mandrake/.claude/skills/review-sheets/assets/serve_sheet.py --sheet design/Jawa/worldbuilding/review/forsaken_crags_fauna_sheet.html --decisions design/Jawa/worldbuilding/review/forsaken_crags_fauna_sheet.decisions.json`
Still open: the owner's ruling itself (approve/revise/cut per row), and —
only after that — porting whichever names survive through the naming-scheme
grammar into real defs. Item stays `doing`.
