# GREYSEA_RULED_CONTENT_1 — build the Grey Sea content ruled at the 2026-09-27 sitting

All 17 agenda questions ruled by question card 2026-09-27, recorded on
`GREYSEA_FLOOR_PASS_1`'s ledger. Authority for every row below:
`design/Jawa/worldbuilding/biomes/grey_deep_sitting_agenda_2026-09-27.md`
(§2 has each question's full framing; §3 is the do-not-re-ask list).
This is the buildable-now half; the parent `GREYSEA_FLOOR_PASS_1` stays open
until the owner walks the floor live.

## The rulings, executable

1. **Pillars: STORY ONLY (Q1).** No waymark job, no murk movement penalty,
   no navigation mechanic. Nothing to build; do not add one.
2. **Catch: keep all 13, rebalanced rare (Q2).** Lower `fishPopulation` on
   `RM_GreySea` and push species from common into uncommon/rare bands —
   sparseness felt at the dock, every catch stays possible. No cuts.
3. **plantDensity 0.22 (Q3)** on `RM_GreySea` (currently 0.14).
4. **All ten understorey flora ship (Q4)** per
   `the_grey_deep_flora_pass_2026-09-27.md`, with the four contested ones
   resolved: lamp-iridescent cushion SHIPS (structural colour — emits nothing,
   ever; the read is oil-sheen only under player light) (Q5); the mason's
   skirt IS a plant (pale banded mat, grazeable by the pillar-snail; the mason
   itself stays def-less fiction) (Q6); the anti-crystal sprig is PURE
   DRESSING — no harvest, no item, no product (Q7); the pool lily rides the
   pool SURFACE engine permitting, lip placement as silent fallback (Q8).
5. **Sponge halo: prose only (Q9).** Description + creature-placement
   flavour. No yield modifier of any kind.
6. **Crust clock (Q10):** cosmetic rime ~1 day parked → first salted door
   2–3 days → whole-footprint jacketing ~a quadrum of neglect.
7. **Crust pace multipliers (Q11):** salt-snow weather roughly doubles
   accretion; a berth near chimney fields/brine channels accretes faster.
   NOTHING purchasable ever modifies the pace — the fuel-for-time ban stands.
8. **Giant lamp response (Q12): deterministic and forgiving.** Worklight-class
   light only (never a torch), only after hours of steady burn, telegraphed by
   the watcher at the rim + fresh scrape-sign; dowsing the lamps always
   resets. It breaks the lamp — never the ship, never the pawns (ruled prior).
9. **Pool sentinel (Q13): ONE new solitary species**, haunts pool shores,
   squirts the crystallising protein shower when crowded. 🔴 BLOCKED on BENCH
   supplying the creature design (name per invented-exotic convention, prose,
   stats, art brief) — do not invent it here; a design pass delivers it onto
   this item.
10. **Elder discharge tell (Q14): motion, crackle and sound only** — arcing
    limb animation, charge-whine, screen-shake; light exists only at the
    discharge instant. Ban 4 (no glow but the giant's mark) keeps its record.
11. **Salt colours (Q16): ratified as shipped** (white/pink/violet/amber).
    No work.

## Housekeeping owed with the build

- **Rare-catch tier migration**: the rare-catch table and the salt cameo still
  carry the campaign-layer (`RUT_`) prefix while every named catch moved to the
  free tier — migrate per the danger pass's note.
- **Roster JSON**: BENCH amends `rosters/the_grey_sea.json` (flora rows,
  formations, pool grade, Elders, sessile layer) in the design-propagation
  wave — not this item; noted here so nobody double-does it.

## Watch out

- `RM_GreySea`'s `<wildAnimals>`/`<wildPlants>` use the shorthand element form
  (`<RM_X>0.5</RM_X>`), never `<li>` — a `<li>` row is silently dropped and can
  discard the def (CLAUDE.md's loader trap).
- `animalDensity`/`plantDensity` unset means 0f and DEAD content — set both
  explicitly (the Propane Lake shipped that bug).
- The pool lily on liquid terrain may need a placement workaround; the ruled
  fallback is the lip, silently — do not file a defect if the engine refuses
  the surface.
- New .cs files (if the sentinel or crust multipliers need any) require
  `<Compile Include>` lines in any csproj with EnableDefaultCompileItems false.

## verify

- Def diffs show density numbers, band moves and the ten flora wired; a
  quicktest map in RM_GreySea grows the understorey at 0.22 and spawns no
  schooling fish.
- Crust ladder timings observable in a parked-ship quicktest (rime by day 1).
- No purchasable crust counter exists anywhere in the shipped set.
